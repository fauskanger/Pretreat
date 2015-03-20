import pyglet


# Abstract observer class
class Observer(object):
    def __init__(self, subject):
        subject.push_handlers(self)


class State:
    def __init__(self, name="BaseState"):
        self.name = name
        print("State: {0}".format(self.name))

    def update(self, delta):
        print("{0} Delta time: {1}".format(self.name, delta))

    def draw(self):
        print("{0} Rendering".format(self.name))

    def handle_event(self, event):
        print("{0} Notified of event: {0}".format(self.name, event))

    def activate(self):
        print("{0} Activated".format(self.name))

    def deactivate(self):
        print("{0} Deactivated".format(self.name))


class StateMachine(pyglet.event.EventDispatcher, Observer):
    def __init__(self, event_subject, name="BaseStateMachine"):
        super().__init__(event_subject)
        print("StateMachine")
        self.name = name
        self.states_stack = []

    def get_current_state(self):
        states_count = len(self.states_stack)
        if states_count < 1:
            return None
        return self.states_stack[states_count-1]

    def push_state(self, state):
        if state is None:
            return False
        self.states_stack.append(state)
        return True

    def pop_state(self):
        states_count = len(self.states_stack)
        popped_state = None
        if states_count > 0:
            popped_state = self.states_stack.pop()
        self.dispatch_event('on_state_machine_pop', popped_state)
        return popped_state

    def update(self, delta):
        print("{0} Delta time: {1}".format(self.name, delta))

    def draw(self):
        print("{0} Rendering".format(self.name))

    def handle_event(self, event):
        print("{0} Notified of event: {0}".format(self.name, event))

StateMachine.register_event_type('on_state_machine_pop')