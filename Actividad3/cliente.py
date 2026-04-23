import socket
import sys

bufsize = 16
address = ("localhost", 12345)

nombre_archivo = input("mensaje: ")
with open(nombre_archivo, "r") as file:
    message = file.read()

lista = []
for i in range(1, len(message)//16 + 1):
    lista.append(message[(i-1)*16:i*16])



# Socket no orientado a conexión
cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 
 # Recibir mensajes. Este método nos entrega el mensaje junto a la dirección de origen del mensaje
for i in lista:
    cliente.sendto(i, address)
 
 # Enviar mensajes. Este método debe especificar la dirección a la que se va a enviar el mensaje
 #message, address = cliente.recvfrom(bufsize)