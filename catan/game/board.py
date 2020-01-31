from random import shuffle
from math import cos, pi, sqrt
from abc import ABCMeta, abstractmethod

from catan.game import HexNumbers, HexTiles, Resource, resource_color
from catan.game.piece import City, Road, Settlement

X_CELL_DIST = 40
Y_CELL_DIST = 35

roll_chance = [0, 0, 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]


class BoardPart(metaclass=ABCMeta):

    def stringify(self):
        return f"({self.x}, {self.y})"

    @property
    def owner(self):
        if self.piece:
            return self.piece.owner
        else:
            return None

    @property
    @abstractmethod
    def color(self):
        pass

    @abstractmethod
    def on_click(self):
        pass

    @abstractmethod
    def draw(self):
        pass


class Hex(BoardPart):
    SIDE_LEN = 80
    HEIGHT = SIDE_LEN * 2
    WIDTH = sqrt(3) * SIDE_LEN
    TIP_HEIGHT = (HEIGHT - SIDE_LEN) // 2
    TOKEN_WIDTH = 30

    def __init__(self, board, x, y, resource, num):
        self.board = board

        self.resource = resource
        self.num = num
        self.roll_chance = roll_chance[self.num]

        self.x = x
        self.y = y

        self.points = self.get_points()
        for point in self.points:
            point.add_hex(self)

        self.polygon_coords = self.calc_polygon_coords()
        self.token_coords = self.calc_token_coords()

    @property
    def color(self):
        return resource_color(self.resource)

    def get_points(self):
        return [
            self.board.grid[self.x-2][self.y+1],
            self.board.grid[self.x-2][self.y-1],
            self.board.grid[self.x+2][self.y+1],
            self.board.grid[self.x+2][self.y-1],
            self.board.grid[self.x][self.y+3],
            self.board.grid[self.x][self.y-3]
        ]

    def calc_polygon_coords(self):
        _x = self.x * X_CELL_DIST
        _y = self.y * Y_CELL_DIST

        return [
            _x, _y,
            _x + self.WIDTH / 2, _y + self.TIP_HEIGHT,
            _x + self.WIDTH / 2, _y + self.TIP_HEIGHT + self.SIDE_LEN,
            _x, _y + self.HEIGHT,
            _x - self.WIDTH / 2, _y + self.TIP_HEIGHT + self.SIDE_LEN,
            _x - self.WIDTH / 2, _y + self.TIP_HEIGHT,
        ]

    def calc_token_coords(self):
        _x = self.x * X_CELL_DIST
        _y = self.y * Y_CELL_DIST + 50 + Hex.TOKEN_WIDTH/2

        return [
            _x - Hex.TOKEN_WIDTH/2, _y,
            _x + Hex.TOKEN_WIDTH/2, _y + Hex.TOKEN_WIDTH
        ], [
            _x, _y + Hex.TOKEN_WIDTH/2
        ]

    def give_resources(self):
        for point in self.points:
            if point.piece:
                point.owner.resource_cards[self.resource.value] += point.piece.resource_collection_rate

    def on_click(self, event):
        pass

    def draw_hex(self):
        h = self.board.game.c.create_polygon(self.polygon_coords, fill=self.color)
        self.board.game.c.tag_bind(h, '<Button-1>', self.on_click)

    def draw_token(self):
        if self.resource == Resource.DESERT:
            return

        oval_points, text_points = self.token_coords

        oval = self.board.game.c.create_oval(oval_points, fill="#FFF")
        text = self.board.game.c.create_text(text_points, font="Times 10", text=self.num)

        self.board.game.c.tag_bind(oval, '<Button-1>', self.on_click)
        self.board.game.c.tag_bind(text, '<Button-1>', self.on_click)

    def draw(self):
        self.draw_hex()
        self.draw_token()


class Lane(BoardPart):
    def __init__(self, board, x, y):
        self.board = board

        self.x = x
        self.y = y

        self.orientation = self.calc_orientation()
        self.polygon_coords = self.calc_polygon_coords()

        self.points = self.get_points()
        for point in self.points:
            point.lanes.append(self)

        self.piece = None

        self._color = "#111"
        self.graphics = None

    @property
    def color(self):
        if self.owner:
            return self.owner.color
        else:
            return self._color

    def get_points(self):
        if self.orientation == '|':
            return [self.board.grid[self.x][self.y-1], self.board.grid[self.x][self.y+1]]
        elif self.orientation == '/':
            return [self.board.grid[self.x-1][self.y+1], self.board.grid[self.x+1][self.y-1]]
        elif self.orientation == '\\':
            return [self.board.grid[self.x-1][self.y-1], self.board.grid[self.x+1][self.y+1]]

    def calc_orientation(self):
        if self.x % 2 == 1:
            return '|'
        elif (self.x % 4 == 2 and self.y % 8 == 1) or (self.x % 4 == 0 and self.y % 8 == 5):
            return '/'
        else:
            return '\\'

    def calc_polygon_coords(self):
        _x = self.x * X_CELL_DIST
        _y = self.y * Y_CELL_DIST + 80

        if self.x % 2 == 1:  # |
            return [
                _x - 10, _y - 40,
                _x + 10, _y - 40,
                _x + 10, _y + 40,
                _x - 10, _y + 40
            ]
        elif (self.x % 4 == 2 and self.y % 8 == 1) or (self.x % 4 == 0 and self.y % 8 == 5):
            return [
                _x + 28, _y - 30,
                _x + 40, _y - 10,
                _x - 28, _y + 30,
                _x - 40, _y + 10
            ]
        else:  # \
            return [
                _x - 28, _y - 30,
                _x - 40, _y - 10,
                _x + 28, _y + 30,
                _x + 40, _y + 10
            ]

    def is_reachable_by(self, player):
        if self.board.game.is_setup_phase():
            if len(player.settlements) == player.turn_num:
                return self.points[0].piece == player.settlements[-1] or self.points[1].piece == player.settlements[-1]
            else:
                return False
        else:
            return self.points[0].is_reachable_by(player) or self.points[1].is_reachable_by(player)

    def on_click(self, event):
        if not (self.is_reachable_by(self.board.game.player)):
            return

        self.board.game.player.build(Road, self)

        self.board.game.draw()

    def draw(self):
        if self.graphics:
            self.board.game.c.delete(self.graphics)

        lane = self.board.game.c.create_polygon(self.polygon_coords, fill=self.color)

        if not self.piece:
            self.board.game.c.tag_bind(lane, '<Button-1>', self.on_click)

        self.graphics = lane


class Point(BoardPart):
    SIDE_LEN = 35
    UPPER_HEIGHT = SIDE_LEN / sqrt(3)
    LOWER_HEIGHT = SIDE_LEN * cos(pi/6) - UPPER_HEIGHT

    def __init__(self, board, x, y):
        self.board = board

        self.x = x
        self.y = y

        self.lanes = []
        self.hexes = []

        self.piece = None
        self.resource_generation = [0] * 5
        self._color = "#111"

        self.graphics = None

    @property
    def color(self):
        if self.owner:
            return self.owner.color
        else:
            return self._color

    @property
    def polygon_coords(self):
        _x = self.x * X_CELL_DIST
        _y = self.y * Y_CELL_DIST + 70

        point_down = self.y % 4 == 0

        if point_down:
            _y += 20
            return [
                _x, _y + Point.UPPER_HEIGHT,
                _x + Point.SIDE_LEN / 2, _y - Point.LOWER_HEIGHT,
                _x - Point.SIDE_LEN / 2, _y - Point.LOWER_HEIGHT
            ]
        else:
            return [
                _x, _y - self.UPPER_HEIGHT,
                _x + Point.SIDE_LEN / 2, _y + Point.LOWER_HEIGHT,
                _x - Point.SIDE_LEN / 2, _y + Point.LOWER_HEIGHT
            ]

    def add_hex(self, h):
        if h.num:
            self.resource_generation[h.resource.value] += h.roll_chance

        self.hexes.append(h)

    def is_crowded(self):
        for lane in self.lanes:
            for point in lane.points:
                if point.piece:
                    return True

        return False

    def is_reachable_by(self, player):
        if self.piece and self.piece.owner == player:
            return True

        for lane in self.lanes:
            if lane.piece and lane.piece.owner == player:
                return True

        return False

    def on_click(self, event):
        if self.is_crowded():
            return

        if not self.piece:
            self.board.game.player.build(Settlement, self)
        elif isinstance(self.piece, Settlement):
            self.board.game.player.build(City, self)

        self.board.game.draw()

    def draw(self):
        if self.graphics:
            self.board.game.c.delete(self.graphics)

        if self.piece:
            if isinstance(self.piece, Settlement):
                self.graphics = self.board.game.c.create_polygon(self.polygon_coords, fill=self.piece.owner.color)
            elif isinstance(self.piece, City):
                self.graphics = self.board.game.c.create_polygon(self.polygon_coords, fill=self.piece.owner.color, outline="white", width=3)
        else:
            self.graphics = self.board.game.c.create_polygon(self.polygon_coords, fill=self._color)
            self.board.game.c.tag_bind(self.graphics, '<Button-1>', self.on_click)


class Board:
    NUM_ROWS = 5
    NUM_COLS = 5

    def __init__(self, game, random=False):
        self.game = game

        self.num_rows = self.NUM_ROWS
        self.num_cols = self.NUM_COLS
        self.grid = [[None] * (4 * self.num_cols + 3) for _ in range(self.num_rows * 8 - 1)]

        self.points = self.make_points()
        self.lanes = self.make_lanes()
        self.hexes = self.make_hexes(random)

    def make_hexes(self, random):
        hexes = []

        resource_tiles = HexTiles.copy()
        number_tokens = HexNumbers.copy()

        if random:
            shuffle(resource_tiles)
            shuffle(number_tokens)

        for row in range(self.num_rows):
            x_offset = 3 + 2 * abs(2 - row)
            for col in range(self.num_cols - abs(2 - row)):
                x = x_offset + 4 * col
                y = 3 + 4 * row

                new_hex = Hex(self, x, y, resource_tiles.pop(), number_tokens.pop())

                hexes.append(new_hex)
                self.grid[x][y] = new_hex

        return hexes

    def make_lanes(self):
        lanes = []

        for row in range(1, (self.num_rows - 1) * 6 - 1, 2):
            x_offset = abs(11 - row) // 2

            if row % 4 == 3:  # |
                for col in range(1 + x_offset, (self.num_cols + 1) * 4 - x_offset, 4):
                    new_lane = Lane(self, col, row)
                    lanes.append(new_lane)
                    self.grid[col][row] = new_lane
            else:  # / and \
                for col in range(1 + x_offset, self.num_cols * 4 - x_offset + 2, 2):
                    new_lane = Lane(self, col, row)
                    lanes.append(new_lane)
                    self.grid[col][row] = new_lane

        return lanes

    def make_points(self):
        points = []

        for row in range(0, (self.num_rows - 1) * 6, 2):
            long_side = 1 if (row % 4) == 0 else 0
            long_side = 1 - long_side if row > 11 else long_side
            x_offset = abs(11 - row) // 2 + long_side

            for col in range(1 + x_offset, self.num_cols * 4 + 2 - x_offset, 4):
                new_point = Point(self, col, row)
                points.append(new_point)
                self.grid[col][row] = new_point

        return points

    def give_resources(self, roll):
        for h in self.hexes:
            if h.num == roll:
                h.give_resources()

    def draw_hexes(self):
        for h in self.hexes:
            h.draw()

    def draw_lanes(self):
        for lane in self.lanes:
            lane.draw()

    def draw_points(self):
        for point in self.points:
            point.draw()

    def draw(self):
        self.draw_hexes()
        self.draw_lanes()
        self.draw_points()
