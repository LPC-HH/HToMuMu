#!/bin/bash

set -e

if [[ $# -ne 1 ]]; then
    echo "Usage:"
    echo "  bash submit_bdt_systematics.sh <ggH|VBF>"
    exit 1
fi


CHANNEL=$1

if [[ "${CHANNEL}" != "ggH" && "${CHANNEL}" != "VBF" ]]; then
    echo "Channel must be ggH or VBF"
    exit 1
fi


ERA="Combined"
MODEL_ERA="Combined"

BKG_SUBSET="Full"
SIG_SUBSET="NottH"

ANALYZER_VERSION="v2.0"
TUPLES_VERSION="v2.0.0"


EOS_DIR="/store/group/lpchmumu/${USER}/analyzer_HiggsMuMu_${ANALYZER_VERSION}/tuples_${TUPLES_VERSION}/systematics"

XROOTD="root://cmseos.fnal.gov"


JOBLIST="jobs_${CHANNEL}.txt"
JDL="bdt_systematics_${CHANNEL}.jdl"


rm -f "${JOBLIST}"

touch "${JOBLIST}"

mkdir -p logs


echo "Looking for systematic tuples in:"
echo "${EOS_DIR}"
echo


FILES=$(xrdfs "${XROOTD}" ls "${EOS_DIR}")


for TUPLE_TYPE in ggH VBF; do

    echo "Finding ${TUPLE_TYPE} tuples..."

    while read -r FILE; do

        BASE=$(basename "${FILE}")

        PREFIX="${TUPLE_TYPE}_${ERA}_"
        SUFFIX="_tuples.root"

        if [[ "${BASE}" != ${PREFIX}*${SUFFIX} ]]; then
            continue
        fi

        SYSTEMATIC="${BASE#${PREFIX}}"
        SYSTEMATIC="${SYSTEMATIC%${SUFFIX}}"

        echo "${ERA} ${TUPLE_TYPE} ${SYSTEMATIC}" >> "${JOBLIST}"

    done <<< "${FILES}"

done


sort -u "${JOBLIST}" -o "${JOBLIST}"

N_JOBS=$(wc -l < "${JOBLIST}")


echo
echo "========================================"
echo "Found ${N_JOBS} jobs"
echo "========================================"

cat "${JOBLIST}"

echo


MODEL_FILE="models/model_${CHANNEL}_${MODEL_ERA}_B${BKG_SUBSET}_S${SIG_SUBSET}_bsC.pkl"

PREPROCESSING_FILE="models/preprocessing_${CHANNEL}_${MODEL_ERA}_B${BKG_SUBSET}_S${SIG_SUBSET}_bsC.pkl"


if [[ ! -f "${MODEL_FILE}" ]]; then
    echo "ERROR: Model not found:"
    echo "${MODEL_FILE}"
    exit 1
fi


if [[ ! -f "${PREPROCESSING_FILE}" ]]; then
    echo "ERROR: Preprocessing file not found:"
    echo "${PREPROCESSING_FILE}"
    exit 1
fi


cat > "${JDL}" <<EOF
Universe = vanilla

Executable = run_bdt_systematic_LPC.sh

Arguments = ${CHANNEL} \$(era) ${MODEL_ERA} \$(tuple_type) \$(systematic) ${BKG_SUBSET} ${SIG_SUBSET}

Log    = logs/\$(tuple_type)_\$(systematic).log
Output = logs/\$(tuple_type)_\$(systematic).out
Error  = logs/\$(tuple_type)_\$(systematic).err

should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_output_files = ""

transfer_input_files = \
    append_bdt_systematic_job.py, \
    xgb_utils.py, \
    ${MODEL_FILE}, \
    ${PREPROCESSING_FILE}

use_x509userproxy = true

request_cpus = 1
request_memory = 4000MB
request_disk = 8000MB

Queue era, tuple_type, systematic from ${JOBLIST}
EOF


echo "Submitting:"
echo "  ${JDL}"
echo

condor_submit "${JDL}"
