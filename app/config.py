from app.pythomas.colors import colors


class Configurations():
    class Strings():
        class Events():
            def __init__(self):
                self.on_path_update = 'on_path_update'

        def __init__(self):
            self.title = 'My Test Application'
            self.resource_path = 'app/resources'
            self.sqlite3_filename = 'db/sqlite3_pretreat.db'
            self.plot_save_filename = "weighted_graph.png"
            self.icon_folder = 'icons/map1'
            self.icons_paths = []  # Will be populated below

            self.altitude_map = 'altitude_map.png'

            self.error_prefix = ' >>> '

            self.pos = 'pos'
            self.weight = 'weight'
            self.label = 'label'
            self.altitude = 'altitude'

            self.events = self.Events()

    class Window():
        def __init__(self):
            self.resizable = True
            self.fullscreen = False
            self.is_fraction_of_screen = False
            self.default_fraction_of_screen = 1 / 2
            self.default_width = 1280
            self.default_height = 720
            self.desired_fps = 60.0
            self.aa_samples = 2

    class World():
        class ZIndexes():
            def __init__(self):
                self.background = -10000
                self.path = -1000
                self.node = -100
                self.node_path = self.node-10

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

            def bt709_relative_luminance(rgb_color, rgb_max=255):
                # used to normalize output in range [0, 1]
                m = rgb_max
                r, g, b = rgb_color
                return 0.2126*r/m + 0.7152*g/m + 0.0722*b/m

            self.color_mode = 'c3B'  # 'c4B' to include alpha, but some parts explicitly expect 3-tuples
            self.vertex_mode = 'v2f'
            self.node_color = (0xCC, 0x99, 0x66)
            node_color_is_dark = bt709_relative_luminance(self. node_color) < 0.5
            self.node_label_color = colors.white if node_color_is_dark else colors.black
            self.edge_color = self.node_color
            self.edge_in_node_color = colors.gray_66
            self.edge_triangle_color = self.node_color
            self.selected_node_color = colors.extra.orange_red
            self.node_occupied_color = colors.red

            self.path_edge_color = colors.extra.crimson
            self.path_node_color = self.path_edge_color
            self.start_node_color = colors.cyan
            self.destination_node_color = colors.magenta

            self.node_order_index = 1
            self.node_radius = 20
            self.selected_radius_increase = max(0.3 * self.node_radius, 5)  # For the outer circle radius
            self.selected_radius_decrease = 0.61 * self.selected_radius_increase  # How much the node circle will shrink
            self.path_radius_increase = self.selected_radius_increase
            self.node_padding = 1/3 * self.node_radius

            self.edge_thickness = self.node_radius/7
            self.edge_end_radius = self.edge_thickness
            self.edge_triangles_width = 4*self.edge_thickness
            self.edge_lane_offset = max(self.edge_thickness, self.edge_triangles_width)*0.4
            self.adjust_edge_to_selection = True

            self.default_rand_seed = 13
            self.blocked_node_edge_cost = float("inf")
            self.edge_refresh_interval = 1/30
            self.pathfinder_refresh_interval = 1/2
            self.z_indexes = self.ZIndexes()

    def __init__(self):
        # Whether or not to run test window instead
        self.test = False
        self.strings = self.Strings()
        self.window = self.Window()
        self.world = self.World()
        self.colors = colors


config = Configurations()
global_string_values = config.strings

import random as original_random

seeded_random = original_random.Random()
seeded_random.seed(config.world.default_rand_seed)