import math
import pyglet
from enum import Enum
from app.classes.animation import Animation

from app.config import config, global_string_values as strings
from app.pythomas import pythomas as lib
from app.pythomas.pythomas import PygletLib as Plib

agent_number = 1


class Trip:
    def __init__(self, path, cost):
        self.path = path
        self.cost = cost

    def get_start(self):
        return self.path[0]

    def get_destination(self):
        return self.path[-1]


class Agent:
    class State(Enum):
        Idle = 0,
        Running = 1,
        Complete = 2

    class TravelState(Enum):
        Unassigned = 0,
        On_Start = 1,
        Underway = 2,
        On_Target = 3,

    def __init__(self, name, animation, path=None):
        global agent_number
        if name is None:
            name = "Agent #{0}".format(agent_number)
        agent_number += 1
        self.animation = animation
        self.state = self.State.Idle
        self.current_node = None
        self.target_node = None
        self.path_nodes = []
        self.travel_expenses = 0.0
        self.trip_coverage = 0.0
        self.travel_state = self.TravelState.Unassigned
        if path is not None:
            self.set_path(path)

    def set_path(self, path_nodes):
        if path_nodes is not None and len(path_nodes) > 1:
            self.path_nodes = path_nodes
            self.set_current_node(path_nodes[0])
            if len(path_nodes) > 2:
                self.set_target_node(path_nodes[1])
                self.set_travel_state(self.TravelState.On_Start)
            else:
                self.set_target_node(self.current_node)
                self.set_travel_state(self.TravelState.On_Target)

    def set_animation_move(self, set_to_move=True):
        if set_to_move:
            self.animation.set_state(Animation.State.Move)
        else:
            self.animation.set_state(Animation.State.Idle)

    def set_state(self, state):
        self.state = state
        if state == self.State.Running:
            self.set_animation_move(set_to_move=True)
        if state == self.State.Idle:
            self.set_animation_move(set_to_move=False)
        if state == self.State.Complete:
            self.set_animation_move(set_to_move=False)

    def set_travel_state(self, travel_state):
        self.travel_state = travel_state

    def set_target_node(self, target_node, set_to_run=False):
        self.target_node = target_node
        if target_node is None:
            return
        self.animation.set_target_position(target_node.get_position(), set_to_move=False)
        if set_to_run and self.state != self.State.Running:
            self.set_state(self.State.Running)

    def set_current_node(self, node):
        self.current_node = node

    def draw(self, batch=None):
        if self.animation is not None:
            self.animation.draw(batch)

    def update(self, dt):
        if self.animation is not None:
            self.animation.update(dt)


class SuperAgent(Agent):
    def __init__(self):
        self.agent_image = pyglet.resource.image(lib.resource("walk.png"))
        self.animation = Animation(self.agent_image, 8, 8, start_rotation=-math.pi)
        Agent.__init__(self, "Agent #111", self.animation)