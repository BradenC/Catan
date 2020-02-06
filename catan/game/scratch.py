import numpy as np
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait
from time import sleep


class MCTNode:
    x = 0

    def __init__(self, num=0):
        self.locked = False
        self.x = num
        self.n = 0
        self.q = 1

    def expand(self):
        self.locked = True
        sleep(2)
        self.x *= -1
        self.locked = False


def favorite_child(children):
    n = 2
    priors = np.random.rand(len(children))

    max_u, best_a = -float("inf"), -1
    locked_nodes = []
    for a in range(len(children)):
        if priors[a] == 0:
            continue

        s = children[a]
        if isinstance(s, MCTNode):
            if s.locked:
                locked_nodes += s
                u = float("-inf")
            else:
                u = s.q + 4 * priors[a] * np.sqrt(n) / (1 + s.n)
        else:
            u = 4 * priors[a] * np.sqrt(n)
        if u > max_u:
            max_u = u
            best_a = a

    print('Picking a... ', end='')
    if best_a == -1:
        if locked_nodes:
            print('locked node')
            return np.random_choice(locked_nodes)
        else:
            raise Exception('No valid children')

    elif not isinstance(children[best_a], MCTNode):
        print('new node')
        children[best_a] = MCTNode(best_a)

    else:
        print('expanded node')

    return children[best_a]


def MCTSearch():
    num_unique_actions = 3
    children = [0] * num_unique_actions
    num_iterations = 4
    fut = None
    # with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    with ProcessPoolExecutor(max_workers=10) as executor:
        for _ in range(num_iterations):
            child = favorite_child(children)
            child.expand()
            # child.fut = executor.submit(child.expand)


if __name__ == '__main__':
    MCTSearch()
