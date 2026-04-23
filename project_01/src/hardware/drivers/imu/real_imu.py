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

import struct
import smbus2

from .imu_base import IMUBase

# MPU-6050 registers
_PWR_MGMT_1   = 0x6B
_ACCEL_XOUT_H = 0x3B
_GYRO_XOUT_H  = 0x43
_ACCEL_CONFIG  = 0x1C
_GYRO_CONFIG   = 0x1B

# Scale factors for default ±2g / ±250°/s ranges
_ACCEL_SCALE  = 9.81 / 16384.0  # LSB → m/s²
_GYRO_SCALE   = 1.0  / 131.0    # LSB → deg/s


class RealIMU(IMUBase):
    """
    Hardware IMU driver for MPU-6050 over I2C.
    All integration math is inherited from IMUBase.
    """

    def __init__(self, i2c_bus: int = 1, i2c_address: int = 0x68, **kwargs):
        super().__init__(**kwargs)
        self._addr = i2c_address
        self._bus  = smbus2.SMBus(i2c_bus)
        # Wake the MPU-6050 (clears sleep bit)
        self._bus.write_byte_data(self._addr, _PWR_MGMT_1, 0x00)

    def _read_raw(self) -> dict:
        # Read 6 accel bytes then 6 gyro bytes in two bursts
        raw_a = self._bus.read_i2c_block_data(self._addr, _ACCEL_XOUT_H, 6)
        raw_g = self._bus.read_i2c_block_data(self._addr, _GYRO_XOUT_H,  6)

        ax, ay, az = struct.unpack('>hhh', bytes(raw_a))
        gx, gy, gz = struct.unpack('>hhh', bytes(raw_g))

        return {
            'accel': (ax * _ACCEL_SCALE, ay * _ACCEL_SCALE, az * _ACCEL_SCALE),
            'gyro':  (gx * _GYRO_SCALE,  gy * _GYRO_SCALE,  gz * _GYRO_SCALE),
        }
