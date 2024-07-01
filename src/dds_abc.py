from confirmer import AccountableConfirmer
from consensus import FloodingConsensus
from event_emitter import EventEmitter

class ABC(EventEmitter):
	def __init__(self, max_failures):
		super().__init__()

		self.ac = AccountableConfirmer(max_failures)
		self.bc = FloodingConsensus()

		abc = self
		ac = self.ac
		bc = self.bc

		abc.on('propose', on_propose)
		bc.on('decide', on_decide)
		ac.on('confirm', on_confirm)
		ac.on('detect', on_detect)

def on_propose(instance, proposal):
	bc = instance.bc
	bc.trigger('propose', proposal)

def on_decide(instance, decision):
	ac = instance.ac
	ac.trigger('submit', decision)

def on_confirm(instance, confirmation):
	abc = instance
	abc.trigger('decide', confirmation)

def on_detect(instance, byzantines, proof):
	abc = instance
	abc.trigger('detect', byzantines, proof)
