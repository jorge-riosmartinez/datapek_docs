#!/bin/bash

# Actualizar lista de paquetes
echo "Actualizando lista de paquetes..."
sudo apt update

# Instalar python3-pip
echo "Instalando python3-pip..."
sudo apt install -y python3-pip

# Instalar i2c-tools
echo "Instalando i2c-tools..."
sudo apt-get install -y i2c-tools 

# Instalar librerías de portaudio y otras dependencias
echo "Instalando librerías de portaudio y otras dependencias..."
sudo apt-get install -y libportaudio2 libportaudio0 portaudio19-dev libopengl-dev liblapack-dev libopenblas-dev

# Instalar git
echo "Instalando git..."
sudo apt install -y git

# Instalar paquetes Python con pip
echo "Instalando paquetes Python con pip..."
pip install smbus tqdm mpu6050-raspberrypi sounddevice pyaudio scipy picamera numpy

echo "Instalación completada con éxito."
