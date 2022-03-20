import networkx as nx


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
