import asyncio

class EventBus():

    def __init__(self):
        self.listener = {}

    def add_listener(self, event_name, listener):
        if not self.listener.get(event_name, None):
            self.listener[event_name] = {listener}
        else:
            self.listener[event_name].add(listener)


        def remove_listener(self, event_name, listener):
            self.listener[event_name].remove(listener)
            if len(self.listener[event_name]) == 0:
                del self.listener[event_name]

        def emit(self, event_name,event ):
            listeners = self.listener.get(event, None)
            for listener in listeners:
                asyncio.create_task(listener(event))


