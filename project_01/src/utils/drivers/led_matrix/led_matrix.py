import numpy as np


""" 
Going to need some sort of hardware interface class here as well for the LED matrix, and 
a bunch of config info as well for like pin numbers and stuff. I could totally hardcode the pins
but i would rather actually set them via args so this driver is more generalized.
"""

class Adafruit607():
    """ Hardware Interface class for the Adafruit 32x32 RGB LED Matrix. """
    def __init__(self, i2c_bus=1, i2c_address=0x70):
        """Initialize the hardware interface."""
        pass

class PixelDataArray():
    """Class to represent the pixel data for the LED matrix display."""
    def __init__(self, width=32, height=32):
        """Initialize the pixel data array."""
        self.width = width
        self.height = height
        self.data = np.zeros((self.height, self.width, 3), dtype=np.uint8) # 3 for RGB channels
    
    def set_pixel(self, x, y, r, g, b):
        """Set the color of a specific pixel."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y, x] = [r, g, b]
        else:
            raise ValueError("Pixel coordinates out of bounds")
    
    def clear(self):
        """Clear the pixel data array."""
        self.data.fill(0)
    
    def get_data(self):
        """Get the pixel data array."""
        return self.data
    
    def set_data(self, new_data):
        """Update the pixel data array with new data."""
        if new_data.shape == self.data.shape:
            self.data = new_data
        else:
            raise ValueError("New data shape does not match pixel data array shape")
        

class LEDMatrix():
    """Class to represent the LED matrix display."""
    def __init__(self, pins):
        """Initialize the LED matrix."""
        # stores data as 32 x 32 x 3 array of RGB values (0-255)
        self.pixel_data = PixelDataArray()
        self.display = None # this will need to be the actual LED matrix interface 
        pass
    
    def update(self, pixel_data):
        """Update the LED matrix with the given pixel data.
        Data should be a 32x32x3 array of RGB values (0-255).
        """
        self.display.update(pixel_data.get_data())

    def clear(self):
        """Clear the display."""
        self.pixel_data.clear()

    def set_pixel(self, x, y, r, g, b):
        """Set the color of a specific pixel."""
        self.pixel_data.set_pixel(x, y, r, g, b)

    def set_frame(self, frame_data):
        """Set the entire frame of the display with the given data."""
        self.pixel_data.set_data(frame_data)
        self.update()
        