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
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
ZOOM = 4.0
ZOOM_MIN = .75
ZOOM_MAX = 8.0
ZOOM_FACTOR = 1.075

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

# Find maze start and end row and column
for row in range(maze_height):
    for col in range(maze_width):
        if cells[row*maze_width + col] & cell_start == cell_start:
            player_row = row
            player_col = col
            player_cell_data = cells[row*maze_width + col]
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


# function to identify poistion of maze
def maze_pos (player_row, player_col):
    # cells are ZOOM*8 wide, ZOOM*8 tall, (zoom*8/2,zoom*8/2) is their center
    # screen is 640 by 480, center is 320,240
    new_x = player_col*(ZOOM*8)+(ZOOM*8/2)
    new_y = player_row*(ZOOM*8)+(ZOOM*8/2)
    new_origin = (-1*new_x+320, -1*new_y+240)
    return new_origin

# function to identify poistion of spiral
def spiral_pos (player_row, player_col, spiral_size):
    # cells are ZOOM*8 wide, ZOOM*8 tall, (zoom*8/2,zoom*8/2) is their center
    # screen is 640 by 480, center is 320,240

    # spiral has variable width (because it will rotate)
    # it's center needs to be calculated relative to
    # the maze_surface origin

    # s_w is width of the spiral image
    # s_h is height of the spiral image
    # m_x is x coord of maze top left
    # m_y is y coord of maze top left
    # end_row is cell row where spiral should be centered
    # end_col is cell col where spiral should be centered
    # new_x = m_x - s_w/2 + (end_row*(ZOOM*8)+(ZOOM*4))
    # Physical center y value should be y= 636, but image is only 1260 tall
    # need to subtract (shift up 6 pixels of 1260 = 
    
    maze_origin = maze_pos(player_row, player_col)
    m_x = maze_origin[0]
    m_y = maze_origin[1]

    new_x = m_x - s_w/2 + (end_col*(ZOOM*8)+(ZOOM*4))
    new_y = m_y - s_h/2 + (end_row*(ZOOM*8)+(ZOOM*4))
    new_origin = (new_x, new_y)
    return new_origin

# Function to render the screen
def screen_paint (origin, player_color):
    global bg_index
    global WINDOW
    WINDOW.fill((0,0,0)) # black background
    # pick the next bg_images item to blit
    #bg_surface.blit(bg_images[bg_index], (0,0))
    WINDOW.blit(bg_images[bg_index], origin)
    #increment the bg_indedx
    bg_index = bg_index + 1
    if bg_index >= len(bg_images):
        bg_index = 0
    # blit the maze
    WINDOW.blit(maze_image, origin)
    # blit the player dot
    pygame.draw.circle(WINDOW, player_color, (320,240), 3)
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
            old_pos = maze_pos(player_row, player_col)
            new_pos = maze_pos(new_player_row, new_player_col)
            for step in range (8):
                interim_pos = (old_pos[0] + (new_pos[0]-old_pos[0])/8*(step+1),old_pos[1] + (new_pos[1]-old_pos[1])/8*(step+1))
                screen_paint(interim_pos, me_color)
                fpsClock.tick(FPS)

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
