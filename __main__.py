import argparse
import os
import sys
import tkinter

from datetime import datetime

from catan import config
from catan.experiment import vs, train
from catan.game.game import Game

from catan.agents import Human, make_model, ZeroBot


# Path setup
current_path = os.path.abspath('..')
parent_path = os.path.dirname(current_path)

sys.path.append(parent_path)
sys.path.append(current_path)


# Parse Arguments
parser = argparse.ArgumentParser()

parser.add_argument('--players', nargs='+', default=[], help='List of names of players')
parser.add_argument('--graphics', nargs="?", const=1, help='Whether to display the game graphically')
parser.add_argument('--turn_delay', default=1, type=int, help="Minimum time between computer moves (seconds)")
parser.add_argument('--num_games', default=1, help='Number of games to be played')

args = parser.parse_args()

# Game type depends on number of players
players = []
if len(args.players) == 0:
    mode = 'train'
elif len(args.players) >= 2:
    mode = 'play'
    players = [make_model(name) for name in args.players]
else:
    raise Exception('How are you supposed to play with just one person?')

# Graphics are always on if a human is playing
one_human = any(isinstance(player, Human) for player in players)
graphics = bool(args.graphics or one_human)

print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3])

if graphics:
    # Add vars to config (just for logging, tbh)
    config['graphics']['display'] = True
    config['graphics']['turn_delay_s'] = args.turn_delay

    # Setup canvas
    CANVAS_WIDTH = 1600
    CANVAS_HEIGHT = 900
    root = tkinter.Tk()
    c = tkinter.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    c['bg'] = 'black'
    rect = c.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill="black")

    # Setup game
    if mode == 'play':
        game = Game(players, canvas=c, turn_delay_s=args.turn_delay)
        c.after(0, game.start)
    elif mode == 'train':
        c.after(0, train, ZeroBot, c, args.turn_delay)
    else:
        raise Exception(f'Unknown mode encountered: {mode}')

    c.pack()
    root.mainloop()

else:
    if mode == 'train':
        train(ZeroBot)
    else:
        vs(players, args.num_games)
