#!/bin/bash

# Colors
greenColour="\e[0;32m\033[1m"
endColour="\033[0m\e[0m"
redColour="\e[0;31m\033[1m"
blueColour="\e[0;34m\033[1m"
yellowColour="\e[0;33m\033[1m"
purpleColour="\e[0;35m\033[1m"
turquoiseColour="\e[0;36m\033[1m"
grayColour="\e[0;37m\033[1m"

function ctrl_c() {
    echo -e "\n\n${redColour}[!] Saliendo...${endColour}\n"
    tput cnorm && exit 1
}

# ctrl+c
trap ctrl_c INT

# Actualizar lista de paquetes
echo -e "${blueColour}Actualizando lista de paquetes...${endColour}"
sudo apt update

# Instalar python3-pip
echo -e "${blueColour}Instalando python3-pip...${endColour}"
sudo apt install -y python3-pip

# Instalar i2c-tools
echo -e "${blueColour}Instalando i2c-tools...${endColour}"
sudo apt-get install -y i2c-tools 

# Instalar librerías de portaudio y otras dependencias
echo -e "${blueColour}Instalando librerías de portaudio y otras dependencias...${endColour}"
sudo apt-get install -y libportaudio2 libportaudio0 portaudio19-dev libopengl-dev liblapack-dev libopenblas-dev

# Instalar git
echo -e "${blueColour}Instalando git...${endColour}"
sudo apt install -y git

# Instalar paquetes Python con pip
echo -e "${blueColour}Instalando paquetes Python con pip...${endColour}"
pip install smbus tqdm mpu6050-raspberrypi sounddevice pyaudio scipy picamera numpy

# Dando permisos de ejecución al programa
echo -e "${blueColour}Dando permisos de ejecución a ejecutar.sh${endColour}"
chmod +x ejecutar.sh

echo -e "${greenColour}Instalación y configuración completada con éxito.${endColour}"
