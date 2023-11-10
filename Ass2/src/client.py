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
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.routing_table = dict()
        self.seen_packets = []

    def begin(self):
        t1 = threading.Thread(target=self.handle_user_input)
        t2 = threading.Thread(target=self.listen)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    def handle_user_input(self):
        #while True:
            #message = input(f'Please type the message you would like to send!').encode()
            #dest_addr = int(input('Enter the desired destination address: '), 16).to_bytes(4, byteorder='big')
        dest_addr = self.address[::-1]
        message = "Hello, World!".encode()
        self.broadcast(message, dest_addr)

    def broadcast(self, message, dest_addr):
        if dest_addr not in self.routing_table:
            packet_id = random.randbytes(2)
            header = b'\x40\x01' + packet_id + self.address + dest_addr
            self.seen_packets.append(packet_id)
            for addr in self.adjacent_networks:
                self.sock.sendto(header + message, (h.addr_to_broadcast_addr(addr), 50000))
                print("Broadcasting!")

        else:
            print(f'Sending packets directly!')
            header = b'\x40\x00' + random.randbytes(2) + self.address + dest_addr
            self.sock.sendto(header + message, (self.routing_table[dest_addr], 50000))

    def listen(self):
        while True:
            incoming_msg, address = self.sock.recvfrom(buffer_size)
            address = address[0]
            bools, no_hops, packet_id, src_addr, dest_addr = h.unpack_header(incoming_msg)
            sender_can_reach_dest = h.check_nth_bit(bools, 7)  # double check
            is_broadcast = h.check_nth_bit(bools, 6)

            if not socket.gethostbyname(socket.gethostname()) == address:

                if is_broadcast and packet_id not in self.seen_packets:
                    print(f'Received request for my location from {address}, sending response!')
                    incoming_msg = b'\x80' + (int.from_bytes(no_hops, byteorder='little') + 1).to_bytes(1, byteorder='little') + incoming_msg[2:]
                    self.sock.sendto(incoming_msg, (address, server_port))
                elif dest_addr != self.address:
                    print(f'Received information that {dest_addr} can be reached by {address}!')
                    self.routing_table[dest_addr] = address
                print(f"Received packet from {src_addr} with the message {incoming_msg} at {datetime.now().strftime('%H:%M:%S')}!")
            self.seen_packets.append(packet_id)



def main(argv):
    addr = h.string_to_hex(argv[1])
    client = Client(argv[0], addr)
    client.begin()


if __name__ == "__main__":
    main(sys.argv[1:])
