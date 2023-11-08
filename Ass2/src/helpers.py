from subprocess import Popen, PIPE, call
def unpack_header(header):
    bools = header[:1]
    packet_id = header[1:3]
    src_addr = header[3:7]
    dest_addr = header[7:]
    return bools, packet_id, src_addr, dest_addr


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


