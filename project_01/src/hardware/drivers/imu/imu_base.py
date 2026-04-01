"""
IMU abstract base class with integrated orientation and position tracking.

Subclasses implement _read_raw() to supply sensor data. All integration
math lives here so SimulatedIMU and RealIMU share identical physics.

Integration approach:
    - Gyro → Euler-angle integration (yaw/pitch/roll). Simple and sufficient
      for a device whose primary motion is rotation about one axis.
    - Accel → remove gravity, double-integrate → position. Drift will
      accumulate over time; zero() resets the reference frame.
    - EMA smoothing applied to raw readings before integration.

Thread safety: all reads/writes of integrated state are protected by _lock.
"""

import time
import threading
import numpy as np
from abc import ABC, abstractmethod

GRAVITY = 9.81  # m/s²


class IMUBase(ABC):
    """
    Abstract IMU driver with threaded EMA integration.

    Public API (all thread-safe):
        start() / stop()
        zero()                        — set current orientation/position as reference
        is_still(threshold_deg_s)     — True if angular velocity EMA < threshold
        get_orientation() → (yaw, pitch, roll) in degrees, relative to zero
        get_position()    → (x, y, z) in metres, relative to zero
        get_yaw() / get_pitch() / get_roll()

    Subclass hook:
        _read_raw() → {'accel': (ax, ay, az), 'gyro': (gx, gy, gz)}
    """

    def __init__(self, sample_rate_hz: float = 100.0, ema_alpha: float = 0.15):
        """
        Args:
            sample_rate_hz : how fast the integration thread loops
            ema_alpha      : EMA weight for new samples (0=no update, 1=no smoothing)
        """
        self._rate  = sample_rate_hz
        self._alpha = ema_alpha
        self._dt    = 1.0 / sample_rate_hz

        self._lock = threading.Lock()

        # EMA-smoothed sensor values
        self._accel_ema = np.array([0.0, 0.0, GRAVITY])
        self._gyro_ema  = np.array([0.0, 0.0, 0.0])

        # Absolute integrated state (world frame, no calibration offset)
        self._orientation_abs = np.array([0.0, 0.0, 0.0])  # yaw, pitch, roll (deg)
        self._velocity_abs    = np.array([0.0, 0.0, 0.0])  # m/s
        self._position_abs    = np.array([0.0, 0.0, 0.0])  # m

        # Calibration reference frame (set by zero())
        self._zero_orientation = np.array([0.0, 0.0, 0.0])
        self._zero_position    = np.array([0.0, 0.0, 0.0])
        self._zero_velocity    = np.array([0.0, 0.0, 0.0])

        self._running = False
        self._thread  = None

    # ------------------------------------------------------------------
    # Thread lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the integration daemon thread."""
        self._running = True
        self._thread = threading.Thread(
            target=self._integration_loop, daemon=True, name='imu-integration'
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the integration thread to stop and wait for it."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)

    # ------------------------------------------------------------------
    # Calibration
    # ------------------------------------------------------------------

    def zero(self) -> None:
        """
        Store the current integrated state as the calibration reference.
        Subsequent get_orientation() and get_position() calls return values
        relative to this snapshot.
        """
        with self._lock:
            self._zero_orientation = self._orientation_abs.copy()
            self._zero_position    = self._position_abs.copy()
            self._zero_velocity    = self._velocity_abs.copy()

    def is_still(self, threshold_deg_s: float = 2.0) -> bool:
        """
        Return True if the EMA-smoothed angular velocity magnitude is below
        threshold_deg_s. When no buttons are held in simulation, this is
        always True, letting CalibrationState proceed immediately.
        """
        with self._lock:
            gyro_mag = float(np.linalg.norm(self._gyro_ema))
        return gyro_mag < threshold_deg_s

    # ------------------------------------------------------------------
    # Read API
    # ------------------------------------------------------------------

    def get_orientation(self) -> tuple:
        """Return (yaw_deg, pitch_deg, roll_deg) relative to calibration zero."""
        with self._lock:
            diff = self._orientation_abs - self._zero_orientation
        return tuple(diff)

    def get_position(self) -> tuple:
        """Return (x_m, y_m, z_m) relative to calibration zero."""
        with self._lock:
            diff = self._position_abs - self._zero_position
        return tuple(diff)

    def get_yaw(self) -> float:
        return self.get_orientation()[0] % 360.0

    def get_pitch(self) -> float:
        return self.get_orientation()[1]

    def get_roll(self) -> float:
        return self.get_orientation()[2]

    # ------------------------------------------------------------------
    # Subclass hook
    # ------------------------------------------------------------------

    @abstractmethod
    def _read_raw(self) -> dict:
        """
        Return current sensor readings. Called at sample_rate_hz from the
        integration thread. Must be non-blocking.

        Returns:
            {
                'accel': (ax, ay, az),  # m/s² — gravity-included body-frame
                'gyro':  (gx, gy, gz),  # deg/s — angular velocity body-frame
            }
        """

    # ------------------------------------------------------------------
    # Integration loop (daemon thread)
    # ------------------------------------------------------------------

    def _integration_loop(self) -> None:
        while self._running:
            t0  = time.time()
            raw = self._read_raw()

            a_raw = np.array(raw['accel'], dtype=float)
            g_raw = np.array(raw['gyro'],  dtype=float)

            with self._lock:
                # EMA smoothing
                self._accel_ema = self._alpha * a_raw + (1 - self._alpha) * self._accel_ema
                self._gyro_ema  = self._alpha * g_raw + (1 - self._alpha) * self._gyro_ema

                # Orientation: direct Euler integration of gyro (yaw, pitch, roll)
                self._orientation_abs += self._gyro_ema * self._dt

                # Position: subtract gravity (assumed along world Z), integrate twice.
                # Simplified: treat EMA accel - (0,0,g) as linear acceleration.
                linear_accel = self._accel_ema - np.array([0.0, 0.0, GRAVITY])
                self._velocity_abs   += linear_accel * self._dt
                self._position_abs   += self._velocity_abs * self._dt

            # Sleep for the remainder of the tick
            elapsed = time.time() - t0
            sleep   = self._dt - elapsed
            if sleep > 0:
                time.sleep(sleep)
