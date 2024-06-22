import logging

from random import randint
from time import sleep

from config import log_level
from consensus import FloodingConsensus
from network import net_start, net_stop

def on_decision(_, decision):
    logger.info(f'Consensus decided {decision}')

logger = logging.getLogger(__name__)

net_start()

consensus = FloodingConsensus()

sleep(1)

value = randint(10000, 99999)
consensus.on('decide', on_decision)
consensus.trigger('propose', value)

# while True:
#     sleep(1)
#
# net_stop()
