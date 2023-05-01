"""
HW 3
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

    global own_port
    own_port = ports[index]

    # Create a socket and bind it to the port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", own_port))

    # Start listening for incoming connections
    sock.listen(5)
    print(f"Server is listening on Port:{own_port}")
    # Connect to all online servers
    connect_to_all_online_servers()

    # Start a thread to accept incoming connections
    accept_thread = threading.Thread(target=accept_connections, args=(sock,))
    accept_thread.start()


def connect_to_all_online_servers():
    """
    Connects to all online servers
    :return:
    """

    print("Attempting to connect to other servers, please wait ...")

    for port in ports:
        if port == own_port or port in connected_servers_dict:
            continue  # Skip the own port and already connected servers

        # Try to establish connection with a server
        try:
            msg_type, subtype, msg_length, sublen, online_servers = connect_to_server("127.0.0.1", port)

            # If connected to a server, then ask for all connected servers and connect to them
            if msg_length != 0:
                online_servers_list = online_servers.split('\0')
                for online_port in online_servers_list:
                    int_online_port = int(online_port)
                    if int_online_port != own_port and int_online_port not in connected_servers_dict:
                        connect_to_server("127.0.0.1", int_online_port)
            break

        except ConnectionRefusedError:
            print(f"couldn't connect port {port}")
    if len(connected_servers_dict) == 0:
        print("No other servers are available...")


def connect_to_server(ip_address, port):
    """
    :param ip_address:
    :param port:
    :return: msg_type, subtype, sublen, data(online servers)
    """

    # Create a socket and connect to another server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", own_port))

    sock.connect((ip_address, port))
    print(f"Connected to {ip_address}:{port}")

    # Add the server to the connected servers dictionary
    connected_servers_dict[port] = ip_address

    # Create a message of type = 0
    request = create_message(REQUEST_CONNECTION_INFO, ABOUT_CONNECTED_SERVERS)

    # Send a message to the server. (request information about connected servers)
    send_message(sock, request)

    msg_type, subtype, length, sublen, data = receive_message(sock)

    return msg_type, subtype, length, sublen, data


def accept_connections(server_socket):
    """
    Accepts incoming connections
    :param server_socket:
    :return:
    """

    while True:
        # Accept the connection
        incoming_connection_socket, incoming_connection_address = server_socket.accept()

        # Add the connection to the dictionary of connected servers
        connected_servers_dict[incoming_connection_address[1]] = incoming_connection_address[0]

        # Print the address of the client
        print(f"Connection from {incoming_connection_address} established")

        # Start a thread to handle the client
        incoming_connection_thread = threading.Thread(target=handle_incoming_connection,
                                                      args=(incoming_connection_socket,))
        incoming_connection_thread.start()


def handle_incoming_connection(incoming_connection_socket):
    """
    Handles the incoming connection
    :param incoming_connection_socket:
    :return:
    """

    # Receive a message from incoming connection
    msg_type, subtype, length, sublen, data = receive_message(incoming_connection_socket)

    # Handle the message
    if msg_type == REQUEST_CONNECTION_INFO and subtype == ABOUT_CONNECTED_SERVERS:
        # Convert connected_servers_dict to string
        online_servers_str = "\0".join(str(port) for port in connected_servers_dict.keys())
        # Convert the online_server_str to message type = 1
        message = create_message(RESPONSE_CONNECTION_INFO, subtype, online_servers_str)
        # Send online_servers_str as a message
        send_message(incoming_connection_socket, message)

    incoming_connection_socket.close()


def create_message(type, subtype, data=""):
    """
    Creates a message
    :param type: integer
    :param subtype: integer
    :param data: string
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
    if length != 0:
        print(f"Received data: {data}")

    return msg_type, subtype, length, sublen, data


if __name__ == "__main__":
    main()
