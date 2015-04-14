from enum import Enum
import math
import networkx as nx
import pyglet

from app.pythomas import pythomas as lib
from app.config import config, global_string_values as strings
from app.classes.graph.path import Path
from app.classes.graph.node import Node


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
        self.refresh_timer = 0
        self._refresh_path = False
        self.waypoints = []

    def start(self):
        self.refresh_path()

    def get_path(self):
        if self.path is None:
            self.update_to_new_path()
        return self.path

    def get_edge_cost(self, from_node, to_node):
        if to_node.has_occupants():
            return config.world.blocked_node_edge_cost
        max_slope = 2   # 60 degrees
        min_slope = -2  # -60 degrees
        slope_width = abs(max_slope - min_slope)
        altitude_wgt_coefficient = 1
        distance_coefficient = 1
        distance = lib.get_point_distance(from_node.get_position(), to_node.get_position())
        alt_raise = 0 if not self.altitude_function else self.altitude_function(from_node, to_node)
        slope = alt_raise/distance
        alt_contribution = float("inf")  # Float representation of infinity
        if min_slope < slope < max_slope:
            alt_contribution = slope - min_slope
        dist_cost = distance
        alt_cost = alt_contribution / slope_width * distance
        return dist_cost * distance_coefficient + altitude_wgt_coefficient * alt_cost

    def notify_node_change(self, node):
        path_nodes = self.get_path_nodes()
        if node.has_occupants():
            if node in path_nodes:
                index = path_nodes.index(node)
                previous_node = path_nodes[index-1] if index > 0 else None
                self.split_path_on_waypoint(previous_node)

    def set_start_node(self, node):
        if self.destination_node == node:
            self.destination_node = None
        self.start_node = node
        self.refresh_path()

    def set_destination_node(self, node):
        if self.start_node == node:
            self.start_node = None
        self.destination_node = node
        self.refresh_path()

    def clear_node(self, node, ignore_refresh=False):
        if not node:
            return
        changed = False
        if self.start_node == node:
            self.start_node = None
            changed = True
        if self.destination_node == node:
            self.destination_node = None
            changed = True
        if changed or node in self.path.get_node_list():
            # self.path.remove_node(node)
            changed = True
        if changed and not ignore_refresh:
            self.refresh_path()

    def add_waypoint(self, node, index=None):
        if node is not self.start_node and node is not self.destination_node:
            if index and index < len(self.waypoints):
                self.waypoints.insert(index, node)
            else:
                self.waypoints.append(node)
        self.refresh_path()

    def remove_waypoint(self, node):
        lib.try_remove(self.waypoints, node)

    def waypoint_index(self, node):
        path_nodes = self.path.get_node_list()
        node_path_index = path_nodes.index(node)
        last_index = len(self.waypoints)
        if node not in path_nodes:
            return last_index
        try:
            return self.waypoints.index(node)
        except ValueError:
            pass
        for waypoint in self.waypoints:
            if path_nodes.index(waypoint) > node_path_index:
                return self.waypoints.index(waypoint)
        return last_index

    def _set_path(self, new_path):
        self.path = new_path
        if new_path is None:
            # self.start_node = None
            # self.destination_node = None
            return
        new_nodes = new_path.get_node_list()
        if len(new_nodes) > 1:
            self.start_node = new_nodes[0]
            self.destination_node = new_nodes[-1]
        elif len(new_nodes) == 1:
            self.start_node = self.destination_node = new_nodes[0]
        # else:
        #     self.start_node = None
        #     self.destination_node = None

    def refresh_path(self):
        self._refresh_path = True

    def update_to_new_path(self):
        new_path = self.assemble_waypoint_paths()
        if not self.path or new_path.get_node_list() != self.path.get_node_list():
            event_type = Pathfinder.get_event_type_on_path_update()
            self._set_path(new_path)
            self.dispatch_event(event_type, self.path)

    def assemble_waypoint_paths(self):
        if not self.start_node or not self.destination_node:
            return None
        start = self.start_node
        destination = self.destination_node
        paths = []
        nodes = [self.start_node]
        nodes.extend(self.waypoints)
        nodes.append(self.destination_node)
        for i in range(1, len(nodes)):
            self.start_node = nodes[i-1]
            self.destination_node = nodes[i]
            paths.append(self.create_path())
        result_nodes = [paths[0].first()]
        for path in paths:
            result_nodes.extend(path.get_node_list()[1:])
        assembled_path = Path(result_nodes)
        self.start_node = start
        self.destination_node = destination
        return assembled_path

    def split_path_on_waypoint(self, node):
        if node is None:
            return
        if node not in self.waypoints and self.path.has_node(node):
            self.add_waypoint(node, index=self.waypoint_index(node))

    def create_path(self):
        return None

    def update(self, dt):
        self.refresh_timer += dt

        if self._refresh_path and self.refresh_timer > config.world.pathfinder_refresh_interval:
            self.update_to_new_path()
            self._refresh_path = False
            self.refresh_timer = 0

        start_color = config.world.start_node_color
        destination_color = config.world.destination_node_color
        if self.start_node and self.start_node.get_color() != start_color:
            self.start_node.set_color(start_color)
        if self.destination_node and self.destination_node.get_color() != destination_color:
            self.destination_node.set_color(destination_color)
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
                nodes = nx.astar_path(self.graph, self.start_node, self.destination_node,
                                      heuristic=self.heuristic_function,
                                      weight=config.strings.weight)
            except nx.NetworkXNoPath:
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