import math
import pyglet
import networkx as nx
from app.pythomas import pythomas as lib
from app.config import config


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

    def set_position(self, new_position):
        self.x = new_position[0]
        self.y = new_position[1]
        self.circle.set_position(new_position)
        self.update_parameters()

    def update_parameters(self):
        self.label = "{0},{1}".format(self.x, self.y)
        pass

    def get_radius(self):
        return self.current_radius

    def get_position(self):
        return self.x, self.y

    def draw(self, radius_offset=0.0, batch=None):
        def draw_circle():
            if radius_offset == 0.0:
                self.circle.draw(batch)
            else:
                self.circle.expand_radius(-radius_offset)
                self.circle.draw(batch)
                self.circle.expand_radius(radius_offset)

        draw_circle()

    def update(self, dt):
        pass


class Edge:
    def __init__(self, from_node, to_node):
        self.shape = None
        self.update_shape(from_node, to_node)

    def update_shape(self, from_node, to_node):
        from_x, from_y = from_node.get_position()
        to_x, to_y = to_node.get_position()
        theta = math.atan2(to_y-from_y, to_x-from_x)
        # theta = -theta
        lane_offset = config.world.edge_lane_offset
        dx = lane_offset * math.sin(theta)
        dy = lane_offset * math.cos(theta)
        offset = dx, -dy
        from_position = lib.sum_points((from_x, from_y), offset)
        to_position = lib.sum_points((to_x, to_y), offset)

        colors = lib.flatten_list_of_tuples([config.world.edge_color * 4])
        self.shape = lib.Rectangle(from_position, to_position, config.world.edge_thickness, colors_list=colors)

    def draw(self, batch=None):
        self.shape.draw(batch)


class Pathfinder:
    def __init__(self, graph):
        self.graph = graph
        self.start_node = None
        self.destination_node = None


class NavigationGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.selected_nodes = []
        # self.selected_nodes_shapes = []
        self.pathfinder = Pathfinder(self.graph)
        # self.nodes = []

    @staticmethod
    def get_node_distance(from_node, to_node):
        x = abs(from_node.x - to_node.x)
        y = abs(from_node.y - to_node.y)
        return math.sqrt(x * x + y * y)

    def get_node_from_position(self, position):
        for node in self.graph.nodes():
            if lib.get_point_distance(position, node.get_position()) < node.get_radius():
                return node
        return None

    def set_start_node(self, node):
        if node is not None:
            self.pathfinder.start_node = node
            print("Start node: {0}".format(node.label))

    def set_destination_node(self, node):
        if node is not None:
            self.pathfinder.destination_node = node
            print("Destination node: {0}".format(node.label))

    def create_edge_from_selected_to(self, node):
        for selected_node in self.selected_nodes:
            self.add_edge(selected_node, node)

    def create_edge_to_selected_from(self, node):
        for selected_node in self.selected_nodes:
            self.add_edge(node, selected_node)

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
        for existing_node in self.graph.nodes():
            distance = self.get_node_distance(existing_node, node)
            if distance < min(node.get_radius(), existing_node.get_radius()):
                return False
        self.graph.add_node(node)
        return True

    def remove_node(self, node):
        if node is None:
            return False
        self.deselect_node(node)
        try:
            self.graph.remove_node(node)
            return True
        except nx.NetworkXError:
            return False

    def add_edge(self, from_node, to_node):
        if from_node is None or to_node is None:
            return False
        try:
            weight = self.get_edge_cost(from_node, to_node)
            self.graph.add_edge(from_node, to_node, weight=weight, object=Edge(from_node, to_node))
            return True
        except nx.NetworkXError:
            return False

    def remove_edge(self, from_node, to_node):
        if from_node is None or to_node is None:
            return False
        if self.graph.has_edge(from_node, to_node):
            try:
                self.graph.remove_edge(from_node, to_node)
                return True
            except nx.NetworkXError:
                return False

    def remove_edges_from_many(self, to_node, from_nodes):
        for from_node in from_nodes:
            self.remove_edge(from_node, to_node)

    def remove_edges_to_many(self, from_node, to_nodes):
        for to_node in to_nodes:
            self.remove_edge(from_node, to_node)

    def get_edge_object(self, edge):
            return self.graph[edge[0]][edge[1]]['object']

    # TODO: batched rendering of primitives
    def draw(self, batch=None):
        def draw_edges():
            for edge in self.graph.edges(data=True):
                self.get_edge_object(edge).draw(batch)


        def draw_selection(node):
            color = config.world.selected_node_color
            radius = node.get_radius() + config.world.selected_radius_increase
            circle = lib.Circle(position=node.get_position(), radius=radius, color=color)
            circle.draw()

        def draw_nodes():
            is_reading_data = True
            for node in self.graph.nodes(data=is_reading_data):
                node_instance = node
                if is_reading_data:
                    node_instance = node[0]
                # node_instance.draw(batch)
                if node_instance in self.selected_nodes:
                    draw_selection(node_instance)
                    node_instance.draw(radius_offset=config.world.selected_radius_decrease)
                    node_instance.draw()
                # if node_instance == self.pathfinder.start_node:
                #     node_instance.draw(radius_offset=+20)
                # elif node_instance == self.pathfinder.destination_node:
                #     node_instance.draw(radius_offset=+20)
                else:
                    node_instance.draw()

        draw_nodes()
        draw_edges()

    def update(self, dt):
        pass

