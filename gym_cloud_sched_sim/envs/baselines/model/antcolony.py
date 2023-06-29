# Strategy: Ant Colony Optimization
# Objective: Balancing resource usage(CPU Memory) in a node, and balancing resource usage between nodes
#
# Algorithm:
# 1. Initialize the pheromone matrix with a constant value
# 2. For each iteration:
#   2.1. For each ant:
#     2.1.1. Select the next node based on the probability of the pheromone matrix
#     2.1.2. Update the pheromone matrix
#   2.2. Evaporate the pheromone matrix
# 3. Select the best node
#

import numpy as np
import random

class Model:
    def __init__(self, env=None):
        self.env = env
        self.n_node = len(env.cluster.nodes) if env else 5

        self.n_feature = 2
        self.n_ant = 10
        self.n_iteration = 20

        self.ant_kind = ['cpu_ratio', 'mem_ratio']

        self.ant_colony = {}
        for ak in self.ant_kind:
            self.ant_colony[ak] = [{'name': f'ant{i}', 'feature': ak, 'current_node': None, 'quality': 0} for i in range(self.n_ant)]
        # for i in range(self.n_ant):
        #     ant = {'name': f'ant{i}', 'feature': self.ant_kind[i % self.n_feature], 'current_node': None, 'quality': 0}
        #     self.ant_colony.append(ant)

        self.pheromone_matrix_ak = {}
        for ak in self.ant_kind:
            self.pheromone_matrix_ak[ak] = np.ones((self.n_node, self.n_node)) * 0.1
        self.pheromone_matrix = np.ones((self.n_node, self.n_node)) * 0.1

        self.solutions = {}
        for ak in self.ant_kind:
            self.solutions[ak] = {}
            for ant in self.ant_colony[ak]:
                self.solutions[ak][ant['name']] = []

        self.evaporate_rate = 0.1

    def reset(self):
        # print("RESET")
        # self.ant_colony = []
        # for i in range(self.n_ant):
        #     ant = {'name': f'ant{i}', 'feature': self.ant_kind[i % self.n_feature], 'current_node': None, 'quality': 0}
        #     self.ant_colony.append(ant)

        # self.pheromone_matrix = np.ones((self.n_node, self.n_node)) * 0.1

        self.ant_colony = {}
        for ak in self.ant_kind:
            self.ant_colony[ak] = [{'name': f'ant{i}', 'feature': ak, 'current_node': None, 'quality': 0} for i in range(self.n_ant)]

        self.pheromone_matrix_ak = {}
        for ak in self.ant_kind:
            self.pheromone_matrix_ak[ak] = np.ones((self.n_node, self.n_node)) * 0.1

        self.pheromone_matrix = np.ones((self.n_node, self.n_node)) * 0.1

        self.solutions = {}
        for ak in self.ant_kind:
            self.solutions[ak] = {}
            for ant in self.ant_colony[ak]:
                self.solutions[ak][ant['name']] = []

    def balance_pheromone_matrix(self):
        for r in range(self.n_node):
            for c in range(self.n_node):
                if r != c:
                    # Avg(pheromone_matrix[ak][r][c] - Std(pheromone_matrix[ak][r][c]))
                    self.pheromone_matrix[r][c] = np.mean([self.pheromone_matrix_ak[ak][r][c] for ak in self.ant_kind]) - np.std([self.pheromone_matrix_ak[ak][r][c] for ak in self.ant_kind])

    def evaluate_fitness(self, env, solution, feature):
        fitness = 0
        for s in solution[1:]:
            feature_value = env.cluster.get_pod(s[0]).spec[feature] + 0.01
            node_value = env.cluster.nodes[s[1]-1].status[feature] + 0.01
            fitness += ((1 - node_value) / feature_value) ** 0.5
            # fitness = round(fitness, 2)
        # print(f"fitness!: {fitness}")
        return fitness
    
    def get_valid_nodes(self, env, pod_name, feature):
        valid_nodes = []
        for node in env.cluster.nodes:
            if 1 - node.status[feature] >= env.cluster.get_pod(pod_name).spec[feature]:
                valid_nodes.append(node)
        return valid_nodes
    
    def compute_probabilities(self, env, valid_nodes, current_node, pheromone_matrix, feature):
        probabilities = []
        for node in valid_nodes:
            if node.node_idx == current_node.node_idx:
                probabilities.append(0)
            else:
                probabilities.append(pheromone_matrix[current_node.node_idx-1][node.node_idx-1])
        if sum(probabilities) == 0:
            probabilities = [1.0 / len(valid_nodes) for node in valid_nodes]
        else:
            probabilities = [p / sum(probabilities) for p in probabilities]
        # print(f"probabilities: {probabilities}")
        return probabilities
    
        # pheromones = [pheromone_matrix[current_node.node_idx-1][node.node_idx-1] for node in valid_nodes]
        # print(f"pheromones: {[round(p, 2) for p in pheromones]}")
        # heuristics = [1 - node.status[feature] for node in valid_nodes]
        # # heuristics = [round(1.0 / (node.node_idx + 1),2) for node in valid_nodes]
        # print(f"heuristics: {heuristics}")
        # probabilities = [round(pheromones[i] * heuristics[i],2) for i in range(len(valid_nodes))]
        # print(f"probabilities: {probabilities}")
        # sum_probabilities = sum(probabilities)
        # if sum_probabilities == 0:
        #     probabilities = [round(1.0 / len(valid_nodes),2) for node in valid_nodes]
        # return probabilities
    
    def select_next_node(self, env, valid_nodes, probabilities):
        next_node = None
        if len(valid_nodes) <= 0:
            return next_node
        if len(valid_nodes) == 1:
            next_node = valid_nodes[0]
        else:
            next_node_idx = np.random.choice(len(valid_nodes), 1, p=probabilities)[0]
            next_node = valid_nodes[next_node_idx]
        return next_node
    
        # cum_probabilities = np.cumsum(probabilities)
        # print(f"cum_probabilities: {cum_probabilities}")
        # random_number = np.random.rand()
        # # print(f"random_number: {random_number}")
        # for i in range(len(cum_probabilities)):
        #     if random_number < cum_probabilities[i]:
        #         return valid_nodes[i]
        # return None
            
    def update_pheromone_matrix(self, env):
        # print("=============================================")
        for ak in self.ant_kind:
            for ant in self.ant_colony[ak]:
                # print('---------------------------------------------')
                solution = self.solutions[ak][ant['name']]
                # print(f"solution: {solution}")    
                if len(solution) <= 1:
                    continue
                for i in range(len(solution)-1):
                    # print(f"solution[{i}]: {solution[i]}")
                    node_prev = env.cluster.nodes[solution[i][1]-1]
                    node_prev_idx = node_prev.node_idx - 1
                    # print(f"solution[{i+1}]: {solution[i+1]}")
                    node_next = env.cluster.nodes[solution[i+1][1]-1]
                    node_next_idx = node_next.node_idx - 1
                    solution_til_i = solution[:i+1]
                    fitness_til_i = self.evaluate_fitness(env, solution_til_i, ant['feature'])
                    # print(f"[{solution[i][1]}] -> [{solution[i+1][1]}] => {fitness_til_i}")
                    self.pheromone_matrix_ak[ak][node_prev_idx][node_next_idx] += fitness_til_i


                
    def evaporate_pheromone_matrix(self): 
        for ak in self.ant_kind:
            self.pheromone_matrix_ak[ak] = self.pheromone_matrix_ak[ak] * (1 - self.evaporate_rate)

    def select_best_node(self, env):
        best_node = None
        best_node_idx = 0
        best_pheromone = 0

        for ak in self.ant_kind:
            for ant in self.ant_colony[ak]:
                solution = self.solutions[ak][ant['name']]
                pheromone = self.pheromone_matrix[solution[-2][1]-1][solution[-1][1]-1]
                node_idx = solution[-1][1]
                if pheromone > best_pheromone:
                    best_pheromone = pheromone
                    best_node_idx = node_idx
                elif pheromone == best_pheromone:
                    if np.random.rand() < 0.5:
                        best_pheromone = pheromone
                        best_node_idx = node_idx

        best_node = env.cluster.nodes[best_node_idx-1]

        return best_node
    
        # for node in env.cluster.nodes:
        #     solution = self.solutions[f'ant{node.node_idx-1}']
        #     # print(f"solutions[{node.node_idx-1}]: {[s[1] for s in solution]}")
        #     fitness = 0
        #     for feature in self.ant_kind:
        #         fitness += self.evaluate_fitness(env, solution, feature)

        #     print(f"fitness: {fitness}")

        #     if fitness > best_fitness:
        #         best_node = node
        #         best_fitness = fitness
        #         print(f"BEST: {best_node.node_idx} ({best_fitness})")
        #     elif fitness == best_fitness:
        #         # Randomly select one
        #         if np.random.rand() < 0.5:
        #             best_node = node
        #             best_fitness = fitness
        #             print(f"BEST: {best_node.node_idx} ({best_fitness})")
        # return best_node

    
    def predict(self, env):
        self.reset()
        if len(env.cluster.pending_pods) == 0:
            return 0
        pod = env.cluster.pending_pods[0]
        for ak in self.ant_kind:
            for ant in self.ant_colony[ak]:
                ant['current_node'] = random.choice(env.cluster.nodes)
                ant['quality'] = 0
                self.solutions[ak][ant['name']] = []
                self.solutions[ak][ant['name']].append((pod.pod_name, ant['current_node'].node_idx))

        for i in range(self.n_iteration):
            for ak in self.ant_kind:
                for ant in self.ant_colony[ak]:
                    valid_nodes = self.get_valid_nodes(env, pod.pod_name, ant['feature'])

                    probabilities = self.compute_probabilities(env, valid_nodes, ant['current_node'], self.pheromone_matrix_ak[ak], ant['feature'])
                    ant['current_node'] = self.select_next_node(env, valid_nodes, probabilities)
                    if ant['current_node'] is None:
                        ant['current_node'] = random.choice(env.cluster.nodes)
                    self.solutions[ak][ant['name']].append((pod.pod_name, ant['current_node'].node_idx))
    
            self.update_pheromone_matrix(env)
            self.evaporate_pheromone_matrix()

        self.balance_pheromone_matrix()


        # print("Updated pheromone matrix:")
        # for i in range(self.n_node):
        #     print([round(e,2) for e in self.pheromone_matrix[i]])

        best_node = self.select_best_node(env)
        if best_node is None:
            # print("best_node is None")
            return 0
        else:
            # print(f"best_node: {best_node.node_idx}")
            best_node_idx = best_node.node_idx
            return best_node_idx