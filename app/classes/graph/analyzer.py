from app.config import config, seeded_random as random
from app.pythomas import pythomas as lib
from app.classes.graph.analysis import Analysis


class Analyzer:
    def __init__(self, nav_graph):
        self.nav_graph = nav_graph

    def score_path(self):
        path = self.nav_graph.pathfinder.get_path()
        nodes = self.nav_graph.pathfinder.get_path_nodes()
        if len(nodes) < 3:
            return None
        edges = self.nav_graph.pathfinder.get_path_edges()
        base_cost = self.nav_graph.pathfinder.get_path_cost()
        # base_costs = dict()
        # for edge in edges:
        #     base_costs[edge] = self.nav_graph.pathfinder.read_edge_cost(edge)
        infinity = float("inf")
        irreplaceable_nodes = []
        costs = dict()
        block_chances = dict()
        for i in range(1, len(nodes)-1):
            predecessor = nodes[i-1]
            node = nodes[i]
            self.nav_graph.block_node(node)
            cost = self.nav_graph.pathfinder.get_path_cost()
            if not cost or cost == infinity:
                irreplaceable_nodes.append(node)
                costs[node] = base_cost
            else:
                costs[node] = cost
            block_chances[node] = 1 / (len(nodes) - 2)
            self.nav_graph.unblock_node(node)
        chance_of_open = 1
        for node in irreplaceable_nodes:
            chance_of_open *= (1-block_chances[node])
        expected_cost = sum(costs[node]*block_chances[node] for node in nodes[1:-1])
        analysis = Analysis(path, base_cost, expected_cost, irreplaceable_nodes, chance_of_open)
        return analysis
