from enum import Enum

import networkx as nx
import pyglet

from app.pythomas import shapes as shapelib
from app.pythomas import pythomas as lib
from app.config import config, global_string_values as strings


class Path:
    def __init__(self, path_nodes):
        path_nodes = None if path_nodes == [None] else path_nodes
        self.nodes = [] if not path_nodes else path_nodes
        self.circles = dict()
        self.complete = False
        if path_nodes:
            self.complete = True
            self.update_node_circles()

    def add_node(self, node, index=None):
        if node in self.nodes:
            return False
        if index is None:
            self.nodes.append(node)
        else:
            self.nodes.insert(index, node)
        return True

    def remove_node(self, node):
        if node in self.circles:
            self.circles[node].delete()
        del self.circles[node]
        return lib.try_remove(self.nodes, node)

    def update_node_circles(self):
        for node in self.nodes:
            if node not in self.circles:
                pos = node.get_position()
                radius = node.get_visual_radius()+5
                color = lib.colors.extra.green
                if node in self.circles:
                    self.circles[node].delete()
                self.circles[node] = shapelib.Circle(pos, radius, color)

    def update(self, dt):
        self.update_node_circles()

    def draw(self, batch=None):
        for key in self.circles:
            self.circles[key].draw(batch)

    def delete(self):
        for key in self.circles:
            self.circles[key].delete()

    def get_edge_list(self):
        nodes = self.get_node_list()
        edges = []
        for i in range(1, self.get_count()):
            edges.append((nodes[i-1], nodes[i]))
        return edges

    def get_node_list(self):
        return self.nodes

    def get_count(self):
        return len(self.nodes)


class Pathfinder(pyglet.event.EventDispatcher):
    def __init__(self, graph):
        self.graph = graph
        self.start_node = None
        self.destination_node = None
        self.path = None
        self.register_event_type(strings.events.on_path_update)

    def get_path(self):
        if self.path is None:
            self.update_to_new_path()
        return self.path

    def get_edge_cost(self, from_node, to_node):
        return lib.get_point_distance(from_node.get_position(), to_node.get_position())

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
            self.start_node = None
            changed = True
        if changed:
            self.update_to_new_path()

    def update_to_new_path(self):
        self.path = self.create_path()
        self.dispatch_event(strings.events.on_path_update, self.path)

    def create_path(self):
        return None

    def update(self, dt):
        if self.start_node:
            self.start_node.set_color(config.world.start_node_color)
        if self.destination_node:
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

# Register event type to class
Pathfinder.register_event_type(strings.events.on_path_update)


class AStarPathfinder(Pathfinder):
    def __init__(self, graph):
        Pathfinder.__init__(self, graph)

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

    def __init__(self, graph):
        Pathfinder.__init__(self, graph)
        self.is_complete = False

    def _update(self, dt):
        pass

    def create_path(self):
        return self.path

    def start(self):
        pass

    def pause(self):
        pass

    def step(self, step_count=1):
        pass

    def stop(self):
        pass