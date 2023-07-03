import os, sys
base_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(base_path)

import gym
import numpy as np
import importlib
import matplotlib.pyplot as plt

from gym_cloud_sched_sim.envs.components.cluster import Cluster
from gym_cloud_sched_sim.envs.components.pod import Pod
from gym_cloud_sched_sim.envs.utils.sim_stress_gen import SimStressGen
from gym_cloud_sched_sim.envs.utils.sim_random_stress_gen import SimRandomStressGen

class CloudSchedSimEnv(gym.Env):
    def __init__(self, reward='train_default', scenario='random', n_node=5, cpu_pool=50000, mem_pool=50000):
        self.reward_fn = self.get_reward_fn(reward)
        self.scenario = scenario
        self.stress_gen = self.get_stress_gen(scenario)

        self.n_node = n_node
        self.cpu_pool = cpu_pool
        self.mem_pool = mem_pool

        self.cluster = Cluster(n_node, cpu_pool, mem_pool)

        self.time = 0
        
        self.reward = 0
        self.done = False
        self.observation_space = gym.spaces.Box(low=0.0, high=1.0, shape=(n_node * 2 + 2,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(n_node + 1)

        self.action_map = {'0': 'standby'}
        for i in range(n_node):
            self.action_map[str(i + 1)] = 'node-{}'.format(i+1)

        self.info = {
            'last_pod' : None,
            'is_scheduled' : None
        }

        self.last_action = 0
        self.last_cluster_state = {
            "nodes": {
            },
            "pods": {
                1: [0.0, 0.0]
            }
        }
        for i in range(n_node):
            self.last_cluster_state["nodes"][i+1] = [1.0, 1.0]



    def get_reward_fn(self, reward):
        if '.py' in reward:
            reward = reward.split('.')[0]
        reward_fn = importlib.import_module(os.path.join('gym_cloud_sched_sim', 'envs', 'rewards', reward).replace('/', '.'))
        return reward_fn
    
    def get_stress_gen(self, scenario):
        if scenario == 'random':
            return SimRandomStressGen()
        else:
            return SimStressGen(scenario)
        
    def update_last_cluster_state(self):
        raw_state = self.get_state()
        self.last_cluster_state = {
            "nodes": {
            },
            "pods": {
                1: [raw_state[-2], raw_state[-1]]
            }
        }
        for i in range(self.n_node):
            self.last_cluster_state["nodes"][i+1] = [raw_state[i*2], raw_state[i*2+1]]

    def get_reward(self):
        reward = self.reward_fn.get_reward(self)
        return reward
    
    def get_state(self):
        node_state = []
        for node in self.cluster.nodes:
            node_cpu_ratio = node.get_node_rsrc_ratio()[0]
            node_mem_ratio = node.get_node_rsrc_ratio()[1]
            node_state += [1 - node_cpu_ratio, 1 - node_mem_ratio]

        if  self.cluster.pending_pods:
            pending_pod = self.cluster.pending_pods[0]
            pending_pod_state = [pending_pod.spec["cpu_ratio"], pending_pod.spec["mem_ratio"]]
        else:
            pending_pod_state = [0, 0]

        state = node_state + pending_pod_state

        return np.array(state, dtype=np.float32)
    
    def get_done(self):
        if self.scenario == 'random':
            len_scenario = 1000
            len_scheduled = len(self.cluster.terminated_pods + self.cluster.running_pods)
        else:
            len_scenario = len(self.stress_gen.scenario)
            len_scheduled = len(self.cluster.terminated_pods + self.cluster.running_pods)
        # print(f"len_scenario: {len_scenario}, len_scheduled: {len_scheduled}")
        
        if len_scenario == len_scheduled:
            self.done = True
        elif self.time - len_scenario > 3000:
            self.done = True
        else:
            self.done = False
        return self.done
    
    def step(self, action):

        # Update last cluster state
        self.update_last_cluster_state()

        # Update last action
        self.last_action = action

        # Update cluster
        self.cluster.update(self.time)

        # Initialize info
        self.info = {
            'last_pod' : None,
            'is_scheduled' : None
        }

        # Do action
        pending_pods = self.cluster.pending_pods

        if pending_pods:

            pending_pod = pending_pods[0]

            try:
                deploy_node = self.cluster.get_node(self.action_map[str(action)])
            except:
                deploy_node = None
            if deploy_node:
                is_scheduled = self.cluster.deploy_pod(pending_pod, deploy_node, self.time)
                self.info = {
                    'last_pod' : pending_pod, # always have values
                    'is_scheduled' : is_scheduled # True / False
                }
            else:
                self.info = {
                    'last_pod' : pending_pod, # None
                    'is_scheduled' : None # None
                }
        else: # No pending pods
            if action == 0:
                self.info = {
                    'last_pod' : None, # None
                    'is_scheduled' : None # False
                }
            else:
                self.info = {
                    'last_pod' : None, # None
                    'is_scheduled' : False # None
                }

        # Get reward
        self.reward = self.get_reward()

        # Get done
        self.done = self.get_done()


        self.time += 1
        is_scheduled = None
        
        new_pod_spec = self.stress_gen.create_pod(self.time)
        node_spec = self.cluster.nodes[0].spec
        if new_pod_spec:
            self.cluster.queue_pod(new_pod_spec, node_spec)

        # Get state
        state = self.get_state()


        return state, self.reward, self.done, self.info

    def reset(self):
        self.time = 0
        self.cluster.reset()
        self.stress_gen.reset()

        return self.get_state()