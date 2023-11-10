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
        self.my_addresses = h.get_addresses()

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
            no_hops_int = int.from_bytes(no_hops, byteorder='little')
            sender_can_reach_dest = h.check_nth_bit(bools, 7)  # double check
            is_broadcast = h.check_nth_bit(bools, 6)
            if address not in self.my_addresses:

                if is_broadcast and packet_id not in self.seen_packets:
                    if src_addr not in self.min_hops_to_endpoint or no_hops_int < self.min_hops_to_endpoint[src_addr]:
                        print(f'Received WhoIs request for {dest_addr} from {address}, appending {src_addr} to my list as well on addr {address}')
                        self.min_hops_to_endpoint[src_addr] = no_hops_int
                        self.forward_table[src_addr] = address
                        print(f'my fwd table is {self.forward_table}')

                    if dest_addr not in self.forward_table:
                        print(f'Forwarding WhoIs request by broadcast!')
                        if dest_addr in self.outstanding_requests:
                            self.outstanding_requests[dest_addr].append(address)
                        else:
                            self.outstanding_requests[dest_addr] = [address]
                        no_hops_int += 1
                        no_hops = no_hops_int.to_bytes(1, byteorder='little')
                        message_to_send = bools + no_hops + incoming_msg[2:]
                        print(f'Broadcasting the WhoIs request for {dest_addr} from {address}')
                        self.broadcast(message_to_send)

                    elif dest_addr in self.forward_table:
                        print(f'Received WhoIs request for {dest_addr}, whom I already know! Sending reply and forwarding!')
                        self.sock.sendto(incoming_msg, (self.forward_table[dest_addr], 50000))
                        no_hops_int = self.min_hops_to_endpoint[dest_addr]
                        no_hops_int += 1
                        no_hops = no_hops_int.to_bytes(1, byteorder='little')
                        message_to_send = b'\x80' + no_hops + incoming_msg[2:]
                        self.sock.sendto(message_to_send, (address, 50000))

                elif not is_broadcast:
                    if dest_addr not in self.forward_table or src_addr not in self.min_hops_to_endpoint or no_hops_int < self.min_hops_to_endpoint[src_addr]:
                        print(f'Received a response to my previous request for {dest_addr} from address {address}, adding to table!')
                        self.forward_table[dest_addr] = address
                        print(f'my fwd table is {self.forward_table}')
                        self.min_hops_to_endpoint[dest_addr] = no_hops_int
                        no_hops_int += 1
                        no_hops = no_hops_int.to_bytes(1, byteorder='little')
                        message_to_send = b'\x80' + no_hops + incoming_msg[2:]
                        for net in self.outstanding_requests[dest_addr]:
                            self.sock.sendto(message_to_send, (net, 50000))
                    else:
                        print(f'Received a regular packet, forwarding!')
                        self.sock.sendto(incoming_msg, (self.forward_table[dest_addr], 50000))
            self.seen_packets.append(packet_id)

    def broadcast(self, packet):
        for addr in self.adjacent_networks:
            self.sock.sendto(packet, (h.addr_to_broadcast_addr(addr), 50000))


def main():
    router = Router()
    router.begin()


if __name__ == "__main__":
    main()






