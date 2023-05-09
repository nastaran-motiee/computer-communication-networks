"""
HW 3
"""

import socket
import sys
import threading
import struct
import atexit

# Colors
RED_COLOR = "\033[0;31m"
GREEN_COLOR = "\033[0;32m"
YELLOW_COLOR = "\033[0;33m"
BLUE_COLOR = "\033[0;34m"
PURPLE_COLOR = "\033[0;35m"
CYAN_COLOR = "\033[0;36m"
RESET_COLOR = "\033[0;0m"

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
sockets = []  # List of sockets
stop_event = threading.Event()  # Global stop event


def create_socket():
    """
    Creates a socket and binds it to the port
    :return:
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sockets.append(sock)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", own_port))
    return sock


@atexit.register
def exit_handler():
    """
    Exit handler.
    This function is called automatically when the program exits.
    :return:
    """
    print("Closing all sockets...")
    for s in sockets:
        s.close()


def create_connection(addr):
    """
    :param addr: address of the server to connect to
    :return: msg_type, subtype, sublen, data(online servers)
    """

    sock = create_socket()
    sock.connect(addr)

    print(f"Connected to {addr}")

    # Add the servers socket to the connected servers dictionary
    connected_servers_dict[addr] = sock

    # Declare that you are a server (message type 2, subtype 0)
    message = create_message(type=DEFINE_USERNAME, subtype=SERVER_RELATED)
    sock.sendall(message)

    # Request information about other connected servers (message type 0, subtype 0)
    message = create_message(type=REQUEST_CONNECTION_INFO, subtype=SERVER_RELATED)
    sock.sendall(message)
    return sock


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
            m_sock = create_connection(addr)
            handle_connection(m_sock, addr)
            break

        except ConnectionRefusedError:
            print(f"{addr} refused the connection...")
        except OSError as os_error:
            print(f"Could not connect to {addr}...", os_error)
    if len(connected_servers_dict) == 0:
        print("No other servers are available...")


def handle_message_by_type(msg_type, subtype, msg_length, sublen, data, incoming_connection_address=None,
                           incoming_connection_socket=None):
    """
    Handles the message based on its type
    :param incoming_connection_socket:
    :param incoming_connection_address:
    :param msg_type:
    :param subtype:
    :param msg_length:
    :param sublen:
    :param data:
    :return:
    """
    if msg_type == RESPONSE_CONNECTION_INFO and msg_length != 0:
        online_servers_list = data.split('\0')  # Split the string to a list of online servers
        # For each online server address
        for online_server_addr in online_servers_list:
            ip, port = online_server_addr.split(':')  # Split the address to ip and port
            address = (ip, int(port))  # Create a tuple of ip and port

            # Connect to the server if it's not your self and not already connected to you
            if address[1] != own_port and address not in connected_servers_dict.keys():
                create_connection(address)

    elif msg_type == DEFINE_USERNAME:
        # Add the address and socket of the server or user to the related dictionary
        add_to_related_dict(subject=subtype, address=incoming_connection_address,
                            username=data, sock=incoming_connection_socket)

    elif msg_type == REQUEST_CONNECTION_INFO:
        # Send information about connected servers or users
        send_info(subtype, incoming_connection_socket)

    elif msg_type == SEND_MESSAGE:
        print("data:", data)
        target_username = data[:sublen]
        msg = data[sublen:]
        for key, value in connected_users_dict.items():
            if value[0] == incoming_connection_address:
                sender_username = key
                msg = sender_username + '\0' + msg
                break

        msg = f"{target_username}{msg}"
        packed_msg = create_message(type=SEND_MESSAGE, subtype=0, sublen=sublen, data=msg)
        if target_username in connected_users_dict.keys():
            connected_users_dict[target_username][1].send(packed_msg)
        else:
            print(f"User '{target_username}' is not connected to this server...")
            print(incoming_connection_address)
            for (server_addr, server_socket) in connected_servers_dict.items():
                if server_addr != incoming_connection_address:
                    server_socket.send(packed_msg)


def accept_connections(server_socket):
    """
    Accepts incoming connections
    :param server_socket:
    :return:
    """

    while not stop_event.is_set():
        try:
            # Accept the connection
            incoming_connection_socket, incoming_connection_address = server_socket.accept()

            # Print the address of the client
            print(f"Connection from {incoming_connection_address} established")

            # Start a thread to handle the client
            incoming_connection_thread = threading.Thread(target=handle_connection,
                                                          args=(incoming_connection_socket,
                                                                incoming_connection_address,))
            incoming_connection_thread.start()
        except socket.timeout:
            pass


def handle_connection(incoming_connection_socket, incoming_connection_address):
    """
    Handles an incoming connection.
    Receives a message from the incoming connection and sends a response.
    :param incoming_connection_socket:
    :param incoming_connection_address:
    :return:
    """

    connected = True  # A flag to indicate if the connection is still active

    while connected:
        try:
            # Receive a message from incoming connection
            msg_type, subtype, length, sublen, data = receive_message(incoming_connection_socket)
            handle_message_by_type(msg_type=msg_type, subtype=subtype, msg_length=length, sublen=sublen, data=data,
                                   incoming_connection_address=incoming_connection_address,
                                   incoming_connection_socket=incoming_connection_socket)

        except Exception as e:
            print(f"Connection with {incoming_connection_address} lost", e)
            connected = False
            incoming_connection_socket.close()


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
        connected_users_dict[username] = [address, sock]


def send_info(subject, sock):
    """
    Sends information about connected servers or users to the target address according to the subject
    :param subject: ABOUT_CONNECTED_SERVERS or ABOUT_CONNECTED_USERS
    :param sock:
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
        message = create_message(type=RESPONSE_CONNECTION_INFO, subtype=subject, data=info)
        # Send online_servers_str as a message
        sock.send(message)


def create_message(type, subtype=0, sublen=0, data=""):
    """
    Creates a message
    :param sublen:
    :param type: integer
    :param subtype: integer
    :param data: string
    :return:
    """

    length = len(data)
    # Create the message
    header = struct.pack('>BBHH', type, subtype, length, sublen)
    message = header + data.encode()

    return message


def receive_message(sock):
    """
    Receives a message
    :param sock:
    :return: msg_type, subtype, sublen, data
    """

    # Receive the header
    header = sock.recv(6)

    if len(header) != 0:
        # Unpack the header
        msg_type, subtype, length, sublen = struct.unpack('>BBHH', header)

        print(f"Received message of type {msg_type} and subtype {subtype} with length {length} and sublength {sublen}")
        # Receive the data
        data = sock.recv(length).decode()
        print(data)

        return msg_type, subtype, length, sublen, data


def main():
    """
    Main function
    :return:
    """

    # Get the index of the port to use from the user
    index = int(input("Enter the index of the port to use (0-4): "))

    global own_port
    own_port = addresses[index][1]

    sock = create_socket()
    sock.listen(5)  # Start listening for incoming connections
    sock.settimeout(1)  # Set a timeout for the accept method

    print(f"Server is listening on port:{own_port}")

    # Start a thread to accept incoming connections
    accept_thread = threading.Thread(target=accept_connections, args=(sock,))
    accept_thread.start()

    # Connect to all online servers
    connect_to_all_online_servers()
    accept_thread.join()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard interrupt...")
    except ConnectionRefusedError:
        print("Connection refused...")
    except Exception as e:
        print(e)
    finally:
        stop_event.set()
        print("Closing server...")
        sys.exit(0)
