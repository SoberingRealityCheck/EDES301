"""
Boot state — shows a splash screen for SPLASH_DURATION seconds then
transitions to the main menu. No button callbacks registered; buttons are
intentionally ignored during boot.
"""

import time
import numpy as np
from .state import State
from pathlib import Path

def _make_splash() -> np.ndarray:
    """Display the splash screen located at src/states/assets/splash.npy as a 32x32x3 uint8 frame."""
    splash_path = Path(__file__).parent / "assets" / "splash.npy"
    if splash_path.exists():
        splash = np.load(splash_path)
        if splash.shape == (32, 32, 3) and splash.dtype == np.uint8:
            return splash
    # Fallback: solid magenta if no valid splash found
    return np.full((32, 32, 3), [255, 0, 255], dtype=np.uint8)


class BootState(State):
    """Displays a splash frame for SPLASH_DURATION seconds, then → 'menu'."""

    SPLASH_DURATION = 2.0  # seconds

    # C5 → E5 → G5 → C6 rising arpeggio
    _BOOT_CHIME = [(523, 0.08), (0, 0.02), (659, 0.08), (0, 0.02),
                   (784, 0.08), (0, 0.02), (1047, 0.13)]

    def enter(self, hw, ctx: dict) -> None:
        super().enter(hw, ctx)
        self._start_time = time.time()
        hw.display.set_frame(_make_splash())
        hw.buzzer.play_sequence(self._BOOT_CHIME)

    def update(self) -> "str | None":
        if time.time() - self._start_time >= self.SPLASH_DURATION:
            return 'menu'
        return None

    def exit(self) -> None:
        pass  # no button callbacks to clear
