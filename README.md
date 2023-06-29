# gym-cloud-sched-sim

## What is this?

This repository is an OpenAI Gym-compatible environment that provides a simulation of cloud scheduling. 
Drawing inspiration from Kubernetes, the environment incorporates similar components found in the Kubernetes ecosystem. 
It takes into consideration various factors related to resource allocation and utilization when scheduling tasks. 
The repository enables users to test the scheduling capabilities based on different scenarios or randomly generated workloads. 
It serves as a valuable tool for evaluating and improving cloud scheduling algorithms and strategies.
Lastly, it also contains GUI simulator that allows users to visualize the scheduling process which can help designing reward functions and debugging.

## Components

- Cluster: Cluster info with Nodes and Pods
- Nodes: resource info & deployed pod info
- Pods: have resource quota & schedule log
- Scheduler: make decisions based on states
- StressGen: Create new pods and queue them

## Installation
    
1. Install directly from the repository:
You can install it as a package from the repository directly using pip. (Recommended)
    ```bash
    pip install 'git+https://github.com/seonwookim92/gym_cloud_sched_sim.git'
    ```

2. Install from the source code:
You can also install it after downloading the source codes.
    ```bash
    git clone https://github.com/seonwookim92/gym_cloud_sched_sim.git
    cd gym_cloud_sched_sim
    pip install -e .
    ```

3. Use without installation:
You can also use the source codes without installing it.
    ```bash
    git clone https://github.com/seonwookim92/gym_cloud_sched_sim.git
    cd gym_cloud_sched_sim
    ```
    ```python
    from gym_cloud_sched_sim.envs.cloud_sched_sim_env import CloudSchedSimEnv
    env = CloudSchedSimEnv()
    ```

## Dependencies
It relies on the following packages:
- gym
- numpy
- matplotlib
- PyQt5 (If you want to use GUI simulator)

## To be added
- [ ] Add more scheduling algorithms
- [ ] Add more reward functions
- [ ] Add more scenarios
- [ ] (README) Adjustable parameters
- [ ] (README) GUI simulator usage
- [ ] (README) How to add new scheduling algorithms