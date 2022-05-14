class StateMachine:
    def __init__(self):
        self.handlers = {}
        self.start_state = None
        self.end_states = []

    def add_state(self, name, handler, end_state=False):
        self.handlers[name] = handler
        if end_state:
            self.end_states.append(name)

    def set_start(self, name):
        self.start_state = name

    def run(self):
        try:
            handler = self.handlers[self.start_state]
        except:
            raise Exception("must call .set_start() before .run()")
        if not self.end_states:
            raise Exception("at least one state must be an end_state")

        while True:
            newState = handler()
            if newState in self.end_states:
                break
            else:
                handler = self.handlers[newState]
