"""
No-op GPIO stub for development on non-BeagleBone hardware.

Imported automatically by hardware drivers via try/except:
    try:
        import Adafruit_BBIO.GPIO as GPIO
    except ImportError:
        from hardware.stubs.gpio import GPIO

All pins read HIGH (logic-high), which means buttons are seen as unpressed
(pull-up configuration). Writes and setup calls are silently ignored.
"""

HIGH = 1
LOW  = 0
IN   = "in"
OUT  = "out"


def setup(pin, mode, **kwargs):
    pass


def input(pin):
    return HIGH  # All pins appear unpressed (pull-up default)


def output(pin, value):
    pass


def cleanup():
    pass
