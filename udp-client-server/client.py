"""
Author: Nastaran Motiee
"""
from threading import Thread
import socket
import sys
import select


server_addr = ('127.0.0.1', 9999)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
my_name = input('Enter your name: ')

disconnect_client = False

sock.sendto(my_name.encode(), server_addr)


def output_recvfrom(sock):
    while not disconnect_client:
        ready_to_read, _, _ = select.select([sock], [], [], 1)  # 1 second timeout

        if ready_to_read:
            data, addr = sock.recvfrom(1024)
            print(data.decode())


x = Thread(target=output_recvfrom, args=(sock,))
x.start()

try:
    for line in sys.stdin:
        sock.sendto(line.strip().encode(), server_addr)
except KeyboardInterrupt:
    print("KeyboardInterrupt detected, disconnecting client...")
    disconnect_client = True
    x.join()
    sock.close()
except Exception as e:
    print("Error occurred", e)


