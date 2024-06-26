#!/usr/bin/env python3
from logging import basicConfig, getLogger
from signal import signal, SIGINT, SIGTERM
from threading import Event

from config import cur_process, log_level
from network import net_start, net_stop

basicConfig(format='%(asctime)s: %(levelname)s: %(name)s: %(message)s', level=log_level)

logger = getLogger(__name__)
exit = Event()

def signal_handler(sig, frame):
    exit.set()

signal(SIGINT,  signal_handler)
signal(SIGTERM, signal_handler)

logger.info(f'Process started, process id: {cur_process}')

net_start()

import test_confirmer
exit.wait()

net_stop()
