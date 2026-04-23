import socket
bufsize = 16
address = ("localhost", 12345)

# Socket no orientado a conexión
servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

 # servidor escuchando
servidor.bind(address)
 
str = ""
 # recibe el mensaje del cliente
while True:
    message, address = servidor.recvfrom(bufsize)
    str += message.decode()
    print(str)





 # Recibir mensajes. Este método nos entrega el mensaje junto a la dirección de origen del mensaje

 
 # Enviar mensajes. Este método debe especificar la dirección a la que se va a enviar el mensaje
servidor.sendto(message, address)