import random
import string
import struct
import socket
import sys
import json
import logging
import threading
from threading import Event, Thread
from util import *

class Server:

    def __init__(self, server_addr, server_port):
        self.server_addr = server_addr
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((server_addr, server_port))
        self.socket.listen(1)
        self.lock = threading.Lock()
        self.threads = {}
        self.clients = {}

    def action(self):
        while True:
            try:
                conn, cli_pub_addr = self.socket.accept()
                thread = threading.Thread(target=self.client_handler, args=(conn, cli_pub_addr))
                thread.start()
                self.threads[cli_pub_addr] = thread
            except socket.timeout:
                continue

    def client_handler(self, conn, client_public_addr):
        msg = recv_msg(conn)
        client_id, client_private_addr = msg_to_payload_addrs(msg)

        send_msg(conn, addr_to_msg(client_public_addr))
        msg = recv_msg(conn)
        client_peer_ids, cli_pub_addr = msg_to_payload_addrs(msg)
        client_peer_ids = json.loads(client_peer_ids)
        if cli_pub_addr != client_public_addr:
            conn.close()
            print('client reply did not match')
            exit()

        print(f'new client {client_id}: private address {client_private_addr[0]}:{client_private_addr[1]}, public address {client_public_addr[0]}:{client_public_addr[1]}')

        for peer_id in client_peer_ids:
            pair0 = f'{client_id}-{peer_id}'
            pair1 = f'{peer_id}-{client_id}'
            with self.lock:
                if pair0 not in self.clients:
                    print(f'({pair0}) does not exist, add ({pair1})')
                    self.clients[pair1] = [
                        conn,
                        client_private_addr,
                        client_public_addr]
                    continue
                else:
                    print(f'({pair0}) exist, pair them')
                    peer_conn, peer_pri_addr, peer_pub_addr = self.clients[pair0]
                    send_msg(peer_conn, payload_addrs_to_msg(str(client_id),
                                                             client_private_addr,
                                                             client_public_addr))
                    send_msg(conn, payload_addrs_to_msg(str(peer_id),
                                                        peer_pri_addr,
                                                        peer_pub_addr))
                    self.clients.pop(pair0)
                    if len(self.clients) == 0:
                        print('all connections are paired')


if __name__ == '__main__':
    server = Server(*addr_from_args(sys.argv))
    server.action()
