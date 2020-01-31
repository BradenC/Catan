import os
import sys
import tkinter

from catan import config
from catan.experiment import experiment
from catan.game.game import Game


# Set up paths so OS can find other files

current_path = os.path.abspath('..')
parent_path = os.path.dirname(current_path)

sys.path.append(parent_path)
sys.path.append(current_path)


# Create a canvas on which to draw the game

if config['graphics']:
    CANVAS_WIDTH = 1600
    CANVAS_HEIGHT = 900

    root = tkinter.Tk()
    c = tkinter.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
    c['bg'] = 'black'
    rect = c.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill="black")

    game = Game(
        num_humans=config['num_players_human'],
        num_bots=config['num_players_cpu'],
        canvas=c
    )

    c.after(0, game.start)
    c.pack()
    root.mainloop()

else:
    experiment.run()
