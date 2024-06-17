import picamera
import time

# Inicializa la cámara
with picamera.PiCamera() as camera:
    # Configura la resolución y la velocidad de fotogramas (FPS) según tus necesidades
    camera.resolution = (1280, 720)  # Cambia la resolución si es necesario
    camera.framerate = 30  # Cambia la velocidad de fotogramas si es necesario

    # Nombre del archivo de video de salida
    output_filename = 'mi_video.h264'

    # Comienza la grabación
    camera.start_recording(output_filename)

    try:
        # Graba durante 10 segundos (puedes ajustar el tiempo)
        camera.wait_recording(10)
    finally:
        # Detiene la grabación
        camera.stop_recording()

# El archivo de video se guardará en el directorio actual con el nombre 'mi_video.h264'
