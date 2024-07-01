from logging import getLogger
from random import choice

from config import cur_process
from confirmer import AccountableConfirmer

logger = getLogger(__name__)

confirmer = AccountableConfirmer()

def on_confirm(_, confirmed):
    logger.info(f'Confirmer confirmed {confirmed}')

def on_detect(_, processes, proof):
    logger.info(f'Confirmer detected {processes} with {proof}')

confirmer.on('confirm', on_confirm)
confirmer.on('detect',  on_detect)

if choice([ True, False ]):
    value = 9876
    logger.info(f'Submitting value {value} to confirmer')
    confirmer.trigger('submit', value)
else:
    value = 1234
    logger.info(f'Submitting value {value} to confirmer')
    confirmer.trigger('submit', value)
