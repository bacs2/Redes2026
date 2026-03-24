import socket

 
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


 
def contains_end_of_message(message, end_sequence):
    return message.endswith(end_sequence)
 
 
def remove_end_of_message(full_message, end_sequence):
    index = full_message.rfind(end_sequence)
    return full_message[:index]
 


def parse_HTTP_message(http_message):

    headandbody = http_message.split(b"\r\n\r\n")
    head = headandbody[0]
    body = headandbody[1] if len(headandbody) > 1 else b""

    #parsear el head
    lines = head.split(b"\r\n")
    request_line = lines[0]

    dict = {}
    dict["Request-Line"] = request_line

    for line in lines[1:]:
        header, content = line.split(b":",1)
        dict[header] = content

    dict["Body"] = body

    print(dict)


dict = {'Request-Line': b'HTTP/1.1 200 OK', b'Content-Type': b' text/html', b'Content-Length': b' 1024', b'Date': b' Thu, 19 Mar 2026 13:17:00 GMT', b'Server': b' Apache/2.4.1 (Unix)', 'Body': b'<!DOCTYPE html>\r\n<html>\r\n<head>\r\n<title>Example Page</title>\r\n</head>\r\n<body>\r\n<h1>Hello, World!</h1>\r\n</body>\r\n</html>\r\n'}
mensaje_original = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 1024\r\nDate: Thu, 19 Mar 2026 13:17:00 GMT\r\nServer: Apache/2.4.1 (Unix)\r\n\r\n<!DOCTYPE html>\r\n<html>\r\n<head>\r\n<title>Example Page</title>\r\n</head>\r\n<body>\r\n<h1>Hello, World!</h1>\r\n</body>\r\n</html>\r\n"
def create_HTTP_message(dict):
    http_message = b""
    http_message += dict["Request-Line"]
    for header, content in dict.items():
        if header != "Request-Line" and header != "Body":
            http_message += b"\r\n" + header + b":" + content
    http_message += b"\r\n\r\n" + dict["Body"]
    print(http_message)
    return http_message


if __name__ == "__main__":

    parse_HTTP_message(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 1024\r\nDate: Thu, 19 Mar 2026 13:17:00 GMT\r\nServer: Apache/2.4.1 (Unix)\r\n\r\n<!DOCTYPE html>\r\n<html>\r\n<head>\r\n<title>Example Page</title>\r\n</head>\r\n<body>\r\n<h1>Hello, World!</h1>\r\n</body>\r\n</html>\r\n")
    create_HTTP_message(dict)




