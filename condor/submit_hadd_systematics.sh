#!/bin/bash

set -e

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <tuples_version>"
    echo "Example:"
    echo "  bash $0 2.2.1"
    exit 1
fi

VERSION="${1#v}"

echo "Using tuples version: v${VERSION}"


mkdir -p logs

PROCESSES=(
    "ggH"
    "VBF"
)


# ============================================================
# Muon pT systematics
# ============================================================

MUON_PT_SYSTS=(
    "scale_up"
    "scale_down"
    "smearing_up"
    "smearing_down"
)


# ============================================================
# JES / JER systematic names
# ============================================================

JET_JES_SYST_NAMES=(

    # --------------------------------------------------------
    # Global JES
    # --------------------------------------------------------

   "CMS_scale_j_FlavorQCD"
   "CMS_scale_j_RelativeBal"
   "CMS_scale_j_HF"
   "CMS_scale_j_BBEC1"
   "CMS_scale_j_EC2"
   "CMS_scale_j_Absolute"

   # # --------------------------------------------------------
   # # 2022
   # # --------------------------------------------------------

   "CMS_scale_j_BBEC1_2022"
   "CMS_scale_j_RelativeSample_2022"
   "CMS_scale_j_EC2_2022"
   "CMS_scale_j_HF_2022"
   "CMS_scale_j_Absolute_2022"

   # # --------------------------------------------------------
   # # 2022EE
   # # --------------------------------------------------------

   "CMS_scale_j_BBEC1_2022EE"
   "CMS_scale_j_RelativeSample_2022EE"
   "CMS_scale_j_EC2_2022EE"
   "CMS_scale_j_HF_2022EE"
   "CMS_scale_j_Absolute_2022EE"

   # --------------------------------------------------------
   # 2023
   # --------------------------------------------------------

   "CMS_scale_j_BBEC1_2023"
   "CMS_scale_j_RelativeSample_2023"
   "CMS_scale_j_EC2_2023"
   "CMS_scale_j_HF_2023"
   "CMS_scale_j_Absolute_2023"

   # --------------------------------------------------------
   # 2023BPix
   # --------------------------------------------------------

   "CMS_scale_j_BBEC1_2023BPix"
   "CMS_scale_j_RelativeSample_2023BPix"
   "CMS_scale_j_EC2_2023BPix"
   "CMS_scale_j_HF_2023BPix"
   "CMS_scale_j_Absolute_2023BPix"

   # --------------------------------------------------------
   # 2024
   # --------------------------------------------------------

   "CMS_scale_j_BBEC1_2024"
   "CMS_scale_j_RelativeSample_2024"
   "CMS_scale_j_EC2_2024"
   "CMS_scale_j_HF_2024"
   "CMS_scale_j_Absolute_2024"

    # --------------------------------------------------------
    # 2025
    # --------------------------------------------------------

   "CMS_scale_j_BBEC1_2025"
   "CMS_scale_j_RelativeSample_2025"
   "CMS_scale_j_EC2_2025"
   "CMS_scale_j_HF_2025"
   "CMS_scale_j_Absolute_2025"


    # ========================================================
    # JER 2022
    # ========================================================

   "CMS_res_j_eta0to1p93_pt0toInf_2022"
   "CMS_res_j_eta1p93to2p5_pt0toInf_2022"
   "CMS_res_j_eta2p5to3p0_pt0to50_2022"
   "CMS_res_j_eta2p5to3p0_pt50toInf_2022"
   "CMS_res_j_eta3to5_pt0to50_2022"
   "CMS_res_j_eta3to5_pt50toInf_2022"

    ## ========================================================
    ## JER 2022EE
    ## ========================================================

   "CMS_res_j_eta0to1p93_pt0toInf_2022EE"
   "CMS_res_j_eta1p93to2p5_pt0toInf_2022EE"
   "CMS_res_j_eta2p5to3p0_pt0to50_2022EE"
   "CMS_res_j_eta2p5to3p0_pt50toInf_2022EE"
   "CMS_res_j_eta3to5_pt0to50_2022EE"
   "CMS_res_j_eta3to5_pt50toInf_2022EE"

    ## ========================================================
    ## JER 2023
    ## ========================================================

   "CMS_res_j_eta0to1p93_pt0toInf_2023"
   "CMS_res_j_eta1p93to2p5_pt0toInf_2023"
   "CMS_res_j_eta2p5to3p0_pt0to50_2023"
   "CMS_res_j_eta2p5to3p0_pt50toInf_2023"
   "CMS_res_j_eta3to5_pt0to50_2023"
   "CMS_res_j_eta3to5_pt50toInf_2023"

    ## ========================================================
    ## JER 2023BPix
    ## ========================================================

   "CMS_res_j_eta0to1p93_pt0toInf_2023BPix"
   "CMS_res_j_eta1p93to2p5_pt0toInf_2023BPix"
   "CMS_res_j_eta2p5to3p0_pt0to50_2023BPix"
   "CMS_res_j_eta2p5to3p0_pt50toInf_2023BPix"
   "CMS_res_j_eta3to5_pt0to50_2023BPix"
   "CMS_res_j_eta3to5_pt50toInf_2023BPix"

    ## ========================================================
    ## JER 2024
    ## ========================================================

   "CMS_res_j_eta0to1p93_pt0toInf_2024"
   "CMS_res_j_eta1p93to2p5_pt0toInf_2024"
   "CMS_res_j_eta2p5to3p0_pt0to50_2024"
   "CMS_res_j_eta2p5to3p0_pt50toInf_2024"
   "CMS_res_j_eta3to5_pt0to50_2024"
   "CMS_res_j_eta3to5_pt50toInf_2024"

    # ========================================================
    # JER 2025
    # ========================================================

   "CMS_res_j_eta0to1p93_pt0toInf_2025"
   "CMS_res_j_eta1p93to2p5_pt0toInf_2025"
   "CMS_res_j_eta2p5to3p0_pt0to50_2025"
   "CMS_res_j_eta2p5to3p0_pt50toInf_2025"
   "CMS_res_j_eta3to5_pt0to50_2025"
   "CMS_res_j_eta3to5_pt50toInf_2025"
)


# ============================================================
# Build full systematic list
# ============================================================

SYSTEMATICS=()

for syst in "${MUON_PT_SYSTS[@]}"; do
    SYSTEMATICS+=("$syst")
done

for syst in "${JET_JES_SYST_NAMES[@]}"; do
    SYSTEMATICS+=("${syst}_up")
    SYSTEMATICS+=("${syst}_down")
done

SYSTEMATICS+=("nanoAOD")

# ============================================================
# Make job list
# ============================================================

JOB_FILE="systematics_jobs.txt"

> "$JOB_FILE"

for syst in "${SYSTEMATICS[@]}"; do

    for process in "${PROCESSES[@]}"; do

        echo "$process $syst $VERSION" >> "$JOB_FILE"

    done

done


# ============================================================
# Summary
# ============================================================

echo
echo "============================================================"
echo "Condor systematic hadd submission"
echo "============================================================"

echo "Version     : v${VERSION}"
echo "Processes   : ${#PROCESSES[@]}"
echo "Systematics : ${#SYSTEMATICS[@]}"
echo "Jobs        : $(wc -l < "$JOB_FILE")"

echo
echo "Job file:"
echo "$JOB_FILE"

echo
echo "First jobs:"
head "$JOB_FILE"

echo
echo "Last jobs:"
tail "$JOB_FILE"

echo
echo "============================================================"


# ============================================================
# Submit
# ============================================================

condor_submit hadd_systematics.sub
