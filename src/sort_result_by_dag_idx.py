import argparse
import os
from typing import Tuple


def option_parser() -> str:
    usage = f'[python] {__file__} \
              --result_file_path [path to result file]'

    arg_parser = argparse.ArgumentParser(usage=usage)
    arg_parser.add_argument('--result_file_path',
                            required=True,
                            type=str,
                            help='path to result file.')
    args = arg_parser.parse_args()

    return args.result_file_path


def main(result_file_path):
    # Read
    f = open(result_file_path, 'r')
    dag_info_header = None
    dag_ext = None
    line_dict = {}
    for line in f:
        line_list = line.split()
        dag_info = line_list[0].split('_')
        dag_idx, dag_ext = os.path.splitext(dag_info.pop(-1))
        dag_info_header = dag_info
        line_dict[str(dag_idx)] = line_list[1:]
    f.close()

    # Sort
    sorted_by_dag_idx = sorted(line_dict.items(),
                               key=lambda i: int(i[0]))

    # Write
    f = open(result_file_path, 'w')
    dag_info_header = '_'.join(dag_info_header)
    for dag_i, results in sorted_by_dag_idx:
        result_str = '\t'.join(results)
        f.write(f'{dag_info_header}_{dag_i}{dag_ext}\t{result_str}\n')
    f.close()


if __name__ == '__main__':
    result_file_path = option_parser()
    main(result_file_path)
