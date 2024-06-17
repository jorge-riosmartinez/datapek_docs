import smbus
import time
import board
from mpu6050 import mpu6050
import os
import csv
import datetime

device_file = '/sys/bus/w1/devices/28-e8795c1f64ff/w1_slave'
# Inicializa I2C para GY-91 (MPU6050)
i2c = board.I2C()  
mpu = mpu6050(0x68)

# Inicializa el sensor DS18B20
def read_temp_raw():
    with open(device_file, 'r') as file:
        lines = file.readlines()
    return lines
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.01)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
# Archivo CSV donde se guardarán los datos
csv_file = "sensor_data.csv"

# Encabezados para el archivo CSV
headers = ['Timestamp', 'Temp_DS18B20', 'Accel_X', 'Accel_Y', 'Accel_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z']

# Escribir los encabezados en el archivo CSV
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers)

while True:
    try:
        # Leer datos de los sensores
        temperature = read_temp()
        
        
        
        
        acceleration = mpu.get_accel_data()
        # gyro = mpu.gyro


        # Obtener el timestamp actual
        timestamp = datetime.datetime.now()
        print([timestamp, temperature, acceleration])
        # Escribe los datos en el archivo CSV
        with open(csv_file, 'a', newline='') as file:
	        
            writer = csv.writer(file)
            writer.writerow([timestamp, temperature, acceleration])

        # Espera un tiempo corto antes de la próxima lectura
        time.sleep(0.01)  # Ajusta este valor según sea necesario

    except Exception as e:
        if e == "KeyboardInterrupt":
            print("Terminando la recopilación de datos.")
            break
        else:
            continue
