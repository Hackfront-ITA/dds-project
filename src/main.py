#!/usr/bin/env python3
import logging

from config import cur_process, log_level
from network import net_start, net_stop
from signal import signal, SIGINT
from threading import Event

exit = Event()

def signal_handler(sig, frame):
    if sig != SIGINT:
        return

    exit.set()

signal(SIGINT, signal_handler)

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(name)s: %(message)s', level=log_level)
logger = logging.getLogger(__name__)
logger.info(f'Process started, process id: {cur_process}')

net_start()

import test_confirmer

while not exit.wait(10):
    pass

net_stop()
