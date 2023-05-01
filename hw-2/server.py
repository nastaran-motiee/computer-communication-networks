"""
HW 2
Author: Nastaran Motiee
"""
import socket
import threading

# Array of 5 ports
ports = [12345, 12346, 12347, 12348, 12349]


def main():
    index = int(input("Enter the index of the port to use (0-4): "))
    own_port = ports[index]

    # Create a socket object (AF_INET refers to IPv4, and SOCK_STREAM refers to TCP)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the host and port
    server_socket.bind(("127.0.0.1", own_port))

    # Start listening for connections with a maximum queue of 5 clients
    server_socket.listen(5)
    print(f"Server is listening on 127.0.0.1:{own_port}")

    # Start a thread that accepts incoming connections
    accept_thread = threading.Thread(target=accept_connections, args=(server_socket,))
    accept_thread.start()

    # Connect to other servers
    connect_to_servers(own_port)


def accept_connections(server_socket):
    while True:
        # Accept connections from clients
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address} established")

        # Create a new thread for each connection
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()


def handle_client(client_socket):
    # Receive data from the client (buffer size 1024 bytes)
    data = client_socket.recv(1024).decode()

    if data == "Hello":
        # Send the "World" message to the client
        client_socket.sendall("World".encode())

    # Close the client socket
    client_socket.close()


def connect_to_servers(own_port):
    for port in ports:
        if port == own_port:
            continue

        try:
            # Connect to the specified host and port
            connect_to_server("127.0.0.1", port)
        except ConnectionRefusedError:
            print(f"No listener on port {port}")


def connect_to_server(host, port):
    # Create a socket object (AF_INET refers to IPv4, and SOCK_STREAM refers to TCP)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the specified host and port
    client_socket.connect((host, port))
    print(f"Connected to {host}:{port}")

    # Send the "Hello" message to the server
    client_socket.sendall("Hello".encode())

    # Receive data from the server (buffer size 1024 bytes)
    data = client_socket.recv(1024).decode()

    if data == "World":
        print("The End")

    # Close the connection
    client_socket.close()


if __name__ == "__main__":
    main()
