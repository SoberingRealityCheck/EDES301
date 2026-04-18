"""
Boot state — displays a black screen briefly to let pygame fully initialise
before any audio plays, then transitions to StartupState.
"""

import time
import numpy as np
from .state import State


class BootState(State):
    """Black screen for BOOT_DURATION seconds, then → 'startup'."""

    BOOT_DURATION = 0.5  # seconds — enough for pygame audio to stabilise

    def enter(self, hw, ctx: dict) -> None:
        super().enter(hw, ctx)
        self._start_time = time.time()
        hw.display.set_frame(np.zeros((32, 64, 3), dtype=np.uint8))

    def update(self) -> "str | None":
        if time.time() - self._start_time >= self.BOOT_DURATION:
            return 'startup'
        return None

    def exit(self) -> None:
        pass
