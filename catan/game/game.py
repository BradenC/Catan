from copy import copy
from random import randint, seed, shuffle
from time import sleep, time

from catan import config, logger
from catan.game.board import Board
from catan.game.constants import DICE_WIDTH, END_TURN_X, END_TURN_Y, ROLL_X, ROLL_Y
from catan.game.player import Player


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


def shuffle_players(players):
    shuffle(players)
    for i, player in enumerate(players):
        player.num = i


class Game:
    def __init__(self, players=[], is_random=False, canvas=None, turn_delay_s=None):
        if config['game']['seed']:
            seed(config['game']['seed'])

        self.board = Board(self, is_random)

        self._player = 0
        self.winner = None
        if players:
            self.players = [Player(self, player_model) for player_model in players]
            shuffle_players(self.players)

            self.player_loop = player_loop(self.players)
            self.player = next(self.player_loop)

        self.start_time = self.end_time = None
        self.turn_num = 0
        self.last_roll = (None, None)

        self.c = canvas
        if self.c:
            self.c.delete("all")
            self.graphics = {}
            self.turn_delay_s = turn_delay_s

        self.depth = 0

    @property
    def player(self):
        return self.players[self._player]

    @player.setter
    def player(self, player):
        self._player = player.num

    def start(self):
        self.start_time = time()
        self.end_turn()

        self.turn_loop()

        self.finish()

        return self

    def turn_loop(self):
        while self.player.is_cpu and not self.is_finished:
            if self.c:
                sleep(self.turn_delay_s)
            self.player.do_action()

    def is_setup_phase(self):
        return self.turn_num < len(self.players) * 2 + 1

    @property
    def duration(self):
        return self.end_time - self.start_time

    @property
    def is_finished(self):
        for player in self.players:
            if player.victory_points >= config['game']['victory_points_to_win']:
                return True

        return False

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
            logger.error('Illegal end turn attempted', data={"player": self.player.name}, tags='actions')
            raise Exception(f'Illegal end turn by player number {self.player.num}')

        self.turn_num += 1
        self.clear_dice()

        self.player = next(self.player_loop)
        self.player.turn_num += 1

    def draw_die(self, x, y, val):
        rect = self.c.create_rectangle(x, y, x + 60, y + 60, fill="white")

        if not val and not self.is_setup_phase() and not self.player.is_cpu:
            self.c.tag_bind(rect, "<Button-1>", lambda event: self.player.roll())
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
            self.c.tag_bind(text, "<Button-1>", lambda event: self.player.end_turn())

        self.graphics['end_turn'] = text

    def draw(self):
        if self.c:
            self.board.draw()
            self.player.draw()
            self.draw_dice()
            self.draw_end_turn()
            self.c.update()

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
        self.winner = self.player
        self.end_time = time()
        self.draw()

        logger.info('Game over', data=self.to_dict(), tags='progress')

    def to_dict(self):
        return {
            'duration_seconds': "{:.4f}".format(self.duration) + 's',
            'num_turns': self.turn_num,
            'winner': self.winner.name,
            'players': [player.to_dict() for player in self.players]
        }

    def copy(self):
        g = Game()
        g.depth = self.depth + 1

        g.board = self.board.copy(g)

        g.players = [player.copy(g) for player in self.players]
        g.player_loop = player_loop(g.players)

        for _ in range(self.turn_num + 1):
            g.player = next(g.player_loop)

        if self.player.num != g.player.num or self.player.name != g.player.name:
            raise Exception('Game did not copy Players correctly')

        g.turn_num = self.turn_num
        g.last_roll = self.last_roll

        return g
