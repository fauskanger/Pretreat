from app.config import config
from app.pythomas import shapes as shapelib
from app.pythomas import pythomas as lib


class Path:
    def __init__(self, path_nodes):
        path_nodes = None if path_nodes == [None] else path_nodes
        self.nodes = [] if not path_nodes else path_nodes
        self.circles = dict()
        self.triangles = dict()
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
                color = config.world.path_edge_color
                if node in self.circles:
                    self.circles[node].delete()
                self.circles[node] = shapelib.Circle(pos, radius, color)

    def update(self, dt):
        self.update_node_circles()

    def draw(self, batch=None):
        pass
        # for key in self.circles:
        #     self.circles[key].draw(batch)

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

