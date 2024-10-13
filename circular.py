import math
from PIL import Image, ImageDraw

# declare variables
width = 4000
low_blue = 96
hi_blue = 224

# create image and drawing context
img = Image.new("RGB", (width, width), (0,0,low_blue))
dctx = ImageDraw.Draw(img)

color_direction = 1
color_step_size = 32
this_color = low_blue

widest_radius = int(math.sqrt(width*width+width*width)) + 1
print(widest_radius)
for radius in range(widest_radius, 0, -8):
    dctx.ellipse([(width/2 - radius, width/2-radius), (width/2+radius, width/2+radius)], (0,0,this_color), None, 0)
    if this_color >= hi_blue:
        color_direction = -1
    if this_color <= low_blue:
        color_direction = 1
    this_color = this_color + color_direction*color_step_size
img.save("out/circles1.png")

this_color = low_blue + 32
color_direction = 1


for radius in range(widest_radius, 0, -8):
    dctx.ellipse([(width/2 - radius, width/2-radius), (width/2+radius, width/2+radius)], (0,0,this_color), None, 0)
    if this_color >= hi_blue:
        color_direction = -1
    if this_color <= low_blue:
        color_direction = 1
    this_color = this_color + color_direction*color_step_size
img.save("out/circles2.png")

this_color = low_blue + 64
color_direction = 1

for radius in range(widest_radius, 0, -8):
    dctx.ellipse([(width/2 - radius, width/2-radius), (width/2+radius, width/2+radius)], (0,0,this_color), None, 0)
    if this_color >= hi_blue:
        color_direction = -1
    if this_color <= low_blue:
        color_direction = 1
    this_color = this_color + color_direction*color_step_size
img.save("out/circles3.png")

this_color = low_blue + 96
color_direction = 1

for radius in range(widest_radius, 0, -8):
    dctx.ellipse([(width/2 - radius, width/2-radius), (width/2+radius, width/2+radius)], (0,0,this_color), None, 0)
    if this_color >= hi_blue:
        color_direction = -1
    if this_color <= low_blue:
        color_direction = 1
    this_color = this_color + color_direction*color_step_size
img.save("out/circles4.png")

this_color = hi_blue
color_direction = -1

for radius in range(widest_radius, 0, -8):
    dctx.ellipse([(width/2 - radius, width/2-radius), (width/2+radius, width/2+radius)], (0,0,this_color), None, 0)
    if this_color >= hi_blue:
        color_direction = -1
    if this_color <= low_blue:
        color_direction = 1
    this_color = this_color + color_direction*color_step_size
img.save("out/circles5.png")

this_color = low_blue + 96
color_direction = -1

for radius in range(widest_radius, 0, -8):
    dctx.ellipse([(width/2 - radius, width/2-radius), (width/2+radius, width/2+radius)], (0,0,this_color), None, 0)
    if this_color >= hi_blue:
        color_direction = -1
    if this_color <= low_blue:
        color_direction = 1
    this_color = this_color + color_direction*color_step_size
img.save("out/circles6.png")

this_color = low_blue + 64
color_direction = -1

for radius in range(widest_radius, 0, -8):
    dctx.ellipse([(width/2 - radius, width/2-radius), (width/2+radius, width/2+radius)], (0,0,this_color), None, 0)
    if this_color >= hi_blue:
        color_direction = -1
    if this_color <= low_blue:
        color_direction = 1
    this_color = this_color + color_direction*color_step_size
img.save("out/circles7.png")

this_color = low_blue + 32
color_direction = -1


for radius in range(widest_radius, 0, -8):
    dctx.ellipse([(width/2 - radius, width/2-radius), (width/2+radius, width/2+radius)], (0,0,this_color), None, 0)
    if this_color >= hi_blue:
        color_direction = -1
    if this_color <= low_blue:
        color_direction = 1
    this_color = this_color + color_direction*color_step_size
img.save("out/circles8.png")
