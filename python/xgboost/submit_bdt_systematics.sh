#!/usr/bin/env bash
set -e

if [[ $# -ne 1 ]]; then
    echo "Usage: bash submit_bdt_systematics.sh <version>" >&2
    echo "Example: EOS_AREA=user bash submit_bdt_systematics.sh 2.4.2" >&2
    exit 1
fi

VERSION=$1
USER_NAME=${USER}
EOS_AREA=${EOS_AREA:-group}  # Set EOS_AREA=user for /store/user/lpchmumu/...

if [[ "${EOS_AREA}" != "group" && "${EOS_AREA}" != "user" ]]; then
    echo "[ERROR] EOS_AREA must be 'group' or 'user': ${EOS_AREA}" >&2
    exit 1
fi

ANALYZER_VERSION="v$(echo "${VERSION}" | cut -d. -f1,2)"
TUPLES_VERSION="v${VERSION}"

ERA="Combined"
MODEL_ERA="Combined"
BKG_SUBSET="Full"
SIG_SUBSET="NottH"

EOS_DIR="/store/${EOS_AREA}/lpchmumu/${USER_NAME}/analyzer_HiggsMuMu_${ANALYZER_VERSION}/tuples_${TUPLES_VERSION}/systematics"
XROOTD="root://cmseos.fnal.gov"

# Preserve the original expected file counts. Verify against EOS if these change.
EXPECTED_SYSTEMATICS_PER_SAMPLE=149
EXPECTED_TOTAL_JOBS=$((2 * EXPECTED_SYSTEMATICS_PER_SAMPLE))

for required in run_bdt_systematic_LPC.sh append_bdt_systematic_job.py xgb_utils.py xgb_kfold.py; do
    if [[ ! -f "${required}" ]]; then
        echo "[ERROR] Required input is missing: ${required}" >&2
        exit 1
    fi
done

mkdir -p logs

echo "========================================"
echo "USER             = ${USER_NAME}"
echo "VERSION          = ${VERSION}"
echo "MODEL ERA        = ${MODEL_ERA}"
echo "EOS AREA         = ${EOS_AREA}"
echo "EOS DIR          = ${EOS_DIR}"
echo "========================================"

echo "[INFO] Listing systematic tuples in EOS"
FILES=$(xrdfs "${XROOTD}" ls "${EOS_DIR}")

for CHANNEL in ggH VBF; do
    echo
    echo "========================================"
    echo "Preparing ${CHANNEL} BDT systematic jobs"
    echo "========================================"

    JOBLIST="jobs_${CHANNEL}.txt"
    JDL="bdt_systematics_${CHANNEL}.jdl"
    : > "${JOBLIST}"

    for TUPLE_TYPE in ggH VBF; do
        echo "[INFO] Finding ${TUPLE_TYPE} tuples"
        while IFS= read -r FILE; do
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

    echo "[INFO] ggH systematics: ${N_GGH} / ${EXPECTED_SYSTEMATICS_PER_SAMPLE}"
    echo "[INFO] VBF systematics: ${N_VBF} / ${EXPECTED_SYSTEMATICS_PER_SAMPLE}"
    echo "[INFO] Total:           ${N_JOBS} / ${EXPECTED_TOTAL_JOBS}"

    if [[ ${N_GGH} -ne ${EXPECTED_SYSTEMATICS_PER_SAMPLE} ||
          ${N_VBF} -ne ${EXPECTED_SYSTEMATICS_PER_SAMPLE} ||
          ${N_JOBS} -ne ${EXPECTED_TOTAL_JOBS} ]]; then
        echo "[ERROR] Unexpected systematic tuple counts. Check EOS_DIR, ERA, and EXPECTED_SYSTEMATICS_PER_SAMPLE." >&2
        exit 1
    fi

    # train.py's test_name (default, non-recategorized, non-Optuna K-fold models).
    TEST_NAME="${CHANNEL}_${MODEL_ERA}_B${BKG_SUBSET}_S${SIG_SUBSET}"

    # All 5 fold models, each with its OWN preprocessing metadata.
    MODEL_FILES=()
    for FOLD in 0 1 2 3 4; do
        MODEL_FILE="models/model_${TEST_NAME}_fold${FOLD}_bsC.json"
        PREPROCESSING_FILE="models/preprocessing_${TEST_NAME}_fold${FOLD}_bsC.pkl"
        for REQUIRED in "${MODEL_FILE}" "${PREPROCESSING_FILE}"; do
            if [[ ! -f "${REQUIRED}" ]]; then
                echo "[ERROR] Missing model input: ${REQUIRED}" >&2
                exit 1
            fi
            MODEL_FILES+=("${REQUIRED}")
        done
    done
    MODEL_FILES_CSV=$(IFS=,; printf '%s' "${MODEL_FILES[*]}")

    cat > "${JDL}" <<EOF_JDL
Universe = vanilla

Executable = run_bdt_systematic_LPC.sh
Arguments = ${CHANNEL} \$(era) ${MODEL_ERA} \$(tuple_type) \$(systematic) ${BKG_SUBSET} ${SIG_SUBSET} ${VERSION} ${USER_NAME} ${EOS_AREA}

Log    = logs/${CHANNEL}_\$(tuple_type)_\$(systematic).log
Output = logs/${CHANNEL}_\$(tuple_type)_\$(systematic).out
Error  = logs/${CHANNEL}_\$(tuple_type)_\$(systematic).err

should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_output_files = ""

# The models/<file> entries are transferred into the scratch directory.
# run_bdt_systematic_LPC.sh passes --models-dir . to the scoring script.
transfer_input_files = append_bdt_systematic_job.py,xgb_utils.py,xgb_kfold.py,${MODEL_FILES_CSV}

use_x509userproxy = true

request_cpus = 1
request_memory = 4000MB
request_disk = 12000MB

Queue era, tuple_type, systematic from ${JOBLIST}
EOF_JDL

    echo "[INFO] Transferring ${#MODEL_FILES[@]} model/preprocessing files per job"
    if [[ "${DRY_RUN:-0}" == "1" ]]; then
        echo "[INFO] DRY_RUN=1: generated ${JDL} without submitting"
    else
        echo "[INFO] Submitting ${JDL}"
        condor_submit "${JDL}"
    fi
done
