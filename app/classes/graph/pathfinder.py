from enum import Enum
import math
import networkx as nx
import pyglet

from app.pythomas import pythomas as lib
from app.config import config, global_string_values as strings
from app.classes.graph.path import Path


class Pathfinder(pyglet.event.EventDispatcher):
    @staticmethod
    def get_event_type_on_path_update():
        return strings.events.on_path_update

    def __init__(self, graph, altitude_function=None):
        self.graph = graph
        self.start_node = None
        self.destination_node = None
        self.path = None
        if False:
            self.path = Path(None)
        self.register_event_type(Pathfinder.get_event_type_on_path_update())
        self.altitude_function = altitude_function

    def start(self):
        self.update_to_new_path()

    def get_path(self):
        if self.path is None:
            self.update_to_new_path()
        return self.path

    def get_edge_cost(self, from_node, to_node):
        max_slope = 2   # 60 degrees
        min_slope = -2  # -60 degrees
        slope_width = abs(max_slope - min_slope)
        altitude_wgt_coefficient = 1
        distance_coefficient = 1
        distance = lib.get_point_distance(from_node.get_position(), to_node.get_position())
        alt_raise = 0 if not self.altitude_function else self.altitude_function(from_node, to_node)
        slope = alt_raise/distance
        alt_contribution = 0
        if min_slope < slope < max_slope:
            alt_contribution = slope - min_slope
        dist_cost = distance
        alt_cost = alt_contribution / slope_width * distance
        return dist_cost * distance_coefficient + altitude_wgt_coefficient * alt_cost

    def set_start_node(self, node):
        if self.destination_node == node:
            self.destination_node = None
        self.start_node = node
        self.update_to_new_path()

    def set_destination_node(self, node):
        if self.start_node == node:
            self.start_node = None
        self.destination_node = node
        self.update_to_new_path()

    def clear_node(self, node):
        changed = False
        if self.start_node == node:
            self.start_node = None
            changed = True
        if self.destination_node == node:
            self.destination_node = None
            changed = True
        if changed:
            self.update_to_new_path()

    def update_to_new_path(self):
        new_path = self.create_path()
        if not self.path or new_path != self.path:
            event_type = Pathfinder.get_event_type_on_path_update()
            # print("Custom event: {0} - {1}".format(event_type, [node.label for node in new_path.get_node_list()]))
            self.path = new_path
            self.dispatch_event(event_type, self.path)

    def create_path(self):
        return None

    def update(self, dt):
        start_color = config.world.start_node_color
        destination_color = config.world.destination_node_color
        if self.start_node and self.start_node.get_color() != start_color:
            self.start_node.set_color()
        if self.destination_node and self.destination_node.get_color() != destination_color:
            self.destination_node.set_color(config.world.destination_node_color)
        if self.path:
            self.path.update(dt)
        self._update(dt)

    def _update(self, dt):
        # Override in inherited implementations to iterate search steps
        pass

    def draw(self, batch=None):
        if self.path:
            self.path.draw(batch)

    def get_path_edges(self):
        if self.path:
            return self.path.get_edge_list()
        return []

    def get_path_nodes(self):
        if self.path:
            return self.path.get_node_list()
        return []

# # Register event type to class
# Pathfinder.register_event_type(strings.events.on_path_update)


class AStarPathfinder(Pathfinder):
    def __init__(self, graph, altitude_function=None):
        Pathfinder.__init__(self, graph, altitude_function)

        def heuristics(from_node, to_node):
            return from_node.get_distance_to(to_node)
        self.heuristic_function = heuristics

    def create_path(self):
        nodes = []
        if self.start_node and self.destination_node:
            try:
                # print("Running NetworkX' A* algorithm.")
                nodes = nx.astar_path(self.graph, self.start_node, self.destination_node, self.heuristic_function)
            except nx.NetworkXNoPath:
                # print("No path from node {0} to node {1}".format(self.start_node.label, self.destination_node.label))
                pass
        path = Path(nodes)
        return path


class CustomPathfinder(Pathfinder):
    class State(Enum):
        Unassigned = 0
        Running = 1
        Paused = 2
        Stopped = 3

    def __init__(self, graph, name, altitude_function=None):
        Pathfinder.__init__(self, graph, altitude_function)
        self.name = name
        self.is_complete = False
        self.use_steps = False
        self.speed = 1  # Steps per second
        self.ticks_counter = 0
        self.running = False

    def _update(self, dt):
        if self.running:
            if self.use_steps:
                    self.ticks_counter += dt * self.speed
                    ticks = int(self.ticks_counter)
                    if ticks > 0:
                        for t in range(ticks):
                            self.tick()
                        self.ticks_counter -= ticks
            else:
                self.complete_search()

    def tick(self):
        pass

    def complete_search(self):
        pass

    def create_path(self):
        return self.path

    def start(self):
        self.running = True

    def pause(self):
        self.running = False

    def toggle_pause(self):
        self.running = not self.running

    def step(self, step_count=1):
        for i in range(step_count):
            self.tick()

    def stop(self):
        pass