from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait
import timeit
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from random import shuffle

from catan import config, logger
from catan.files import dirname_models
from catan.game.actions import get_action_by_id, get_legal_action_ids, num_unique_actions
from catan.agents.agent import Agent

NUM_UNIQUE_ACTIONS = num_unique_actions()


def timed(func):
    def time_wrapper(*args, **kwargs):
        global timelog
        start = timeit.default_timer()
        ret = func(*args, **kwargs)
        duration = timeit.default_timer() - start

        if config['logging']['categories']['timing']:
            timelog += f'duration: {duration} | func: {func.__name__}\n'
            # print(f'duration: {duration} | func: {func.__name__}')

        return ret

    return time_wrapper


if config['training']['gpu']:
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
else:
    device = torch.device("cpu")


class GameState:
    _board_tensor = None
    num_layers = {
        'board': 5,
        'pieces': 6,
        'resource_cards': 10
    }

    def __init__(self, game):
        self.game = game

        board_tensor = self.get_board_tensor()
        piece_tensor = self.get_piece_tensor()
        resource_card_tensor = self.get_resource_card_tensor()
        complete_game_tensor = np.concatenate((board_tensor, piece_tensor, resource_card_tensor), axis=2)

        self._t = torch.from_numpy(complete_game_tensor).to(device)

    @property
    def tensor(self):
        return self._t

    @staticmethod
    def from_game(game):
        return GameState(game)._t

    @staticmethod
    def get_player_list_with_current_player_first(game):
        player_list = game.players.copy()
        i = player_list.index(game.player)
        player_list[0], player_list[i] = player_list[i], player_list[0]

        return player_list

    def get_board_tensor(self):
        if self._board_tensor is None:
            self._board_tensor = self.tensify_board()

        return self._board_tensor

    def tensify_board(self):
        board = self.game.board
        num_layers = GameState.num_layers['board']
        t = np.zeros((board.grid_height, board.grid_width, num_layers), dtype=int)

        for h in self.game.board.hexes:
            if h.resource.id >= 5: continue
            t[h.x][h.y][h.resource.id] = h.roll_chance

        return t

    def get_piece_tensor(self):
        board = self.game.board
        num_layers = GameState.num_layers['pieces']
        t = np.zeros((board.grid_height, board.grid_width, num_layers), dtype=int)

        for player in self.get_player_list_with_current_player_first(self.game):
            for road in player.roads:
                t[road.x][road.y][player.num*3] = 1
            for settlement in player.settlements:
                t[settlement.x][settlement.y][player.num*3 + 1] = 1
            for city in player.cities:
                t[city.x][city.y][player.num*3 + 2] = 1

        return t

    def get_resource_card_tensor(self):
        board = self.game.board
        num_layers = GameState.num_layers['resource_cards']
        t = np.zeros((board.grid_height, board.grid_width, num_layers), dtype=int)

        for player in self.get_player_list_with_current_player_first(self.game):
            for i, amt in enumerate(player.resource_cards):
                t[:, :, (player.num*5 + i)] = amt

        return t


class ConvBlock(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv1 = nn.Conv2d(in_channels=21, out_channels=32, kernel_size=5, stride=1, padding=2)
        self.bn1 = nn.BatchNorm2d(32)

    def forward(self, s):
        s = s.view(-1, 21, 22, 23).float()  # TODO investigate why this .float() is necessary
        s = self.conv1(s)
        s = self.bn1(s)
        s = F.relu(s)
        return s


class ResBlock(nn.Module):
    def __init__(self):
        super().__init__()

        inplanes = 32
        planes = 32

        self.layer1 = nn.Sequential(
            nn.Conv2d(inplanes, planes, kernel_size=5, stride=1, padding=2, bias=False),
            nn.BatchNorm2d(planes),
            nn.ReLU()
        )

        self.layer2 = nn.Sequential(
            nn.Conv2d(planes, planes, kernel_size=5, stride=1, padding=2, bias=False),
            nn.BatchNorm2d(planes)
        )

    def forward(self, x):
        residual = x
        out = self.layer1(x)
        out = self.layer2(out)
        out += residual
        out = F.relu(out)
        return out


class OutBlock(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv = nn.Conv2d(32, 3, kernel_size=1)
        self.bn = nn.BatchNorm2d(3)
        self.fc1 = nn.Linear(3 * 22 * 23, 16)
        self.fc2 = nn.Linear(16, 1)

        self.conv1 = nn.Conv2d(32, 16, kernel_size=1)
        self.bn1 = nn.BatchNorm2d(16)
        self.fc = nn.Linear(16 * 22 * 23, NUM_UNIQUE_ACTIONS)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, s):
        v = self.conv(s)
        v = self.bn(v)
        v = F.relu(v)
        v = v.view(-1, 3 * 22 * 23)  # batch_size X channel X height X width
        v = self.fc1(v)
        v = F.relu(v)
        v = self.fc2(v)
        v = torch.tanh(v)

        p = self.conv1(s)
        p = self.bn1(p)
        p = F.relu(p)
        p = p.view(-1, 22 * 23 * 16)
        p = self.fc(p)
        p = self.softmax(p)
        # p = p2.exp()

        return p, v


class AlphaLoss(nn.Module):
    def forward(self, policy_x, policy_y, val_x, val_y):
        policy_x = policy_x.view(-1)
        val_x = val_x.view(-1)

        policy_error = torch.sum((-policy_y * ((1e-8 + policy_x).log())))
        value_error = (val_x - val_y) ** 2
        total_error = (value_error + policy_error).mean()

        return total_error


class ZeroCNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv = ConvBlock()
        for block in range(19):
            setattr(self, "res_%i" % block, ResBlock())
        self.outblock = OutBlock()

    @staticmethod
    def get_path(net_version=None):
        version = f'_{net_version}' if net_version is not None else ''
        return dirname_models + f'/zero{version}.pt'

    def forward(self, s):
        s = self.conv(s)
        for block in range(19):
            s = getattr(self, "res_%i" % block)(s)
        s = self.outblock(s)

        return s

    def load(self, net_version=None):
        self.load_state_dict(torch.load(self.get_path(net_version)))
        self.to(device)

    def save(self, net_version=None):
        torch.save(self.state_dict(), self.get_path(net_version))


class MCTNode:
    # executor = ProcessPoolExecutor(max_workers=6)
    # executor = ThreadPoolExecutor(max_workers=6)

    # @timed
    def __init__(self, game, net, action_id=None, parent=None):
        logger.trace(f"id: {id(self)}", tags='mcts')
        self.game = game.copy()

        self.action_id = action_id
        if action_id is not None:
            func, args, kwargs = get_action_by_id(self.game, action_id)
            func(*args, **kwargs)

            while True:
                if self.game.can_roll():
                    self.game.player.roll()
                else:
                    legal_actions = self.game.player.get_legal_action_ids()
                    if len(legal_actions) == 1:
                        func, args, kwargs = get_action_by_id(self.game, legal_actions[0])
                        func(*args, **kwargs)
                    else:
                        break

        self.w = 0  # total q value
        self.n = 0  # number of visits

        self.parent = parent
        self.original_priors = None
        self.legal_action_ids = []
        self.priors = None
        self.children = [0] * num_unique_actions(game)

        self.expansion = None

        if self.game.is_finished:
            return

        if config['training']['parallel']:
            self.expansion = self.executor.submit(self.expand, net)
            self.expansion.node = self
            self.expansion.add_done_callback(MCTNode.backup_from_future)
        else:
            self.expand(net)
            self.backup()

    @property
    def q(self):
        if self.game.is_finished:
            return 1
        else:
            n = self.n or 1
            return self.w / n

    @property
    def pi(self):
        pi = np.asarray([0 if not isinstance(s, MCTNode) else s.n for s in self.children])
        pi_sum = np.sum(pi)
        if pi_sum > 0:
            pi = pi/pi_sum

        return pi

    # @timed
    def favorite_child(self, net):
        logger.trace(f'node id: {id(self)}', tags='mcts')

        MCTNode.favorite_child.count += 1
        expanding = []

        max_u, best_a = -float("inf"), -1
        for a in range(num_unique_actions(self.game)):
            if self.priors[a] == 0:
                continue

            s = self.children[a]
            if isinstance(s, MCTNode):
                # if s.expansion is not None and s.expansion.running():
                #     expanding.append(s)
                #     continue
                q = s.q if s.game.player.num == self.game.player.num else -s.q
                q *= config['training']['q_mult_factor']
                u = q + config['training']['c_puct'] * self.priors[a] * np.sqrt(self.n) / (1 + s.n)
            else:
                u = config['training']['c_puct'] * self.priors[a] * np.sqrt(self.n)

            if u > max_u:
                max_u = u
                best_a = a

        if best_a == -1:
            if len(expanding) > 0:
                logger.trace("Favorite child is already expanding. Waiting...", tags='mcts')
                node = np.random.choice(expanding)
                wait([node.expansion])
                return node
            else:
                logger.error("No legal moves detected", data={
                    "player_num": self.game.player.num,
                    "original_priors": self.original_priors.data.numpy().tolist(),
                    "legal_actions": get_legal_action_ids(self.game),
                    "priors": self.priors.data.numpy().tolist()
                })
                raise Exception(f"No legal moves for player {self.game.player.name}")

        a = best_a

        if not isinstance(self.children[a], MCTNode):
            logger.trace("Favorite child is new", tags='mcts')
            self.children[a] = MCTNode(self.game, net, a, parent=self)
        else:
            logger.trace("Favorite child is already expanded", tags='mcts')

        return self.children[a]

    # @timed
    def expand(self, net):
        logger.trace(f'node id: {id(self)}', tags='mcts')
        MCTNode.expand.count += 1

        with torch.no_grad():
            child_priors, value_estimate = net(GameState.from_game(self.game))

        self.priors = child_priors.view(-1).cpu()
        self.original_priors = self.priors.clone().detach()
        self.w = value_estimate.item()

        if self.parent is None:
            self.add_dirichlet_noise()

        # Mask illegal actions
        legal_action_ids = get_legal_action_ids(self.game)
        for i in range(len(self.priors)):
            if i not in legal_action_ids:
                self.priors[i] = 0

        if len(legal_action_ids) == 0:
            raise Exception('Legal action ids is empty')

        self.legal_action_ids = legal_action_ids

    def add_dirichlet_noise(self):
        eps = config['training']['dirichlet']['epsilon']

        alphas = (np.ones(NUM_UNIQUE_ACTIONS,) * config['training']['dirichlet']['alpha'])
        noise = torch.from_numpy(np.random.default_rng().dirichlet(alphas))

        self.priors = torch.add(self.priors * (1 - eps), noise * eps)
        # torch.add(self.priors * (1 - eps), noise * eps, out=self.priors)

    # @timed
    def backup(self):
        logger.trace(f'node id: {id(self)}', tags='mcts')

        val = self.q
        current = self

        while current.parent is not None:
            if current.game.player.num != current.parent.game.player.num:
                val *= -1

            current = current.parent

            current.n += 1
            current.w += val

    @staticmethod
    def backup_from_future(fut):
        fut.node.backup()

    def log(self):
        logger.debug(f'''\
self id: {id(self)}
cards: {self.game.player.resource_cards}
legal action ids: {self.legal_action_ids}

q: {self.q}
n: {self.n}

a, n, p, q, u:
{
        np.asarray([
            (
                i,
                s.n,
                self.priors[i].item(),
                s.q,
                s.q + config['training']['c_puct'] * self.priors[i].item() * np.sqrt(self.n) / (1 + s.n)
            )
                for i, s in enumerate(self.children) if isinstance(s, MCTNode)
        ])
}

original_priors:
{self.original_priors}
''')
        for node in self.children:
            if isinstance(node, MCTNode):
                node.log()
        logger.debug('up')


MCTNode.favorite_child.count = 0
MCTNode.expand.count = 0


class ZeroMCT:
    def __init__(self):
        self.root = None

    # @timed
    def search(self, game, net, num_iterations=None):
        start = timeit.default_timer()
        MCTNode.favorite_child.count = 0
        MCTNode.expand.count = 0
        num_iterations = num_iterations or config['training']['mcts_iterations']

        self.root = MCTNode(game, net)
        if config['training']['parallel']:
            wait([self.root.expansion])

        for i in range(num_iterations):
            logger.trace(f'Return to root - iteration {i}', tags='mcts')

            current = self.root
            while current.n > 0:
                current = current.favorite_child(net)
                if current.game.is_finished:
                    current.backup()
                    break

            current.n = 1

        end = timeit.default_timer()
        self.log(duration=end-start)

    @property
    def pi(self):
        return self.root.pi

    def log(self, duration):
        if config['logging']['categories']['mcts']:
            np.set_printoptions(linewidth=120, suppress=True, precision=8)
            torch.set_printoptions(linewidth=120, precision=8)
            logger.debug(f'Search Complete\n'
                         f'Player: {self.root.game.player.num} | {self.root.game.player.name}\n'
                         f'Duration: {duration}s\n'
                         f'Fav_child Count: {MCTNode.favorite_child.count}\n'
                         f'Expand Count: {MCTNode.expand.count}\n'
                         f'Duration/Fav_child: {duration / MCTNode.favorite_child.count}\n'
                         f'Duration/Expand: {duration / MCTNode.expand.count}')
            self.root.log()


class ZeroBot(Agent):
    raw_samples = []
    samples = []
    net = ZeroCNN().to(device)

    if config['training']['optimizer'] == 'Adam':
        optimizer = optim.Adam(
            net.parameters(),
            lr=config['training']['learning rate']
        )
    elif config['training']['optimizer'] == 'SGD':
        optimizer = optim.SGD(
            net.parameters(),
            lr=config['training']['learning rate'],
            momentum=config['training']['momentum']
        )
        scheduler = torch.optim.lr_scheduler.MultiStepLR(
            optimizer,
            milestones=config['training']['milestones'],
            gamma=config['training']['lr_gamma']
        )

    criterion = AlphaLoss().to(device)
    threshold = .55

    def __init__(self, net_version=None, name=None):
        super().__init__()

        if net_version is not None:
            self.net = ZeroCNN()
            self.net.load(net_version)
            self.name = name or f'Zero_v{net_version}'
        else:
            self.net = ZeroBot.net
            self.name = name or 'Zero'

        self.mct = ZeroMCT()

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, player):
        self._player = player
        player.name = self.name

    @property
    def game(self):
        return self._player.game

    @staticmethod
    def cook_samples(winner):
        ZeroBot.samples += [(raw[0], raw[1], 1 if raw[2] == winner else -1) for raw in ZeroBot.raw_samples]
        ZeroBot.raw_samples = []

    def choose_action(self):
        logger.debug('Starting to choose an action', tags='planning')

        self.mct.search(self.game, self.net)

        # inputs, pi_target, value_target
        ZeroBot.raw_samples.append((
            GameState.from_game(self.mct.root.game),
            self.mct.root.pi,
            self.player
        ))

        action_id = np.random.choice(range(len(self.mct.pi)), p=self.mct.pi)

        logger.debug(f'Action ID chosen: {action_id}', tags='planning')

        return get_action_by_id(self.game, action_id)

    @staticmethod
    def train():
        batch_size = len(ZeroBot.samples) // 10
        shuffle(ZeroBot.samples)

        for epoch in range(config['training']['num_epochs']):

            running_loss = 0.0
            for i, sample in enumerate(ZeroBot.samples):
                inputs, pi_target, v_target = sample

                inputs = inputs.to(device)
                pi_target = torch.as_tensor(pi_target).to(device)
                v_target = torch.as_tensor(v_target).to(device)

                # zero the parameter gradients
                ZeroBot.optimizer.zero_grad()

                # forward + backward + optimize
                pi_out, v_out = ZeroBot.net(inputs)
                loss = ZeroBot.criterion(pi_out, pi_target, v_out, v_target)
                loss.backward()
                ZeroBot.optimizer.step()
                ZeroBot.scheduler.step()

                # print statistics
                running_loss += loss.item()
                if i % batch_size == batch_size - 1:  # print every 100 mini-batches
                    logger.debug(f'[{epoch + 1}, {i + 1}] loss: {running_loss / batch_size}', tags='training')
                    running_loss = 0.0

        ZeroBot.samples = []
