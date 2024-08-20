import pygame, sys, random
from pygame.locals import *
import argparse
import json

pygame.init()
 
# Colours
BACKGROUND = (0, 0, 0)
 
# Game Setup
FPS = 30
fpsClock = pygame.time.Clock()
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
 
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
maze_image = pygame.image.load(image_file_loaction)
maze_image = pygame.transform.scale_by(maze_image, 4)

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
    # cells are 4*8 wide, 4*8 tall, (16,16) is their center
    # screen is 640 by 480, center is 320,240
    new_x = player_col*32+16
    new_y = player_row*32+16
    new_origin = (-1*new_x+320, -1*new_y+240)
    return new_origin
    



# The main function that controls the game
def main () :
    global player_row
    global player_col
    looping = True
  
    # The main game loop
    while looping :
        moved = False
        new_player_row = player_row
        new_player_col = player_col
        # Get inputs
        for event in pygame.event.get() :
            if event.type == QUIT :
                pygame.quit()
                sys.exit()

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
                WINDOW.fill(BACKGROUND)
                WINDOW.blit(maze_image, interim_pos)
                pygame.draw.circle(WINDOW, me_color, (320,240), 3)
                pygame.display.update()
                fpsClock.tick(FPS)

            player_row = new_player_row
            player_col = new_player_col

        player_cell_data = cells[new_player_row*maze_width + new_player_col]
        if player_cell_data & on_path == on_path:
            me_color = (0,0,255)
        else:
            me_color = (255,0,0)
        if player_cell_data & cell_end == cell_end:
            me_color = (0,255,0)
            

        # Render elements of the game
        WINDOW.fill(BACKGROUND)
        WINDOW.blit(maze_image, maze_pos(player_row, player_col))
        pygame.draw.circle(WINDOW, me_color, (320,240), 3)
        pygame.display.update()
        fpsClock.tick(FPS)


 
main()
