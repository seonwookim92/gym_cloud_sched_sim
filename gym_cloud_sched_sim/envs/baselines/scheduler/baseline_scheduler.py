import os, sys
base_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
sys.path.append(base_path)

# from gym_cloud_sched_sim.envs.baselines.model import *

import importlib

class BaselineScheduler:
    def __init__(self, env, model_name='default', eval=False):
        self.env = env
        self.eval = eval

        self.model_name = model_name.split('.')[0]
        self.model = self.load_model(model_name)

    def decision(self, env):
        action = self.model.predict(env)
        return action
    
    def load_model(self, model_name):
        if '.py' in model_name:
            model_name = model_name.split('.')[0]
        module_path = 'gym_cloud_sched_sim.envs.baselines.model.{}'.format(model_name)
        if model_name == 'default':
            model = importlib.import_module(module_path).Model(self.env, self.eval)
        else:
            model = importlib.import_module(module_path).Model(self.env)
        return model