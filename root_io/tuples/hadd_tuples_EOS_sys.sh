#!/bin/bash

ANALYZER_VERSION="v2.0"
TUPLES_VERSION="v2.0.0"

EOS_PATH="/eos/uscms/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_$ANALYZER_VERSION/tuples_$TUPLES_VERSION/"
inEOS_PATH="/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_$ANALYZER_VERSION/tuples_$TUPLES_VERSION/"

EOS_OUTDIR="/eos/uscms${inEOS_PATH}systematics/"

echo "Creating EOS output directory:"
echo "$EOS_OUTDIR"

xrdfs root://cmseos.fnal.gov mkdir -p "${inEOS_PATH}systematics/"

PROCESSES=(
    "ggH"
    "VBF"
)

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

MUON_PT_SYSTS=(
    "scale_up"
    "scale_down"
    "smearing_up"
    "smearing_down"
)

JET_JES_SYST_NAMES=(
    "CMS_scale_j_FlavorQCD"
    "CMS_scale_j_RelativeBal"
    "CMS_scale_j_HF"
    "CMS_scale_j_BBEC1"
    "CMS_scale_j_EC2"
    "CMS_scale_j_Absolute"

    "CMS_scale_j_BBEC1_2022"
    "CMS_scale_j_RelativeSample_2022"
    "CMS_scale_j_EC2_2022"
    "CMS_scale_j_HF_2022"
    "CMS_scale_j_Absolute_2022"

    "CMS_scale_j_BBEC1_2022EE"
    "CMS_scale_j_RelativeSample_2022EE"
    "CMS_scale_j_EC2_2022EE"
    "CMS_scale_j_HF_2022EE"
    "CMS_scale_j_Absolute_2022EE"

    "CMS_scale_j_BBEC1_2023"
    "CMS_scale_j_RelativeSample_2023"
    "CMS_scale_j_EC2_2023"
    "CMS_scale_j_HF_2023"
    "CMS_scale_j_Absolute_2023"

    "CMS_scale_j_BBEC1_2023BPix"
    "CMS_scale_j_RelativeSample_2023BPix"
    "CMS_scale_j_EC2_2023BPix"
    "CMS_scale_j_HF_2023BPix"
    "CMS_scale_j_Absolute_2023BPix"

    "CMS_scale_j_BBEC1_2024"
    "CMS_scale_j_RelativeSample_2024"
    "CMS_scale_j_EC2_2024"
    "CMS_scale_j_HF_2024"
    "CMS_scale_j_Absolute_2024"

    "CMS_scale_j_BBEC1_2025"
    "CMS_scale_j_RelativeSample_2025"
    "CMS_scale_j_EC2_2025"
    "CMS_scale_j_HF_2025"
    "CMS_scale_j_Absolute_2025"

    "CMS_res_j_eta0to1p93_pt0toInf_2022"
    "CMS_res_j_eta1p93to2p5_pt0toInf_2022"
    "CMS_res_j_eta2p5to3p0_pt0to50_2022"
    "CMS_res_j_eta2p5to3p0_pt50toInf_2022"
    "CMS_res_j_eta3to5_pt0to50_2022"
    "CMS_res_j_eta3to5_pt50toInf_2022"

    "CMS_res_j_eta0to1p93_pt0toInf_2022EE"
    "CMS_res_j_eta1p93to2p5_pt0toInf_2022EE"
    "CMS_res_j_eta2p5to3p0_pt0to50_2022EE"
    "CMS_res_j_eta2p5to3p0_pt50toInf_2022EE"
    "CMS_res_j_eta3to5_pt0to50_2022EE"
    "CMS_res_j_eta3to5_pt50toInf_2022EE"

    "CMS_res_j_eta0to1p93_pt0toInf_2023"
    "CMS_res_j_eta1p93to2p5_pt0toInf_2023"
    "CMS_res_j_eta2p5to3p0_pt0to50_2023"
    "CMS_res_j_eta2p5to3p0_pt50toInf_2023"
    "CMS_res_j_eta3to5_pt0to50_2023"
    "CMS_res_j_eta3to5_pt50toInf_2023"

    "CMS_res_j_eta0to1p93_pt0toInf_2023BPix"
    "CMS_res_j_eta1p93to2p5_pt0toInf_2023BPix"
    "CMS_res_j_eta2p5to3p0_pt0to50_2023BPix"
    "CMS_res_j_eta2p5to3p0_pt50toInf_2023BPix"
    "CMS_res_j_eta3to5_pt0to50_2023BPix"
    "CMS_res_j_eta3to5_pt50toInf_2023BPix"

    "CMS_res_j_eta0to1p93_pt0toInf_2024"
    "CMS_res_j_eta1p93to2p5_pt0toInf_2024"
    "CMS_res_j_eta2p5to3p0_pt0to50_2024"
    "CMS_res_j_eta2p5to3p0_pt50toInf_2024"
    "CMS_res_j_eta3to5_pt0to50_2024"
    "CMS_res_j_eta3to5_pt50toInf_2024"

    "CMS_res_j_eta0to1p93_pt0toInf_2025"
    "CMS_res_j_eta1p93to2p5_pt0toInf_2025"
    "CMS_res_j_eta2p5to3p0_pt0to50_2025"
    "CMS_res_j_eta2p5to3p0_pt50toInf_2025"
    "CMS_res_j_eta3to5_pt0to50_2025"
    "CMS_res_j_eta3to5_pt50toInf_2025"
)

SYSTEMATICS=()

for syst in "${MUON_PT_SYSTS[@]}"; do
    SYSTEMATICS+=("$syst")
done

for jes in "${JET_JES_SYST_NAMES[@]}"; do
    SYSTEMATICS+=("${jes}_up")
    SYSTEMATICS+=("${jes}_down")
done

run_hadd() {
    local output_file=$1
    shift

    local input_patterns=("$@")
    local input_files=()

    shopt -s nullglob

    for pattern in "${input_patterns[@]}"; do
        matches=( $pattern )

        if (( ${#matches[@]} == 0 )); then
            echo "[WARNING] No files matched:"
            echo "          $pattern"
            continue
        fi

        for f in "${matches[@]}"; do
            if [[ -f "$f" ]]; then
                input_files+=("$f")
            fi
        done
    done

    shopt -u nullglob

    if (( ${#input_files[@]} == 0 )); then
        echo "[WARNING] No valid input files for:"
        echo "          $output_file"
        echo "          Skipping."
        return
    fi

    echo
    echo "Creating:"
    echo "  $output_file"
    echo "Number of input files: ${#input_files[@]}"

    hadd -f "$output_file" "${input_files[@]}"
}

for syst in "${SYSTEMATICS[@]}"; do

    echo
    echo "============================================================"
    echo "Systematic: $syst"
    echo "============================================================"

    for process in "${PROCESSES[@]}"; do

        echo
        echo "Process: $process"

        input_patterns=()

        for era in "${ERAS[@]}"; do
            dataset_era=$(get_dataset_era_name "$era")

            if [[ "$dataset_era" == "UNKNOWN" ]]; then
                echo "[WARNING] Unknown era: $era"
                continue
            fi

            dataset_dir="${process}_${dataset_era}_${syst}"
            input_patterns+=( "${EOS_PATH}${dataset_dir}/*.root" )
        done

        output_file="${EOS_OUTDIR}${process}_Combined_${syst}_tuples.root"

        run_hadd "$output_file" "${input_patterns[@]}"

    done
done

echo
echo "Done."
echo "Files were written directly to:"
echo "$EOS_OUTDIR"
