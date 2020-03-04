from copy import copy

from catan import config, logger
from catan.game.actions import get_action_by_id, get_legal_action_ids
from catan.game.resource import resources
from catan.game.constants import PLAYER_X, PLAYER_Y
from catan.game.piece import City, Road, Settlement
from catan.agents import Human


def action(func):
    def action_wrapper(*args, **kwargs):
        player = args[0]

        log_func = logger.debug if player.game.depth == 0 else logger.trace
        log_func(
            data={
                'num': player.num,
                'player': player.name,
                'depth': player.game.depth,
                'function': func.__name__
            },
            tags='actions'
        )

        func(*args, **kwargs)

        player.game.draw()

        if not player.is_cpu:
            player.game.turn_loop()

    return action_wrapper


class Player:
    def __init__(self, game, model=None, name=None):
        self.game = game

        self.model = model
        if self.model:
            self.model.player = self
            self.is_cpu = model.is_cpu
            self.name = name or model.name
        else:
            self.is_cpu = False
            self.name = name

        self._num = None
        self.color = None

        # wood, brick, grain, sheep, ore
        self.resource_cards = [0] * 5
        # self.resource_cards = [7, 7, 3, 3, 0]
        self.resource_generation = [0] * 5
        self.development_cards = []
        self.cities = []
        self.roads = []
        self.settlements = []
        self.turn_num = 0

    @property
    def num(self):
        return self._num

    @num.setter
    def num(self, num):
        self._num = num

        if self._num == 0:
            self.color = 'purple'
        elif self._num == 1:
            self.color = 'blue'
        elif self._num == 2:
            self.color = 'maroon'
        else:
            self.color = 'cyan'

    @property
    def victory_points(self):
        return len(self.settlements) + 2*len(self.cities)

    @property
    def has_won(self):
        return self.victory_points >= config['game']['victory_points_to_win']

    @property
    def num_remaining_cities(self):
        return City.max_per_player - len(self.cities)

    @property
    def num_remaining_roads(self):
        return Road.max_per_player - len(self.roads)

    @property
    def num_remaining_settlements(self):
        return Settlement.max_per_player - len(self.settlements)

    @action
    def end_turn(self):
        if not self.game.can_end_turn():
            raise Exception(f'ERROR {self.name} cannot end turn')

        self.game.end_turn()

    @action
    def roll(self):
        if not self.game.can_roll():
            raise Exception(f'ERROR {self.name} cannot roll')

        self.game.roll()

    @action
    def trade(self, give_resource, receive_resource):
        if self.resource_cards[give_resource] < 4:
            raise Exception(f'ERROR {self.name} cannot trade - not enough {give_resource} to give')

        self.resource_cards[give_resource] -= 4
        self.resource_cards[receive_resource] += 1

    @action
    def build(self, piece_type, position):
        if position.piece:
            if not (isinstance(position.piece, Settlement) and piece_type == City):
                raise Exception(f'ERROR {self.name} cannot place piece - piece already exists there')

        if self.game.is_setup_phase():
            if piece_type == City:
                return
            if piece_type == Road and self.game.player.turn_num <= len(self.game.player.roads):
                return
            if piece_type == Settlement and self.game.player.turn_num <= len(self.game.player.settlements):
                return
        elif self.can_afford(piece_type):
            for i in range(5):
                self.resource_cards[i] -= piece_type.cost[i]
        else:
            return

        if piece_type == City:
            self.settlements.remove(position.piece)

        piece = piece_type(position, self)
        self.add_piece(piece)
        position.piece = piece

    def get_legal_action_ids(self):
        return get_legal_action_ids(self.game)

    def do_action(self):
        legal_action_ids = self.get_legal_action_ids()
        if self.game.can_roll():
            self.roll()
        elif len(legal_action_ids) == 1:
            func1, args, kwargs = get_action_by_id(self.game, legal_action_ids[0])
            func1(*args, **kwargs)
        else:
            self.model.do_action()

    def can_afford(self, piece):
        if piece.get_num_placed_by(self) >= piece.max_per_player:
            return False

        if self.game.is_setup_phase():
            if piece == Settlement and len(self.settlements) < self.turn_num:
                return True
            if piece == Road and len(self.roads) == len(self.settlements) - 1:
                return True
            return False

        cost = piece.cost
        for i in range(5):
            if self.resource_cards[i] < cost[i]:
                return False

        return True

    def add_piece(self, piece):
        if isinstance(piece, Road):
            self.roads.append(piece)
            return

        if isinstance(piece, City):
            self.cities.append(piece)
        elif isinstance(piece, Settlement):
            self.settlements.append(piece)

        self.resource_generation = [sum(x) for x in zip(self.resource_generation, piece.resource_generation)]

    def draw_name_banner(self, x, y):
        if 'name_banner' in self.game.graphics:
            self.game.c.delete(self.game.graphics['name_banner'][0])
            self.game.c.delete(self.game.graphics['name_banner'][1])

        rect = self.game.c.create_rectangle(x, y, x + 20, y + 60, fill=self.color)
        text = self.game.c.create_text(x + 30, y - 16, fill="white", text=self.name, font="default 60 bold", anchor="nw")
        self.game.graphics['name_banner'] = (rect, text)

    def draw_resource_cards(self, x, y):
        y += 100
        _i = 0

        if 'res_cards' not in self.game.graphics:
            self.game.graphics['res_cards'] = [None] * len(self.resource_cards)

        for res in resources:
            if res.name == 'water' or res.name == 'desert':
                continue

            if self.game.graphics['res_cards'][_i]:
                self.game.c.delete(self.game.graphics['res_cards'][_i][0])
                self.game.c.delete(self.game.graphics['res_cards'][_i][1])

            rect = self.game.c.create_rectangle(x, y, x + 70, y + 100, outline=res.color, width=4)
            text = self.game.c.create_text(x + 35, y + 50, text=self.resource_cards[_i], font="default 50", fill=res.color)

            self.game.graphics['res_cards'][_i] = (rect, text)
            x += 90
            _i += 1

    def draw_remaining_pieces(self, x, y):
        if 'remaining_pieces' in self.game.graphics:
            self.game.c.delete(self.game.graphics['remaining_pieces'][0])
            self.game.c.delete(self.game.graphics['remaining_pieces'][1])
            self.game.c.delete(self.game.graphics['remaining_pieces'][2])

        roads = self.game.c.create_text(
            x, y, fill="white", text=f"R - {self.num_remaining_roads}", font="default 60 bold", anchor="nw")

        settlements = self.game.c.create_text(
            x, y + 80, fill="white", text=f"S - {self.num_remaining_settlements}", font="default 60 bold", anchor="nw")

        cities = self.game.c.create_text(
            x, y + 160, fill="white", text=f"C - {self.num_remaining_cities}", font="default 60 bold", anchor="nw")

        self.game.graphics['remaining_pieces'] = (roads, settlements, cities)

    def draw(self):
        self.draw_name_banner(PLAYER_X, PLAYER_Y)
        self.draw_resource_cards(PLAYER_X + 38, PLAYER_Y)
        self.draw_remaining_pieces(PLAYER_X + 30, PLAYER_Y + 220)

    def stringify_stats(self):
        roads = len(self.roads)
        settlements = len(self.settlements)
        cities = len(self.cities)

        stat_string = f"""\
| Name: {self.name}
| Victory Points: {self.victory_points}
| Roads: {roads}
| Settlements: {settlements}
| Cities: {cities}
| Resource Cards: {self.resource_cards}
| Development Cards: {[]}
"""
        return stat_string

    def to_dict(self):
        return {
            'name': self.name,
            'num': self.num,
            'model': type(self.model).__name__,
            'victory_points': self.victory_points,
            'num_roads': len(self.roads),
            'num_settlements': len(self.settlements),
            'num_cities': len(self.cities),
            'resource_cards': self.resource_cards
        }

    def copy(self, game):
        p = Player(game)
        p.resource_cards = copy(self.resource_cards)
        p.resource_generation = copy(self.resource_generation)
        p.development_cards = copy(self.development_cards)
        p.cities = [city.copy(game, self) for city in self.cities]
        p.settlements = [settlement.copy(game, self) for settlement in self.settlements]
        p.roads = [road.copy(game, self) for road in self.roads]
        p.turn_num = self.turn_num
        p.is_cpu = self.is_cpu
        p.name = self.name
        p.num = self.num
        p.color = self.color

        return p
