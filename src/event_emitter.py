class EventEmitter(object):
    callbacks = None

    def __init__(self):
        self.callbacks = {}

    def on(self, event_name, callback):
        if event_name not in self.callbacks:
            self.callbacks[event_name] = []

        self.callbacks[event_name].append(callback)

    def trigger(self, event_name, *args, **kwargs):
        if event_name not in self.callbacks:
            return

        for callback in self.callbacks[event_name]:
            callback(self, *args, **kwargs)
