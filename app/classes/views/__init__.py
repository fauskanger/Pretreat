import math
import sys
import csv
from itertools import count


class View:
    def __init__(self, name):
        self.name = name

    def run(self):
        pass


import pyglet
from app.classes.windows.main_window import MainWindow
from app.classes.windows.test_window import TestWindow


class PygletWindowView(View):
    def __init__(self):
        super().__init__("Pyglet window view")
        if config.test:
            self.window = TestWindow()
        else:
            self.window = MainWindow()

    def run(self):
        print("Starting window: {0}".format(self.window.window_name))
        self.window.run_update()
        pyglet.app.run()


from app.config import config, seeded_random as random
from app.pythomas import pythomas as lib
from app.classes.graph.navigation_graph import NavigationGraph, Node
from app.classes.graph.analyzer import Analyzer
from app.classes.graph.agent import GoodAgent
from pymongo import MongoClient
import copy


class WalkDataKey:
    def __init__(self):
        self.n_rows = -1
        self.n_cols = -1
        self.walk_i = -1
        self.path_i = -1
        self.path_len = -1
        self.death = False
        self.success = False

    def complete(self):
        return self.death or self.success

    def __repr__(self):
        s = '{}\t\t{}\t\t{}\t\t\t{}\t\t\t{}\t\t{}'\
            .format(*self.csv_line())
        return s

    def key(self):
        return str(self)

    def csv_line(self):
        return [self.n_rows, self.n_cols, self.path_i, self.path_len, self.success, self.death]

class ConsoleView(View):
    class StatsNames:
        death = 'death'
        success = 'success'

    def __init__(self):
        super().__init__("Console View")
        self.nav_graph = NavigationGraph()
        self.nav_graph.set_no_visuals(no_visuals=True)
        self.running = True
        self.client = MongoClient()
        self.db = self.client.pretreat
        self.stats_names = self.StatsNames
        self.walk_data_key = WalkDataKey()
        self.walk_keys = []
        # print('Collections: \n'.format(self.db.collection_names(include_system_collections=False)))

        self.stats = dict()

    def run(self):
        print("Starting {}".format(self.name))
        n_rows_min, n_cols_min = 5, 5
        n_rows_max, n_cols_max = 20, 20
        for n_rows in range(n_rows_min, n_rows_max, 3):
            self.walk_data_key.n_rows = n_rows
            for n_cols in range(n_cols_min, n_cols_max, 3):
                self.walk_data_key.n_cols = n_cols
                self.run_repeated_walks(n_rows, n_cols)
        self.save_results()

    def write_csv(self, line, f):
        writer = csv.writer(f)
        writer.writerow(line)

    def save_results(self):
        def print_progress(ratio):
            sys.stdout.write("\rSaving to file.. Progress: {:.3f}%".format(ratio))
            sys.stdout.flush()

        used_keys = []
        # print('\n\tRows \tCols \tDistance \tPathLen \tSuccess \tDeath \tCount')
        with open('console_view_results.csv', 'w', newline='', encoding='utf-8') as f:
            self.write_csv(['sep=,'], f)
            self.write_csv('\n\tRows \tCols \tDistance \tPathLen \tSuccess \tDeath \tCount'.split(), f)
            ki = -1
            for walk_key in self.walk_keys:
                ki += 1
                key = walk_key.key()
                r_count = self.stats[key]
                if key not in used_keys:
                    line = walk_key.csv_line()
                    line.append(r_count)
                    self.write_csv(line, f)
                    print_progress(ki / len(self.walk_keys))
                    # print('\t{}\t{}'.format(walk_key, count))
                used_keys.append(key)

        keys = [key.key() for key in self.walk_keys]
        if any(key not in keys for key in self.stats.keys()):
            raise Exception('Something is very wrong.')

    def generate_new_grid(self, n_rows, n_cols):
        self.nav_graph.generate_viewless_grid(n_rows, n_cols, make_hex=False)

    def create_new_path(self):
        start_node, destination_node = random.sample(self.nav_graph.graph.nodes(), 2)
        self.nav_graph.set_start_node(start_node)
        self.nav_graph.set_destination_node(destination_node)
        self.nav_graph.pathfinder.update_to_new_path()
        return self.nav_graph.pathfinder.get_path_nodes()

    def create_until_path(self, n_rows, n_cols):
        # Create graph and path
        path_nodes = None
        while not path_nodes:
            self.nav_graph.clear()
            self.generate_new_grid(n_rows, n_cols)
            self.create_new_path()
            path_nodes = self.nav_graph.pathfinder.get_path_nodes()
        return path_nodes

    def get_fairest_n_evils(self, p_walk_ok=0.5):
        dimension = self.walk_data_key.n_rows * self.walk_data_key.n_cols
        path_len = self.walk_data_key.n_rows + self.walk_data_key.n_cols - 1
        n_evils = dimension * (1 + math.log(p_walk_ok)/path_len)
        return n_evils

    def run_repeated_walks(self, n_rows, n_cols):
        path_nodes = self.create_until_path(n_rows, n_cols)
        nodes = self.nav_graph.graph.nodes()
        self.walk_data_key.path_len = len(path_nodes)

        # Add waypoint for interest
        if len(nodes) > 2 and False:
            waypoint = nodes[int(len(nodes)/2)]
            self.nav_graph.pathfinder.add_waypoint(waypoint)

        ok = 0
        fail = 0
        walk_i = -1
        n_runs = 1000
        n_evil_steps = 10
        min_evils = 2
        max_evils = int(self.get_fairest_n_evils(p_walk_ok=0.5) * 1.1)
        if min_evils >= max_evils:
            max_evils = min_evils + 1
        step = int((max_evils - min_evils) / n_evil_steps)
        step = step if step >= 1 else 1
        for n_evils in range(min_evils, max_evils, step):
            walk_i += 1
            self.walk_data_key.walk_i = walk_i
            n_evils = min_evils + (max_evils-min_evils) * int(walk_i/n_runs)
            if self.perform_walk(nodes, walk_i, path_nodes, n_evils):
                ok += 1
            else:
                fail += 1
            if not walk_i < n_runs:
                break

    def perform_walk(self, nodes, walk_i, path_nodes, n_evils):
        # print('Path: {}'.format(path_nodes))

        # Add evil nodes
        start_node = path_nodes[0]
        evils = random.sample([node for node in nodes if node is not start_node], n_evils)

        # Iterate path nodes
        for path_i in range(0, len(path_nodes)):
            node = path_nodes[path_i]
            self.walk_data_key.path_i = path_i
            # print('Current: {}\nEvils: {}'.format(node, evils))
            new_evils = self.move_evils(evils)
            if any(evil is node for evil in evils):
                self.walk_collide(node, path_i, walk_i)
                return False
            # Update the new positions
            evils = new_evils
        self.walk_success(len(path_nodes), walk_i)
        return True

    def walk_success(self, path_index, walk_i):
        self.walk_data_key.success = True
        self.increment_stats_for_walk_data()
        # print(" >> {} - No collision! Success!".format(walk_i))

    def walk_collide(self, node, path_index, walk_i):
        self.walk_data_key.death = True
        self.increment_stats_for_walk_data()
        # print(" >> {} - Died on {}".format(walk_i, node))

    def increment_stats_for_walk_data(self):
        if not self.walk_data_key.complete():
            raise AttributeError('The key object does not describe a completed walk.')
        key = self.walk_data_key.key()
        try:
            self.stats[key] += 1
        except KeyError:
            self.stats[key] = 1
        # Save key
        self.walk_keys.append(copy.copy(self.walk_data_key))
        # Reset flags
        self.walk_data_key.death = False
        self.walk_data_key.success = False

    def move_evils(self, evils):
        i_evil = -1
        new_evils = []
        for evil in evils:
            i_evil += 1
            # Move evil (or stay)
            neighbors = self.nav_graph.graph.neighbors(evil)
            remaining_evils = evils[i_evil:] if i_evil < len(evils)-1 else []
            available_neighbors = [neighbor for neighbor in neighbors if neighbor not in evils[i_evil:]]
            new_evils.append(random.choice(available_neighbors + [evil]))
        return new_evils



