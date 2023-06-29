# import time
# from kubernetes import client, config

import os, sys
base_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(base_path)

import random


# from kube_stress_generator.job_gen import JobGenerator
# from kube_gym.utils import monitor

class SimRandomStressGen:
    def __init__(self):

        self.pod_idx = 0
        self.last_quequed_time = 0
    
    def create_pod(self, time): # time: sec-based time, scenario: list of jobs

        if random.random() < 0.15:
            return []
        if self.pod_idx >= 1000:
            return []

        duration = random.randint(1, 3)
        # Generate integer between 1 and 30, but more on the lower side
        cpu = random.randint(1, 30) ** 2
        mem = random.randint(1, 30) ** 2
        cpu = random.randint(1, 30) / 100
        mem = random.randint(1, 30) / 100

        pod_spec = [self.pod_idx, time, duration, cpu, mem, 0, 0]

        self.pod_idx += 1
        self.last_quequed_time = time

        return [pod_spec]
        
    def reset(self):
        self.pod_idx = 0
        self.last_scheduled_time = 0