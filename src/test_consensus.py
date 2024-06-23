from logging import getLogger
from random import randint
from time import sleep

from consensus import FloodingConsensus

logger = getLogger(__name__)
consensus = FloodingConsensus()

def on_decision(_, decision):
    logger.info(f'Consensus decided {decision}')

consensus.on('decide', on_decision)

sleep(1)

value = randint(10000, 99999)
consensus.trigger('propose', value)
