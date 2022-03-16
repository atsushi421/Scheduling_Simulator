import random
import copy
import time
import networkx as nx
import pandas as pd
from typing import List

from .utils import set_ranku, convert_to_ave_comm_dag, convert_to_virtual_entry_dag, convert_to_virtual_exit_dag


class QLHEFT:
    def __init__(self, dag: nx.DiGraph, inout_ratio: float, alpha: float, gamma: float):
        self.G = copy.deepcopy(dag)
        convert_to_ave_comm_dag(self.G, inout_ratio)
        self._virtual_entry_i = convert_to_virtual_entry_dag(self.G)
        self._virtual_exit_i = convert_to_virtual_exit_dag(self.G)
        set_ranku(self.G)
        self.alpha = alpha
        self.gamma = gamma
        self.q_table = pd.DataFrame(index=range(self.G.number_of_nodes()), columns=range(self.G.number_of_nodes()))
        self.q_table.fillna(0, inplace=True)
        self.learning_log = {}

    def learn(self, max_episode: int) -> None:
        learning_start_time = time.time()
        episode = 0

        while(episode != max_episode):
            # Initial setting
            episode += 1
            current_state = self._virtual_entry_i
            choose_nodes = {self._virtual_entry_i}
            choosable_nodes = set(self.G.succ[current_state])

            # Learning
            while(len(choose_nodes) != self.G.number_of_nodes()):
                # Choice node
                choose_node = random.choice(list(choosable_nodes))
                choosable_nodes.remove(choose_node)
                choose_nodes.add(choose_node)
                before_state = current_state
                current_state = choose_node

                # Update choosable_nodes
                add_options = set(self.G.succ[current_state]) - choose_nodes - choosable_nodes
                for add_option in add_options:
                    if(not (set(self.G.pred[add_option]) <= choose_nodes)):
                        continue
                    choosable_nodes.add(add_option)

                # Update Q_table
                current_state_series = self.q_table.loc[current_state, :]
                max_qv_action = current_state_series.idxmax()
                self.q_table.at[before_state, choose_node] = (self.q_table.at[before_state, choose_node]
                                                              + self.alpha
                                                              * (self.G.nodes[choose_node]['ranku']
                                                                 + self.gamma
                                                                 * self.q_table.at[current_state, max_qv_action]
                                                                 - self.q_table.at[before_state, choose_node]))

        # write learning_log
        self.learning_log['duration'] = time.time() - learning_start_time
        self.learning_log['episode'] = episode

    def get_sched_list(self) -> List[int]:
        pass  # TODO
