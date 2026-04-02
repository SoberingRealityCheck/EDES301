"""
StateMachine — owns all states and drives the update loop.

The loop runs on a daemon thread at STATE_MACHINE_HZ. The main thread
(DebugDisplay or run_device.py) calls start() and stop().

Transition flow:
    current_state.update() returns a string → _transition(string)
    _transition calls exit() on the old state, enter() on the new one.

All states share a single ctx dict that persists across transitions.
"""

import time
import threading

from states.boot_state         import BootState
from states.startup_state      import StartupState
from states.menu_state         import MenuState
from states.calibration_state  import CalibrationState
from states.app_runner_state   import AppRunnerState


STATE_MACHINE_HZ = 30.0


class StateMachine:
    """
    Manages state transitions and runs the update loop on a daemon thread.

    Usage:
        sm = StateMachine(hw)
        sm.start()          # spawns background thread
        ...
        sm.stop()           # signals thread to exit and waits
    """

    _STATE_MAP = {
        'boot':        BootState,
        'startup':     StartupState,
        'menu':        MenuState,
        'calibration': CalibrationState,
        'app_runner':  AppRunnerState,
    }

    def __init__(self, hw):
        """
        Args:
            hw : HardwareManager
        """
        self.hw  = hw
        self.ctx = {}

        # Build one instance of each state (they are reused across transitions)
        self._states = {name: cls() for name, cls in self._STATE_MAP.items()}

        self._current_name  = 'boot'
        self._current_state = self._states['boot']
        self._current_state.enter(hw, self.ctx)

        self._running = False
        self._thread  = None

    # ------------------------------------------------------------------
    # Thread lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Spawn the state-machine daemon thread."""
        self._running = True
        self._thread  = threading.Thread(
            target=self._loop, daemon=True, name='state-machine'
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the loop to exit and wait for the thread."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    # ------------------------------------------------------------------
    # Loop
    # ------------------------------------------------------------------

    def _loop(self) -> None:
        interval = 1.0 / STATE_MACHINE_HZ
        while self._running:
            t0         = time.time()
            next_name  = self._current_state.update()
            if next_name is not None:
                self._transition(next_name)
            elapsed = time.time() - t0
            sleep   = interval - elapsed
            if sleep > 0:
                time.sleep(sleep)

    def _transition(self, name: str) -> None:
        if name not in self._states:
            print(f"[StateMachine] Unknown state '{name}' — ignoring.")
            return
        print(f"[StateMachine] {self._current_name} → {name}")
        self._current_state.exit()
        self._current_name  = name
        self._current_state = self._states[name]
        self._current_state.enter(self.hw, self.ctx)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    @property
    def current_state_name(self) -> str:
        """Return the name of the active state. Used by DebugDisplay title bar."""
        return self._current_name
