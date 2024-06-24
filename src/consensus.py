from logging import getLogger

from event_emitter import EventEmitter
from network import BestEffortBroadcast

from config import network, num_hosts, processes

CLASS_ID = 'fl-cs'

ALLOWED_PACKETS = [
    'proposal',
    'decided',
]

instances = {}
correct = set(processes)

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

        self.receivedfrom = [ None ] * num_hosts
        for i in range(0, num_hosts):
            self.receivedfrom[i] = set()
        self.receivedfrom[0] = set(processes)

        self.proposals = [ None ] * num_hosts
        for i in range(0, num_hosts):
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
    c.proposals[r] = c.proposals[r].union(ps)

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


def c_choose(proposals):
    logger.debug(f'Deciding from {proposals}')

    return min(proposals)

def on_receive(_, source, payload):
    if payload[0] not in instances:
        return

    instance = instances[payload[0]]

    if payload[1] not in ALLOWED_PACKETS:
        return

    sender = source[0]
    type = payload[1].replace('-', '_')
    args = payload[2:]

    instance.trigger(f'm_{type}', sender, *args)

beb.on('receive', on_receive)
# pfd.on('crash', on_crash)
