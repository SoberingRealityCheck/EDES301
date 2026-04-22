"""
HardwareManager — single object that owns all hardware.

Instantiate once and pass everywhere. All hardware components are
accessible as attributes:

    hw.display   : LEDMatrix
    hw.imu       : IMUBase subclass (SimulatedIMU in sim, RealIMU on device)
    hw.buttons   : dict{'left','right','select','back'} → Button

Button polling threads are daemon threads started in __init__. Each thread
loops on button.wait_for_press() so that registered on_press_callback
functions fire automatically when a physical button is pressed.

For the simulator, call hw.simulate_press('left') etc. to directly invoke
the currently registered callback without a physical press.
"""

import threading
from pathlib import Path

import yaml

from hardware.drivers.led_matrix.led_matrix import LEDMatrix
from hardware.drivers.button.button import Button
from hardware.drivers.imu.real_imu import RealIMU          # default for on-device
from hardware.drivers.buzzer.real_buzzer import RealBuzzer  # default for on-device


_config_path = Path(__file__).parent.parent / "config.yaml"
with open(_config_path, "r") as _f:
    _config = yaml.safe_load(_f)


class HardwareManager:
    """
    Central hardware owner. Construct once; pass to states and apps.

    Args:
        imu_class : class to instantiate as self.imu.
                    Default: RealIMU. Pass SimulatedIMU for development.
    """

    def __init__(self, imu_class=None, buzzer_class=None):
        if imu_class is None:
            imu_class = RealIMU
        if buzzer_class is None:
            buzzer_class = RealBuzzer

        # Display
        self.display = LEDMatrix()

        # Buzzer
        self.buzzer = buzzer_class(pin=_config.get("BUZZER_PIN", "P9_21"))

        # IMU
        self.imu = imu_class()
        self.imu.start()

        # Buttons — keyed by logical name
        self.buttons = {
            'left':   Button(_config["LEFT_BUTTON_PIN"],   press_low=False),
            'right':  Button(_config["RIGHT_BUTTON_PIN"],  press_low=False),
            'select': Button(_config["SELECT_BUTTON_PIN"], press_low=False),
            'back':   Button(_config["BACK_BUTTON_PIN"],   press_low=False),
        }

        self._start_button_threads()

    # ------------------------------------------------------------------
    # Button polling threads
    # ------------------------------------------------------------------

    def _start_button_threads(self) -> None:
        """Spawn one daemon thread per button that loops on wait_for_press()."""
        for name, button in self.buttons.items():
            t = threading.Thread(
                target=self._button_loop,
                args=(button,),
                daemon=True,
                name=f'btn-{name}',
            )
            t.start()

    def _button_loop(self, button: Button) -> None:
        """Loop target: call wait_for_press() indefinitely."""
        while True:
            button.wait_for_press()

    # ------------------------------------------------------------------
    # Simulator bridge
    # ------------------------------------------------------------------

    def simulate_press(self, button_name: str) -> None:
        """
        Directly invoke the on_press_callback for a button by name.
        Called by DebugDisplay on keyboard events.

        Does nothing if the button has no callback registered (safe to call
        any time regardless of which state is active).
        """
        button = self.buttons.get(button_name)
        if button is None:
            return
        cb = button.on_press_callback
        if cb is not None:
            cb()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """Stop IMU thread and clear the display."""
        self.imu.stop()
        self.display.clear()
