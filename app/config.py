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