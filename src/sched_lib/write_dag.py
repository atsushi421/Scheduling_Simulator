from platform import node
import networkx as nx
from networkx.readwrite import json_graph


def write_dag(G: nx.DiGraph) -> None:
    # node label
    for node_i in range(G.number_of_nodes()):
        G.nodes[node_i]['label'] = f'[{node_i}]\n' \
                                   f'C: {G.nodes[node_i]["exec"]}'
        if('ranku' in G.nodes[node_i].keys()):
            G.nodes[node_i]['label'] += f'\nranku: {G.nodes[node_i]["ranku"]}'
        if('virtual' in G.nodes[node_i].keys()):
            G.nodes[node_i]['style'] = 'dotted'
    
    # edge labal
    for start_i, end_i in G.edges():
        G.edges[start_i, end_i]['label'] = \
                f'{G.edges[start_i, end_i]["comm"]}'

    pdot = nx.drawing.nx_pydot.to_pydot(G)
    pdot.write_png('test.png')
