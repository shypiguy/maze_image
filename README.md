# maze_image
Make a 2D maze out of an image file
# Usage
python maze_image.py **input_file** -o [`--`output_file] **output_file_name** -d [`--`max-dimension] **max_dimension** -s [`--`sharpness] **sharpening_factor** -b [`--`bright_target] **brightness** -a|`--`no-a [`-`-start_end_anywhere|`--`no_start_end_anywhere] **start_anywhere_bool** -c [`--`config_file] **config_file_path** -f [`--`face_detect] **face_detect_bool** -h [`--`help]


"input_file" is the path and file name of a image file

"output_file_name" is the beginning of the maze image's file name (maze_image will save the maze as a series of .png files and a maze metadata file named [output_file_name]_data.json)

"max_dimension" is an optional integer argument, indicating how long the longest side of the maze structure should be in cells. Default if not supplied is 50. Mazes over 150 cells wide or high take a long time to create! Use wisely!

"sharpening_factor" is a positive float value, indicating how much sharpness filter should be applied to the image before maze generation. Default is 1.0 which indicates no additional sharpening. 1.3 would be a 30% increase in sharpness, .7 would be a 30% reduction in sharpness

"brightness" is an integer value between 0 and 255 indicating how much the image should be brightened to reduce blocked cells in the resulting maze. Default is 224. Higher values result in more maze path cells, lower values result in less maze path cells.

"start_anywhere_bool" is a True/False Yes/No value indicating if the solved maze path beginning and end can be any cell in the maze (True) or if the start and end points of the solution path must both be on the edges of the resulting maze.

"config_file_path" is the path to a non-standard config file with structure described in the config file section of this document

"face_detect_bool" is a True/False Yes/No value indicating if face detection should be used to block detected faces in the source image from the maze path creation (True) or if this pre-processing step can be skipped. 

-h [`--`help] outputs online help for these options

**example:** python ./maze_image.py /home/foo/Pictures/Aunt_Martha.jpg -o am --max_dimension 135

This would make a maze image 135 cells wide named am.png and maze metadata file out of a picture of your Aunt Martha.

## Config Files
At runtime, maze_image.py sources its parameters from the following, in order:

 1. Defaults
 2. /etc/maze_image.conf
 3. ~/.config/maze_image.conf
 4. ./maze_image.conf
 5. the custom config file inidcated by the -c [`--`config_file] command line argument
 6. command line arguments

An example config file is provided in the source, and may contain or omit any of the following entries:

    # Configuration for maze_image.py
    
    [image processing]
    sharpness = 1.2
    bright_target = 218
    face_detect = True
    
    [maze generation]
    max_dimension = 62
    start_end_anywhere = True