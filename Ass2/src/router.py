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
        self.outstanding_requests = dict()  # Stores if any routers have requested data from it
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.min_hops_to_endpoint = dict()  # Minimum hops to each endpoint
        self.requested_addresses = []  # All addresses currently requested by it

    def begin(self):
        t1 = threading.Thread(target=self.listen)

        t1.start()

        t1.join()

    def listen(self):
        while True:
            incoming_msg, address = self.sock.recvfrom(buffer_size)
            address = address[0]
            header = incoming_msg[:12]
            bools, no_hops, packet_id, src_addr, dest_addr = h.unpack_header(header)
            sender_can_reach_dest = h.check_nth_bit(bools, 7)  # double check
            is_broadcast = h.check_nth_bit(bools, 6)

            if dest_addr not in self.forward_table:
                if not sender_can_reach_dest and packet_id not in self.seen_packets:  # if that, then it is a request
                    print(f'received request for addr {dest_addr} from {address}')
                    self.seen_packets.append(packet_id)
                    if address not in self.outstanding_requests:
                        self.outstanding_requests[dest_addr] = [address]
                    else:
                        self.outstanding_requests[dest_addr].append(address)
                    incoming_msg = b'\x40' + incoming_msg[1:]
                    self.broadcast(incoming_msg)
                elif sender_can_reach_dest:  # maybe say if pack id not in seen packets
                    print(f'Received word that router {address} CAN reach dest {dest_addr}')
                    if dest_addr not in self.min_hops_to_endpoint or self.min_hops_to_endpoint[dest_addr] < no_hops:
                        self.min_hops_to_endpoint[dest_addr] = int.from_bytes(no_hops, byteorder='little')
                        self.forward_table[dest_addr] = address
                        print(f'fwd table is updated, now {self.forward_table}')
                    no_hops = self.min_hops_to_endpoint[dest_addr] + 1
                    header = b'\x80' + no_hops.to_bytes(1, byteorder='little') + header[2:]
                    incoming_msg = header + incoming_msg[12:]
                    for router in self.outstanding_requests[dest_addr]:  # Reply to all routers that need this dest
                        print(f'Contacting router {router} to say i know {dest_addr}')
                        self.sock.sendto(incoming_msg, (router, 50000))  # send dest_is_known reply
                    del self.outstanding_requests[dest_addr]
            elif dest_addr in self.forward_table and packet_id not in self.seen_packets:
                print(f'Received packet that i know the path to already dest: {dest_addr}')
                self.seen_packets.append(packet_id)
                if not sender_can_reach_dest:  # if that, then it is a request
                    incoming_msg = b'\x80' + (self.min_hops_to_endpoint[dest_addr] + 1).to_bytes(1) + incoming_msg[2:]
                    self.sock.sendto(incoming_msg, (address, 50000))
                #fwd
                self.sock.sendto(incoming_msg, (self.forward_table[dest_addr], 50000))
            if packet_id not in self.seen_packets:
                self.seen_packets.append(packet_id)




    def broadcast(self, packet):
        for addr in self.adjacent_networks:
            self.sock.sendto(packet, (h.addr_to_broadcast_addr(addr), 50000))
            print("Broadcasted request!")

def main():
    router = Router()
    router.begin()


if __name__ == "__main__":
    main()






