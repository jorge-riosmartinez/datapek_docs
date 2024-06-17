from gpiozero import LED
from time import sleep

led = LED(17)  # Reemplaza 17 con el número del pin GPIO que estés usando

while True:
    print("led on")
    led.on()
    sleep(1)
    led.off()
    print("led off")
    sleep(1)