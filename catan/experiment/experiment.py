from datetime import datetime
import json
from tqdm import tqdm

from catan import config
from catan.experiment.plots import plot_results
from catan.game.game import Game


def run():
    timestring = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    results_filename = f"Catan/catan/experiment/results/{timestring}"

    results = {
        'config': config,
        'games': []
    }

    for _ in range(config['experiment_reps']):
        for _ in tqdm(range(config['games_per_experiment'])):
            g = Game()
            g.start()

            results['games'].append(g.to_jsonable())

    with open(results_filename, 'a+') as f:
        json.dump(results, f)

    if config['games_per_experiment'] % 20 == 0:
        plot_results(results)
