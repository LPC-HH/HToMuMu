#!/bin/bash

# Copy the hadded BDT-score tuples (output of scripts/hadd_bdt.sh) for one
# channel/variant to EOS.
#
# Source:      BDT_score/<channel><variant>/BFull_SNottH/{signal,background,data}_Combined.root
# Destination: /store/group/lpchmumu/$USER/analyzer_HiggsMuMu_<ANALYZER_VERSION>/tuples_<TUPLES_VERSION>/BDT_score/<channel><variant>/BFull_SNottH/

if [ "$#" -lt 1 ] || [ "$#" -gt 3 ]; then
    echo "Usage: $0 <ggH|VBF> [variant] [tuples_version]"
    echo "Example: $0 ggH"
    echo "Example: $0 VBF asimovFitflatMassRes"
    echo "Example: $0 VBF asimovFitflatMassRes 2.4.2"
    exit 1
fi

CHANNEL="$1"
VARIANT="${2:-}"
TUPLES_VERSION_NUM="${3:-2.4.2}"

case "$CHANNEL" in
    ggH|VBF) ;;
    *)
        echo "Error: invalid channel '$CHANNEL' (allowed: ggH, VBF)"
        exit 1
        ;;
esac

if [[ ! "$TUPLES_VERSION_NUM" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: tuples_version must be of the form a.b.c (e.g. 2.4.2)"
    exit 1
fi

ANALYZER_VERSION="v${TUPLES_VERSION_NUM%.*}"
TUPLES_VERSION="v${TUPLES_VERSION_NUM}"

SUBDIR="BDT_score/${CHANNEL}${VARIANT}/BFull_SNottH"
LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)/${SUBDIR}"

inEOS_PATH="/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_$ANALYZER_VERSION/tuples_$TUPLES_VERSION/"
EOS_DIR="${inEOS_PATH}${SUBDIR}/"

FILES=(
    "signal_Combined.root"
    "background_Combined.root"
    "data_Combined.root"
)

COPY_MAX_RETRIES=10
COPY_RETRY_DELAY=10


if [ ! -d "$LOCAL_DIR" ]; then
    echo "Error: local directory not found:"
    echo "    $LOCAL_DIR"
    exit 1
fi

MISSING=false
for f in "${FILES[@]}"; do
    if [ ! -f "${LOCAL_DIR}/${f}" ]; then
        echo "[ERROR] Missing ${LOCAL_DIR}/${f}"
        MISSING=true
    fi
done
if $MISSING; then
    echo "Run 'bash scripts/hadd_bdt.sh ${CHANNEL} ${VARIANT}' from the HToMuMu directory first"
    echo "(note: hadd_bdt.sh needs both ggH and VBF BDT-scored tuples present)."
    exit 1
fi


echo
echo "============================================================"
echo "Copying hadded BDT score tuples to EOS"
echo "Source:"
echo "    ${LOCAL_DIR}/"
echo "Destination:"
echo "    ${EOS_DIR}"
echo "============================================================"
echo

xrdfs root://cmseos.fnal.gov mkdir -p "${EOS_DIR}"

FAILED=()

for f in "${FILES[@]}"; do

    EOS_OUTPUT="root://cmseos.fnal.gov//${EOS_DIR#/}${f}"

    echo
    echo "============================================================"
    echo "Copying ${f}"
    echo "    -> ${EOS_OUTPUT}"
    echo "============================================================"

    COPY_SUCCESS=false

    for ATTEMPT in $(seq 1 ${COPY_MAX_RETRIES}); do

        echo "EOS copy attempt ${ATTEMPT}/${COPY_MAX_RETRIES}"

        if eos cp "${LOCAL_DIR}/${f}" "${EOS_OUTPUT}"; then
            COPY_SUCCESS=true
            echo "[OK] ${f} copied on attempt ${ATTEMPT}"
            break
        fi

        echo "[WARNING] EOS copy attempt ${ATTEMPT} failed."

        if [ $ATTEMPT -lt $COPY_MAX_RETRIES ]; then
            echo "Retrying in ${COPY_RETRY_DELAY} seconds..."
            sleep ${COPY_RETRY_DELAY}
        fi

    done

    if ! $COPY_SUCCESS; then
        echo "[ERROR] ${f} failed after ${COPY_MAX_RETRIES} attempts."
        FAILED+=("$f")
    fi

done


echo
echo "============================================================"
if (( ${#FAILED[@]} == 0 )); then
    echo " ALL FILES COPIED"
    echo " ${EOS_DIR}"
    echo "============================================================"
else
    echo " COPY FAILED FOR: ${FAILED[*]}"
    echo "============================================================"
    exit 1
fi
