from PIL import Image, ImageFont, ImageDraw

import pyledscape
import time

WIDTH  = 32
HEIGHT = 32

im     = Image.new("RGBX", (WIDTH, HEIGHT), "white")

# data   = im.tobytes()
# print(data)
# print(len(data))

disp   = pyledscape.pyLEDscape()

try:
    disp.draw(im)
    time.sleep(5)
except:
    pass

disp.close()

