#!/usr/bin/env python

#The MIT License (MIT)

#Copyright (c) 2016 Bill Jones

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


import random
import sys
from PIL import Image, ImageOps, ImageStat, ImageEnhance, ImageChops
import numpy as np
import cv2
import json

sys.modules['Image'] = Image
import argparse

def point_in_box_oval (point_x, point_y, box_left, box_top, box_right, box_bottom):
    answer = False
    oval_b = (box_right-box_left)/2
    oval_a = (box_bottom-box_top)/2
    center_x = box_left + oval_b
    center_y = box_top + oval_a
    x_delta = point_x - center_x
    y_delta = point_y - center_y
    if x_delta ** 2/oval_b ** 2 + y_delta **2/oval_a ** 2< 1:
        answer = True
    return answer

def blockfaces(image_in): # takes a color image in, outputs single channel with faces masked in black
    # initialize the all white output image
    blockfaces_out = Image.new("1", (image_in.size[0], image_in.size[1]), 255)
    bfseq = [255 for pixel in range (blockfaces_out.size[0]*blockfaces_out.size[1])]
    # convert the input image to open_cv RBG format
    open_cv_image = np.array(image_in)  
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    # detect the faces as box in face
    gray_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    face = face_classifier.detectMultiScale(gray_image,  minNeighbors=16, minSize=(32, 32)) #scaleFactor=1.2,
    for box in face:
        # set new dimensions for face box (narrower, taller)
        new_l = int(box[0]+box[2]*.1)
        new_t = int(box[1]-box[3]*.1)
        new_r = int(new_l+box[2]*.8)
        new_b = int(new_t+box[3]*1.2)
        facepic = image_in.crop((new_l, new_t, new_r, new_b))
        # build the channel data for the face box
        facepic_r = list(facepic.getdata(0))
        facepic_g = list(facepic.getdata(1))
        facepic_b = list(facepic.getdata(2))
        #build hue histogram
        hueset = {}
        for row in range(facepic.size[1]):
            for col in range(facepic.size[0]):
                if point_in_box_oval (col, row, 0, 0, facepic.size[0], facepic.size[1]):
                    face_pixel_address = row*facepic.size[0]+col
                    rv = facepic_r[face_pixel_address]
                    gv = facepic_g[face_pixel_address]
                    bv = facepic_b[face_pixel_address]
                    minv = min(rv,gv,bv)
                    maxv = max(rv,gv,bv)
                    hue = 0.0
                    if maxv > minv:
                        if rv == maxv:
                            hue = (gv-bv)/(maxv-minv)
                        if gv == maxv:
                            hue = 2.0 + (bv-rv)/(maxv-minv)
                        if bv == maxv:
                            hue = 4.0 + (rv-gv)/(maxv-minv)
                    hue = hue * 60
                    if hue < 0:
                        hue = hue + 360
                    hue = round(hue)
                    hueset[hue] = hueset.get(hue,  0) + 1
        # find face hue range 
        targetsum = .51*facepic.size[0]/2*facepic.size[1]/2*np.pi
        peaksum = 0
        peakhue = 0
        peakvariance = 0
        variance = 0
        while peaksum < targetsum:
            for basehue in range(360):
                setsum = 0
                for hue in range(basehue-variance,basehue+variance+1):
                    if hue < 0:
                        hue = hue+360
                    if hue > 359:
                        hue = hue-360
                    setsum = setsum + hueset.get(hue,0)
                if setsum > peaksum:
                    peaksum = setsum
                    peakhue = basehue
                    peakvariance = variance
            variance = variance + 1
        variance = variance + 3
        print(peakhue, peakvariance, peaksum)
        
        # construct the faceskin image for this box
        for row in range(facepic.size[1]):
            for col in range(facepic.size[0]):
                if point_in_box_oval (col, row, 0, 0, facepic.size[0], facepic.size[1]):
                    face_pixel_address = row*facepic.size[0]+col
                    image_pixel_address = (row+new_t)*blockfaces_out.size[0] + col + new_l 
                    rv = facepic_r[face_pixel_address]
                    gv = facepic_g[face_pixel_address]
                    bv = facepic_b[face_pixel_address]
                    minv = min(rv,gv,bv)
                    maxv = max(rv,gv,bv)
                    hue = 0.0
                    if maxv > minv:
                        if rv == maxv:
                            hue = (gv-bv)/(maxv-minv)
                        if gv == maxv:
                            hue = 2.0 + (bv-rv)/(maxv-minv)
                        if bv == maxv:
                            hue = 4.0 + (rv-gv)/(maxv-minv)
                    hue = hue * 60
                    if hue < 0:
                        hue = hue + 360
                    hue = round(hue)
                    huematch = 0
                    for targethue in range (peakhue-peakvariance,peakhue+peakvariance+1):
                        comparehue = targethue
                        if comparehue > 359:
                            comparehue = comparehue-360
                        if comparehue < 0:
                            comparehue = comparehue+360
                        if hue == comparehue:
                            huematch = 1
                    if huematch == 1:
                        bfseq[image_pixel_address] = 0
    blockfaces_out.putdata(bfseq)
    return blockfaces_out


#Set up command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input_file",  help="the graphics file to be converted")
parser.add_argument("output_file",  help="destination for the maze graphic file")
parser.add_argument("--max_dimension", help="specify the max (width or height) of the output maze, default = 100",  type=int)
parser.add_argument("--sharpen", help="specify the sharpening factor applied before generating the maze, default = 1",  type=float)
parser.add_argument("--bright_target", help="specify the brightness target to be achieved before generating the maze, scale of 0-255, default = 128",  type=int)


args=parser.parse_args()

#Provide a default value for max_dimension if it's not specified on the command line
if args.max_dimension:
    max_dimension = args.max_dimension
else:
    max_dimension = 100

#Provide a default value for sharpen if it's not specified on the command line
if args.sharpen:
    sharpness = args.sharpen
else:
    sharpness = 1.0    

#Provide a default value for bright_target if it's not specified on the command line
if args.bright_target:
    bright_target = args.bright_target
else:
    bright_target = 128    

im = Image.open(args.input_file)

#decide what factor to resize by - target is longest dimension = 200
longest = 0
factor = 1

if im.size[0] > im.size[1]:
    longest = im.size[0]
else:
    longest = im.size[1]
    
if longest > max_dimension:
    factor = longest / max_dimension

# backup the original image
orig_im = im
# get the face mask 
maskim = blockfaces(orig_im)
maskim.save(args.output_file+"_mask.png")
maskim = maskim.resize((int(orig_im.size[0]/factor),int(orig_im.size[1]/factor)),Image.NEAREST)
maskim.save(args.output_file+"_mask_small.png")
#print(ImageStat.Stat(im).mean)
# Analyze the overall brightness of the reduced black and white image 
tempim = im
enhancer=ImageEnhance.Sharpness(tempim)
tempim=enhancer.enhance(sharpness)
bwtempim = tempim.convert("1")
littletempim=bwtempim.resize((int(bwtempim.size[0]/factor),int(bwtempim.size[1]/factor)),Image.BICUBIC)
overall_mean = ImageStat.Stat(littletempim).mean[0]
print(overall_mean)
# Decide whether to auto-invert 
inverted = False
if overall_mean < 128:
    inverted = True
    # invert the orginal image and the little temp image
    littletempim = ImageOps.invert(littletempim)
    orig_im = ImageOps.invert(orig_im)
    tempim = ImageOps.invert(tempim)
    overall_mean = ImageStat.Stat(littletempim).mean[0]
# Adjust the brightness to the target
while overall_mean < bright_target:
    enhancer=ImageEnhance.Brightness(tempim)
    tempim = enhancer.enhance(1.1)
    bwtempim = tempim.convert("1")
    littletempim=bwtempim.resize((int(bwtempim.size[0]/factor),int(bwtempim.size[1]/factor)),Image.BICUBIC)
    overall_mean = ImageStat.Stat(littletempim).mean[0]
    print(overall_mean)


# set the maze image
im = littletempim

# superimpose the mask image on the maze image 
im = ImageChops.darker(im, maskim)
im.save(args.output_file+"_mask_comp.png")

# add a border
im = ImageOps.expand(im, border=3, fill=255) 

random.seed()
maze = []

width = im.size[0]  
height = im.size[1]

up = 0
right=1
down=2
left=3
entered = 4
blocked=5


squares_entered = 0
squares_blocked=0
systematic = 0

frame_num = 0

#initialize memory for the maze
maze = [[[0 for element in range(6)] for row in range(width)] for col in range(height)]


def move_blocked(row, col, direction):
    global maze
    fcol = col
    frow= row
    if direction == up:
        frow = row-1
    elif direction == down:
        frow = row + 1
    elif direction == right:
        fcol = col +1
    elif direction == left:
        fcol = col - 1
    if (frow > -1 and frow< height) and (fcol > -1 and fcol < width):
        return maze[frow][fcol][entered]
    return 1
    
def stuck(row, col):
    global squares_blocked
    global maze
    stuck_sum = 0
    for i in range(4):
        stuck_sum = stuck_sum + move_blocked(row, col, i)
    if stuck_sum == 4:
        return 1
    return 0 
    

    
def random_direction():
    return random.randint(0, 3)
    
def random_square(initialize):
    global squares_blocked
    global maze
    global systematic
    

    
    if systematic == 1:
        for row in range (height):
            for col in range (width):
                if stuck(row, col) == 0 and maze[row][col][entered] == 1 and maze[row][col][blocked] == 0:
                    return [row,  col]
        for row in range (height):
            for col in range (width):
                if stuck(row, col) == 0 and maze[row][col][blocked] == 0: 
                    maze[row][col][entered] == 1 
                    return [row,  col]
        return [0, 0]            
    bad_tries = 0
    your_square = [random.randint(0, height - 1), random.randint(0, width - 1)]
    while stuck(your_square[0], your_square[1]) == 1 or (maze[your_square[0]][your_square[1]][entered] == 0 and initialize == 0) or maze[your_square[0]][your_square[1]][blocked] == 1:
        your_square = [random.randint(0, height - 1), random.randint(0, width - 1)]
        bad_tries = bad_tries + 1
        if bad_tries > 1000:
            systematic = 1
            # switching to systematic
            return random_square(initialize)
    return your_square
    
def move(row, col, direction):
    global maze
    global squares_entered
    if move_blocked(row, col, direction)==1:
        raise Exception("Move blocked")
    fcol = col
    frow= row
    if direction == up:
        frow = row-1
        maze[row][col][up]=1
        maze[row-1][col][entered]=1
        maze[row-1][col][down]=1
    elif direction == down:
        frow = row + 1
        maze[row][col][down]=1
        maze[row+1][col][entered]=1
        maze[row+1][col][up]=1
    elif direction == right:
        fcol = col +1
        maze[row][col][right] =1
        maze[row][col+1][entered]=1
        maze[row][col+1][left]=1
    elif direction == left:
        fcol = col - 1
        maze[row][col][left]=1
        maze[row][col-1][entered]=1
        maze[row][col-1][right]=1
    #squares_entered = squares_entered + 1
    draw_square(row, col)
    draw_square(frow, fcol)
    # diabling frame write for debug purposes write_frame()
    return [frow, fcol]
 
def blocked_count():
    global maze
    bc = 0
    for row  in range (height):
        for col in range (width):
            bc = bc + stuck(row, col)
    return bc
    
def entered_count():
    global maze
    ec = 0
    for row  in range (height):
        for col in range (width):
            ec = ec + maze[row][col][entered]
    return ec



def draw_square(drow, dcol):
    global maze
    global imseq
    global wval
    global bval
    global frame_num
    top_corner = (drow*64*width)+ (dcol*8)
    if maze[drow][dcol][blocked]== 1:
        for brow in range (8):
            for bcol in range (8):
                imseq[top_corner+(brow*width*8)+(bcol)] = 0
    else:
        #top left corner
        imseq[top_corner] = 0
        #top right corner
        imseq[top_corner + 7] = 0
        #bottom left corner
        imseq[top_corner+(7*width*8)] = 0
        #bottom right corner
        imseq[top_corner+(7*width*8)+7] = 0
        # top edge
        pval = wval
        if maze[drow][dcol][up] == 0:
            pval = bval
        for i in range (1,7):
            imseq[top_corner + i] = pval
        # bottom edge
        pval = wval
        if maze[drow][dcol][down] == 0:
            pval = bval
        for i in range (1,7):
            imseq[top_corner +(7*width*8)+ i] = pval
        # left edge
        pval = wval
        if maze[drow][dcol][left] == 0:
            pval = bval
        for i in range (1,7):
            imseq[top_corner + (width * i*8)] = pval
        # right edge
        pval = wval    
        if maze[drow][dcol][right] == 0:
            pval = bval
        for i in range (1,7):
            imseq[top_corner + 7 + (i * width*8)] = pval


def write_frame():
    global imseq
    global frame_num
    im.putdata(imseq)
    im.save(args.output_file+str(frame_num).zfill(6)+".png")
    frame_num = frame_num + 1
#current_square = random_square()
#current_direction = random_direction()
 

#"/home/bill/Development/Python/maze/tf.png"
wval = 255
bval = 0

# set up the black squares as unavailable
seq = list(im.getdata())

im=Image.new("1", (width*8, height*8))
imseq = [255 for pixel in range (im.size[0]*im.size[1])]
 
for row in range(height):
    for col in range(width):
        if seq[(row*width)+(col)] == 0:
            for info in range(6):
                maze[row][col][info] = 1
            draw_square(row,  col)
            
#print "after blocking black pixels:"
#print entered_count() 

# mark any isolated white squares as done and blocked
for row in range(height):
    for col in range(width):
        if seq[(row*width)+(col)] == 255: 
            if stuck(row, col) == 1:
                maze[row][col][entered] = 1
# after blocking isolated white pixels:
squares_entered = entered_count()
 

current_square = random_square(1)
maze[current_square[0]][current_square[1]][entered] = 1
while squares_entered < (height * width):
    
    #new walk
    
    while stuck(current_square[0], current_square[1]) ==0 and maze[current_square[0]][current_square[1]][entered] == 1:
        current_direction = random_direction()
        while move_blocked(current_square[0], current_square[1], current_direction) == 1:
            current_direction = random_direction()
         
        current_square = move(current_square[0], current_square[1], current_direction)
        #maze[current_square[0]][current_square[1]][entered] = 1
    squares_entered = entered_count()
    if squares_entered > (width*height):
        break
    current_square = random_square(0)
    maze[current_square[0]][current_square[1]][entered] = 1  

   

print ("Calculated")

# build the maze image
#im=im.resize((im.size[0]*8,im.size[1]*8),Image.NEAREST)
#im=Image.new("1", (width*8, height*8))
#imseq = [255 for pixel in range (im.size[0]*im.size[1])]
#"/home/bill/Development/Python/maze/tf.png"
wval = 255
bval = 0
for row in range (height):
    for col in range (width):
        top_corner = (row*64*width)+ (col*8)
        if maze[row][col][blocked]== 1:
            for brow in range (8):
                for bcol in range (8):
                    imseq[top_corner+(brow*width*8)+(bcol)] = 0
        else:
            #top left corner
            imseq[top_corner] = 0
            #top right corner
            imseq[top_corner + 7] = 0
            #bottom left corner
            imseq[top_corner+(7*width*8)] = 0
            #bottom right corner
            imseq[top_corner+(7*width*8)+7] = 0
            # top edge
            pval = wval
            if maze[row][col][up] == 0:
                pval = bval
            for i in range (1,7):
                imseq[top_corner + i] = pval
            # bottom edge
            pval = wval
            if maze[row][col][down] == 0:
                pval = bval
            for i in range (1,7):
                imseq[top_corner +(7*width*8)+ i] = pval
            # left edge
            pval = wval
            if maze[row][col][left] == 0:
                pval = bval
            for i in range (1,7):
                imseq[top_corner + (width * i*8)] = pval
            # right edge
            pval = wval    
            if maze[row][col][right] == 0:
                pval = bval
            for i in range (1,7):
                imseq[top_corner + 7 + (i * width*8)] = pval

sdata = [(2, 2), (3, 3), (3, 5), (4, 4), (4, 5), (5, 3), (5, 4), (5, 5)]
fdata = [(2, 3), (2,4), (2, 4), (3, 2),(3,3), (3, 4), (3, 5), (4, 2),(4, 3), (4, 4),  (4, 5),  (5, 3),  (5, 4)]
# Start Square
#for dot in sdata:
#    imseq[dot[0]*width*8 + dot[1]] =bval
# Finish Square
#top_corner = (height*8*width)+ (width*8)
#for dot in fdata:   
#    imseq[top_corner + dot[0]*width*8 + dot[1]] = bval
# write the black and white maze
im.putdata(imseq)
im.save(args.output_file+".png")

#convert to rgb and apply the original image on top
orig_im = orig_im.resize((im.size[0]-48,im.size[1]-48),Image.BICUBIC)
orig_im = ImageOps.expand(orig_im, border=24, fill=(255,255,255)) 
orig_imseq_r = list(orig_im.getdata(0))
orig_imseq_g = list(orig_im.getdata(1))
orig_imseq_b = list(orig_im.getdata(2))
maze_im = im.convert("RGB")
maze_imseq_r = list(maze_im.getdata(0))
maze_imseq_g = list(maze_im.getdata(1))
maze_imseq_b = list(maze_im.getdata(2))
maze_imseq_a = [0] * len(maze_imseq_r)
for row in range (height):  #trying
    for col in range (width): #trying
        top_corner = (row*64*width)+ (col*8)
        subl_factor = .35
        if maze[row][col][blocked]== 1:
            subl_factor = 0
        for brow in range (1,7):
            for bcol in range (1,7):
                # fill in block body with color image data
                maze_imseq_r[top_corner+(brow*width*8)+(bcol)] = orig_imseq_r[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_r[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_g[top_corner+(brow*width*8)+(bcol)] = orig_imseq_g[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_g[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_b[top_corner+(brow*width*8)+(bcol)] = orig_imseq_b[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_b[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_a[top_corner+(brow*width*8)+(bcol)] = 255
        # get adjacent blockage info
        paint_up = False
        paint_right = False
        paint_down = False
        paint_left = False
        if maze[row][col][blocked]== 1:
            if maze[row-1][col][blocked]== 1:
                    paint_up = True
            if maze[row][col+1][blocked]== 1:
                    paint_right = True
            if maze[row+1][col][blocked]== 1:
                    paint_down = True
            if maze[row][col-1][blocked]== 1:
                    paint_left = True
        else:
            paint_up = maze[row][col][up] == 1
            paint_right = maze[row][col][right] == 1
            paint_down = maze[row][col][down] == 1
            paint_left = maze[row][col][left] == 1
        if paint_up:
            for brow in range(1):
                for bcol in range (1,7):
                    maze_imseq_r[top_corner+(brow*width*8)+(bcol)] = orig_imseq_r[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_r[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                    maze_imseq_g[top_corner+(brow*width*8)+(bcol)] = orig_imseq_g[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_g[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                    maze_imseq_b[top_corner+(brow*width*8)+(bcol)] = orig_imseq_b[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_b[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                    maze_imseq_a[top_corner+(brow*width*8)+(bcol)] = 255
        if paint_right:
            for brow in range(1,7):
                for bcol in range (7,8):
                    maze_imseq_r[top_corner+(brow*width*8)+(bcol)] = orig_imseq_r[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_r[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                    maze_imseq_g[top_corner+(brow*width*8)+(bcol)] = orig_imseq_g[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_g[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                    maze_imseq_b[top_corner+(brow*width*8)+(bcol)] = orig_imseq_b[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_b[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                    maze_imseq_a[top_corner+(brow*width*8)+(bcol)] = 255
        if paint_down:
            for brow in range(7,8):
                for bcol in range (1,7):
                    maze_imseq_r[top_corner+(brow*width*8)+(bcol)] = orig_imseq_r[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_r[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                    maze_imseq_g[top_corner+(brow*width*8)+(bcol)] = orig_imseq_g[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_g[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                    maze_imseq_b[top_corner+(brow*width*8)+(bcol)] = orig_imseq_b[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_b[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                    maze_imseq_a[top_corner+(brow*width*8)+(bcol)] = 255
        if paint_left:
            for brow in range(1,7):
                for bcol in range (1):
                    maze_imseq_r[top_corner+(brow*width*8)+(bcol)] = orig_imseq_r[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_r[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                    maze_imseq_g[top_corner+(brow*width*8)+(bcol)] = orig_imseq_g[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_g[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                    maze_imseq_b[top_corner+(brow*width*8)+(bcol)] = orig_imseq_b[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_b[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                    maze_imseq_a[top_corner+(brow*width*8)+(bcol)] = 255
        # do the corners
        if maze[row][col][blocked]== 1:
            if paint_up and paint_right:
                brow = 0
                bcol = 7
                maze_imseq_r[top_corner+(brow*width*8)+(bcol)] = orig_imseq_r[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_r[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_g[top_corner+(brow*width*8)+(bcol)] = orig_imseq_g[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_g[top_corner+(brow*width*8)+(bcol)])*subl_factor) 
                maze_imseq_b[top_corner+(brow*width*8)+(bcol)] = orig_imseq_b[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_b[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_a[top_corner+(brow*width*8)+(bcol)] = 255
            if paint_down and paint_right:
                brow = 7
                bcol = 7
                maze_imseq_r[top_corner+(brow*width*8)+(bcol)] = orig_imseq_r[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_r[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_g[top_corner+(brow*width*8)+(bcol)] = orig_imseq_g[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_g[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_b[top_corner+(brow*width*8)+(bcol)] = orig_imseq_b[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_b[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_a[top_corner+(brow*width*8)+(bcol)] = 255
            if paint_down and paint_left:
                brow = 7
                bcol = 0
                maze_imseq_r[top_corner+(brow*width*8)+(bcol)] = orig_imseq_r[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_r[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_g[top_corner+(brow*width*8)+(bcol)] = orig_imseq_g[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_g[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_b[top_corner+(brow*width*8)+(bcol)] = orig_imseq_b[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_b[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_a[top_corner+(brow*width*8)+(bcol)] = 255
            if paint_up and paint_left:
                brow = 0
                bcol = 0
                maze_imseq_r[top_corner+(brow*width*8)+(bcol)] = orig_imseq_r[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_r[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_g[top_corner+(brow*width*8)+(bcol)] = orig_imseq_g[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_g[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_b[top_corner+(brow*width*8)+(bcol)] = orig_imseq_b[top_corner+(brow*width*8)+(bcol)] + int((255-orig_imseq_b[top_corner+(brow*width*8)+(bcol)])*subl_factor)
                maze_imseq_a[top_corner+(brow*width*8)+(bcol)] = 255

maze_im.putdata(list(zip(maze_imseq_r, maze_imseq_g, maze_imseq_b)))
if inverted == True:
    maze_im = ImageOps.invert(maze_im)
    maze_imseq_r = list(maze_im.getdata(0))
    maze_imseq_g = list(maze_im.getdata(1))
    maze_imseq_b = list(maze_im.getdata(2))
maze_im.save(args.output_file+"_recolor.png")
alpha_maze_im = Image.new("RGBA", (maze_im.width, maze_im.height))
alpha_maze_im.putdata(list(zip(maze_imseq_r, maze_imseq_g, maze_imseq_b, maze_imseq_a)))
alpha_maze_im.save(args.output_file+"_alpha.png")




def whats_left(cur_dir):
    if cur_dir == up:
        return left
    elif cur_dir == left:
        return down
    elif cur_dir == down:
        return right
    elif cur_dir == right:
        return up
    else:
        return left
        
def whats_right(cur_dir):
    if cur_dir == up:
        return right
    elif cur_dir == right:
        return down
    elif cur_dir == down:
        return left
    elif cur_dir == left:
        return up
    else:
        return right
        
def can_go(row, col, dir):
   global maze
   return maze[row][col][dir]
  
def move_from(row,  col,  direction):
    global path
    if can_go(row, col, direction) == 1:
        fcol = col
        frow= row
        if direction == up:
            frow = row-1
        elif direction == down:
            frow = row + 1
        elif direction == right:
            fcol = col +1
        elif direction == left:
            fcol = col - 1
        path[frow][fcol] = abs(path[frow][fcol] -1) # switch the value of the square
        path[row][col] = path[frow][fcol] #set the original point to match
        return [frow, fcol]

def move_from_simple(row,  col,  direction):
    if can_go(row, col, direction) == 1:
        fcol = col
        frow= row
        if direction == up:
            frow = row-1
        elif direction == down:
            frow = row + 1
        elif direction == right:
            fcol = col +1
        elif direction == left:
            fcol = col - 1
        return [frow, fcol]

def not_solved(cell_in, direction_in):
    answer = True
    for direction in cell_in[3]:
        if direction[0] == direction_in:
            answer = False
    return answer

def cell_in_maze_map(cell_in, maze_map_in):
    answer = False
    for cell in maze_map_in:
        if cell_in[0] == cell[0] and cell_in[1] == cell[1]:
            answer = True
    return answer

def opposite_direction(direction_in):
    if direction_in == down:
        answer = up
    elif direction_in == left:
        answer = right
    elif direction_in == up:
        answer = down
    elif direction_in == right:
        answer = left
    return answer
        
# Build the network of destinations and intersections
# destination is a cell with only one way out
# intersection is a cell with 3 or 4 ways out
# anything else is a hallway

# define maze map data structure
cell_type = 0 # first data element
hallway = 0       # cell type value
destination = 1   # cell type value
intersection = 2  # cell type value
neighbor = 1  # second data element
distance = 2  #third data element
cell_type = [[-1 for row in range(width)] for col in range(height)]

# step 1 identify cell types:
for row in range(height):
    for col in range(width):
        if maze[row][col][blocked]==0:
            dir_sum = 0
            for direction in range(4):
                dir_sum = dir_sum + maze[row][col][direction]
            if dir_sum >= 3:
                cell_type[row][col]=intersection
            elif dir_sum == 1:
                cell_type[row][col]=destination
            else:
                cell_type[row][col]=hallway
# step 2 reduce map
row_element = 0
col_element = 1
type_element = 2
neighbors = 3
maze_map = []
for row in range(height):
    for col in range(width):
        if cell_type[row][col] == destination or cell_type[row][col] == intersection:
            maze_map += [[row, col, cell_type[row][col], []]]
#print(maze_map)    #debug step
solved_maze_map = []
for cell in maze_map:
    start_row = cell[row_element]
    start_col = cell[col_element]
    if cell[type_element] == destination:
        neighbor_count = 1 
    elif cell[type_element] == intersection:
        neighbor_count = 3 
    while len(cell[neighbors]) < neighbor_count:
        cum_distance = 0
        neighbor_found = False
        # pick a direction not listed in neighbors
        start_direction = 5
        for try_direction in range(4):
           if can_go(start_row, start_col, try_direction) == 1:
                if try_direction < start_direction and not_solved(cell, try_direction) == True:
                    start_direction = try_direction
        next_direction = start_direction
        this_cell = [cell[row_element], cell[col_element]]
        while neighbor_found == False:
            cum_distance = cum_distance + 1                   
            next_cell = move_from_simple(this_cell[0], this_cell[1], next_direction)
            if cell_in_maze_map(next_cell, maze_map) == True:
                neighbor_found = True
                cell[neighbors] += [[start_direction, next_cell[0], next_cell[1], cum_distance]]
            else:
                this_cell = next_cell
                if can_go(this_cell[0],  this_cell[1],  whats_left(next_direction)) ==1:
                    next_direction = whats_left(next_direction)
                else:
                    while can_go(this_cell[0],  this_cell[1],  next_direction) ==0:
                        next_direction = whats_right(next_direction)
    solved_maze_map += [cell]
#print(solved_maze_map)    #debug step

# step through the map to build a sorted list of the longest paths
distance_list = []
for cell in solved_maze_map:
    if cell[2] == 1 and (cell[0] == 0 or cell[0] == height-1 or cell[1] == 0 or cell[1] == width-1): # dead end on an edge
        start_point = [cell[0], cell[1], [[cell[3][0][1],cell[3][0][2],cell[3][0][3]]]]
        #print(start_point)
        current_node = 0
        while len(start_point[2]) > current_node:
            this_point = start_point[2][current_node]
            for node in solved_maze_map:
                if node[0] == this_point[0] and node[1] == this_point[1]:
                    for next_node in node[3]:
                        next_node_found = False
                        for point in start_point[2]:
                            if next_node[1] == point[0] and next_node[2] == point[1]:
                                next_node_found = True
                        if next_node_found == False:
                            start_point[2] += [[next_node[1], next_node[2], next_node[3] + this_point[2]]]
            current_node = current_node + 1
        distance_list += [start_point]    
#print(distance_list)

#step throught the distance list to find the longest path
long_start_row = 0
long_start_col = 0
long_end_row = height - 1
long_end_col = width - 1
max_dist = 0
for start_point in distance_list:
    for end_point in start_point[2]:
        if (end_point[0] == 0 or end_point[0] == height-1 or end_point[1] == 0 or end_point[1] == width - 1) and end_point[2] > max_dist:
            long_start_row = start_point[0]
            long_start_col = start_point[1]
            long_end_row = end_point[0]
            long_end_col = end_point[1]
            max_dist = end_point[2]
        
                
    
        
                
            



# start solving
pass_thru_origin = 0

#check if start and destination are open
if  maze[0][0][blocked] ==1 or maze[height-1][width-1][blocked] == 1:
    pass_thru_origin = 2 # make solution fail fast

solved = 0
path=[[0 for row in range(width)] for col in range(height)]
cur_row = long_start_row
cur_col = long_start_col
cur_dir = right
new_point = []

if maze[cur_row][cur_col][cur_dir] == 0:
    cur_dir = down
    

while  solved == 0: # pass_thru_origin <= 1 and
    
    if can_go(cur_row,  cur_col,  whats_left(cur_dir)) ==1:
        cur_dir = whats_left(cur_dir)
    else:
        while can_go(cur_row,  cur_col,  cur_dir) ==0:
            cur_dir = whats_right(cur_dir)
    new_point = move_from(cur_row,  cur_col,  cur_dir)
    cur_row = new_point[0]
    cur_col = new_point[1]
    if cur_col ==0 and cur_dir ==0:
        pass_thru_origin = pass_thru_origin + 1
    if cur_col == long_end_col and cur_row == long_end_row:
        solved = 1

if solved == 0:
    print ("No solution")
else:
    print( "SOLVED!")
    im = im.convert("RGB")
    r_imseq = list(im.getdata(band=0))
    g_imseq = list(im.getdata(band=1))
    b_imseq = list(im.getdata(band=2))
    wval = 255
    bval = 0
    im.save(args.output_file+"_rgb.png")
    for row in range (height):
        for col in range (width):
            top_corner = (row*64*width)+ (col*8)
            # apply the solution dots
            if path[row][col] ==1:
                for dot in fdata:
                    g_imseq[top_corner + dot[0]*width*8 + dot[1]] = 0 
                    b_imseq[top_corner + dot[0]*width*8 + dot[1]] = 0 
    #print(list(zip(r_imseq, g_imseq, b_imseq)))
    im.putdata(list(zip(r_imseq, g_imseq, b_imseq)))
    im.save(args.output_file+"_solution.png")
    #for i in range (1, 240):
    #    write_frame()


print ("done")

# cut and size the background images
# data to work with: width, height, alpha_maze_im, long_end_row, long_end_col
# what is the pixel location of the center of the circles?
ccx = long_end_col*8 + 4
ccy = long_end_row*8 + 4

# assuming no scaling...
# top of crop box is
crop_top = 2000 - ccy
crop_left = 2000 - ccx
crop_bottom  = crop_top + height*8
crop_right = crop_left + width*8

for index in range(5):
    file_index = index + 1
    circ_img = Image.open("./src/circles" + str(file_index) + ".png")
    circ_img = circ_img.crop((crop_left, crop_top, crop_right, crop_bottom))
    circ_img.save(args.output_file+"_bg"+str(file_index)+".png")



# build the maze data file
mdf = {}
mdf.update({"jsonType":"maze_image"})
mdf.update({"version":"0.0.1"})
mdf.update({"description":"no description given"})
mdf.update({"metaData":"no medatadata given"})
mdf.update({"name":args.output_file})
mdf.update({"width":width})
mdf.update({"height":height})
mdf.update({"originalImage":args.input_file})
mdf.update({"gameImage":args.output_file+"_alpha.png"})
cells_out = []
for row in range(height):
    for col in range(width):
        cell_value = 0
        if maze[row][col][blocked] == 0:
            for direction in range(4):
                if maze[row][col][direction] == 1:
                    cell_value = cell_value + 2**direction
        if path[row][col] == 1:
            cell_value = cell_value + 16
        if row == long_start_row and col == long_start_col:
            cell_value = cell_value + 32
        if row == long_end_row and col == long_end_col:
            cell_value = cell_value + 64
        cells_out.append(cell_value)
mdf.update({"cells":cells_out})
with open(args.output_file+"_data.json", "w") as f:
    f.write(json.dumps(mdf))

