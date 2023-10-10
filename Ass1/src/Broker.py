import socket

localIP = "Broker"

localPort = 50000
bufferSize = 1024

UDPBrokerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPBrokerSocket.bind((localIP, localPort))
print("Broker up and listening")
# TODO Extend this to handle incoming message from both producers and consumers
# Subscribed is a dict matching consumers to stream numbers, assumes consumers sub to only 1 stream
subscribed = dict()

def from_producer(incoming_msg):
    return incoming_msg[0:1] == b'\xAA'


while True:
    incoming_msg = UDPBrokerSocket.recvfrom(bufferSize)[0]
    address = UDPBrokerSocket.recvfrom(bufferSize)[1]
    isAnnouncement = incoming_msg[5:6] == b'\x00'
    stream_no = incoming_msg[3:4]   # Stream number will always be byte 4
    if isAnnouncement:
        pass
        #for i in range(len(consumer_list)):
            # Forwards announcement to all consumers
            #UDPBrokerSocket.sendto(incoming_msg, (consumer_list[i].name, 50000))
    elif from_producer(incoming_msg):
        UDPBrokerSocket.sendto(str.encode(f"Frame{incoming_msg[4:4]} received!"), address)
        print("Frame received!")
    else:
        subscribed[incoming_msg[0:3]] = stream_no

