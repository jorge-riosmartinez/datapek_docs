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
	echo -e "\n\n ${redColour} [!] Saliendo...${endColour}\n"
	tput cnorm && exit 1
}

# ctrl+c
trap ctrl_c INT

# Función para mostrar el menú y obtener la selección del usuario
mostrar_menu() {
    echo "Seleccione las opciones que desea activar:"
    echo "1. Unidad de Medición Inercial (IMU)"
    echo "2. Cámara"
    echo "3. Micrófono"
    echo "4. Temperatura"
    echo "5. Ejecutar"
    echo "6. Salir"
}

# Inicializar variables de opciones
imu=""
camara=""
audio=""
temperatura=""

# Obtener el nombre del perro, nombre de la prueba y duración de la prueba
read -p "Ingrese el nombre del perro: " nombre_perro
read -p "Ingrese el nombre de la prueba: " nombre_prueba
read -p "Ingrese la duración de la prueba en segundos: " duracion

# Loop para mostrar el menú y procesar la entrada del usuario
while true; do
    mostrar_menu
    read -p "Seleccione una opción (1-6): " opcion

    case $opcion in
        1)
            imu="--imu"
            echo "Unidad de Medición Inercial (IMU) activada."
            ;;
        2)
            camara="--camara"
            echo "Cámara activada."
            ;;
        3)
            audio="--audio"
            echo "Micrófono activado."
            ;;
        4)
            temperatura="--temperatura"
            echo "Temperatura activada."
            ;;
        5)
            # Ejecutar el comando de Python con las opciones seleccionadas
            comando="python firmware/adquisicion_datos.py -n $nombre_perro -p $nombre_prueba -d $duracion $imu $camara $audio $temperatura"
            echo "Ejecutando: $comando"
            eval $comando
            exit 0
            ;;
        6)
            echo "Saliendo..."
            exit 0
            ;;
        *)
            echo "Opción no válida. Intente de nuevo."
            ;;
    esac
done
