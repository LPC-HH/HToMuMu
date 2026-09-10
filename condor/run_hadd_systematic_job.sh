#!/bin/bash

set -e

PROCESS=$1
SYST=$2

ANALYZER_VERSION="v2.1"
TUPLES_VERSION="v2.1.0"

EOS_REDIRECTOR="root://cmseos.fnal.gov"

EOS_BASE="/store/group/lpchmumu/${USER}/analyzer_HiggsMuMu_${ANALYZER_VERSION}/tuples_${TUPLES_VERSION}"
EOS_OUTDIR="${EOS_BASE}/systematics"

echo "============================================================"
echo "Starting job"
echo "Process    : ${PROCESS}"
echo "Systematic: ${SYST}"
echo "Host       : $(hostname)"
echo "============================================================"


# ============================================================
# Setup CMS / ROOT environment
# ============================================================

echo
echo "Setting up CMS environment..."

source /cvmfs/cms.cern.ch/cmsset_default.sh

export SCRAM_ARCH=el9_amd64_gcc12
CMSSW_VERSION="CMSSW_15_0_19"

WORKDIR="$(pwd)"

echo "SCRAM_ARCH    : ${SCRAM_ARCH}"
echo "CMSSW version : ${CMSSW_VERSION}"
echo "Work directory: ${WORKDIR}"

scram project CMSSW "${CMSSW_VERSION}"

cd "${CMSSW_VERSION}/src"
eval "$(scram runtime -sh)"
cd "${WORKDIR}"

echo
echo "Checking commands..."

if ! command -v hadd >/dev/null 2>&1; then
    echo "[ERROR] hadd is not available"
    exit 1
fi

if ! command -v xrdfs >/dev/null 2>&1; then
    echo "[ERROR] xrdfs is not available"
    exit 1
fi

if ! command -v xrdcp >/dev/null 2>&1; then
    echo "[ERROR] xrdcp is not available"
    exit 1
fi

echo "hadd  : $(command -v hadd)"
echo "xrdfs : $(command -v xrdfs)"
echo "xrdcp : $(command -v xrdcp)"


# ============================================================
# Eras
# ============================================================

ERAS=(
    "2022"
    "2022EE"
    "2023"
    "2023BPix"
    "2024"
    "2025"
)


get_dataset_era_name() {

    local era=$1

    if [[ "$era" == "2022" ]]; then
        echo "Summer22"

    elif [[ "$era" == "2022EE" ]]; then
        echo "Summer22EE"

    elif [[ "$era" == "2023" ]]; then
        echo "Summer23"

    elif [[ "$era" == "2023BPix" ]]; then
        echo "Summer23BPix"

    elif [[ "$era" == "2024" ]]; then
        echo "Summer24"

    elif [[ "$era" == "2025" ]]; then
        echo "Summer25"

    else
        echo "UNKNOWN"
    fi
}


# ============================================================
# Find input files on EOS
# ============================================================

INPUT_FILES=()

echo
echo "Searching input files..."
echo

for era in "${ERAS[@]}"; do

    dataset_era=$(get_dataset_era_name "$era")

    if [[ "$dataset_era" == "UNKNOWN" ]]; then
        echo "[WARNING] Unknown era: ${era}"
        continue
    fi

    dataset_dir="${PROCESS}_${dataset_era}_${SYST}"

    eos_dir="${EOS_BASE}/${dataset_dir}"

    echo "------------------------------------------------------------"
    echo "Era       : ${era}"
    echo "Directory : ${eos_dir}"

    # List files remotely
    mapfile -t files < <(
        xrdfs "${EOS_REDIRECTOR}" ls "${eos_dir}/" 2>/dev/null \
        | grep '\.root$' || true
    )

    if (( ${#files[@]} == 0 )); then
        echo "[WARNING] No ROOT files found."
        continue
    fi

    echo "Found ${#files[@]} ROOT files"

    for f in "${files[@]}"; do
        INPUT_FILES+=("${EOS_REDIRECTOR}/${f}")
    done

done


# ============================================================
# Check files
# ============================================================

echo
echo "============================================================"
echo "Total input files: ${#INPUT_FILES[@]}"
echo "============================================================"

if (( ${#INPUT_FILES[@]} == 0 )); then

    echo "[ERROR] No input ROOT files found."
    echo
    echo "Process    : ${PROCESS}"
    echo "Systematic: ${SYST}"

    exit 1
fi


# ============================================================
# Run hadd locally
# ============================================================

OUTPUT_FILE="${PROCESS}_Combined_${SYST}_tuples.root"

echo
echo "Creating local file:"
echo "${OUTPUT_FILE}"
echo

hadd -f "${OUTPUT_FILE}" "${INPUT_FILES[@]}"

HADD_STATUS=$?

if [[ ${HADD_STATUS} -ne 0 ]]; then
    echo "[ERROR] hadd failed with status ${HADD_STATUS}"
    exit ${HADD_STATUS}
fi


# ============================================================
# Check output
# ============================================================

if [[ ! -f "${OUTPUT_FILE}" ]]; then
    echo "[ERROR] Output file was not created:"
    echo "${OUTPUT_FILE}"
    exit 1
fi

echo
echo "Local output:"
ls -lh "${OUTPUT_FILE}"


# ============================================================
# Make EOS output directory
# ============================================================

echo
echo "Creating EOS output directory:"
echo "${EOS_OUTDIR}"

xrdfs "${EOS_REDIRECTOR}" mkdir -p "${EOS_OUTDIR}"


# ============================================================
# Copy output to EOS
# ============================================================

EOS_OUTPUT="${EOS_REDIRECTOR}/${EOS_OUTDIR}/${OUTPUT_FILE}"

echo
echo "Copying:"
echo "  ${OUTPUT_FILE}"
echo "to:"
echo "  ${EOS_OUTPUT}"
echo

xrdcp -f "${OUTPUT_FILE}" "${EOS_OUTPUT}"

XRDCP_STATUS=$?

if [[ ${XRDCP_STATUS} -ne 0 ]]; then
    echo "[ERROR] xrdcp failed with status ${XRDCP_STATUS}"
    exit ${XRDCP_STATUS}
fi


# ============================================================
# Verify
# ============================================================

echo
echo "Checking EOS output..."

xrdfs "${EOS_REDIRECTOR}" stat "${EOS_OUTDIR}/${OUTPUT_FILE}"

echo
echo "============================================================"
echo "SUCCESS"
echo
echo "Process    : ${PROCESS}"
echo "Systematic: ${SYST}"
echo
echo "Output:"
echo "${EOS_OUTDIR}/${OUTPUT_FILE}"
echo "============================================================"

rm -f "${OUTPUT_FILE}"
