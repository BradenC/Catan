import numpy as np
import matplotlib.pyplot as plt

from catan import config

"""
These graphs show statistics about the results from many games played between two opponents.

The games are pooled such that each data points represents the average results across multiple games.
"""

# The number of points to be shown on the graph
num_groups = 50

# The number of games to be combined into each data point
group_size = config['games_per_experiment'] // num_groups

plot_players = []
player_color = ['b', 'g']
player_shape = ['o', 'o']


class PlotPlayer:
    def __init__(self, name, color, shape):
        self.name = name
        self.color = color
        self.shape = shape

    @staticmethod
    def from_results(results):
        return [PlotPlayer(player['name'], player_color[player['num']], player_shape[player['num']])
                for player in results['games'][0]['players']]


def pool(lst):
    """
    return a new array that is an average grouping of the old array

    e.g.
    pool([1, 2, 3, 4, 5, 6], 3)
    => (1 + 2 + 3)/3, (4 + 5 + 6)/3]
    => [2, 5]
    """
    return [sum(lst[i:i+group_size])/group_size for i in range(0, len(lst), group_size)]


def get_player_record(players, name):
    """
    Given an array of players, return the one matching the given name
    """

    return next(player for player in players if player['name'] == name)


def plot_win_ratio(results, ax):
    """
    Bar chart showing the ratio of wins between the two players
    """

    ax.set_title(f'Win Ratio')

    p1_wins = [1 if game['winner'] == plot_players[0].name else 0 for game in results['games']]
    p2_wins = [1 if game['winner'] == plot_players[1].name else 0 for game in results['games']]

    p1_wins = pool(p1_wins)
    p2_wins = pool(p2_wins)

    rang = np.arange(num_groups)
    width = .8

    ax.bar(rang, p1_wins, width, label=plot_players[0].name, color=plot_players[0].color)
    ax.bar(rang, p2_wins, width, label=plot_players[1].name, color=plot_players[1].color, bottom=p1_wins)

    ax.set_yticks([])
    ax.set_xticks([])

    ax.legend()


def plot_victory_points(results, ax):
    """
    Dot graph showing how many victory points each player achieved
    """

    ax.set_title(f'Average VP ({group_size} games)')
    ax.set_ylabel('Victory Points')

    for player in plot_players:
        player.victory_points = [get_player_record(game['players'], player.name)['victory_points']
                                 for game in results['games']]
        ax.plot(pool(player.victory_points), f'{player.shape}{player.color}', label=player.name)

    ax.set_ylim(0, 10)

    ax.set_xticks([])

    ax.legend()


def plot_turn_length(results, ax):
    """
    Line graph showing how many milliseconds each player took while deciding their turn
    """

    ax.set_yticks([])
    ax.set_xticks([])

    ax.set_title('Turn Length (ms)')


def plot_game_length(results, ax):
    """
    Line graphs showing how many turns each game took
    """

    ax.set_title('Turns Per Game')

    turns_per_game = [game['num_turns'] for game in results['games']]

    ax.plot(pool(turns_per_game))

    ax.set_xticks([])

    ax.set_ylim(0)


def plot_results(results):
    global plot_players

    plot_players = PlotPlayer.from_results(results)

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

    plot_win_ratio(results, ax1)
    plot_victory_points(results, ax2)
    plot_turn_length(results, ax3)
    plot_game_length(results, ax4)

    fig.canvas.set_window_title('Graphs of Catan')
    fig.suptitle('Average Agent Performance')

    plt.show()
