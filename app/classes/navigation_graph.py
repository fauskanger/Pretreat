import math
import pyglet
import networkx as nx
from enum import Enum
from app.pythomas import pythomas as lib
from app.config import config


class Node:
    class State(Enum):
        Default = 0,
        Start = 1,
        Destination = 2

    def __init__(self, x, y, altitude=0, content=None, is_selected=False):
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
        self.state = self.State.Default
        self.is_selected = is_selected

    def set_as_selected(self, is_selected=True):
        self.is_selected = is_selected

    def set_radius(self, new_radius):
        self.current_radius = new_radius
        self.circle.set_radius(self.current_radius)

    def set_state(self, state):
        self.state = state

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

    def get_padded_radius(self):
        padding = config.world.selected_radius_increase+config.world.node_padding
        return self.get_radius() + padding

    def get_visual_radius(self):
        extra = 0.0
        if self.is_selected:
            extra += config.world.selected_radius_increase
        return self.get_radius()+extra

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

    def set_color(self, color):
        self.circle.set_color(color)

    def update(self, dt):
        pass


class Edge:
    def __init__(self, from_node, to_node):
        self.shape = None
        self.inner_from_shape = None
        self.inner_to_shape = None
        self.p1_circle = None
        self.p2_circle = None
        self.update_shape(from_node, to_node)

    def draw(self, batch=None):
        self.shape.draw(batch)
        self.inner_from_shape.draw(batch)
        self.inner_to_shape.draw(batch)
        self.p1_circle.draw(batch)
        self.p2_circle.draw(batch)

    def update_shape(self, from_node, to_node):
        from_x, from_y = from_node.get_position()
        to_x, to_y = to_node.get_position()
        theta = math.atan2(to_y-from_y, to_x-from_x)

        def get_pos_offset(node):
            offset_radius = config.world.edge_lane_offset
            if node.is_selected and config.world.adjust_edge_to_selection:
                offset_radius += config.world.selected_radius_decrease
            dx = offset_radius * math.sin(theta)
            dy = offset_radius * math.cos(theta)
            offset = dx, -dy
            return offset

        from_offset = get_pos_offset(from_node)
        to_offset = get_pos_offset(to_node)
        from_position = lib.sum_points(from_node.get_position(), from_offset)
        to_position = lib.sum_points(to_node.get_position(), to_offset)

        from_circle_point = lib.get_point_on_circle(circle_center=from_node.get_position(),
                                                    radius=from_node.get_visual_radius(),
                                                    line_point=from_position,
                                                    direction_point=to_position)

        to_circle_point = lib.get_point_on_circle(circle_center=to_node.get_position(),
                                                  radius=to_node.get_visual_radius(),
                                                  line_point=to_position,
                                                  direction_point=from_position)
        self.p1_circle = self.p2_circle = None
        if from_circle_point is not None:
            self.p1_circle = lib.Circle(from_circle_point, config.world.edge_end_radius, lib.colors.red)
        if to_circle_point is not None:
            self.p2_circle = lib.Circle(to_circle_point, config.world.edge_end_radius, lib.colors.blue)

        colors = list(config.world.edge_color * 4)
        if from_circle_point is None or to_circle_point is None:
            print("Could not draw to circle.")
            self.shape = lib.Rectangle(from_position, to_position,
                                       config.world.edge_thickness, colors_list=colors)
            self.inner_from_shape = self.inner_to_shape = None
        else:
            self.shape = lib.Rectangle(from_circle_point, to_circle_point,
                                       config.world.edge_thickness, colors_list=colors)
            inner_color = lib.colors.extra.green
            inner_line_width = 4
            self.inner_from_shape = lib.Rectangle(from_node.get_position(), self.p1_circle.get_position(),
                                                  radius=inner_line_width,  color=inner_color)
            self.inner_to_shape = lib.Rectangle(to_node.get_position(), self.p2_circle.get_position(),
                                                radius=inner_line_width,  color=inner_color)


class Pathfinder:
    def __init__(self, graph):
        self.graph = graph
        self.start_node = None
        self.destination_node = None


class NavigationGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.selected_nodes = []
        self.pathfinder = Pathfinder(self.graph)
        self.states_color = {
            Node.State.Default: config.world.node_color,
            Node.State.Start: config.world.start_node_color,
            Node.State.Destination: config.world.destination_node_color,
            }

    @staticmethod
    def get_node_distance(from_node, to_node):
        x = abs(from_node.x - to_node.x)
        y = abs(from_node.y - to_node.y)
        return math.sqrt(x * x + y * y)

    def is_valid_node_position(self, position):
        for existing_node in self.graph.nodes():
            distance = lib.get_point_distance(existing_node.get_position(), position)
            if distance < existing_node.get_padded_radius()*2:
                return False
        return True

    def get_node_from_position(self, position):
        for node in self.graph.nodes():
            if lib.get_point_distance(position, node.get_position()) < node.get_radius():
                return node
        return None

    def set_node_to_default(self, node):
        self.set_node_state(node, Node.State.Default)

    def set_node_state(self, node, state):
        if node is not None:
            node.set_color(self.states_color[state])
            node.set_state(state)
            if state == Node.State.Start:
                self.set_node_to_default(self.pathfinder.start_node)
                self.pathfinder.start_node = node
            elif state == Node.State.Destination:
                self.set_node_to_default(self.pathfinder.destination_node)
                self.pathfinder.destination_node = node

    def set_start_node(self, node):
        if node is not None:
            print("Start node: {0}".format(node.label))
            self.set_node_to_default(self.pathfinder.start_node)
            self.set_node_state(node, Node.State.Start)

    def set_destination_node(self, node):
        if node is not None:
            print("Destination node: {0}".format(node.label))
            self.set_node_to_default(self.pathfinder.destination_node)
            self.set_node_state(node, Node.State.Destination)

    def create_edge_from_selected_to(self, node):
        for selected_node in self.selected_nodes:
            self.add_edge(selected_node, node)

    def create_edge_to_selected_from(self, node):
        for selected_node in self.selected_nodes:
            self.add_edge(node, selected_node)

    def update_node_edges(self, node):
        for neighbor_node in nx.all_neighbors(self.graph, node):
            def update_edge_shape(from_node, to_node):
                edge = self.get_edge_object((from_node, to_node))
                if edge is not None:
                    edge.update_shape(from_node, to_node)

            update_edge_shape(node, neighbor_node)
            update_edge_shape(neighbor_node, node)

    def select_node(self, node):
        if node is None or node in self.selected_nodes:
            return False
        self.selected_nodes.append(node)
        node.set_as_selected(is_selected=True)
        self.update_node_edges(node)
        return True

    def deselect_node(self, node):
        if node is None or node not in self.selected_nodes:
            return False
        self.selected_nodes.remove(node)
        node.set_as_selected(is_selected=False)
        self.update_node_edges(node)
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
        for node in self.selected_nodes:
            self.deselect_node(node)
        self.selected_nodes = []

    def get_edge_cost(self, from_node, to_node):
        return self.get_node_distance(from_node, to_node)

    def add_node(self, node):
        if node is None or not self.is_valid_node_position(node.get_position()):
            return False
        self.graph.add_node(node)
        return True

    def move_node(self, node, position):
        if node is None or not self.is_valid_node_position(node.get_position()):
            return False
        node.set_position(position)
        self.update_node_edges(node)

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
        if from_node is None or to_node is None or from_node == to_node:
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
        try:
            return self.graph[edge[0]][edge[1]]['object']
        except KeyError:
            return None

    # TODO: batched rendering of primitives
    def draw(self, batch=None):

        def draw_selected_nodes():
            def draw_node_as_selected(node):
                color = config.world.selected_node_color
                radius = node.get_radius() + config.world.selected_radius_increase
                circle = lib.Circle(position=node.get_position(), radius=radius, color=color)
                circle.draw()
            for selected_node in self.selected_nodes:
                draw_node_as_selected(selected_node)
        draw_selected_nodes()

        def draw_nodes():
            is_reading_data = True
            for node in self.graph.nodes(data=is_reading_data):
                node_instance = node
                if is_reading_data:
                    node_instance = node[0]
                # node_instance.draw(batch)
                if node_instance in self.selected_nodes:
                    node_instance.draw(radius_offset=config.world.selected_radius_decrease)
                else:
                    node_instance.draw()
        draw_nodes()

        def draw_edges():
            for edge in self.graph.edges(data=True):
                self.get_edge_object(edge).draw(batch)
        draw_edges()

    def update(self, dt):
        pass

