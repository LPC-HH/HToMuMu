#!/bin/bash

set -e

echo "========================================"
echo "Host: $(hostname)"
echo "PWD:  $(pwd)"
echo "Date: $(date)"
echo "========================================"

CHANNEL=$1
ERA=$2
MODEL_ERA=$3
TUPLE_TYPE=$4
SYSTEMATIC=$5
BKG_SUBSET=$6
SIG_SUBSET=$7

echo "CHANNEL     = ${CHANNEL}"
echo "ERA         = ${ERA}"
echo "MODEL ERA   = ${MODEL_ERA}"
echo "TUPLE TYPE  = ${TUPLE_TYPE}"
echo "SYSTEMATIC  = ${SYSTEMATIC}"
echo "BKG SUBSET  = ${BKG_SUBSET}"
echo "SIG SUBSET  = ${SIG_SUBSET}"

echo
echo "========================================"
echo "Setting up CMSSW"
echo "========================================"

# Save Condor working directory before changing directories
WORKDIR=$(pwd)

source /cvmfs/cms.cern.ch/cmsset_default.sh

export SCRAM_ARCH=el9_amd64_gcc12

scramv1 project CMSSW CMSSW_15_0_19
cd CMSSW_15_0_19/src
eval "$(scramv1 runtime -sh)"

cd "${WORKDIR}"

# Condor container may not define USER
export USER="${USER:-mbarrial}"

echo "USER = ${USER}"

echo
echo "========================================"
echo "Python environment"
echo "========================================"

which python3
python3 --version

python3 -c "import numpy; print('numpy:', numpy.__version__)"
python3 -c "import uproot; print('uproot:', uproot.__version__)"
python3 -c "import xgboost; print('xgboost:', xgboost.__version__)"

echo
echo "========================================"
echo "Running BDT job"
echo "========================================"

python3 append_bdt_systematic_job.py \
    "${CHANNEL}" \
    "${ERA}" \
    "${MODEL_ERA}" \
    "${TUPLE_TYPE}" \
    "${SYSTEMATIC}" \
    "${BKG_SUBSET}" \
    "${SIG_SUBSET}"

STATUS=$?

echo
echo "========================================"
echo "Python exit status: ${STATUS}"
echo "========================================"

exit ${STATUS}
