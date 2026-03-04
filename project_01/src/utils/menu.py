""" 
Some sort of like, selection interface for moving between different apps. Operating system of the device.
"""

import os
import numpy as np 
import importlib

class AppPreview():
    """Class to represent the preview of an app in the main menu.
    """
    def __init__(self, name, icon, app):
        """Initialize the app preview.
        Args:
            - name: must be unique. will not be displayed externally
            - icon: the icon to display for the app
            - app: the app instance
        """
        self.name = name
        self.icon = icon
        self.app = app # the actual app class (i.e. WindowAppClass, FluidSimAppClass, etc.)


class MainMenu():
    """Class to represent the main menu of the device.
    """
    def __init__(self):
        """Initialize the main menu."""
        self.WIDTH = 32 
        self.HEIGHT = 32
        self.apps = []
        pass
    
    def load_apps(self):
        """Looks in the /apps directory for available apps and loads them into the menu.
        apps should contain:
            a main.py file with an App class that can be instantiated
            a name.txt file with the name of the app to be displayed in the menu
            an icon.npy file with a 32x32x3 array representing the icon to be displayed in the menu
        apps should be organized as follows:
/apps
    /app_1
        /src
            ...
        main.py
        name.txt
        icon.npy
    /app_2
        /src
            ...
        main.py
        name.txt
        icon.npy
    ...
        """
        app_dir = os.path.join("..", "apps")
        for app_name in os.listdir(app_dir):
            if os.path.isdir(os.path.join(app_dir, app_name)):
                # Load the app's main.py file and create an instance of the app class
                app_main_path = os.path.join(app_dir, app_name, "main.py")
                if os.path.exists(app_main_path):
                    # Dynamically import the app's main.py file
                    spec = importlib.util.spec_from_file_location(app_name, app_main_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Create an instance of the app class (assuming it's called "App")
                    if hasattr(module, "App"):
                        app_instance = module.App()
                        # Load the app's name and icon
                        name_path = os.path.join(app_dir, app_name, "name.txt")
                        icon_path = os.path.join(app_dir, app_name, "icon.npy")
                        if os.path.exists(name_path) and os.path.exists(icon_path):
                            with open(name_path, "r") as f:
                                name = f.read().strip()
                            icon = np.load(icon_path)
                            self.apps.append(AppPreview(name, icon, app_instance))
                        else:
                            print(f"Warning: {app_name} is missing name.txt or icon.npy")
                    else:
                        print(f"Warning: {app_name} does not have an App class in main.py")
                else:
                    print(f"Warning: {app_name} does not have a main.py file")

    def display(self):
        """Display the main menu."""
        # needs to be implemented
        pass

    def move_left(self):
        """Move the selection left."""
        # needs to be implemented
        pass

    def move_right(self):
        """Move the selection right."""
        # needs to be implemented
        pass

    def settings(self):
        """Display the settings menu."""
        # needs to be implemented
        pass
    
    def select_option(self, option):
        """Select an option from the main menu."""
        # needs to be implemented
        pass