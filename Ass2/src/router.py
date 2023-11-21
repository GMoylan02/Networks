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
        print(f"Router {self.ip} up and listening!")
        self.seen_packets = []
        self.forward_table = dict()
        self.outstanding_requests = dict()  # Stores if any routers have requested data from it
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.min_hops_to_endpoint = dict()  # Minimum hops to each endpoint
        self.my_addresses = h.get_addresses()
        self.sock.bind(('', server_port))  # potentially problematic
        print(f'my addresses are {self.my_addresses}')
        self.ack_table = dict()  # stores which routers it is waiting on acks from

    def begin(self):
        t1 = threading.Thread(target=self.listen)
        #t2 = threading.Thread(target=self.send_until_ack)

        t1.start()

        t1.join()

    def listen(self):
        while True:
            incoming_msg, address = self.sock.recvfrom(buffer_size)
            address = address[0]
            header = incoming_msg[:12]
            bools, no_hops, packet_id, src_addr, dest_addr = h.unpack_header(header)
            no_hops_int = int.from_bytes(no_hops, byteorder='little')
            ack = h.check_nth_bit(bools, 7)  # double check
            is_broadcast = h.check_nth_bit(bools, 6)
            forget_request = h.check_nth_bit(bools, 5)

            if forget_request and packet_id not in self.seen_packets:
                if src_addr in self.forward_table:
                    del self.forward_table[src_addr]
                    print(f'Received forgetMe request from {src_addr}!')
                    print(f'My routing table is now {self.forward_table} after removing {src_addr}')
                self.broadcast(incoming_msg)

            elif ack:
                self.ack_table[address] = True
                print(f'Ack from {address} received!')

            elif address not in self.my_addresses and not ack and not forget_request:

                if is_broadcast and packet_id not in self.seen_packets:
                    if src_addr not in self.min_hops_to_endpoint or no_hops_int < self.min_hops_to_endpoint[src_addr]:
                        print(f'Received WhoIs request for {dest_addr} from {address}, appending {src_addr} to my list as well on addr {address}')
                        self.min_hops_to_endpoint[src_addr] = no_hops_int
                        self.forward_table[src_addr] = address
                        print(f'My routing table is {self.forward_table} after adding {src_addr}')

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
                        self.sock.sendto(incoming_msg, (self.forward_table[dest_addr], 50000))  # forward packet
                        no_hops_int = self.min_hops_to_endpoint[dest_addr]
                        no_hops_int += 1
                        no_hops = no_hops_int.to_bytes(1, byteorder='little')
                        message_to_send = b'\x00' + no_hops + incoming_msg[2:]
                        # This may be a source of error, either way this is a poor design choice
                        # send until ack recd
                        if address not in self.my_addresses and address[:3] != '192':  # if its not an endpoint

                            self.ack_table[address] = False
                            t2 = threading.Thread(target=self.send_until_ack, args=(message_to_send, address))
                            t2.start()
                            #t2.join()
                            print(f'Continuously sending packet to {address} until an ack is received!')

                elif not is_broadcast:
                    # send ack
                    message_to_send = b'\x80' + no_hops + incoming_msg[2:12] + 'This packet is an ack'.encode()
                    self.sock.sendto(message_to_send, (address, 50000))
                    if dest_addr not in self.forward_table or src_addr not in self.min_hops_to_endpoint or no_hops_int < self.min_hops_to_endpoint[src_addr]:
                        print(f'Received a response to my previous request for {dest_addr} from address {address}')

                        self.forward_table[dest_addr] = address
                        print(f'My routing table is {self.forward_table} after adding {dest_addr}')
                        self.min_hops_to_endpoint[dest_addr] = no_hops_int
                        no_hops_int += 1
                        no_hops = no_hops_int.to_bytes(1, byteorder='little')
                        message_to_send = b'\x00' + no_hops + incoming_msg[2:]
                        for net in self.outstanding_requests[dest_addr]:
                            self.sock.sendto(message_to_send, (net, 50000))
                    else:
                        print(f'Sending ack to {address}!')
                        #send ack
                        message_to_send = b'\x80' + no_hops + incoming_msg[2:12] + 'This packet is an ack'.encode()
                        self.sock.sendto(message_to_send, (address, 50000))

                        print(f'Received a regular packet, forwarding!')
                        self.sock.sendto(incoming_msg, (self.forward_table[dest_addr], 50000))
            self.seen_packets.append(packet_id)

    def broadcast(self, packet):
        for addr in self.adjacent_networks:
            self.sock.sendto(packet, (h.addr_to_broadcast_addr(addr), 50000))

    def send_until_ack(self, packet, address):
        while not self.ack_table[address]:
            print(f'Sent {address} a packet, still waiting for ack!')
            self.sock.sendto(packet, (address, 50000))
            sleep(2)
        self.ack_table[address] = False  # Reset ack for future use


def main():
    router = Router()
    router.begin()


if __name__ == "__main__":
    main()






