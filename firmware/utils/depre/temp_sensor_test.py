import os

# Ruta al dispositivo
device_file = '/sys/bus/w1/devices/28-e8795c1f64ff/w1_slave'

def read_temp_raw():
    with open(device_file, 'r') as file:
        lines = file.readlines()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

print("Temperatura: {:.1f} °C".format(read_temp()))