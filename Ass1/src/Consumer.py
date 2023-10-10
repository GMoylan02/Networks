import socket
import threading
import time

bufferSize = 1024


def main():
    consumer1 = Consumer(b'\xCC\xBB\xAA')
    consumer1.listen()


if __name__ == '__main__':
    main()


class Consumer:
    def __init__(self, consumer_id):
        self.consumer_id = consumer_id
        self.name = f'Consumer{consumer_id}'
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPsocket.bind((self.name, 50000))

    def consume(self):
        t1 = threading.Thread(target=self.__listen, args=())
        t2 = threading.Thread(target=self.__ping, args=(0.5,))

        t1.start()
        t2.start()

        t1.join()
        t2.join()


    def __subscribe(self, stream_no, producer_id):
        header = self.consumer_id + stream_no + producer_id
        self.UDPsocket.sendto(header, ("Broker", 50000))

    # Periodically pings the broker
    def __ping(self, interval):
        while True:
            time.sleep(interval)
            header = self.consumer_id + b'\x00' + b'\x00\x00\x00'
            self.UDPsocket.sendto(header, ("Broker", 50000))


    def __listen(self):
        while True:
            incoming_msg = self.UDPsocket.recvfrom(bufferSize)
            producer_id = incoming_msg[0:3]
            stream_no = incoming_msg[4:4]
            is_announcement = incoming_msg[5:5] == 0x00
            if is_announcement and stream_no % self.consumer_id == 0: # Just arbritrary, consumer m subs to producer n if m is a multiple of n
                self.__subscribe(stream_no, producer_id)
            else:
                print("Received a frame!")




