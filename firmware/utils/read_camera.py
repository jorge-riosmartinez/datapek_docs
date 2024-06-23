import picamera
import time

# Duración del video en segundos
duracion_del_video = 10

# Crear una instancia de la cámara
with picamera.PiCamera() as camera:
    camera.resolution = (1920, 1080)  # Configura la resolución del video
    camera.start_preview()  # Muestra una vista previa en la pantalla conectada a la Raspberry Pi
    time.sleep(2)  # Tiempo para que la cámara se estabilice
    
    # Comenzar a grabar
    camera.start_recording('video.h264')
    print("Inicio de grabación.")
    camera.wait_recording(duracion_del_video)
    camera.stop_recording()
    print("Grabación finalizada.")
    
    camera.stop_preview()