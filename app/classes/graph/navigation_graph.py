import math

import networkx as nx

from app.config import config
from app.pythomas import pythomas as lib
from app.classes.graph.node import Node
from app.classes.graph.edge import Edge
from app.classes.graph.pathfinder import AStarPathfinder
from app.classes.graph.pretreat_pathfinder import PretreatPathfinder


class NavigationGraph():
    def __init__(self):
        self.graph = nx.DiGraph()
        # self.selected_nodes = []
        self.pathfinder = PretreatPathfinder(self.graph)
        self.pathfinder.push_handlers(self)
        self.node_positions_dirty = False
        self.node_set_dirty = False
        self.select_dirty = False

    def on_path_update(self, path):
        # print("Path updated. {0}".format([node.label for node in path.get_node_list()]))
        path_edge_tuples = [] if not path else path.get_edge_list()
        for edge_tuple in self.graph.edges():
                edge = self.get_edge_object(edge_tuple)
                is_path_edge = edge_tuple in path_edge_tuples
                edge.set_as_path_edge(is_path_edge=is_path_edge)

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
            def update_edge_weight(from_node, to_node):
                cost = self.pathfinder.get_edge_cost(from_node, to_node)
                if self.graph.has_edge(from_node, to_node):
                    self.graph[from_node][to_node][config.strings.wgt] = cost

            def update_edge_shape(from_node, to_node):
                edge = self.get_edge_object((from_node, to_node))
                if edge:
                    edge.update_shape()

            update_edge_weight(node, neighbor_node)
            update_edge_weight(neighbor_node, node)
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
        self.select_dirty = True
        self.update_node_edges(node)
        return added

    def deselect_node(self, node):
        if not node:
            return False
        # removed = lib.try_remove(self.selected_nodes, node)
        removed = node.is_selected()
        node.set_as_selected(selected=False)
        self.select_dirty = True
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
            # print("Remove selection from node: {0}".format(removed))

    def add_node(self, node):
        if node is None or not self.is_valid_node_position(node.get_position()):
            return False
        self.graph.add_node(node)
        self.node_set_dirty = True
        self.update_node_labels()
        return True

    def move_node(self, node, position):
        if node is None or not self.is_valid_node_position(position, node_exceptions=[node]):
            return False

        node.set_position(position)
        self.node_positions_dirty = True
        self.update_node_edges(node)

    def remove_node(self, node):
        if node is None:
            return False
        self.deselect_node(node)
        self.remove_all_node_edges(node)
        try:
            self.graph.remove_node(node)
            self.node_set_dirty = True
            if self.pathfinder:
                self.pathfinder.clear_node(node)
            self.update_node_labels()
            return True
        except nx.NetworkXError:
            return False

    def add_edge(self, from_node, to_node):
        if from_node is None or to_node is None or from_node == to_node:
            return False
        try:
            weight = self.pathfinder.get_edge_cost(from_node, to_node)
            self.graph.add_edge(from_node, to_node, weight=weight, object=Edge(from_node, to_node))
            self.node_set_dirty = True
            return True
        except nx.NetworkXError:
            return False

    def remove_edge(self, from_node, to_node):
        if from_node is None or to_node is None:
            return False
        try:
            self.graph.remove_edge(from_node, to_node)
            self.node_set_dirty = True
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

    def update_node_labels(self):
        count = self.graph.number_of_nodes()
        all_labels = [str(i) for i in range(1, count+1)]
        used_labels = []
        unlabeled_nodes = []
        for node in self.graph.nodes():
            if node.label and int(node.label) <= count:
                used_labels.append(node.label)
            else:
                unlabeled_nodes.append(node)

        unused_labels = [str(label) for label in all_labels if str(label) not in used_labels]

        for i in range(len(unlabeled_nodes)):
            node = unlabeled_nodes[i]
            label = unused_labels[i]
            node.set_label(label)

    # TODO: batched rendering of primitives
    def draw(self, batch=None):
        selected_nodes = self.get_selected_nodes()
        path_edges = self.pathfinder.get_path_edges()

        def draw_path():
            if self.pathfinder:
                self.pathfinder.draw()
        draw_path()

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
                if edge in path_edges:
                    pass
                else:
                    self.get_edge_object(edge).draw(batch)
        draw_edges()

        def draw_node_labels():
            for node in self.graph.nodes():
                node.draw_label()
        draw_node_labels()

    def update(self, dt):
        any_dirty = self.node_positions_dirty or self.node_set_dirty or self.select_dirty

        if self.pathfinder and any_dirty:
            self.pathfinder.update_to_new_path()
        else:
            self.pathfinder.update(dt)

        self.node_positions_dirty = False
        self.node_set_dirty = False
        self.select_dirty = False

    def start_pathfinding(self):
        self.update_path()

    def update_path(self):
        if self.pathfinder:
            self.pathfinder.update_to_new_path()
