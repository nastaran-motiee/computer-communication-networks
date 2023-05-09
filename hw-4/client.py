"""
HW 4
"""
import time
import threading
from threading import Thread
import socket
import struct
import atexit
import queue

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
ECHO = 4

# Message subtypes
USER_RELATED = 1
SERVER_RELATED = 0

disconnect_client = False
server_addresses = [('127.0.0.1', 12345), ('127.0.0.1', 12346), ('127.0.0.1', 12347), ('127.0.0.1', 12348),
                    ('127.0.0.1', 12349)]  # Predefined addresses for the servers

messages = []  # List of messages received.
sockets = []  # List of sockets
current_master_server_addr = None  # The address of the current master server
stop_event = threading.Event()
rtt_list_completed = threading.Event()
rtt_list = []  # List of RTT results


def send_message(sock, subtype=1):
    # TODO subtype may change in the next assignment
    """
    Sends a message to (type=3)
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
    while not stop_event.is_set():
        # Receive the header
        try:
            header = sock.recv(6)

            # Unpack the header
            if len(header):
                msg_type, subtype, length, sublen = struct.unpack('>BBHH', header)

                # Receive the data
                data = sock.recv(length).decode()
                handle_message(msg_type, data, sublen)
        except ConnectionAbortedError:
            print('Connection aborted.')
            break
        except Exception as e:
            print(e)
            break


def create_socket():
    """
    Creates a socket
    :return:
    """
    # Create a socket and connect to the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockets.append(sock)
    return sock


def handle_message(msg_type, data, sublen):
    if msg_type == SEND_MESSAGE:
        msg_from = data[sublen:]
        sender_username, msg = msg_from.split('\0')
        messages.append(f"\033[0;31m{sender_username}:\033[0;0m {msg}")
    elif msg_type == RESPONSE_CONNECTION_INFO:
        connected_servers = []
        if data != '\0':
            online_servers_list = data.split('\0')  # Split the string to a list of online servers
            # For each online server address

            for online_server_addr in online_servers_list:
                ip, port = online_server_addr.split(':')  # Split the address to ip and port
                address = (ip, int(port))  # Create a tuple of ip and port
                connected_servers.append(address)  # Add the address to the list of connected servers
        connected_servers.append(current_master_server_addr)
        global rtt_list
        rtt_list = connect_to_all_servers_and_measure_rtt(connected_servers)
        print(f"RTT results: {rtt_list}")
        rtt_list_completed.set()


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


def connect_to_server_and_measure_rtt(addr, results_queue):
    """
    Connects to a server and measures the RTT
    :param addr:
    :param results_queue:
    :return:
    """
    sock = create_socket()
    try:
        sock.connect(addr)
        msg = create_message(ECHO)
        start_time = time.time()
        sock.send(msg)
        response = sock.recv(6)
        end_time = time.time()

        msg_type, _, _, _ = struct.unpack('>BBHH', response)
        if msg_type == ECHO:
            rtt = end_time - start_time
            results_queue.put((addr, rtt))

        sock.close()
    except ConnectionRefusedError:
        print(f"Connection refused by server at {addr}.")
        results_queue.put((addr, float('inf')))


def connect_to_all_servers_and_measure_rtt(server_addrs):
    """
    Connects to all servers and measures the RTT
    :param server_addrs: list of server addresses
    :return:
    """
    results_queue = queue.Queue()
    threads = []

    for addr in server_addrs:
        thread = threading.Thread(target=connect_to_server_and_measure_rtt, args=(addr, results_queue))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    rtt_results = []
    while not results_queue.empty():
        rtt_results.append(results_queue.get())

    return rtt_results


def exit_handler():
    """
    Closes the sockets
    :return:
    """
    print('Closing the sockets...')
    for s in sockets:
        s.close()


@atexit.register
def close_sockets():
    for s in sockets:
        s.close()


def main():
    global current_master_server_addr
    # Choose a server to connect to
    server_addr_index = input("Enter the index of the server to connect to (0-4):").strip()

    # Create a socket and connect to the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect(server_addresses[int(server_addr_index)])
    current_master_server_addr = server_addresses[int(server_addr_index)]
    res = connect_to_all_servers_and_measure_rtt([server_addresses[int(server_addr_index)]])

    print(f"RTT to server {server_addresses[int(server_addr_index)]} is {res[0][1]}")

    sockets.append(sock)
    # Create a username
    username = input('Enter your username:').strip()
    create_username(sock, username)

    # Start a thread to receive messages
    receive_thread = Thread(target=receive_message, args=(sock,))
    receive_thread.start()

    while True:
        time.sleep(0.5)
        read_or_write = input(
            CYAN_COLOR + '1. Enter 1 - to send a message.\n2. Enter 2 - to read new messages. \n3. Enter 3 - to '
                         'exit.\n4. Enter 4 - to connect to best server.\n' + RESET_COLOR).strip()
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
                    messages.pop()
        elif read_or_write == '3':
            sock.close()
            break
        elif read_or_write == '4':
            # Request information about other connected servers (message type 0, subtype 0)
            message = create_message(type=REQUEST_CONNECTION_INFO, subtype=SERVER_RELATED)
            sock.send(message)
            while not rtt_list_completed.is_set():
                pass
            rtt_list_completed.clear()
            # Choose the best server
            best_server = min(rtt_list, key=lambda x: x[1])
            print(f"Best server is {best_server[0]} with RTT {best_server[1]}")
            if best_server[0] != current_master_server_addr:
                sock.close()
                sock = create_socket()
                sock.connect(best_server[0])
                current_master_server_addr = best_server[0]
                print(f"Connected to {best_server[0]}")
                # Create a username
                username = input('Enter your username:').strip()
                create_username(sock, username)
                # Start a thread to receive messages
                receive_thread = Thread(target=receive_message, args=(sock,))
                receive_thread.start()

    receive_thread.join()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted.')
    except ConnectionRefusedError:
        print('Connection refused.')
    except Exception as e:
        print('Exception occurred.', e)
    finally:
        stop_event.set()
        exit_handler()
