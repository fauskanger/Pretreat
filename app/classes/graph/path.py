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

    # def update_node_circles(self):
    #     for node in self.circles:
    #         circle = self.circles[node]
    #         pos = node.get_position()
    #         radius = node.get_visual_radius()+5
    #         color = config.world.path_edge_color
    #         if circle.get_position() != pos:
    #             circle.set_position(pos)
    #         if circle.radius != radius:
    #             circle.set_radius(radius)
    #         if circle.color != color:
    #             circle.set_color(color)

    # def create_node_circle(self, node):
    #     pos = node.get_position()
    #     radius = node.get_visual_radius()+5
    #     color = config.world.path_edge_color
    #     if node in self.circles:
    #         self.circles[node].delete()
    #     self.circles[node] = shapelib.Circle(pos, radius, color)

    # def create_node_circles(self):
    #     for node in self.nodes:
    #         if node not in self.circles:
    #             self.create_node_circle(node)

    def update(self, dt):
        # self.update_node_circles()
        pass

    def draw(self, batch=None):
        pass
        # for key in self.circles:
        #     self.circles[key].draw(batch)

    def delete(self):
        # for key in self.circles:
        #     self.circles[key].delete()
        pass

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

