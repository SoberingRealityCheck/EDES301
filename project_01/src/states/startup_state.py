"""
Startup state — shows a splash screen with chime for SPLASH_DURATION seconds
then transitions to the main menu. Entered from BootState after pygame is
fully initialised so audio plays cleanly.
"""

import time
import numpy as np
from .state import State
from pathlib import Path


def _make_splash() -> np.ndarray:
    """Load splash.npy (32x32x3) and center it on a 32x64 frame.

    Falls back to a solid magenta 32x64 frame if the file is missing or invalid.
    """
    frame = np.zeros((32, 64, 3), dtype=np.uint8)
    splash_path = Path(__file__).parent / "assets" / "splash.npy"
    if splash_path.exists():
        splash = np.load(splash_path)
        if splash.shape == (32, 32, 3) and splash.dtype == np.uint8:
            frame[:, 16:48] = splash
            return frame
    frame[:, 16:48] = 255  # magenta fallback centered
    frame[:, 16:48, 1] = 0
    return frame


class StartupState(State):
    """Fades into a splash frame for SPLASH_DURATION seconds, then → 'menu'."""

    SPLASH_DURATION = 2.0  # seconds

    # G#5 -> G5 -> F5 -> F5 -> G5
    # hehehe
    _BOOT_CHIME = [
        (830, 0.2),
        (784, 0.2),
        (698, 0.2),
        (698, 0.2),
        (784, 0.2)
    ]

    def enter(self, hw, ctx: dict) -> None:
        super().enter(hw, ctx)
        self._start_time = time.time()
        hw.display.set_frame(_make_splash())
        hw.buzzer.play_sequence(self._BOOT_CHIME)

    def update(self) -> "str | None":
        self.brightness = min(1.0, (time.time() - self._start_time) / self.SPLASH_DURATION)
        self.hw.display.set_frame((self.brightness * _make_splash()).astype(np.uint8))
        if time.time() - self._start_time >= self.SPLASH_DURATION:
            return 'menu'
        return None

    def exit(self) -> None:
        pass
