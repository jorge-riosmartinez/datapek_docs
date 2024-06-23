from gpiozero import LED
from time import sleep

class ControladorLEDs:
    def __init__(self):
        # Inicialización de LEDs
        self.alarma = LED(17)
        self.parpadear = LED(18)
        self.estatus = LED(27)

    def encender_alarma(self):
        print("Alarma ON")
        self.alarma.on()

    def apagar_alarma(self):
        print("Alarma OFF")
        self.alarma.off()

    def parpadeo_rapido(self):
        print("Parpadeo rápido")
        self.parpadear.blink(on_time=0.5, off_time=0.5, n=5, background=False)

    def indicar_listo(self):
        print("LED de estatus: Listo")
        self.estatus.on()
        sleep(1)
        self.estatus.off()

    def grabacion(self, estado):
        if estado.lower() == "encender":
            # print("Grabación ON")
            self.estatus.off()  # Apagar el LED de estatus
            self.parpadear.blink(on_time=0.5, off_time=0.5, background=True)
        elif estado.lower() == "apagar":
            # print("Grabación OFF")
            self.parpadear.off()
            self.estatus.on()  # Encender el LED de estatus