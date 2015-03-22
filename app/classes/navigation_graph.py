import math
import pyglet
import networkx as nx
from app.pythomas import pythomas as lib
from app.config import config, global_string_values as strings


class Node:
    def __init__(self, x, y, altitude=0, content=None):
        self.current_radius = config.world.node_radius
        self.default_color = config.world.node_color
        self.current_color = self.default_color
        self.x = int(x)
        self.y = int(y)
        self.label = "{0},{1}".format(x, y)
        self.altitude = altitude
        self.content = content
        self.batch_group = pyglet.graphics.OrderedGroup(config.world.node_order_index)
        self.printed = False
        self.circle = lib.Circle((x, y), self.current_radius, self.current_color)

    def set_radius(self, new_radius):
        self.current_radius = new_radius
        self.circle.radius = self.current_radius

    def get_radius(self):
        return self.current_radius

    def get_position(self):
        return self.x, self.y

    def draw(self, radius_offset=0.0, batch=None):
        self.circle.expand_radius(-radius_offset)
        self.circle.draw(batch)
        self.circle.expand_radius(radius_offset)

    def update(self, dt):
        pass


class NavigationGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.selected_nodes = []
        self.selected_nodes_shapes = []
        # self.nodes = []

    @staticmethod
    def get_node_distance(from_node, to_node):
        x = abs(from_node.x-to_node.x)
        y = abs(from_node.y-to_node.y)
        return math.sqrt(x*x + y*y)

    def get_node_from_position(self, position):
        for node in self.graph.nodes():
            if lib.get_point_distance(position, node.get_position()) < node.get_radius():
                return node
        return None

    

    def select_node(self, node):
        if node is None or node in self.selected_nodes:
            return False
        self.selected_nodes.append(node)
        return True

    def deselect_node(self, node):
        if node is None or node not in self.selected_nodes:
            return False
        self.selected_nodes.remove(node)
        return True

    def select_node_at_position(self, position):
        node = self.get_node_from_position(position)
        if node is not None:
            if not self.select_node(node):
                self.deselect_node(node)

    def deselect_node_at_position(self, position):
        node = self.get_node_from_position(position)
        if node is not None:
            if not self.deselect_node(node):
                self.select_node(node)

    def deselect_all_nodes(self):
        self.selected_nodes = []

    def get_edge_cost(self, from_node, to_node):
        return self.get_node_distance(from_node, to_node)

    def add_node(self, node):
        if node is None:
            return False
        self.graph.add_node(node)
        # self.nodes.append(node)
        return True

    def add_edge(self, from_node, to_node):
        if self.graph.has_node(from_node) and self.graph.has_node(to_node):
            if not self.graph.has_edge(from_node, to_node):
                self.graph.add_edge(from_node, to_node)
                return True
        return False

    # TODO: batched rendering of primitives
    def draw(self, batch=None):
        def draw_selection():
            for node in self.selected_nodes:
                color = config.world.selected_node_color
                circle = lib.Circle(position=node.get_position(), radius=node.get_radius()+4, color=color)
                circle.draw()
            pass
        draw_selection()

        def draw_nodes():
            is_reading_data = True
            for node in self.graph.nodes(data=is_reading_data):
                node_instance = node
                if is_reading_data:
                    node_instance = node[0]
                # node_instance.draw(batch)
                if node in self.selected_nodes:
                    node_instance.draw(radius_offset=config.world.selected_radius_decrease)
                else:
                    node_instance.draw()
        draw_nodes()

    def update(self, dt):
        pass

