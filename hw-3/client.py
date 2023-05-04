"""
HW 2
Author: Nastaran Motiee
"""
import time
from threading import Thread
import socket
import sys
import select
import struct

# Message types
DEFINE_USERNAME = 2
SEND_MESSAGE = 3

# Message subtypes
USER_RELATED = 1
SERVER_RELATED = 0

disconnect_client = False


def main():
    server_addresses = [('127.0.0.1', 12345), ('127.0.0.1', 12346), ('127.0.0.1', 12347), ('127.0.0.1', 12348),
                        ('127.0.0.1', 12349)]  # Predefined addresses for the servers

    # Choose a server to connect to
    server_addr_index = input("Enter the index of the server to connect to (0-4):")

    # Create a socket and connect to the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

    sock.connect(server_addresses[int(server_addr_index)])

    # Create a username
    username = input('Enter your username:').strip()
    create_username(sock, username)

    # Start a thread to receive messages
    receive_thread = Thread(target=receive_message, args=(sock,))
    receive_thread.start()

    # Start a thread to send messages
    send_thread = Thread(target=send_message, args=(sock,))
    send_thread.start()


def send_message(sock, subtype=SERVER_RELATED):
    # TODO subtype may change in the next assignment
    """
    Sends a message to the server
    :param subtype:
    :param sock: socket
    :return:
    """

    target_username = input('Enter the username of the recipient:').strip()
    message = input('Enter your message:').strip()

    sublen = len(target_username)
    length = len(message) + sublen

    # Create the message type = 3
    header = struct.pack('>BBHH', SEND_MESSAGE, subtype, length, sublen)
    packed_message = header + f"{target_username}{message}".encode()
    sock.sendall(packed_message)


def receive_message(sock):
    while True:
        data = sock.recv(6)
        print(data.decode())


def create_username(sock, username):
    """
    Creates a username for the client
    :param sock: socket
    :param username: username
    :return:
    """
    length = len(username)
    sublen = 0  # Just for now sublen is 0 (it's related to the next assignment)

    # Create the message type = 2
    header = struct.pack('>BBHH', DEFINE_USERNAME, USER_RELATED, length, sublen)
    message = header + username.encode()
    sock.send(message)


if __name__ == '__main__':
    main()
