import pyglet
from pyglet.window import key, mouse

from app.config import config
from app.pythomas import pythomas as lib
from app.classes.graph.agent import SuperAgent
from app.classes.graph.navigation_graph import NavigationGraph, Node
from app.pythomas.pythomas import PygletLib as Plib


class BaseEventHandler:
    def __init__(self, window):
        self.window = window

    def on_key_press(self, symbol, modifiers):
        pass

    def on_key_release(self, symbol, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass


class BaseWindow:
    def __init__(self, outer_handler, window_name="Base Window", window_parameters=None):
        if window_parameters is None:
            window_parameters = BaseWindow.get_default_window_parameters()
        # super(BaseWindow, self).__init__(**window_parameters)
        self.window = pyglet.window.Window(**window_parameters)
        self.window_name = window_name
        self.outer_handler = outer_handler
        self.pressed_keys = key.KeyStateHandler()
        self.window.push_handlers(self.pressed_keys)
        self.window.push_handlers(self.outer_handler)

    def update(self, dt):
        pass

    def run_update(self):
        pyglet.clock.schedule_interval(self.update, 1.0/config.window.desired_fps)

    @staticmethod
    def get_default_window_parameters():
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screen = display.get_default_screen()

        template = pyglet.gl.Config(sample_buffers=1, samples=config.window.aa_samples)
        aa = "No"
        try:
            gl_config = screen.get_best_config(template)
        except pyglet.window.NoSuchConfigException:
            template = pyglet.gl.Config()
            gl_config = screen.get_best_config(template)
        else:
            aa = "Yes ({0}x{0})".format(gl_config.samples)

        # print('Display: {0}'.format(display))
        print('Screen: {0}'.format(screen))
        print('Anti-alias: {0}'.format(aa))

        def get_initial_window_size():
            if config.window.fullscreen:
                display_scale = 1
            else:
                display_scale = config.window.default_fraction_of_screen

            width = int(config.window.default_width)
            height = int(config.window.default_height)
            if config.window.is_fraction_of_screen:
                width = int(screen.width*display_scale)
                height = int(screen.height*display_scale)
            return height, width
        window_height, window_width = get_initial_window_size()
        return dict(caption=config.strings.title,
                    fullscreen=config.window.fullscreen,
                    resizable=config.window.resizable,
                    width=window_width,
                    height=window_height,
                    visible=False,
                    config=gl_config,
                    )


class MainWindow(BaseWindow):
    def __init__(self, outer_handler):
        super(MainWindow, self).__init__(outer_handler, "Main window")
        # self.push_handlers()
        self.nav_graph = NavigationGraph()
        # Create content
        self.text_label = pyglet.text.Label('Hello, world. Press F!',
                                            font_name='Times New Roman',
                                            font_size=self.window.height/10,
                                            x=self.window.width // 2, y=self.window.height // 2,
                                            anchor_x='center', anchor_y='center',
                                            color=(255, 0, 0, 255))
        self.altitude_image = pyglet.resource.image(lib.resource(config.strings.altitude_map))
        self.background_image = self.altitude_image  # pyglet.resource.image(lib.resource('bag/oasis2.png'))

        self.agent = SuperAgent()
        self.window.set_visible(True)
        if not self.window.fullscreen:
            self.window.set_size(config.window.default_width, config.window.default_height)
        self.window.push_handlers(self)
        self.draw_background = True
        self.accumulated_scroll_y = 0.0

        # Dragging of nodes:
        self.dragged_nodes = None
        self.dragged_node_start_positions = None
        self.drag_click_start = None

        # Press S/D then click
        self.set_path_end_on_click = False
        self.next_node_click_state = None

    def get_pixel(self, position, image=None):
        image = self.altitude_image if not image else image
        x, y = position
        x = int(x)
        y = int(y)

        raw = image.get_region(x, y, 1, 1).get_image_data()

        pformat = 'RGB'
        pitch = raw.width * len(pformat)
        pixels = raw.get_data(pformat, pitch)
        print(tuple([color for color in pixels]))

    def update(self, dt):
        self.agent.update(dt)
        self.nav_graph.update(dt)

    def on_draw(self):
        self.window.clear()
        if self.draw_background:
            self.background_image.blit(0, 0)

        def draw_graph():
            nav_batch = pyglet.graphics.Batch()
            self.nav_graph.draw(nav_batch)
            nav_batch.draw()
        draw_graph()
        # self.text_label.draw()
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
                    diff = lib.sum_points(self.get_invert_coordinates(self.drag_click_start), (x, y))
                    moved_pos = lib.sum_points(diff, start_pos)
                    self.nav_graph.move_node(node, moved_pos)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.MIDDLE:
            def reset_node_dragging():
                self.drag_click_start = None
                self.dragged_nodes = None
                self.dragged_node_start_positions = None
            reset_node_dragging()

    def on_mouse_press(self, x, y, button, modifiers):
        node = self.nav_graph.get_node_from_position((x, y))
        selected_nodes = self.nav_graph.get_selected_nodes()

        if button == mouse.MIDDLE:

            if node in selected_nodes:
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
                    self.nav_graph.add_node(Node(x, y))
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
                    self.nav_graph.add_node(Node(x, y))
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
        if symbol == key.B:
            self.draw_background = not self.draw_background
        if symbol == key.SPACE:
            self.nav_graph.start_pathfinding()
        if symbol == key.G:
            self.draw_graph_grid()
        if symbol == key.S or symbol == key.D:
            self.set_path_end_on_click = True
            self.next_node_click_state = None

    def on_resize(self, width, height):
        self.background_image.width = width
        self.background_image.height = height
        pass
