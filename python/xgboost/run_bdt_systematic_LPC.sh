#!/usr/bin/env bash
set -e

if [[ $# -ne 12 ]]; then
    echo "Usage: $0 <channel> <era> <model_era> <tuple_type> <systematic> <bkg_subset> <sig_subset> <version> <user> <input_dir> <output_dir> <model_name>" >&2
    exit 2
fi

CHANNEL=$1
ERA=$2
MODEL_ERA=$3
TUPLE_TYPE=$4
SYSTEMATIC=$5
BKG_SUBSET=$6
SIG_SUBSET=$7
VERSION=$8
USER_NAME=$9
INPUT_DIR=${10}
OUTPUT_DIR=${11}
MODEL_NAME=${12}

echo "========================================"
echo "Host: $(hostname)"
echo "PWD:  $(pwd)"
echo "Date: $(date)"
echo "========================================"
echo "CHANNEL     = ${CHANNEL}"
echo "ERA         = ${ERA}"
echo "MODEL ERA   = ${MODEL_ERA}"
echo "TUPLE TYPE  = ${TUPLE_TYPE}"
echo "SYSTEMATIC  = ${SYSTEMATIC}"
echo "BKG SUBSET  = ${BKG_SUBSET}"
echo "SIG SUBSET  = ${SIG_SUBSET}"
echo "VERSION     = ${VERSION}"
echo "USER        = ${USER_NAME}"
echo "INPUT DIR   = ${INPUT_DIR}"
echo "OUTPUT DIR  = ${OUTPUT_DIR}"
echo "MODEL NAME  = ${MODEL_NAME}"

# Keep the Condor scratch directory for the transferred model files.
WORKDIR=$(pwd)

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc12
scramv1 project CMSSW CMSSW_15_0_19
cd CMSSW_15_0_19/src
eval "$(scramv1 runtime -sh)"
cd "${WORKDIR}"

echo "========================================"
echo "Python environment"
echo "========================================"
which python3
python3 --version
python3 -c 'import ROOT, numpy, uproot, xgboost, pandas, matplotlib, mplhep; print("[INFO] Python dependencies imported successfully")'

echo "========================================"
echo "Running K-fold BDT systematic job"
echo "========================================"

# Condor flattens models/<file> transfers into the scratch directory.
# The Python job therefore reads its models from '.'.
python3 append_bdt_systematic_job.py \
    "${CHANNEL}" \
    "${ERA}" \
    "${MODEL_ERA}" \
    "${TUPLE_TYPE}" \
    "${SYSTEMATIC}" \
    "${BKG_SUBSET}" \
    "${SIG_SUBSET}" \
    "${VERSION}" \
    "${USER_NAME}" \
    --models-dir . \
    --input-dir "${INPUT_DIR}" \
    --output-dir "${OUTPUT_DIR}" \
    --model-name "${MODEL_NAME}" \
    --skim-chunks 1 \
    --score-chunk-rows 500000

echo "========================================"
echo "[INFO] Job finished successfully"
echo "========================================"
