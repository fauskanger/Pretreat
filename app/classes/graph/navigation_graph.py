import math
import pyglet

from heapq import heappush, heappop
import networkx as nx

from app.config import config, seeded_random as random
from app.pythomas import pythomas as lib
from app.classes.graph.node import Node
from app.classes.graph.edge import Edge
from app.classes.graph.pathfinder import AStarPathfinder, CustomPathfinder
from app.classes.graph.agency import Agency
from app.classes.graph.pretreat_pathfinder import PretreatPathfinder


class NavigationGraph():
    def __init__(self):
        self.graph = nx.DiGraph()
        # self.selected_nodes = []
        self.altitude_image = pyglet.resource.image(lib.resource(config.strings.altitude_map))
        self.pathfinder = AStarPathfinder(self.graph, self.altitude_function)
        self.pathfinder.push_handlers(self)
        self.node_positions_dirty = False   # Node positions
        self.node_set_dirty = False         # Adding/Removing nodes
        self.node_selected_dirty = False    # Selected/deselected nodes
        self.render_batch = pyglet.graphics.Batch()
        self.edge_update_timer = 0
        self.agency = Agency(self)
        self.update_edge_on_next = []

    def get_altitude(self, position):
        min_altitude = config.world.min_altitude
        max_altitude = config.world.max_altitude
        # pixel_value = 1 - lib.get_pixel(self.altitude_image, position)[0]/255
        # altitude = (max_altitude - min_altitude) * pixel_value + min_altitude
        # return altitude
        return min_altitude

    def altitude_function(self, from_node, to_node):
        to_alt = self.get_altitude(to_node.get_position())
        from_alt = self.get_altitude(from_node.get_position())
        return to_alt - from_alt

    def create_node(self, position):
        x, y = position
        return Node(x, y, altitude=self.get_altitude(position))

    def on_path_update(self, path):
        # print("Path updated. {0}".format([node.label for node in path.get_node_list()]))
        self.refresh_path_components()

    def refresh_path_components(self):
        self.set_path_components()
        self.redraw_all_edges()
        self.refresh_all_nodes()

    def set_path_components(self):
        self.set_path_edges()
        self.set_path_nodes()

    def set_path_edges(self):
        path_edge_tuples = self.pathfinder.get_path_edges()
        for edge_tuple in self.graph.edges():
                edge = self.get_edge_object(edge_tuple)
                is_path_edge = edge_tuple in path_edge_tuples
                edge.set_as_path_edge(is_path_edge=is_path_edge)

    def set_path_nodes(self):
        path_nodes = self.pathfinder.get_path_nodes()
        for node in self.graph.nodes():
            is_path_node = node in path_nodes
            node.set_as_path_node(is_path_node=is_path_node)

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

    def create_random_path(self, only_if_none=False):
        if not only_if_none or not self.pathfinder.get_path_nodes():
            # if not self.graph.nodes():
            #     self.generate_grid_with_margin(5, 5, 100, 400, 300)
            count = 0
            while not self.pathfinder.get_path_nodes() and count < 5:
                count += 1
                start, destination = random.sample(self.graph.nodes(), 2)
                self.set_start_node(start)
                self.set_destination_node(destination)
                self.pathfinder.update_to_new_path()

    def create_edge_from_selected_to(self, node):
        for selected_node in self.get_selected_nodes():
            self.add_edge(selected_node, node)

    def create_edge_to_selected_from(self, node):
        for selected_node in self.get_selected_nodes():
            self.add_edge(node, selected_node)

    def update_node_edges(self, node):
        if not node in self.graph:
            return
        for neighbor_node in nx.all_neighbors(self.graph, node):
            def update_edge_weight(from_node, to_node):
                if self.graph.has_edge(from_node, to_node):
                    cost = self.pathfinder.calculate_edge_cost(from_node, to_node)
                    # Default weight-attribute in NetworkX, used by e.g. AStarPathfinder
                    self.graph[from_node][to_node][config.strings.weight] = cost

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
        self.node_selected_dirty = True
        self.redraw_edges(node)
        return added

    def deselect_node(self, node):
        if not node:
            return False
        # removed = lib.try_remove(self.selected_nodes, node)
        removed = node.is_selected()
        node.set_as_selected(selected=False)
        self.node_selected_dirty = True
        self.redraw_edges(node)
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
            self.deselect_node(node)

    def add_node(self, node):
        if node is None or not self.is_valid_node_position(node.get_position()):
            return False
        self.graph.add_node(node)
        self.node_set_dirty = True
        self.update_node_labels()
        return True

    # def add_nodes_from(self, list_of_nodes):
    #     self.graph.add_nodes_from(list_of_nodes)
    #     self.node_set_dirty = True
    #     self.update_node_labels()

    def move_node(self, node, dx, dy):
        x, y = node.get_position()
        new_position = x+dx, y+dy
        if node is None or not self.is_valid_node_position(new_position, node_exceptions=[node]):
            return False

        node.move(dx, dy)
        self.redraw_edges(node)
        self.node_positions_dirty = True

    def redraw_edges(self, node):
        if node not in self.update_edge_on_next:
            self.update_edge_on_next.append(node)

    def redraw_all_edges(self):
        for node in self.graph.nodes():
            self.update_edge_on_next.append(node)

    def refresh_all_nodes(self):
        for node in self.graph.nodes():
            if node is self.pathfinder.start_node:
                node.set_state(Node.State.Start)
            elif node is self.pathfinder.destination_node:
                node.set_state(Node.State.Destination)
            else:
                node.set_state(Node.State.Default)

    def set_node_position(self, node, new_position):
        dx, dy = lib.subtract_points(new_position, node.get_position())
        self.move_node(node, dx, dy)

    def remove_node(self, node):
        if node is None:
            return False
        self.deselect_node(node)
        self.remove_all_node_edges(node)
        try:
            self.graph.remove_node(node)
        except nx.NetworkXError:
            return False
        else:
            node.delete()
            self.node_set_dirty = True
            if node in self.update_edge_on_next:
                self.update_edge_on_next.remove(node)
            if self.pathfinder:
                self.pathfinder.clear_node(node)
            self.update_node_labels()
            return True

    def add_edge(self, from_node, to_node):
        if from_node is None or to_node is None or from_node == to_node:
            return False
        if self.graph.has_edge(from_node, to_node):
            return False
        weight = self.pathfinder.calculate_edge_cost(from_node, to_node)
        try:
            self.graph.add_edge(from_node, to_node, weight=weight, object=Edge(from_node, to_node))
        except nx.NetworkXError:
            return False
        else:
            self.node_set_dirty = True
            return True

    def remove_edge(self, from_node, to_node):
        edge = self.get_edge_object((from_node, to_node))
        if edge:
            edge.delete()
        if from_node is None or to_node is None:
            return False
        try:
            self.graph.remove_edge(from_node, to_node)
        except nx.NetworkXError:
            return False
        else:
            self.node_set_dirty = True
            return True

    def remove_edges_from_many(self, to_node, from_nodes):
        for from_node in from_nodes:
            self.remove_edge(from_node, to_node)

    def remove_edges_to_many(self, from_node, to_nodes):
        for to_node in to_nodes:
            self.remove_edge(from_node, to_node)

    def remove_all_node_edges(self, node):
        for u, v in self.graph.edges():
            if u is node or v is node:
                self.remove_edge(u, v)

    def get_edge_object(self, edge):
        # Works with both (u, v)-tuples and edges from nx.G.edges()
        if edge is None:
            return None
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

        unused_labels = [label for label in all_labels if label not in used_labels]

        for i in range(len(unlabeled_nodes)):
            node = unlabeled_nodes[i]
            label = unused_labels[i]
            node.set_label(label)

    # TODO: batched rendering of primitives
    def draw(self):
        selected_nodes = self.get_selected_nodes()
        path_edges = self.pathfinder.get_path_edges()
        batch = self.render_batch

        def draw_path():
            if self.pathfinder:
                self.pathfinder.draw(batch)
        draw_path()

        def draw_edges():
            for edge in self.graph.edges(data=True):
                if edge in path_edges:
                    pass
                else:
                    self.get_edge_object(edge).draw(batch)
        draw_edges()

        def draw_selected_nodes():
            for selected_node in selected_nodes:
                selected_node.draw_selected_indicator(batch)
        draw_selected_nodes()

        def draw_nodes():
            is_reading_data = True
            for node in self.graph.nodes(data=is_reading_data):
                node_instance = node
                if is_reading_data:
                    node_instance = node[0]

                node_instance.draw_path(batch)
                if node_instance in selected_nodes:
                    node_instance.draw(radius_offset=config.world.selected_radius_decrease, batch=batch)
                else:
                    node_instance.draw(batch=batch)
        draw_nodes()

        self.render_batch.draw()

        def draw_node_labels():
            for node in self.graph.nodes():
                node.draw_label()
        draw_node_labels()

    def update(self, dt):
        self.update_nodes(dt)
        self.update_edges(dt)
        self.update_path(dt)
        self.agency.update(dt)

        self.node_positions_dirty = False
        self.node_set_dirty = False
        self.node_selected_dirty = False

    def add_occupant(self, node, occupant=True):
        if not node.has_occupants() and node.state is Node.State.Default:
            node.add_occupant(occupant)
            self.node_set_dirty = True
            # self.update_node_edges(node)
            self.pathfinder.notify_node_change(node)

    def remove_occupant(self, node, occupant=True, remove_all=False):
        if node.has_occupants():
            if remove_all:
                node.remove_all_occupants()
            else:
                node.remove_occupant(occupant)
            self.node_set_dirty = True
            # self.update_node_edges(node)
            self.pathfinder.notify_node_change(node)

    def update_nodes(self, dt):
        for node in self.graph.nodes():
            node.update(dt)

    def update_edges(self, dt):
        self.edge_update_timer += dt
        if self.edge_update_timer > config.world.edge_refresh_interval:
            for node in self.update_edge_on_next:
                self.update_node_edges(node)
            self.edge_update_timer = 0
            self.update_edge_on_next.clear()

    def update_path(self, dt):
        must_reevaluate_path = self.node_positions_dirty or self.node_set_dirty
        # must_refresh_path = self.node_selected_dirty
        if self.pathfinder and must_reevaluate_path:
            self.pathfinder.refresh_path()
        self.pathfinder.update(dt)

    def start_pathfinding(self):
        self.pathfinder.start()

    def refresh_path_radius(self):
        pass

    def find_nearest_nodes(self, node, number_of_hits=1, candidates=None, exceptions=()):
        candidates = self.graph.nodes() if not candidates else candidates
        candidates = [candidate for candidate in candidates if candidate != node and candidate not in exceptions]

        def key_function(candidate):
            return NavigationGraph.get_node_distance(candidate, node)

        sorted_list = sorted(candidates, key=key_function)
        return sorted_list[:number_of_hits]

    def clear(self):
        nodes = self.graph.nodes()
        for node in nodes:
            self.remove_node(node)
        print("All nodes and edges removed.")

    def generate_grid_with_margin(self, rows, cols, margin, width, height, make_hex=True):
        if margin > 1:
            margin = 1
        if margin < 0:
            margin = 0
        w, h = width, height
        self.generate_grid(rows, cols, (1-margin)*w, (1-margin)*h, (margin*w, margin*h), make_hex)

    def generate_grid(self, row_count, col_count, max_width, max_height, start_pos=(0, 0), make_hex=True):
        nodes = []
        start_x, start_y = start_pos
        width = max_width-start_x
        height = max_height-start_y
        row_step = height/(row_count-1)
        col_step = width/(col_count-1)
        hex_offset = row_step/2 if make_hex else 0
        for row_i in range(row_count):
            odd = True
            for col_i in range(col_count):
                x = col_i * col_step
                y = row_i * row_step
                x, y = lib.sum_points((x, y), start_pos)
                if odd:
                    y += hex_offset
                if not (odd and make_hex) or row_i < row_count - 1:
                    node = self.create_node((x, y))
                    nodes.append(node)
                    self.add_node(node)
                odd = not odd

        w2 = col_step * col_step
        h2 = row_step * row_step
        if w2 < h2:
            w2 /= 4
        else:
            h2 /= 4
        max_near_distance = math.sqrt(w2 + h2) + 5

        random.shuffle(nodes)

        for node in nodes:
            def is_near(candidate):
                return NavigationGraph.get_node_distance(candidate, node) < max_near_distance
            neighbors = [candidate for candidate in nodes if is_near(candidate)]
            max_degree = 6
            for neighbor in neighbors:
                degree = self.graph.degree(neighbor)
                if degree < max_degree:
                    val = random.random()*100
                    if val > degree/max_degree*75:
                        self.add_edge(neighbor, node)
                        self.add_edge(node, neighbor)

    def neighbors_of(self, node):
        try:
            return self.graph.neighbors(node)
        except nx.exception.NetworkXError:
            return []

    def get_random_neighbor(self, from_node, include_from=True, node_filter_callback=None):
        if not from_node:
            return None
        candidates = self.neighbors_of(from_node)
        if include_from:
            candidates.append(from_node)
        if node_filter_callback:
            candidates = [node for node in candidates if node_filter_callback(node)]
            if not candidates:
                return None
        return random.choice(candidates)

