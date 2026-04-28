import socket
#flags: SYN = 0b00000100, ACK = 0b00000010, FIN = 0b00000001
SYN = 0b00000100
ACK = 0b00000010
FIN = 0b00000001


class socketTCP:
    def __init__(self):
        self.socketUDP = self.socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.direccion_origen = None
        self.direccion_destino = None
        self.secuencia = 0
        self.bufsize = 16


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
            "secuencia": 0,
            "mensaje": 0
        })
        self.socketUDP.sendto(handshake1.to_bytes(21, byteorder='big'), self.direccion_destino)

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
        pass


    
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
    segment = socketTCP.create_segment(dict_segment)
    print(segment)

    dict_segment = socketTCP.parse_segment(segment)
    print(dict_segment)