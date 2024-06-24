from logging import getLogger

from event_emitter import EventEmitter
from network import BestEffortBroadcast

from config import keys, processes

CLASS_ID = 'ac-cf'

ALLOWED_PACKETS = [
    'submit',
    'light-certificate',
    'full-certificate',
]

instances = {}

max_failures = floor(num_hosts / 3)

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
        self.obt_light_certs = []
        self.obt_full_certs = []

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
    instance.value = value

    share = tss_share_sign()
    id = instance.id.hex()
    raw = bytes('submit' + value + share, 'utf8')
    sig = tss_share_sign(raw, keys[cur_process][0])

    beb.trigger('send', [ id, 'submit', value, share, sig ])

def on_submit_r(instance, sender, value, share, sig):
    raw = bytes('submit' + value + share, 'utf8')
    if not tss_share_verify(raw, keys[sender][1], sig):
        return

    if not tss_share_verify(value, keys[sender][1], share):
        return

    if value != instance.value:
        return

    if process in instance.xfrom:
        return

    instance.xfrom.append(process)
    if len(instance.xfrom) >= num_hosts - max_failures:
        instance.trigger('e_from_over_th')

    instance.light_cert.append((sender, share))
    instance.full_cert.append((sender, 'submit', value, share, sig))

def on_from_over_th(instance):
    instance.confirmed = True
    instance.trigger('confirm', value)

    combined = tss_combine(instance.light_cert)
    beb.trigger('send', ('light-certificate', instance.value, combined))

def on_light_certificate(instance, sender, value, light_cert):
    if not light_cert_valid(light_cert, value):
        return

    instance.obt_light_certs.append(('light-certificate', value, light_cert))

    for entry in light_cert:
        process = entry[0]
        instance.lc_dict[process] += 1

        if instance.lc_dict[process] >= 2 and instance.confirmed and not instance.fc_sent:
            instance.fc_sent = True
            beb.trigger('send', [ 'full-certificate', instance.value, instance.full_cert ])

def on_full_certificate(instance, sender, value, full_cert):
    if not full_cert_valid(full_cert, value):
        return

    instance.obt_full_certs.append(full_cert)

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


def light_cert_valid():
    pass

def full_cert_valid():
    pass
