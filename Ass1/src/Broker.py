import socket
from main import consumer_list

localIP = "Broker"

localPort = 50000
bufferSize = 1024

UDPBrokerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPBrokerSocket.bind((localIP, localPort))
print("Broker up and listening")
# TODO figure out how to have it listen for both producers and consumers
while (True):
    incoming_msg = UDPBrokerSocket.recvfrom(bufferSize)
    isAnnouncement = incoming_msg[5:5] == 0x00  # this should get the 5th byte??
    if isAnnouncement:
        for i in range(len(consumer_list)):
            UDPBrokerSocket.sendto(incoming_msg, (consumer_list[i].name, 50000))  # Forwards announcement to all consumers
    else:


