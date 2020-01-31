from abc import ABCMeta
import json


class Piece(metaclass=ABCMeta):
    max_per_player = None
    cost = None

    def __init__(self, location, owner):
        self._location = location
        self.owner = owner

    def stringify(self):
        return self._location.stringify()


class Road(Piece):
    max_per_player = 15
    cost = [1, 1, 0, 0, 0]

    @staticmethod
    def get_num_placed_by(player):
        return len(player.roads)

    @property
    def lane(self):
        return self._location


class Building(Piece, metaclass=ABCMeta):
    resource_collection_rate = None

    def __init__(self, location, owner):
        super().__init__(location, owner)
        self.resource_generation = [chance * self.resource_collection_rate for chance in self.point.resource_generation]

    @property
    def point(self):
        return self._location


class Settlement(Building):
    max_per_player = 5
    cost = [1, 1, 1, 1, 0]
    resource_collection_rate = 1

    @staticmethod
    def get_num_placed_by(player):
        return len(player.settlements)


class City(Building):
    max_per_player = 4
    cost = [0, 0, 0, 2, 3]
    resource_collection_rate = 2

    @staticmethod
    def get_num_placed_by(player):
        return len(player.cities)
