import numpy as np


alphas = (np.ones(5,) * 2)
print(np.random.default_rng().dirichlet(alphas, 10))
