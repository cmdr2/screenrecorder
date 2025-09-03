class EventDispatcher:
    def __init__(self):
        self._event_listeners = {}

    def add_event_listener(self, event_type, callback):
        if event_type not in self._event_listeners:
            self._event_listeners[event_type] = []
        self._event_listeners[event_type].append(callback)

    def remove_event_listener(self, event_type, callback):
        if event_type in self._event_listeners:
            self._event_listeners[event_type].remove(callback)
            if not self._event_listeners[event_type]:
                del self._event_listeners[event_type]

    def dispatch_event(self, event_type, **kwargs):
        listeners = self._event_listeners.get(event_type, [])
        for callback in listeners:
            callback(event_type, **kwargs)
