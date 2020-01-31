from enum import Enum


class Resource(Enum):
    WOOD = 0
    BRICK = 1
    GRAIN = 2
    SHEEP = 3
    ORE = 4
    WATER = 5
    DESERT = 6


def resource_shortname(res):
    if res is Resource.WOOD:
        return 'W'
    elif res is Resource.BRICK:
        return 'B'
    elif res is Resource.GRAIN:
        return 'G'
    elif res is Resource.SHEEP:
        return 'S'
    elif res is Resource.ORE:
        return 'O'
    elif res is Resource.WATER:
        return '  -  '
    elif res is Resource.DESERT:
        return ' DES '


def resource_color(res):
    if res == Resource.WOOD:
        return "#262"
    if res == Resource.BRICK:
        return "#E75"
    if res == Resource.GRAIN:
        return "#FC2"
    if res == Resource.SHEEP:
        return "#9B3"
    if res == Resource.ORE:
        return "#678"
    if res == Resource.DESERT:
        return "#FCA"
    if res == Resource.WATER:
        return "#04A"


HexTiles = [
    Resource.WOOD,
    Resource.GRAIN,
    Resource.ORE,
    Resource.ORE,
    Resource.SHEEP,
    Resource.SHEEP,
    Resource.BRICK,
    Resource.GRAIN,
    Resource.WOOD,
    Resource.GRAIN,
    Resource.WOOD,
    Resource.DESERT,
    Resource.SHEEP,
    Resource.BRICK,
    Resource.ORE,
    Resource.BRICK,
    Resource.GRAIN,
    Resource.SHEEP,
    Resource.WOOD,
]

HexNumbers = [6, 2, 5, 3, 9, 10, 8, 8, 4, 11, 3, 0, 10, 5, 6, 4, 9, 12, 11]
