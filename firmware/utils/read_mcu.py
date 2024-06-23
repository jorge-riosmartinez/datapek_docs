import smbus

# Constants for the MPU6050
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47
Device_Address = 0x68   # MPU6050 device address

class GY_91:
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.MPU_Init()

    def MPU_Init(self):
        """Initialize the MPU6050 with the standard settings."""
        # Write to registers to set up the sensor
        self.bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
        self.bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
        self.bus.write_byte_data(Device_Address, CONFIG, 0)
        self.bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
        self.bus.write_byte_data(Device_Address, INT_ENABLE, 1)

    def read_raw_data(self, addr):
        """Read the raw data from the sensor."""
        high = self.bus.read_byte_data(Device_Address, addr)
        low = self.bus.read_byte_data(Device_Address, addr+1)
        value = ((high << 8) | low)
        if value > 32768:
            value -= 65536
        return value