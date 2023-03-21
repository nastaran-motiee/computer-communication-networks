"""
Author: Nastaran Motiee
ID: 329022727
"""
import threading
import time
import socket
import select

UDP_IP = '0.0.0.0'
UDP_PORT = 9999

db = dict()


class Server(threading.Thread):
    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.stop_flag = False

    def run(self):
        global sender_addr

        print("Server is running")

        while not self.stop_flag:

            try:
                # Set a timeout for the blocking recvfrom() operation using select()
                ready_to_read, _, _ = select.select([self.sock], [], [], 1)  # 1 second timeout

                if ready_to_read:
                    data, sender_addr = self.sock.recvfrom(1024)
                    data = data.decode()

                    # if the client does not exist in database, add the client
                    if not db.get(sender_addr):
                        db[sender_addr] = data
                        print(f"{data}: from {sender_addr} was added to database")
                        self.sock.sendto("Your name and address were added to the database.".encode(), sender_addr)
                    else:
                        # else check if the receiver exists in the database
                        receiver_client, message = data.split(maxsplit=1)
                        existing_clients = list(db.values())
                        index = existing_clients.index(receiver_client)
                        receiver_addr = list(db.keys())[index]
                        self.sock.sendto(f"You have a new message.\n {db.get(sender_addr)}: {message}".encode(),
                                         receiver_addr)

            except ValueError as e:
                self.sock.sendto("User does not exist. please try again.".encode(),
                                 sender_addr)

            except Exception as e:
                print("Error occurred:", e)

    def stop(self):
        self.stop_flag = True


def main():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

    sock.bind((UDP_IP, UDP_PORT))

    # Start the receiver thread
    server = Server(sock)
    server.start()

    try:
        while True:
            # Keep the main thread running, waiting for KeyboardInterrupt
            time.sleep(1)
    except KeyboardInterrupt:
        print("Ctrl + C detected, stopping the server...")
        server.stop()
        server.join()
        sock.close()
        print("Server stopped and socket closed.")


if __name__ == '__main__':
    main()
