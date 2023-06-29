# import os, sys
# base_path = os.path.join(os.path.dirname(__file__), "..", "..")
# sys.path.append(base_path)

# from kube_sim_gym.components.pod import Pod
# from kube_sim_gym.components.node import Node

from gym_cloud_sched_sim.envs.components.pod import Pod
from gym_cloud_sched_sim.envs.components.node import Node


class Cluster:
    def __init__(self, n_node, cpu_pool, mem_pool, debug=False):
        self.debug = debug

        self.n_node = n_node

        self.nodes = []
        for i in range(n_node):
            node = Node(i+1, "node-{}".format(i+1), cpu_pool, mem_pool)
            self.nodes.append(node)
        if self.debug:
            print("(Cluster) Cluster initialized with {} nodes".format(self.n_node))
            print("(Cluster) Node spec: cpu_pool={}, mem_pool={}".format(cpu_pool, mem_pool))
            print(f"(Cluster) Nodes: {[n.node_name for n in self.nodes]}")

        self.pending_pods = []
        self.running_pods = []
        self.terminated_pods = []

    def get_pod(self, pod_name):
        all_pods = self.pending_pods + self.running_pods + self.terminated_pods
        for pod in all_pods:
            if pod.pod_name == pod_name:
                if self.debug:
                    print(f"(Cluster) Found pod {pod_name} in cluster")
                    print(f"(Cluster) Pod spec: {pod.spec}")
                return pod
            
    def get_node(self, node_name):
        for node in self.nodes:
            if node.node_name == node_name:
                if self.debug:
                    print(f"(Cluster) Found node {node_name} in cluster")
                    print(f"(Cluster) Node spec: {node.spec}")
                return node
        return None

    def queue_pod(self, pod_spec_li, node_spec):
        for pod_spec in pod_spec_li:
            pod = Pod(pod_spec, node_spec)
            if self.debug:
                print(f"(Cluster) Queuing pod {pod.pod_name}")
            self.pending_pods.append(pod)

    def deploy_pod(self, pod, node, time):
        is_allocated = node.alloc(pod, time)
        if is_allocated:
            pod.deploy(node, time)
            self.running_pods.append(pod)
            self.pending_pods.remove(pod)
            if self.debug:
                print(f"(Cluster) Deployed pod {pod.pod_name} to node {node.node_name}")
            return True
        else:
            if self.debug:
                print(f"(Cluster) Failed to deploy pod {pod.pod_name} to node {node.node_name}")
            return False

    def terminate_pod(self, pod, node, time):
        node.dealloc(pod, time)
        pod.terminate(time)
        self.running_pods.remove(pod)
        self.terminated_pods.append(pod)
        if self.debug:
            print(f"(Cluster) Terminated pod {pod.pod_name} from node {node.node_name}")

    def update(self, time):
        # Terminating pods that have exceeded their TTL
        for pod in self.running_pods:
            if pod.is_expired(time):
                node = self.get_node(pod.status["node_name"])
                self.terminate_pod(pod, node, time)

    def reset(self):
        self.pending_pods = []
        self.running_pods = []
        self.terminated_pods = []
        for node in self.nodes:
            node.reset()
