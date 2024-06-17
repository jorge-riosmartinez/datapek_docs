import time
from datetime import datetime

# Nombre del archivo donde se guardarán los registros
log_file = "battery_life_log.txt"

# Captura la hora de inicio una sola vez
start_time = time.time()
start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Función para añadir un registro al archivo
def log_runtime(minutes_passed):
    with open(log_file, "a") as file:
        # Usamos start_datetime, que no cambia, para "Funcionando desde"
        log_entry = f"Funcionando desde: {start_datetime}, Tiempo transcurrido: {minutes_passed} minutos\n"
        print(log_entry)
        file.write(log_entry)

def main():
    minutes_passed = 0
    
    while True:
        # Espera un tiempo específico, por ejemplo, 10 segundos = 0.1 minutos
        time.sleep(60)  # Ajusta aquí el intervalo de tiempo real
        minutes_passed += 1  # Ajusta este valor basado en el intervalo de espera
        log_runtime(round(minutes_passed, 1))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Registro finalizado por el usuario.")
    except Exception as e:
        print(f"Error: {e}")