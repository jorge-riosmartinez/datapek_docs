import time
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250
import board
import adafruit_bmp280

# Configura el MPU-9250
mpu9250 = MPU9250(address_ak=AK8963_ADDRESS, address_mpu_master=MPU9050_ADDRESS_68, address_mpu_slave=None, bus=1, gfs=GFS_1000, afs=AFS_8G, mfs=AK8963_BIT_16, mode=AK8963_MODE_C100HZ)
mpu9250.configure()

# Configura el BMP280
i2c = board.I2C()  # Utiliza el bus I2C por defecto
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

# Abrir archivo de registro
with open("sensor_log.txt", "w") as file:
    start_time = time.time()
    while time.time() - start_time < 10:  # Leer durante 10 segundos
        # Leer datos del MPU-9250
        accel_data = mpu9250.readAccelerometerMaster()
        gyro_data = mpu9250.readGyroscopeMaster()
        mag_data = mpu9250.readMagnetometerMaster()
        
        # Leer datos del BMP280
        temp = bmp280.temperature
        pressure = bmp280.pressure

        # Escribir datos en el archivo
        file.write(f"Accel: {accel_data}, Gyro: {gyro_data}, Mag: {mag_data}, Temp: {temp}, Pressure: {pressure}\n")
        
        # Pequeña pausa
        time.sleep(0.1)

print("Datos guardados en sensor_log.txt")
import time
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250
import board
import adafruit_bmp280

# Configura el MPU-9250
mpu9250 = MPU9250(address_ak=AK8963_ADDRESS, address_mpu_master=MPU9050_ADDRESS_68, address_mpu_slave=None, bus=1, gfs=GFS_1000, afs=AFS_8G, mfs=AK8963_BIT_16, mode=AK8963_MODE_C100HZ)
mpu9250.configure()

# Configura el BMP280
i2c = board.I2C()  # Utiliza el bus I2C por defecto
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

# Abrir archivo de registro
with open("sensor_log.txt", "w") as file:
    start_time = time.time()
    while time.time() - start_time < 10:  # Leer durante 10 segundos
        # Leer datos del MPU-9250
        accel_data = mpu9250.readAccelerometerMaster()
        gyro_data = mpu9250.readGyroscopeMaster()
        mag_data = mpu9250.readMagnetometerMaster()
        
        # Leer datos del BMP280
        temp = bmp280.temperature
        pressure = bmp280.pressure

        # Escribir datos en el archivo
        file.write(f"Accel: {accel_data}, Gyro: {gyro_data}, Mag: {mag_data}, Temp: {temp}, Pressure: {pressure}\n")
        
        # Pequeña pausa
        time.sleep(0.1)

print("Datos guardados en sensor_log.txt")
