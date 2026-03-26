import socket

IP = "192.168.56.101"

if __name__ == "__main__":
    buff_size = 1000
    end_of_message = "\n"
    new_socket_address = (IP, 8003)
    #
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(new_socket_address)
     
    server_socket.listen(3)

    while True:
        new_socket, new_socket_address = server_socket.accept()
        recv_message = new_socket.recv(buff_size)
        print(recv_message +b"holaaaaaa")

        headers = [
        "HTTP/1.1 200 OK",
        "Server: nginx/1.17.0",
        "Date: Wed, 25 Mar 2026 19:59:36 GMT",
        "Content-Type: text/html; charset=utf-8",
        "Content-Length: 237",
        "Connection: keep-alive",
        "Access-Control-Allow-Origin: *"
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
            <h3><a href="replace">¿Qué es un hjcjcsalfldsproxy?</a></h3>
        </body>
        </html>"""

        # Unimos todo con \r\n
        # Nota: Necesitamos DOS \r\n entre headers y body
        response_full = "\r\n".join(headers) + "\r\n\r\n" + body

        # Si necesitas enviarlo por un socket, debes convertirlo a bytes:
        response_bytes = response_full.encode()

        new_socket.send(response_bytes)

        new_socket.close()
















