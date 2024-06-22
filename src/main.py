#!/usr/bin/env python3
import logging

from config import log_level

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(name)s: %(message)s', level=log_level)
logger = logging.getLogger(__name__)
logger.info(f'Process started')

import test_consensus
