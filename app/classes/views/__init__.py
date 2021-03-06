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
        self.n_evils = -1

    def complete(self):
        return self.death or self.success

    def __repr__(self):
        s = '{}\t\t{}\t\t{}\t\t\t{}\t\t\t{}\t\t{}'\
            .format(*self.csv_line())
        return s

    def key(self):
        return str(self)

    def csv_line(self):
        return [self.n_rows, self.n_cols, self.path_i, self.n_evils, self.path_len, self.success, self.death]

class ConsoleView(View):
    class Strings:
        death = 'death'
        success = 'success'
        retreat = 'retreat'

    def __init__(self):
        super().__init__("Console View")
        self.nav_graph = NavigationGraph()
        self.nav_graph.set_no_visuals(no_visuals=True)
        self.running = True
        self.client = MongoClient()
        self.db = self.client.pretreat
        self.strings = self.Strings
        self.walk_data_key = WalkDataKey()
        self.walk_keys = []
        # print('Collections: \n'.format(self.db.collection_names(include_system_collections=False)))

        self.stats = dict()

    def run(self):
        print("Starting {}".format(self.name))
        n_rows_min, n_cols_min = 5, 5
        n_rows_max, n_cols_max = 20, 20
        rows_iter = [i for i in range(n_rows_min, n_rows_max, 3)]
        cols_iter = [i for i in range(n_cols_min, n_cols_max, 3)]
        row_i = -1
        for n_rows in rows_iter:
            row_i += 1
            self.walk_data_key.n_rows = n_rows
            col_i = -1
            for n_cols in cols_iter:
                col_i += 1

                def get_progress():
                    row_ratio = row_i/len(rows_iter)
                    col_ratio = col_i/len(cols_iter)
                    ratio_per_row = 1 / len(rows_iter)
                    ratio_per_col = 1 / len(cols_iter) * ratio_per_row
                    return row_ratio + col_ratio * ratio_per_row, ratio_per_col
                self.walk_data_key.n_cols = n_cols
                self.run_repeated_walks(n_rows, n_cols, get_progress)
        self.save_results()

    def run_repeated_walks(self, n_rows, n_cols, get_progress):
        path_nodes = self.create_until_path(n_rows, n_cols)
        nodes = self.nav_graph.graph.nodes()
        self.walk_data_key.path_len = len(path_nodes)

        # Add waypoint for interest
        if len(nodes) > 2 and False:
            waypoint = nodes[int(len(nodes)/2)]
            self.nav_graph.pathfinder.add_waypoint(waypoint)

        n_runs = 1000
        for walk_i in range(0, n_runs):
            progress, ratio_per_batch = get_progress()
            progress += walk_i / n_runs * ratio_per_batch
            self.print_progress(progress, 'Walking{}'.format(' .'*int(10*walk_i/n_runs)))
            self.walk_data_key.walk_i = walk_i
            self.walk_incremental_evils(path_nodes)

    def walk_incremental_evils(self, path_nodes):
        n_evil_steps = 10
        min_evils = 2
        max_evils = self.get_n_evils_so(p_walk_ok=0.5) + 1

        if min_evils + n_evil_steps > max_evils:
            max_evils = min_evils + n_evil_steps
        step = int((max_evils - min_evils) / n_evil_steps)
        step = step if step >= 1 else 1
        nodes = self.nav_graph.graph.nodes()
        for n_evils in range(min_evils, max_evils, step):
            self.walk_data_key.n_evils = n_evils
            # n_evils = min_evils + (max_evils-min_evils) * int(walk_i/n_runs)
            self.perform_walk(nodes, path_nodes, n_evils)

    def perform_walk(self, nodes, initial_path, n_evils):
        # print('Path: {}'.format(path_nodes))

        # Add evil nodes
        start_node = initial_path[0]
        evils = random.sample([node for node in nodes if node is not start_node], n_evils)
        path = None
        n_previous_steps = 0
        while True:
            path = path if path else initial_path
            complete = self.follow_path(path, evils)
            if complete:
                self.walk_data_key.path_len += n_previous_steps
                return
            path_i = self.walk_data_key.path_i
            current_node = path[path_i]
            n_previous_steps += path_i
            self.nav_graph.set_start_node(current_node)
            self.nav_graph.pathfinder.update_to_new_path()
            path = self.nav_graph.pathfinder.get_path_nodes()

    def follow_path(self, path_nodes, evils):
        # Iterate path nodes, returns True if complete, False if evil detected
        for path_i in range(0, len(path_nodes)):
            node = path_nodes[path_i]
            self.walk_data_key.path_i = path_i
            # print('Current: {}\nEvils: {}'.format(node, evils))
            moved_evils = self.move_evils(evils)
            if any(evil is node for evil in evils):
                self.walk_collide()
                return True
            next_node = path_nodes[path_i+1] if path_i < len(path_nodes)-1 else None
            if any(evil is next_node for evil in evils):
                return False
            # Update the new positions
            evils.clear()
            evils.extend(moved_evils)
        self.walk_success()
        return True

    def walk_success(self):
        self.walk_data_key.success = True
        self.increment_stats_for_walk_data()
        # print(" >> {} - No collision! Success!".format(walk_i))

    def walk_collide(self):
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
            # remaining_evils = evils[i_evil:] if i_evil < len(evils)-1 else []
            available_neighbors = [neighbor for neighbor in neighbors if neighbor not in evils[i_evil:]]
            new_evils.append(random.choice(available_neighbors + [evil]))
        return new_evils

    def print_progress(self, ratio, text):
        sys.stdout.write("\rProgress: {:.3f}% - {}".format(ratio*100, text))
        sys.stdout.flush()

    def save_results(self):
        used_keys = []
        # print('\n\tRows \tCols \tDistance \tPathLen \tSuccess \tDeath \tCount')
        with open('console_view_results.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['sep=,'])
            writer.writerow('\n\tRows \tCols \tDistance \tnEvils \tPathLen \tSuccess \tDeath \tCount'.split())
            ki = -1
            for walk_key in self.walk_keys:
                ki += 1
                key = walk_key.key()
                r_count = self.stats[key]
                if key not in used_keys:
                    line = walk_key.csv_line()
                    line.append(r_count)
                    writer.writerow(line)
                    # print('\t{}\t{}'.format(walk_key, count))
                self.print_progress(ki / len(self.walk_keys), 'Saving to file..')
                used_keys.append(key)

        keys = [key.key() for key in self.walk_keys]
        if any(key not in keys for key in self.stats.keys()):
            raise Exception('Something is very wrong.')

    def generate_new_grid(self, n_rows, n_cols):
        print('New grid: {} x {}'.format(n_rows, n_cols))
        self.nav_graph.generate_viewless_grid(n_rows, n_cols, make_hex=False)

    def create_until_path(self, n_rows, n_cols):
        # Create graph until and path can be found
        path_nodes = None
        while not path_nodes:
            self.nav_graph.clear()
            self.generate_new_grid(n_rows, n_cols)
            self.create_new_path()
            path_nodes = self.nav_graph.pathfinder.get_path_nodes()
        return path_nodes

    def create_new_path(self):
        # start_node, destination_node = random.sample(self.nav_graph.graph.nodes(), 2)
        nodes = self.nav_graph.graph.nodes()
        start_node, destination_node = nodes[0], nodes[-1]
        self.nav_graph.set_start_node(start_node)
        self.nav_graph.set_destination_node(destination_node)
        self.nav_graph.pathfinder.update_to_new_path()
        return self.nav_graph.pathfinder.get_path_nodes()

    def get_n_evils_so(self, p_walk_ok=0.5):
        dimension = self.walk_data_key.n_rows * self.walk_data_key.n_cols
        path_len = self.walk_data_key.n_rows + self.walk_data_key.n_cols - 1
        n_evils = dimension * (1 + math.log(p_walk_ok)/path_len)
        return int(n_evils)



