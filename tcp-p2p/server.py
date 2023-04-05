"""
Author: Nastaran Motiee
"""
import socket
import threading
import struct

# Message types
REQUEST_CONNECTION_INFO = 0
RESPONSE_CONNECTION_INFO = 1
DEFINE_USERNAME = 2
SEND_MESSAGE = 3

# Message subtypes
ABOUT_CONNECTED_SERVERS = 0
ABOUT_CONNECTED_USER = 1

ports = [12345, 12346, 12347, 12348, 12349]  # Array of 5 ports
connected_servers_dict = {}  # Global dictionary to store server addresses and sockets


def main():
    """
    Main function
    :return:
    """
    # Get the index of the port to use from the user
    index = int(input("Enter the index of the port to use (0-4): "))
    own_port = ports[index]

    # Create a socket and bind it to the port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", own_port))

    # Start listening for incoming connections
    sock.listen(5)
    print(f"Server is listening on Port:{own_port}")

    # Start a thread to accept incoming connections
    accept_thread = threading.Thread(target=accept_connections, args=(sock,))
    accept_thread.start()

    # Connect to all online servers
    connect_to_all_online_servers(own_port)


def accept_connections(server_socket):
    """
    Accepts incoming connections
    :param server_socket:
    :return:
    """

    while True:
        client_socket, client_address = server_socket.accept()  # Accept the connection
        print(f"Connection from {client_address} established")  # Print the address of the client

        # Start a thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()


def handle_client(client_socket):
    """
    Handles the client
    :param client_socket:
    :return:
    """

    # Receive a message from the client
    msg_type, subtype, sublen, data = receive_message(client_socket)

    # Handle the message
    if msg_type == REQUEST_CONNECTION_INFO and subtype == ABOUT_CONNECTED_SERVERS:
        online_servers_str = ",".join(str(port) for port in connected_servers_dict.keys())
        client_socket.sendall(online_servers_str.encode())

    client_socket.close()


def connect_to_all_online_servers(own_port):
    """
    Connects to all online servers
    :param own_port:
    :return:
    """
    num_of_connections = 0
    print("Attempting to connect to other servers...")

    for port in ports:
        if port == own_port or port in connected_servers_dict:
            continue  # Skip the own port and already connected servers

        try:
            online_ports = connect_to_server("127.0.0.1", port, own_port)
            if online_ports:
                for online_port in online_ports:
                    if online_port:
                        int_online_port = int(online_port)
                        if int_online_port != own_port and int_online_port not in connected_servers_dict:
                            sock = connect_to_server("127.0.0.1", int_online_port, own_port)
                            if sock is not None:
                                connected_servers_dict[int_online_port] = sock
            num_of_connections += 1
        except ConnectionRefusedError:
            pass
    if num_of_connections == 0:
        print("No other servers are available...")


def connect_to_server(host, port, own_port):
    """
    Connects to a server
    :param host:
    :param port:
    :param own_port:
    :return: online_servers_list
    """

    # Create a socket and connect to another server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", own_port))

    sock.connect((host, port))
    print(f"Connected to {host}:{port}")

    # Add the server to the connected servers dictionary
    connected_servers_dict[port] = sock

    # Send a message to the server
    request = create_message(REQUEST_CONNECTION_INFO, ABOUT_CONNECTED_SERVERS, "")
    send_message(sock, request)

    # Receive a message from the server
    # TODO: Start with message type = 1
    online_servers_data = sock.recv(1024).decode()
    online_servers_list = online_servers_data.split(',')

    return online_servers_list


def create_message(type, subtype, data):
    """
    Creates a message
    :param type:
    :param subtype:
    :param data:
    :return:
    """
    length = len(data)
    sublen = 0  # Just for now sublen is 0 (it's related to the next assignment)

    # Create the message
    header = struct.pack('>BBHH', type, subtype, length, sublen)
    message = header + data.encode()

    return message


def send_message(sock, message):
    """
    Sends a message
    :param sock:
    :param message:
    :return:
    """
    sock.sendall(message)


def receive_message(sock):
    """
    Receives a message
    :param sock:
    :return: msg_type, subtype, sublen, data
    """
    header = sock.recv(6)
    msg_type, subtype, length, sublen = struct.unpack('>BBHH', header)
    print(f"Received message of type {msg_type} and subtype {subtype} with length {length} and sublength {sublen}")
    data = sock.recv(length).decode()
    print(f"Received data: {data}")
    return msg_type, subtype, sublen, data


if __name__ == "__main__":
    main()
