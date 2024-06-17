from tqdm import tqdm
import RPi.GPIO as GPIO
import time

# Configuración de los pines GPIO
led_pins = [17, 18, 27]
GPIO.setmode(GPIO.BCM)  # Usa el número de pin del Broadcom SOC Channel
GPIO.setup(led_pins, GPIO.OUT, initial=GPIO.LOW)

def toggle_led(pin):
    """Enciende y luego apaga el LED especificado."""
    GPIO.output(pin, GPIO.HIGH)
    print(f"LED en pin {pin} encendido.")
    time.sleep(1)  # Espera 1 segundo
    GPIO.output(pin, GPIO.LOW)
    print(f"LED en pin {pin} apagado.")
    time.sleep(1)  # Espera 1 segundo

try:
    for i in range(2):
        for pin in led_pins:
            toggle_led(pin)

finally:
    print("Limpiando los pines GPIO y apagando todos los LEDs.")
    GPIO.cleanup()  # Restablece los pines GPIO a su estado inicial


print("Iniciando test acelerometro")

from mpu6050 import mpu6050
import time

sensor = mpu6050(0x68)

try:
    print("iniciando prueba acelerometro")
    time.sleep(2)
    start_time = time.time()
    while time.time() - start_time < 3:  # Leer durante 10 segundos
        accel_data = sensor.get_accel_data()
        print("Acelerómetro:", accel_data)
        time.sleep(0.0001)  # Intervalo de 1 segundo entre lecturas
    print("iniciando prueba giroscopio")
    time.sleep(2)
    start_time = time.time()
    while time.time() - start_time < 3:  # Leer durante 10 segundos
        gyro_data = sensor.get_gyro_data()
        print("Giroscopio:", gyro_data)
        time.sleep(0.0001)  # Intervalo de 1 segundo entre lecturas

except Exception as e:
    print("Ocurrió un error:", e)


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
# Ruta al dispositivo
device_file = find_temp_device()




print("Iniciando prueba sensor de temperatura")
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
        temp_c = float(temp_string) / 1000.0
        return temp_c
    

start_time = time.time()

# Bucle para mostrar la temperatura por 5 segundos
lecturas = 0
while lecturas < 5:
    try:
        print("Temperatura: {:.1f} °C".format(read_temp()))
        time.sleep(1)  # Espera 1 segundo antes de la próxima lectur
        lecturas += 1
    except Exception as e:
        print("problema con sensor de temperatura")
        print(e)
        break