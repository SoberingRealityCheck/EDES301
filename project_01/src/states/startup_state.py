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
    """Display the splash screen located at
    src/states/assets/splash.npy as a 32x32x3 uint8 frame.

    Fades from black to full brightness over the first second, then
    holds at full brightness.

    If the file is missing or invalid, returns a solid magenta frame as a fallback.
    """
    splash_path = Path(__file__).parent / "assets" / "splash.npy"
    if splash_path.exists():
        splash = np.load(splash_path)
        if splash.shape == (32, 32, 3) and splash.dtype == np.uint8:
            return splash
    # Fallback: solid magenta if no valid splash found
    return np.full((32, 32, 3), [255, 0, 255], dtype=np.uint8)


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
