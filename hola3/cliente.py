import socket
import os
import time

# Dirección y puerto del servidor
server_address = ("0.0.0.0", 5005)

# Directorio donde se guardarán los archivos recibidos
received_directory = 'ArchivosRecibidos'

# Tamaño del buffer para recibir los datos
buffer_size = 65507


def receive_file(connection_num, file_size):
    # Crear socket UDP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Tiempo inicial de recepción
    start_time = time.time()

    # Enviar solicitud de archivo al servidor
    message = f"SEND {file_size}"
    client_socket.sendto(message.encode(), server_address)

    # Esperar respuesta del servidor
    response, server = client_socket.recvfrom(buffer_size)
    response = response.decode()

    # Si el servidor envía una respuesta de error, mostrar mensaje y cerrar socket
    if response.startswith('ERROR'):
        print(response)
        client_socket.close()
        return

    # Si el servidor envía el tamaño del archivo, crear el archivo en el directorio correspondiente
    file_path = os.path.join(received_directory, f"Cliente{connection_num}-Prueba-{file_size}.txt")
    with open(file_path, 'wb') as f:
        bytes_received = 0

        # Recibir los datos en fragmentos y escribirlos en el archivo
        while bytes_received < int(response):
            data, server = client_socket.recvfrom(buffer_size)
            f.write(data)
            bytes_received += len(data)

    # Tiempo final de recepción
    end_time = time.time()

    # Cerrar socket
    client_socket.close()

    # Mostrar mensaje de éxito y tiempo de recepción
    print(f"Archivo recibido correctamente en {end_time - start_time:.2f} segundos.")


if __name__ == '__main__':
    # Crear directorio para archivos recibidos, si no existe
    os.makedirs(received_directory, exist_ok=True)

    # Obtener el tamaño del archivo a enviar del usuario
    file_size = input("Seleccione el tamaño del archivo a enviar (100MB/250MB): ")
    while file_size not in ["100MB", "250MB"]:
        file_size = input("Tamaño no válido. Seleccione el tamaño del archivo a enviar (100MB/250MB): ")

    # Realizar las conexiones especificadas
    for i in range(25):
        print(f"Conexión {i+1}:")
        receive_file(i+1, file_size)
        print()
