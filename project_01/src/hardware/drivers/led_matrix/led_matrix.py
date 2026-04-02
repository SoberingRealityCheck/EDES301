import numpy as np
from .led_strip.opc import Client
import time


class LEDMatrix():
    """
    Hardware interface for the Adafruit 32x32 RGB LED Matrix.

    On real hardware this class drives the panel via GPIO.
    In simulation it is a no-op — DebugDisplay reads hw.display.pixel_data
    directly each frame and renders it to the pygame window.
    """
    def __init__(self, pins=None):
        try: 
            import Adafruit_BBIO.GPIO as GPIO
            self.simulation = False
        except ImportError:
            self.simulation = True
        
        if self.simulation:
            print("LEDMatrix initialized in SIMULATION mode.")
        else:
            self.opc_client = Client('localhost:7890')
            time.sleep(1) # give it a sec to startup
            assert self.opc_client.can_connect(), "Could not connect to OPC server at localhost:7890"
            
        self.pixel_data = PixelDataArray()

    def update(self) -> None:
        """Send a 32x32x3 uint8 array to the panel. No-op in simulation."""
        # check to see if we're running in simulation or on real hardware
        if not self.simulation:
            self.opc_client.put_pixels(self.pixel_data.get_data().reshape(-1, 3).tolist(), channel=0)

    def set_frame(self, frame_data: np.ndarray) -> None:
        """Write a complete 32x32x3 frame and push it to the panel."""
        self.pixel_data.set_data(frame_data)
        self.update()

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        self.pixel_data.set_pixel(x, y, r, g, b)
        self.update()

    def clear(self) -> None:
        self.pixel_data.clear()
        self.update()
    
    def cleanup(self) -> None:
        """Cleanup resources. No-op for the LED matrix."""
        pass

    # random methods that might be useful for debugging or something
    def __del__(self):
        self.cleanup()
    
    def __enter__(self):
        return self

    def __str__(self):
        return f"LEDMatrix(simulation={self.simulation})"
    


class PixelDataArray():
    """32x32 RGB pixel buffer."""

    def __init__(self, width: int = 32, height: int = 32):
        self.width  = width
        self.height = height
        self.data   = np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y, x] = [r, g, b]
        else:
            raise ValueError("Pixel coordinates out of bounds")
        
    def set_data(self, new_data: np.ndarray) -> None:
        if new_data.shape == self.data.shape:
            self.data = new_data.copy()
        else:
            raise ValueError(
                f"Shape mismatch: expected {self.data.shape}, got {new_data.shape}"
            )

    def clear(self) -> None:
        self.data.fill(0)

    def get_data(self) -> np.ndarray:
        return self.data

    def set_data(self, new_data: np.ndarray) -> None:
        if new_data.shape == self.data.shape:
            self.data = new_data.copy()
        else:
            raise ValueError(
                f"Shape mismatch: expected {self.data.shape}, got {new_data.shape}"
            )

