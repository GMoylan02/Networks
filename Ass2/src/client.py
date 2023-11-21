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
        while True:
            message = input(f'Please type the message you would like to send!').encode()
            dest_addr = int(input('Enter the desired destination address: '), 16).to_bytes(4, byteorder='big')
            self.broadcast(message, dest_addr)
            sleep(1)
            if input(f'Would you like to broadcast to all routers telling them to remove you from their routing tables?'
                     f' (Yes/No)').lower() == 'yes':
                header = b'\x60\x00' + random.randbytes(2) + self.address + self.address
                message = 'This packet is a forgetMe request'.encode()
                for addr in self.adjacent_networks:
                    self.sock.sendto(header + message, (h.addr_to_broadcast_addr(addr), 50000))

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
            header = b'\x00\x00' + random.randbytes(2) + self.address + dest_addr
            self.sock.sendto(header + message, (self.routing_table[dest_addr], 50000))

    def listen(self):
        while True:
            incoming_msg, address = self.sock.recvfrom(buffer_size)
            address = address[0]
            bools, no_hops, packet_id, src_addr, dest_addr = h.unpack_header(incoming_msg)
            ack = h.check_nth_bit(bools, 7)  # double check
            is_broadcast = h.check_nth_bit(bools, 6)
            forget_me = h.check_nth_bit(bools, 5)


            if not socket.gethostbyname(socket.gethostname()) == address and not ack and not forget_me:

                if is_broadcast and packet_id not in self.seen_packets and dest_addr == self.address:
                    print(f'Received request for my location from {address}, sending response!')
                    incoming_msg = b'\x00' + (int.from_bytes(no_hops, byteorder='little') + 1).to_bytes(1, byteorder='little') + incoming_msg[2:]
                    self.sock.sendto(incoming_msg, (address, server_port))
                elif dest_addr != self.address and not is_broadcast:
                    print(f'Received information that {dest_addr} can be reached by {address}!')
                    self.routing_table[dest_addr] = address
                    # send ack
                    message_to_send = b'\x80' + incoming_msg[1:]
                    print(f'Sending ack to {address}')
                    self.sock.sendto(message_to_send, (address, 50000))
                print(f"Received packet from {src_addr} with the message {incoming_msg}!")
            self.seen_packets.append(packet_id)

    def get_destination(self):
        destinations = [b'\xaa\xaa\xaa\xaa', b'\xbb\xbb\xbb\xbb', b'\xcc\xcc\xcc\xcc', b'\xdd\xdd\xdd\xdd']
        destinations.remove(self.address)
        return destinations[random.randint(0, 2)]

    def send_removal_request(self):
        header = b'\x60\x00' + random.randbytes(2) + self.address + self.address
        for net in self.adjacent_networks:
            self.sock.sendto(header, (h.addr_to_broadcast_addr(net), 50000))


def main(argv):
    addr = h.string_to_hex(argv[1])
    client = Client(argv[0], addr)
    client.begin()


if __name__ == "__main__":
    main(sys.argv[1:])
