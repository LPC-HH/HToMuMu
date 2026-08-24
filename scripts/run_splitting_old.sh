echo "---------------- Splitting on ggH tuples ---------------- "
python3 scripts/split_tuples_original.py signal ggH
python3 scripts/split_tuples_original.py data ggH

echo "---------------- Splitting on VBF tuples ---------------- "
python3 scripts/split_tuples_original.py signal VBF
python3 scripts/split_tuples_original.py data VBF
