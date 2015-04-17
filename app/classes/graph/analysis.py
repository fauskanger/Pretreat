from app.config import config, seeded_random as random
from app.pythomas import pythomas as lib
from app.classes.persist import PersistentObject


class Analysis(PersistentObject):
    def __init__(self, path, base_cost, expected_cost, irreplaceable_nodes, chance_of_open):
        self.path = path
        self.base_cost = base_cost
        self.expected_cost = expected_cost
        self.irreplaceable_nodes = irreplaceable_nodes
        self.chance_of_open = chance_of_open

    def chance_of_closed(self):
        return 1-self.chance_of_open