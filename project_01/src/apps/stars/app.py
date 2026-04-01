"""
Glass app — renders a 360° panoramic image slice based on IMU yaw.

The device acts as a "window": rotating the device left/right pans through
the panorama. The IMU's current yaw (relative to calibration zero) selects
which 32-column slice to display.

To use a real panorama:
    1. Load a high-res equirectangular image and resize to 32 pixels tall.
    2. Save as a numpy array:  np.save('panorama.npy', frame)  shape (32, W, 3)
    3. Set PANORAMA_FILE below to the path of that file.
    4. Remove the placeholder _compute_frame() body and uncomment the real one.
"""

import math
import time
import numpy as np
from pathlib import Path

import yaml

from apps.base_app import BaseApp

PANORAMA_FILE = None   # Set to Path(...) when you have a real panorama


class App(BaseApp):
    """Glass app — panorama viewer driven by IMU yaw."""

    def __init__(self, hw):
        super().__init__(hw)
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.refresh_rate = config.get("refresh_rate", 15)

        # Load panorama if available
        self._panorama = None
        if PANORAMA_FILE is not None and Path(PANORAMA_FILE).exists():
            self._panorama = np.load(PANORAMA_FILE)  # expected shape: (32, W, 3)

    def run(self) -> None:
        while self.running:
            frame = self._compute_frame()
            self.hw.display.set_frame(frame)
            time.sleep(1 / self.refresh_rate)

    def _compute_frame(self) -> np.ndarray:
        """Return a 32x32x3 uint8 frame based on current IMU yaw."""
        if self._panorama is not None:
            # Real panorama path
            yaw       = self.hw.imu.get_yaw()                 # 0–360 deg
            pan_w     = self._panorama.shape[1]
            col_start = int((yaw / 360.0) * pan_w) % pan_w
            col_end   = col_start + 32

            if col_end <= pan_w:
                return self._panorama[:, col_start:col_end, :].copy()
            else:
                # Wrap around
                left  = self._panorama[:, col_start:, :]
                right = self._panorama[:, :col_end - pan_w, :]
                return np.concatenate([left, right], axis=1).copy()

        # Placeholder: pulsing colour that shifts with yaw so you can see IMU working
        t   = time.time()
        yaw = self.hw.imu.get_yaw()
        hue = (yaw / 360.0)  # 0–1
        r   = int((math.sin(t * 1.0 + hue * 6.28)       + 1) / 2 * 200)
        g   = int((math.sin(t * 1.5 + hue * 6.28 + 2.0) + 1) / 2 * 200)
        b   = int((math.sin(t * 0.8 + hue * 6.28 + 4.0) + 1) / 2 * 255)
        return np.full((32, 32, 3), [r, g, b], dtype=np.uint8)

    def cleanup(self) -> None:
        pass  # display already cleared by BaseApp.stop()

    def on_left(self) -> None:
        pass  # reserved for future brightness/offset controls

    def on_right(self) -> None:
        pass

    def on_select(self) -> None:
        pass
