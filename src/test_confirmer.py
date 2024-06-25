from logging import getLogger
from random import randint
from time import sleep

from confirmer import AccountableConfirmer
# from main import exit

logger = getLogger(__name__)
confirmer = AccountableConfirmer()

def on_confirm(_, confirmed):
    logger.info(f'Confirmer confirmed {confirmed}')

def on_detect(_, processes, proof):
    logger.info(f'Confirmer detected {processes} with {proof}')

confirmer.on('confirm', on_confirm)
confirmer.on('detect', on_detect)

sleep(1)

value = 123456
confirmer.trigger('submit', value)
