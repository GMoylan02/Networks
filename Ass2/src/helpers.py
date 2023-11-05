from subprocess import Popen, PIPE, call
def unpack_header(header):
    bools = header[:1]
    src_addr = header[1:5]
    dest_addr = header[5:]
    return bools, src_addr, dest_addr


def unpack_bools(bools):
    return False


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



