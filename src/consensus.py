from logging import getLogger
from secrets import token_hex

from event_emitter import EventEmitter
from network import BestEffortBroadcast

PROCESSES = set([
    '10.173.2.1',
    '10.173.2.4'
])
K_N = len(PROCESSES)
CLASS_ID = '0c84640d'

ALLOWED_PACKETS = [
    'proposal',
    'decided',
]

instances = {}
correct = set(PROCESSES)

logger = getLogger(__name__)

beb = BestEffortBroadcast
# pfd = PerfectFailureDetector

class FloodingConsensus(EventEmitter):
    def __init__(self):
        super().__init__()

        self.id = CLASS_ID
        instances[self.id] = self

        self.round = 1
        self.decision = None

        self.receivedfrom = [ None ] * K_N
        for i in range(0, K_N):
            self.receivedfrom[i] = set()
        self.receivedfrom[0] = set(PROCESSES)

        self.proposals = [ None ] * K_N
        for i in range(0, K_N):
            self.proposals[i] = set()

        self.on('propose', on_propose)

        self.on('m_proposal', on_proposal)
        self.on('e_correct_in_receivedfrom', on_correct_in_receivedfrom)
        self.on('m_decided', on_decided)

def on_crash(_, p):
    global correct

    correct.remove(p)

def on_propose(c, v):
    logger.debug(f'[{c.id}] Proposing value {v}')

    c.proposals[1].add(v)
    proposals = list(c.proposals[1])
    beb.trigger('send', [ c.id, 'proposal', 1, proposals])

def on_proposal(c, p, r, ps):
    global correct

    logger.debug(f'[{c.id}] Received proposals from {p} round {r}: {ps}')

    c.receivedfrom[r].add(p)
    c.proposals[r].union(ps)

    if correct <= c.receivedfrom[c.round] and c.decision == None:
        c.trigger('e_correct_in_receivedfrom')

def on_correct_in_receivedfrom(c):
    logger.debug(f'[{c.id}] All correct processes participated in round {c.round}')

    if c.receivedfrom[c.round] == c.receivedfrom[c.round - 1]:
        c.decision = c_choose(c.proposals[c.round])

        logger.debug(f'[{c.id}] Decision made: {c.decision}')

        beb.trigger('send', [ c.id, 'decided', c.decision ])
        c.trigger('decide', c.decision)
    else:
        c.round += 1

        proposals = c.proposals[c.round - 1]
        logger.debug(f'[{id}] Requesting new round {c.round}, proposals {proposals}')

        beb.trigger('send', [ id, 'proposal', c.round, proposals])

def on_decided(c, p, v):
    global correct

    if not (p in correct and c.decision == None):
        return

    c.decision = v

    logger.debug(f'[{c.id}] Decision received: {c.decision}')

    beb.trigger('send', [ c.id, 'decided', c.decision ])
    c.trigger('decide', c.decision)


def on_receive(_, source, payload):
    if payload[0] not in instances:
        return

    instance = instances[payload[0]]

    if payload[1] not in ALLOWED_PACKETS:
        return

    sender = source[0]
    args = payload[2:]

    instance.trigger(f'm_{payload[1]}', sender, *args)

beb.on('receive', on_receive)
# pfd.on('crash', on_crash)
