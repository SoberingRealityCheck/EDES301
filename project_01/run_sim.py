"""
Simulator entry point — Window to Another World.

Run from project_01/:
    python run_sim.py

Adds src/ to sys.path so all project modules are importable. The
Adafruit_BBIO stub is handled automatically via try/except inside each
driver — no sys.path tricks needed.

Controls:
    A          left button
    W          select button
    S          back button
    D          right button
    ← / →      virtual IMU yaw (rotate left / right)
    ↑ / ↓      virtual IMU pitch (tilt up / down)
    Escape / Q quit

Dependencies:
    uv sync 
    source venv/bin/activate  # if using the provided virtual environment
"""

import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "src"))

from hardware.drivers.imu.sim_imu import SimulatedIMU
from hardware.drivers.buzzer.sim_buzzer import SimBuzzer
from hardware import HardwareManager
from state_machine import StateMachine
from debug_display import DebugDisplay

if __name__ == "__main__":
    hw = HardwareManager(imu_class=SimulatedIMU, buzzer_class=SimBuzzer)
    sm = StateMachine(hw)
    sm.start()
    DebugDisplay(hw, sm).run()
