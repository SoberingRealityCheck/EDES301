#!/usr/bin/python3
# Draw images with PIL and send them to the display.
# Dual scrolling example with fixed time on each side and
# the date scrolling around.
#
from PIL import Image, ImageFont, ImageDraw
import time, datetime
from colorsys import hsv_to_rgb
import io
import pyledscape


# print im.format, im.size, im.mode
# use a truetype font
font      = ImageFont.truetype("./fonts/spincycle.ttf", 24)

i         = 0
width     = 32
height    = 32

disp      = Image.new("RGBX", (width,height), "black")
im        = Image.new("RGBX", (width,height), "black")
im_draw   = ImageDraw.Draw(im)
disp_draw = ImageDraw.Draw(disp)

matrix    = pyledscape.pyLEDscape()

def rainbow(i):
	rgb = [int(x*256) for x in hsv_to_rgb(i/256.0, 0.8, 0.8)]
	return (rgb[0], rgb[1], rgb[2])


try:
    while True:
    	im.paste("black", (0, 0, width, height))
    	
    	text = "H i !"

    	# Draw the date 
    	im_draw.text((0, 0), text, font=font, fill=rainbow(i))

    	# Make it scroll
    	disp.paste(im.crop((0, 0, i, height)), (width-i, 0))
    	disp.paste(im.crop((i+1, 0, width-1, height)), (0,0))
    
    	# Draw image
    	try:
            matrix.draw(disp)

    	except Exception as e:
    		print("ERROR drawing image: \n\t{0}".format(e))
    		break;
    
    	i = (i+1) % width
    	time.sleep(0.025)

except KeyboardInterrupt:
    print("Stopping")




