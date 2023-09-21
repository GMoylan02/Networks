import socket
import time
localIP = "Producer"

localPort = 50000
bufferSize = 1024
video_path = '\..\First20Frames'


# TODO allow for 1 producer to have multiple streams
class Producer:
    def __init__(self, producer_id: bytes):
        self.id = producer_id
        self.no_streams = 0
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPsocket.bind((localIP, localPort))

    # TODO Include functionality for the producer to wait for subscriptions before continuing
    def notify_broker(self, stream_no):
        msg = str.encode(f"Announcing the topic contained in this header!")
        header = self.id + stream_no.to_bytes(1, 'big') + 0x0000.to_bytes(2, 'big')
        self.UDPsocket.sendto(header + msg, ("Broker", 50000))

    # Publishes the videos as packets to the broker
    # Assumes the frames follow the file naming convention of "frame001.png" and so on
    # TODO implement functionality to send audio as well
    def publish(self, stream_no):
        bytes_to_send = bytearray()
        for i in range(1, 21):
            bytes_to_send.extend(png_to_bytearray(f"{video_path}\frame{i:03d}.png"))
            header = self.id + stream_no + i.to_bytes(1, 'big') + 0x01  # See txt file for byte break down
            self.UDPsocket.sendto(header + bytes_to_send[i-1], ("Broker", 50000))

# Increment the number of streams, notify the broker, give ample time for consumers to sub, and then publish frames
    def new_stream(self):
        self.no_streams += 1
        self.notify_broker(self.no_streams)
        time.sleep(1)
        self.publish(self.no_streams)


# Given the filepath, converts a png file to a bytearray
def png_to_bytearray(filepath: str):
    with open(filepath, "rb") as img:
        return bytearray(img.read())
