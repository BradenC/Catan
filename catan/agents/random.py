from random import choice as random_choice, shuffle

from catan.game.piece import City, Road, Settlement
from catan.logging import logger
from catan.agents.agent import Agent


class RandomBot(Agent):
    """
    Bot that chooses a move randomly from all legal moves
    Each move possibility is considered separately
    e.g. if there are 3 legal road placements, and the player can afford a road, they will count as 3 possible moves
    """

    def choose_action(self):
        ####
        # Check for required actions
        if self.game.can_roll():
            return self.player.roll, [], {}

        if self.game.can_end_turn():
            end_turn_action = [(self.player.end_turn, [], {})]
        else:
            end_turn_action = []

        ####
        # Find all legal actions

        trade_actions = [(self.player.trade, trade, {}) for trade in find_legal_trade_actions(self.game)]
        road_actions = [(self.player.build, [Road, lane], {}) for lane in find_legal_roads(self.game)]
        settlement_actions = [(self.player.build, [Settlement, point], {}) for point in find_legal_settlements(self.game)]
        city_actions = [(self.player.build, [City, point], {}) for point in find_legal_cities(self.game)]

        legal_actions = end_turn_action + trade_actions + road_actions + settlement_actions + city_actions

        ####
        # Choose one random action

        action = random_choice(legal_actions)

        ####
        # Log chosen action

        logger.debug(
            data={
                'ending actions': len(end_turn_action),
                'trade actions': len(trade_actions),
                'road actions': len(road_actions),
                'settlement actions': len(settlement_actions),
                'city actions': len(city_actions),
            },
            tags='planning'
        )

        ####
        # Return chosen action
        return action


def find_legal_trade_actions(game):
    legal_trades = []
    resource_ids = range(0, 4)

    for from_resource_id, from_resource_amount in enumerate(game.player.resource_cards):
        if from_resource_amount >= 4:
            for to_resource_id in resource_ids:
                legal_trades.append([from_resource_id, to_resource_id])

    shuffle(legal_trades)
    return legal_trades


def find_legal_roads(game):
    legal_lanes = []

    if game.player.can_afford(Road):
        for lane in game.board.lanes:
            if lane.is_reachable_by(game.player) and not lane.piece:
                legal_lanes.append(lane)

    shuffle(legal_lanes)
    return legal_lanes


def find_legal_settlements(game):
    legal_points = []

    if game.player.can_afford(Settlement):
        for point in game.board.points:
            if (point.is_reachable_by(game.player) or game.is_setup_phase()) and not point.is_crowded():
                legal_points.append(point)

    shuffle(legal_points)
    return legal_points


def find_legal_cities(game):
    legal_points = []

    if game.player.can_afford(City):
        for point in game.board.points:
            if isinstance(point.piece, Settlement) and point.owner == game.player:
                legal_points.append(point)

    shuffle(legal_points)
    return legal_points
