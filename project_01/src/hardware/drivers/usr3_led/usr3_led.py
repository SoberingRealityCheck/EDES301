"""
USR3 LED driver for the BeagleBone Black onboard LED.
Falls back to a no-op stub on non-BeagleBone hardware.
"""
import time

try:
    import Adafruit_BBIO.GPIO as GPIO
except ImportError:
    from hardware.stubs import gpio as GPIO


class USR3LED:
    def __init__(self):
        GPIO.setup("USR3", GPIO.OUT)

    def on(self):
        GPIO.output("USR3", GPIO.HIGH)

    def off(self):
        GPIO.output("USR3", GPIO.LOW)


def main():
    light = USR3LED()
    while True:
        light.on()
        time.sleep(0.1)
        light.off()
        time.sleep(0.1)
