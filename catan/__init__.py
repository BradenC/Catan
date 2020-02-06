import json
with open('Catan/catan/config.json', 'r') as f:
    config = json.load(f)

from catan.logging import logger
from catan.game.game import Game
from catan.files import dirname
