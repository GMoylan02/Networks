import socket

localIP = "Broker"

localPort = 50000
bufferSize = 1024

UDPBrokerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPBrokerSocket.bind((localIP, localPort))
print("Broker up and listening")
# TODO Extend this to handle incoming message from both producers and consumers
while True:
    incoming_msg = UDPBrokerSocket.recvfrom(bufferSize)
    isAnnouncement = incoming_msg[5:5] == 0x00  # this should get the 5th byte??
    if isAnnouncement:
        # Reply to producer for demonstration purposes
        # TODO fix it never gets here
        UDPBrokerSocket.sendto(str.encode("Announcement received!"), (f'Producer', 50000))
        print("Announcement received!")
        #for i in range(len(consumer_list)):
            # Forwards announcement to all consumers
            #UDPBrokerSocket.sendto(incoming_msg, (consumer_list[i].name, 50000))
    else:
        UDPBrokerSocket.sendto(str.encode(f"Frame{incoming_msg[4:4]} received!"), (f'Producer', 50000))
        print("Frame received!")


