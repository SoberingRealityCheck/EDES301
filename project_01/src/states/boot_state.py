"""
Boot state — shows a splash screen for SPLASH_DURATION seconds then
transitions to the main menu. No button callbacks registered; buttons are
intentionally ignored during boot.
"""

import time
import numpy as np
from .state import State


def _make_splash() -> np.ndarray:
    """Generate a simple 32x32 splash frame: dark background, bright border."""
    frame = np.zeros((32, 32, 3), dtype=np.uint8)
    # Outer border — cyan
    frame[0,  :] = [0, 200, 200]
    frame[31, :] = [0, 200, 200]
    frame[:,  0] = [0, 200, 200]
    frame[:, 31] = [0, 200, 200]
    # Inner cross
    frame[15:17, 8:24] = [0, 100, 180]
    frame[8:24, 15:17] = [0, 100, 180]
    return frame


class BootState(State):
    """Displays a splash frame for SPLASH_DURATION seconds, then → 'menu'."""

    SPLASH_DURATION = 2.0  # seconds

    def enter(self, hw, ctx: dict) -> None:
        super().enter(hw, ctx)
        self._start_time = time.time()
        hw.display.set_frame(_make_splash())

    def update(self) -> "str | None":
        if time.time() - self._start_time >= self.SPLASH_DURATION:
            return 'menu'
        return None

    def exit(self) -> None:
        pass  # no button callbacks to clear
