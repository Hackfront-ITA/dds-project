from logging import getLogger

from event_emitter import EventEmitter
from network import BestEffortBroadcast

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

        self.on('submit', on_submit_l)

        self.on('m_submit', on_submit_r)
        self.on('e_from_over_th', on_from_over_th)
        self.on('m_light_certificate', on_light_certificate)
        self.on('e_conflicting_light_certs', on_conflicting_light_certs)
        self.on('m_full_certificate', on_full_certificate)
        self.on('e_conflicting_full_certs', on_conflicting_full_certs)

def on_submit_l(instance, value):
    instance.value = value

    share = tss_share_sign()
    id = instance.id.hex()
    sig = x_sign([ 'submit', value, share ])

    beb.trigger('send', [ id, 'submit', value, share, sig ])

def on_submit_r(instance, sender, value, share, sig):
    if not x_verify([ 'submit', value, share ]):
        return

    if not tss_share_verify(process, value, share):
        return

    if value != instance.value:
        return

    if process in instance.xfrom:
        return

    instance.xfrom.append(process)
    if len(instance.xfrom) >= num_hosts - max_failures:
        instance.trigger('e_from_over_th')

    instance.light_cert.append(share)
    instance.full_cert.append([ 'submit', value, share, sig ])

def on_from_over_th(instance):
    instance.confirmed = True
    instance.trigger('confirm', value)

    combined = tss_combine(instance.light_cert)
    beb.trigger('send', [ 'light-certificate', instance.value, combined ])

def on_light_certificate(instance, sender, value, light_cert):
    if not valid(light_cert, value):
        return

    instance.obt_light_certs.append([ 'light-certificate', value, light_cert ])
    if False and instance.confirmed:
        instance.trigger('e_conflicting_full_certs', cert_1, cert_2)

def on_conflicting_light_certs(instance, cert_1, cert_2):
    beb.trigger('send', [ 'full-certificate', instance.value, instance.full_cert ])
    pass

def on_full_certificate(instance, sender, value, full_cert):
    if not valid(full_cert, value):
        return

    instance.obt_full_certs.append(full_cert)
    if False:
        instance.trigger('conflicting-full-certs', cert_1, cert_2)

def on_conflicting_full_certs(instance, cert_1, cert_2):
    proof = []
    for i in range(num_hosts):
        if True:
            continue

        pair = (m1, m2)
        proof.append(pair)

    f = get_processes(proof)
    
    instance.trigger('detect', f, proof)


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
