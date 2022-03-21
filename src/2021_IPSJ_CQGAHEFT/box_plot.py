import argparse
from operator import attrgetter
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from typing import Tuple


def option_parser() -> Tuple[str, str, str]:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--source_result_dir',
                            required=True,
                            type=str,
                            help='path of source result dir')
    arg_parser.add_argument('--ylabel',
                            required=True,
                            type=str,
                            help="['Duration', 'Makespan']")
    arg_parser.add_argument('--xlabel',
                            required=False,
                            type=str,
                            help="xaxis label")
    arg_parser.add_argument('--format',
                            required=False,
                            type=str,
                            help="xaxis label")
    arg_parser.add_argument('--dest_dir',
                            required=True,
                            type=str,
                            help="path of dest dir")
    args = arg_parser.parse_args()

    return args.source_result_dir, args.ylabel, args.xlabel, args.format, args.dest_dir


def main(source_result_dir, ylabel, xlabel, format, dest_dir):
    # Initialize variables
    files = os.listdir(source_result_dir)
    xaxis_labels = [f for f in files if os.path.isdir(os.path.join(source_result_dir, f))]
    xaxis_labels = [str(fv) for fv in sorted([float(v) for v in xaxis_labels])]
    algorithm_names = [os.path.splitext(filename)[0] for filename in os.listdir(f'{source_result_dir}/{xaxis_labels[0]}')]

    # Create source dataframe
    source_list = []
    for algorithm_name in algorithm_names:
        xaxis_dict = {}
        for xaxis_label in xaxis_labels:
            read_df = pd.read_csv(f'{source_result_dir}/{xaxis_label}/{algorithm_name}.csv')
            drop_columns = list(read_df.columns.values)
            drop_columns.remove(ylabel)
            read_df.drop(columns=drop_columns, inplace=True)
            xaxis_dict[xaxis_label] = read_df.iloc[:, 0].values.tolist()
        melt_df_per_alg = pd.melt(pd.DataFrame(xaxis_dict))
        melt_df_per_alg['species'] = algorithm_name
        source_list.append(melt_df_per_alg)
    source_list.sort(key=lambda melt_df: melt_df['value'].median())
    source_df = pd.concat(source_list, axis=0)

    # Plot
    plt.style.use('default')
    sns.set()
    sns.set_style('whitegrid')
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    sns.boxplot(x='variable', y='value', data=source_df, hue='species', showfliers=True, palette='Greys_r', ax=ax)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[0:len(algorithm_names)], labels[0:len(algorithm_names)])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_ylim(source_df['value'].min()-100, source_df['value'].max()+100)

    # Save
    if(format):
        plt.savefig(f'{dest_dir}/{os.path.basename(source_result_dir)}_box_plot.{format}')
    else:
        plt.savefig(f'{dest_dir}/{os.path.basename(source_result_dir)}_box_plot.pdf')


if __name__ == '__main__':
    source_result_dir, ylabel, xlabel,  format, dest_dir = option_parser()
    main(source_result_dir, ylabel, xlabel, format, dest_dir)
