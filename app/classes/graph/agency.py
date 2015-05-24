from app.config import config, seeded_random as random
from app.pythomas import pythomas as lib
from app.classes.graph.agent import Agent, AutonomousAgent, GoodAgent


class Agency(object):
    def __init__(self, nav_graph):
        self.nav_graph = nav_graph
        self.good_guy = None
        self.agents = []

    def clear(self):
        self.agents.clear()

    def create_new_set(self, n_evils=1, reset_path=True):
        for agent in self.agents:
            agent.leave_current_node()
        self.clear()
        self.nav_graph.create_random_path(only_if_none=not reset_path)
        self.good_guy = GoodAgent(self.nav_graph)
        # self.good_guy.start()
        self.agents.append(self.good_guy)
        self.add_evil_agent(n_evils)

    def add_evil_agent(self, n_evils=1):
        start_n = len(self.agents)
        for n in range(n_evils):
            self.agents.append(AutonomousAgent("Agent {}".format(n+start_n), self.nav_graph))

    def update(self, dt):
        for agent in self.agents:
            if agent.state is agent.State.Running:
                agent.update(dt)
            else:
                agent.start()

