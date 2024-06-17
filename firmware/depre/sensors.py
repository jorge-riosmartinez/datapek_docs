import smbus
from picamera import PiCamera
import sounddevice as sd
import sys
import scipy.io.wavfile as wav
import os
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


def record_video(duration, folder_name):
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        video_path = f'{folder_name}/video.h264'
        camera.start_recording(video_path)
        camera.wait_recording(duration)
        camera.stop_recording()


def record_audio(duration, folder_name, sample_rate=44100, channels=1):
    audio_path = f'{folder_name}/audio.wav'
    print("Recording audio...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='float64')
    sd.wait()  # Wait until the recording is complete
    print("Audio recording completed. Saving...")
    wav.write(audio_path, sample_rate, recording)

def collect_temperature_data(duration, folder_name):
    temp_path = os.path.join(folder_name, 'temperature_data.txt')
    start_time = time.time()
    with open(temp_path, 'w') as file:
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > duration:
                break
            temp_c = read_temp()
            file.write(f"{elapsed_time:.2f}, {temp_c}\n")
            time.sleep(1)  # Read temperature every second

def read_temp_raw():
    with open(device_file, 'r') as file:
        lines = file.readlines()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        return float(temp_string) / 1000.0
            