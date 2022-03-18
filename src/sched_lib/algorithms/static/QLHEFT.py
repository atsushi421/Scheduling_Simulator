import random
import copy
import time
import networkx as nx
import numpy as np
from numpy import random as rnd
from typing import List

from  sched_lib.algorithms.dag_utils import set_ranku, convert_to_ave_comm_dag, convert_to_virtual_entry_dag, convert_to_virtual_exit_dag


class QLHEFT:
    def __init__(self, dag: nx.DiGraph, alpha: float, gamma: float):
        self.G = copy.deepcopy(dag)
        self._virtual_entry_i = convert_to_virtual_entry_dag(self.G)
        self._virtual_exit_i = convert_to_virtual_exit_dag(self.G)
        set_ranku(self.G)
        self.alpha = alpha
        self.gamma = gamma
        self.q_table = np.zeros((self.G.number_of_nodes(), self.G.number_of_nodes()))
        self.learning_log = {}

    def learn(self, max_episode: int) -> None:
        learning_start_time = time.time()

        for _e in range(max_episode):
            # Initial setting
            current_state = self._virtual_entry_i
            choose_nodes = {self._virtual_entry_i}
            choosable_nodes = list(self.G.succ[current_state])

            # Learning
            for _k in range(self.G.number_of_nodes() - 1):
                # Choice node
                rnd.shuffle(choosable_nodes)
                choose_node = choosable_nodes.pop()
                choose_nodes.add(choose_node)
                before_state = current_state
                current_state = choose_node

                # Update choosable_nodes
                add_options = set(self.G.succ[current_state]) - set(choosable_nodes)
                for add_option in add_options:
                    if(set(self.G.pred[add_option]) <= choose_nodes):
                        choosable_nodes.append(add_option)

                # Update Q_table
                max_qv_action = np.argmax(self.q_table[current_state])
                self.q_table[before_state, choose_node] = (self.q_table[before_state, choose_node]
                                                           + self.alpha
                                                           * (self.G.nodes[choose_node]['ranku']
                                                              + self.gamma
                                                              * self.q_table[current_state, max_qv_action]
                                                              - self.q_table[before_state, choose_node]))

        # write learning_log
        self.learning_log['duration'] = time.time() - learning_start_time

    def get_sched_list(self) -> List[int]:
        # Initial setting
        current_state = self._virtual_entry_i
        sched_list = [self._virtual_entry_i]
        choosable_nodes = set(self.G.succ[current_state])

        while(len(sched_list) != self.G.number_of_nodes()):
            # Choice node
            max_qv = -1
            max_qv_action = None
            for choosable_node in choosable_nodes:
                if(self.q_table[current_state, choosable_node] > max_qv):
                    max_qv = self.q_table[current_state, choosable_node]
                    max_qv_action = choosable_node
            choosable_nodes.remove(max_qv_action)
            sched_list.append(max_qv_action)
            current_state = max_qv_action
            
            # Update choosable_nodes
            add_options = set(self.G.succ[current_state]) - set(sched_list) - choosable_nodes
            for add_option in add_options:
                if(not (set(self.G.pred[add_option]) <= set(sched_list))):
                    continue
                choosable_nodes.add(add_option)

        # Remove virtual nodes
        sched_list.remove(self._virtual_entry_i)
        sched_list.remove(self._virtual_exit_i)

        return sched_list


class QLHEFTToClusteredProcessor(QLHEFT):
    def __init__(self, dag: nx.DiGraph, alpha: float, gamma: float, inout_ratio: float):
        super().__init__(dag, alpha, gamma)
        convert_to_ave_comm_dag(self.G, inout_ratio)