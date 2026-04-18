import numpy as np

WIDTH = 64
HEIGHT = 32


class LEDMatrix:
    """
    Hardware interface for the 64x32 RGB LED Matrix (PocketBeagle + pyledscape).

    Accepts PIL Images (RGBX, 64x32) via draw(), which matches the Widget
    pattern used in the application layer. Numpy helpers (set_frame, set_pixel)
    are provided as a convenience shim.

    In simulation mode all hardware calls are no-ops; DebugDisplay reads
    pixel_data directly each frame.
    """

    def __init__(self):
        try:
            import pyledscape
            self._matrix = pyledscape.pyLEDscape()
            self.simulation = False
        except ImportError:
            self._matrix = None
            self.simulation = True

        if self.simulation:
            print("LEDMatrix initialized in SIMULATION mode.")

        self.pixel_data = PixelDataArray(WIDTH, HEIGHT)

    # ------------------------------------------------------------------
    # Primary interface (PIL Image)
    # ------------------------------------------------------------------

    def draw(self, image) -> None:
        """Send a PIL Image (mode RGBX or RGB, 64x32) to the panel."""
        # Keep pixel_data in sync for simulation / debug renderer
        rgb = image.convert("RGB")
        self.pixel_data.set_data(np.array(rgb, dtype=np.uint8))

        if not self.simulation:
            if image.mode != "RGBX":
                image = image.convert("RGBX")
            self._matrix.draw(image)

    # ------------------------------------------------------------------
    # Convenience numpy helpers
    # ------------------------------------------------------------------

    def set_frame(self, frame_data: np.ndarray) -> None:
        """Write a complete H×W×3 uint8 numpy array and push to panel."""
        self.pixel_data.set_data(frame_data)
        if not self.simulation:
            from PIL import Image
            img = Image.fromarray(frame_data, mode="RGB").convert("RGBX")
            self._matrix.draw(img)

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        self.pixel_data.set_pixel(x, y, r, g, b)
        if not self.simulation:
            from PIL import Image
            img = Image.fromarray(self.pixel_data.get_data(), mode="RGB").convert("RGBX")
            self._matrix.draw(img)

    def clear(self) -> None:
        from PIL import Image
        self.draw(Image.new("RGBX", (WIDTH, HEIGHT), "black"))

    def cleanup(self) -> None:
        pass

    def __del__(self):
        self.cleanup()

    def __enter__(self):
        return self

    def __str__(self):
        return f"LEDMatrix(simulation={self.simulation}, {WIDTH}x{HEIGHT})"


class PixelDataArray:
    """64x32 RGB pixel buffer (numpy-backed, used by simulation renderer)."""

    def __init__(self, width: int = WIDTH, height: int = HEIGHT):
        self.width = width
        self.height = height
        self.data = np.zeros((height, width, 3), dtype=np.uint8)

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y, x] = [r, g, b]
        else:
            raise ValueError(f"Pixel ({x},{y}) out of bounds for {self.width}x{self.height}")

    def set_data(self, new_data: np.ndarray) -> None:
        if new_data.shape == self.data.shape:
            self.data = new_data.copy()
        else:
            raise ValueError(f"Shape mismatch: expected {self.data.shape}, got {new_data.shape}")

    def clear(self) -> None:
        self.data.fill(0)

    def get_data(self) -> np.ndarray:
        return self.data
