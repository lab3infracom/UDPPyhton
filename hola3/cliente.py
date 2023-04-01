# cliente de un servidor UPD en python

import os
import socket
import sys
import threading
import datetime
from time import time
import queue as q

# Dirección y puerto del servidor
server_address = ('192.168.20.60', 3400)


def recive_data(sock, i, queue, numConnections):

    # Guardar en la carpeta ArchivosRecibidos
    file = open("UDP/ArchivosRecibidos/Cliente" + str(i) + "-Prueba-" + numConnections + ".txt", "w")

    # Tamaño máximo de datagrama
    MAX_PACKET_SIZE = 65507

    # Recibir respuesta
    print(sys.stderr, 'Cliente ' + str(i) + ' - ' + 'Esperando respuesta')

    start_time = time()
    data = b'data'
    while data:
        data, server = sock.recvfrom(MAX_PACKET_SIZE)
        if data == b'FIN':
            print(sys.stderr, 'Cliente ' + str(i) + ' - ' + 'Recibido "%s"' % data)
            break

        file.write(data.decode())

    print(sys.stderr, 'Cliente ' + str(i) + ' - ' + 'Cerrando socket ' + str(i))

    end_time = time()
    total_time = end_time - start_time

    sock.close()

    # Colocar el tiempo total en la cola
    queue.put(total_time)


if __name__ == "__main__":

    idThread = 0

    # Pedir al usuario el tamaño del mensaje y el número de clientes
    init_message = input('Introduce el tamaño del mensaje: ').encode()
    sec_message = input('Introduce el número de clientes: ')

    # Obtener la fecha y hora actual para el nombre del archivo de logs
    actual_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    # Crear el archivo de logs
    log = open('UDP/Logs/' + actual_date + '-log.txt', 'w')

    for i in range(0, int(sec_message)):

        # Crear un socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Crear una cola para almacenar los tiempos de transferencia
        queue = q.Queue()

        # Enviar mensaje al servidor
        sock.sendto(init_message, server_address)

        # Iniciar los threads para la transferencia de datos
        thread = threading.Thread(target=recive_data, args=(sock, i, queue, sec_message))
        thread.start()

        # Esperar a que el hilo termine
        thread.join()

        # Obtener el tiempo de transferencia de la cola
        total_time = queue.get()

        print(sys.stderr, total_time)

        # Escribir la información de transferencia en el archivo de logs
        log.write(f'[{i}], Archivo: {init_message.decode()}MB.txt, Tamaño: {os.path.getsize("UDP/ArchivosRecibidos/Cliente" + str(i) + "-Prueba-" + sec_message + ".txt")} bytes, Tiempo de transferencia: {total_time} segundos\n')

        # Incrementar el ID del hilo
        idThread += 1
