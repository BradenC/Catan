from abc import ABCMeta, abstractmethod
from time import sleep

from catan import config


class Model(metaclass=ABCMeta):
    def __init__(self, player):
        self.player = player
        self.game = self.player.game

    def take_turn(self):
        while True:
            if config['graphics'] and config['turn_delay']:
                self.game.c.update()
                sleep(config['turn_delay'])

            func, args, kwargs = self.choose_action()

            func(*args, **kwargs)

            if func == self.player.end_turn or self.game.is_finished:
                break

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
