import struct
from collections import namedtuple


def addr_from_args(args, host='127.0.0.1', port=9999):
    if len(args) >= 3:
        host, port = args[1], int(args[2])
    elif len(args) == 2:
        host, port = host, int(args[1])
    else:
        host, port = host, port
    return host, port


def msg_to_addr(data):
    ip, port = data.decode('utf-8').strip().split(':')
    return (ip, int(port))


def msg_to_addrs(msg):
    ret = []
    data = msg.decode('utf-8').strip().split(':')
    while len(data) > 0:
        ret.append((data[0], int(data[1])))
        data = data[2:]
    return ret


def msg_to_payload_addrs(msg):
    data = msg.decode('utf-8').strip().split(':')
    ret = [data[0]]
    data = data[1:]
    while len(data) > 0:
        ret.append((data[0], int(data[1])))
        data = data[2:]
    return ret


def addr_to_msg(addr):
    return '{}:{}'.format(addr[0], addr[1]).encode('utf-8')


def addrs_to_msg(*addrs):
    msg = ''
    for addr in addrs:
        msg += f'{addr[0]}:{addr[1]}:'
    return msg[:-1].encode('utf-8')


def payload_addrs_to_msg(payload, *addrs):
    msg = payload
    for addr in addrs:
        msg += f':{addr[0]}:{addr[1]}'
    return msg.encode('utf-8')


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


class Client(namedtuple('Client', 'conn, pub, priv')):

    def peer_msg(self):
        return addr_to_msg(self.pub) + b'|' + addr_to_msg(self.priv)
