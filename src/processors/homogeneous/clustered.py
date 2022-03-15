from typing import Tuple


class Core:
    def __init__(self, cc_id: int, core_id: int):
        self.cc_id = cc_id
        self.core_id = core_id
        self.log = []
        self.idle = True
        self.proc_node = -1
        self.remain_proc_time = 0

    def allocate(self, node_i, exec_time) -> None:
        self.idle = False
        self.proc_node = node_i
        self.remain_proc_time = exec_time

    def process(self) -> None:
        if(not self.idle):
            self.remain_proc_time -= 1
            if(self.remain_proc_time == 0):
                self.idle = True
                self.proc_node = -1


class Cluster:
    def __init__(self, cc_id: int, num_cores: int):
        self.cc_id = cc_id
        self.cores = []
        for core_id in range(1, num_cores+1):
            self.cores.append(Core(self.cc_id, core_id))

    def process(self) -> None:
        for core in self.cores:
            core.process()

    def is_idle(self) -> Tuple[bool, int]:
        for core in self.cores:
            if(core.idle):
                return True, core.core_id
            return False, None


class CluesteredProcessor:
    def __init__(self, num_clusters, num_cores, inout_ratio):
        self.inout_ratio = inout_ratio
        self.clusters = []
        for cluster_id in range(1, num_clusters+1):
            self.clusters.append(Cluster(cluster_id, num_cores))

    def process(self):
        for cluster in self.clusters:
            cluster.process()

    def is_idle(self) -> Tuple[bool, Tuple[int, int]]:
        for cluster in self.clusters:
            result, core_id = cluster.is_idle()
            if(result):
                return True, (cluster.cc_id, core_id)
