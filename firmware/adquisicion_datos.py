import threading
import time
from picamera import PiCamera
from utils.read_mcu import GY_91, ACCEL_XOUT_H, ACCEL_YOUT_H, ACCEL_ZOUT_H, GYRO_XOUT_H, GYRO_YOUT_H, GYRO_ZOUT_H
from utils.led_control import ControladorLEDs
# print("test")
import sounddevice as sd
import sys
import scipy.io.wavfile as wav
import os
import argparse


def record_video(duration, folder_name):
    with PiCamera() as camera:
        camera.resolution = (320, 240)
        video_path = f'{folder_name}/video.h264'
        camera.start_recording(video_path)
        camera.wait_recording(duration)
        camera.stop_recording()

def collect_sensor_data(duration, folder_name, sensor):
    file_path = f'{folder_name}/IMU_data.txt'
    with open(file_path, 'w') as file:
        start_time = time.time()
        while time.time() - start_time < duration:
            elapsed_time = time.time() - start_time
            accel_x = sensor.read_raw_data(ACCEL_XOUT_H)
            accel_y = sensor.read_raw_data(ACCEL_YOUT_H)
            accel_z = sensor.read_raw_data(ACCEL_ZOUT_H)
            gyro_x = sensor.read_raw_data(GYRO_XOUT_H)
            gyro_y = sensor.read_raw_data(GYRO_YOUT_H)
            gyro_z = sensor.read_raw_data(GYRO_ZOUT_H)
            file.write(f"{elapsed_time:.2f}, {accel_x}, {accel_y}, {accel_z}, {gyro_x}, {gyro_y}, {gyro_z}\n")
            time.sleep(0.01)

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
    import os
def find_temp_device(base_path='/sys/bus/w1/devices/'):
    """
    Encuentra el primer dispositivo 1-Wire en el directorio especificado y devuelve la ruta al archivo w1_slave.
    """
    # Lista todos los elementos en el directorio base
    try:
        directories = os.listdir(base_path)
    except FileNotFoundError:
        print("El directorio especificado no existe.")
        return None

    # Filtra para obtener solo los directorios que parecen dispositivos (comienzan con '28-', típico para sensores DS18B20)
    for directory in directories:
        if directory.startswith('28-'):
            device_path = os.path.join(base_path, directory, 'w1_slave')
            if os.path.exists(device_path):
                return device_path

    print("No se encontraron dispositivos.")
    return None

# Ruta al dispositivo de temperatura
device_file = find_temp_device()
led = ControladorLEDs()

def main():
    parser = argparse.ArgumentParser(description='Script para adquisicion de datos con video')
    parser.add_argument('-n','--nombre_perro',type=str,help='Nombre del perro')
    parser.add_argument('-p','--prueba',type=str,help='nombre de la prueba, por ejemplo, juguete.')
    parser.add_argument('-d','--duracion',type=int,default=120, help='Duracion de la prueba en segundos')
    parser.add_argument('--imu', action='store_true', help='Activar la recolección de datos del IMU')
    parser.add_argument('--camara', action='store_true', help='Activar la grabación de video')
    parser.add_argument('--audio', action='store_true', help='Activar la grabación de audio')
    parser.add_argument('--temperatura', action='store_true', help='Activar la recolección de datos de temperatura')


    args = parser.parse_args()


    folder_name = f"{args.nombre_perro}/{args.prueba}"
    duration = args.duracion
    sensor = GY_91()
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    print("Start")
    threads = []

    if args.camara:
        video_thread = threading.Thread(target=record_video, args=(duration, folder_name))
        threads.append(video_thread)

    if args.imu:
        sensor_thread = threading.Thread(target=collect_sensor_data, args=(duration, folder_name, sensor))
        threads.append(sensor_thread)

    if args.audio:
        audio_thread = threading.Thread(target=record_audio, args=(duration, folder_name))
        threads.append(audio_thread)

    if args.temperatura:
        temperature_thread = threading.Thread(target=collect_temperature_data, args=(duration, folder_name))
        threads.append(temperature_thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    # temperature_thread.join()

if __name__ == "__main__":
    led.grabacion("encender")
    main()
    led.grabacion("apagar")