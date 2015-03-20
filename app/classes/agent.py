import pyglet

from app.config import config, global_string_values as strings
from app.pythomas.pythomas import PygletLib as Plib

agent_number = 0


class Agent:
    def __init__(self, name, animation):
        if name is None:
            name = "Agent #{0}".format(agent_number)
        self.animation = animation
