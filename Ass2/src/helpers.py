from subprocess import Popen, PIPE, call
import socket
import netifaces as ni
def unpack_header(header):
    bools = header[:1]
    no_hops = header[1:2]
    packet_id = header[2:4]
    src_addr = header[4:8]
    dest_addr = header[8:12]
    return bools, no_hops, packet_id, src_addr, dest_addr


def check_nth_bit(byte, n):
    return (int.from_bytes(byte, byteorder='little') >> n) & 1 == 1


def get_addresses():
    return [ni.ifaddresses('eth1')[ni.AF_INET][0]['addr'], ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']]


def unpack_bools(bools):
    pass


def string_to_hex(str):
    return bytes.fromhex(str)


def get_adjacent_networks():
    result = []
    p = Popen('route', shell=True, stdout=PIPE)
    while True:
        o = p.stdout.readline()
        if not o:
            break
        # while you encounter a number or .
        current = ''
        i = 0
        while o[i] == 46 or 48 <= o[i] <= 57:
            current += chr(o[i])
            i += 1
        if current != '':
            result.append(current)
    return result


# Takes an ip and replaces the last section with 255
def addr_to_broadcast_addr(ip):
    sections = ip.split(".")
    sections[-1] = '255'
    return '.'.join(str(x) for x in sections)


