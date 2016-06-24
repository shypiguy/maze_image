# maze_image
Make a 2D maze out of an image file
# Usage
python maze_image.py **input_file** **output_file_name** --max-dimension **max_number_of_cells width or height**


"input_file" is the path and file name of a image file


"output_file_name" is the beginning of the maze image's file name (maze_image will save the maze as a .png file, and the solution as <output file>_solution.png)


--max_dimension is an optional argument, default if not supplied is 100. Mazes over 150 cells wide or high take a long time to create! Use wisely!


example: python ./maze_image.py /home/foo/Pictures/Aunt_Martha.jpg am --max_dimension 135


This would make a maze image 135 cells wide named am.png out of a picture of your Aunt Martha, and if there is a solution to get from the top left corner to the bottom right corner, it will also create a second image of the maze with a breadcrumb trail from top left to bottom right named am_solution.png
