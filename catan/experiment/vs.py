from tqdm import tqdm
from catan.game.game import Game, logger


def count_wins(game_results, player_name):
    return sum([1 if game['winner'] == player_name else 0 for game in game_results])


def win_ratio(game_results, player_name):
    return count_wins(game_results, player_name) / len(game_results)


def vs(players, num_games):
    game_results = []

    for _ in tqdm(range(num_games)):
        game = Game(players)
        game.start()

        game_results.append(game.to_dict())

    logger.info(
        message=f'Player {players[0].name} won {count_wins(game_results, players[0].name)}/{num_games} games against {players[1].name}',
        tags=['progress', 'training']
    )

    return game_results
