import random

class Model:
    def __init__(self, env=None):
        self.last_node_scheduled = -1

    def predict(self, env):
        # Round robin
        self.last_node_scheduled = (self.last_node_scheduled + 1) % len(env.cluster.nodes) + 1
        return self.last_node_scheduled
