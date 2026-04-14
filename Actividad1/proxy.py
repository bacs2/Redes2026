import socket
import sys
import json

IP = "172.20.10.13" #"192.168.56.101"


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

http_image = """HTTP/1.1 200 OK\r\n
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
 

def receive_full_message(connection_socket, buff_size):

    full_message = b""
    end_headers = b"\r\n\r\n"
    
    # Recibir datos iterativamente hasta encontrar el fin de los headers (\r\n\r\n)
    while end_headers not in full_message:
        recv_message = connection_socket.recv(buff_size)
        #si se cierra la conexión salimos
        if not recv_message:
            break 
        full_message += recv_message

    # Si por algún motivo nos desconectamos antes de que llegue el header, salimos
    if end_headers not in full_message:
        return full_message

    #Separar los headers del resto del body (podría haber llegado parte del body junto a los headers)
    head_bytes, body_bytes = full_message.split(end_headers, 1)

    # 3. Buscar el encabezado Content-Length para saber el tamaño real del body
    content_length = 0
    for line in head_bytes.split(b"\r\n"):
        if line.lower().startswith(b"content-length:"):
            try:
                content_length = int(line.split(b":", 1)[1].strip())
            except ValueError:
                pass
            break

    # 4. Si hay un body, seguir recibiendo del socket hasta alcanzar el tamaño exacto
    while len(body_bytes) < content_length:
        recv_message = connection_socket.recv(buff_size)
        if not recv_message:
            break # El socket se cortó antes de tiempo
        body_bytes += recv_message
        full_message += recv_message

    return full_message


# Esta función extrae la URL desde la request line
def extract_url_from_request_line(request_line):
    parts = request_line.split()
    if len(parts) >= 2:
        return parts[1]  # La URL es la segunda parte
    return None
     
if __name__ == "__main__":

    #abrimos el archivo config
    with open("config.json", 'r') as file:
        config = json.load(file)
    # guardamos info de config
    usuario = config["user"]
    blocked_pag = config["blocked"]
    forbidden_words = config["forbidden_words"]


    buff_size = 50
    new_socket_address = (IP, 8000)
    print("Proxy iniciado en IP: " + IP + " y puerto: 8000")
    print("Tamaño del buffer: " + str(buff_size))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(new_socket_address)
     
    server_socket.listen(3)

    while True:
        #recibimos el mensaje del cliente
        c2p_socket, new_socket_address = server_socket.accept()
        recv_message = receive_full_message(c2p_socket, buff_size)

        print("mensaje recibido por cliente: " + recv_message.decode())

        #parsear el mensaje y extraemos el destinatario y la url a la que se quiere conectar
        parsed_message = parse_HTTP_message(recv_message)

        # ==========================================
        # escudo anti CONNECT (HTTPS)
        # ==========================================
        request_line_str = parsed_message["head"]["Request-Line"].decode()
        if request_line_str.startswith("CONNECT"):
            print("Ignorando basura de fondo (HTTPS CONNECT)...")
            c2p_socket.close() # Le cerramos el socket
            continue           # Volvemos al inicio del while para esperar otra cosa
        # ==========================================


        url = extract_url_from_request_line(parsed_message["head"]["Request-Line"].decode())
        host = parsed_message["head"]["Host"].decode() 
        host = host.split(":")[0].strip() #borrar en caso de que no funcione


        #chequeamos si la dirección esta bloqueada
        is_blocked = False
        for block_url in blocked_pag:
            #si la dirección está bloqueada, enviamos error 403 
            if block_url == url:
                #mandamos el html de error 403
                c2p_socket.send(respuesta_403.encode())
                #nos debe mandar una peticion para la imagen del gato, esperamos esa petición
                try:
                    response_wait_image = receive_full_message(c2p_socket, buff_size)
                except:
                    pass
                #enviamos la imagen del gato
                try:
                    with open("403.jpg", "rb") as img_file:
                        img_data = img_file.read()
                        peso = len(img_data)
                        headers_image = (
                            "HTTP/1.1 200 OK\r\n"
                            "Content-Type: image/jpeg\r\n"
                            f"Content-Length: {peso}\r\n"
                            "Connection: close\r\n"
                            "\r\n"
                        ).encode()
                        http_image = headers_image + img_data
                        c2p_socket.send(http_image)
                except Exception as e:
                    print("Error enviando imagen: ", e)
                
                print("se ha bloqueado el acceso a la página: " + url)
                c2p_socket.close()
                is_blocked = True
                break

        if is_blocked:
            continue


    
            
            
        #agregamos el header de quien pregunta

        ##################################
        # preguntar si es el correo o el nombre parseado del correo
        parsed_message["head"]["X-ElQuePregunta"] = usuario.encode()

        #reconstruimos el mensaje con el nuevo header
        new_http_message = create_HTTP_message(parsed_message)
        print("dictionario del mensaje a enviar al servidor: " + str(parsed_message))
        print("mensaje a enviar al servidor: " + new_http_message.decode())
        print("URL al que se va a conectar: " + url)

        #actuamos como cliente y enviamos un mensaje al servidor
        p2s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = (host,80)
        p2s_socket.connect(address)
        p2s_socket.send(new_http_message)

        print ("Host al que se va a conectar: " + host)

        # esperamos respuesta del servidor
        response_server_message = receive_full_message(p2s_socket, buff_size)
        print("Respuesta del servidor: " + response_server_message.decode())

        #chequeamos si la respuesta contiene alguna palabra prohibida
        for dict in forbidden_words:
            for word , replace in dict.items():
                if word.encode() in response_server_message:
                    #si la respuesta contiene una palabra prohibida, la reemplazamos por su contraparte
                    response_server_message = response_server_message.replace(word.encode(), replace.encode())

        print("Respuesta del servidor después de reemplazar palabras prohibidas: " + response_server_message.decode())
        
        #redireccionamos a cliente
        c2p_socket.send(response_server_message)

        #cerramos sockets de cliente y servidor
        p2s_socket.close()
        c2p_socket.close()















