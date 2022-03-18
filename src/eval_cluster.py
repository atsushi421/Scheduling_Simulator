import argparse
import os
import networkx as nx
from typing import Tuple

from sched_lib.file_handling_helper import read_dag
from sched_lib.processors.homogeneous.cluster import CluesteredProcessor
from sched_lib.algorithms.static.HEFT import HEFT_cluster
from sched_lib.algorithms.static.QLHEFT import QLHEFTToClusteredProcessor
from sched_lib.algorithms.static.CQGAHEFT import CQGAHEFT
from sched_lib.scheduler.list_scheduler import ListSchedulerToClusteredProcessor


def option_parser() -> Tuple[str, str, int, int, float, bool]:
    usage = f'[python] {__file__} \
              --dag_file_path [<path to dag file>] \
              --algorithm [<algorithm name>] \
              --num_of_clusters [<int>] \
              --num_of_cores [<int>] \
              --inout_ratio [<float>] \
              --dest_file path [path to result file]'

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
    arg_parser.add_argument('--dest_file_path',
                            required=True,
                            type=str,
                            help='path to result file.')
    args = arg_parser.parse_args()

    return args.dag_file_path, args.algorithm, args.num_of_clusters, args.num_of_cores, args.inout_ratio, args.dest_file_path


def main(dag_file_path, alg, num_clusters, num_cores, inout_ratio, dest_file_path):
    G = read_dag(dag_file_path)
    P = CluesteredProcessor(num_clusters, num_cores, inout_ratio)

    if(alg == 'HEFT'):
        sched_list = HEFT_cluster(G, P.inout_ratio)
        S = ListSchedulerToClusteredProcessor(G, P, sched_list)
    elif(alg == 'QL-HEFT'):
        qlheft = QLHEFTToClusteredProcessor(G, 1.0, 0.2, P.inout_ratio)  # HACK
        qlheft.learn(30000)  # HACK
        print(qlheft.learning_log['duration'])
        sched_list = qlheft.get_sched_list()
        S = ListSchedulerToClusteredProcessor(G, P, sched_list)
    elif(alg == 'CQGA-HEFT'):
        cqgaheft = CQGAHEFT(G, 8, 8, 0.001, 1.0, 0.2, P)  # HACK
        cqgaheft.evolution()
        sched_list = cqgaheft.get_sched_list()
        S = ListSchedulerToClusteredProcessor(G, P, sched_list)

    # Write result  # HACK
    S.schedule()
    f = open(dest_file_path, "a")
    f.write(os.path.basename(dag_file_path) + "\t" + str(S.get_makespan()) + "\n")
    f.close()


if __name__ == '__main__':
    dag_file_path, alg, num_clusters, num_cores, inout_ratio, dest_file_path = option_parser()
    main(dag_file_path, alg, num_clusters, num_cores, inout_ratio, dest_file_path)
