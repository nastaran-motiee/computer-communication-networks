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
SERVER_RELATED = 0
USER_RELATED = 1

addresses = [('127.0.0.1', 12345), ('127.0.0.1', 12346), ('127.0.0.1', 12347), ('127.0.0.1', 12348),
             ('127.0.0.1', 12349)]  # Predefined addresses for the servers
connected_servers_dict = {}  # Global dictionary to store server addresses and sockets
connected_users_dict = {}  # Global dictionary to store user addresses and sockets


def main():
    """
    Main function
    :return:
    """

    # Get the index of the port to use from the user
    index = int(input("Enter the index of the port to use (0-4): "))

    global own_port
    own_port = addresses[index][1]

    # Create a socket and bind it to the port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", own_port))

    # Start listening for incoming connections
    sock.listen(5)

    print(f"Server is listening on port:{own_port}")

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

    for addr in addresses:
        if addr[1] == own_port or addr[1] in connected_servers_dict:
            continue  # Skip the own port and already connected servers

        # Try to establish connection with a server
        try:
            msg_type, subtype, msg_length, sublen, online_servers = create_connection(addr)

            # If the server we connected to is connected to other servers,
            # then it will send their addresses, so msg_length won't be 0
            if msg_length != 0:
                online_servers_list = online_servers.split('\0')  # Split the string to a list of online servers
                # For each online server address
                for online_server_addr in online_servers_list:
                    ip, port = online_server_addr.split(':')  # Split the address to ip and port
                    address = (ip, int(port))  # Create a tuple of ip and port

                    # Connect to the server if it's not your self and not already connected to you
                    if address[1] != own_port and address not in connected_servers_dict.keys():
                        create_connection(address)

            break

        except ConnectionRefusedError:
            print(f"{addr} refused the connection...")
    if len(connected_servers_dict) == 0:
        print("No other servers are available...")


def create_connection(addr):
    """
    :param addr: address of the server to connect to
    :return: msg_type, subtype, sublen, data(online servers)
    """

    # Create a socket and connect to another server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", own_port))
    sock.connect(addr)

    print(f"Connected to {addr}")

    # Add the servers socket to the connected servers dictionary
    connected_servers_dict[addr] = sock

    # Declare that you are a server (message type 2, subtype 0)
    message = create_message(DEFINE_USERNAME, SERVER_RELATED)
    send_message(sock, message)

    # Request information about other connected servers (message type 0, subtype 0)
    message = create_message(REQUEST_CONNECTION_INFO, SERVER_RELATED)
    send_message(sock, message)

    # Receive the response
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

        # Print the address of the client
        print(f"Connection from {incoming_connection_address} established")

        # Start a thread to handle the client
        incoming_connection_thread = threading.Thread(target=handle_incoming_connection,
                                                      args=(incoming_connection_socket, incoming_connection_address,))
        incoming_connection_thread.start()


def handle_incoming_connection(incoming_connection_socket, incoming_connection_address):
    """
    Handles an incoming connection.
    Receives a message from the incoming connection and sends a response.
    :param incoming_connection_socket:
    :return:
    """

    connected = True  # A flag to indicate if the connection is still active

    while connected:
        # Receive a message from incoming connection
        msg_type, subtype, length, sublen, data = receive_message(incoming_connection_socket)

        if msg_type == DEFINE_USERNAME:
            # Add the address and socket of the server or user to the related dictionary
            add_to_related_dict(subtype, incoming_connection_address, data, incoming_connection_socket)
        elif msg_type == REQUEST_CONNECTION_INFO:
            # Send information about connected servers or users
            send_info(subtype, incoming_connection_socket)


def add_to_related_dict(subject, address, username, sock):
    """
    Adds the address and socket of a server or a user to the related dictionary according to the subject
    :param subject:
    :param address:
    :param username:
    :param sock:
    :return:
    """
    if subject == SERVER_RELATED:
        connected_servers_dict[address] = sock
    elif subject == USER_RELATED:
        connected_users_dict[username] = address


def send_info(subject, target_address):
    """
    Sends information about connected servers or users to the target address according to the subject
    :param subject: ABOUT_CONNECTED_SERVERS or ABOUT_CONNECTED_USERS
    :param target_address: The address to send the information to
    :return:
    """
    info = None
    if subject == SERVER_RELATED:
        # Convert connected_servers_dict to string
        info = "\0".join(f"{ip}:{port}" for ip, port in connected_servers_dict.keys())
    elif subject == USER_RELATED:
        # Convert connected_users_dict to string
        info = "\0".join(f"{username}" for username in connected_users_dict.keys())

    if info:
        # Convert the info to message type = 1
        message = create_message(RESPONSE_CONNECTION_INFO, subject, info)
        # Send online_servers_str as a message
        send_message(target_address, message)


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

    return msg_type, subtype, length, sublen, data


if __name__ == "__main__":
    main()
