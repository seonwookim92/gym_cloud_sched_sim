# import time
# from kubernetes import client, config

import os, sys
base_path = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(base_path)


class SimStressGen:
    def __init__(self, scenario_file="scenario-5l-5m-1000p-10m.csv"):

        self.scenario_file = scenario_file
        self.scenario = self.load_scenario(scenario_file)

    def load_scenario(self, scenario_file):
        # Load scenario
        scenario_path = os.path.join(base_path, "scenarios/", scenario_file)
        scenario = []
        with open(scenario_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                scenario.append(line.strip().split(",") + [0, 0])
        return scenario
    
    
    def create_pod(self, time): # time: sec-based time, scenario: list of jobs
        pod_spec_li = []
        for pod_spec in self.scenario:
            if time > int(pod_spec[1]) and pod_spec[-1] == 0:
                pod_spec[-1] = 1
                pod_spec_li.append(pod_spec)
        return pod_spec_li
            
        
    def reset(self):
        self.scenario = self.load_scenario(self.scenario_file)
