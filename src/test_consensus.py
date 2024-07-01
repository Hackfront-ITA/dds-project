from logging import getLogger
from random import randint
from time import sleep

from dds_abc import ABC
from config import t0_ac
from consensus import FloodingConsensus

logger = getLogger(__name__)
consensus = ABC(t0_ac)

def on_decision(_, decision):
	logger.info(f'Consensus decided {decision}')

consensus.on('decide', on_decision)

def on_detect(_, processes, proof):
	logger.info(f'ABC detected {processes} with {proof}')

consensus.on('detect', on_detect)

sleep(1)

value = randint(10000, 99999)
consensus.trigger('propose', value)
