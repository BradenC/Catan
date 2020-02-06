from abc import ABC, abstractmethod


class Agent(ABC):
    def __init__(self, name=None):
        self._player = None
        self._name = name

        self.is_cpu = True

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, player):
        self._player = player

    @property
    def game(self):
        return self._player.game

    @property
    def name(self):
        return self._name or type(self).__name__

    @name.setter
    def name(self, name):
        self._name = name

    def do_action(self):
        func, args, kwargs = self.choose_action()
        func(*args, **kwargs)

    @abstractmethod
    def choose_action(self):
        """
        Choose an action for the agent to perform

        returns
            function
            args
            kwargs
        """
        pass
