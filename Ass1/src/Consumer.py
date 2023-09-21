import socket
bufferSize = 1024
class Consumer:
    def __init__(self, id):
        self.id = id
        self.name = f'Consumer{id}'
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPsocket.bind((self.name, 50000))

    def subscribe(self, stream_no):
        header = self.id + stream_no
        subscribe = str.encode("subscribe")
        self.UDPsocket.sendto(header + subscribe, ("Broker", 50000))

    def listen(self):
        while True:
            incoming_msg = self.UDPsocket.recvfrom(bufferSize)
            is_announcement = incoming_msg[5:5] == 0x00
            stream_no = incoming_msg[0]
            if is_announcement and stream_no % self.number == 0: # Just arbritrary, consumer m subs to producer n if m is a multiple of n
                self.subscribe(incoming_msg)
            else:
                print("Received a frame!")


