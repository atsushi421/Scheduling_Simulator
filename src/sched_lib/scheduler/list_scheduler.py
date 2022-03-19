import json
import copy
import sys
import networkx as nx
from typing import List, Union
from abc import ABCMeta, abstractmethod

from sched_lib.exceptions import AlgorithmError


class ListScheduler(metaclass=ABCMeta):
    def __init__(self, dag: nx.DiGraph, processor, sched_list: List[int]):
        self.G = copy.deepcopy(dag)
        self.P = copy.deepcopy(processor)
        self.sched_list = copy.deepcopy(sched_list)
        self.sched_log = {}
        self._current_time = 0

    @abstractmethod
    def schedule(self):
        pass

    @abstractmethod
    def _allocate_task(self, node_i):
        pass

    @abstractmethod
    def dump_log_to_json(self, filename: str) -> None:
        pass

    def _get_finish_time(self, node_i) -> int:
        try:
            return self.sched_log[str(node_i)]['finish_time']
        except KeyError:
            raise AlgorithmError(f'node {node_i} does not allocated.')

    def _wait_one(self) -> None:
        self._current_time += 1
        self.P.process()

    def get_makespan(self) -> int:
        ft_list = []
        for log in self.sched_log.values():
             ft_list.append(log['finish_time'])

        return max(ft_list)

    def get_cpu_usage(self) -> float:
        sum_exec = 0
        for node_i in range(self.G.number_of_nodes()):
            sum_exec += self.G.nodes[node_i]['exec']


class ListSchedulerToClusteredProcessor(ListScheduler):
    def __init__(self, dag: nx.DiGraph, processor, sched_list: List[int]):
        super().__init__(dag, processor, sched_list)

    def _get_allocated_cc_id(self, node_i) -> int:
        try:
            return self.sched_log[str(node_i)]['allocated_cc_id']
        except KeyError:
            raise AlgorithmError(f'node {node_i} does not allocated.')

    def _get_latest_data_arrival_time(self, cc_id, node_i) -> int:
        latest_data_arrival_time = self._current_time
        for pred_i in self.G.pred[node_i]:
            comm_time = None
            if(self._get_allocated_cc_id(pred_i) == cc_id):
                comm_time = self.G.edges[pred_i, node_i]['comm']
            else:
                comm_time = int(self.G.edges[pred_i, node_i]['comm'] * self.P.inout_ratio)
            data_arrival_time = self._get_finish_time(pred_i) + comm_time
            if(data_arrival_time > latest_data_arrival_time):
                latest_data_arrival_time = data_arrival_time

        return latest_data_arrival_time

    def _allocate_task(self, node_i, cc_id, core_id) -> None:
        exec_time = self.G.nodes[node_i]['exec']
        dest_cluster = self.P.clusters[cc_id-1]
        dest_cluster.cores[core_id-1].allocate(node_i, exec_time)
        self.sched_log[str(node_i)] = {'allocated_cc_id': cc_id,
                                       'allocated_core_id': core_id,
                                       'start_time': self._current_time,
                                       'finish_time': self._current_time + exec_time}

    def schedule(self) -> None:
        while(self.sched_list):
            head = self.sched_list.pop(0)

            # Find the core that can be allocated most early
            dest_cc_id = None
            dest_core_id = None
            earliest_allocatable_time = sys.maxsize
            for cluster in self.P.clusters:
                latest_data_arrival_time = self._get_latest_data_arrival_time(cluster.cc_id, head)
                shortest_remain, core_id = self.P.get_shortest_remain(cluster.cc_id)
                allocatable_time = max(latest_data_arrival_time,
                                       self._current_time + shortest_remain)
                if(allocatable_time < earliest_allocatable_time):
                    earliest_allocatable_time = allocatable_time
                    dest_cc_id = cluster.cc_id
                    dest_core_id = core_id

            while(self._current_time != earliest_allocatable_time):
                self._wait_one()
            self._allocate_task(head, dest_cc_id, dest_core_id)

    def dump_log_to_json(self, filename: str) -> None:  # HACK
        format_log = {'coreNum': self.P.num_of_clusters * self.P.num_of_cores,
                      'makespan': self.get_makespan(),
                      'taskSet': []}
        for node_i, log in self.sched_log.items():
            format_log['taskSet'].append({'coreID': self.P.num_of_cores * (log['allocated_cc_id']-1) + log['allocated_core_id'],
                                          'taskName': f'task_{node_i}',
                                          'startTime': log['start_time'],
                                          'executionTime': log['finish_time'] - log['start_time']})

        with open(f'{filename}.json', 'w') as fp:
            json.dump(format_log, fp, indent=4)
