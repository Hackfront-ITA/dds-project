from logging import getLogger
from time import sleep

from event_emitter import EventEmitter
from network import BestEffortBroadcast
from tss import tss_share_sign, tss_share_verify, tss_combine, tss_verify

from config import cur_process, keys, num_hosts, processes

CLASS_ID = 'ac-cf'

ALLOWED_PACKETS = [
    'submit',
    'light-certificate',
    'full-certificate',
]

instances = {}

max_failures = 4

logger = getLogger(__name__)
beb = BestEffortBroadcast

class AccountableConfirmer(EventEmitter):
    def __init__(self):
        super().__init__()

        self.id = CLASS_ID
        instances[self.id] = self

        self.value = None
        self.confirmed = False
        self.xfrom = []
        self.light_cert = []
        self.full_cert = []
        # self.obt_light_certs = []
        # self.obt_full_certs = []

        self.fc_sent = False
        self.detected = False

        self.lc_dict = {}
        self.fc_dict = {}

        for process in processes:
            self.lc_dict[process] = set()
            self.fc_dict[process] = set()

        self.on('submit', on_submit_l)

        self.on('m_submit', on_submit_r)
        self.on('e_from_over_th', on_from_over_th)
        self.on('m_light_certificate', on_light_certificate)
        self.on('m_full_certificate', on_full_certificate)

def on_submit_l(instance, value):
    logger.debug(f'[{instance.id}] Submitting value {value}')

    instance.value = value

    sleep(1)

    raw = str(value)
    share = tss_share_sign(raw, keys[cur_process][0])

    raw = 'submit' + str(value) + share
    sig = tss_share_sign(raw, keys[cur_process][0])

    beb.trigger('send', [ instance.id, 'submit', value, share, sig ])

def on_submit_r(instance, sender, value, share, sig):
    logger.debug(f'[{instance.id}] Received submission from {sender}, for {value}')

    raw = 'submit' + str(value) + share
    if not tss_share_verify(raw, keys[sender][1], sig):
        logger.warn(f'[{instance.id}] Invalid submit message signature, from {sender}')
        return

    if not tss_share_verify(str(value), keys[sender][1], share):
        logger.warn(f'[{instance.id}] Invalid submit share, from {sender}')
        return

    if value != instance.value:
        logger.warn(f'[{instance.id}] Invalid submit value, from {sender}')
        return

    if sender in instance.xfrom:
        logger.warn(f'[{instance.id}] Duplicate submit message, from {sender}')
        return

    instance.xfrom.append(sender)

    instance.light_cert.append(share)
    instance.full_cert.append((sender, 'submit', value, share, sig))

    if len(instance.xfrom) >= num_hosts - max_failures and not instance.confirmed:
        instance.trigger('e_from_over_th')

def on_from_over_th(instance):
    logger.debug(f'[{instance.id}] Receive threshold triggered')

    instance.confirmed = True
    instance.trigger('confirm', instance.value)

    combined = tss_combine(instance.light_cert)
    beb.trigger('send', [ instance.id, 'light-certificate', instance.value, combined, instance.xfrom ])

def on_light_certificate(instance, sender, value, light_cert, participants):
    logger.debug(f'[{instance.id}] Received light certificate from {sender}, for {value}, content: {light_cert[:16]}..., {participants}')

    pk = []
    for participant in participants:
        pk.append(keys[participant][1])

    if not tss_verify([ str(value) ] * len(participants), pk, light_cert):
        logger.warn(f'[{instance.id}] Invalid light cert signature, from {sender}')
        return

    # instance.obt_light_certs.append(('light-certificate', value, light_cert))

    for participant in participants:
        instance.lc_dict[participant].add(value)

        if len(instance.lc_dict[participant]) >= 2 and instance.confirmed and not instance.fc_sent:
            instance.fc_sent = True
            beb.trigger('send', [ instance.id, 'full-certificate', instance.value, instance.full_cert ])

def on_full_certificate(instance, sender, value, full_cert):
    logger.debug(f'[{instance.id}] Received full certificate from {sender}, for {value}, content: {full_cert}')

    if not full_cert_valid(full_cert, value):
        logger.warn(f'[{instance.id}] Invalid full cert received from {sender}')
        return

    # instance.obt_full_certs.append(full_cert)

    if instance.detected:
        return

    byzantines = []
    proof = []

    for message in full_cert:
        message = tuple(message)
        process = message[0]

        messages = instance.fc_dict[process]
        messages.add(message)

        assert(len(messages) <= 2)

        if len(messages) == 2:
            byzantines.append(process)
            proof.append(tuple(messages))

    if len(byzantines) == 0:
        return

    instance.detected = True
    instance.trigger('detect', byzantines, proof)

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

def full_cert_valid(full_cert, val):
    for entry in full_cert:
        sender, _, value, share, sig = entry

        raw = 'submit' + str(value) + share
        if not tss_share_verify(raw, keys[sender][1], sig):
            logger.warn(f'[{instance.id}] Invalid signature in FC from {sender} about {value}')
            return False

        if not tss_share_verify(str(value), keys[sender][1], share):
            logger.warn(f'[{instance.id}] Invalid share in FC from {sender} about {value}')
            return False

        if value != val:
            logger.warn(f'[{instance.id}] Invalid value in FC from {sender}: {value}')
            return False

    return True
