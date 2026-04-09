import socket
import sys
import json

IP = "192.168.56.101"


#http error 403
html_403 = (
                        "<html>"
                        "<head><title>Bloqueado</title></head>"
                        "<body>"
                        "<h1>Error 403: Sitio Prohibido</h1>"
                        "<img src='403.jpg'>" 
                        "</body>"
                        "</html>"
                    )
 respuesta_403 = (
                        "HTTP/1.1 403 Forbidden\r\n"
                        "Content-Type: text/html\r\n"
                        f"Content-Length: {len(html_403)}\r\n"
                        "\r\n"
                        f"{html_403}"
                    )

http_image = ("""HTTP/1.1 200 OK\r\n
Content-Type: image/png\r\n
Content-Length: 15432\r\n
Connection: close\r\n
\r\n\r\n
"""


headers = [
"HTTP/1.1 200 OK",
"Server: nginx/1.17.0",
"Date: Wed, 25 Mar 2026 19:59:36 GMT",
"Content-Type: text/html; charset=utf-8",
"Content-Length: 237",
"Connection: keep-alive",
"Access-Control-Allow-Origin: *",
]

# Definimos el cuerpo (HTML)
body = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>CC4303</title>
</head>
<body>
    <h1>Bienvenide ... oh? no puedo ver tu nombre :c!</h1>
    <h3><a href="replace">¿Qué es un proxy?</a></h3>
</body>
</html>"""


def create_HTTP_message(headers, body):
    return ("\r\n".join(headers) + "\r\n\r\n" + body).encode("utf-8")


def create_HTTP_message(parsed_dict):
    head_dict = parsed_dict["head"]
    body = parsed_dict["body"]
    
    # Extraemos la primera línea (Request-Line)
    request_line = head_dict["Request-Line"]
    if isinstance(request_line, str):
        request_line = request_line.encode("utf-8")
        
    lines = [request_line]
    
    # Agregamos el resto de los headers iterando el diccionario "head"
    for key, value in head_dict.items():
        if key == "Request-Line":
            continue
        
        # Nos aseguramos de que todo se empaquete en bytes
        k = key.encode("utf-8") if isinstance(key, str) else key
        v = value.encode("utf-8") if isinstance(value, str) else value
        
        lines.append(k + b": " + v)
        
    # Unimos todos los headers
    head_bytes = b"\r\n".join(lines)
    
    # Verificamos que el body también sea bytes
    body_bytes = body.encode("utf-8") if isinstance(body, str) else body
    
    # Unimos head y body con los saltos correspondientes
    return head_bytes + b"\r\n\r\n" + body_bytes


http = create_HTTP_message(headers, body)




def parse_HTTP_message(http_message):

    headandbody = http_message.split(b"\r\n\r\n")
    head = headandbody[0]
    body = headandbody[1] if len(headandbody) > 1 else b""

    # parsear el head
    lines = head.split(b"\r\n")
    
    # Este será el diccionario interno para los headers
    head_dict = {}
    head_dict["Request-Line"] = lines[0]

    for line in lines[1:]:
        if b":" in line:
            header, content = line.split(b":", 1)
            # Usar strip() ayuda a limpiar espacios (como el que viene después de los ':')
            head_dict[header.decode().strip()] = content.strip()

    # Este es el diccionario principal que agrupa head y body
    resultado = {
        "head": head_dict,
        "body": body
    }

    print(resultado)
    return resultado

 
def contains_end_of_message(message, end_sequence):
    return message.endswith(end_sequence)
 

def receive_full_message(connection_socket, buff_size, end_sequence):
 
     # recibimos la primera parte del mensaje
     recv_message = connection_socket.recv(buff_size)
     full_message = recv_message
 
     # verificamos si llegó el mensaje completo o si aún faltan partes del mensaje
     is_end_of_message = contains_end_of_message(full_message.decode(), end_sequence)
     
 
     # entramos a un while para recibir el resto y seguimos esperando información
     # mientras el buffer no contenga secuencia de fin de mensaje
     while not is_end_of_message:
         # recibimos un nuevo trozo del mensaje
         recv_message = connection_socket.recv(buff_size)
 
         # lo añadimos al mensaje "completo"
         full_message += recv_message
 
         # verificamos si es la última parte del mensaje
         is_end_of_message = contains_end_of_message(full_message.decode(), end_sequence)
 
     # removemos la secuencia de fin de mensaje, esto entrega un mensaje en string
     full_message = remove_end_of_message(full_message.decode(), end_sequence)
 
     # finalmente retornamos el mensaje
     return full_message
     
if __name__ == "__main__":

    #abrimos el archivo config
    with open(config.json, 'r') as file:
        config = json.load(file)
    # guardamos info de config
    usuario = config["user"]
    blocked_pag = config["blocked"]
    forbidden_words = config["forbidden_words"]

    #ElQuePregunta = config['X-ElQuePregunta']
    parsedHTTP = parse_HTTP_message(http)
    buff_size = 1000
    end_of_message = "\n"
    new_socket_address = (IP, 8001)
    #
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(new_socket_address)
     
    server_socket.listen(3)

    while True:
        #recibimos el mensaje del cliente
        new_socket, new_socket_address = server_socket.accept()
        recv_message = receive_full_message(new_socket, buff_size, end_of_message)

        print("mensaje recibido por cliente: " + recv_message.decode())

        #parsear el mensaje y extraemos el destinatario
        parse_message = parse_HTTP_message(recv_message)
        Host = parse_message["head"]["Host"].decode().strip()
        print(recv_message)
        print (parse_message)
        #chequeamos si la dirección esta bloqueada
        for i in blocked_pag:
            #si la dirección está bloqueada, enviamos error 403 
            if i == Host:
                #mandamos el html de error 403
                new_socket.send(respuesta_403.encode())
                #nos debe mandar una peticion para la imagen del gato, esperamos esa petición
                response_wait_image = new_socket.recv(buff_size)
                #enviamos la imagen del gato
                with open("403.jpg", "rb") as img_file:
                    img_data = img_file.read()
                    http_image = ("""HTTP/1.1 200 OK\r\nContent-Type: image/png\r\nContent-Length: 15432\r\nConnection: close\r\n\r\n{img_data}""")
                    new_socket.send(http_image.encode())

    
            
            else:
                #agregamos el header de quien pregunta

                ##################################
                # preguntar si es el correo o el nombre parseado del correo

                parse_message["head"]["X-ElQuePregunta"] = usuario.encode()
                #reconstruimos el mensaje con el nuevo header
                new_http_message = create_HTTP_message(parse_message)

        
        #actuamos como cliente y enviamos un mensaje al servidor
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #address = (Host,80)# ??
        client_socket.connect((Host,80))
        client_socket.send(recv_message)


        # esperamos respuesta del servidor
        message = receive_full_message(client_socket, buffer_size, end_of_message)
        print(message)

        #chequeamos si la respuesta contiene alguna palabra prohibida
        for word in forbidden_words:
            if word.encode() in message:
                #si la respuesta contiene una palabra prohibida, la reemplazamos por su contraparte
                redacted_word = forbidden_words[word]
                message = message.replace(word.encode(), redacted_word.encode())


        #redireccionamos a cliente
        new_socket.send(message)

        #cerramos sockets de cliente y servidor
        client_socket.close()
        new_socket.close()


        #headers= headers + [4f"X-ElQuePregunta:{ElQuePregunta}"]
        # Unimos todo con \r\n
        # Nota: Necesitamos DOS \r\n entre headers y body
        #response_full = "\r\n".join(headers) + "\r\n\r\n" + body

        # Si necesitas enviarlo por un socket, debes convertirlo a bytes:
        #response_bytes = response_full.encode()

        #new_socket.send(response_bytes)















