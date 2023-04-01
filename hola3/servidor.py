import socket
import os
import time
import datetime

# Definir la dirección y puerto en el que se espera recibir conexiones
UDP_IP = "192.168.20.35"
UDP_PORT = 5005

# Tamaño máximo de cada paquete UDP
MAX_PACKET_SIZE = 65507

# Archivos disponibles para envío
FILES = {"file1": "100MB.txt", "file2": "250MB.txt"}

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
            file_name = data.decode()

            # Verificar si el archivo existe
            if file_name not in FILES:
                sock.sendto("ERROR".encode(), addr)
                continue

            # Enviar mensaje de confirmación con el tamaño del archivo
            file_size = os.path.getsize(FILES[file_name])
            sock.sendto(str(file_size).encode(), addr)

            # Esperar mensaje de confirmación del cliente
            data, addr = sock.recvfrom(MAX_PACKET_SIZE)
            if data.decode() != "OK":
                continue

            # Abrir el archivo y enviarlo en paquetes
            with open(FILES[file_name], "rb") as f:
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

if __name__ == "_main_":
    main()