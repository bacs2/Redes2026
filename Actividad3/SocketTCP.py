import socket
import numpy as np
#flags: SYN = 0b00000100, ACK = 0b00000010, FIN = 0b00000001
SYN = 0b00000100
ACK = 0b00000010
FIN = 0b00000001


class SocketTCP:
    def __init__(self):
        self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.direccion_origen = None
        self.direccion_destino = None
        self.secuencia = np.random.randint(0, 100)
        self.bufsize = 21


    #retorna un diccionario con los campos del segmento: flags, secuencia y mensaje
    @staticmethod
    def parse_segment(message):
        parse_message = {}

        # Primer byte (8 bits) para las flags, desfasado 20 bytes (16 datos + 4 secuencia)
        parse_message["flags"] = (message >> (8*20)) & 0xFF
        # Siguientes 4 bytes (32 bits) para la secuencia, desfasado 16 bytes (datos)
        parse_message["secuencia"] = (message >> (8*16)) & 0xFFFFFFFF
        # Últimos 16 bytes (128 bits) para los datos, usando una máscara de 16 bytes
        parse_message["mensaje"] = message & ((1 << (8*16)) - 1)

        return parse_message

    #método para crear un segmento a partir de un diccionario con los campos: flags, secuencia y mensaje
    @staticmethod
    def create_segment(dict_segment):
        flags = dict_segment["flags"]
        secuencia = dict_segment["secuencia"]
        datos = dict_segment["mensaje"]
        
        # Ensamblamos el segmento desplazando los bits a sus posiciones correspondientes
        # Mismo desfase: 20 bytes para flags, 16 para secuencia, 0 para los datos
        seg = (flags << (8*20)) | (secuencia << (8*16)) | datos
        return seg
    
    #metodo para esperar por una conexion
    def bind(self,address):
        self.socketUDP.bind(address)
    

    #metodo para establecer una conexion con un servidor
    def connect(self, address ):
        self.direccion_destino = address

        #primer handshake, desde el cliente mandamos un mensaje de SYN
        handshake1 = self.create_segment({
            "flags": SYN,
            "secuencia": self.secuencia,
            "mensaje": 0
        })
        self.socketUDP.sendto(handshake1.to_bytes(21, byteorder='big'), address)

        #segundo handshake, el servidor responde con un mensaje de SYN-ACK
        handshake2, _ = self.socketUDP.recvfrom(self.bufsize)
        parsed_handshake2 = self.parse_segment(int.from_bytes(handshake2, byteorder='big'))

        #tercer handshake, el cliente responde con un mensaje de ACK
        handshake3 = self.create_segment({
            "flags": ACK,
            "secuencia": parsed_handshake2["secuencia"],
            "mensaje": 0
        })
        self.socketUDP.sendto(handshake3.to_bytes(21, byteorder='big'), self.direccion_destino)





    def accept(self):
        #esperamos el primer handshake del cliente, un mensaje de SYN
        handshake1, direccion_cliente = self.socketUDP.recvfrom(self.bufsize)
        parsed_handshake1 = self.parse_segment(int.from_bytes(handshake1, byteorder='big'))

        new_socketTCP = None

        #chequear si el mensaje tiene un SYN
        if parsed_handshake1["flags"] == SYN:

            handshake2 = self.create_segment({
                "flags": SYN | ACK,
                "secuencia": parsed_handshake1["secuencia"],
                "mensaje": 0
            })
            self.socketUDP.sendto(handshake2.to_bytes(21, byteorder='big'), direccion_cliente)
            new_socketTCP = SocketTCP()
            new_socketTCP.direccion_destino = direccion_cliente
        else: 
            print("Mensaje recibido no es un SYN, no se establece conexión")
            return None, None   


        return new_socketTCP, direccion_cliente

    
if __name__ == "__main__":
    mensaje = 0b1010101010101010  # 16 bits para un número "1010..."
    secuencia = 1 # secuencia numérica
    print(secuencia)
    flags = SYN 
    dict_segment = {
        "flags": flags,
        "secuencia": secuencia,
        "mensaje": mensaje
    }
    segment = SocketTCP.create_segment(dict_segment)
    print(segment)

    dict_segment = SocketTCP.parse_segment(segment)
    print(dict_segment)