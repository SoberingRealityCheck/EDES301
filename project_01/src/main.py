"""
Blah Blah Blah Description etc etc etc 

license etc etc etc
"""


from utils.drivers.led_matrix.led_matrix import LEDMatrix
from utils.drivers.button.button import Button
from utils.drivers.usr3_led.usr3_led import USR3_LED

import yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


LEFT_BUTTON_PIN = config["LEFT_BUTTON_PIN"] 
RIGHT_BUTTON_PIN = config["RIGHT_BUTTON_PIN"]
SELECT_BUTTON_PIN = config["SELECT_BUTTON_PIN"]
BACK_BUTTON_PIN = config["BACK_BUTTON_PIN"]
I2C_SDA_PIN = config["I2C_SDA_PIN"]
I2C_SCL_PIN = config["I2C_SCL_PIN"]
DISPLAY_GPIO_PINS = config["DISPLAY_GPIO_PINS"]


class WindowDevice:
    """ 
    Class to represent the main 'Window to Another World' device. 
    This class will be the main interface for the program, and will contain the main 
    loop along with the setup and cleanup functions. 
    """
    def __init__(self):
        """Initialize the hardware components."""
        # Initialize Display
        self.display = LEDMatrix(DISPLAY_GPIO_PINS) # this will need to be the LED matrix interface
        
        # Initialize Buttons
        self.left_button = Button(LEFT_BUTTON_PIN)
        self.right_button = Button(RIGHT_BUTTON_PIN)
        self.select_button = Button(SELECT_BUTTON_PIN)
        self.back_button = Button(BACK_BUTTON_PIN)

        # Time threshold for resetting the people count (in seconds)
        self.reset_time = 2.0
