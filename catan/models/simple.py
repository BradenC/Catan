from catan.game import Resource
from catan.game.piece import City, Road, Settlement

from catan.models.model import Model

from catan.models.random import\
    find_legal_roads,\
    find_legal_settlements,\
    find_legal_cities


class SimpleBot(Model):
    """
    Bot that chooses a move based on a basic priority over all legal moves
    Also sorts legal trades
    """

    def choose_action(self):
        if self.game.can_roll():
            return self.player.roll, [], {}

        legal_cities = find_legal_cities(self.game)
        if self.player.can_afford(City) and self.player.settlements:
            return self.player.build, [City, best_point(self.player, legal_cities)], {}

        legal_settlements = find_legal_settlements(self.game)
        if self.player.can_afford(Settlement) and legal_settlements:
            return self.player.build, [Settlement, best_point(self.player, legal_settlements)], {}

        legal_roads = find_legal_roads(self.game)
        if self.player.can_afford(Road) and legal_roads:
            return self.player.build, [Road, legal_roads[0]], {}

        if min(self.player.resource_cards) == 0 and max(self.player.resource_cards) >= 4:
            return self.player.trade, find_best_trade_actions(self.player), {}

        if self.game.can_end_turn():
            return self.player.end_turn, [], {}


def best_point(player, points):
    return max([(point, calc_point_value(player, point)) for point in points], key=lambda x: x[1])[0]


def calc_point_value(player, point):
    res_gen_current = [res + 1 for res in player.resource_generation]
    res_gen_discounted = [a/b for (a, b) in zip(point.resource_generation, res_gen_current)]

    return sum(res_gen_discounted)


def find_best_trade_actions(player):
    resources_to_give = [key for (key, val) in enumerate(player.resource_cards) if val >= 4]
    resources_to_receive = [key for (key, val) in enumerate(player.resource_cards) if val == 0]

    return Resource(resources_to_give[0]), Resource(resources_to_receive[0])
