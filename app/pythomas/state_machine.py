class State:
    def __init__(self):
        print("State")


class StateMachine:
    def __init__(self):
        print("StateMachine")
        self.states_stack = []