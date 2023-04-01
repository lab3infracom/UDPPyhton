import socket
import os
import time
import datetime

# Definir la dirección y puerto en el que se espera recibir conexiones
UDP_IP = "0.0.0.0"
UDP_PORT = 5005

# Tamaño máximo de cada paquete UDP
MAX_PACKET_SIZE = 65507

# Archivos disponibles para envío
FILES = {"file1": {"name": "100MB.txt", "size": 100 * 1024 * 1024},
         "file2": {"name": "250MB.txt", "size": 250 * 1024 * 1024}}

# Crear un directorio de logs si no existe
LOG_DIR = "Logs"
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)


def main():
    # Crear socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    # Esperar conexiones
    print(f"Servidor iniciado. Esperando conexiones en {UDP_IP}:{UDP_PORT}")
    while True:
        data, addr = sock.recvfrom(MAX_PACKET_SIZE)

        # Verificar si se recibió un comando para enviar un archivo
        if data.decode() == "SEND":
            # Enviar mensaje de confirmación
            sock.sendto("READY".encode(), addr)

            # Recibir el nombre del archivo a enviar
            data, addr = sock.recvfrom(MAX_PACKET_SIZE)

            # Preguntar al usuario por el tamaño del archivo
            file_size = 0
            while file_size not in FILES.values():
                file_size = input("Ingrese el tamaño del archivo que desea enviar (100 o 250 MB): ")
                try:
                    file_size = int(file_size)
                except ValueError:
                    file_size = 0

            # Obtener el nombre del archivo según su tamaño
            for file_data in FILES.values():
                if file_data["size"] == file_size:
                    file_name = file_data["name"]
                    break

            # Enviar mensaje de confirmación con el tamaño del archivo
            sock.sendto(str(file_size).encode(), addr)

            # Esperar mensaje de confirmación del cliente
            data, addr = sock.recvfrom(MAX_PACKET_SIZE)
            if data.decode() != "OK":
                continue

            # Abrir el archivo y enviarlo en paquetes
            with open(os.path.join("data", file_name), "rb") as f:
                start_time = time.time()
                while True:
                    data = f.read(MAX_PACKET_SIZE)
                    if not data:
                        break
                    sock.sendto(data, addr)

            # Calcular tiempo de transferencia
            end_time = time.time()
            transfer_time = end_time - start_time

            # Escribir registro en el archivo de log
            log_file_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-log.txt")
            log_file_path = os.path.join(LOG_DIR, log_file_name)
            with open(log_file_path, "a") as f:
                f.write(f"Archivo enviado: {file_name}\n")
                f.write(f"Tamaño del archivo: {file_size} bytes\n")
                f.write(f"Tiempo de transferencia: {transfer_time} segundos\n")
                f.write(f"Conexión recibida de: {addr}\n\n")


if __name__ == "__main__":
    main()
