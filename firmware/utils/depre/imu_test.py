from mpu6050 import mpu6050
import time

sensor = mpu6050(0x68)

try:
    # Leer acelerómetro
    accel_data = sensor.get_accel_data()
    print("Acelerómetro:", accel_data)

except Exception as e:
    print("Ocurrió un error:", e)
