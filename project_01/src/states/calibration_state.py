"""
Calibration state — requires the device to be held still for
STILLNESS_DURATION seconds before zeroing the IMU and launching the app.

Visual feedback: a 32-pixel wide progress bar fills left-to-right from
red to green as the still timer accumulates. Motion resets the bar.

Back button returns to the menu without launching.
"""

import numpy as np
from .state import State


class CalibrationState(State):
    """
    Waits for hw.imu.is_still() to be True for STILLNESS_DURATION seconds.
    When satisfied: calls hw.imu.zero() and transitions to 'app_runner'.
    Back button: transitions to 'menu'.
    """

    STILLNESS_DURATION  = 2.0   # seconds of continuous stillness required
    STILLNESS_THRESHOLD = 2.0   # deg/s — passed to imu.is_still()
    UPDATE_RATE_HZ      = 30.0  # state machine tick rate (for dt calculation)

    def enter(self, hw, ctx: dict) -> None:
        super().enter(hw, ctx)
        self._still_time = 0.0
        self._next_state = None
        self._dt         = 1.0 / self.UPDATE_RATE_HZ

        hw.buttons['back'].on_press_callback   = self._on_back
        hw.buttons['left'].on_press_callback   = None
        hw.buttons['right'].on_press_callback  = None
        hw.buttons['select'].on_press_callback = None

        self._render_progress(0.0)
        print("[Calibration] Hold still for 2 seconds…")

    def update(self) -> "str | None":
        if self._next_state is not None:
            return self._next_state

        if self.hw.imu.is_still(self.STILLNESS_THRESHOLD):
            self._still_time += self._dt
            progress = min(self._still_time / self.STILLNESS_DURATION, 1.0)
            self._render_progress(progress)

            if self._still_time >= self.STILLNESS_DURATION:
                self.hw.imu.zero()
                print("[Calibration] IMU zeroed — launching app.")
                return 'app_runner'
        else:
            if self._still_time > 0.0:
                print("[Calibration] Motion detected — resetting timer.")
            self._still_time = 0.0
            self._render_progress(0.0)

        return None

    def exit(self) -> None:
        self.hw.buttons['back'].on_press_callback = None

    def _on_back(self) -> None:
        print("[Calibration] Back → menu.")
        self._next_state = 'menu'

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def _render_progress(self, progress: float) -> None:
        """
        Draw a horizontal progress bar.
        progress : float in [0.0, 1.0]
        Left portion is green (filled), right is red (unfilled).
        """
        frame      = np.zeros((32, 64, 3), dtype=np.uint8)
        filled_cols = int(round(progress * 64))

        # Filled (green)
        if filled_cols > 0:
            frame[:, :filled_cols] = [0, 220, 80]

        # Unfilled (dim red)
        if filled_cols < 64:
            frame[:, filled_cols:] = [120, 20, 20]

        # Bright dividing line
        if 0 < filled_cols < 64:
            frame[:, filled_cols - 1] = [255, 255, 255]

        self.hw.display.set_frame(frame)
