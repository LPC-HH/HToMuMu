#!/bin/bash
# Train the K-fold BDTs (train.py) for each channel in turn, stopping at the first failure.
#
# With no arguments this runs, in order:
#   python3 train.py VBF Combined --stage all --use-optuna --objective asimov_fit --weights flatMassRes
#   python3 train.py ggH Combined --stage all --use-optuna --objective asimov_fit --weights flatMassRes
# (plus --bkg-subset Full --sig-subset NottH, which are train.py's defaults anyway).
#
# Run it in the background with:
#   nohup bash run_train.sh [options] > training.log 2>&1 &

# ---------------------------------------------------------------------------
# Defaults: edit these to change what a plain `bash run_train.sh` does
# ---------------------------------------------------------------------------
STAGE="all"              # dev | test | final | apply | all | legacy | compare
USE_OPTUNA=true          # true -> --use-optuna
OBJECTIVE="asimov_fit"   # auc_w | asimov | asimov_fit
WEIGHTS="flatMassRes"    # massRes | flat | flatMassRes | "" (= train.py module flags)
CHANNELS=("VBF" "ggH")   # trained in this order
ERA="Combined"
USE_RECAT=false          # true -> --use-recategorization
declare -a bkg_subset=("Full")    # e.g. ("Full" "NoDY50")
declare -a sig_subset=("NottH")   # e.g. ("Full" "NottH" "VBF")
DRY_RUN=false
EXTRA_ARGS=()            # anything after `--` is passed to train.py verbatim

usage() {
    cat <<EOF
Usage: bash run_train.sh [options] [-- extra train.py args]

All options are optional; the defaults (top of this script) reproduce
  train.py <ch> ${ERA} --stage ${STAGE} --use-optuna --objective ${OBJECTIVE} --weights ${WEIGHTS}
for the channels: ${CHANNELS[*]}

  --stage S          dev|test|final|apply|all|legacy|compare      (default: ${STAGE})
  --use-optuna       pass --use-optuna                             (default: ${USE_OPTUNA})
  --no-optuna        do not pass --use-optuna
  --objective O      auc_w|asimov|asimov_fit                       (default: ${OBJECTIVE})
  --weights W        massRes|flat|flatMassRes, or "" for none      (default: ${WEIGHTS})
  --channels "A B"   space-separated channels, trained in order    (default: "${CHANNELS[*]}")
  --era E            (default: ${ERA})
  --recat            pass --use-recategorization
  --dry-run          print the commands without running them
  -h, --help         this message
  -- ARGS...         passed to every train.py call, e.g. -- --do-systematics --optuna-trials 50

Background run:  nohup bash run_train.sh [options] > training.log 2>&1 &
EOF
}

die() { echo "[ERROR] $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Optional overrides
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --stage)      [[ $# -ge 2 ]] || die "--stage needs a value"; STAGE="$2"; shift 2 ;;
        --use-optuna) USE_OPTUNA=true; shift ;;
        --no-optuna)  USE_OPTUNA=false; shift ;;
        --objective)  [[ $# -ge 2 ]] || die "--objective needs a value"; OBJECTIVE="$2"; shift 2 ;;
        --weights)    [[ $# -ge 2 ]] || die "--weights needs a value"; WEIGHTS="$2"; shift 2 ;;
        --channels)   [[ $# -ge 2 ]] || die "--channels needs a value"; read -r -a CHANNELS <<< "$2"; shift 2 ;;
        --era)        [[ $# -ge 2 ]] || die "--era needs a value"; ERA="$2"; shift 2 ;;
        --recat)      USE_RECAT=true; shift ;;
        --dry-run)    DRY_RUN=true; shift ;;
        -h|--help)    usage; exit 0 ;;
        --)           shift; EXTRA_ARGS=("$@"); break ;;
        *)            usage >&2; die "unknown argument '$1' (train.py options go after --)" ;;
    esac
done

# ---------------------------------------------------------------------------
# Validation (fail now rather than after hours of VBF training)
# ---------------------------------------------------------------------------
case "${STAGE}" in dev|test|final|apply|all|legacy|compare) ;; *) die "invalid --stage '${STAGE}'" ;; esac
case "${OBJECTIVE}" in auc_w|asimov|asimov_fit) ;; *) die "invalid --objective '${OBJECTIVE}'" ;; esac
case "${WEIGHTS}" in massRes|flat|flatMassRes|"") ;; *) die "invalid --weights '${WEIGHTS}'" ;; esac
[[ ${#CHANNELS[@]} -gt 0 ]] || die "no channels given"
for ch in "${CHANNELS[@]}"; do
    case "${ch}" in ggH|VBF) ;; *) die "invalid channel '${ch}' (ggH or VBF)" ;; esac
done
if [[ "${OBJECTIVE}" != "auc_w" ]]; then
    if [[ "${STAGE}" == "compare" || "${STAGE}" == "legacy" ]]; then
        die "--objective ${OBJECTIVE} applies to --stage dev/test/final/apply/all (use --objective auc_w)"
    fi
    if [[ "${STAGE}" != "dev" && "${USE_OPTUNA}" != true ]]; then
        die "--objective ${OBJECTIVE} selects its Asimov Optuna config: add --use-optuna"
    fi
fi
if [[ "${STAGE}" == "compare" && ( -n "${WEIGHTS}" || "${USE_OPTUNA}" == true ) ]]; then
    die "--stage compare runs every weight scheme and parameter set itself: use --weights \"\" --no-optuna"
fi

# ---------------------------------------------------------------------------
# Build the common train.py options
# ---------------------------------------------------------------------------
common=(--stage "${STAGE}")
[[ "${USE_OPTUNA}" == true ]] && common+=(--use-optuna)
common+=(--objective "${OBJECTIVE}")
[[ -n "${WEIGHTS}" ]] && common+=(--weights "${WEIGHTS}")
[[ "${USE_RECAT}" == true ]] && common+=(--use-recategorization)

cd "$(dirname "$0")" || die "cannot cd to the script directory"

echo "Channels: ${CHANNELS[*]} | era: ${ERA} | stage: ${STAGE} | optuna: ${USE_OPTUNA}"\
     "| objective: ${OBJECTIVE} | weights: ${WEIGHTS:-<module flags>} | recat: ${USE_RECAT}"
start_all=$(date +%s)

for ch in "${CHANNELS[@]}"; do
    for bs in "${bkg_subset[@]}"; do
        for ss in "${sig_subset[@]}"; do
            cmd=(python3 train.py "${ch}" "${ERA}" "${common[@]}" --bkg-subset "${bs}" --sig-subset "${ss}" "${EXTRA_ARGS[@]}")
            echo "[$(date '+%F %T')] ${cmd[*]}"
            [[ "${DRY_RUN}" == true ]] && continue
            start=$(date +%s)
            "${cmd[@]}" || die "${ch} (B ${bs}, S ${ss}) failed with exit code $?; stopping"
            echo "[$(date '+%F %T')] ${ch} (B ${bs}, S ${ss}) done in $(( ($(date +%s) - start) / 60 )) min"
        done
    done
done

[[ "${DRY_RUN}" == true ]] || echo "[$(date '+%F %T')] All done in $(( ($(date +%s) - start_all) / 60 )) min"
