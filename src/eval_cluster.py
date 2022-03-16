import argparse
import networkx as nx
from typing import Tuple

from file_handling_helper import read_dag
from processors.homogeneous.cluster import CluesteredProcessor
from algorithms.static.HEFT import HEFT_cluster
from algorithms.static.QLHEFT import QLHEFT
from scheduler.list_scheduler import ListSchedulerToClusteredProcessor
from debug_write_dag import write_dag


def option_parser() -> Tuple[str, str, int, int, float, bool]:
    usage = f'[python] {__file__} \
              --dag_file_path [<path to dag file>] \
              --algorithm [<algorithm name>] \
              --num_of_clusters [<int>] \
              --num_of_cores [<int>] \
              --inout_ratio [<float>]'

    arg_parser = argparse.ArgumentParser(usage=usage)
    arg_parser.add_argument('--dag_file_path',
                            required=True,
                            type=str,
                            help='path to dag file (.tgff, .yaml, .json, or , .dot)')
    arg_parser.add_argument('--algorithm',
                            required=True,
                            type=str,
                            choices=['HEFT', 'QL-HEFT', 'CQGA-HEFT'],
                            help='Algorithm name used for evaluation.')
    arg_parser.add_argument('--num_of_clusters',
                            required=True,
                            type=int,
                            help='Number of clusters in a clustered many-core processor.')
    arg_parser.add_argument('--num_of_cores',
                            required=True,
                            type=int,
                            help='Number of cores in a single cluster.')
    arg_parser.add_argument('--inout_ratio',
                            required=True,
                            type=float,
                            help='Ratio of communication time outside the cluster to \
                                  communication time inside the cluster for clustered many-core processor.')
    args = arg_parser.parse_args()

    return args.dag_file_path, args.algorithm, args.num_of_clusters, args.num_of_cores, args.inout_ratio


def main(dag_file_path, alg, num_clusters, num_cores, inout_ratio):
    G = read_dag(dag_file_path)
    P = CluesteredProcessor(num_clusters, num_cores, inout_ratio)

    if(alg == 'HEFT'):
        sched_list = HEFT_cluster(G, P.inout_ratio)
        S = ListSchedulerToClusteredProcessor(G, P, sched_list)
    elif(alg == 'QL-HEFT'):
        qlheft = QLHEFT(G, P.inout_ratio, 1.0, 0.2)
        qlheft.learn(1000)
        print(qlheft.q_table)
    elif(alg == 'CQGA-HEFT'):
        pass  # TODO

    S.schedule()
    print(S.get_makespan())


if __name__ == '__main__':
    dag_file_path, alg, num_clusters, num_cores, inout_ratio = option_parser()
    main(dag_file_path, alg, num_clusters, num_cores, inout_ratio)
