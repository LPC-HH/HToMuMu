#!/bin/bash
#
# hadd the per-job CreateTuple outputs on EOS into <Type>_<Era>_tuples.root.
#
# Usage:
#   ./hadd_tuples_EOS.sh [-e ERAS] [-t TYPES] [-c | -eos] [-s]
#   ./hadd_tuples_EOS.sh -e 2024 -t "ggH VBF"          # only ggH_2024 and VBF_2024
#   ./hadd_tuples_EOS.sh -e "2023 2023BPix" -t DY -c   # DY for two eras, copy to EOS
#   ./hadd_tuples_EOS.sh -e 2024 -t DY -s -eos         # Z-peak-sized DY: build on scratch, move to EOS
#   ./hadd_tuples_EOS.sh                               # everything
# ERAS / TYPES are space- or comma-separated; default is all of ALL_ERAS / ALL_TYPES.
# -s writes the merged files to 3DayLifetime scratch instead of the current directory
#    (use it when outputs won't fit in the nobackup quota, e.g. with the Z region included).
# Merging goes through merge_large_tree.C (not plain hadd) so trees > 100 GB are not
# split into <name>_1.root.

ANALYZER_VERSION="v2.8"
TUPLES_VERSION="v2.8.0"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRATCH_DIR="/uscmst1b_scratch/lpc1/3DayLifetime/$USER/hadd_tuples_${TUPLES_VERSION}"
WORK_DIR="."
USE_SCRATCH=false

EOS_PATH="/eos/uscms/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_$ANALYZER_VERSION/tuples_$TUPLES_VERSION/"
inEOS_PATH="/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_$ANALYZER_VERSION/tuples_$TUPLES_VERSION/"

COPY_TO_EOS=false
DELETE_AFTER_COPY=false

ALL_ERAS="2022 2022EE 2023 2023BPix 2024 2025 2026"
ALL_TYPES="Data DY EWK TT DiBoson ggH VBF ttH"
SEL_ERAS="${ALL_ERAS}"
SEL_TYPES="${ALL_TYPES}"


############################################################
# Parse options
############################################################

while [[ $# -gt 0 ]]; do

    case "$1" in

        -c)
            COPY_TO_EOS=true
            DELETE_AFTER_COPY=false
            ;;

        -eos)
            COPY_TO_EOS=true
            DELETE_AFTER_COPY=true
            ;;

        -s|--scratch)
            USE_SCRATCH=true
            ;;

        -e|--eras)
            SEL_ERAS="${2//,/ }"
            shift
            ;;

        -t|--types)
            SEL_TYPES="${2//,/ }"
            shift
            ;;

        *)
            echo "[ERROR] Unknown option: $1"
            echo
            echo "Usage:"
            echo "  $0          # hadd locally and keep local files"
            echo "  $0 -c       # hadd locally, copy to EOS, keep local files"
            echo "  $0 -eos     # hadd locally, copy to EOS, delete local files"
            echo "  -e|--eras  \"2024 2023BPix\"   only these eras  (${ALL_ERAS})"
            echo "  -t|--types \"ggH VBF DY\"      only these types (${ALL_TYPES})"
            echo "  -s|--scratch                 write merged files to ${SCRATCH_DIR}"
            echo "                               instead of the current directory (e.g. $0 -e 2024 -t DY -s -eos)"
            exit 1
            ;;

    esac

    shift

done


############################################################
# Era / type selection
############################################################

in_list()  # in_list WORD "LIST": exact, case-sensitive word match
{
    [[ " $2 " == *" $1 "* ]]
}

for ERA in ${SEL_ERAS}; do
    in_list "${ERA}" "${ALL_ERAS}" || { echo "[ERROR] Unknown era '${ERA}'. Valid: ${ALL_ERAS}"; exit 1; }
done
for TYPE in ${SEL_TYPES}; do
    in_list "${TYPE}" "${ALL_TYPES}" || { echo "[ERROR] Unknown type '${TYPE}'. Valid: ${ALL_TYPES}"; exit 1; }
done

if $USE_SCRATCH; then
    WORK_DIR="${SCRATCH_DIR}"
    mkdir -p "${WORK_DIR}" || { echo "[ERROR] cannot create ${WORK_DIR}"; exit 1; }
fi

echo "Eras : ${SEL_ERAS}"
echo "Types: ${SEL_TYPES}"
echo "Work dir (hadd output): ${WORK_DIR}"

if $USE_SCRATCH && ! $COPY_TO_EOS; then
    echo
    echo "[WARNING] -s without -c/-eos: merged files stay only on 3DayLifetime scratch"
    echo "          and will be purged after 3 days."
fi


############################################################
# Prepare EOS directory
############################################################

if $COPY_TO_EOS; then

    echo
    echo "============================================================"

    if $DELETE_AFTER_COPY; then
        echo " EOS MODE"
        echo " hadd locally -> copy to EOS -> delete local file"
    else
        echo " COPY MODE"
        echo " hadd locally -> copy to EOS -> keep local file"
    fi

    echo "============================================================"
    echo "EOS destination:"
    echo "${inEOS_PATH}haddTuples/"
    echo "============================================================"
    echo

    eosmkdir "${inEOS_PATH}haddTuples/" 2>/dev/null || true

else

    echo
    echo "============================================================"
    echo " LOCAL MODE"
    echo " hadd locally -> keep local file"
    echo "============================================================"
    echo

fi


COPY_MAX_RETRIES=10
COPY_RETRY_DELAY=10


merge()
{
    OUTPUT_FILE="$1"
    shift
    OUT_PATH="${WORK_DIR}/${OUTPUT_FILE}"

    echo
    echo "============================================================"
    echo "Creating: ${OUT_PATH}"
    echo "============================================================"


    # Inputs: a pattern that matches nothing (e.g. <dataset>{,_ext*}/*.root for a dataset without
    # extensions) stays unexpanded and is dropped here; duplicates are removed.
    local -a INPUTS=()
    local -A SEEN=()
    local INPUT
    for INPUT in "$@"; do
        if [[ ! -e "${INPUT}" ]]; then
            [[ "${INPUT}" == *_ext\** ]] || echo "[WARNING] no input matches ${INPUT}"
            continue
        fi
        [[ -n "${SEEN[${INPUT}]:-}" ]] && continue
        SEEN[${INPUT}]=1
        INPUTS+=("${INPUT}")
    done
    if (( ${#INPUTS[@]} == 0 )); then
        echo "[ERROR] no input files for ${OUT_PATH}"
        return 1
    fi
    # Directories merged (extensions are normalised together by CreateTuple: h_sumOfgenWeight_sample)
    printf '%s\n' "${INPUTS[@]}" | xargs -n1 dirname | sort | uniq -c | sed 's/^/    /'

    # hadd equivalent that lifts the 100 GB TTree limit (see merge_large_tree.C)
    INPUT_LIST="$(mktemp "${WORK_DIR}/.hadd_inputs_XXXXXX.txt")"
    printf '%s\n' "${INPUTS[@]}" > "${INPUT_LIST}"

    root -l -b -q "${SCRIPT_DIR}/merge_large_tree.C+(\"${OUT_PATH}\",\"${INPUT_LIST}\")"

    HADD_STATUS=$?
    rm -f "${INPUT_LIST}"

    if [ $HADD_STATUS -ne 0 ]; then
        echo
        echo "[ERROR] hadd failed for:"
        echo "        ${OUT_PATH}"
        echo
        return 1
    fi

    if $COPY_TO_EOS; then
        
        EOS_OUTPUT="root://cmseos.fnal.gov//${inEOS_PATH#/}haddTuples/${OUTPUT_FILE}"

        echo
        echo "Copying ${OUT_PATH} to EOS..."
        echo "Destination:"
        echo "    ${EOS_OUTPUT}"
        echo

        COPY_SUCCESS=false

        for ATTEMPT in $(seq 1 ${COPY_MAX_RETRIES}); do

            echo "------------------------------------------------------------"
            echo "EOS copy attempt ${ATTEMPT}/${COPY_MAX_RETRIES}"
            echo "------------------------------------------------------------"

            eos cp "${OUT_PATH}" "${EOS_OUTPUT}"

            COPY_STATUS=$?

            if [ $COPY_STATUS -eq 0 ]; then

                COPY_SUCCESS=true

                echo
                echo "[OK] EOS copy successful on attempt ${ATTEMPT}"
                echo

                break

            fi


            echo
            echo "[WARNING] EOS copy attempt ${ATTEMPT} failed."

            if [ $ATTEMPT -lt $COPY_MAX_RETRIES ]; then
                echo "Retrying in ${COPY_RETRY_DELAY} seconds..."
                echo
                sleep ${COPY_RETRY_DELAY}
            fi

        done


        if ! $COPY_SUCCESS; then

            echo
            echo "============================================================"
            echo "[ERROR] EOS COPY FAILED"
            echo "============================================================"
            echo "File:"
            echo "    ${OUT_PATH}"
            echo
            echo "Failed after ${COPY_MAX_RETRIES} attempts."
            echo
            echo "Local file will be kept."
            echo "============================================================"
            echo

            return 1

        fi


        if $DELETE_AFTER_COPY; then

            echo "Removing local file:"
            echo "    ${OUT_PATH}"

            rm -f "${OUT_PATH}"

        else

            echo "Keeping local file:"
            echo "    ${OUT_PATH}"

        fi

    fi

    return 0
}


# merge only if <Type>_<Era>_tuples.root is in the -t / -e selection
merge_selected()
{
    local NAME="${1%_tuples.root}"
    local TYPE="${NAME%%_*}"   # first field: EWK_pythia_2024 is selected by -t EWK
    local ERA="${NAME##*_}"    # last field
    in_list "${TYPE}" "${SEL_TYPES}" && in_list "${ERA}" "${SEL_ERAS}" || return 0
    merge "$@"
}


era_banner()
{
    in_list "$1" "${SEL_ERAS}" || return 0
    echo
    echo "############################################################"
    echo "# $1"
    echo "############################################################"
}



############################################################
# 2022
############################################################

era_banner 2022

merge_selected Data_2022_tuples.root \
    ${EOS_PATH}Muon_2022{C..D}/*.root \
    ${EOS_PATH}SingleMuon_2022C/*.root

# All-aMC@NLO DY (stitch_weight is already in the weights, lib/DYStitching.h): jet-binned 0J/1J/2J
# everywhere + 105to160 and VBFFilter inside LHE mll [105, 160). No POWHEG.
merge_selected DY_2022_tuples.root \
    ${EOS_PATH}DYto2L-2Jets_{0,1,2}J_Summer22{,_ext*}/*.root \
    ${EOS_PATH}DYto2Mu-2Jets_105to160_Summer22{,_ext*}/*.root \
    ${EOS_PATH}DYto2Mu-2Jets_105to160_VBFFilter_Summer22{,_ext*}/*.root

merge_selected EWK_2022_tuples.root \
    ${EOS_PATH}EWK_2Mu2J_Summer22{,_ext*}/*.root

# Same EWK process showered with Pythia (alternative to the nominal Herwig7 2Mu2J sample)
merge_selected EWK_pythia_2022_tuples.root \
    ${EOS_PATH}EWK_2Mu2J_pythia_Summer22{,_ext*}/*.root

merge_selected TT_2022_tuples.root \
    ${EOS_PATH}TTto2L2Nu_Summer22{,_ext*}/*.root \
    ${EOS_PATH}TTtoLNu2Q_Summer22{,_ext*}/*.root

merge_selected DiBoson_2022_tuples.root \
    ${EOS_PATH}WZto2L2Q_*22{,_ext*}/*.root \
    ${EOS_PATH}WZto3LNu_*22{,_ext*}/*.root \
    ${EOS_PATH}ZZto2L2Nu_*22{,_ext*}/*.root \
    ${EOS_PATH}ZZto2L2Q_*22{,_ext*}/*.root \
    ${EOS_PATH}ZZto4L_*22{,_ext*}/*.root \
    ${EOS_PATH}WWto2L2Nu_*22{,_ext*}/*.root

merge_selected ggH_2022_tuples.root \
    ${EOS_PATH}ggH_*22{,_ext*}/*.root

merge_selected VBF_2022_tuples.root \
    ${EOS_PATH}VBF_*22{,_ext*}/*.root

merge_selected ttH_2022_tuples.root \
    ${EOS_PATH}ttH_*22{,_ext*}/*.root



############################################################
# 2022EE
############################################################

era_banner 2022EE

merge_selected Data_2022EE_tuples.root \
    ${EOS_PATH}Muon*_2022{E..G}/*.root

# All-aMC@NLO DY (stitch_weight is already in the weights, lib/DYStitching.h): jet-binned 0J/1J/2J
# everywhere + 105to160 and VBFFilter inside LHE mll [105, 160). No POWHEG.
merge_selected DY_2022EE_tuples.root \
    ${EOS_PATH}DYto2L-2Jets_{0,1,2}J_Summer22EE{,_ext*}/*.root \
    ${EOS_PATH}DYto2Mu-2Jets_105to160_Summer22EE{,_ext*}/*.root \
    ${EOS_PATH}DYto2Mu-2Jets_105to160_VBFFilter_Summer22EE{,_ext*}/*.root

merge_selected EWK_2022EE_tuples.root \
    ${EOS_PATH}EWK_2Mu2J_Summer22EE{,_ext*}/*.root

# Same EWK process showered with Pythia (alternative to the nominal Herwig7 2Mu2J sample)
merge_selected EWK_pythia_2022EE_tuples.root \
    ${EOS_PATH}EWK_2Mu2J_pythia_Summer22EE{,_ext*}/*.root

merge_selected TT_2022EE_tuples.root \
    ${EOS_PATH}TTto2L2Nu_Summer22EE{,_ext*}/*.root \
    ${EOS_PATH}TTtoLNu2Q_Summer22EE{,_ext*}/*.root

merge_selected DiBoson_2022EE_tuples.root \
    ${EOS_PATH}WZto2L2Q_*22EE{,_ext*}/*.root \
    ${EOS_PATH}WZto3LNu_*22EE{,_ext*}/*.root \
    ${EOS_PATH}ZZto2L2Nu_*22EE{,_ext*}/*.root \
    ${EOS_PATH}ZZto2L2Q_*22EE{,_ext*}/*.root \
    ${EOS_PATH}ZZto4L_*22EE{,_ext*}/*.root \
    ${EOS_PATH}WWto2L2Nu_*22EE{,_ext*}/*.root

merge_selected ggH_2022EE_tuples.root \
    ${EOS_PATH}ggH_*22EE{,_ext*}/*.root

merge_selected VBF_2022EE_tuples.root \
    ${EOS_PATH}VBF_*22EE{,_ext*}/*.root

merge_selected ttH_2022EE_tuples.root \
    ${EOS_PATH}ttH_*22EE{,_ext*}/*.root



############################################################
# 2023
############################################################

era_banner 2023

merge_selected Data_2023_tuples.root \
    ${EOS_PATH}Muon*_2023C*/*.root

# All-aMC@NLO DY (stitch_weight is already in the weights, lib/DYStitching.h): jet-binned 0J/1J/2J
# everywhere + 105to160 and VBFFilter inside LHE mll [105, 160). No POWHEG.
merge_selected DY_2023_tuples.root \
    ${EOS_PATH}DYto2L-2Jets_{0,1,2}J_Summer23{,_ext*}/*.root \
    ${EOS_PATH}DYto2Mu-2Jets_105to160_Summer23{,_ext*}/*.root \
    ${EOS_PATH}DYto2Mu-2Jets_105to160_VBFFilter_Summer23{,_ext*}/*.root

merge_selected EWK_2023_tuples.root \
    ${EOS_PATH}EWK_2Mu2J_Summer23{,_ext*}/*.root

# Same EWK process showered with Pythia (alternative to the nominal Herwig7 2Mu2J sample)
merge_selected EWK_pythia_2023_tuples.root \
    ${EOS_PATH}EWK_2Mu2J_pythia_Summer23{,_ext*}/*.root

merge_selected TT_2023_tuples.root \
    ${EOS_PATH}TTto2L2Nu_Summer23{,_ext*}/*.root \
    ${EOS_PATH}TTtoLNu2Q_Summer23{,_ext*}/*.root

merge_selected DiBoson_2023_tuples.root \
    ${EOS_PATH}WZto2L2Q_*23{,_ext*}/*.root \
    ${EOS_PATH}WZto3LNu_*23{,_ext*}/*.root \
    ${EOS_PATH}ZZto2L2Nu_*23{,_ext*}/*.root \
    ${EOS_PATH}ZZto2L2Q_*23{,_ext*}/*.root \
    ${EOS_PATH}ZZto4L_*23{,_ext*}/*.root \
    ${EOS_PATH}WWto2L2Nu_*23{,_ext*}/*.root

merge_selected ggH_2023_tuples.root \
    ${EOS_PATH}ggH_*23{,_ext*}/*.root

merge_selected VBF_2023_tuples.root \
    ${EOS_PATH}VBF_*23{,_ext*}/*.root

merge_selected ttH_2023_tuples.root \
    ${EOS_PATH}ttH_*23{,_ext*}/*.root



era_banner 2023BPix

merge_selected Data_2023BPix_tuples.root \
    ${EOS_PATH}Muon*_2023D*/*.root

# All-aMC@NLO DY (stitch_weight is already in the weights, lib/DYStitching.h): jet-binned 0J/1J/2J
# everywhere + 105to160 and VBFFilter inside LHE mll [105, 160). No POWHEG.
merge_selected DY_2023BPix_tuples.root \
    ${EOS_PATH}DYto2L-2Jets_{0,1,2}J_Summer23BPix{,_ext*}/*.root \
    ${EOS_PATH}DYto2Mu-2Jets_105to160_Summer23BPix{,_ext*}/*.root \
    ${EOS_PATH}DYto2Mu-2Jets_105to160_VBFFilter_Summer23BPix{,_ext*}/*.root

merge_selected EWK_2023BPix_tuples.root \
    ${EOS_PATH}EWK_2Mu2J_Summer23BPix{,_ext*}/*.root

# Same EWK process showered with Pythia (alternative to the nominal Herwig7 2Mu2J sample)
merge_selected EWK_pythia_2023BPix_tuples.root \
    ${EOS_PATH}EWK_2Mu2J_pythia_Summer23BPix{,_ext*}/*.root

merge_selected TT_2023BPix_tuples.root \
    ${EOS_PATH}TTto2L2Nu_Summer23BPix{,_ext*}/*.root \
    ${EOS_PATH}TTtoLNu2Q_Summer23BPix{,_ext*}/*.root

merge_selected DiBoson_2023BPix_tuples.root \
    ${EOS_PATH}WZto2L2Q_*23BPix{,_ext*}/*.root \
    ${EOS_PATH}WZto3LNu_*23BPix{,_ext*}/*.root \
    ${EOS_PATH}ZZto2L2Nu_*23BPix{,_ext*}/*.root \
    ${EOS_PATH}ZZto2L2Q_*23BPix{,_ext*}/*.root \
    ${EOS_PATH}ZZto4L_*23BPix{,_ext*}/*.root \
    ${EOS_PATH}WWto2L2Nu_*23BPix{,_ext*}/*.root

merge_selected ggH_2023BPix_tuples.root \
    ${EOS_PATH}ggH_*23BPix{,_ext*}/*.root

merge_selected VBF_2023BPix_tuples.root \
    ${EOS_PATH}VBF_*23BPix{,_ext*}/*.root

merge_selected ttH_2023BPix_tuples.root \
    ${EOS_PATH}ttH_*23BPix{,_ext*}/*.root


era_banner 2024

merge_selected Data_2024_tuples.root \
    ${EOS_PATH}Muon*_2024*/*.root

# All-aMC@NLO DY (stitch_weight is already in the weights, lib/DYStitching.h): jet-binned 0J/1J/2J
# everywhere + 105to160 and VBFFilter inside LHE mll [105, 160). No POWHEG.
merge_selected DY_2024_tuples.root \
    ${EOS_PATH}DYto2Mu-2Jets_{0,1,2}J_Summer24{,_ext*}/*.root \
    ${EOS_PATH}DYto2Mu-2Jets_105to160_Summer24{,_ext*}/*.root \
    ${EOS_PATH}DYto2Mu-2Jets_105to160_VBFFilter_Summer24{,_ext*}/*.root

merge_selected EWK_2024_tuples.root \
    ${EOS_PATH}EWK_2Mu2J_Summer24{,_ext*}/*.root

# Same EWK process showered with Pythia (alternative to the nominal Herwig7 2Mu2J sample)
merge_selected EWK_pythia_2024_tuples.root \
    ${EOS_PATH}EWK_2Mu2J_pythia_Summer24{,_ext*}/*.root

merge_selected TT_2024_tuples.root \
    ${EOS_PATH}TTto2L2Nu_Summer24{,_ext*}/*.root \
    ${EOS_PATH}TTtoLNu2Q_Summer24{,_ext*}/*.root

merge_selected DiBoson_2024_tuples.root \
    ${EOS_PATH}WZto2L2Q_*24{,_ext*}/*.root \
    ${EOS_PATH}WZto3LNu_*24{,_ext*}/*.root \
    ${EOS_PATH}ZZto2L2Nu_*24{,_ext*}/*.root \
    ${EOS_PATH}ZZto2L2Q_*24{,_ext*}/*.root \
    ${EOS_PATH}ZZto4L_*24{,_ext*}/*.root \
    ${EOS_PATH}WWto2L2Nu_*24{,_ext*}/*.root

merge_selected ggH_2024_tuples.root \
    ${EOS_PATH}ggH_*24{,_ext*}/*.root

merge_selected VBF_2024_tuples.root \
    ${EOS_PATH}VBF_*24{,_ext*}/*.root

merge_selected ttH_2024_tuples.root \
    ${EOS_PATH}ttH_*24{,_ext*}/*.root



############################################################
# 2025
############################################################

era_banner 2025

merge_selected Data_2025_tuples.root \
    ${EOS_PATH}Muon*_2025*/*.root

# All-aMC@NLO DY (stitch_weight is already in the weights, lib/DYStitching.h): jet-binned 0J/1J/2J
# everywhere + 105to160 and VBFFilter inside LHE mll [105, 160). No POWHEG.
merge_selected DY_2025_tuples.root \
    ${EOS_PATH}DYto2Mu-2Jets_{0,1,2}J_Summer25{,_ext*}/*.root \
    ${EOS_PATH}DYto2Mu-2Jets_105to160_Summer25{,_ext*}/*.root \
    ${EOS_PATH}DYto2Mu-2Jets_105to160_VBFFilter_Summer25{,_ext*}/*.root

merge_selected EWK_2025_tuples.root \
    ${EOS_PATH}EWK_2Mu2J_Summer25{,_ext*}/*.root

# Same EWK process showered with Pythia (alternative to the nominal Herwig7 2Mu2J sample)
merge_selected EWK_pythia_2025_tuples.root \
    ${EOS_PATH}EWK_2Mu2J_pythia_Summer25{,_ext*}/*.root

merge_selected TT_2025_tuples.root \
    ${EOS_PATH}TTto2L2Nu_Summer25{,_ext*}/*.root \
    ${EOS_PATH}TTtoLNu2Q_Summer25{,_ext*}/*.root

merge_selected DiBoson_2025_tuples.root \
    ${EOS_PATH}WZto2L2Q_*25{,_ext*}/*.root \
    ${EOS_PATH}WZto3LNu_*25{,_ext*}/*.root \
    ${EOS_PATH}ZZto2L2Nu_*25{,_ext*}/*.root \
    ${EOS_PATH}ZZto2L2Q_*25{,_ext*}/*.root \
    ${EOS_PATH}ZZto4L_*25{,_ext*}/*.root \
    ${EOS_PATH}WWto2L2Nu_*25{,_ext*}/*.root

merge_selected ggH_2025_tuples.root \
    ${EOS_PATH}ggH_*25{,_ext*}/*.root

merge_selected VBF_2025_tuples.root \
    ${EOS_PATH}VBF_*25{,_ext*}/*.root

############################################################
# 2026
############################################################

era_banner 2026

merge_selected Data_2026_tuples.root \
    ${EOS_PATH}Muon*_2026*/*.root

############################################################
# Finished
############################################################

echo
echo "============================================================"
echo " ALL HADD JOBS FINISHED"
echo "============================================================"

if $COPY_TO_EOS; then

    echo "Files were copied to:"
    echo "${inEOS_PATH}haddTuples/"

    if $DELETE_AFTER_COPY; then
        echo "Local copies were deleted after successful EOS copies."
    else
        echo "Local copies were kept in ${WORK_DIR}."
    fi

else

    echo "Files were stored in ${WORK_DIR} only."

fi

echo "============================================================"
