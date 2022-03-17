#!/bin/bash


### echo usage
function show_usage () {
    echo "Usage: $0 [-h]"
    echo "          [--dag_dir <path of dag dir>]"
    echo "          [--num_of_chosen_nodes <int>]"
    echo "          [--split_num <int>]"
    exit 0;
}


### initialize option variables
DAG_DIR="${PWD}/../DAGs/tgff/50"
NUM_OF_CHOSEN_NODES=0
SPLIT_NUM=0
PYTHON_SCRIPT_DIR="${PWD}"


### parse command options
OPT=`getopt -o h -l help,dag_dir:,num_of_chosen_nodes:,split_num: -- "$@"`

if [ $? != 0 ] ; then
    echo "[Error] Option parsing processing is failed." 1>&2
    show_usage
    exit 1
fi

eval set -- "$OPT"

while true
do
    case $1 in
    -h | --help)
        show_usage;
        shift
        ;;
    --dag_dir)
        DAG_DIR="$2"
        shift 2
        ;;
    --num_of_chosen_nodes)
        NUM_OF_CHOSEN_NODES=$2
        shift 2
        ;;
    --split_num)
        SPLIT_NUM=$2
        shift 2
        ;;
    --)
        shift
        break
        ;;
    esac
done


# do command
DAG_FILES=${DAG_DIR}/*
for filepath in ${DAG_FILES}
do
    python3 ${PYTHON_SCRIPT_DIR}/split_node.py --dag_file_path ${filepath} \
                                               --num_of_chosen_nodes ${NUM_OF_CHOSEN_NODES} \
                                               --split_num ${SPLIT_NUM}
done


if [ $? -ne 0 ]; then
    echo "$0 is Failed."
else
    echo "$0 is successfully completed." 1>&2
fi


# EOF
