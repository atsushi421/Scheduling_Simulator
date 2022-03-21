import argparse
import os
import pandas as pd
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
    arg_parser.add_argument('--comparison_base',
                            required=True,
                            type=str,
                            help="base algorithm (1.0 of xaxis)")
    arg_parser.add_argument('--comparison',
                            required=True,
                            type=str,
                            help="comparison algorithm")
    arg_parser.add_argument('--format',
                            required=False,
                            type=str,
                            help="output figure format")
    arg_parser.add_argument('--dest_dir',
                            required=True,
                            type=str,
                            help="path of dest dir")
    args = arg_parser.parse_args()

    return args.source_result_dir, args.ylabel, args.xlabel, args.comparison_base, args.comparison, args.format, args.dest_dir


def main(source_result_dir, ylabel, xlabel, comparison_base, comparison, format, dest_dir):
    # Initialize variables
    files = os.listdir(source_result_dir)
    xaxis_labels = [f for f in files if os.path.isdir(os.path.join(source_result_dir, f))]
    xaxis_labels = [str(fv) for fv in sorted([float(v) for v in xaxis_labels])]
    algorithm_names = [os.path.splitext(filename)[0] for filename in os.listdir(f'{source_result_dir}/{xaxis_labels[0]}')]

    # Create source dataframe
    xaxis_dict = {}
    for xaxis_label in xaxis_labels:
        comparison_df = pd.read_csv(f'{source_result_dir}/{xaxis_label}/{comparison}.csv')
        base_df = pd.read_csv(f'{source_result_dir}/{xaxis_label}/{comparison_base}.csv')
        drop_columns = list(comparison_df.columns.values)
        drop_columns.remove(ylabel)
        comparison_df.drop(columns=drop_columns, inplace=True)
        base_df.drop(columns=drop_columns, inplace=True)
        xaxis_dict[xaxis_label] = [comp / base for (base, comp) in zip(base_df.iloc[:, 0].values.tolist(), comparison_df.iloc[:, 0].values.tolist())]
    melt_df = pd.melt(pd.DataFrame(xaxis_dict))
    melt_df['species'] = f'{comparison} / {comparioson_base}'

    # Plot
    plt.style.use('default')
    sns.set()
    sns.set_style('whitegrid')
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    sns.boxplot(x='variable', y='value', data=melt_df, hue='species', showfliers=True, palette='Greys_r', ax=ax)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[0:len(algorithm_names)], labels[0:len(algorithm_names)])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_ylim(melt_df['value'].min()-0.1, melt_df['value'].max()+0.1)

    # Save
    if(format):
        plt.savefig(f'{dest_dir}/{os.path.basename(source_result_dir)}_comparison_{comparioson_base}_box_plot.{format}')
    else:
        plt.savefig(f'{dest_dir}/{os.path.basename(source_result_dir)}_comparison_{comparioson_base}_box_plot.pdf')


if __name__ == '__main__':
    source_result_dir, ylabel, xlabel, comparioson_base, comparison, format, dest_dir = option_parser()
    main(source_result_dir, ylabel, xlabel, comparioson_base, comparison, format, dest_dir)
