"""
Real IMU driver — reads sensor data over I2C on the BeagleBone.

TODO: implement _read_raw() for your specific IMU chip.
      Common chips: MPU-6050 (0x68), BNO055 (0x28), LSM6DS3 (0x6A).

      The smbus2 library works well on BeagleBone:
          pip install smbus2
          bus = smbus2.SMBus(1)

      _read_raw() must return:
          {
              'accel': (ax, ay, az),  # m/s², gravity-included
              'gyro':  (gx, gy, gz),  # deg/s
          }
      Scale raw register values to these units before returning.
"""

from .imu_base import IMUBase


class RealIMU(IMUBase):
    """
    Hardware IMU driver. Reads raw sensor registers in _read_raw() over I2C.
    All integration math is inherited from IMUBase.
    """

    def __init__(self, i2c_bus: int = 1, i2c_address: int = 0x68, **kwargs):
        """
        Args:
            i2c_bus     : I2C bus number (1 on BeagleBone Black)
            i2c_address : I2C address of the IMU chip
            **kwargs    : forwarded to IMUBase (sample_rate_hz, ema_alpha)
        """
        super().__init__(**kwargs)
        self._bus_num = i2c_bus
        self._addr    = i2c_address
        # TODO: open bus and configure sensor registers here
        # Example (MPU-6050):
        #   import smbus2
        #   self._bus = smbus2.SMBus(i2c_bus)
        #   self._bus.write_byte_data(i2c_address, 0x6B, 0)  # wake up

    def _read_raw(self) -> dict:
        """
        Read accelerometer and gyroscope registers.
        TODO: replace placeholder with real register reads.
        """
        # Placeholder — returns stationary gravity vector, no rotation
        return {
            'accel': (0.0, 0.0, 9.81),
            'gyro':  (0.0, 0.0, 0.0),
        }
