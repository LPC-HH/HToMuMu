#!/bin/bash
#
# FSR validation (plot_fsr_validation.py) for 2024 on the v2.7.0 tuples on EOS.
#   ggH / VBF : hadded tuples (small)
#   Data      : 1 in DATA_EVERY per-job files over all 2024 runs (blinded to m < 110 GeV on load by the plotter);
#               the full Z-peak data does not fit in memory either. The data plots are shape comparisons.
#   DY        : 1 in DY_EVERY per-job files of every DY dataset (0J/1J/2J, 105-160, VBF-filtered, with extensions);
#               the full DY does not fit in memory. Every event keeps its full stitched weight, so the stitched mix is
#               kept; only the overall DY yield ("Events / bin" axes) is scaled down by ~1/DY_EVERY.
#
# Usage (from plot_macros/):  bash run_fsr_validation_2024.sh [DY_EVERY] [DATA_EVERY]      (defaults 30, 10)
# Output: ../plots/fsr_validation/2024/, log: fsr_validation_2024.log

DY_EVERY=${1:-30}
DATA_EVERY=${2:-10}
EOS_TUPLES="/eos/uscms/store/group/lpchmumu/${USER}/analyzer_HiggsMuMu_v2.7/tuples_v2.7.0"

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

DY_FILES=()
for dataset in "${EOS_TUPLES}"/DYto2Mu-2Jets_*Summer24*; do
    mapfile -t -O "${#DY_FILES[@]}" DY_FILES < <(ls "${dataset}"/*_tuples.root | awk -v n="${DY_EVERY}" 'NR % n == 1')
done
if [ ${#DY_FILES[@]} -eq 0 ]; then
    echo "[ERROR] No DY files found in ${EOS_TUPLES}"
    exit 1
fi
echo "DY: ${#DY_FILES[@]} files (1 in ${DY_EVERY} per dataset)"

# Sorted by run period (Muon0/1_2024C ... I), so every period is sampled
mapfile -t DATA_FILES < <(ls "${EOS_TUPLES}"/Muon*_2024*/*_tuples.root | awk -v n="${DATA_EVERY}" 'NR % n == 1')
if [ ${#DATA_FILES[@]} -eq 0 ]; then
    echo "[ERROR] No 2024 data files found in ${EOS_TUPLES}"
    exit 1
fi
echo "Data: ${#DATA_FILES[@]} files (1 in ${DATA_EVERY})"

nohup python3 plot_fsr_validation.py --era 2024 \
    --ggh "${EOS_TUPLES}/haddTuples/ggH_2024_tuples.root" \
    --vbf "${EOS_TUPLES}/haddTuples/VBF_2024_tuples.root" \
    --data "${DATA_FILES[@]}" \
    --dy "${DY_FILES[@]}" \
    > fsr_validation_2024.log 2>&1 &

echo "Started (PID $!), log: $(pwd)/fsr_validation_2024.log"
