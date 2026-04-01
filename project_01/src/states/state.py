from abc import ABC, abstractmethod


class State(ABC):
    """
    Abstract base class for all state machine states.

    Lifecycle per activation:
        enter(hw, ctx)  — called once when state becomes active;
                          store hw/ctx and register button callbacks here
        update()        — called repeatedly by StateMachine at ~30 Hz;
                          return a transition name string to switch state, or None to stay
        exit()          — called once before transitioning away;
                          clear all button callbacks registered by this state

    Transition names (strings returned from update()):
        'boot'        → BootState
        'menu'        → MenuState
        'calibration' → CalibrationState
        'app_runner'  → AppRunnerState
    """

    def enter(self, hw, ctx: dict) -> None:
        """
        Called when this state is activated.

        Args:
            hw  : HardwareManager — owns display, imu, buttons
            ctx : shared dict that persists across all state transitions
        """
        self.hw  = hw
        self.ctx = ctx

    @abstractmethod
    def update(self) -> "str | None":
        """
        Called repeatedly at ~30 Hz. Return a transition name or None.
        Must not block for more than a few milliseconds.
        """

    def exit(self) -> None:
        """Called before leaving this state. Override to clear button callbacks."""
