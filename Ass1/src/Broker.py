import socket

localIP = "Broker"

localPort = 50000
bufferSize = 1024

UDPBrokerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPBrokerSocket.bind((localIP, localPort))
print("Broker up and listening")
# Subscribed is a dict matching consumers to stream numbers, assumes consumers sub to only 1 stream
subscribed = dict()


def from_producer(incoming):
    return incoming[0:1] == b'\xAA'


while True:
    incoming_msg = UDPBrokerSocket.recvfrom(bufferSize)[0]
    address = UDPBrokerSocket.recvfrom(bufferSize)[1]
    isAnnouncement = incoming_msg[5:6] == b'\x00'
    is_ping = incoming_msg[4:7] == b'\x00\x00\x00\x00'
    incoming_id = incoming_msg[0:3]
    stream_no = incoming_msg[3:4]   # Stream number will always be byte 4
    frame_no = incoming_msg[4:5]
    consumer_address_list = []

    if isAnnouncement:
        print(f"Received announcement from {address}!")
        for consumer_address in consumer_address_list:  # Forward announcement
            UDPBrokerSocket.sendto(incoming_msg, (consumer_address, 50000))
    elif from_producer(incoming_id):    # Forward frames to subscribed consumers
        print(f"Forwarding frames from stream {stream_no} to all subscribers!")
        for address in subscribed:
            if subscribed[address] == stream_no:
                UDPBrokerSocket.sendto(incoming_msg, (address, 50000))
    elif is_ping and address not in consumer_address_list:    #
        print(f"Ping from {address} received!")
        consumer_address_list.append(address)
    else:
        print(f"{address} just subscribed to stream number {stream_no}!")
        subscribed[address] = stream_no
