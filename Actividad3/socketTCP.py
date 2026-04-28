

import socket

class socketTCP:
    def __init__(self):
        self.socketUDP = self.socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.direccion_origen = None
        self.direccion_destino = None
        self.secuencia = 0
        self.bufsize = 16

    staticmethod
    def parse_segment(message):
        parse_message = {}

        #el primer byte son las flags
        parse_message["flags"] = message[0:8]
        #el segundo byte es la secuencia
        parse_message["secuencia"] = message[8:8*5]
        #el resto es el mensaje
        parse_message["mensaje"] = message[8*5:]

        return parse_message

    staticmethod
    def create_segment(dict_segment):
        seg = dict_segment["flags"] + dict_segment["secuencia"] + dict_segment["mensaje"]
        return seg
    
    def bind(self,address):
        self.socketUDP.bind(address)
    
    def connect(self, address ):
        self.direccion_destino = address
        handshake1 = self.create_segment({
            "flags": "00000001",
            "secuencia": "00000000000000000000000000000000",
            "mensaje": ""
        })
        self.socketUDP.sendto(handshake1, self.direccion_destino)

        handshake2 = self.socketUDP.recvfrom(self.bufsize)
        
        parsed_handshake2 = self.parse_segment(handshake2[0])


    def accept(self):
        pass


    
if __name__ == "__main__":
    mensaje = "1010101010101010"
    secuencia = "00000000000000000000000000000001" #secuencia de 32 bits
    print(secuencia)
    flags = "00000100"
    dict_segment = {
        "flags": flags,
        "secuencia": secuencia,
        "mensaje": mensaje
    }
    segment = socketTCP.create_segment(dict_segment)
    print(segment)

    dict_segment = socketTCP.parse_segment(segment)
    print(dict_segment)