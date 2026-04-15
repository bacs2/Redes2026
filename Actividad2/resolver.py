import socket
from dnslib import DNSRecord

IP = "172.20.10.23" #"192.168.0.10"
BUFF_SIZE = 1024

# =====================guia============================

def send_dns_message(address, port):
     # Acá ya no tenemos que crear el encabezado porque dnslib lo hace por nosotros, por default pregunta por el tipo A
     qname = "example.com"
     q = DNSRecord.question(qname)
     server_address = (address, port)
     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     try:
         # lo enviamos, hacemos cast a bytes de lo que resulte de la función pack() sobre el mensaje
         sock.sendto(bytes(q.pack()), server_address)
         # En data quedará la respuesta a nuestra consulta
         data, _ = sock.recvfrom(4096)
         # le pedimos a dnslib que haga el trabajo de parsing por nosotros 
         d = DNSRecord.parse(data)
     finally:
         sock.close()
     # Ojo que los datos de la respuesta van en en una estructura de datos
     return d

# Es dnslib la que sabe como se debe imprimir la estructura, usa el mismo formato que dig, los datos NO vienen en un string gigante, sino en una estructura de datos
print (send_dns_message("8.8.8.8", 53))

# =======================================================

def obtener_mensaje_dns():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_adress = (IP, 8000)

    server.bind(server_adress)
    print(f"socket escuchando en {IP}:{8000}")

    while True:
        mensaje, client_address = server.recvfrom(BUFF_SIZE)
        print(f"mensaje recibido de {client_address}")
        print(mensaje)

    server.close()

if __name__ == "__main__":
    obtener_mensaje_dns()
