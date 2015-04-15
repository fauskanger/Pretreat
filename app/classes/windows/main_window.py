import pyglet
from pyglet.window import key, mouse

from app.config import config
from app.pythomas import pythomas as lib
from app.pythomas.pythomas import PygletLib as Plib
from app.classes.windows.base_window import BaseWindow
from app.classes.graph.agent import SuperAgent
from app.classes.graph.navigation_graph import NavigationGraph, Node
from app.classes.graph.analyzer import Analyzer


class MainWindow(BaseWindow):
    def __init__(self, outer_handler=None):
        super(MainWindow, self).__init__("Main window", outer_handler)
        # self.push_handlers()
        self.nav_graph = NavigationGraph()
        self.analyzer = Analyzer(self.nav_graph)

        self.altitude_image = self.nav_graph.altitude_image
        self.background_image = self.altitude_image

        self.agent = SuperAgent()
        self.window.set_visible(True)
        if not self.window.fullscreen:
            self.window.set_size(config.window.default_width, config.window.default_height)
        self.draw_background = True
        self.accumulated_scroll_y = 0.0

        # Dragging of nodes:
        self.dragged_nodes = None
        self.dragged_node_start_positions = None
        self.drag_click_start = None

        # Press S/D then click to set Start/Destination node
        self.set_path_end_on_click = False
        self.next_node_click_state = None

    def update(self, dt):
        self.agent.update(dt)
        self.nav_graph.update(dt)

    def on_draw(self):
        self.window.clear()
        if self.draw_background:
            self.background_image.blit(0, 0)

        def draw_graph():
            self.nav_graph.draw()
        draw_graph()
        if self.agent.state != self.agent.State.Idle:
            self.agent.draw()

    def draw_graph_grid(self):
        start_label = destination_label = None
        if self.nav_graph.pathfinder:
            if self.nav_graph.pathfinder.start_node:
                start_label = self.nav_graph.pathfinder.start_node.label
            if self.nav_graph.pathfinder.destination_node:
                destination_label = self.nav_graph.pathfinder.destination_node.label
        self.nav_graph.clear()
        self.nav_graph.generate_grid_with_margin(8, 11, 0.1, self.window.width, self.window.height)
        for node in self.nav_graph.graph.nodes():
            if start_label and node.label == start_label:
                self.nav_graph.set_start_node(node)
            if destination_label and node.label == destination_label:
                self.nav_graph.set_destination_node(node)

    def analyze_path(self):
        expected_cost, base_cost, irreplaceables = self.analyzer.score_path()
        ratio = expected_cost/base_cost
        print("Initial cost, before blocking: {0}".format(base_cost))
        print("Expected cost, where possible: {0}".format(expected_cost))
        print("  => Ratio = {0} ({2}{1}%)".format(ratio, (ratio-1)*100, "-" if ratio < 1 else "+"))
        print("Irreplaceable nodes ({1}): {0}".
              format([node.label for node in irreplaceables], len(irreplaceables)))

    def on_mouse_motion(self, x, y, dx, dy):
        # cursor = self.window.get_system_mouse_cursor(self.window.CURSOR_CROSSHAIR)
        # self.window.set_mouse_cursor(cursor)
        pass

    def get_next_node_state_from_scroll(self, forward, node):
        if node is not None:
            states_count = len(list(Node.State))
            print("Current state: {1} Length: {0}".format(states_count, node.state))
            value = node.state.value if node.state else Node.State.Default.value
            value += 1 if forward else -1
            value = (value + states_count) % states_count
            print("Next state from scroll", value, Node.State(value))
            return Node.State(value)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        node = self.nav_graph.get_node_from_position((x, y))
        if node:
            self.accumulated_scroll_y += scroll_y
            if abs(self.accumulated_scroll_y) > 1:
                forward = self.accumulated_scroll_y > 0
                state = self.get_next_node_state_from_scroll(forward, node)
                if state is not None:
                    self.nav_graph.set_node_state(node, state)
                    print(node.state)
                self.accumulated_scroll_y = 0.0

    def get_invert_coordinates(self, point):
        return -point[0], -point[1]

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.MIDDLE:
            if self.dragged_nodes:
                for i in range(len(self.dragged_nodes)):
                    start_pos = self.dragged_node_start_positions[i]
                    node = self.dragged_nodes[i]
                    diff = lib.subtract_points((x, y), self.drag_click_start)
                    moved_pos = lib.sum_points(diff, start_pos)
                    self.nav_graph.set_node_position(node, moved_pos)
                    # self.nav_graph.update_node_edges(node)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.MIDDLE:
            def reset_node_dragging():
                self.drag_click_start = None
                self.dragged_nodes = None
                self.dragged_node_start_positions = None
            reset_node_dragging()

    def on_mouse_press(self, x, y, button, modifiers):
        position = x, y
        node = self.nav_graph.get_node_from_position((x, y))
        selected_nodes = self.nav_graph.get_selected_nodes()

        if button == mouse.MIDDLE:

            # if node in selected_nodes:
            def set_dragged_node():
                if self.dragged_nodes is None:
                    self.dragged_nodes = selected_nodes
                    self.drag_click_start = (x, y)
                    self.dragged_node_start_positions = []
                    for selected_node in self.dragged_nodes:
                        self.dragged_node_start_positions.append(selected_node.get_position())

            set_dragged_node()

        if button == mouse.LEFT:

            if self.set_path_end_on_click and self.next_node_click_state:
                self.nav_graph.set_node_state(node, self.next_node_click_state)
                self.next_node_click_state = None
                self.set_path_end_on_click = False
            elif Plib.is_ctrl_pressed(self.pressed_keys):
                self.nav_graph.toggle_select(node)
            elif Plib.is_alt_pressed(self.pressed_keys):
                self.nav_graph.remove_node(node)
            elif self.pressed_keys[key.S]:
                self.nav_graph.set_start_node(node)
                self.set_path_end_on_click = False  # Prevent next click from setting node to start
            elif self.pressed_keys[key.D]:
                self.nav_graph.set_destination_node(node)
                self.set_path_end_on_click = False  # Prevent next click from setting node to destination
            elif node:
                self.nav_graph.deselect_all_nodes()
                self.nav_graph.toggle_select(node)
            else:
                self.nav_graph.deselect_all_nodes()

        if button == mouse.RIGHT:

            if Plib.is_ctrl_pressed(self.pressed_keys):
                if not selected_nodes:
                    self.nav_graph.add_node(self.nav_graph.create_node(position))
                else:
                    if not Plib.is_shift_pressed(self.pressed_keys):
                        self.nav_graph.create_edge_from_selected_to(node)
                    else:
                        self.nav_graph.create_edge_to_selected_from(node)

            elif Plib.is_alt_pressed(self.pressed_keys):
                if not selected_nodes:
                    self.nav_graph.remove_node(node)
                else:
                    if not Plib.is_shift_pressed(self.pressed_keys):
                        self.nav_graph.remove_edges_from_many(node, selected_nodes)
                    else:
                        self.nav_graph.remove_edges_to_many(node, selected_nodes)
            else:

                if node is None:
                    self.nav_graph.add_node(self.nav_graph.create_node(position))
                else:
                    def all_selected_has_edge():
                        for selected_node in selected_nodes:
                            has_uv = self.nav_graph.graph.has_edge(selected_node, node)
                            has_vu = self.nav_graph.graph.has_edge(node, selected_node)
                            if not has_uv or not has_vu:
                                return False
                        return True
                    if not all_selected_has_edge():
                        self.nav_graph.create_edge_to_selected_from(node)
                        self.nav_graph.create_edge_from_selected_to(node)
                    else:
                        self.nav_graph.remove_edges_to_many(node, selected_nodes)
                        self.nav_graph.remove_edges_from_many(node, selected_nodes)

    def on_key_release(self, symbol, modifiers):
        if symbol == key.S:
            if self.set_path_end_on_click:
                self.next_node_click_state = Node.State.Start
        elif symbol == key.D:
            if self.set_path_end_on_click:
                self.next_node_click_state = Node.State.Destination
        else:
            self.set_path_end_on_click = False
            self.next_node_click_state = None

    def on_key_press(self, symbol, modifiers):
        if symbol == key.A:
            self.draw_background = not self.draw_background
        if symbol == key.SPACE:
            self.nav_graph.start_pathfinding()
        if symbol == key.G:
            self.draw_graph_grid()
        if symbol == key.S or symbol == key.D:
            self.set_path_end_on_click = True
            self.next_node_click_state = None
        if symbol == key.E:
            self.analyze_path()
        if symbol == key.B:
            for node in self.nav_graph.get_selected_nodes():
                if node.has_occupants():
                    self.nav_graph.unblock_node(node)
                else:
                    self.nav_graph.block_node(node)
        if symbol == key.C:
            path_edges = self.nav_graph.pathfinder.get_path_edges()
            self.nav_graph.pathfinder.waypoints.clear()
            self.nav_graph.set_node_to_default(self.nav_graph.pathfinder.start_node)
            self.nav_graph.set_node_to_default(self.nav_graph.pathfinder.destination_node)
            for u, v in path_edges:
                edge = self.nav_graph.get_edge_object((u, v))
                edge.set_as_path_edge(is_path_edge=False)
            self.nav_graph.pathfinder.update_to_new_path()
            self.nav_graph.refresh_path_components()
        if symbol == key.W:
            self.nav_graph.pathfinder.waypoints.clear()
            self.nav_graph.pathfinder.refresh_path()

    def on_resize(self, width, height):
        self.background_image.width = width
        self.background_image.height = height
        pass
