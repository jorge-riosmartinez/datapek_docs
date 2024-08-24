# Datapek-cc

**Datapek** es un proyecto desarrollado dentro del marco del proyecto Tzuku por la Facultad de Matemáticas de la Universidad Autónoma de Yucatán. Este repositorio contiene el firmware necesario para configurar y operar una Raspberry Pi como parte del sistema Datapek.

## Instalación del Firmware

Sigue estos pasos para instalar y configurar el firmware en tu Raspberry Pi:

### Preparación de la Tarjeta SD

1. **Grabar la imagen del sistema operativo**:
   - Descarga y abre el [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
   - Selecciona la imagen "Raspberry Pi OS (32-bit) Bullseye" y graba la imagen en una tarjeta SD.

2. **Configuración inicial**:
   - Al finalizar la grabación, configura un usuario y contraseña para tu Raspberry Pi.
   - Establece también los detalles de conexión Wi-Fi mediante el Imager.

3. **Conexión SSH**:
   - Inserta la tarjeta SD en tu Raspberry Pi y enciéndela.
   - Busca la dirección IP de la Raspberry Pi en tu red y conéctate a ella mediante SSH.

### Instalación de Dependencias

Una vez conectado a la Raspberry Pi via SSH, ejecuta los siguientes comandos para instalar las dependencias necesarias:

```bash
sudo apt update
sudo apt install python3-pip
sudo apt-get install -y i2c-tools 
sudo apt-get install libportaudio2 libportaudio0 portaudio19-dev libopengl-dev liblapack-dev libopenblas-dev

sudo apt install git -y

pip install smbus tqdm mpu6050-raspberrypi sounddevice pyaudio scipy picamera numpy
```
### Configuración del dispositivo

Abrir el menu de Configuración 

```bash
sudo raspi-config
```
Navegar a interface options y habilitar las siguientes opciones:

- Legagy camera
- i2c
- 1wire

ejecuta 

```
sudo reboot
```
### Obtener scripts


Reconectate a la raspberry y clona el repositorio.

```
git clone https://github.com/DrCarlimp/Datapek-cc/tree/development
```


###Configuración wifi

El siguiente paso consiste en implementar un hotspot movil desde el telefono que se usara para controlar el dispositivo. 

Como ejemplo se puede usar una red wifi con los siguientes elementos:

SSID: wifi_datapek
Pass: 2023Datapek

el siguiente paso es configurar la rapsberry para conectarse a la red anterior. 
Para hacerlo es necesario ejecutar el comando:

```
sudo raspi-config
```

```
system options/wireless area network (podria aparecer como: WLAN)
```

Utilizar una terminal en el telefono movil como:

- terminus (en android)


### Diagnostico

Ejecutar el diagnostico que permite conocer el funcionamiento de los sensores:

- Temperatura 
- IMU
- Leds

python firmware/utils/diagnostico.py


### Uso

Para iniciar la recoleccion de datos es necesario usar el script adquisicion_datos.py. Dicho script toma los siguientes argumentos:


-n,--nombre_perro: Nombre del perro 
-p, --prueba: nombre de la prueba, por ejemplo juguete
-d, --duracion: duracion de la prueba en segundos 
--imu: activa la recolección de datos del IMU
--camara: activa la grabacion de video de la camara
--audio: activa la grabacion de audio del microfono
--temperatura: activa la recolección de datos del sensor ds18b20

las salidas del script son:

Carpeta con el nombre del perro
 - carpeta con el nombre de la prueba
	- archivos de los sensores seleccionados. 
	
	
ejemplo:

Habilitar zona wifi en telefono movil con las credenciales:
```
SSID: wifi_datapek
Password: 2023Datapek
```

Una vez que el dispositivo este conectado a la red, buscar el IP de datapek. 

Posteriormente abrir una aplicacion de "terminal". Por ejemplo Terminus. usar la ip para conectarse mediante ssh al dispositivo. 

```
ssh uady@IP de Datapek
por ejemplo
ssh uady@192.168.68.100

password: datapek2023
```

Para la ejecucion del script de adquisicion de datos se puede correr esta instrucción:

```
python firmware/adquisicion_datos.py -n doug -p test -d 20 --imu --camara --audio --temperatura
```	

los argumentos relacionados con los sensores son opcionales, pueden elegirse unicamente los de interes para la prueba.

Finalmente, los datos obtenido se pueden encontrar en:

```	
/home/uady/doug/test
```	
