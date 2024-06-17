import picamera
import smbus
import threading
import time
import csv

# Inicializa la c�mara
def initialize_camera():
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

# Funci�n para leer datos del MPU6050
def read_mpu_data():
    # Define las constantes y funciones relacionadas con el MPU6050 aqu�
    # (c�digo que se encuentra en tu segundo archivo)

    # Abre un archivo CSV para escribir los datos
    with open('datos_acelerometro.csv', 'w', newline='') as csvfile:
        fieldnames = ['Ax', 'Ay', 'Az', 'Gx', 'Gy', 'Gz']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Escribe la cabecera del archivo CSV
        writer.writeheader()

        while True:
            # Leer datos del aceler�metro y giroscopio
            # (c�digo relacionado con la lectura de datos del MPU6050)

            # Realiza alguna acci�n con los datos, como imprimirlos
            print(f"{Ax},{Ay},{Az},{Gx},{Gy},{Gz}")

            # Escribe los datos en el archivo CSV
            writer.writerow({'Ax': Ax, 'Ay': Ay, 'Az': Az, 'Gx': Gx, 'Gy': Gy, 'Gz': Gz})

            # Pausa para controlar la velocidad de lectura
            time.sleep(0.002)

if __name__ == "__main__":
    # Inicializa el bus I2C
    bus = smbus.SMBus(1)  # o bus = smbus.SMBus(0) para placas m�s antiguas
    Device_Address = 0x68  # Direcci�n del dispositivo MPU6050

    # Inicializa el MPU6050
    MPU_Init()

    # Inicia dos hilos separados para la grabaci�n de video y la lectura de datos del MPU6050
    camera_thread = threading.Thread(target=initialize_camera)
    mpu_thread = threading.Thread(target=read_mpu_data)

    # Inicia ambos hilos
    camera_thread.start()
    mpu_thread.start()

    # Espera a que ambos hilos finalicen
    camera_thread.join()
    mpu_thread.join()
