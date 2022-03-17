import argparse
import random
import os
from typing import Tuple

from sched_lib.file_handling_helper import read_dag
from sched_lib.write_dag import write_dag


def option_parser() -> Tuple[str, int, int]:
    usage = f'[python] {__file__} \
              --dag_file_path [path to dag file] \
              --num_of_chosen_nodes [<int>] \
              --split_num [int]'

    arg_parser = argparse.ArgumentParser(usage=usage)
    arg_parser.add_argument('--dag_file_path',
                            required=True,
                            type=str,
                            help='path to dag file.')
    arg_parser.add_argument('--num_of_chosen_nodes',
                            required=True,
                            type=int,
                            help='Number of nodes chosen to be split.')
    arg_parser.add_argument('--split_num',
                            required=True,
                            type=int,
                            help='The choose nodes are splitted by this number.')
    args = arg_parser.parse_args()

    return args.dag_file_path, args.num_of_chosen_nodes, args.split_num


def main(dag_file_path, num_of_chosen_nodes, split_num):
    G = read_dag(dag_file_path)
    choice_options = (set(G.nodes) - {v for v, d in G.in_degree() if d == 0}
                                   - {v for v, d in G.out_degree() if d == 0})
    chosen_nodes = random.sample(list(choice_options), num_of_chosen_nodes)
    for chosen_node in chosen_nodes:
        preds = G.pred[chosen_node]
        succs = G.succ[chosen_node]
        for i in range(split_num-1):
            new_node_i = G.number_of_nodes()
            G.add_node(new_node_i, exec=G.nodes[chosen_node]['exec'])
            for pred_i in preds:
                G.add_edge(pred_i, new_node_i, comm=G.edges[pred_i, chosen_node]['comm'])
            for succ_i in succs:
                G.add_edge(new_node_i, succ_i, comm=G.edges[chosen_node, succ_i]['comm'])

    # Write
    dest_dir = os.path.dirname(dag_file_path)
    filename = os.path.splitext(os.path.basename(dag_file_path))[0]
    write_dag(G, dest_dir, filename)


if __name__ == '__main__':
    dag_file_path, num_of_chosen_nodes, split_num = option_parser()
    main(dag_file_path, num_of_chosen_nodes, split_num)
