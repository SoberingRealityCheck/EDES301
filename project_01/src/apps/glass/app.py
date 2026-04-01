"""
Glass app — renders a 360° panoramic image slice based on IMU pitch and yaw.

The device acts as a "window": rotating the device left/right and up/down pans
through the panorama. The IMU's current yaw and pitch (relative to calibration zero) 
select which 32x32 slice to display.

The frame is actually a downscaled portion of the image, based on a customizable FOV 
parameter. Pressing the left and right buttons adjusts the FOV, 
allowing you to zoom in and out of the panorama. The FOV is applied symmetrically in both
directions, so a smaller FOV means a smaller slice of the panorama is stretched to fill the 32x32 display.

Upon initializing the program, the app maps the top and bottom of the panorama to the possible
180 degrees of pitch, and the left and right edges to the 360 degrees of yaw. The app then continuously
reads the current yaw and pitch from the IMU, calculates the corresponding slice of the panorama 
based on the FOV, and displays it on the screen. 

The result is an immersive experience where you can explore the panorama by simply moving the device around!

To use a real panorama:
    1. Load a high-res pixel image.
    2. Rename to panorama.png and place in the same directory as this file.
    3. Run png_to_npy.py to convert it to panorama.npy.
    4. Set PANORAMA_FILE below to the path of that .npy file.
"""

import math
import time
import numpy as np
from pathlib import Path

import yaml

from apps.base_app import BaseApp

PANORAMA_FILE = "src/apps/glass/panorama.npy"   # Set to Path(...) when you have a real panorama


class App(BaseApp):
    """Glass app — panorama viewer driven by IMU yaw and pitch."""

    def __init__(self, hw):
        super().__init__(hw)
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.refresh_rate = config.get("refresh_rate", 15)
        self.debug = bool(config.get("debug", False))

        self.fov = config.get("fov", 10)  # Field of view in degrees, adjustable with buttons

        # Load panorama if available
        self._panorama = None
        if PANORAMA_FILE is not None and Path(PANORAMA_FILE).exists():
            print("Loading panorama from", PANORAMA_FILE)
            self._panorama = np.load(PANORAMA_FILE)  # expected shape: (H, W, 3) where H is typically 32 but can be larger if you want vertical FOV > 90 deg
        else:
            print("No panorama found at", PANORAMA_FILE, "- using placeholder display")


    def run(self) -> None:
        while self.running:
            frame = self._compute_frame()
            self.hw.display.set_frame(frame)
            time.sleep(1 / self.refresh_rate)

    def compute_pixel_center(self, yaw, pitch):
        """Convert yaw and pitch to pixel coordinates in the panorama."""
        pan_h, pan_w, _ = self._panorama.shape
        yaw_norm = yaw % 360.0
        pitch_clamped = max(-90.0, min(90.0, pitch))

        x = (yaw_norm / 360.0) * pan_w
        # Invert vertical mapping: +pitch looks up (toward smaller image y).
        y = ((90.0 - pitch_clamped) / 180.0) * (pan_h - 1)
        return x, y

    def compute_fov_pixels(self):
        """Convert the current FOV in degrees to pixel dimensions in the panorama."""
        pan_h, pan_w, _ = self._panorama.shape
        # Clamp FOV in pixels so slice dimensions are never zero or out of bounds.
        fov_x = max(1, min(pan_w, int((self.fov / 360.0) * pan_w)))
        fov_y = max(1, min(pan_h, int((self.fov / 180.0) * pan_h)))
        return fov_x, fov_y

    def _compute_frame(self) -> np.ndarray:
        """Return a 32x32x3 uint8 frame based on current IMU yaw and pitch."""
        if self._panorama is not None:
            yaw   = self.hw.imu.get_yaw()   # 0–360 deg
            pitch = self.hw.imu.get_pitch() # -90–90 deg

            center_x, center_y = self.compute_pixel_center(yaw, pitch)
            fov_x, fov_y = self.compute_fov_pixels()
            frame = self._sample_panorama_bilinear(center_x, center_y, fov_x, fov_y)
            if self.debug:
                print("Frame Data:")
                print("  Yaw:", yaw)
                print("  Pitch:", pitch)
                print("  Center:", center_x, center_y)
                print("  FOV:", fov_x, fov_y)
                print("  Frame shape:", frame.shape)
                print("  Frame pixel range:", frame.min(), "-", frame.max())
            return frame


        # Placeholder: pulsing colour that shifts with yaw and pitch so you can see IMU working
        t     = time.time()
        yaw   = self.hw.imu.get_yaw()
        pitch = self.hw.imu.get_pitch()
        r     = int((math.sin(t * 1.0 + yaw / 360.0 * math.pi * 2) + 1) / 2 * 200)
        g     = int((math.sin(t * 1.5 + pitch / 180.0 * math.pi + 2.0) + 1) / 2 * 200)
        b     = int((math.sin(t * 0.8 + yaw / 360.0 * math.pi * 4 + pitch / 180.0 * math.pi * 2 + 4.0) + 1) / 2 * 255)
        return np.full((32, 32, 3), [r, g, b], dtype=np.uint8)

    def cleanup(self) -> None:
        pass  # display already cleared by BaseApp.stop()

    def on_left(self) -> None:
        self.fov = max(5, self.fov - 5)  # Decrease FOV to zoom in

    def on_right(self) -> None:
        self.fov = min(90, self.fov + 5)  # Increase FOV to zoom out

    def on_select(self) -> None:
        pass

    def _sample_panorama_bilinear(self, center_x, center_y, fov_x, fov_y) -> np.ndarray:
        """Sample a 32x32 view with bilinear interpolation from fractional coordinates."""
        pan_h, pan_w, _ = self._panorama.shape

        # Pixel-center aligned sampling grid over the requested FOV window.
        x_offsets = (np.arange(32, dtype=np.float32) + 0.5 - 16.0) * (fov_x / 32.0)
        y_offsets = (np.arange(32, dtype=np.float32) + 0.5 - 16.0) * (fov_y / 32.0)
        grid_x, grid_y = np.meshgrid(center_x + x_offsets, center_y + y_offsets)

        # Panorama wraps horizontally and clamps vertically.
        grid_x = np.mod(grid_x, pan_w)
        grid_y = np.clip(grid_y, 0.0, pan_h - 1.0)

        x0 = np.floor(grid_x).astype(np.int32)
        y0 = np.floor(grid_y).astype(np.int32)
        x1 = (x0 + 1) % pan_w
        y1 = np.minimum(y0 + 1, pan_h - 1)

        wx = (grid_x - x0)[..., None]
        wy = (grid_y - y0)[..., None]

        c00 = self._panorama[y0, x0].astype(np.float32)
        c10 = self._panorama[y0, x1].astype(np.float32)
        c01 = self._panorama[y1, x0].astype(np.float32)
        c11 = self._panorama[y1, x1].astype(np.float32)

        top = c00 * (1.0 - wx) + c10 * wx
        bot = c01 * (1.0 - wx) + c11 * wx
        out = top * (1.0 - wy) + bot * wy
        return np.clip(out, 0, 255).astype(np.uint8)
