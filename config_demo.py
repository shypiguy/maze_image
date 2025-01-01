# Demonstrate config and command argument handling

# Order of precedence
# 1. command line arguments
# 2. command line config file location
# 3. ./maze_image.conf 
# 4. User ~/.config/maze_image.conf
# 5. /etc/maze_image.conf
# 6. app defaults

# arguments
# input_file file_spec
# -o --output_file output_file file_spec
# -d --max_dimension max_dimension (integer)
# -s --sharpness sharpness (float)
# -b --bright_target bright_target (integer)
# -a --start_end_anywhere, --no-start_end_anywhere start_end_anywhere (boolean - not created)
# -c --config_file  provided_config (path spec - not created)
# -f --face_detect, --no-face_detect detect_faces (boolean - not created)

import configparser, os, argparse, time

# Global App Defaults
max_dimension = 50
sharpness = 1.0
bright_target = 224
start_end_anywhere = True
detect_faces = True

# Get Command Line Arguments
parser = argparse.ArgumentParser(prog='maze_image', usage='%(prog)s [options]')
parser.add_argument('input_file',  help="the graphics file to be converted")
parser.add_argument('-o','--output_file',  help="destination for the maze graphic files and maze metadata")
parser.add_argument('-d','--max_dimension', help="specify the max (width or height) of the output maze, default = 100",  type=int)
parser.add_argument('-s','--sharpness', help="specify the sharpening factor applied before generating the maze, default = 1",  type=float)
parser.add_argument('-b','--bright_target', help="specify the brightness target to be achieved before generating the maze, scale of 0-255, default = 224",  type=int)
parser.add_argument('-a','--start_end_anywhere',action=argparse.BooleanOptionalAction, help="optional argument, allows maze to start and end anywhere, not just on the edges")
parser.add_argument('-f','--face_detect',action=argparse.BooleanOptionalAction, help="optional argument, attempts to detect faces and exclude them from the maze paths")
parser.add_argument('-c','--config_file', help="specify the path to a custom config file not in the list of expected config files")
args=parser.parse_args()

# use config parser to get and resolve stored configurations
config = configparser.ConfigParser()
if args.config_file:
   config.read(['/etc/maze_image.conf', os.path.expanduser('~/.config/maze_image.conf'), './maze_image.conf', args.config_file])
else:
   config.read([ '/etc/maze_image.conf', os.path.expanduser('~/.config/maze_image.conf'), './maze_image.conf'])

if config.has_option('image processing', 'sharpness'):
    sharpness = config.getfloat('image processing', 'sharpness')

if config.has_option('image processing', 'bright_target'):
    bright_target = config.getint('image processing', 'bright_target')

if config.has_option('image processing', 'face_detect'):
    detect_faces = config.get('image processing', 'face_detect')

if config.has_option('maze generation', 'max_dimension'):
    max_dimension = config.getint('maze generation', 'max_dimension')
   
if config.has_option('maze generation', 'start_end_anywhere'):
    start_end_anywhere = config.get('maze generation', 'start_end_anywhere')

# Apply command line arguments
if args.max_dimension:
    max_dimension = args.max_dimension

if args.sharpness:
    sharpness = args.sharpness

if args.bright_target:
    bright_target = args.bright_target

if args.start_end_anywhere != None:
    start_end_anywhere = args.start_end_anywhere

if args.face_detect != None:
    detect_faces = args.face_detect

output_file = 'maze_image_' + time.strftime('%Y%m%d%H%M%S', time.gmtime())
if args.output_file:
    output_file = args.output_file


print ('sharpness = ', sharpness)
print ('bright_target = ', bright_target) 
print ('face_detect = ', detect_faces) 
print ('max_dimension = ', max_dimension) 
print ('start_end_anywhere = ', start_end_anywhere) 
print ('output_file = ', output_file) 




