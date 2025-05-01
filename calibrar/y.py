"""
RECORD ACCELEROMETER MEASUREMENTS FROM MPU6050 FOR CALIBRATION
VIA MAGNETO

Adapted for Raspberry Pi Zero with MPU6050 on I2C bus (address 0x68)
"""

import os
import math
import time
import pandas
import smbus2  # I2C communication library for Raspberry Pi

# MPU6050 constants
MPU6050_ADDR = 0x68  # I2C address of MPU6050
ACCEL_XOUT_H = 0x3B  # Starting register for accelerometer data
PWR_MGMT_1 = 0x6B    # Power management register
ACCEL_CONFIG = 0x1C  # Accelerometer configuration register
ACCEL_SCALE = 16384.0  # LSB/g for ±2g range (default)

# Global variables
MAX_MEAS = 200  # Maximum number of readings in the session
AVG_MEAS = 25   # Number of measurements to average for each reading
FILENAME = os.path.join(os.getcwd(), 'mpu6050_acceldata.txt')  # Output file


class MPU6050:
    """Interface with MPU6050 accelerometer/gyroscope via I2C."""

    def __init__(self, address=MPU6050_ADDR, bus_num=1):
        """Initialize MPU6050 on specified I2C bus and address.

        Args:
            address (int): I2C address of MPU6050, default 0x68
            bus_num (int): I2C bus number, default 1 (use 0 for older Raspberry Pi models)
        """
        self.address = address
        self.bus = smbus2.SMBus(bus_num)
        
        # Wake up the MPU6050 (it starts in sleep mode)
        self.bus.write_byte_data(self.address, PWR_MGMT_1, 0)
        
        # Configure accelerometer for ±2g range
        self.bus.write_byte_data(self.address, ACCEL_CONFIG, 0)
        
        # Wait for device to stabilize
        time.sleep(0.1)

    def read_raw_data(self, reg):
        """Read raw 16-bit data from specified register.
        
        Args:
            reg (int): Register address to read from
            
        Returns:
            int: 16-bit signed integer value
        """
        # Read high and low bytes
        high = self.bus.read_byte_data(self.address, reg)
        low = self.bus.read_byte_data(self.address, reg + 1)
        
        # Combine high and low bytes
        value = (high << 8) | low
        
        # Convert to signed value
        if value > 32767:
            value -= 65536
            
        return value

    def read_accel(self):
        """Read accelerometer data and convert to g units.
        
        Returns:
            tuple: (x, y, z) acceleration in g units
        """
        # Read raw acceleration data
        x = self.read_raw_data(ACCEL_XOUT_H)
        y = self.read_raw_data(ACCEL_XOUT_H + 2)
        z = self.read_raw_data(ACCEL_XOUT_H + 4)
        
        # Convert to g units
        ax = x / ACCEL_SCALE
        ay = y / ACCEL_SCALE
        az = z / ACCEL_SCALE
        
        return (ax, ay, az)


def record_data_pt(sensor):
    """Record data from MPU6050 and return averaged result."""
    ax = ay = az = 0.0

    for _ in range(AVG_MEAS):
        # Read data
        try:
            ax_now, ay_now, az_now = sensor.read_accel()
        except Exception as e:
            print(f"[ERROR]: Error reading sensor: {e}")
            raise SystemExit("[ERROR]: Exiting due to sensor read error.")
            
        ax += ax_now
        ay += ay_now
        az += az_now
        
        # Small delay between readings
        time.sleep(0.01)

    return (ax / AVG_MEAS, ay / AVG_MEAS, az / AVG_MEAS)


def list_to_delim_file(mylist, filename, delimiter=',', f_mode='a'):
    """Convert list to Pandas dataframe, then save as a text file."""
    df = pandas.DataFrame(mylist)
    df.to_csv(
        filename,  # path and filename
        sep=delimiter,
        mode=f_mode,
        header=False,  # no col. labels
        index=False  # no row numbers
    )


def main():
    try:
        # Initialize MPU6050 sensor
        sensor = MPU6050(address=MPU6050_ADDR)
        data = []  # data list

        print('[INFO]: MPU6050 initialized successfully.')
        print('[INFO]: Place sensor level and stationary.')
        input('[INPUT]: Press Enter to continue...')

        # Take measurements
        for _ in range(MAX_MEAS):
            user = input(
                '[INPUT]: Ready for measurement? Type \'m\' to measure or \'q\' to save and quit: ').lower()
            if user == 'm':
                # Record data to list
                ax, ay, az = record_data_pt(sensor)
                magn = math.sqrt(ax**2 + ay**2 + az**2)
                print('[INFO]: Avgd Readings: {:.4f}, {:.4f}, {:.4f} Magnitude: {:.4f}'.format(
                    ax, ay, az, magn))
                data.append([ax, ay, az])
            elif user == 'q':
                # Save, then quit
                print('[INFO]: Saving data and exiting...')
                list_to_delim_file(data, FILENAME, delimiter='\t')
                print('[INFO]: Done!')
                return
            else:
                print('[ERROR]: \'{}\' is an unknown input. Terminating!'.format(user))
                if data:
                    list_to_delim_file(data, FILENAME, delimiter='\t')
                return

        # Save once max is reached
        print('[WARNING]: Reached max. number of datapoints, saving file...')
        list_to_delim_file(data, FILENAME, delimiter='\t')
        print('[INFO]: Done!')
        
    except Exception as e:
        print(f"[ERROR]: {e}")
        if 'data' in locals() and data:
            print('[INFO]: Saving collected data before exit...')
            list_to_delim_file(data, FILENAME, delimiter='\t')


if __name__ == '__main__':
    main()
