# import os, sys
# base_path = os.path.join(os.path.dirname(__file__), "..", "..")
# sys.path.append(base_path)

class Node:
    def __init__(self, node_idx, node_name ,cpu_pool, mem_pool, debug=False):
        self.debug = debug

        self.node_idx = node_idx
        self.node_name = node_name

        self.spec = {
            "cpu_pool": cpu_pool,
            "mem_pool": mem_pool,
        }
        self.status = {
            "cpu_util": 0,
            "mem_util": 0,
            "cpu_ratio": 0,
            "mem_ratio": 0,
            "n_pod": 0,
            "running_pods": []
        }

    def get_node_rsrc_ratio(self):
        return self.status["cpu_ratio"], self.status["mem_ratio"]

    def alloc(self, pod, time):
        chk_cpu = self.spec["cpu_pool"] >= self.status["cpu_util"] + pod.spec["cpu_req"]
        chk_mem = self.spec["mem_pool"] >= self.status["mem_util"] + pod.spec["mem_req"]
        if chk_cpu and chk_mem:
            self.status["cpu_util"] += pod.spec["cpu_req"]
            self.status["mem_util"] += pod.spec["mem_req"]
            self.status["cpu_ratio"] = round(self.status["cpu_util"] / self.spec["cpu_pool"], 2)
            self.status["mem_ratio"] = round(self.status["mem_util"] / self.spec["mem_pool"], 2)
            self.status["n_pod"] += 1
            self.status["running_pods"].append(pod)

            if self.debug:
                print("(Node) Allocate pod {} to node {}".format(pod.pod_name, self.node_name))

            return True
        else:
            if self.debug:
                print("(Node) Failed to allocate pod {} to node {}".format(pod.pod_name, self.node_name))
            return False

    def dealloc(self, pod, time):
        self.status["cpu_util"] -= pod.spec["cpu_req"]
        self.status["mem_util"] -= pod.spec["mem_req"]
        self.status["cpu_ratio"] = round(self.status["cpu_util"] / self.spec["cpu_pool"], 2)
        self.status["mem_ratio"] = round(self.status["mem_util"] / self.spec["mem_pool"], 2)
        self.status["n_pod"] -= 1
        self.status["running_pods"].remove(pod)

        if self.debug:
            print("(Node) Deallocate pod {} from node {}".format(pod.pod_name, self.node_name))

    def reset(self):
        self.status["cpu_util"] = 0
        self.status["mem_util"] = 0
        self.status["cpu_ratio"] = 0
        self.status["mem_ratio"] = 0
        self.status["n_pod"] = 0

        # Delete all pods
        for pod in self.status["running_pods"]:
            del pod

        self.status["running_pods"] = []