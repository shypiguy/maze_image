import pygame, sys, random
from pygame.locals import *
import argparse
import json


pygame.init()
 
# Colours
BACKGROUND = (255, 255, 0)
 
# Game Setup
FPS = 30
fpsClock = pygame.time.Clock()
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 960
ZOOM = 4.0
ZOOM_MIN = .75
ZOOM_MAX = 8.0
ZOOM_FACTOR = 1.075
BG_TICK_PER_FRAME = 5

# Maze data constants
cell_blocked = 0
cango_up = 1
cango_right = 2
cango_down = 4
cango_left = 8
on_path = 16
cell_start = 32
cell_end = 64

# Play variables
player_row = 0
player_col = 0
end_row = 0
end_col = 0
player_cell_data = 0
bg_index = 0
bg_tick = 0
 
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Maze Game!')

#Set up command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input_file",  help="the maze file to be played")
args=parser.parse_args()

# Load maze data
f = open (args.input_file, "r")
maze_data = json.loads(f.read())

# Load maze structure data
cells = maze_data['cells']
maze_width = maze_data['width']
maze_height = maze_data['height']
been_there = [0] * maze_width * maze_height

# Find maze start and end row and column
for row in range(maze_height):
    for col in range(maze_width):
        if cells[row*maze_width + col] & cell_start == cell_start:
            player_row = row
            player_col = col
            player_cell_data = cells[row*maze_width + col]
            # maybe let this happen naturally?
            been_there[row*maze_width + col] = 1
        if cells[row*maze_width + col] & cell_end == cell_end:
            end_row = row
            end_col = col
            print((end_row, end_col))
            
# Load maze image
image_file_location = maze_data['gameImage']
o_maze_image = pygame.image.load(image_file_location).convert_alpha()
# Draw the target bullseye
pygame.draw.circle(o_maze_image, (255,0,0), (end_col*8+4,end_row*8+4), 3)
pygame.draw.circle(o_maze_image, (255,255,255), (end_col*8+4,end_row*8+4), 2)
pygame.draw.circle(o_maze_image, (255,0,0), (end_col*8+4,end_row*8+4), 1)

maze_image = pygame.transform.scale_by(o_maze_image, ZOOM)
maze_size = maze_image.get_size()

# Load list of background images
bg_images = []
bg_image_locations = maze_data['backgroundImages']
o_bg_images = [pygame.image.load(f'{i}') for i in bg_image_locations]
bg_images = [pygame.image.load(f'{i}') for i in bg_image_locations]
for i in range(len(bg_images)):
    bg_images[i] = pygame.transform.scale_by(o_bg_images[i], ZOOM)

# function to determine if a cell is "cruisable" (has exactly 2 exits)
def is_cruise (cell_row, cell_col):
    exit_count = 0
    is_it = False
    cell = cells[cell_row*maze_width + cell_col]
    if cell & cango_up == cango_up:
        exit_count = exit_count + 1
    if cell & cango_down == cango_down:
        exit_count = exit_count + 1
    if cell & cango_right == cango_right:
        exit_count = exit_count + 1
    if cell & cango_left == cango_left:
        exit_count = exit_count + 1
    if exit_count == 2:
        is_it = True
    return is_it

# function to identify the next cruisable cell
def next_cell (cell_row, cell_col, from_row, from_col):
    if is_cruise(cell_row, cell_col):
        directions = cells[cell_row*maze_width + cell_col]
        #get rid of non-directional markers
        if directions & on_path == on_path:
            directions = directions - on_path
        if directions & cell_start == cell_start:
            directions = directions - cell_start
        if directions & cell_end == cell_end:
            directions = directions - cell_end
        #get rid of reverse direction
        if from_row > cell_row:
            directions = directions - cango_down
        if from_row < cell_row:
            directions = directions - cango_up
        if from_col > cell_col:
            directions = directions - cango_right
        if from_col < cell_col:
            directions = directions - cango_left
        # identify next cell
        next_row = cell_row
        next_col = cell_col
        if directions & cango_down == cango_down:
            next_row = cell_row + 1
        if directions & cango_up == cango_up:
            next_row = cell_row - 1
        if directions & cango_right == cango_right:
            next_col = cell_col + 1
        if directions & cango_left == cango_left:
            next_col = cell_col - 1
        return [next_row, next_col]
    else:
        return [cell_row, cell_col]

# procedure to leave a breadcrumb
def breadcrumb (cell_row, cell_col):
    global been_there
    global maze_image
    # pick color and draw style
    if cells[cell_row*maze_width + cell_col] & on_path == on_path:
        crumb_color = (255,255,0) #yellow
        # check above
        if cell_row > 0:
            if cells[(cell_row-1)*maze_width + cell_col] & on_path == on_path and \
               cells[cell_row*maze_width + cell_col] & cango_up == cango_up and \
               been_there[(cell_row-1)*maze_width + cell_col] == 1:
                pygame.draw.rect(o_maze_image, crumb_color, (cell_col*8 + 3, cell_row *8 -4, 2, 8))
        #check below
        if cell_row < maze_height -1:
            if cells[(cell_row+1)*maze_width + cell_col] & on_path == on_path and \
               cells[cell_row*maze_width + cell_col] & cango_down == cango_down and \
               been_there[(cell_row+1)*maze_width + cell_col] == 1:
                pygame.draw.rect(o_maze_image, crumb_color, (cell_col*8 + 3, cell_row*8 + 4, 2, 8))
        #check left
        if cell_col > 0:
            if cells[cell_row*maze_width + cell_col-1] & on_path == on_path and \
               cells[cell_row*maze_width + cell_col] & cango_left == cango_left and \
               been_there[cell_row*maze_width + cell_col-1] == 1:
                pygame.draw.rect(o_maze_image, crumb_color, (cell_col*8-4, cell_row*8 + 3, 8, 2))
        #Check right
        if cell_col < maze_width - 1:
            if cells[cell_row*maze_width + cell_col+1] & on_path == on_path and \
               cells[cell_row*maze_width + cell_col] & cango_right == cango_right and \
               been_there[cell_row*maze_width + cell_col+1] == 1:
                pygame.draw.rect(o_maze_image, crumb_color, (cell_col*8+4, cell_row*8 + 3, 8, 2))
                
        
            
    else:
        crumb_color = (255,0,0) #red
        pygame.draw.circle(o_maze_image, crumb_color, (cell_col*8+4,cell_row*8+4), 2)
    #maze_image = pygame.transform.scale_by(o_maze_image, ZOOM)
    been_there[cell_row*maze_width + cell_col] = 1

# function to identify poistion of maze
def maze_pos (player_row, player_col):
    # cells are ZOOM*8 wide, ZOOM*8 tall, (zoom*8/2,zoom*8/2) is their center
    # screen is 640 by 480, center is 320,240
    new_x = player_col*(ZOOM*8)+(ZOOM*8/2)
    new_y = player_row*(ZOOM*8)+(ZOOM*8/2)
    new_origin = (-1*new_x+(WINDOW_WIDTH/2), -1*new_y+(WINDOW_HEIGHT/2))
    if been_there[player_row*maze_width + player_col] == 0:
        breadcrumb(player_row, player_col)
    return new_origin

# Function to render the screen
def screen_paint (origin, player_color):
    global bg_index
    global bg_tick
    global WINDOW
    WINDOW.fill((0,0,0)) # black background
    # pick the next bg_images item to blit
    #bg_surface.blit(bg_images[bg_index], (0,0))
    WINDOW.blit(bg_images[bg_index], origin)
    #increment the bg_tick and bg_inded
    bg_tick = bg_tick + 1
    if bg_tick == BG_TICK_PER_FRAME:
        bg_tick = 0
        bg_index = bg_index + 1
        if bg_index >= len(bg_images):
            bg_index = 0
    # blit the maze
    WINDOW.blit(maze_image, origin)
    # blit the player dot
    pygame.draw.circle(WINDOW, player_color, (WINDOW_WIDTH/2,WINDOW_HEIGHT/2), 3)
    # update the screen
    pygame.display.update()
    

# The main function that controls the game
def main () :
    global player_row
    global player_col
    global ZOOM
    global maze_image
    global maze_surface
    global bg_images
    global bg_surface
    global bg_index
    looping = True
    lum = 0
    lum_dir = 5
    spiral_angle = 0
    spiral_step = 24
    
    # The main game loop
    while looping :
        moved = False
        zoomed = False
        new_player_row = player_row
        new_player_col = player_col
        # Get inputs
        for event in pygame.event.get() :
            if event.type == QUIT :
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PERIOD:
                    if ZOOM < ZOOM_MAX:
                        ZOOM = ZOOM*ZOOM_FACTOR
                        zoomed = True
                elif event.key == pygame.K_COMMA:
                    if ZOOM > ZOOM_MIN:
                        ZOOM = ZOOM/ZOOM_FACTOR
                        zoomed = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if player_cell_data & cango_up == cango_up:
                    new_player_row = player_row - 1
                    moved = True
            elif event.key == pygame.K_RIGHT:
                if player_cell_data & cango_right == cango_right:
                    new_player_col = player_col + 1
                    moved = True
            elif event.key == pygame.K_DOWN:
                if player_cell_data & cango_down == cango_down:
                    new_player_row = player_row + 1
                    moved = True
            elif event.key == pygame.K_LEFT:
                if player_cell_data & cango_left == cango_left:
                    new_player_col = player_col - 1
                    moved = True
                
   
        # Processing

        # transition animation
        if moved == True:
            cruise = True
            old_pos = maze_pos(player_row, player_col)
            new_pos = maze_pos(new_player_row, new_player_col)
            while cruise:
                # smoothly move to next cell
                for step in range (8):
                    interim_pos = (old_pos[0] + (new_pos[0]-old_pos[0])/8*(step+1),old_pos[1] + (new_pos[1]-old_pos[1])/8*(step+1))
                    screen_paint(interim_pos, me_color)
                    fpsClock.tick(FPS)
                maze_image = pygame.transform.scale_by(o_maze_image, ZOOM)
                cruise_cell = next_cell(new_player_row, new_player_col, player_row, player_col)
                if cruise_cell[0] == new_player_row and cruise_cell[1] == new_player_col:
                    cruise = False
                else:
                    player_row = new_player_row
                    player_col = new_player_col
                    new_player_row = cruise_cell[0]
                    new_player_col = cruise_cell[1]
                    old_pos = maze_pos(player_row, player_col)
                    new_pos = maze_pos(new_player_row, new_player_col)
                    

            player_row = new_player_row
            player_col = new_player_col

        player_cell_data = cells[new_player_row*maze_width + new_player_col]
        if zoomed:
            maze_image = pygame.transform.scale_by(o_maze_image, ZOOM)
            for i in range(len(bg_images)):
                bg_images[i] = pygame.transform.scale_by(o_bg_images[i], ZOOM)
        if player_cell_data & on_path == on_path:
            me_color = (0,0,255)
        else:
            me_color = (255,0,0)
        if player_cell_data & cell_end == cell_end:
            me_color = (0,255,0)
            

        # Render elements of the game
        new_origin = maze_pos (player_row, player_col)
        screen_paint(new_origin, me_color)
        pygame.display.update()
        fpsClock.tick(FPS)


 
main()
