import socket

IP = "10.0.2.15"

if __name__ == "__main__":
    buff_size = 1000
    end_of_message = "\n"
    new_socket_address = (IP, 8000)
    #
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(new_socket_address)
     
    server_socket.listen(3)

    while True:
        new_socket, new_socket_address = server_socket.accept()
        recv_message = connection_socket.recv(buff_size)
        new_socket.close()
        print(recv_message)

















