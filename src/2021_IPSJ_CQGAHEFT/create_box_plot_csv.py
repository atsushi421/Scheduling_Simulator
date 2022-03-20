import argparse
import os
import pandas as pd

from typing import Tuple


def option_parser() -> Tuple[str, str, str]:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--source_result_dir',
                            required=True,
                            type=str,
                            help='path of source result dir')
    arg_parser.add_argument('--yaxis',
                            required=True,
                            type=str,
                            help="['Duration', 'Makespan']")
    arg_parser.add_argument('--dest_dir',
                            required=True,
                            type=str,
                            help="path of dest dir")
    args = arg_parser.parse_args()

    return args.source_result_dir, args.yaxis, args.dest_dir


def main(source_result_dir, yaxis, dest_dir):
    # Initialize variables
    files = os.listdir(source_result_dir)
    xaxis_labels = [f for f in files if os.path.isdir(os.path.join(source_result_dir, f))]
    xaxis_labels = [str(fv) for fv in sorted([float(v) for v in xaxis_labels])]
    algorithm_names = [os.path.splitext(filename)[0] for filename in os.listdir(f'{source_result_dir}/{xaxis_labels[0]}')]

    # Create dataframe
    df_per_xaxis_list = []
    for xaxis_label in xaxis_labels:
        df_per_alg_list = []
        for algorithm_name in algorithm_names:
            df_per_alg = pd.read_csv(f'{source_result_dir}/{xaxis_label}/{algorithm_name}.csv')
            drop_columns = list(df_per_alg.columns.values)
            drop_columns.remove(yaxis)
            df_per_alg.drop(columns=drop_columns, inplace=True)
            df_per_alg.columns = [algorithm_name]
            df_per_alg.index = [f'{xaxis_label}' for _ in range(len(df_per_alg.index))]
            df_per_alg_list.append(df_per_alg)
        df_per_xaxis_list.append(pd.concat(df_per_alg_list, axis=1))
    output_df = pd.concat(df_per_xaxis_list, axis=0)

    # Output csv
    output_df.to_csv(f'{dest_dir}/{os.path.basename(source_result_dir)}_box_plot.csv')

if __name__ == '__main__':
    source_result_dir, yaxis, dest_dir = option_parser()
    main(source_result_dir, yaxis, dest_dir)
