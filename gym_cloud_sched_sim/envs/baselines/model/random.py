import random

class Model:
    def __init__(self, env=None):
        pass

    def predict(self, env):
        state = env.get_state()
        n_actions = env.action_space.n
        return random.randint(0, n_actions - 1)
