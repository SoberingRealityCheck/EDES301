"""
Simulated IMU for development without hardware.

DebugDisplay calls inject_rotation() on arrow KEY_DOWN events and
inject_rotation(axis, 0) on KEY_UP events. The integration thread in
IMUBase picks up the injected values via _read_raw() on every tick.

When no arrow keys are held, gyro returns (0,0,0), so is_still() returns
True and CalibrationState will proceed automatically after its 2-second
timer.
"""

import threading
import numpy as np
from .imu_base import IMUBase, GRAVITY


class SimulatedIMU(IMUBase):
    """
    IMU driven by keyboard arrow keys instead of real sensor hardware.

    Inject rotation rates (deg/s) from DebugDisplay:
        hw.imu.inject_rotation('yaw',   rate)   # ← / → arrows
        hw.imu.inject_rotation('pitch', rate)   # ↑ / ↓ arrows
        hw.imu.inject_rotation('roll',  rate)   # (not mapped by default)
    """

    _AXIS_INDEX = {'yaw': 0, 'pitch': 1, 'roll': 2}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._virtual_gyro  = np.zeros(3)        # deg/s, settable via inject_rotation
        self._virtual_accel = np.array([0.0, 0.0, GRAVITY])  # static gravity
        self._gyro_lock     = threading.Lock()   # separate lock for inject (avoids nesting)

    def inject_rotation(self, axis: str, rate_deg_per_sec: float) -> None:
        """
        Set the angular velocity for one axis. Call with rate=0 on KEY_UP.

        Args:
            axis            : 'yaw', 'pitch', or 'roll'
            rate_deg_per_sec: signed rate in deg/s (e.g. +90 or -90)
        """
        idx = self._AXIS_INDEX.get(axis)
        if idx is None:
            raise ValueError(f"Unknown axis '{axis}'. Use 'yaw', 'pitch', or 'roll'.")
        with self._gyro_lock:
            self._virtual_gyro[idx] = rate_deg_per_sec

    def _read_raw(self) -> dict:
        with self._gyro_lock:
            gyro = self._virtual_gyro.copy()
        return {
            'accel': tuple(self._virtual_accel),
            'gyro':  tuple(gyro),
        }

    def get_yaw(self) -> float:
        """Return yaw wrapped to [0, 360)."""
        return super().get_yaw() % 360.0

    def get_pitch(self) -> float:
        """Return pitch clamped to the panorama-friendly range [-90, 90]."""
        pitch = super().get_pitch()
        return max(-90.0, min(90.0, pitch))
