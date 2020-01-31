from catan.models.random import RandomBot
from catan.models.basic import BasicBot
from catan.models.simple import SimpleBot
from catan.models.zero import ZeroBot


def model_thing():
    while True:
        yield SimpleBot
        yield ZeroBot
