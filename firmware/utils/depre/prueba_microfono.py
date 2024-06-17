import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

def grabar_audio(duracion=10, frecuencia_muestreo=44100, nombre_archivo='grabacion.wav', canales=1):
    print("Grabando...")
    grabacion = sd.rec(int(duracion * frecuencia_muestreo), samplerate=frecuencia_muestreo, channels=canales, dtype='float64')
    sd.wait()  # Espera hasta que la grabación esté completa
    print("Grabación completada. Guardando...")
    wav.write(nombre_archivo, frecuencia_muestreo, grabacion)

# Configura los parámetros
duracion = 10  # Duración de la grabación en segundos
frecuencia_muestreo = 44100  # Frecuencia de muestreo en Hz
nombre_archivo = 'mi_grabacion.wav'  # Nombre del archivo de salida
canales = 1  # Número de canales de audio

grabar_audio(duracion, frecuencia_muestreo, nombre_archivo, canales)