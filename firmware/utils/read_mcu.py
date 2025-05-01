import smbus
import time

# MPU6050 Register Addresses.
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
INT_ENABLE = 0x38

# Accelerometer data registers
ACCEL_XOUT_H = 0x3B
ACCEL_XOUT_L = 0x3C
ACCEL_YOUT_H = 0x3D
ACCEL_YOUT_L = 0x3E
ACCEL_ZOUT_H = 0x3F
ACCEL_ZOUT_L = 0x40

# Gyroscope data registers
GYRO_XOUT_H = 0x43
GYRO_XOUT_L = 0x44
GYRO_YOUT_H = 0x45
GYRO_YOUT_L = 0x46
GYRO_ZOUT_H = 0x47
GYRO_ZOUT_L = 0x48

# MPU6050 I2C Address
Device_Address = 0x68

class GY_91:
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.MPU_Init()
        
    def MPU_Init(self):
        """Initialize the MPU6050 with the standard settings."""
        # Wake up the MPU6050 (it starts in sleep mode)
        self.bus.write_byte_data(Device_Address, PWR_MGMT_1, 0x00)
        time.sleep(0.1)  # Wait for sensor to stabilize
        
        # Configure the sample rate
        self.bus.write_byte_data(Device_Address, SMPLRT_DIV, 0x07)
        
        # Configure the digital low pass filter
        self.bus.write_byte_data(Device_Address, CONFIG, 0x00)
        
        # Configure gyroscope range (±250°/s)
        self.bus.write_byte_data(Device_Address, GYRO_CONFIG, 0x00)
        
        # Configure accelerometer range (±2g)
        self.bus.write_byte_data(Device_Address, ACCEL_CONFIG, 0x00)
        
        # Enable data ready interrupt
        self.bus.write_byte_data(Device_Address, INT_ENABLE, 0x01)
    
    def read_raw_data(self, addr):
        """Read the raw data from the sensor by combining high and low bytes."""
        high = self.bus.read_byte_data(Device_Address, addr)
        low = self.bus.read_byte_data(Device_Address, addr + 1)
        
        # Combine high and low bytes
        value = ((high << 8) | low)
        
        # Convert to signed value
        if value > 32767:
            value -= 65536
            
        return value
    
    def get_accel_data(self):
        """Get raw accelerometer data without scaling."""
        # Read raw accelerometer data
        x = self.read_raw_data(ACCEL_XOUT_H)
        y = self.read_raw_data(ACCEL_YOUT_H)
        z = self.read_raw_data(ACCEL_ZOUT_H)
        
        return {"x": x, "y": y, "z": z}
    
    def get_gyro_data(self):
        """Get raw gyroscope data without scaling."""
        # Read raw gyroscope data
        x = self.read_raw_data(GYRO_XOUT_H)
        y = self.read_raw_data(GYRO_YOUT_H)
        z = self.read_raw_data(GYRO_ZOUT_H)
        
        return {"x": x, "y": y, "z": z}



"""
#######################################################
################### Example usage #####################
#######################################################
if __name__ == "__main__":
    mpu = GY_91()
    time.sleep(2)  # Wait for sensor to stabilize
    
    try:
        while True:
            
            accel_data = mpu.get_accel_data()
            gyro_data = mpu.get_gyro_data()
            
            
            print("Raw Accelerometer: X={}, Y={}, Z={}".format(
                accel_data["x"], accel_data["y"], accel_data["z"]))
            print("Raw Gyroscope: X={}, Y={}, Z={}".format(
                gyro_data["x"], gyro_data["y"], gyro_data["z"]))
            
            time.sleep(0.5)  
    
    except KeyboardInterrupt:
        print("Measurement stopped by user")
"""
