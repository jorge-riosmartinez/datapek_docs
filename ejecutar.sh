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
    echo -e "\n\n ${redColour}[!] Saliendo...${endColour}\n"
    tput cnorm && exit 1
}

# ctrl+c
trap ctrl_c INT

# Función para mostrar el menú y obtener la selección del usuario
mostrar_menu() {
    echo -e "${blueColour}Seleccione las opciones que desea activar:${endColour}"
    echo -e "${yellowColour}1. Unidad de Medición Inercial (IMU)${endColour}"
    echo -e "${yellowColour}2. Cámara${endColour}"
    echo -e "${yellowColour}3. Micrófono${endColour}"
    echo -e "${yellowColour}4. Temperatura${endColour}"
    echo -e "${yellowColour}5. Ejecutar${endColour}"
    echo -e "${yellowColour}6. Salir${endColour}"
}

# Inicializar variables de opciones
imu=""
camara=""
audio=""
temperatura=""

# Obtener el nombre del perro, nombre de la prueba y duración de la prueba
echo -ne "${grayColour}Ingrese el nombre del perro: ${endColour}" && read nombre_perro
echo -ne "${grayColour}Ingrese el nombre de la prueba: ${endColour}" && read nombre_prueba
echo -ne "${grayColour}Ingrese la duración de la prueba en segundos: ${endColour}" && read duracion

# Loop para mostrar el menú y procesar la entrada del usuario
while true; do
    mostrar_menu
    echo -ne "${grayColour}Seleccione una opción (1-6): ${endColour}" && read opcion

    case $opcion in
        1)
            imu="--imu"
            echo -e "${greenColour}Unidad de Medición Inercial (IMU) activada.${endColour}"
            ;;
        2)
            camara="--camara"
            echo -e "${greenColour}Cámara activada.${endColour}"
            ;;
        3)
            audio="--audio"
            echo -e "${greenColour}Micrófono activado.${endColour}"
            ;;
        4)
            temperatura="--temperatura"
            echo -e "${greenColour}Temperatura activada.${endColour}"
            ;;
        5)
            # Ejecutar el comando de Python con las opciones seleccionadas
            comando="python firmware/adquisicion_datos.py -n $nombre_perro -p $nombre_prueba -d $duracion $imu $camara $audio $temperatura"
            echo -e "${blueColour}Ejecutando: $comando${endColour}"
            eval $comando
            exit 0
            ;;
        6)
            echo -e "${redColour}Saliendo...${endColour}"
            exit 0
            ;;
        *)
            echo -e "${redColour}Opción no válida. Intente de nuevo.${endColour}"
            ;;
    esac
done
