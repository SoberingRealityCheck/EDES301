import threading
from abc import ABC, abstractmethod


class BaseApp(ABC):
    """
    Abstract base class for all Window apps.

    Apps receive the full HardwareManager object and run their main loop on a
    background thread. The state machine (AppRunnerState) manages the app lifecycle:
        - Calls start() to launch
        - Polls is_done() each cycle
        - Calls stop() when done or when the user presses back

    Button responsibility:
        - Apps register on_left / on_right / on_select callbacks in start()
          and clear them in stop().
        - The BACK button is reserved for AppRunnerState — do NOT register it here.

    To signal self-completion from inside run(), set self._done = True.
    """

    def __init__(self, hw):
        """
        Args:
            hw : HardwareManager — provides hw.display, hw.imu, hw.buttons
        """
        self.hw      = hw
        self.running = False
        self._done   = False
        self._thread = None

    # ------------------------------------------------------------------
    # Lifecycle — called by AppRunnerState
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Clear display, run optional setup, register button callbacks, spawn run() thread."""
        self.hw.display.clear()
        self._setup()
        self.hw.buttons['left'].on_press_callback   = self.on_left
        self.hw.buttons['right'].on_press_callback  = self.on_right
        self.hw.buttons['select'].on_press_callback = self.on_select
        self.running = True
        self._thread = threading.Thread(target=self.run, daemon=True, name='app-runner')
        self._thread.start()

    def stop(self) -> None:
        """Signal run loop to exit, join thread, clear button callbacks, call cleanup."""
        self.running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self.hw.buttons['left'].on_press_callback   = None
        self.hw.buttons['right'].on_press_callback  = None
        self.hw.buttons['select'].on_press_callback = None
        self.cleanup()
        self.hw.display.clear()

    def is_done(self) -> bool:
        """Return True if the app has signaled completion from inside run()."""
        return self._done

    # ------------------------------------------------------------------
    # Hooks — override as needed
    # ------------------------------------------------------------------

    def _setup(self) -> None:
        """Optional pre-run initialization. Called before run() thread is spawned."""

    # ------------------------------------------------------------------
    # Abstract interface — must implement in subclass
    # ------------------------------------------------------------------

    @abstractmethod
    def run(self) -> None:
        """
        Main render loop. Must check self.running and exit when False.
        Set self._done = True to signal AppRunnerState that the app finished naturally.

        Example skeleton:
            def run(self):
                while self.running:
                    frame = self._compute_frame()
                    self.hw.display.set_frame(frame)
                    time.sleep(1 / self.refresh_rate)
        """

    @abstractmethod
    def cleanup(self) -> None:
        """Release any app-specific resources. Called after thread has stopped."""

    @abstractmethod
    def on_left(self) -> None:
        """Called when the left button is pressed."""

    @abstractmethod
    def on_right(self) -> None:
        """Called when the right button is pressed."""

    @abstractmethod
    def on_select(self) -> None:
        """Called when the select button is pressed."""
