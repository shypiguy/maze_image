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

 
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Maze Game!')


#Set up command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input_file",  help="the maze file to be palyed")
args=parser.parse_args()

# Load maze data
f = open (args.input_file, "r")
maze_data = json.loads(f.read())

# Load maze image
image_file_loaction = maze_data['gameImage']
o_maze_image = pygame.image.load(image_file_loaction).convert_alpha()
maze_image = pygame.transform.scale_by(o_maze_image, ZOOM)
maze_size = maze_image.get_size()
print(maze_size)
maze_surface = pygame.Surface(maze_size)
maze_surface.fill((0,255,255))
maze_surface.blit(maze_image, (0,0))

# Load maze structure data
cells = maze_data['cells']
maze_width = maze_data['width']
maze_height = maze_data['height']

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
player_cell_data = 0

# Find maze start row and column
for row in range(maze_height):
    for col in range(maze_width):
        if cells[row*maze_width + col] & cell_start == cell_start:
            player_row = row
            player_col = col
            player_cell_data = cells[row*maze_width + col]

# function to identify poistion of maze
def maze_pos (player_row, player_col):
    # cells are ZOOM*8 wide, ZOOM*8 tall, (zoom*8/2,zoom*8/2) is their center
    # screen is 640 by 480, center is 320,240
    new_x = player_col*(ZOOM*8)+(ZOOM*8/2)
    new_y = player_row*(ZOOM*8)+(ZOOM*8/2)
    new_origin = (-1*new_x+320, -1*new_y+240)
    return new_origin
    



# The main function that controls the game
def main () :
    global player_row
    global player_col
    global ZOOM
    global maze_image
    global maze_surface
    looping = True
    lum = 0
    lum_dir = 5
  
    # The main game loop
    while looping :
        if lum_dir == 5:
            if lum == 255:
                lum_dir = -5
        else:
            if lum == 0:
                lum_dir = 5
        lum = lum + lum_dir
        moved = False
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
                elif event.key == pygame.K_COMMA:
                    if ZOOM > ZOOM_MIN:
                        ZOOM = ZOOM/ZOOM_FACTOR

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
                WINDOW.fill((lum,lum,0))
                WINDOW.blit(maze_surface, interim_pos)
                pygame.draw.circle(WINDOW, me_color, (320,240), 3)
                pygame.display.update()
                fpsClock.tick(FPS)

            player_row = new_player_row
            player_col = new_player_col

        player_cell_data = cells[new_player_row*maze_width + new_player_col]
        maze_surface = pygame.transform.scale_by(o_maze_image, ZOOM)        
        if player_cell_data & on_path == on_path:
            me_color = (0,0,255)
        else:
            me_color = (255,0,0)
        if player_cell_data & cell_end == cell_end:
            me_color = (0,255,0)
            

        # Render elements of the game
        WINDOW.fill((lum,lum,0))
        WINDOW.blit(maze_surface, maze_pos(player_row, player_col))
        pygame.draw.circle(WINDOW, me_color, (320,240), 3)
        pygame.display.update()
        fpsClock.tick(FPS)


 
main()
