import numpy as np

def get_reward(env, cluster, action, is_scheduled, time, debug=False):

    util = {}
    for node in cluster.nodes:
        cpu_ratio, mem_ratio = node.get_node_rsrc_ratio()
        util[node.node_name] = {
            "cpu": cpu_ratio,
            "mem": mem_ratio
        }

    # AvgUtil = mean of cpu and mem utilization of all node
    avg_cpu = round(np.mean([util[node]["cpu"] for node in util]), 2)
    avg_mem = round(np.mean([util[node]["mem"] for node in util]), 2)
    avg_util = round((avg_cpu + avg_mem) / 2, 2)
    if debug:
        print(f"(Stragegy_Default) Avg CPU util: {avg_cpu}")
        print(f"(Stragegy_Default) Avg Mem util: {avg_mem}")
        print(f"(Stragegy_Default) Avg Util: {avg_util}")

    # ImBalance = summation of standard deviation of each resource in all nodes
    std_cpu = round(np.std([util[node]["cpu"] for node in util]), 2)
    std_mem = round(np.std([util[node]["mem"] for node in util]), 2)
    imbalance = round(std_cpu + std_mem, 2)
    if debug:
        print(f"(Stragegy_Default) Std CPU util: {std_cpu}")
        print(f"(Stragegy_Default) Std Mem util: {std_mem}")
        print(f"(Stragegy_Default) Imbalance: {imbalance}")

    # Reward = a*AvgUtil - b*ImBalance
    a = 1
    b = 1
    reward = round(a * avg_util - b * imbalance, 2)
    if debug:
        print(f"(DRS) Reward: {reward}")

    return reward