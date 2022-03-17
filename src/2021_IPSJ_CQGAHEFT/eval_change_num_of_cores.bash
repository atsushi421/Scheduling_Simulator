#!/bin/bash


### echo usage
function show_usage () {
    echo "Usage: $0 [-h]"
    echo "          [--dag_dir <path of dag dir>]"
    echo "          [-a <algorithm name> or --algorithm <algorithm name>]"
    echo "          [--num_of_clusters <int>]"
    echo "          [-s <int> or --start_num_of_cores <int>]"
    echo "          [-e <int> or --end_num_of_cores <int>]"
    echo "          [-r <float> or --inout_ratio <float>]"
    echo "          [-d <path of dir> or --dest_dir <path of dir>]"
    exit 0;
}


### initialize option variables
DAG_DIR="${PWD}/../../DAGs/tgff/100"
ALGORITHM=""
NUM_OF_CLUSTERS=0
START=0
END=0
INOUT_RATIO=0
DEST_DIR="${PWD}/result/change_num_of_cores"
PYTHON_SCRIPT_DIR="${PWD}/../"


### parse command options
OPT=`getopt -o ha:s:e:r:d: -l help,dag_dir:,algorithm:,num_of_clusters:,start_num_of_cores:,end_num_of_cores:,inout_ratio:,dest_dir: -- "$@"`

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
    -a | --algorithm)
        ALGORITHM="$2"
        shift 2
        ;;
    --num_of_clusters)
        NUM_OF_CLUSTERS=$2
        shift 2
        ;;
    -s | --start_num_of_cores)
        START=$2
        shift 2
        ;;
    -e | --end_num_of_cores)
        END=$2
        shift 2
        ;;
    -r | --inout_ratio)
        INOUT_RATIO=$2
        shift 2
        ;;
    -d | --dest-dir)
        DEST_DIR="$2/change_num_of_cores"
        shift 2
        ;;
    --)
        shift
        break
        ;;
    esac
done


### evaluation
for num_of_cores in `seq ${START} ${END}`
do
    DEST_FILE="${DEST_DIR}/${num_of_cores}/${ALGORITHM}.csv"

    # check dest file exist
    if [ -e "${DEST_FILE}" ]; then
        echo "The following file is already existing. Do you overwrite?"
        echo "FILE: ${DEST_FILE}"
        while :
        do
            read -p "[Y]es / [N]o? >> " INP
            if [[ ${INP} =~ [yYnN] ]]; then
                break
            fi
            echo "[Error] Input again [Y]es or [N]o."
        done
        if [[ ${INP} =~ [yY] ]]; then
            rm ${DEST_FILE}
            if [ $? -ne 0 ]; then
                echo "[Error] Cannot overwrite the destination file: ${DEST_FILE}." 1>&2
                exit 1
            fi
        elif [[ ${INP} =~ [nN] ]]; then
            exit 1
        fi
    fi

    # make destination directory
    if [[ ! -e "${DEST_FILE}" || ${INP} =~ [yY] ]]; then
        mkdir -p "$(dirname "${DEST_FILE}")" && touch "${DEST_FILE}"
        if [ $? -ne 0 ]; then
            echo "[Error] Cannot make the destination file: ${DEST_FILE}." 1>&2
            exit 1
        fi
    fi

    # eval command
    DAG_FILES=${DAG_DIR}/*
    for filepath in ${DAG_FILES}
    do
        python3 ${PYTHON_SCRIPT_DIR}/eval_cluster.py --dag_file_path ${filepath} \
                                                     --algorithm ${ALGORITHM} \
                                                     --num_of_clusters ${NUM_OF_CLUSTERS} \
                                                     --num_of_cores ${num_of_cores} \
                                                     --inout_ratio ${INOUT_RATIO} \
                                                     --dest_file_path ${DEST_FILE}
    done

    # sort
    python3 ${PYTHON_SCRIPT_DIR}/sort_result_by_dag_idx.py --result_file_path ${DEST_FILE}
done



if [ $? -ne 0 ]; then
    echo "$0 is Failed."
else
    echo "$0 is successfully completed." 1>&2
fi


# EOF
