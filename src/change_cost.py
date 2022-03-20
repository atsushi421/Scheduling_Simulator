import argparse
import random
import os
from typing import Tuple

from sched_lib.file_handling_helper import read_dag
from sched_lib.write_dag import write_dag


def option_parser() -> Tuple[str, int, int]:
    usage = f'[python] {__file__} \
              --dag_file_path [path to dag file] \
              --exec_factor [<int>] \
              --comm_factor [int]'

    arg_parser = argparse.ArgumentParser(usage=usage)
    arg_parser.add_argument('--dag_file_path',
                            required=True,
                            type=str,
                            help='path to dag file.')
    arg_parser.add_argument('--exec_factor',
                            required=True,
                            type=float,
                            help='Factor multiplied by the execution time of all nodes.')
    arg_parser.add_argument('--comm_factor',
                            required=True,
                            type=float,
                            help='Factor multiplied by the communication time of all edges.')
    args = arg_parser.parse_args()

    return args.dag_file_path, args.exec_factor, args.comm_factor


def main(dag_file_path, exec_factor, comm_factor):
    G = read_dag(dag_file_path)
    for node_i in range(G.number_of_nodes()):
        G.nodes[node_i]['exec'] = int(G.nodes[node_i]['exec'] * exec_factor)
    for s, t in G.edges:
        G.edges[s, t]['comm'] = int(G.edges[s, t]['comm'] * comm_factor)

    # Write
    dest_dir = os.path.dirname(dag_file_path)
    filename = os.path.splitext(os.path.basename(dag_file_path))[0]
    write_dag(G, dest_dir, filename)


if __name__ == '__main__':
    dag_file_path, exec_factor, comm_factor = option_parser()
    main(dag_file_path, exec_factor, comm_factor)
