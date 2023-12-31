import socket
import time
import threading
import netifaces as ni
import os

"""
 Name: Gerard Moylan
 Student ID: 21364007
"""

localIP = "Producer"

localPort = 50000
bufferSize = 1024
video_path = '/FrameSamples'
audio_path = 'AudioSample.m4v'


class Producer:
    """
    How to use the Producer:

    Simply instantiate a producer and call the produce method
    producer1 = Producer(YOUR_ID)
    producer1.produce()

    Don't call any of the private methods as those are meant to be used internally
    """
    def __init__(self, producer_id: bytes):
        self.producer_id = producer_id
        self.name = 'Producer'
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        ip = ni.ifaddresses('eth1')[ni.AF_INET][0]['addr']  # Getting eth1 ip as opposed to eth0
        self.UDPsocket.bind((ip, 50000))
        self.ping_received = False
        self.stream_ids = []

    def produce(self):
        t1 = threading.Thread(target=self.__new_stream)
        t2 = threading.Thread(target=self.__ping, args=(2,))
        t3 = threading.Thread(target=self.__listen_for_updates)

        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()

    def __new_stream(self):
        while True:
            print(f"Producer id {self.producer_id} started a new stream!")
            stream_no = self.__find_unused_stream_id()

            choice = input('Type "notify" to notify possible consumers of your stream!!')
            while choice.lower() != 'notify':
                choice = input('Type "notify" to notify possible consumers of your stream!!')
            self.__notify_broker(stream_no)

            choice = input('Type "publish" to publish the stream!')
            while choice.lower() != 'publish':
                choice = input('Type "publish" to publish the stream!')
            self.__publish(stream_no)

            choice = input('Type "restart" to start a new stream!')
            while choice.lower() != 'restart':
                input('Type "restart" to start a new stream!')

    def __ping(self, interval):
        while not self.ping_received:
            # sender_id:3 - stream no:1 - frame_no:2 - is_announce:1 - ping_recd:1 - is_ping:1 - is_subscription:1 - audio_no:2
            header = self.producer_id + b'\x00\x00\x00\x00\x00\x01\x00\x00\x00'
            print("Pinged Broker!")
            self.UDPsocket.sendto(header, ("Broker", 50000))
            time.sleep(interval)

    def __listen_for_updates(self):
        while True:
            pair = self.UDPsocket.recvfrom(bufferSize)
            incoming_msg = pair[0]
            stream_no = incoming_msg[3:4]
            ping_recd = incoming_msg[7:8] == b'\x01'

            if stream_no != b'\x00' and not int.from_bytes(stream_no, signed=False, byteorder='little') in self.stream_ids:
                # Must be stream id update
                self.stream_ids.append(int.from_bytes(stream_no, signed=False, byteorder='little'))
            elif ping_recd:
                # Must be a ping received
                self.ping_received = True

    def __notify_broker(self, stream_no):
        print(f'Producer {self.producer_id} is announcing stream no {stream_no}!')
        msg = str.encode(f"Announcing the topic contained in this header!")
        # sender_id:3 - stream no:1 - frame_no:2 - is_announce:1 - ping_recd:1 - is_ping:1 - is_subscription:1 - audio_no:2
        header = self.producer_id + stream_no.to_bytes(1, 'little') + b'\x00\x00\x01\x00\x00\x00\x00\x00'
        self.UDPsocket.sendto(header + msg, ("Broker", 50000))

    # Publishes the videos as packets to the broker
    def __publish(self, stream_no):
        print(f'Producer {self.producer_id} started publishing stream no {stream_no}!')
        frames = os.listdir(video_path)
        no_frames = (len(frames))
        frames.sort()
        audio_list = m4v_to_bytes(audio_path, no_frames)  # List of bytes
        for i, frame in enumerate(frames):
            # sender_id:3 - stream no:1 - frame_no:2 - is_announce:1 - ping_recd:1 - is_ping:1 - is_subscription:1 - audio_no 2
            header = self.producer_id + stream_no.to_bytes(1, 'little', signed=False) + i.to_bytes(2, 'little', signed=False) + b'\x00\x00\x00\x00\x00\x00'
            self.UDPsocket.sendto(header + bytes(png_to_bytearray(video_path + '/' + frame)), ("Broker", 50000))
            # Audio:
            header = self.producer_id + stream_no.to_bytes(1, 'little', signed=False) + b'\x00\x00\x00\x00\x00\x00' + i.to_bytes(2, 'little', signed=False)
            self.UDPsocket.sendto(header + audio_list[i], ("Broker", 50000))


    def __find_unused_stream_id(self):
        if len(self.stream_ids) == 0:
            return 1
        else:
            self.stream_ids.sort()
            return self.stream_ids[-1]+1


# Given the filepath, converts a png file to a bytearray
def png_to_bytearray(filepath: str):
    with open(filepath, "rb") as img:
        t = bytearray(img.read())
        return t


    # Turn m4v into n segments
def m4v_to_bytes(filepath: str, n):
    with open(filepath, 'rb') as audio:
        t = audio.read()
    bytes_length = len(t)
    ret = []
    diff = 0
    if bytes_length % n != 0:
        segment_length = 1 + int((bytes_length / n))
        diff = (n * segment_length) - bytes_length
    else:
        segment_length = int(bytes_length / n)

    for i in range(n-1):
        ret.append(t[segment_length*n:segment_length*(n+1)])
    ret.append(t[-diff:])

    return ret

