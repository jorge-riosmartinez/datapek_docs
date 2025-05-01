import smbus
import time
import os

# MPU6050 Registers
MPU6050_ADDR = 0x68  # I2C address of the MPU6050
PWR_MGMT_1 = 0x6B
GYRO_CONFIG = 0x1B
GYRO_XOUT_H = 0x43

# Initialize I2C bus
bus = smbus.SMBus(1)  # Use I2C bus 1 on Raspberry Pi

# Wake up MPU6050
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0x00)

# Configure gyroscope range (±250 deg/s)
bus.write_byte_data(MPU6050_ADDR, GYRO_CONFIG, 0x00)

# Function to read raw gyroscope data
def read_raw_gyro_data(addr):
    """Read raw 16-bit gyroscope data from MPU6050."""
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = (high << 8) | low
    if value > 32768:  # Convert to signed value
        value = value - 65536
    return value

# Function to read gyroscope data in deg/s
def read_gyro_data():
    """Read gyroscope data in deg/s."""
    gyro_x = read_raw_gyro_data(GYRO_XOUT_H) / 131.0
    gyro_y = read_raw_gyro_data(GYRO_XOUT_H + 2) / 131.0
    gyro_z = read_raw_gyro_data(GYRO_XOUT_H + 4) / 131.0
    return gyro_x, gyro_y, gyro_z

# Main script
if __name__ == "__main__":
    # Create a folder to save the data
    folder_name = "mpu6050_gyro_data"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # File path to save the data
    file_path = os.path.join(folder_name, "gyro_data.txt")

    # Open the file for writing
    with open(file_path, "w") as file:
        # Write header
        file.write("timestamp,gyro_x,gyro_y,gyro_z\n")

        # Read data for 30 seconds
        print("Reading gyroscope data for 30 seconds...")
        start_time = time.time()
        while time.time() - start_time < 30:
            # Read gyroscope data
            gyro_x, gyro_y, gyro_z = read_gyro_data()

            # Get current timestamp
            timestamp = time.time() - start_time

            # Write data to file
            file.write(f"{timestamp:.3f},{gyro_x:.3f},{gyro_y:.3f},{gyro_z:.3f}\n")

            # Print data to console (optional)
            print(f"Timestamp: {timestamp:.3f}, Gyro: ({gyro_x:.3f}, {gyro_y:.3f}, {gyro_z:.3f})")

            # Wait for the next sample (adjust delay for desired sampling rate)
            time.sleep(0.01)  # ~100 Hz sampling rate

    print(f"\nGyroscope data saved to {file_path}")
