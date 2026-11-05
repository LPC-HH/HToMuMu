#!/bin/bash
# Six-variant (plus the Asimov-Optuna ones once their configs exist) BDT comparison for ggH and VBF (train.py --stage compare), end to end:
#   {DEFAULT_PARAMS, Optuna} x {mass_res, flat, flatMassRes} training weights per channel.
# Each variant's fold models are reused if they exist (pass --retrain to retrain them all),
# every nominal tuple is skimmed once into root_io/tuples/BDT_score/<channel>compare/ with all
# six scores as branches, and both channels are then hadded.
#
# Run from python/xgboost on an EAF GPU node inside the xgboost_env micromamba environment:
#   bash run_compare.sh [--categories] [extra train.py options, e.g. --retrain --device cpu]
# --categories also runs plot_BDT_Categories.py for every variant of both channels.
# --plots-only only redraws the comparison plots from the saved models (no training, no tuples,
#   no hadd); e.g. bash run_compare.sh --plots-only --tight-cut 0.85. It reads the scores from
#   the compare tuples if they exist and are newer than the models (add --rescore to evaluate the
#   models on the training skims instead).
# --categories-only only runs plot_BDT_Categories.py for every variant of both channels on the
#   existing hadded compare tuples (no training, no scoring, no hadd). Each variant is saved
#   under its own key (<channel>compare_<variant>) in root_io/bdt_categories.json.

# the braces make bash read the whole script before running it, so editing this file
# during a (long) run cannot break that run
{
set -e
cd "$(dirname "$0")"

run_categories=false
categories_only=false
plots_only=false
train_args=()
for arg in "$@"; do
    if [[ "${arg}" == "--categories" ]]; then
        run_categories=true
    elif [[ "${arg}" == "--categories-only" ]]; then
        categories_only=true
    else
        [[ "${arg}" == "--plots-only" ]] && plots_only=true
        train_args+=("${arg}")
    fi
done
if ${plots_only} && ${run_categories}; then
    echo "--plots-only and --categories are mutually exclusive"
    exit 1
fi

if ${categories_only} && { (( ${#train_args[@]} > 0 )) || ${run_categories}; }; then
    echo "--categories-only takes no other options"
    exit 1
fi

channels=("ggH" "VBF")
era="Combined"
variants=("base" "optimized" "flat" "optimized_flat" "flatMassRes" "optimized_flatMassRes")
# the Asimov-Optuna variants exist once train.py --stage dev --objective asimov (asimov_fit) has
# written its config; asimov_config <channel> <opt_tag>
asimov_config() { echo "python/xgboost/models/dev/config_optuna_${1}_${era}_BFull_SNottH_flatMassRes_${2}.json"; }

# one at a time: each run rewrites the whole root_io/bdt_categories.json
run_all_categories() {
    cd plot_macros
    for channel in "${channels[@]}"; do
        channel_variants=("${variants[@]}")
        for opt_tag in asimov asimovFit; do
            [[ -f "../$(asimov_config "${channel}" "${opt_tag}")" ]] && channel_variants+=("${opt_tag}_flatMassRes")
        done
        for variant in "${channel_variants[@]}"; do
            echo "========== ${channel}: categories for ${variant} =========="
            python3 plot_BDT_Categories.py "${channel}" "${era}" --compare --score "${variant}"
        done
    done
}

if ${categories_only}; then
    cd ../..
    for channel in "${channels[@]}"; do
        for sample in background signal data; do
            file="root_io/tuples/BDT_score/${channel}compare/BFull_SNottH/${sample}_${era}.root"
            if [[ ! -f "${file}" ]]; then
                echo "${file} not found: run bash run_compare.sh first"
                exit 1
            fi
        done
    done
    run_all_categories
    exit 0
fi

for channel in "${channels[@]}"; do
    echo "========== ${channel}: train.py --stage compare ${train_args[*]} =========="
    python3 train.py "${channel}" "${era}" --stage compare "${train_args[@]}"
done

if ${plots_only}; then
    exit 0
fi

# hadd_template.sh hadds the ggH and VBF signal files together, so both channels must be
# scored before either directory is hadded
cd ../..
for channel in "${channels[@]}"; do
    echo "========== ${channel}: hadd =========="
    bash scripts/hadd_bdt.sh "${channel}" compare
done

if ${run_categories}; then
    run_all_categories
fi

exit 0
}
