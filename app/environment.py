import math
import networkx as nx
import matplotlib.pyplot as plt

from app.config import config, seeded_random as random, global_string_values as strings


def error(message):
    print("{0}{1}".format(strings.error_prefix, message))


class Node():
    def __init__(self, x, y, altitude, content=None):
        self.x = int(x)
        self.y = int(y)
        self.label = "{0},{1}".format(x, y)
        self.altitude = altitude
        self.content = content

    def get_position(self):
        return self.x, self.y


class GraphGenerator():

    def __init__(self):
        print("Created GraphGenerator")

        self.altitudes_above_upper_bound = False
        self.altitudes_below_lower_bound = False

    def reset(self):
        self.altitudes_above_upper_bound = False
        self.altitudes_below_lower_bound = False

    def is_altitudes_within_bounds(self):
        return not (self.altitudes_above_upper_bound or self.altitudes_below_lower_bound)

    def create_node_altitude_from_node(self, node, graph):
        node_pos = graph.node[node][strings.pos]
        return self.create_node_altitude_from_pos(node_pos[0], node_pos[1])

    def create_node_altitude_from_pos(self, node_x, node_y):
        # Normalize into range [0, 1]
        x = node_x / config.world.size_x
        y = node_y / config.world.size_y
        max_normalized_position = 1/2  # 1/2 * 1/2 + 1/2 * 1/2

        # Create altitude value from normalized position
        normalized_position = max_normalized_position - ((x-1/2) * (x-1/2) + (y-1/2) * (y-1/2))
        pos_ratio = normalized_position/max_normalized_position
        pos_ratio_exp = pos_ratio * pos_ratio
        pos_altitude = pos_ratio_exp * (config.world.max_altitude - config.world.min_altitude) + config.world.min_altitude
        pos_altitude = int(pos_altitude)

        # Constrain so the sum of weights equals 1
        rand_altitude_offset = random.choice(range(-pos_altitude, pos_altitude))
        constrained_rand_altitude_offset = rand_altitude_offset * config.world.rand_altitude_factor
        constrained_pos_altitude = pos_altitude * (1 - config.world.rand_altitude_factor)
        # Sum partial altitudes
        altitude = constrained_pos_altitude + constrained_rand_altitude_offset

        # Verify altitude
        if altitude > config.world.max_altitude:
            self.altitudes_above_upper_bound = True
            error("Altitude of node in {0},{1} is too high ({2})"
                  .format(node_x, node_y, altitude))
            altitude = config.world.max_altitude
        elif altitude < config.world.min_altitude:
            self.altitudes_below_lower_bound = True
            error("Altitude of node in {0},{1} is too low ({2})"
                  .format(node_x, node_y, altitude))
            altitude = config.world.min_altitude

        return altitude


    def get_edge_weight_from_nodes(self, from_node, to_node, graph):
        target_pos = graph.node[to_node][strings.pos]
        x = target_pos[0] / config.world.size_x
        y = target_pos[1] / config.world.size_y
        rnd_wgt = 0  # int(random.random() * max_weight/2)
        max_pos = 1/2  # 1/2 * 1/2 + 1/2 * 1/2
        # max on (.5,.5), range [0, maxpos]
        current_pos = max_pos - ((x-1/2) * (x-1/2) + (y-1/2) * (y-1/2))
        pos_ratio = current_pos/max_pos
        pos_ratio_exp = pos_ratio * pos_ratio
        pos_weight = pos_ratio_exp * (config.world.max_weight - config.world.min_weight) + config.world.min_weight
        edge_weight = int(rnd_wgt + pos_weight)
        if edge_weight < config.world.min_weight:
            edge_weight = config.world.min_weight
        return edge_weight

    def create_graph(self, nodes, force_path=True):
        self.reset()
        graph = nx.Graph(is_environment=True)

        size_x = config.world.size_x
        size_y = config.world.size_y
        start_x = config.world.start_x
        start_y = config.world.start_y

        col_num_a = config.world.col_num_a
        padding = config.world.padding

        max_weight = config.world.max_weight
        min_weight = config.world.min_weight
        min_degree = config.world.min_degree
        max_degree = config.world.max_degree
        base_edge_chance = config.world.base_edge_chance
        number_of_edge_types = config.world.number_of_edge_types

        print("X => Start: {0} End: {1}".format(start_x, start_x + size_x))
        print("Y => Start: {0} End: {1}".format(start_y, start_y + size_y))

        def create_nodes():
            for y in range(start_y, start_y + size_y):
                for x in range(start_x, start_x + size_x):
                    key = (y - start_y) * size_x + x
                    altitude = self.create_node_altitude_from_pos(x, y)
                    print("Creating node {0},{1} with key {2}, altitude={3}".format(x, y, key, altitude))
                    nodes[key] = Node(x, y, altitude)
        create_nodes()

        def add_nodes_to_graph():
            for n_key in nodes.keys():
                n = nodes[n_key]
                print("Adding node with key: {0}".format(n_key))
                graph.add_node(n, pos=(n.x, n.y), label="{0}".format(n_key), altitude=n.altitude)
        add_nodes_to_graph()

        def create_edges():
            count = 0
            for n_key in nodes.keys():
                count += 1
                print("Reading node with key: {0}".format(n_key))
                n = nodes[n_key]
                targets = []
                previous_x = n.x - 1
                previous_y = n.y - 1

                if n.x > start_x and random.random() < base_edge_chance:
                    left_key = (n.y - start_y) * size_x + previous_x
                    print("Targeting left node with key: {0}".format(left_key))
                    targets.append(nodes[left_key])

                if n.y > start_y and random.random() < base_edge_chance:
                    above_key = (previous_y - start_y) * size_x + n.x
                    print("Targeting above node with key: {0}".format(above_key))
                    targets.append(nodes[above_key])

                for t in targets:
                    if n == t:
                        error("SHOULD NOT HAPPEN!")
                        Exception("Should not happen! Edge to self.")
                    # col = int(size_x/col_num_a)
                    # if nx.degree(G, t) >= max_degree and count % col != 0:
                    #     print("SKIPPED {0} - {1}".format(count, col))
                    #     continue
                    edge_weight = self.get_edge_weight_from_nodes(n, t, graph)
                    print("Adding edge between nodes {0} and {1} with weight {2}"
                          .format(graph.node[n][strings.label], graph.node[t][strings.label], edge_weight))
                    graph.add_edge(n, t, weight=edge_weight)
        create_edges()

        def remove_undesired_edges():
            random_order_nodes = graph.nodes()
            random.shuffle(random_order_nodes)
            for node in random_order_nodes:
                number_to_remove = graph.degree(node) - max_degree
                if number_to_remove > 0:
                    remove = random.sample(graph.edges(node), number_to_remove)
                    adjusted_remove = []
                    for edge in remove:
                        u = edge[0]
                        v = edge[1]
                        if u == node and graph.degree(v) > min_degree \
                                or v == node and graph.degree(u) > min_degree:
                            adjusted_remove.append(edge)
                            print("")
                    weight_loss = sum(graph[u][v][strings.wgt] for (u, v) in adjusted_remove)
                    graph.remove_edges_from(adjusted_remove)
                    removed_labels = str.join(", ", (graph.node[v][strings.label] for (u, v) in adjusted_remove))
                    print("Removed edge(s) from {0} to {2} (wgt={1})"
                          .format(graph.node[node][strings.label], weight_loss, removed_labels))
        remove_undesired_edges()

        return graph


class Environment():

    def __init__(self):
        self.graph_generator = GraphGenerator()
        self.nodes = dict()
        self.graph = self.graph_generator.create_graph(self.nodes)
        G = self.graph
        nodes = self.nodes

        # for node in G.nodes():
        #     if nx.degree(G, node) >= max_degree:
        #         edges = G.edges([node])
        #         edge_to_remove = random.choice(edges)
        #         edge_u = G.node[edge_to_remove[0]]
        #         edge_v = G.node[edge_to_remove[1]]
        #         edge_wgt = edge_to_remove[0]['weight']
        #         print("Removing edge ({2}) from {0} to {1}".format(edge_u['label'], G.edge[edge_u][edge_v]['weight']))
        #         G.remove_edges_from([edge_to_remove])


        size_x = config.world.size_x
        size_y = config.world.size_y
        start_x = config.world.start_x
        start_y = config.world.start_y

        col_num_a = config.world.col_num_a
        padding = config.world.padding

        max_weight = config.world.max_weight
        min_weight = config.world.min_weight
        min_degree = config.world.min_degree
        max_degree = config.world.max_degree
        base_edge_chance = config.world.base_edge_chance
        number_of_edge_types = config.world.number_of_edge_types

        first_node = nodes[1]
        last_node = nodes[len(nodes)]
        start_node = nodes[config.world.padding * config.world.size_x + config.world.padding + 1]
        target_node = nodes[len(nodes) - config.world.padding * config.world.size_x - config.world.padding]
        last_pos = last_node.get_position()
        x_pos = last_pos[0]
        y_pos = last_pos[1]
        d = math.sqrt(math.pow(x_pos - nodes[1].get_position()[0], 2) + math.pow(y_pos - nodes[1].get_position()[1], 2))
        print("Length from first node ({1}) to last node ({2}) is: {0} units."
              .format(d, nodes[1].get_position(), last_node.get_position()))
        print("Total number of nodes: {0}".format(self.graph.number_of_nodes()))

        # Find path
        path_nodes = None
        if nx.has_path(G, start_node, target_node):
            path_nodes = nx.astar_path(G, start_node, target_node)
            print("Path from {1} to {2} found with length: {0}"
                  .format(len(path_nodes), G.node[start_node][strings.label], G.node[target_node][strings.label]))
            for node in path_nodes:
                print("Via: {0}".format(G.node[node][strings.label]))

        path_edges = []
        current_node = start_node
        if path_nodes is not None:
            for node in path_nodes:
                if node == current_node:
                    continue
                print("Path from {0} to {1}".format(G.node[current_node][strings.label], G.node[node][strings.label]))
                if G.has_edge(current_node, node):
                    path_edges.append((current_node, node))
                elif G.has_edge(node, current_node):
                    path_edges.append((node, current_node))
                else:
                    error("SOMETHING VERY strange is going on.")
                current_node = node

        # Divide edges into groups based on weight and path
        weight_step = (max_weight-min_weight) / float(number_of_edge_types)
        sorted_edges = dict()

        for i in range(0, number_of_edge_types):
            sorted_edges[i] = []

        for (u, v, d) in G.edges(data=True):
            weight = float(d[strings.wgt])
            number_of_steps = (weight-min_weight) / (max_weight-min_weight)
            weight_index = number_of_steps * (number_of_edge_types-1)
            print("Weight-index: {0} ({1}) per: {2}".format(weight_index, weight, weight_step))
            sorted_edges[int(weight_index)].append((u, v))

        print("Printing out path edges: ")
        for (u, v) in path_edges:
            print("{0}-{1}".format(G.node[u][strings.label], G.node[v][strings.label]))

        #   Drawing:
        #
        def draw_using_matplotlib():

            def get_node_color(node):
                #  altitude = self.graph.node[node][strings.altitude]
                r = 'FF'
                g = '00'
                b = '00'
                color_string = "#{0}{1}{2}".format(r, g, b)
                return color_string

            # Draw nodes. Map of node positions { node_key: (x, y) }
            nodes_pos = nx.get_node_attributes(G, strings.pos)
            is_reading_data = True
            for node in G.nodes(data=is_reading_data):
                node_instance = node
                if is_reading_data:
                    node_instance = node[0]
                node_color = get_node_color(node_instance)
                node_pos = {0: (node_instance.x, node_instance.y)}
                print(node_pos)
                nx.draw_networkx_nodes(G, [node_pos], node, node_size=1000, node_color=node_color)

            # Draw path edges
            nx.draw_networkx_edges(G, nodes_pos,
                                   edgelist=path_edges, width=15, alpha=1, edge_color='#00FF00')

            # Draw all edges
            for index_key in sorted_edges.keys():
                edge_list = sorted_edges[index_key]
                fraction = index_key / len(sorted_edges)
                if index_key == len(sorted_edges)-1:
                    nx.draw_networkx_edges(G, nodes_pos,
                                           edgelist=edge_list, width=(1-fraction)*6 + 2,
                                           alpha=(1-fraction)*2/3 + 0.33, edge_color='b', style='dashed')
                # elif index_key == 0:
                #     nx.draw_networkx_edges(G, nodes_pos,
                #                            edgelist=edge_list, width=10, alpha=1, edge_color='g')
                else:
                    nx.draw_networkx_edges(G, nodes_pos,
                                           edgelist=edge_list, width=(1-fraction)*6 + 2, alpha=(1-fraction)*2/3 + 0.33)


            # labels
            node_labels = nx.get_node_attributes(G, strings.label)
            nx.draw_networkx_labels(G, nodes_pos, node_labels, font_size=18, font_family='sans-serif')

            plt.axis('off')
            plt.savefig(strings.plot_save_filename)  # save figure in a file (e.g. .png-format)

            # nx.draw_graphviz(G)
            # nx.write_dot(G,'file.dot')

            plt.show()  # display
        #  draw_using_matplotlib()



