#!/bin/bash
# Usage: bash skim_tuplizer_files.sh
# Skims each <dataset>_CombinedTuples.root to <dataset>_skim.root in the same directory.

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skim_script="$dir/../skim_tree.py"

for path in data/Muon0_2024H/Muon0_2024H data/Muon1_2024H/Muon1_2024H signal/ggH/ggH signal/VBF/VBF; do
    input="$dir/${path}_CombinedTuples.root"
    output="$dir/${path}_skim.root"
    if [[ ! -s "$input" ]]; then
        echo "Missing $input, skipping"
        continue
    fi
    echo "Skimming $input -> $output"
    python3 "$skim_script" "$input" "$output" --tuples --tree tree_output || echo "FAILED: $input"
done
