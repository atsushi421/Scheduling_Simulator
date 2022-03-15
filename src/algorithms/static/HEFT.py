import copy
import networkx as nx
from typing import List

from .utils import set_ranku, get_ave_comm_dag


def HEFT_cluster(dag: nx.DiGraph, inout_ratio: float) -> List[int]:
    G = get_ave_comm_dag(dag, inout_ratio)
    set_ranku(G)
    ranku_dict = nx.get_node_attributes(G, 'ranku')
    sorted_by_ranku = sorted(ranku_dict.items(),
                             key=lambda i: i[1],
                             reverse=True)

    return [k for k, v in sorted_by_ranku]
