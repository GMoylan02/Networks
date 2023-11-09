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
    # TODO implement dest_is_known reply

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
        header = b'\x40\x00' + random.randbytes(2) + self.address + self.address[::-1]
        print(header)
        message = 'Hello, World!'.encode()
        for addr in self.adjacent_networks:
            self.sock.sendto(header + message, (h.addr_to_broadcast_addr(addr), 50000))
            print("message sent!")

    def listen(self):
        while True:
            incoming_msg, address = self.sock.recvfrom(buffer_size)
            address = address[0]
            bools, no_hops, packet_id, src_addr, dest_addr = h.unpack_header(incoming_msg)
            if h.check_nth_bit(bools, 6):
                print(f'received request for my location, contacting router {address}')
                incoming_msg = b'\x80' + (int.from_bytes(no_hops, byteorder='little') + 1).to_bytes(1, byteorder='little') + incoming_msg[2:]
                self.sock.sendto(incoming_msg, (address, server_port))
            print(f'from {src_addr}, bools is {bools}, no_hops is {no_hops}')
            print(f"Received packet from {src_addr} with the message {incoming_msg} at {datetime.now().strftime('%H:%M:%S')}!")



def main(argv):
    addr = h.string_to_hex(argv[1])
    client = Client(argv[0], addr)
    client.begin()


if __name__ == "__main__":
    main(sys.argv[1:])
