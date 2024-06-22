import logging

from event_emitter import EventEmitter
from ipaddress import IPv4Address, IPv4Network
from json import dumps, loads
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from threading import Thread

BUF_SIZE = 128
NET_IPS = '10.173.0.0/16'
BC_PORT = 4678
bc_addr = str(IPv4Network(NET_IPS, False).broadcast_address)

def send_handler(_, data):
    payload = dumps(data).encode('ascii')

    sock.sendto(payload, (bc_addr, BC_PORT))

def recv_handler(_):
    global running, sock

    logger.debug('Started receiving thread')

    while running:
        msg = sock.recvfrom(BUF_SIZE)
        # logger.debug(f'Received message from {msg[1][0]}:{msg[1][1]}: {msg[0]}')

        payload = loads(msg[0])
        BestEffortBroadcast.trigger('receive', msg[1], payload)

logger = logging.getLogger(__name__)

sock = socket(AF_INET, SOCK_DGRAM)
sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
sock.bind((bc_addr, BC_PORT))

running = True
recv_thread = Thread(target=recv_handler, args=( None, ))


BestEffortBroadcast = EventEmitter()
BestEffortBroadcast.on('send', send_handler)

def net_start():
    global recv_thread, running

    recv_thread.start()

def net_stop():
    global recv_thread, running

    running = False
    recv_thread.join()
