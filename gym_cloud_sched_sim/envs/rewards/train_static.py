import numpy as np

def get_available_nodes(cluster_state):
    if cluster_state['pods'][1] == [0, 0]:
        return [0]
    
    last_pod_state = cluster_state['pods'][1]

    ret = []
    
    if last_pod_state == [0, 0]:
        ret = [i + 1 for i in range(len(cluster_state['nodes']))]
        return ret
    
    for idx, node_idx in enumerate(cluster_state['nodes']):
        node_state = cluster_state['nodes'][node_idx]
        if (node_state[0] - last_pod_state[0] > 0) and (node_state[1] - last_pod_state[1] > 0):
            ret.append(idx+1)
    if not ret:
        ret.append(0)
    return ret

def get_reward(env):

    # Feature extraction
    is_scheduled = env.info['is_scheduled']
    last_cluster_state = env.last_cluster_state
    last_pod_state = last_cluster_state['pods'][1]
    last_action = env.last_action
    util = {}
    for node in env.cluster.nodes:
        cpu_ratio, mem_ratio = node.get_node_rsrc_ratio()
        util[node.node_name] = {
            "cpu": cpu_ratio,
            "mem": mem_ratio
        }

    # pwd : Penalty for the wrong decision
    if is_scheduled == False:
        pwd = -1
    elif is_scheduled == None and last_pod_state != [0, 0]:
        if get_available_nodes(last_cluster_state) == [0]:
            pwd = 0
        else:
            pwd =  -1
    else:
        pwd =  0
    
    # rbd1 : Resource Balance Degree across nodes
    std_cpu = round(np.std([util[node]["cpu"] for node in util]), 2)
    std_mem = round(np.std([util[node]["mem"] for node in util]), 2)
    rbd1 = (std_cpu ** 2 + std_mem ** 2) ** 0.5
    rbd1 = - round(rbd1, 2)

    # rbd2 : Resource Difference of the scheduled(tried) node
    if last_action == 0:
        rbd2 = 0
    else:
        print(f"last_cluster_state: {last_cluster_state}")
        _cpu = last_cluster_state['nodes'][last_action][0] - last_pod_state[0]
        _mem = last_cluster_state['nodes'][last_action][1] - last_pod_state[1]
        rbd2 = abs(_cpu - _mem)
        rbd2 = - round(rbd2, 2)

    # reward = pwd / 3 + rbd1 / 2 + rbd2
    reward = pwd + rbd1 + rbd2

    reward = round(reward, 2)

    return reward