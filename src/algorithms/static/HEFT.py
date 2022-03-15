import copy
import networkx as nx
from typing import List

from utils import set_ranku


def HEFT(dag: nx.DiGraph) -> List[int]:
    G = copy.deepcopy(dag)
    set_ranku(G)
    
