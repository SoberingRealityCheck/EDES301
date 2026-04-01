"""
Hardware entry point — Window to Another World (BeagleBone Black).

Run from project_01/src/ on the device:
    python run_device.py

Or from project_01/:
    python -c "import sys; sys.path.insert(0,'src'); exec(open('run_device.py').read())"

No pygame. StateMachine runs on the main thread.
"""

import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "src"))

from hardware.drivers.imu.real_imu import RealIMU
from hardware import HardwareManager
from state_machine import StateMachine

if __name__ == "__main__":
    hw = HardwareManager(imu_class=RealIMU)
    sm = StateMachine(hw)
    try:
        sm._loop()          # run on main thread (blocking)
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        sm.stop()
        hw.cleanup()
