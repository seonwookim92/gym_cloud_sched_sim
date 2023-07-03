import numpy as np

def get_reward(env):

    # Simple reward function
    # 1. Gives disadvantage when the pod is not scheduled.
    # 2. Gives advantage when the pod is scheduled to the node with less utilization than average.

    is_scheduled = env.info['is_scheduled']

    util = {}
    for node in env.cluster.nodes:
        cpu_ratio, mem_ratio = node.get_node_rsrc_ratio()
        util[node.node_name] = {
            "cpu": cpu_ratio,
            "mem": mem_ratio
        }

    # AvgUtil = mean of cpu and mem utilization of all node
    avg_cpu = round(np.mean([util[node]["cpu"] for node in util]), 2)
    avg_mem = round(np.mean([util[node]["mem"] for node in util]), 2)


    # Compare the selected node's utilization with the mean utilization
    # If the selected node's utilization is less than the mean utilization, give advantage
    is_cpu_less_than_avg = util[env.cluster.nodes[env.last_action - 1].node_name]["cpu"] < avg_cpu if env.info['is_scheduled'] else False
    is_mem_less_than_avg = util[env.cluster.nodes[env.last_action - 1].node_name]["mem"] < avg_mem if env.info['is_scheduled'] else False

    # If the pending pod is just listed, do not give disadvantage
    if env.cluster.pending_pods:
        if env.cluster.pending_pods[0].spec['arrival_time'] == env.time:
            is_scheduled = True
    if env.last_action == 0:
        is_scheduled = True

    # Reward = a * is_scheduled + b * is_cpu_less_than_avg + c * is_mem_less_than_avg
    a = -5
    b = 1
    c = 1

    reward = a * (not is_scheduled) + b * is_cpu_less_than_avg + c * is_mem_less_than_avg
    reward = round(reward, 2)

    return reward