from catan.agents.agent import Agent


class Human(Agent):
    """
    Placeholder model for human player
    """
    def __init__(self, name=None):
        super().__init__(name=name)
        self.is_cpu = False

    def choose_action(self):
        pass
