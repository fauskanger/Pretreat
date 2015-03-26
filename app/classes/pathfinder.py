import networkx as nx


class Pathfinder:
    def __init__(self, graph):
        self.graph = graph
        self.start_node = None
        self.destination_node = None
        self.path = None

    def set_start_node(self, node):
        self.start_node = node

    def set_destination_node(self, node):
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


class AStarPathfinder(Pathfinder):
    def __init__(self, graph):
        Pathfinder.__init__(self, graph)

    def find_path(self):
        return nx.astar_path(self.graph, self.start_node, self.destination_node)
