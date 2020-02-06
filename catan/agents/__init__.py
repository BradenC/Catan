from catan.agents.agent import Agent
from catan.agents.random import RandomBot
from catan.agents.basic import BasicBot
from catan.agents.human import Human
from catan.agents.simple import SimpleBot
from catan.agents.zero import ZeroBot

from catan.agents.cnn import CNN
from catan.agents.mct import MCT


def make_model(name):
    if name.lower() == 'basic':
        return BasicBot()
    elif name.lower() == 'simple':
        return SimpleBot()
    elif name.lower() == 'random':
        return RandomBot()
    elif name.lower() == 'zero':
        return ZeroBot()
    else:
        return Human(name)
