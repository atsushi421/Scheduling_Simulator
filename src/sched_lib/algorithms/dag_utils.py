import networkx as nx
import numpy as np


def set_ranku(G: nx.DiGraph) -> None:
    def _ranku(node_i):
        if(node_i in exit_nodes):
            G.nodes[node_i]['ranku'] = G.nodes[node_i]['exec']
        else:
            for uncalc_succ_i in [sn for sn in G.succ[node_i] if 'ranku' not in G.nodes[sn].keys()]:
                _ranku(uncalc_succ_i)

            max_value = 0
            for succ_i in G.succ[node_i]:
                tmp = G.edges[node_i, succ_i]['comm'] + G.nodes[succ_i]['ranku']
                if(tmp > max_value):
                    max_value = tmp
            G.nodes[node_i]['ranku'] = G.nodes[node_i]['exec'] + max_value

    entry_nodes = [v for v, d in G.in_degree() if d == 0]
    exit_nodes = [v for v, d in G.out_degree() if d == 0]
    for entry_node in entry_nodes:
        _ranku(entry_node)


def convert_to_ave_comm_dag(G: nx.DiGraph, inout_ratio: float) -> None:
    for s, t in G.edges:
        G.edges[s, t]['comm'] = int((G.edges[s, t]['comm'] + G.edges[s, t]['comm']*inout_ratio) / 2)


def convert_to_virtual_entry_dag(G: nx.DiGraph) -> int:
    entry_nodes = [v for v, d in G.in_degree() if d == 0]
    virtual_entry_i = G.number_of_nodes()
    G.add_node(virtual_entry_i, exec=0, virtual=True)
    for entry_i in entry_nodes:
        G.add_edge(virtual_entry_i, entry_i, comm=0)

    return virtual_entry_i


def convert_to_virtual_exit_dag(G: nx.DiGraph) -> int:
    exit_nodes = [v for v, d in G.out_degree() if d == 0]
    virtual_exit_i = G.number_of_nodes()
    G.add_node(virtual_exit_i, exec=0, virtual=True)
    for exit_i in exit_nodes:
        G.add_edge(exit_i, virtual_exit_i, comm=0)

    return virtual_exit_i


def get_ccr(dag: nx.DiGraph) -> float:
    sum_comm = 0
    for s, t in dag.edges:
        sum_comm += dag.edges[s, t]['comm']
    ave_comm = sum_comm / dag.number_of_edges()
    
    sum_exec = 0
    for node_i in dag.nodes:
        sum_exec += dag.nodes[node_i]['exec']
    ave_exec = sum_exec / dag.number_of_nodes()
    
    return ave_comm / ave_exec


def convert_to_specified_ccr_dag(G: nx.DiGraph, CCR: float) -> None:
    while(abs(CCR - (cur_ccr := round(get_ccr(G), 3))) > 0.01):
        if(cur_ccr > CCR):
            for s, t in G.edges:
                G.edges[s, t]['comm'] = int(np.ceil(G.edges[s, t]['comm'] * 0.99))
            for node_i in G.nodes:
                G.nodes[node_i]['exec'] = int(np.ceil(G.nodes[node_i]['exec'] * 1.01))
        else:
            for s, t in G.edges:
                G.edges[s, t]['comm'] = int(np.ceil(G.edges[s, t]['comm'] * 1.01))
            for node_i in G.nodes:
                G.nodes[node_i]['exec'] = int(np.ceil(G.nodes[node_i]['exec'] * 0.99))
