import socket
import threading
import sys
import helpers as h
from datetime import datetime
from time import sleep
import random

"""
 Name: Gerard Moylan
 Student ID: 21364007
"""

server_port = 50000
buffer_size = 65535


class Client:
    # TODO rework unpack

    def __init__(self, local_ip, addr):
        self.address = addr
        self.ip = local_ip
        self.adjacent_networks = h.get_adjacent_networks()  # Actually probably not needed at all
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.bind(('', server_port))
        print(f"Client {self.ip} up and running at {datetime.now().strftime('%H:%M:%S')}!")
        print(f'deez {h.addr_to_broadcast_addr(self.adjacent_networks[0])}')
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def begin(self):
        t1 = threading.Thread(target=self.broadcast)
        t2 = threading.Thread(target=self.listen)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    def broadcast(self):
        header = b'\x00' + random.randbytes(2) + self.address + self.address[::-1]
        message = 'Hello, World!'.encode()
        for addr in self.adjacent_networks:
            print(f'deez2 {h.addr_to_broadcast_addr(addr)}')
            self.sock.sendto(header + message, (h.addr_to_broadcast_addr(addr), 50000))
            print("message sent!")

    def listen(self):
        while True:
            incoming_msg, address = self.sock.recvfrom(buffer_size)
            bools, packet_id, src_addr, dest_addr = h.unpack_header(incoming_msg[:9])
            print(f"Received packet from {src_addr} with the message {incoming_msg[12:]} at {datetime.now().strftime('%H:%M:%S')}!")



def main(argv):
    addr = h.string_to_hex(argv[1])
    client = Client(argv[0], addr)
    client.begin()


if __name__ == "__main__":
    main(sys.argv[1:])
