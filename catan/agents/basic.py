from catan.game.piece import City, Road, Settlement
from catan.agents.agent import Agent
from catan.agents.random import\
    find_legal_trade_actions,\
    find_legal_roads,\
    find_legal_settlements,\
    find_legal_cities


class BasicBot(Agent):
    """
    Bot that chooses a move based on a basic priority over all legal moves
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

        legal_trade_actions = find_legal_trade_actions(self.game)
        if legal_trade_actions:
            return self.player.trade, legal_trade_actions[0], {}

        if self.game.can_end_turn():
            return self.player.end_turn, [], {}


def best_point(player, points):
    return max([(point, calc_point_value(player, point)) for point in points], key=lambda x: x[1])[0]


def calc_point_value(player, point):
    res_gen_current = [res + 1 for res in player.resource_generation]
    res_gen_discounted = [a/b for (a, b) in zip(point.resource_generation, res_gen_current)]

    return sum(res_gen_discounted)
