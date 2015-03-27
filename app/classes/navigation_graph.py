import math
import pyglet
import networkx as nx
from enum import Enum

from app.config import config
from app.pythomas import pythomas as lib
from app.pythomas import shapes as shapelib
from app.classes.node import Node
from app.classes.edge import Edge
from app.classes.pathfinder import AStarPathfinder


class NavigationGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        # self.selected_nodes = []
        self.pathfinder = AStarPathfinder(self.graph)

    def get_selected_nodes(self):
        return [node for node in self.graph.nodes() if node.is_selected()]

    @staticmethod
    def get_node_distance(from_node, to_node):
        x = abs(from_node.x - to_node.x)
        y = abs(from_node.y - to_node.y)
        return math.sqrt(x * x + y * y)

    def is_valid_node_position(self, position, node_exceptions=None):
        for existing_node in self.graph.nodes():
            if node_exceptions and existing_node in node_exceptions:
                continue
            distance = lib.get_point_distance(existing_node.get_position(), position)
            if distance < existing_node.get_padded_radius()*2:
                return False
        return True

    def get_node_from_position(self, position):
        for node in self.graph.nodes():
            if lib.get_point_distance(position, node.get_position()) < node.get_radius():
                return node
        return None

    def _set_node_state(self, node, state):
        node.set_state(state)

    def set_node_state(self, node, state):
        if node:
            if state is Node.State.Start:
                self.set_start_node(node)
            elif state is Node.State.Destination:
                self.set_destination_node(node)
            elif state is Node.State.Default:
                self.set_node_to_default(node)

    def set_node_to_default(self, node):
        if node:
            self.pathfinder.clear_node(node)
            self._set_node_state(node, Node.State.Default)

    def set_start_node(self, node):
        if node and node != self.pathfinder.start_node:
            print("Start node: {0}".format(node.label))
            self.set_node_to_default(self.pathfinder.start_node)
            self.pathfinder.set_start_node(node)
            self._set_node_state(node, Node.State.Start)
        else:
            print("Nope! Cannot set start node: {0}, existing: {1}"
                  .format(node, self.pathfinder.start_node))

    def set_destination_node(self, node):
        if node and node != self.pathfinder.destination_node:
            print("Destination node: {0}".format(node.label))
            self.set_node_to_default(self.pathfinder.destination_node)
            self.pathfinder.set_destination_node(node)
            self._set_node_state(node, Node.State.Destination)
        else:
            print("Nope! Cannot set destination node: {0}, existing: {1}"
                  .format(node, self.pathfinder.destination_node))

    def create_edge_from_selected_to(self, node):
        for selected_node in self.get_selected_nodes():
            self.add_edge(selected_node, node)

    def create_edge_to_selected_from(self, node):
        for selected_node in self.get_selected_nodes():
            self.add_edge(node, selected_node)

    def update_node_edges(self, node):
        for neighbor_node in nx.all_neighbors(self.graph, node):
            def update_edge_shape(from_node, to_node):
                edge = self.get_edge_object((from_node, to_node))
                if edge is not None:
                    edge.update_shape()

            update_edge_shape(node, neighbor_node)
            update_edge_shape(neighbor_node, node)

    def toggle_select(self, node, compare=None):
        if node:
            if compare is None:
                compare = node.is_selected()
            if compare:
                self.deselect_node(node)
            else:
                self.select_node(node)

    def select_node(self, node):
        if not node:
            return False
        # added = lib.try_append(self.selected_nodes, node)
        added = not node.is_selected()
        node.set_as_selected(selected=True)
        self.update_node_edges(node)
        return added

    def deselect_node(self, node):
        if not node:
            return False
        # removed = lib.try_remove(self.selected_nodes, node)
        removed = node.is_selected()
        node.set_as_selected(selected=False)
        self.update_node_edges(node)
        return removed

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
        for node in self.get_selected_nodes():
            removed = self.deselect_node(node)
            print("Remove selection from node: {0}".format(removed))

    def get_edge_cost(self, from_node, to_node):
        return self.get_node_distance(from_node, to_node)

    def add_node(self, node):
        if node is None or not self.is_valid_node_position(node.get_position()):
            return False
        self.graph.add_node(node)
        return True

    def move_node(self, node, position):
        if node is None or not self.is_valid_node_position(position, node_exceptions=[node]):
            return False

        node.set_position(position)
        self.update_node_edges(node)

    def remove_node(self, node):
        if node is None:
            return False
        self.deselect_node(node)
        self.remove_all_node_edges(node)
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

    def remove_all_node_edges(self, node):
        for u, v in self.graph.edges():
            if u == node or v == node:
                self.graph.remove_edge(u, v)

    def get_edge_object(self, edge):
        try:
            return self.graph[edge[0]][edge[1]]['object']
        except KeyError:
            return None

    def update_path_nodes(self, dt):
        if self.pathfinder.start_node:
            self.pathfinder.start_node.set_color(config.world.start_node_color)
        if self.pathfinder.destination_node:
            self.pathfinder.destination_node.set_color(config.world.destination_node_color)

    # TODO: batched rendering of primitives
    def draw(self, batch=None):
        selected_nodes = self.get_selected_nodes()

        def draw_selected_nodes():
            def draw_node_as_selected(node):
                node.draw_selected_indicator()
            for selected_node in selected_nodes:
                draw_node_as_selected(selected_node)
        draw_selected_nodes()

        def draw_nodes():
            is_reading_data = True
            for node in self.graph.nodes(data=is_reading_data):
                node_instance = node
                if is_reading_data:
                    node_instance = node[0]

                if node_instance in selected_nodes:
                    node_instance.draw(radius_offset=config.world.selected_radius_decrease)
                else:
                    node_instance.draw()
        draw_nodes()

        def draw_edges():
            for edge in self.graph.edges(data=True):
                self.get_edge_object(edge).draw(batch)
        draw_edges()

    def update(self, dt):
        self.update_path_nodes(dt)
        pass
