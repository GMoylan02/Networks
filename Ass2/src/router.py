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
current_dests = []  #queue
current_routers = []  #queue


class Router:
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.adjacent_networks = h.get_adjacent_networks()
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.bind(('', server_port))
        print(f"Router {self.ip} up and listening at {datetime.now().strftime('%H:%M:%S')}!")
        self.seen_packets = []
        self.forward_table = dict()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def begin(self):
        t1 = threading.Thread(target=self.listen)

        t1.start()

        t1.join()

    def listen(self):
        while True:
            incoming_msg, address = self.sock.recvfrom(buffer_size)
            bools, packet_id, src_addr, dest_addr = h.unpack_header(incoming_msg[:11])
            dest_is_known = bools[0] == b'\b01' # double check

            if dest_addr not in self.forward_table and packet_id not in self.seen_packets:
                if not dest_is_known:
                    print(f'Router {self.ip} received packet id {packet_id}')
                    # this may break for lots of packets, refactor later
                    current_dests.append(dest_addr)
                    current_routers.append(address)
                    self.broadcast(incoming_msg)
                    self.seen_packets.append(packet_id)
                else:
                    self.forward_table[current_dests.pop(0)] = address
                    self.sock.sendto(incoming_msg, (current_routers.pop(0), 50000)) # send dest_is_known reply
            elif dest_addr in self.forward_table and packet_id not in self.seen_packets:
                self.sock.sendto(incoming_msg, (self.forward_table[dest_addr], 50000))



    def broadcast(self, packet):
        for addr in self.adjacent_networks:
            self.sock.sendto(packet, (h.addr_to_broadcast_addr(addr), 50000))
            print("message sent!")

def main():
    router = Router()
    router.begin()


if __name__ == "__main__":
    main()






