import argparse
import networkx as nx
from typing import Tuple

from file_handling_helper import read_dag
from debug_write_dag import write_dag


def option_parser() -> Tuple[argparse.FileType]:
    usage = f'[python] {__file__} \
              --dag_file_path [<path to dag file>]'

    arg_parser = argparse.ArgumentParser(usage=usage)
    arg_parser.add_argument('--dag_file_path',
                            type=str,
                            help='path to dag file (.tgff, .yaml, .json, or , .dot)')
    args = arg_parser.parse_args()

    return args.dag_file_path


# def set_ave_comm(G: nx.DiGraph, target)


def main(dag_file_path):
    G = read_dag(dag_file_path)
    write_dag(G)


if __name__ == '__main__':
    dag_file_path = option_parser()
    main(dag_file_path)
