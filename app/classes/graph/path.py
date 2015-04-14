from app.config import config
from app.pythomas import shapes as shapelib
from app.pythomas import pythomas as lib


class Path:
    def __init__(self, path_nodes):
        path_nodes = None if path_nodes == [None] else path_nodes
        self.nodes = [] if not path_nodes else path_nodes
        self.complete = False
        if path_nodes:
            self.complete = True

    def __add__(self, other):
        if self.last() is other.first():
            if len(other.nodes) > 1:
                return Path(self.nodes + other.nodes[1:])
            return self.copy()
        else:
            return Path(self.nodes + other.nodes)

    def add_node(self, node, index=None):
        if node in self.nodes:
            return False
        if index is None:
            self.nodes.append(node)
        else:
            self.nodes.insert(index, node)
        return True

    def remove_node(self, node):
        return lib.try_remove(self.nodes, node)

    def update(self, dt):
        pass

    def draw(self, batch=None):
        pass

    def delete(self):
        pass

    def get_edge_list(self):
        nodes = self.get_node_list()
        edges = []
        for i in range(1, self.get_count()):
            edges.append((nodes[i-1], nodes[i]))
        return edges

    def first(self):
        if not self.nodes:
            return None
        return self.nodes[0]

    def last(self):
        if not self.nodes:
            return None
        return self.nodes[-1]

    def has_node(self, node):
        return node in self.get_node_list()

    def get_node_list(self):
        return self.nodes

    def get_count(self):
        return len(self.nodes)

    def copy(self):
        return Path(self.nodes)


