import socket
import threading
import sys
import subprocess
import helpers as h
from datetime import datetime
"""
 Name: Gerard Moylan
 Student ID: 21364007
"""

server_port = 50000
buffer_size = 65535


class Router:
    def __init__(self, ip):
        self.adjacent_networks = h.get_adjacent_networks()
        self.ip = ip
        try:
            self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.sock.bind((self.ip, server_port))
        except:
            print(f"doesnt like ip {ip}")
        print(f"Router {self.ip} up and listening at {datetime.now().strftime('%H:%M:%S')}!")

    def listen(self):
        while True:
            incoming_msg, address = self.sock.recvfrom(buffer_size)
            print(f"Received packet from {address}!")

            bools, src_addr, dest_addr = h.unpack_header(incoming_msg[:9])

            if dest_addr not in self.adjacent_networks:
                self.broadcast(incoming_msg)
            else:
                self.sock.sendto(incoming_msg, (dest_addr, 50000))

    def broadcast(self, packet):
        print(f"Router {self.ip} is broadcasting!")
        for addr in self.adjacent_networks:
            self.sock.sendto(packet, (addr, 50000))


def main(argv):
    router = Router(argv)
    router.listen()


if __name__ == "__main__":
    main(sys.argv[1])






