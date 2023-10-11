import socket
import time

localIP = "Producer"

localPort = 50000
bufferSize = 1024
video_path = '/First20Frames'


class Producer:
    def __init__(self, producer_id: bytes):
        self.id = producer_id
        self.name = 'Producer'
        self.no_streams = 0
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        print(self.name)
        self.UDPsocket.bind(("Producer", localPort))

    def notify_broker(self, stream_no):
        print(f'Producer {self.id} is announcing stream no {stream_no}!')
        msg = str.encode(f"Announcing the topic contained in this header!")
        header = self.id + stream_no.to_bytes(1, 'big') + b'\x00\x00'
        print(header)
        self.UDPsocket.sendto(header + msg, ("Broker", 50000))

    # Publishes the videos as packets to the broker
    # Assumes the frames follow the file naming convention of "frame001.png" and so on
    # TODO implement functionality to send audio as well
    def publish(self, stream_no):
        print(f'Producer {self.id} started publishing stream no {stream_no}!')
        for i in range(1, 21):
            header = self.id + stream_no.to_bytes(1, 'big') + i.to_bytes(1, 'big') + b'\x01'
            self.UDPsocket.sendto(header + bytes(png_to_bytearray(f"{video_path}/frame{i:03d}.png")), ("Broker", 50000))

# Increment the number of streams, notify the broker, give ample time for consumers to sub, and then publish frames
    def new_stream(self):
        print(f"Producer id {self.id} started a stream!")
        # TODO figure out a mechanism where stream numbers dont overlap
        self.no_streams += 1
        self.notify_broker(self.no_streams)
        time.sleep(1)
        self.publish(self.no_streams)


# Given the filepath, converts a png file to a bytearray
def png_to_bytearray(filepath: str):
    with open(filepath, "rb") as img:
        t = bytearray(img.read())
        return t
