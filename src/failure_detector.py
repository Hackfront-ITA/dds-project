from logging import getLogger
from threading import Event, Thread

from event_emitter import EventEmitter
from network import BestEffortBroadcast

from config import network, num_hosts, processes

DELTA = 5

CLASS_ID = 'pfd'

ALLOWED_PACKETS = [
	'heartbeat',
]

instances = {}

logger = getLogger(__name__)
beb = BestEffortBroadcast

class PerfectFailureDetector(EventEmitter):
	def __init__(self):
		super().__init__()

		self.id = CLASS_ID
		instances[self.id] = self

		self.alive = set(processes)
		self.detected = set()

		self.exit = Event()
		self.send_thread = Thread(target=send_main, args=( self, ))

		self.on('m_heartbeat', on_heartbeat)

		self.send_thread.start()

	def __del__(self):
		self.exit.set()
		self.send_thread.join()

def send_main(pfd):
	while True:
		for process in processes:
			if process not in pfd.alive and process not in pfd.detected:
				pfd.detected.add(process)
				logger.debug(f'[{pfd.id}] Process {process} is detected')
				pfd.trigger('crash', process)

		pfd.alive = set()
		beb.trigger('send', [ pfd.id, 'heartbeat' ])
		pfd.exit.wait(DELTA)

def on_heartbeat(pfd, sender):
	pfd.alive.add(sender)

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
