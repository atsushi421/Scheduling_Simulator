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
    arg_parser.add_argument('--normalized_by_median',
                            required=False,
                            type=str,
                            help="Normalize all algorithm values by the median of the specified algorithm")
    arg_parser.add_argument('--format',
                            required=False,
                            type=str,
                            help="xaxis label")
    arg_parser.add_argument('--dest_dir',
                            required=True,
                            type=str,
                            help="path of dest dir")
    args = arg_parser.parse_args()

    return args.source_result_dir, args.ylabel, args.xlabel, args.normalized_by_median, args.format, args.dest_dir


def main(source_result_dir, ylabel, xlabel, normalized_by_median, format, dest_dir):
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
            if(normalized_by_median):
                base_df = pd.read_csv(f'{source_result_dir}/{xaxis_label}/{normalized_by_median}.csv')
                base_value = base_df[ylabel].median()

            read_df = pd.read_csv(f'{source_result_dir}/{xaxis_label}/{algorithm_name}.csv')
            drop_columns = list(read_df.columns.values)
            drop_columns.remove(ylabel)
            read_df.drop(columns=drop_columns, inplace=True)
            if(normalized_by_median):
                xaxis_dict[xaxis_label] = [v / base_value for v in read_df.iloc[:, 0].values.tolist()]
            else:
                xaxis_dict[xaxis_label] = read_df.iloc[:, 0].values.tolist()
        melt_df_per_alg = pd.melt(pd.DataFrame(xaxis_dict))
        melt_df_per_alg['species'] = algorithm_name
        source_list.append(melt_df_per_alg)
    source_list.sort(key=lambda melt_df: melt_df['value'].max())
    source_df = pd.concat(source_list, axis=0)

    # Plot
    plt.style.use('default')
    sns.set()
    sns.set_style('whitegrid')
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.subplots_adjust(hspace=0.5)
    sns.boxplot(x='variable', y='value', data=source_df, hue='species', showfliers=True, palette='Greys_r', ax=ax)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[0:len(algorithm_names)], labels[0:len(algorithm_names)])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel + ' [ms]')
    if(normalized_by_median):
        ax.set_ylim(source_df['value'].min()-0.45, source_df['value'].max()+0.05)
    else:
        ax.set_ylim(source_df['value'].min()-100, source_df['value'].max()+100)

    # Save
    if(normalized_by_median):
        if(format):
            plt.savefig(f'{dest_dir}/{os.path.basename(source_result_dir)}_box_plot_normalized_by_{normalized_by_median}.{format}')
        else:
            plt.savefig(f'{dest_dir}/{os.path.basename(source_result_dir)}_box_plot_normalized_by_{normalized_by_median}.pdf')
    else:
        if(format):
            plt.savefig(f'{dest_dir}/{os.path.basename(source_result_dir)}_box_plot.{format}')
        else:
            plt.savefig(f'{dest_dir}/{os.path.basename(source_result_dir)}_box_plot.pdf')


if __name__ == '__main__':
    source_result_dir, ylabel, xlabel, normalized_by_median, format, dest_dir = option_parser()
    main(source_result_dir, ylabel, xlabel, normalized_by_median, format, dest_dir)
