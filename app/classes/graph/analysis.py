from app.config import config, seeded_random as random
from app.pythomas import pythomas as lib
from app.classes.persist import PersistentObject


class Analysis(PersistentObject):
    def __init__(self, path, base_cost, expected_cost, irreplaceable_nodes, chance_of_open):
        self.path = path
        self.base_cost = 0
        self.expected_cost = 0
        self.irreplaceable_nodes = []
        self.chance_of_open = 1

    def chance_of_closed(self):
        return 1-self.chance_of_open