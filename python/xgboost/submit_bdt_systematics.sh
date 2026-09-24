#!/bin/bash

set -e

if [[ $# -ne 1 ]]; then
    echo "Usage:"
    echo "  bash submit_bdt_systematics.sh <version>"
    echo
    echo "Example:"
    echo "  bash submit_bdt_systematics.sh 2.2.1"
    exit 1
fi

VERSION=$1
USER_NAME="${USER}"

ANALYZER_VERSION="v$(echo "${VERSION}" | cut -d. -f1,2)"
TUPLES_VERSION="v${VERSION}"

ERA="Combined"
MODEL_ERA="Combined"

BKG_SUBSET="Full"
SIG_SUBSET="NottH"

EOS_DIR="/store/group/lpchmumu/${USER_NAME}/analyzer_HiggsMuMu_${ANALYZER_VERSION}/tuples_${TUPLES_VERSION}/systematics"

XROOTD="root://cmseos.fnal.gov"

EXPECTED_SYSTEMATICS_PER_SAMPLE=149
EXPECTED_TOTAL_JOBS=$((2 * EXPECTED_SYSTEMATICS_PER_SAMPLE))

echo
echo "========================================"
echo "Configuration"
echo "========================================"
echo "USER             = ${USER_NAME}"
echo "VERSION          = ${VERSION}"
echo "ANALYZER VERSION = ${ANALYZER_VERSION}"
echo "TUPLES VERSION   = ${TUPLES_VERSION}"
echo "EOS DIR          = ${EOS_DIR}"
echo "========================================"
echo

echo "Looking for systematic tuples in:"
echo "${EOS_DIR}"
echo

FILES=$(xrdfs "${XROOTD}" ls "${EOS_DIR}")

mkdir -p logs


# ============================================================
# Submit one set of jobs for each BDT
# ============================================================

for CHANNEL in ggH VBF; do

    echo
    echo "========================================"
    echo "Preparing ${CHANNEL} BDT systematic jobs"
    echo "========================================"

    JOBLIST="jobs_${CHANNEL}.txt"
    JDL="bdt_systematics_${CHANNEL}.jdl"

    rm -f "${JOBLIST}"
    touch "${JOBLIST}"


    # ========================================================
    # Find systematic tuples
    # ========================================================

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

    N_GGH=$(awk '$2 == "ggH"' "${JOBLIST}" | wc -l)
    N_VBF=$(awk '$2 == "VBF"' "${JOBLIST}" | wc -l)


    # ========================================================
    # Check expected number of systematics
    # ========================================================

    echo
    echo "========================================"
    echo "Systematic tuple check"
    echo "========================================"
    echo "ggH systematics : ${N_GGH} / ${EXPECTED_SYSTEMATICS_PER_SAMPLE}"
    echo "VBF systematics : ${N_VBF} / ${EXPECTED_SYSTEMATICS_PER_SAMPLE}"
    echo "Total jobs      : ${N_JOBS} / ${EXPECTED_TOTAL_JOBS}"
    echo "========================================"

    if [[ "${N_GGH}" -ne "${EXPECTED_SYSTEMATICS_PER_SAMPLE}" ]]; then
        echo "[ERROR] Expected ${EXPECTED_SYSTEMATICS_PER_SAMPLE} ggH systematics, found ${N_GGH}"
        exit 1
    fi

    if [[ "${N_VBF}" -ne "${EXPECTED_SYSTEMATICS_PER_SAMPLE}" ]]; then
        echo "[ERROR] Expected ${EXPECTED_SYSTEMATICS_PER_SAMPLE} VBF systematics, found ${N_VBF}"
        exit 1
    fi

    if [[ "${N_JOBS}" -ne "${EXPECTED_TOTAL_JOBS}" ]]; then
        echo "[ERROR] Expected ${EXPECTED_TOTAL_JOBS} total jobs, found ${N_JOBS}"
        exit 1
    fi

    echo "[OK] All expected systematic tuples were found."


    # ========================================================
    # Model files
    # ========================================================

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


    # ========================================================
    # Create JDL
    # ========================================================

    cat > "${JDL}" <<EOF
Universe = vanilla

Executable = run_bdt_systematic_LPC.sh

Arguments = ${CHANNEL} \$(era) ${MODEL_ERA} \$(tuple_type) \$(systematic) ${BKG_SUBSET} ${SIG_SUBSET} ${VERSION} ${USER_NAME}

Log    = logs/${CHANNEL}_\$(tuple_type)_\$(systematic).log
Output = logs/${CHANNEL}_\$(tuple_type)_\$(systematic).out
Error  = logs/${CHANNEL}_\$(tuple_type)_\$(systematic).err

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
request_memory = 2000MB
request_disk = 3000MB

Queue era, tuple_type, systematic from ${JOBLIST}
EOF


    echo
    echo "Submitting:"
    echo "  ${JDL}"
    echo

    condor_submit "${JDL}"

done
