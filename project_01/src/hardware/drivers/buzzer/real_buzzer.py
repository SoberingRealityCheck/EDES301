"""
Real buzzer driver — drives the HCW-KC1206 passive piezo via BeagleBone PWM.

The HCW-KC1206 is a passive piezo: it needs an external PWM signal at the
desired frequency to produce a tone. On the BeagleBone Black we use
Adafruit_BBIO.PWM, which wraps the kernel's PWM sysfs interface.

PWM pin must be a hardware-PWM-capable pin (e.g. "P9_21" or "P9_22").
Set BUZZER_PIN in src/config.yaml to the pin you're wiring to.

TODO: confirm the wiring pin before deploying.
"""

import threading
import time

from .buzzer_base import BuzzerBase

try:
    import Adafruit_BBIO.PWM as _PWM
    _HAS_BBIO = True
except ImportError:
    _HAS_BBIO = False


class RealBuzzer(BuzzerBase):
    """Passive piezo buzzer driven by BeagleBone hardware PWM."""

    DUTY_CYCLE = 50   # 50 % square wave — maximum amplitude for passive piezo

    def __init__(self, pin: str = "P9_21"):
        self._pin        = pin
        self._stop_event = threading.Event()
        self._pwm_active = False
        self._pwm_lock   = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def beep(self, freq: float, duration: float) -> None:
        threading.Thread(target=self._do_beep, args=(freq, duration), daemon=True).start()

    def play_sequence(self, notes: list) -> None:
        self._stop_event.clear()
        threading.Thread(target=self._run_seq, args=(notes,), daemon=True).start()

    def stop(self) -> None:
        self._stop_event.set()
        self._pwm_off()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _pwm_on(self, freq: float) -> None:
        if not _HAS_BBIO:
            return
        with self._pwm_lock:
            try:
                _PWM.start(self._pin, self.DUTY_CYCLE, freq)
                self._pwm_active = True
            except Exception as e:
                print(f"[RealBuzzer] PWM start failed: {e}")

    def _pwm_off(self) -> None:
        if not _HAS_BBIO:
            return
        with self._pwm_lock:
            if self._pwm_active:
                try:
                    _PWM.stop(self._pin)
                except Exception:
                    pass
                self._pwm_active = False

    def _do_beep(self, freq: float, duration: float) -> None:
        self._pwm_on(freq)
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            time.sleep(0.005)
        self._pwm_off()

    def _run_seq(self, notes: list) -> None:
        for freq, duration in notes:
            if self._stop_event.is_set():
                break
            if freq > 0:
                self._pwm_on(freq)
            else:
                self._pwm_off()  # rest
            deadline = time.monotonic() + duration
            while time.monotonic() < deadline:
                if self._stop_event.is_set():
                    break
                time.sleep(0.005)
        self._pwm_off()
