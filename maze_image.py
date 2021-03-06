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
from PIL import Image
sys.modules['Image'] = Image
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("input_file",  help="the graphics file to be converted")
parser.add_argument("output_file",  help="destination for the maze graphic file")
parser.add_argument("--max_dimension", help="specify the max (width or height) of the output maze, default = 100",  type=int)

args=parser.parse_args()

if args.max_dimension:
    max_dimension = args.max_dimension
else:
    max_dimension = 100


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


im=im.resize((im.size[0]/factor,im.size[1]/factor),Image.BICUBIC)
im = im.convert("1")

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
            #print "switching to systematic"
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

def print_unentered():
    for row  in range (height):
        for col in range (width):
            if maze[row][col][entered] == 0:
                print row,  col,  seq[(row*height)+(col)]
                print maze[row][col]
   

#current_square = random_square()
#current_direction = random_direction()
#print current_square[0]
#print current_square[1]
#print current_direction
#print move(current_square[0], current_square[1], current_direction)
#print move(1, 1, 0)

# set up the black squares as unavailable
seq = list(im.getdata())
#print seq
for row in range(height):
    for col in range(width):
        if seq[(row*width)+(col)] == 0:
            for info in range(6):
                maze[row][col][info] = 1
            #squares_blocked = squares_blocked + 1
            
#print "after blocking black pixels:"
#print entered_count() 

# mark any isolated white squares as done and blocked
for row in range(height):
    for col in range(width):
        if seq[(row*width)+(col)] == 255: 
            if stuck(row, col) == 1:
                maze[row][col][entered] = 1
#print "after blocking isolated white pixels:"
squares_entered = entered_count()
#print squares_entered
#print maze
#print squares_blocked,  height * width

current_square = random_square(1)
maze[current_square[0]][current_square[1]][entered] = 1
while squares_entered < (height * width):
    
    #print "new walk"
    
    while stuck(current_square[0], current_square[1]) ==0 and maze[current_square[0]][current_square[1]][entered] == 1:
        current_direction = random_direction()
        while move_blocked(current_square[0], current_square[1], current_direction) == 1:
            current_direction = random_direction()
        #print "row = %d, col = %d, direction = %d" % (current_square[0], current_square[1], current_direction)
        
        current_square = move(current_square[0], current_square[1], current_direction)
        #maze[current_square[0]][current_square[1]][entered] = 1
    squares_entered = entered_count()
    if squares_entered > (width*height):
        break
    #print   (width*height) - squares_entered
    current_square = random_square(0)
    maze[current_square[0]][current_square[1]][entered] = 1  

   

print "Calculated"

# build the maze image
#im=im.resize((im.size[0]*8,im.size[1]*8),Image.NEAREST)
im=Image.new("1", (width*8, height*8))
imseq = [255 for pixel in range (im.size[0]*im.size[1])]
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
for dot in sdata:
    imseq[dot[0]*width*8 + dot[1]] =bval
# Finish Square
#top_corner = (height*8*width)+ (width*8)
for dot in fdata:
    imseq[top_corner + dot[0]*width*8 + dot[1]] = bval
im.putdata(imseq)
im.save(args.output_file+".png")



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
        
# start solving
pass_thru_origin = 0

#check if start and destination are open
if  maze[0][0][blocked] ==1 or maze[height-1][width-1][blocked] == 1:
    pass_thru_origin = 2 # make solution fail fast

solved = 0
path=[[0 for row in range(width)] for col in range(height)]
cur_row = 0
cur_col = 0
cur_dir = right
new_point = []

if maze[cur_row][cur_col][cur_dir] == 0:
    cur_dir = down
    

while pass_thru_origin <= 1 and solved == 0:
    
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
    if cur_col == width -1 and cur_row == height -1:
        solved = 1

if solved == 0:
    print "No solution"
else:
    print "SOLVED!"
    imseq = [255 for pixel in range (im.size[0]*im.size[1])]
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
    im.convert("RGB")
    for row in range (height):
        for col in range (width):
            top_corner = (row*64*width)+ (col*8)
            if path[row][col] ==1:
                for dot in fdata:
                    imseq[top_corner + dot[0]*width*8 + dot[1]] = [255, 0, 0]
    im.putdata(imseq)
    im.save(args.output_file+"_solution.png")


print "done"


