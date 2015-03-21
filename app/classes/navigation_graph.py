import math
import pyglet
import networkx as nx
from app.pythomas import pythomas as lib
from app.config import config, global_string_values as strings


class Node:
    def __init__(self, x, y, altitude=0, content=None):
        self.current_radius = config.world.default_node_radius
        self.default_color = config.world.default_node_color
        self.current_color = self.default_color
        self.x = int(x)
        self.y = int(y)
        self.label = "{0},{1}".format(x, y)
        self.altitude = altitude
        self.content = content
        self.batch_group = pyglet.graphics.OrderedGroup(config.world.default_node_order_index)
        self.draw_points_list = self.create_draw_points()
        self.vertex_list = self.create_vertex_list()
        self.printed = False

    def update_draw_points(self):
        self.draw_points_list = self.create_draw_points()

    def create_draw_points(self):
        return lib.get_circle_points(center=(self.x, self.y), radius=self.current_radius, include_center=True)

    def set_radius(self, new_radius):
        self.current_radius = new_radius

    def get_position(self):
        return self.x, self.y

    def create_vertex_list(self):
        number_of_vertices = int(len(self.draw_points_list)/2)
        vertex_list = pyglet.graphics.vertex_list(number_of_vertices, 'v2f', config.world.color_mode)
        vertex_list.vertices = self.draw_points_list
        vertex_list.colors = self.current_color*number_of_vertices
        return vertex_list

    def update_vertex_list_points(self):
        self.vertex_list = self.create_vertex_list()

    def draw(self, batch=None):
        mode = pyglet.gl.GL_TRIANGLE_FAN
        if self.vertex_list is None:
            self.update_vertex_list_points()
        if batch is None:
            # pyglet.graphics.draw(self.vertex_list.get_size(), mode, self.vertex_list)
            self.vertex_list.draw(mode)
        else:
            if not self.printed:
                # print("Draw_points_list ({0}):\n {1}".format(len(self.draw_points_list), self.draw_points_list))
                # print("Node Colors: {0}\n{1}\n{2}\n{3}\n{4}".format(*draw_arguments))
                self.printed = True
            batch.add(self.vertex_list.get_size(), mode, None,
                      ('v2f', self.vertex_list.vertices),
                      (config.world.color_mode, self.vertex_list.colors))

    def update(self, dt):
        pass


class NavigationGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        # self.nodes = []

    @staticmethod
    def get_distance(from_node, to_node):
        x = abs(from_node.x-to_node.x)
        y = abs(from_node.y-to_node.y)
        return math.sqrt(x*x + y*y)

    def get_edge_cost(self, from_node, to_node):
        return self.get_distance(from_node, to_node)

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

    def draw(self, batch=None):
        def draw_nodes():
            is_reading_data = True
            for node in self.graph.nodes(data=is_reading_data):
                node_instance = node
                if is_reading_data:
                    node_instance = node[0]
                node_instance.draw()
        draw_nodes()

