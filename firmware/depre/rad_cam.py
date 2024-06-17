import picamera
import time

# Inicializa la c�mara
with picamera.PiCamera() as camera:
    # Configura la resoluci�n y la velocidad de fotogramas (FPS) seg�n tus necesidades
    camera.resolution = (1280, 720)  # Cambia la resoluci�n si es necesario
    camera.framerate = 30  # Cambia la velocidad de fotogramas si es necesario

    # Nombre del archivo de video de salida
    output_filename = 'mi_video.h264'

    # Comienza la grabaci�n
    camera.start_recording(output_filename)

    try:
        # Graba durante 10 segundos (puedes ajustar el tiempo)
        camera.wait_recording(10)
    finally:
        # Detiene la grabaci�n
        camera.stop_recording()

# El archivo de video se guardar� en el directorio actual con el nombre 'mi_video.h264'
