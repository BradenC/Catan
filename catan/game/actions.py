from catan.game.piece import City, Road, Settlement


def num_unique_actions(game=None):
    """
    Number of unique actions possible in a game
    = end_turn(1) + road actions(72) + settlement actions(54) + city actions(54) + trade actions(20)
    = 201
    """
    if game is not None:
        return 1 + len(game.board.lanes) + 2 * len(game.board.points) + 20
    else:
        return 201


def find_legal_trade_actions(game):
    legal_trades = []
    resource_ids = range(0, 4)

    for from_resource_id, from_resource_amount in enumerate(game.player.resource_cards):
        if from_resource_amount >= 4:
            for to_resource_id in resource_ids:
                legal_trades.append([from_resource_id, to_resource_id])

    return legal_trades


def find_legal_lanes_for_roads(game):
    legal_lanes = []

    if game.player.can_afford(Road):
        for lane in game.board.lanes:
            if lane.is_reachable_by(game.player) and not lane.piece:
                legal_lanes.append(lane)

    return legal_lanes


def find_legal_points_for_settlements(game):
    legal_points = []

    if game.player.can_afford(Settlement):
        for point in game.board.points:
            if (point.is_reachable_by(game.player) or game.is_setup_phase()) and not point.is_crowded():
                legal_points.append(point)

    return legal_points


def find_legal_points_for_cities(game):
    legal_points = []

    if game.player.can_afford(City):
        for point in game.board.points:
            if isinstance(point.piece, Settlement) and point.owner == game.player:
                legal_points.append(point)

    return legal_points


def trade_id_to_pair(trade_id):
    from_res = trade_id // 4
    to_res = trade_id % 4

    if from_res <= to_res:
        to_res = to_res + 1 if to_res < 4 else 0

    return from_res, to_res


def trade_pair_to_id(pair):
    from_res, to_res = pair

    trade_id = from_res * 4 + to_res
    if from_res < to_res:
        trade_id -= 1

    return trade_id


def get_legal_action_ids(game):
    """Find all legal moves for the current player"""
    road_start = 1
    settlement_start = road_start + len(game.board.lanes)
    city_start = settlement_start + len(game.board.points)
    trade_start = city_start + len(game.board.points)

    end_turn = [0] if game.can_end_turn() else []

    road_actions = [lane.id + road_start for lane in find_legal_lanes_for_roads(game)]
    settlement_actions = [point.id + settlement_start for point in find_legal_points_for_settlements(game)]
    city_actions = [point.id + city_start for point in find_legal_points_for_cities(game)]
    trade_actions = [trade_pair_to_id(resource) + trade_start for resource in find_legal_trade_actions(game)]

    if game.is_setup_phase():
        trade_actions = []
    # print('getting legal action ids')
    # print(f'resources: {game.player.resource_cards}')
    # print(f'end_turn: {end_turn}')
    # print(f'roll: {roll}')
    # print(f'road actions: {road_actions}')
    # print(f'settlement actions: {settlement_actions}')
    # print(f'city actions: {city_actions}')
    # print(f'trade actions: {trade_actions}')

    return end_turn + road_actions + settlement_actions + city_actions + trade_actions


def get_action_by_id(game, action_id):
    end_turn = 0
    road_start = 1
    settlement_start = road_start + len(game.board.lanes)
    city_start = settlement_start + len(game.board.points)
    trade_start = city_start + len(game.board.points)

    func = None
    args = []
    kwargs = {}

    if action_id == end_turn:
        func = game.player.end_turn

    elif action_id < trade_start:
        func = game.player.build

        if action_id < settlement_start:
            args = (Road, game.board.lanes[action_id - road_start])
        elif action_id < city_start:
            args = (Settlement, game.board.points[action_id - settlement_start])
        elif action_id < trade_start:
            args = (City, game.board.points[action_id - city_start])

    else:
        func = game.player.trade

        trade_id = action_id - trade_start
        args = trade_id_to_pair(trade_id)

    return func, args, kwargs
