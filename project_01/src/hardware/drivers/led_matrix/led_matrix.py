import numpy as np


class Adafruit607():
    """
    Hardware interface for the Adafruit 32x32 RGB LED Matrix.

    On real hardware this class drives the panel via GPIO.
    In simulation it is a no-op — DebugDisplay reads hw.display.pixel_data
    directly each frame and renders it to the pygame window.

    TODO: implement update() for real hardware when the panel arrives.
    """
    def __init__(self):
        pass

    def update(self, pixel_data: np.ndarray) -> None:
        """Send a 32x32x3 uint8 array to the panel. No-op in simulation."""
        pass


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


class LEDMatrix():
    """Interface to the 32x32 RGB LED matrix display."""

    def __init__(self, pins=None):
        self.pixel_data = PixelDataArray()
        self.display    = Adafruit607()

    def set_frame(self, frame_data: np.ndarray) -> None:
        """Write a complete 32x32x3 frame and push it to the panel."""
        self.pixel_data.set_data(frame_data)
        self.display.update(self.pixel_data.get_data())

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        self.pixel_data.set_pixel(x, y, r, g, b)

    def clear(self) -> None:
        self.pixel_data.clear()
        self.display.update(self.pixel_data.get_data())
