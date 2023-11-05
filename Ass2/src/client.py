import socket
import threading
import sys
import subprocess
import string
import helpers as h
from datetime import datetime

"""
 Name: Gerard Moylan
 Student ID: 21364007
"""

server_port = 50000
buffer_size = 65535


class Client:

    def __init__(self, local_ip, addr):
        self.address = addr
        self.ip = local_ip
        self.adjacent_networks = h.get_adjacent_networks()
        try:
            self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.sock.bind((self.ip, server_port))
        except:
            print(f"Doesnt like ip {self.ip}, {datetime.now().strftime('%H:%M:%S')}")
        print(f"Client {self.ip} up and running at {datetime.now().strftime('%H:%M:%S')}!")

    def begin(self):
        t1 = threading.Thread(target=self.send)
        t2 = threading.Thread(target=self.listen)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    def send(self):
        message = "Hello, World!".encode()
        header = b'\x00' + self.address + self.address[::-1]
        for addr in self.adjacent_networks:
            self.sock.sendto(header + message, (addr, 50000))

    def listen(self):
        while True:
            incoming_msg, address = self.sock.recvfrom(buffer_size)
            bools, src_addr, dest_addr = h.unpack_header(incoming_msg[:9])
            print(f"Received packet from {src_addr} with the message {incoming_msg[12:]} at {datetime.now().strftime('%H:%M:%S')}!")


def main(argv):
    addr = h.string_to_hex(argv[1])
    client = Client(argv[0], addr)
    client.begin()


if __name__ == "__main__":
    main(sys.argv[1:])
