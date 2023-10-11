import socket

localIP = "Broker"

localPort = 50000
bufferSize = 1024

UDPBrokerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPBrokerSocket.bind((localIP, localPort))
print("Broker up and listening")
# Subscribed is a dict matching consumers to stream numbers, assumes consumers sub to only 1 stream
subscribed = dict()
stream_ids = []
consumer_address_list = []
producer_address_list = []


def from_producer(incoming):
    return incoming[0:1] == b'\xAA'


while True:
    pair = UDPBrokerSocket.recvfrom(bufferSize)
    incoming_msg = pair[0]
    address = pair[1]

    # sender_id:3 - stream no:1 - frame_no:1 - is_announce:1 - ping_recd:1 - is_ping:1 - is_subscription:1
    sender_id = incoming_msg[0:3]
    stream_no = incoming_msg[3:4]
    frame_no = incoming_msg[4:5]
    is_announcement = incoming_msg[5:6] == b'\x01'
    ping_recd = incoming_msg[6:7] == b'\x01'
    is_ping = incoming_msg[7:8] == b'\x01'
    is_subscription = incoming_msg[8:9]
    is_from_producer = from_producer(sender_id)

    stream_no_int = int.from_bytes(stream_no, signed=False, byteorder='little')

    if is_announcement:
        print(f"Received announcement from {address}!")
        for producer_address in producer_address_list:
            print('Informed a producer about an announcement!')
            header = b'\x00\x00\x00' + stream_no + b'\x00\x00\x00\x00\x00'
            UDPBrokerSocket.sendto(header, producer_address)
        for consumer_address in consumer_address_list:  # Forward announcement
            print('Forwarded announcement!')
            UDPBrokerSocket.sendto(incoming_msg, consumer_address)

    elif is_from_producer and frame_no != b'\x00':    # Forward frames to subscribed consumers
        print(f"Forwarding frames from stream {stream_no_int} to all subscribers!")
        for address in subscribed:
            if subscribed[address] == stream_no:
                UDPBrokerSocket.sendto(incoming_msg, address)

    elif is_ping and (address not in consumer_address_list or address not in producer_address_list):    #
        # sender_id:3 - stream no:1 - frame_no:1 - is_announce:1 - ping_recd:1 - is_ping:1 - is_subscription:1
        print(f"Ping from {address} received, telling id {sender_id} to stop!")
        UDPBrokerSocket.sendto(sender_id + b'\x00\x00\x00\x01\x00\x00', address)
        if is_from_producer:
            print('got a ping from producer')
            producer_address_list.append(address)
        else:
            consumer_address_list.append(address)

    elif is_subscription and stream_no != b'\x00':
        print(f"{address} just subscribed to stream number {stream_no_int}!")
        subscribed[address] = stream_no
