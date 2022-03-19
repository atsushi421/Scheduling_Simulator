#!/bin/bash


### echo usage
function show_usage () {
    echo "Usage: $0 [-h]"
    echo "          [--dag_dir <path of dag dir>]"
    echo "          [-a <algorithm name> or --algorithm <algorithm name>]"
    echo "          [--num_of_clusters <int>]"
    echo "          [--num_of_cores <int>]"
    echo "          [--inout_ratio <int>]"
    echo "          [--write_duration]"
    echo "          [--write_makespan]"
    echo "          [-d <path of dir> or --dest_dir <path of dir>]"
    exit 0;
}


### initialize option variables
DAG_DIR="${PWD}/DAGs/80/dot"
ALGORITHM=""
NUM_OF_CLUSTERS=0
NUM_OF_CORES=0
INOUT_RATIO=0
WRITE_DURATION=""
WRITE_MAKESPAN=""
DEST_DIR="${PWD}/result/change_inout_ratio"
PYTHON_SCRIPT_DIR="${PWD}/../"


### parse command options
OPT=`getopt -o ha:d: -l help,dag_dir:,algorithm:,num_of_clusters:,num_of_cores:,inout_ratio:,write_duration,write_makespan,dest_dir: -- "$@"`

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
    --num_of_cores)
        NUM_OF_CORES=$2
        shift 2
        ;;
    --inout_ratio)
        INOUT_RATIO="$2"
        shift 2
        ;;
    --write_duration)
        WRITE_DURATION="--write_duration"
        shift
        ;;
    --write_makespan)
        WRITE_MAKESPAN="--write_makespan"
        shift
        ;;
    -d | --dest-dir)
        DEST_DIR="$2/change_inout_ratio"
        shift 2
        ;;
    --)
        shift
        break
        ;;
    esac
done


### evaluation
DEST_FILE="${DEST_DIR}/${INOUT_RATIO}/${ALGORITHM}.csv"

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

# make destination directory & write columns
if [[ ! -e "${DEST_FILE}" || ${INP} =~ [yY] ]]; then
    mkdir -p "$(dirname "${DEST_FILE}")" && touch "${DEST_FILE}"
    if [ $? -ne 0 ]; then
        echo "[Error] Cannot make the destination file: ${DEST_FILE}." 1>&2
        exit 1
    fi
fi

# write columns
COLUMNS="Filename"
if [ -n ${WRITE_DURATION} ]; then
    COLUMNS+=",Duration"
fi
if [ -n ${WRITE_MAKESPAN} ]; then
    COLUMNS+=",Makespan"
fi
echo "${COLUMNS}" >> ${DEST_FILE}

# eval command
DAG_FILES=${DAG_DIR}/*
for filepath in ${DAG_FILES}
do
    python3 ${PYTHON_SCRIPT_DIR}/eval_cluster.py --dag_file_path ${filepath} \
                                                 --algorithm ${ALGORITHM} \
                                                 --num_of_clusters ${NUM_OF_CLUSTERS} \
                                                 --num_of_cores ${NUM_OF_CORES} \
                                                 --inout_ratio "${INOUT_RATIO}" \
                                                 ${WRITE_MAKESPAN} \
                                                 ${WRITE_DURATION} \
                                                 --dest_file_path ${DEST_FILE}
done

# sort
python3 ${PYTHON_SCRIPT_DIR}/sort_result_by_dag_idx.py --result_file_path ${DEST_FILE}



if [ $? -ne 0 ]; then
    echo "$0 is Failed."
else
    echo "$0 is successfully completed." 1>&2
fi


# EOF
