from logging import getLogger

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

max_failures = num_hosts - 1

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
            self.lc_dict[process] = 0
            self.fc_dict[process] = []

        self.on('submit', on_submit_l)

        self.on('m_submit', on_submit_r)
        self.on('e_from_over_th', on_from_over_th)
        self.on('m_light_certificate', on_light_certificate)
        self.on('m_full_certificate', on_full_certificate)

def on_submit_l(instance, value):
    logger.debug(f'[{instance.id}] Submitting value {value}')

    instance.value = value

    raw = str(value)
    share = tss_share_sign(raw, keys[cur_process][0])

    raw = 'submit' + str(value) + share
    sig = tss_share_sign(raw, keys[cur_process][0])

    beb.trigger('send', [ instance.id, 'submit', value, share, sig ])

def on_submit_r(instance, sender, value, share, sig):
    logger.debug(f'[{instance.id}] Received submission from {sender}, for {value}')

    raw = 'submit' + str(value) + share
    if not tss_share_verify(raw, keys[sender][1], sig):
        return

    if not tss_share_verify(str(value), keys[sender][1], share):
        return

    if value != instance.value:
        return

    if sender in instance.xfrom:
        return

    instance.xfrom.append(sender)

    instance.light_cert.append((sender, share))
    instance.full_cert.append((sender, 'submit', value, share, sig))

    if len(instance.xfrom) >= num_hosts - max_failures:
        instance.trigger('e_from_over_th')

def on_from_over_th(instance):
    logger.debug(f'[{instance.id}] Receive threshold triggered')

    instance.confirmed = True
    instance.trigger('confirm', instance.value)

    senders, shares = zip(*instance.light_cert)
    combined = tss_combine(shares)
    beb.trigger('send', [ instance.id, 'light-certificate', instance.value, combined, senders ])

def on_light_certificate(instance, sender, value, light_cert, participants):
    logger.debug(f'[{instance.id}] Received light certificate from {sender}, for {value}, content: {light_cert[:16]}..., {participants}')

    pk = []
    for participant in participants:
        pk.append(keys[participant][1])

    if not tss_verify([ str(value) ] * len(participants), pk, light_cert):
        return

    # instance.obt_light_certs.append(('light-certificate', value, light_cert))

    for participant in participants:
        instance.lc_dict[participant] += 1

        if instance.lc_dict[participant] >= 2 and instance.confirmed and not instance.fc_sent:
            instance.fc_sent = True
            beb.trigger('send', [ instance.id, 'full-certificate', instance.value, instance.full_cert ])

def on_full_certificate(instance, sender, value, full_cert):
    logger.debug(f'[{instance.id}] Received full certificate from {sender}, for {value}, content: {full_cert}')

    if not full_cert_valid(full_cert, value):
        return

    # instance.obt_full_certs.append(full_cert)

    if instance.detected:
        return

    byzantines = []
    proof = []

    for message in full_cert:
        process = message[0]
        messages = instance.fc_dict[process]
        messages.append(message)

        assert(len(messages) <= 2)

        if len(messages) == 2:
            byzantines.append[process]
            proof.append((messages[0], messages[1]))

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
            return False

        if not tss_share_verify(str(value), keys[sender][1], share):
            return False

        if value != val:
            return False
