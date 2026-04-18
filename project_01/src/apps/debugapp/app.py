"""
Debug app — cycles through test patterns to verify the display pipeline.

Left / right buttons step through patterns.
The app runs until the user presses back (handled by AppRunnerState).
"""

import time
import numpy as np
from apps.base_app import BaseApp


class App(BaseApp):
    """Debug app: left/right step through test patterns."""

    PATTERNS = ["checkerboard", "gradient", "border", "imu_yaw"]
    REFRESH_RATE = 15  # Hz

    def __init__(self, hw):
        super().__init__(hw)
        self._pattern_idx = 0

    def run(self) -> None:
        while self.running:
            frame = self._make_frame()
            self.hw.display.set_frame(frame)
            time.sleep(1 / self.REFRESH_RATE)

    def _make_frame(self) -> np.ndarray:
        frame   = np.zeros((32, 64, 3), dtype=np.uint8)
        pattern = self.PATTERNS[self._pattern_idx]

        if pattern == "checkerboard":
            for y in range(32):
                for x in range(64):
                    frame[y, x] = [200, 0, 0] if (x + y) % 2 == 0 else [0, 0, 200]

        elif pattern == "gradient":
            for x in range(64):
                v = int(x / 63 * 255)
                frame[:, x] = [0, v, 255 - v]

        elif pattern == "border":
            frame[0,  :] = [255, 255, 255]
            frame[31, :] = [255, 255, 255]
            frame[:,  0] = [255, 255, 255]
            frame[:, 63] = [255, 255, 255]

        elif pattern == "imu_yaw":
            # Visualize current yaw as a filled green bar (0–64 columns)
            yaw  = self.hw.imu.get_yaw()           # 0–360
            cols = int((yaw / 360.0) * 64)
            frame[:, :cols] = [0, 200, 50]
            frame[:, cols:] = [30, 30, 30]
            # White marker line
            if cols < 64:
                frame[:, cols] = [255, 255, 255]

        return frame

    def cleanup(self) -> None:
        pass

    def on_left(self) -> None:
        self._pattern_idx = (self._pattern_idx - 1) % len(self.PATTERNS)

    def on_right(self) -> None:
        self._pattern_idx = (self._pattern_idx + 1) % len(self.PATTERNS)

    def on_select(self) -> None:
        pass
