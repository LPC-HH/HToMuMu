#!/bin/bash

ANALYZER_VERSION="v2.8"
TUPLES_VERSION="v2.8.0"

inEOS_PATH="/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_$ANALYZER_VERSION/tuples_$TUPLES_VERSION/"
EOS_HADD_PATH="root://cmseos.fnal.gov/${inEOS_PATH}haddTuples/"
#EOS_HADD_PATH="./"

COPY_TO_EOS=false
DELETE_AFTER_COPY=false
WORK_DIR="."

for opt in "$@"; do
    case "$opt" in
        -c)
            COPY_TO_EOS=true
            DELETE_AFTER_COPY=false
            ;;
        -eos)
            COPY_TO_EOS=true
            DELETE_AFTER_COPY=true
            ;;
        *)
            echo "Usage: $0 [-c|-eos]" >&2
            exit 1
            ;;
    esac
done

if $DELETE_AFTER_COPY; then
    WORK_DIR=$(mktemp -d "${TMPDIR:-/tmp}/hadd_tuples_XXXXXX") || exit 1
fi

echo "=============================================="
echo "Reading input tuples from:"
echo "${EOS_HADD_PATH}"
echo
echo "Working directory for combined tuples: ${WORK_DIR}"
echo "=============================================="


############### Combined ################

FAILED_MERGES=()
MERGED_FILES=()

merge()
{
    local output="$1"
    shift
    if hadd -f "${WORK_DIR}/${output}" "$@"; then
        MERGED_FILES+=("${WORK_DIR}/${output}")
    else
        FAILED_MERGES+=("$output")
    fi
}

merge Data_Combined_tuples.root \
    ${EOS_HADD_PATH}Data_2022_tuples.root \
    ${EOS_HADD_PATH}Data_2022EE_tuples.root \
    ${EOS_HADD_PATH}Data_2023_tuples.root \
    ${EOS_HADD_PATH}Data_2023BPix_tuples.root \
    ${EOS_HADD_PATH}Data_2024_tuples.root \
    ${EOS_HADD_PATH}Data_2025_tuples.root \
    ${EOS_HADD_PATH}Data_2026_tuples.root


merge DY_Combined_tuples.root \
    ${EOS_HADD_PATH}DY_2022_tuples.root \
    ${EOS_HADD_PATH}DY_2022EE_tuples.root \
    ${EOS_HADD_PATH}DY_2023_tuples.root \
    ${EOS_HADD_PATH}DY_2023BPix_tuples.root \
    ${EOS_HADD_PATH}DY_2024_tuples.root \
    ${EOS_HADD_PATH}DY_2025_tuples.root


merge EWK_Combined_tuples.root \
    ${EOS_HADD_PATH}EWK_2022_tuples.root \
    ${EOS_HADD_PATH}EWK_2022EE_tuples.root \
    ${EOS_HADD_PATH}EWK_2023_tuples.root \
    ${EOS_HADD_PATH}EWK_2023BPix_tuples.root \
    ${EOS_HADD_PATH}EWK_2024_tuples.root \
    ${EOS_HADD_PATH}EWK_2025_tuples.root

merge EWK_pythia_Combined_tuples.root \
    ${EOS_HADD_PATH}EWK_pythia_2022_tuples.root \
    ${EOS_HADD_PATH}EWK_pythia_2022EE_tuples.root \
    ${EOS_HADD_PATH}EWK_pythia_2023_tuples.root \
    ${EOS_HADD_PATH}EWK_pythia_2023BPix_tuples.root \
    ${EOS_HADD_PATH}EWK_pythia_2024_tuples.root \
    ${EOS_HADD_PATH}EWK_pythia_2025_tuples.root

merge TT_Combined_tuples.root \
    ${EOS_HADD_PATH}TT_2022_tuples.root \
    ${EOS_HADD_PATH}TT_2022EE_tuples.root \
    ${EOS_HADD_PATH}TT_2023_tuples.root \
    ${EOS_HADD_PATH}TT_2023BPix_tuples.root \
    ${EOS_HADD_PATH}TT_2024_tuples.root \
    ${EOS_HADD_PATH}TT_2025_tuples.root


merge DiBoson_Combined_tuples.root \
    ${EOS_HADD_PATH}DiBoson_2022_tuples.root \
    ${EOS_HADD_PATH}DiBoson_2022EE_tuples.root \
    ${EOS_HADD_PATH}DiBoson_2023_tuples.root \
    ${EOS_HADD_PATH}DiBoson_2023BPix_tuples.root \
    ${EOS_HADD_PATH}DiBoson_2024_tuples.root \
    ${EOS_HADD_PATH}DiBoson_2025_tuples.root


merge ggH_Combined_tuples.root \
    ${EOS_HADD_PATH}ggH_2022_tuples.root \
    ${EOS_HADD_PATH}ggH_2022EE_tuples.root \
    ${EOS_HADD_PATH}ggH_2023_tuples.root \
    ${EOS_HADD_PATH}ggH_2023BPix_tuples.root \
    ${EOS_HADD_PATH}ggH_2024_tuples.root \
    ${EOS_HADD_PATH}ggH_2025_tuples.root


merge VBF_Combined_tuples.root \
    ${EOS_HADD_PATH}VBF_2022_tuples.root \
    ${EOS_HADD_PATH}VBF_2022EE_tuples.root \
    ${EOS_HADD_PATH}VBF_2023_tuples.root \
    ${EOS_HADD_PATH}VBF_2023BPix_tuples.root \
    ${EOS_HADD_PATH}VBF_2024_tuples.root \
    ${EOS_HADD_PATH}VBF_2025_tuples.root


#hadd -f ttH_Combined_tuples.root \
#    ${EOS_HADD_PATH}ttH_2022_tuples.root \
#    ${EOS_HADD_PATH}ttH_2022EE_tuples.root \
#    ${EOS_HADD_PATH}ttH_2023_tuples.root \
#    ${EOS_HADD_PATH}ttH_2023BPix_tuples.root \
#    ${EOS_HADD_PATH}ttH_2024_tuples.root \
#   ${EOS_HADD_PATH}ttH_2025_tuples.root


############### Copy to EOS ################

if (( ${#FAILED_MERGES[@]} > 0 )); then
    echo "[ERROR] ${#FAILED_MERGES[@]} combined merge(s) failed:" >&2
    printf '    %s\n' "${FAILED_MERGES[@]}" >&2
    exit 1
fi

if $COPY_TO_EOS; then

    echo
    echo "=============================================="
    echo "Copying combined tuples to EOS"
    echo "Destination:"
    echo "${inEOS_PATH}haddTuples/"
    echo "=============================================="

    eosmkdir "${inEOS_PATH}haddTuples/" 2>/dev/null || true

    for output in "${MERGED_FILES[@]}"; do
        if ! eos cp "$output" "${EOS_HADD_PATH}"; then
            echo "[ERROR] EOS copy failed for ${output}. Local files are in ${WORK_DIR}." >&2
            exit 1
        fi
    done

    if $DELETE_AFTER_COPY; then
        rm -- "${MERGED_FILES[@]}" && rmdir -- "${WORK_DIR}"
    fi
fi
