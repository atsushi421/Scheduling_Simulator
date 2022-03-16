from typing import Tuple


class Core:
    def __init__(self, cc_id: int, core_id: int):
        self.cc_id = cc_id
        self.core_id = core_id
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

    def get_shortest_remain(self) -> Tuple[int, int]:
        min_remain_proc_time = self.cores[0].remain_proc_time
        min_core_id = self.cores[0].core_id
        for core in self.cores[1:]:
            if(core.remain_proc_time < min_remain_proc_time):
                min_remain_proc_time = core.remain_proc_time
                min_core_id = core.core_id

        return min_remain_proc_time, min_core_id


class CluesteredProcessor:
    def __init__(self, num_clusters, num_cores, inout_ratio):
        self.num_of_cores = num_cores
        self.num_of_clusters = num_clusters
        self.inout_ratio = inout_ratio
        self.clusters = []
        for cc_id in range(1, self.num_of_clusters+1):
            self.clusters.append(Cluster(cc_id, self.num_of_cores))

    def process(self) -> None:
        for cluster in self.clusters:
            cluster.process()

    def get_shortest_remain(self, cc_id: int) -> Tuple[int, int]:
        return self.clusters[cc_id - 1].get_shortest_remain()
