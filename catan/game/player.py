from catan.game import Resource, resource_color
from catan.game.constants import PLAYER_X, PLAYER_Y
from catan.game.piece import City, Road, Settlement
from catan.logging import logger


def action(func):
    def action_wrapper(*args, **kwargs):
        player = args[0]

        logger.info(
            data={
                'player': player.name,
                'function': func.__name__,
                'arguments': args
            },
            tags='actions'
        )

        func(*args, **kwargs)

        if player.victory_points >= player.game.victory_point_goal:
            player.game.finish()

        player.game.draw()

    return action_wrapper


class Player:
    count = 0

    def __init__(self, game, model=None, name=None):
        self.game = game

        self.num = Player.count
        Player.count += 1

        if model:
            self.model = model(self)
            self.is_cpu = True
            self.name = model.__name__
        else:
            self.is_cpu = False
            self.name = name or f"Player{self.num}"

        if self.num == 0:
            self.color = 'purple'
        elif self.num == 1:
            self.color = 'blue'
        elif self.num == 2:
            self.color = 'maroon'
        else:
            self.color = 'cyan'

        # wood, brick, grain, sheep, ore
        self.resource_cards = [0] * 5
        self.resource_generation = [0] * 5
        self.development_cards = []
        self.cities = []
        self.roads = []
        self.settlements = []
        self.turn_num = 0

    @property
    def victory_points(self):
        return len(self.settlements) + 2*len(self.cities)

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

        if not self.is_cpu:
            self.game.end_turn()

    @action
    def roll(self):
        if not self.game.can_roll():
            raise Exception(f'ERROR {self.name} cannot roll')

        self.game.roll()

    @action
    def trade(self, give_resource, receive_resource):
        if self.resource_cards[give_resource.value] < 4:
            raise Exception(f'ERROR {self.name} cannot trade - not enough {give_resource.name} to give')

        self.resource_cards[give_resource.value] -= 4
        self.resource_cards[receive_resource.value] += 1

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

    def take_turn(self):
        if self.is_cpu:
            self.model.take_turn()

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

        for res in Resource:
            if res.name == 'WATER' or res.name == 'DESERT':
                continue

            if self.game.graphics['res_cards'][_i]:
                self.game.c.delete(self.game.graphics['res_cards'][_i][0])
                self.game.c.delete(self.game.graphics['res_cards'][_i][1])

            rect = self.game.c.create_rectangle(x, y, x + 70, y + 100, outline=resource_color(res), width=4)
            text = self.game.c.create_text(x + 35, y + 50, text=self.resource_cards[_i], font="default 50", fill=resource_color(res))

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

    def to_jsonable(self):
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
