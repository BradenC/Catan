from abc import ABC, abstractmethod


class Piece(ABC):
    max_per_player = None
    cost = None

    def __init__(self, location, owner):
        self._location = location

        self._owner = owner.num

    @property
    def game(self):
        return self._location.board.game

    @property
    def owner(self):
        return self.game.players[self._owner]

    @property
    def x(self):
        return self._location.x

    @property
    def y(self):
        return self._location.y

    @abstractmethod
    def copy(self, game, player):
        pass


class Road(Piece):
    max_per_player = 15
    cost = [1, 1, 0, 0, 0]

    @staticmethod
    def get_num_placed_by(player):
        return len(player.roads)

    @property
    def lane(self):
        return self._location

    @lane.setter
    def lane(self, lane):
        self._location = lane

    def copy(self, game, player):
        r = Road(game.board.lanes[self.lane.id], player)
        game.board.lanes[self.lane.id].piece = r
        return r


class Building(Piece, ABC):
    resource_collection_rate = None

    def __init__(self, location, owner):
        super().__init__(location, owner)
        self.resource_generation = [chance * self.resource_collection_rate for chance in self.point.resource_generation]

    @property
    def point(self):
        return self._location

    @point.setter
    def point(self, point):
        self._location = point


class Settlement(Building):
    max_per_player = 5
    cost = [1, 1, 1, 1, 0]
    resource_collection_rate = 1

    @staticmethod
    def get_num_placed_by(player):
        return len(player.settlements)

    def copy(self, game, player):
        s = Settlement(game.board.points[self.point.id], player)
        game.board.points[self.point.id].piece = s
        return s


class City(Building):
    max_per_player = 4
    cost = [0, 0, 0, 2, 3]
    resource_collection_rate = 2

    @staticmethod
    def get_num_placed_by(player):
        return len(player.cities)

    def copy(self, game, player):
        c = City(game.board.points[self.point.id], player)
        game.board.points[self.point.id].piece = c
        return c
