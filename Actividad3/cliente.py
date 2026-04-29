import socket
import sys
import SocketTCP as SocketTCP
bufsize = 16
address = ("localhost", 8000)


if __name__ == "__main__":
    client_socketTCP = SocketTCP.SocketTCP()
    client_socketTCP.connect(address)