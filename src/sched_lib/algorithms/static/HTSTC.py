import copy
import sys
import networkx as nx
from typing import List

from sched_lib.exceptions import UnimplementedError
from sched_lib.algorithms.dag_utils import convert_to_ave_comm_dag, set_ranku
from sched_lib.processors.homogeneous.cluster import CluesteredProcessor
from sched_lib.scheduler.list_scheduler import ListSchedulerToClusteredProcessor


class HTSTCListSchedulerToClusteredProcessor(ListSchedulerToClusteredProcessor):
    def __init__(self, dag: nx.DiGraph, processor: CluesteredProcessor, sched_list: List[int]) -> None:
        super().__init__(dag, processor, sched_list)

    def schedule_using_task_duplication(self) -> None:
        # Get normal sched_log
        G = copy.deepcopy(self.G)
        P = copy.deepcopy(self.P)
        sched_list = copy.deepcopy(self.sched_list)
        normal_scheduler = ListSchedulerToClusteredProcessor(G, P, sched_list)
        normal_scheduler.schedule()
        normal_sched_log = normal_scheduler.sched_log

        # Communication between CCs (debug)
        for node_i in self.G.nodes:
            succs = self.G.succ[node_i]
            for succ_i in succs:
                if(normal_sched_log[str(node_i)]['allocated_cc_id'] != normal_sched_log[str(succ_i)]['allocated_cc_id']):
                    # print(f'between CCs edge: ({node_i}, {succ_i})')
                    # print(f'comm: {self.G.edges[node_i, succ_i]["comm"]}')
                    # print(f'EST - EFT: {normal_sched_log[str(succ_i)]["start_time"] - normal_sched_log[str(node_i)]["finish_time"]}')
                    if(normal_sched_log[str(succ_i)]["start_time"] - normal_sched_log[str(node_i)]["finish_time"]
                            < self.G.edges[node_i, succ_i]["comm"]):
                        raise UnimplementedError('TODO: Task Duplication')

        self.schedule()  # HACK


class HTSTC:
    def __init__(self, dag: nx.DiGraph, inout_ratio: float) -> None:
        self.G = copy.deepcopy(dag)
        self.inout_ratio = inout_ratio

    def task_clustering(self) -> None:
        perform_clustering_flag = True
        while(perform_clustering_flag):
            for node_i in self.G.nodes:
                succs = list(self.G.succ[node_i])
                if(len(self.G.pred[node_i])==1 and len(succs)==1):
                    single_succ = succs[0]
                    if(len(self.G.pred[single_succ])==1 and len(self.G.succ[single_succ])==1):
                        if(self.G.edges[node_i, single_succ]['comm'] >= self.G.nodes[single_succ]['exec']):
                            # Perform clustering
                            self.G.nodes[node_i]['exec'] += (self.G.nodes[single_succ]['exec']
                                                             + int(self.G.edges[node_i, single_succ]['comm']))
                            new_succ = list(self.G.succ[single_succ])
                            self.G.add_edge(node_i, new_succ[0], comm=self.G.edges[single_succ, new_succ[0]]['comm'])
                            self.G.remove_node(single_succ)
                            perform_clustering_flag = True
                            break
            perform_clustering_flag = False

    def _set_pre(self) -> None:
        for node_i in self.G.nodes:
            comm_plus_ranku_list = []
            for succ_i in self.G.succ[node_i]:
                comm_plus_ranku_list.append(self.G.edges[node_i, succ_i]['comm'] + self.G.nodes[succ_i]['ranku'])
            if(comm_plus_ranku_list):
                self.G.nodes[node_i]['pre'] = max(comm_plus_ranku_list)
            else:
                self.G.nodes[node_i]['pre'] = 0

    def get_sched_list(self) -> List[int]:
        self.task_clustering()
        set_ranku(self.G)
        self._set_pre()
        pre_dict = nx.get_node_attributes(self.G, 'pre')
        sorted_by_pre = sorted(pre_dict.items(),
                                key=lambda i: i[1],
                                reverse=True)

        return [k for k, v in sorted_by_pre]
