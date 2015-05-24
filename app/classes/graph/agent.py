import math
import pyglet
import networkx as nx
from enum import Enum
from pyglet.event import EventDispatcher

from app.config import config, global_string_values as strings, seeded_random as random
from app.pythomas import pythomas as lib
from app.pythomas.pythomas import PygletLib as Plib

from app.classes.animation import Animation

if False:
    from app.classes.graph.navigation_graph import NavigationGraph

agent_number = 1


class Trip:
    def __init__(self, path, cost):
        self.path = path
        self.cost = cost

    def get_start(self):
        return self.path[0]

    def get_destination(self):
        return self.path[-1]


class AgentUpdatedMessage(object):
    def __init__(self, agent, message):
        self.agent = agent
        self.message = message


class Agent(pyglet.event.EventDispatcher):
    event_type_on_agent_update = strings.events.on_agent_update

    class State(Enum):
        Idle = 0,
        Running = 1,
        Complete = 2

    class TravelState(Enum):
        Unassigned = 0,
        On_Start = 1,
        Underway = 2,
        On_Target = 3,

    def __init__(self, name, nav_graph, animation=None, path=None, step_interval=0, team='evil'):
        global agent_number
        if name is None:
            name = "Agent #{0}".format(agent_number)
        agent_number += 1
        self.name = name
        self.nav_graph = nav_graph
        self.push_handlers(self.nav_graph.agency)
        self.animation = animation

        self.step_interval = step_interval
        self.step_reached = False
        self._dt_counter = 0
        self.state = self.State.Idle
        self.current_node = None
        self.target_node = None
        self.team = team

        self.path_nodes = []
        self.travel_expenses = 0.0
        self.trip_coverage = 0.0
        self.travel_state = self.TravelState.Unassigned
        if path is not None:
            self.set_path(path)
        self.dispatch_event(self.event_type_on_agent_update, self, "Agent Created, Ready for duty!")

    def is_good_guy(self, compare_team='good'):
        return self.team == compare_team

    def set_path(self, path_nodes, move_to_first_node=False):
        if path_nodes:
            self.path_nodes = path_nodes
            self.set_target_node(self.path_nodes[-1])
            if move_to_first_node:
                self._move_to_first_path_node()

    def _move_to_first_path_node(self):
        self.move_to_node(self.path_nodes[0])
        if len(self.path_nodes) > 1:
            # self.set_target_node(self.path_nodes[1])
            self.set_travel_state(self.TravelState.On_Start)
        else:
            self.set_target_node(self.current_node)
            self.set_travel_state(self.TravelState.On_Target)

    def set_animation_move(self, set_to_move=True):
        if self.animation:
            if set_to_move:
                self.animation.set_state(Animation.State.Move)
            else:
                self.animation.set_state(Animation.State.Idle)

    def set_state(self, state):
        self.state = state
        if config.world.draw_agent_animation:
            if state == self.State.Running:
                self.set_animation_move(set_to_move=True)
            if state == self.State.Idle:
                self.set_animation_move(set_to_move=False)
            if state == self.State.Complete:
                self.set_animation_move(set_to_move=False)

    def set_travel_state(self, travel_state):
        self.travel_state = travel_state

    def is_complete(self):
        return self.state is self.State.Complete

    def is_idle(self):
        return self.state is self.State.Idle

    def set_target_node(self, target_node, set_to_run=False):
        self.target_node = target_node
        if target_node is None:
            return
        if self.animation:
            self.animation.set_target_position(target_node.get_position(), set_to_move=False)
        if set_to_run and self.state != self.State.Running:
            self.set_state(self.State.Running)

    def _is_on_target(self):
        return self.current_node is self.target_node

    def leave_current_node(self):
        if self.current_node:
            self.nav_graph.remove_occupant(self.current_node, occupant=self)

    def move_to_node(self, node):
        self.set_state(self.State.Running)
        self.set_travel_state(self.TravelState.Underway)
        self.leave_current_node()
        self.current_node = node
        self.nav_graph.add_occupant(self.current_node, occupant=self)
        if self._is_on_target():
            self.set_travel_state(self.TravelState.On_Target)
            if self.current_node is self.path_nodes[-1]:
                self.set_state(self.State.Complete)

    def move_to_next_node(self):
        if self.travel_state is self.TravelState.On_Target:
            return
        try:
            sz = len(self.path_nodes)
            path_i = self.path_nodes.index(self.current_node)+1
            if path_i < sz:
                self.move_to_node(self.path_nodes[path_i])
        except ValueError:  # from index()
            return
        except IndexError:  # from using path_i as index
            return
        if self._is_on_target():
            self.set_travel_state(self.TravelState.On_Target)

    def draw(self, batch=None):
        if self.animation and config.world.draw_agent_animation:
            self.animation.draw(batch)

    def _update_step_timer(self, dt):
        self._dt_counter += dt
        self.step_reached = False
        if self._dt_counter > self.step_interval:
            self._dt_counter -= self.step_interval
            self.step_reached = True

    def update(self, dt):
        self._update_step_timer(dt)
        if self.animation and config.world.draw_agent_animation:
            self.animation.update(dt)

    def start(self):
        pass

# Register event
Agent.register_event_type(Agent.event_type_on_agent_update)


class GoodAgent(Agent):
    def __init__(self, nav_graph, step_interval=config.world.agent_step_interval):
        # self.agent_image = pyglet.resource.image(lib.resource("walk.png"))
        # self.animation = Animation(self.agent_image, 8, 8, start_rotation=-math.pi)
        Agent.__init__(self, "Agent #111", nav_graph=nav_graph, animation=None,
                       step_interval=step_interval, team='good')
        path = self.nav_graph.pathfinder.get_path_nodes()
        self.set_path(path, move_to_first_node=False)
        self.set_target_node(self.path_nodes[-1])

    def update(self, dt):
        super().update(dt)
        if self.step_reached:
            self.move_to_next_node()

    def start(self):
        if self.path_nodes:
            first_node = self.path_nodes[0]
            if first_node.all_occupants_are(team=self.team, if_none=True):
                self._move_to_first_path_node()


class AutonomousAgent(Agent):
    def __init__(self, name, nav_graph, animation=None, step_interval=config.world.agent_step_interval, team='evil'):
        Agent.__init__(self, name, nav_graph, animation, step_interval=step_interval, team=team)
        self.start()
        if False:
            self.nav_graph = NavigationGraph()

    def set_random_next_as_target(self):
        def callback(node):
            return node is self.current_node or not node.any_occupant_is(self.team)
        next_node = self.nav_graph\
            .get_random_neighbor(self.current_node, include_from=True, node_filter_callback=callback)
        self.set_path([self.current_node, next_node])

    def move_to_random_next(self):
        self.set_random_next_as_target()
        self.move_to_next_node()

    def update(self, dt):
        super().update(dt)
        if self.step_reached:
            self.move_to_random_next()

    def start(self):
        super().start()
        if self.nav_graph.graph.nodes():
            self.set_state(self.State.Running)
            self.move_to_random_next()
        else:
            self.set_travel_state(self.TravelState.Unassigned)
            self.set_state(self.state.Idle)


class EvilAgent(AutonomousAgent):
    def __init__(self, name, nav_graph):
        super().__init__(name, nav_graph, team='evil')

