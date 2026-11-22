#!/bin/bash
set -euo pipefail

# Split the hadded BDT_score tuples into per-category trees.
#
# Run from the HToMuMu directory:
#
#   bash scripts/run_splitting.sh [-bkgs] [-r] [-d] [-v <variant>]
#
# Options:
#   -bkgs  Split individual background MC samples (DY, EWK, TT, DiBoson).
#          Without this option, split signal, data, and combined bkg.
#   -r     Use the re-categorization BDT.
#   -d     Delete previous split tuples for the selected mode and exit.
#   -v     BDT variant label (default: asimovFit_flatMassRes).
#
# Examples:
#   bash scripts/run_splitting.sh
#   bash scripts/run_splitting.sh -bkgs
#   bash scripts/run_splitting.sh -r
#   bash scripts/run_splitting.sh -v asimovFit_flatMassRes
#   bash scripts/run_splitting.sh -bkgs -r -v asimovFit_flatMassRes
#   bash scripts/run_splitting.sh -bkgs -d

RECAT_ARG=""
REMOVE_PREVIOUS=false
VARIANT="asimovFit_flatMassRes"
BKGS_ONLY=false

# -------------------------------------------------------
# Parse arguments
# -------------------------------------------------------

while [[ $# -gt 0 ]]; do
    case "$1" in
        -bkgs)
            BKGS_ONLY=true
            shift
            ;;
        -r)
            RECAT_ARG="-r"
            shift
            ;;
        -d)
            REMOVE_PREVIOUS=true
            shift
            ;;
        -v)
            if [[ $# -lt 2 ]]; then
                echo "[Error] -v requires a variant label"
                exit 1
            fi
            VARIANT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [-bkgs] [-r] [-d] [-v <variant>]"
            exit 0
            ;;
        *)
            echo "[Error] Unknown option: $1"
            echo "Usage: $0 [-bkgs] [-r] [-d] [-v <variant>]"
            exit 1
            ;;
    esac
done

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------

VARIANT_SUFFIX="${VARIANT//_/}"
[ "$VARIANT" = "base" ] && VARIANT_SUFFIX=""

SUFFIX="${RECAT_ARG:+reCat}${VARIANT_SUFFIX}"

SPLIT_DIR="./root_io/tuples/split_tuples"

echo "[Config] Variant: ${VARIANT}"
echo "[Config] Recategorization: ${RECAT_ARG:-disabled}"
echo "[Config] Background-only mode: ${BKGS_ONLY}"
echo "[Config] Output suffix: ${SUFFIX}"

# -------------------------------------------------------
# Remove previous outputs
# -------------------------------------------------------

if $REMOVE_PREVIOUS; then

    echo "---------------- Removing previous split tuples ----------------"

    for channel in ggH VBF; do

        OUTPUT_DIR="${SPLIT_DIR}/${channel}${SUFFIX}"

        if $BKGS_ONLY; then

            for sample in DY EWK TT DiBoson; do
                FILE="${OUTPUT_DIR}/output_${sample}.root"

                if [[ -f "$FILE" ]]; then
                    echo "[Remove] $FILE"
                    rm "$FILE"
                fi
            done

        else

            for file in \
                allData_combined.root \
                output_signal_M125_13TeV_cats_pythia8.root \
                output_bkg.root
            do
                FILE="${OUTPUT_DIR}/${file}"

                if [[ -f "$FILE" ]]; then
                    echo "[Remove] $FILE"
                    rm "$FILE"
                fi
            done

        fi

    done

    # Remove the combined data file only in default mode
    if ! $BKGS_ONLY; then

        FILE="${SPLIT_DIR}/allData_combined${SUFFIX}.root"

        if [[ -f "$FILE" ]]; then
            echo "[Remove] $FILE"
            rm "$FILE"
        fi

    fi

    echo "[Done] Previous split tuples removed."
    exit 0
fi

# -------------------------------------------------------
# Run splitting
# -------------------------------------------------------

if $BKGS_ONLY; then

    echo "---------------- Splitting background MC samples ----------------"

    for channel in ggH VBF; do

        echo "---------------- Processing ${channel} categories ----------------"

        for sample in DY EWK TT DiBoson; do

            echo "---------------- Splitting ${sample} in ${channel} ----------------"

            python3 scripts/split_tuples.py \
                "$sample" "$channel" $RECAT_ARG -v "$VARIANT"

        done

    done

else

    echo "---------------- Splitting on ggH tuples ----------------"

    for sample in signal data bkg; do

        echo "---------------- Splitting ${sample} in ggH ----------------"

        python3 scripts/split_tuples.py \
            "$sample" ggH $RECAT_ARG -v "$VARIANT"

    done

    echo "---------------- Splitting on VBF tuples ----------------"

    for sample in signal data bkg; do

        echo "---------------- Splitting ${sample} in VBF ----------------"

        python3 scripts/split_tuples.py \
            "$sample" VBF $RECAT_ARG -v "$VARIANT"

    done

    # -------------------------------------------------------
    # Hadd data
    # -------------------------------------------------------

    echo "---------------- Hadding the data files ----------------"

    hadd -f \
        "${SPLIT_DIR}/allData_combined${SUFFIX}.root" \
        "${SPLIT_DIR}/ggH${SUFFIX}/allData_combined.root" \
        "${SPLIT_DIR}/VBF${SUFFIX}/allData_combined.root"

fi

echo "---------------- Splitting completed ----------------"
