import socket
bufsize = 16
address = ("localhost", 8000)

import SocketTCP as SocketTCP

if __name__ == "__main__":
    server_socketTCP = SocketTCP.SocketTCP()
    server_socketTCP.bind(address)
    connection_socketTCP, new_address = server_socketTCP.accept()
    print(f"Conexion establecida con {new_address}, secuencia inicial: {connection_socketTCP.secuencia}")