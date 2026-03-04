""" 
main app code
"""





import yaml


class App():
    """Class representing the Glass app. 
    This class will contain the main loop for the app, as well as any setup and cleanup functions. 

    Methods:
        App(): constructor for the app, initializes the display and buttons
        _setup(): setup function for the app, initializes the hardware components
        run(): main loop for the app, contains the main logic for the app
        cleanup(): cleanup function for the app, cleans up the hardware components

        Lbutton_callback(): callback function for the left button, called when the left button is pressed
        Rbutton_callback(): callback function for the right button, called when the right button is pressed
        Bbutton_callback(): callback function for the bottom button, called when the bottom button is pressed
        Abutton_callback(): callback function for the top button, called when the top button is pressed
    """
    def __init__(self, display, buttons):
        """Initialize the app with the given display and buttons."""
        self.display = display
        self.buttons = buttons

        # import all args from the config file as attributes of the class
        with open("config.yaml", "r") as f: # this is the config file located in the same directory as this main.py file
            config = yaml.safe_load(f)
        for key, value in config.items():
            setattr(self, key, value)



