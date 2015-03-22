class Colors():
    def __init__(self):
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.cyan = (0, 255, 255)
        self.magenta = (255, 0, 255)
        self.yellow = (255, 255, 0)
        self.black = (0, 0, 0)

    @staticmethod
    def half_color(color):
        def half(color_value):
            return int(color_value/2)
        return tuple(half(cv) for cv in color)


class Configurations():

    class Strings():
        def __init__(self):
            self.title = 'My Test Application'
            self.resource_path = 'app/resources'
            self.plot_save_filename = "weighted_graph.png"
            self.icon_folder = 'icons/map1'
            self.icons_paths = []  # Will be populated below

            self.error_prefix = ' >>> '

            self.pos = 'pos'
            self.wgt = 'weight'
            self.label = 'label'
            self.altitude = 'altitude'

    class Window():
        def __init__(self):
            self.resizable = True
            self.fullscreen = False
            self.is_fraction_of_screen = False
            self.default_fraction_of_screen = 1/2
            self.default_width = 560
            self.default_height = 434
            self.desired_fps = 60.0

    class World():
        def __init__(self):
            self.size_x = 18
            self.size_y = 13
            self.start_x = 1
            self.start_y = 1

            self.col_num_a = 4
            self.padding = 3

            self.max_weight = 10
            self.min_weight = 1

            self.min_altitude = 1
            self.max_altitude = 100
            self.rand_altitude_factor = 0.3
            self.min_degree = 2
            self.max_degree = 2
            self.base_edge_chance = 1
            self.number_of_edge_types = 5

            self.color_mode = 'c3B'
            self.node_color = (255, 255, 255)
            self.selected_node_color = (0, 0, 0)
            self.node_order_index = 1

            self.node_radius = 20
            self.selected_radius_increase = 2  # For the outer circle radius
            self.selected_radius_decrease = 5  # How much the node circle will shrink

            self.default_rand_seed = 13

    def __init__(self):
        self.strings = self.Strings()
        self.window = self.Window()
        self.world = self.World()


config = Configurations()
global_string_values = config.strings

import random as original_random
seeded_random = original_random.Random()
seeded_random.seed(config.world.default_rand_seed)