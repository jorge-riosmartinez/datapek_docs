import board
import adafruit_bmp280

# Crear una instancia de I2C
i2c = board.I2C()

# Crear una instancia del sensor BMP280
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

try:
    # Leer la temperatura y la presión
    temp = bmp280.temperature
    pressure = bmp280.pressure

    print("Temperatura:", temp, "°C")
    print("Presión:", pressure, "hPa")

except Exception as e:
    print("Ocurrió un error:", e)