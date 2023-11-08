import socket
import threading
import sys
import subprocess
import helpers as h
from datetime import datetime
from time import sleep
"""
 Name: Gerard Moylan
 Student ID: 21364007
"""

server_port = 50000
buffer_size = 65535


class Router:
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.adjacent_networks = h.get_adjacent_networks()
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.bind(('', server_port))
        print(f"Router {self.ip} up and listening at {datetime.now().strftime('%H:%M:%S')}!")
        self.seen_packets = []
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def begin(self):
        t1 = threading.Thread(target=self.listen)

        t1.start()

        t1.join()

    def listen(self):
        while True:
            incoming_msg, address = self.sock.recvfrom(buffer_size)
            bools, packet_id, src_addr, dest_addr = h.unpack_header(incoming_msg[:11])

            # Start broadcasting to every router except the one it just received a packet from
            if packet_id not in self.seen_packets:
                print(f'Router {self.ip} received packet id {packet_id}')
                self.broadcast(incoming_msg)
                self.seen_packets.append(packet_id)

    def broadcast(self, packet):
        for addr in self.adjacent_networks:
            self.sock.sendto(packet, (h.addr_to_broadcast_addr(addr), 50000))
            print("message sent!")

def main():
    router = Router()
    router.begin()


if __name__ == "__main__":
    main()






