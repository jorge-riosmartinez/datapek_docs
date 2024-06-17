from utils.led_control import ControladorLEDs

# Crear una instancia del controlador de LEDs
controlador = ControladorLEDs()

# Usar el método grabacion para encender el parpadeo que simula grabación
controlador.grabacion("encender")

# Aquí puedes poner más lógica de tu programa...

# Por ejemplo, mantener la grabación por 10 segundos antes de apagar
import time
time.sleep(10)

# Luego apagar el parpadeo que simula grabación
controlador.grabacion("apagar")