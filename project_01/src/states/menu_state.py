"""
Menu state — displays app icons on the LED matrix and lets the user cycle
through them with left/right buttons. Pressing select transitions to
CalibrationState and stores the chosen app in ctx['selected_app'].
"""

from pathlib import Path

import numpy as np

from .state import State
from hardware.apps_loader import scan_apps, AppEntry


class MenuState(State):
    """
    Left / right cycle through loaded apps.
    Select → write ctx['selected_app'] and transition to 'calibration'.
    Back  → no-op (already at the root).
    """

    def enter(self, hw, ctx: dict) -> None:
        super().enter(hw, ctx)

        # Load apps once; cache for the lifetime of this state instance
        if not hasattr(self, '_apps'):
            apps_dir = Path(__file__).parent.parent / "apps"
            self._apps = scan_apps(apps_dir)
            self._idx  = 0

        self._next_state    = None
        self._display_dirty = True  # force initial render

        if not self._apps:
            print("[MenuState] No apps found.")

        # Register button callbacks
        hw.buttons['left'].on_press_callback   = self._on_left
        hw.buttons['right'].on_press_callback  = self._on_right
        hw.buttons['select'].on_press_callback = self._on_select
        hw.buttons['back'].on_press_callback   = None

    def update(self) -> "str | None":
        if self._display_dirty and self._apps:
            self.hw.display.set_frame(self._apps[self._idx].icon)
            self._display_dirty = False

        if self._next_state is not None:
            return self._next_state

        return None

    def exit(self) -> None:
        self.hw.buttons['left'].on_press_callback   = None
        self.hw.buttons['right'].on_press_callback  = None
        self.hw.buttons['select'].on_press_callback = None

    # ------------------------------------------------------------------
    # Button callbacks (called from btn-* threads)
    # ------------------------------------------------------------------

    def _on_left(self) -> None:
        if not self._apps:
            return
        self._idx = (self._idx - 1) % len(self._apps)
        self._display_dirty = True
        print(f"[Menu] ← {self._apps[self._idx].name}")

    def _on_right(self) -> None:
        if not self._apps:
            return
        self._idx = (self._idx + 1) % len(self._apps)
        self._display_dirty = True
        print(f"[Menu] → {self._apps[self._idx].name}")

    def _on_select(self) -> None:
        if not self._apps:
            return
        self.ctx['selected_app'] = self._apps[self._idx]
        self._next_state = 'calibration'
        print(f"[Menu] Selected: {self._apps[self._idx].name}")
