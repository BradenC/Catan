import json

from tqdm import tqdm

from catan import config, Game, logger
from catan.agents import RandomBot, SimpleBot
from catan.experiment.vs import vs, win_ratio
from catan.experiment.plot import plot_results
from catan.files import dirname

results_filename = dirname + '/results'


def process_results(game_results, plot=True):
    record = {
        'config': config,
        'games': game_results
    }

    with open(results_filename, 'a+') as f:
        json.dump(record, f)
        f.write('\n')

    if plot:
        plot_results(game_results)


def train(agent, canvas=None, turn_delay_s=None):
    vs_random_results = []
    vs_simple_results = []

    logger.info(data=config)

    for i in range(config['training']['iterations']):
        for _ in tqdm(range(config['training']['episodes_per_iteration'])):
            winner = Game(
                players=[agent(name='ZeroOne'), agent(name='ZeroTwo')],
                canvas=canvas,
                turn_delay_s=turn_delay_s
            ).start().winner
            agent.cook_samples(winner)

        logger.debug(f'Finished round {i} of episodes', tags=['progress', 'training'])

        agent.net.save(i)

        agent.train()

        p1, p2 = agent(), agent(net_version=i)
        vs_results = vs([p1, p2], config['training']['games_per_improvement_test'])

        if win_ratio(vs_results, p1.name) > agent.threshold:
            agent.net.load(i)

        vs_random_results += vs([agent(), RandomBot()], config['training']['games_per_ground_test'])
        vs_simple_results += vs([agent(), SimpleBot()], config['training']['games_per_ground_test'])

    logger.info('Finished', tags='progress')
    agent.net.save()

    process_results(vs_random_results)
    process_results(vs_simple_results)
