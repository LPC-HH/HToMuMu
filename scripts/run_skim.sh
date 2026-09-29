#!/bin/bash
# Orchestrates the skim stage: deletes previous skim outputs, then runs
# skim+hadd for each (mode, channel) pair in parallel as independent
# background pipelines (each channel's hadd only depends on that channel's
# own skim, not on the others), with per-job logs and tracked exit statuses.
#
# Usage: scripts/run_skim.sh (bdt|kin|both)

set -e

MODE=$1
if [[ "$MODE" != "bdt" && "$MODE" != "kin" && "$MODE" != "both" ]]; then
    echo "Usage: $0 (bdt|kin|both)"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

MODES_TO_RUN=()
[[ "$MODE" == "bdt" || "$MODE" == "both" ]] && MODES_TO_RUN+=("bdt")
[[ "$MODE" == "kin" || "$MODE" == "both" ]] && MODES_TO_RUN+=("kin")

CHANNELS=("ggH" "VBF")

dir_for() {
    local mode=$1 channel=$2
    if [[ "$mode" == "bdt" ]]; then
        echo "root_io/skim/${channel}reCat"
    else
        echo "root_io/skim/${channel}"
    fi
}

echo "---------------- Removing previous skim outputs ----------------"
for m in "${MODES_TO_RUN[@]}"; do
    for c in "${CHANNELS[@]}"; do
        d=$(dir_for "$m" "$c")
        mkdir -p "$d"
        echo "Cleaning $d"
        find "$d" -maxdepth 1 -type f -name "*.root" -delete
    done
done

LOGDIR="$REPO_ROOT/scripts/logs"
mkdir -p "$LOGDIR"
echo "Logs for this run: $LOGDIR"

run_pipeline() {
    local mode=$1 channel=$2 dir=$3 log=$4
    {
        echo "---------------- Skimming $channel ($mode) ----------------"
        python3 "scripts/run_skim_${channel}.py" "$mode"
        echo "---------------- Hadding $dir ----------------"
        (cd "$dir" && bash hadd_skim.sh)
    } > "$log" 2>&1
}

declare -A PIDS
RUNNING_PIDS=()
trap 'echo "Interrupted, killing running jobs..."; kill "${RUNNING_PIDS[@]}" 2>/dev/null; exit 1' INT TERM

for m in "${MODES_TO_RUN[@]}"; do
    for c in "${CHANNELS[@]}"; do
        d=$(dir_for "$m" "$c")
        key="$m/$c"
        log="$LOGDIR/${m}_${c}.log"
        run_pipeline "$m" "$c" "$d" "$log" &
        pid=$!
        PIDS["$key"]=$pid
        RUNNING_PIDS+=("$pid")
    done
done

FAILED=0
for key in "${!PIDS[@]}"; do
    pid=${PIDS[$key]}
    log="$LOGDIR/${key/\//_}.log"
    if wait "$pid"; then
        echo "[OK]   $key"
    else
        echo "[FAIL] $key -- log tail ($log):"
        tail -n 20 "$log"
        FAILED=1
    fi
done

echo "Full logs kept in: $LOGDIR"
exit $FAILED
