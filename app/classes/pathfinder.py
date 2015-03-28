import networkx as nx
from enum import Enum
from app.pythomas import shapes as shapelib
from app.pythomas import pythomas as lib
from app.classes.node import Node


class Path:
    def __init__(self, path_nodes=None):
        self.nodes = [] if not path_nodes else path_nodes
        self.circles = dict()

    def add_node(self, node, index=None):
        if node in self.nodes:
            return False
        if index is None:
            self.nodes.append(node)
        else:
            self.nodes.insert(index, node)
        return True

    def remove_node(self, node):
        del self.circles[node]
        return lib.try_remove(self.nodes, node)

    def update_node_circles(self):
        for node in self.nodes:
            if node not in self.circles:
                pos = node.get_position()
                radius = node.get_visual_radius()+5
                color = lib.colors.extra.green
                self.circles[node] = shapelib.Circle(pos, radius, color)

    def draw(self):
        for circle in self.circles:
            circle.draw()

    def get_node_list(self):
        return self.nodes


class Pathfinder:
    def __init__(self, graph):
        self.graph = graph
        self.start_node = None
        self.destination_node = None
        self.path = None

    def get_path(self):
        if self.path is None:
            self.update_path()
        return self.path

    def set_start_node(self, node):
        if self.destination_node == node:
            self.destination_node = None
        self.start_node = node

    def set_destination_node(self, node):
        if self.start_node == node:
            self.start_node = None
        self.destination_node = node

    def clear_node(self, node):
        if self.start_node == node:
            self.start_node = None
        if self.destination_node == node:
            self.start_node = None

    def update_path(self):
        self.path = self.find_path()

    def find_path(self):
        return None

    def update(self, dt):
        pass

    def draw(self, batch=None):
        if self.path:
            self.path.draw(batch)


class AStarPathfinder(Pathfinder):
    def __init__(self, graph):
        Pathfinder.__init__(self, graph)

    def find_path(self):
        return Path(nx.astar_path(self.graph, self.start_node, self.destination_node))


class CustomPathfinder(Pathfinder):
    class State(Enum):
        Unassigned = 0
        Running = 1
        Paused = 2
        Stopped = 3

    def __init__(self, graph):
        Pathfinder.__init__(self, graph)
        self.is_complete = False

    def find_path(self):
        return self.path

    def start(self):
        pass

    def pause(self):
        pass

    def step(self, step_count=1):
        pass

    def stop(self):
        pass