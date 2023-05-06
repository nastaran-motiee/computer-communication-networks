"""
HW 2
Author: Nastaran Motiee
"""
import time
from threading import Thread
import socket
import struct

# Message types
DEFINE_USERNAME = 2
SEND_MESSAGE = 3

# Message subtypes
USER_RELATED = 1
SERVER_RELATED = 0

disconnect_client = False
server_addresses = [('127.0.0.1', 12345), ('127.0.0.1', 12346), ('127.0.0.1', 12347), ('127.0.0.1', 12348),
                    ('127.0.0.1', 12349)]  # Predefined addresses for the servers

messages = []  # List of messages received.


def main():
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

    while True:
        read_or_write = input(
            '1. Enter 1 - to send a message.\n2. Enter 2 - to read your messages. \n3. Enter 3- to exit.\n').strip()
        if read_or_write == '1':
            # Start a thread to send messages
            send_thread = Thread(target=send_message, args=(sock,))
            send_thread.start()
            send_thread.join()
        elif read_or_write == '2':
            if len(messages) == 0:
                print('\033[0;32mYou have no messages.\033[0;0m')
            else:
                # Print the messages
                for msg in messages:
                    print(msg)
        elif read_or_write == '3':
            sock.close()
            break


def send_message(sock, subtype=1):
    # TODO subtype may change in the next assignment
    """
    Sends a message to (type=3)
    :param subtype:
    :param sock: socket
    :return:
    """
    # input, o, e = select.select([sys.stdin, sock], [], [], 10)
    # TODO : continue from here

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
        # Receive the header
        try:
            header = sock.recv(6)
        except ConnectionAbortedError:
            print('Connection aborted.')
            break
        except Exception as e:
            print(e)
            break

        if len(header) == 0:
            print('Connection closed.')
            continue

        # Unpack the header
        msg_type, subtype, length, sublen = struct.unpack('>BBHH', header)

        # Receive the data
        data = sock.recv(length).decode()
        msg_from = data[sublen:]
        sender_username, msg = msg_from.split('\0')

        messages.append(f"{sender_username}: {msg}")
        print("length" + str(len(messages)))

        return msg_type, subtype, length, sublen, data


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
