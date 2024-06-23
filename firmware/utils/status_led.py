import RPi.GPIO as GPIO

# Opción para desactivar advertencias, descomenta la siguiente línea si deseas hacerlo
# GPIO.setwarnings(False)

# Limpiar todos los pines al inicio (opcional)
GPIO.cleanup()

# Configura el modo del GPIO
GPIO.setmode(GPIO.BCM)

# Configura el pin al que está conectado el LED
LED_PIN = 18
# Limpiar específicamente el pin del LED (opcional)
# GPIO.cleanup(LED_PIN)
GPIO.setup(LED_PIN, GPIO.OUT)

# Enciende el LED
GPIO.output(LED_PIN, GPIO.HIGH)