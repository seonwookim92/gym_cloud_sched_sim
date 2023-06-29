import random
import numpy as np

class Model:
    def __init__(self, env=None, eval=False):
        self.env = env
        self.eval = eval

    def predict(self, env):
        if self.eval:
            available_actions = [1, 2, 3, 4, 5]
            # available_actions = self.get_available_actions(env)
        else:
            available_actions = self.get_available_actions(env)
        
        prioritized_actions = self.prioritize_actions(env, available_actions)
        return prioritized_actions[0]
    
    def get_confidence(self, env):
        score = {}
        # If there is no pending pod, the confidence for action 0 is 1
        if env.cluster.pending_pods == []:
            score[0] = 1
            for idx, action in enumerate([1, 2, 3, 4, 5]):
                score[action] = 0
        else:
            score[0] = 0
            for idx, action in enumerate([1, 2, 3, 4, 5]):
                score[action] = self.scoring_action(env, action)

        # Return array
        confidence = np.array([score[0], score[1], score[2], score[3], score[4], score[5]])
        return confidence

    def get_available_actions(self, env):

        if env.cluster.pending_pods == []:
            return [0]

        pod = env.cluster.pending_pods[0]
        ret = []
        
        for idx, node in enumerate(env.cluster.nodes):
            cpu_avail = node.spec["cpu_pool"] - node.status["cpu_util"]
            mem_avail = node.spec["mem_pool"] - node.status["mem_util"]
            if pod.spec["cpu_req"] <= cpu_avail and pod.spec["mem_req"] <= mem_avail:
                ret.append(idx+1)
        if not ret:
            ret.append(0)
        return ret
    
    def prioritize_actions(self, env, actions):
        score = {}
        for idx, action in enumerate(actions):
            score[action] = self.scoring_action(env, action)
        
        sorted_score = sorted(score.items(), key=lambda x: x[1], reverse=True)
        max_score = sorted_score[0][1]
        if np.array(sorted_score)[:, 1].tolist().count(max_score) > 1:
            max_score_actions = [x[0] for x in sorted_score if x[1] == max_score]
            # Shuffle the actions with the same score
            random.shuffle(max_score_actions)
            return max_score_actions

        return [x[0] for x in sorted_score]

    def scoring_action(self, env, action):
        # Score_cpu = (cpu_pool - cpu_util - pod's cpu_req) / cpu_pool
        # Score_mem = (mem_pool - mem_util - pod's mem_req) / mem_pool
        # Score = (Score_cpu + Score_mem) / 2
        if action == 0:
            return 0
        node = env.cluster.nodes[action-1]
        pod = env.cluster.pending_pods[0] if env.cluster.pending_pods else None
        pod_cpu_req = pod.spec["cpu_req"] if pod else 0
        pod_mem_req = pod.spec["mem_req"] if pod else 0
        score_cpu = (node.spec["cpu_pool"] - node.status["cpu_util"] - pod_cpu_req) / node.spec["cpu_pool"]
        score_mem = (node.spec["mem_pool"] - node.status["mem_util"] - pod_mem_req) / node.spec["mem_pool"]
        score1 = (score_cpu + score_mem) / 2

        # Score2 = (1 - abs(cpu_util - mem_util)) / 2
        score2 = (1 - abs(node.status["cpu_ratio"] - node.status["mem_ratio"])) / 2

        # print(f"Action({action}) score : {score1} /  {score2}")
        # Score = (Score1 + Score2) / 2
        score = round((score1 + 2 * score2) / 2, 2)

        return score