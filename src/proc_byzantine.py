from logging import getLogger
from time import sleep

from config import cur_process, keys
from network import BestEffortBroadcast
from tss import tss_share_sign

logger = getLogger(__name__)
beb = BestEffortBroadcast

logger.info('Process is byzantine!')

recv_values = []

def on_receive(_, source, payload):
    if payload[1] != 'submit':
        return

    if payload[2] in recv_values:
        return

    recv_values.append(payload[2])

    raw = str(payload[2])
    share = tss_share_sign(raw, keys[cur_process][0])

    payload[3] = share

    raw = 'submit' + str(payload[2]) + share
    sig = tss_share_sign(raw, keys[cur_process][0])

    payload[4] = sig

    info = payload[:3]
    logger.debug(f'Replying packet: {info}')

    beb.trigger('send', payload)

beb.on('receive', on_receive)
