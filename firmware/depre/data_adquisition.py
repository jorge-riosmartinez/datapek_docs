import threading
import time
from picamera import PiCamera
from read_mcu import GY_91

def record_video(duration, folder_name):
    """Record video for a given duration."""
    with PiCamera() as camera:
        camera.resolution = (640, 480)  # Set resolution
        camera.start_recording(f'{folder_name}/video.h264')  # Start recording
        camera.wait_recording(duration)
        camera.stop_recording()

def collect_sensor_data(duration, folder_name, sensor):
    """Collect sensor data from GY-91 for a given duration."""
    start_time = time.time()
    with open(f'{folder_name}/sensor_data.txt', 'w') as file:
        while time.time() - start_time < duration:
            accel_x = sensor.read_raw_data(ACCEL_XOUT_H)
            accel_y = sensor.read_raw_data(ACCEL_YOUT_H)
            accel_z = sensor.read_raw_data(ACCEL_ZOUT_H)
            gyro_x = sensor.read_raw_data(GYRO_XOUT_H)
            gyro_y = sensor.read_raw_data(GYRO_YOUT_H)
            gyro_z = sensor.read_raw_data(GYRO_ZOUT_H)
            file.write(f'{time.time()}, {accel_x}, {accel_y}, {accel_z}, {gyro_x}, {gyro_y}, {gyro_z}\n')
            time.sleep(0.1)  # Collect data every 0.1 seconds

def main(folder_name, duration):
    """Main function to handle video recording and sensor data collection."""
    import os
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    sensor = GY_91()  # Create sensor object
    
    # Threads to handle recording and data collection simultaneously
    video_thread = threading.Thread(target=record_video, args=(duration, folder_name))
    sensor_thread = threading.Thread(target=collect_sensor_data, args=(duration, folder_name, sensor))

    # Start threads
    video_thread.start()
    sensor_thread.start()

    # Wait for threads to complete
    video_thread.join()
    sensor_thread.join()

if __name__ == "__main__":
    folder_name = 'data'
    duration = 10  # Duration in seconds
    print("hola mundo")
    time.sleep(5)
    main(folder_name, duration)