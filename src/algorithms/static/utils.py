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
