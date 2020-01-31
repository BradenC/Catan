from random import randint, seed, shuffle
from time import time

from catan import config
from catan.game.board import Board
from catan.game.constants import DICE_WIDTH, END_TURN_X, END_TURN_Y, ROLL_X, ROLL_Y
from catan.game.player import Player
from catan.logging import logger
from catan.models import model_thing


def player_loop(players):
    i = -1

    # Setup phase
    while i < len(players):
        yield players[i]
        i += 1

    i -= 1
    while i >= 0:
        yield players[i]
        i -= 1

    # Regular play
    while True:
        if i < len(players) - 1:
            i += 1
        else:
            i = 0

        yield players[i]


class Game:
    victory_point_goal = config['victory_point_goal']

    def __init__(self, num_humans=0, num_bots=2, is_random=False, canvas=None):
        if config['seed']:
            seed(config['seed'])

        self.board = Board(self, is_random)

        self.model_thing = model_thing()
        self.players = [Player(self)                   for _ in range(num_humans)]\
                     + [Player(self, model=next(self.model_thing)) for _ in range(num_bots)]
        shuffle(self.players)

        self.player_loop = player_loop(self.players)
        self.player = next(self.player_loop)

        self.start_time = self.end_time = None
        self.turn_num = 0
        self.is_finished = False
        self.last_roll = (None, None)

        self.c = canvas
        if self.c:
            self.graphics = {}

    def start(self):
        self.start_time = time()
        self.end_turn()

    def is_setup_phase(self):
        return self.turn_num < len(self.players) * 2 + 1

    @property
    def duration(self):
        return self.end_time - self.start_time

    def clear_dice(self):
        self.last_roll = (None, None)

    def can_roll(self):
        logger.debug(f'Checking if player {self.player.name} can roll.', tags='checks')

        if self.is_setup_phase():
            return False

        if self.last_roll[0]:
            return False

        return True

    def roll(self):
        d1 = randint(1, 6)
        d2 = randint(1, 6)
        self.last_roll = (d1, d2)

        self.board.give_resources(d1 + d2)

    def can_end_turn(self):
        logger.debug(f'Checking if player {self.player.name} can end their turn', tags='checks')

        if self.is_setup_phase():
            if len(self.player.settlements) == len(self.player.roads) == self.player.turn_num:
                return True
        elif self.last_roll[0]:
            return True

        return False

    def end_turn(self):
        if not self.can_end_turn():
            return

        while True:
            self.turn_num += 1
            self.clear_dice()

            self.player = next(self.player_loop)
            self.player.turn_num += 1

            self.draw()

            self.player.take_turn()

            if not self.player.is_cpu or self.is_finished:
                break

    def draw_die(self, x, y, val):
        rect = self.c.create_rectangle(x, y, x + 60, y + 60, fill="white")

        if not val and not self.is_setup_phase() and not self.player.is_cpu:
            self.c.tag_bind(rect, "<Button-1>", lambda event: self.roll())
            return

        self.graphics['dice'].append(rect)

        if val == 1:
            self.graphics['dice'] += [
                self.c.create_oval(x + 3/8 * DICE_WIDTH, y + 3/8 * DICE_WIDTH, x + 5/8 * DICE_WIDTH, y + 5/8 * DICE_WIDTH, fill="black")
            ]
        elif val == 2:
            self.graphics['dice'] += [
                self.c.create_oval(x + 1/8 * DICE_WIDTH, y + 1/8 * DICE_WIDTH, x + 3/8 * DICE_WIDTH, y + 3/8 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 5/8 * DICE_WIDTH, y + 5/8 * DICE_WIDTH, x + 7/8 * DICE_WIDTH, y + 7/8 * DICE_WIDTH, fill="black")
            ]
        elif val == 3:
            self.graphics['dice'] += [
                self.c.create_oval(x + 1/8 * DICE_WIDTH, y + 1/8 * DICE_WIDTH, x + 3/8 * DICE_WIDTH, y + 3/8 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 3/8 * DICE_WIDTH, y + 3/8 * DICE_WIDTH, x + 5/8 * DICE_WIDTH, y + 5/8 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 5/8 * DICE_WIDTH, y + 5/8 * DICE_WIDTH, x + 7/8 * DICE_WIDTH, y + 7/8 * DICE_WIDTH, fill="black")
            ]
        elif val == 4:
            self.graphics['dice'] += [
                self.c.create_oval(x + 1/8 * DICE_WIDTH, y + 1/8 * DICE_WIDTH, x + 3/8 * DICE_WIDTH, y + 3/8 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 5/8 * DICE_WIDTH, y + 1/8 * DICE_WIDTH, x + 7/8 * DICE_WIDTH, y + 3/8 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 1/8 * DICE_WIDTH, y + 5/8 * DICE_WIDTH, x + 3/8 * DICE_WIDTH, y + 7/8 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 5/8 * DICE_WIDTH, y + 5/8 * DICE_WIDTH, x + 7/8 * DICE_WIDTH, y + 7/8 * DICE_WIDTH, fill="black")
            ]
        elif val == 5:
            self.graphics['dice'] += [
                self.c.create_oval(x + 1/8 * DICE_WIDTH, y + 1/8 * DICE_WIDTH, x + 3/8 * DICE_WIDTH, y + 3/8 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 5/8 * DICE_WIDTH, y + 1/8 * DICE_WIDTH, x + 7/8 * DICE_WIDTH, y + 3/8 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 1/8 * DICE_WIDTH, y + 5/8 * DICE_WIDTH, x + 3/8 * DICE_WIDTH, y + 7/8 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 5/8 * DICE_WIDTH, y + 5/8 * DICE_WIDTH, x + 7/8 * DICE_WIDTH, y + 7/8 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 3/8 * DICE_WIDTH, y + 3/8 * DICE_WIDTH, x + 5/8 * DICE_WIDTH, y + 5/8 * DICE_WIDTH, fill="black")
            ]
        elif val == 6:
            self.graphics['dice'] += [
                self.c.create_oval(x + 1/8 * DICE_WIDTH, y + 1/16 * DICE_WIDTH, x + 3/8 * DICE_WIDTH, y + 5/16 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 1/8 * DICE_WIDTH, y + 6/16 * DICE_WIDTH, x + 3/8 * DICE_WIDTH, y + 10/16 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 1/8 * DICE_WIDTH, y + 11/16 * DICE_WIDTH, x + 3/8 * DICE_WIDTH, y + 15/16 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 5/8 * DICE_WIDTH, y + 1/16 * DICE_WIDTH, x + 7/8 * DICE_WIDTH, y + 5/16 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 5/8 * DICE_WIDTH, y + 6/16 * DICE_WIDTH, x + 7/8 * DICE_WIDTH, y + 10/16 * DICE_WIDTH, fill="black"),
                self.c.create_oval(x + 5/8 * DICE_WIDTH, y + 11/16 * DICE_WIDTH, x + 7/8 * DICE_WIDTH, y + 15/16 * DICE_WIDTH, fill="black")
            ]

    def draw_dice(self):
        if 'dice' in self.graphics:
            for g in self.graphics['dice']:
                self.c.delete(g)

        self.graphics['dice'] = []

        x = ROLL_X
        y = ROLL_Y

        self.graphics['dice'] += [
            self.draw_die(x, y, self.last_roll[0]),
            self.draw_die(x + DICE_WIDTH + 20, y, self.last_roll[1])
        ]

    def draw_end_turn(self):
        if 'end_turn' in self.graphics:
            self.c.delete(self.graphics['end_turn'])

        if not self.can_end_turn() or self.player.is_cpu:
            return

        text = self.c.create_text(END_TURN_X, END_TURN_Y, text="End Turn", fill="white", font="default 30", anchor="nw")

        if not self.player.is_cpu:
            self.c.tag_bind(text, "<Button-1>", lambda event: self.end_turn())

        self.graphics['end_turn'] = text

    def draw(self):
        if self.c:
            self.board.draw()
            self.player.draw()
            self.draw_dice()
            self.draw_end_turn()

    def game_recap(self):
        time_string = "{:.4f}".format(self.duration) + 's'

        return '\n\n' \
               'Game Stats \n\n' \
               f"| Winner: {self.player.name}\n" \
               f"| Time: {time_string}\n" \
               f"| Turns: {self.turn_num}"

    def player_recap(self):
        player_recap = '\n\nPlayer Stats\n'
        for player in self.players:
            player_recap += ('\n' + player.stringify_stats())

        return player_recap

    def finish(self):
        self.is_finished = True
        self.end_time = time()

        game_finished_message = 'Game Over'
        game_recap = self.game_recap()
        player_recap = self.player_recap()

        logger.info(game_finished_message + game_recap + player_recap)

    def to_jsonable(self):
        return {
            'duration_seconds': "{:.4f}".format(self.duration) + 's',
            'num_turns': self.turn_num,
            'winner': self.player.name,
            'players': [player.to_jsonable() for player in self.players]
        }
