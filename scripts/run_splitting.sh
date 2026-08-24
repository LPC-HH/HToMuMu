echo "---------------- Splitting on ggH tuples ---------------- "
python3 scripts/split_tuples.py signal ggH
python3 scripts/split_tuples.py data ggH

echo "---------------- Splitting on VBF tuples ---------------- "
python3 scripts/split_tuples.py signal VBF
python3 scripts/split_tuples.py data VBF

echo "---------------- Hadding the data files  ---------------- "
hadd -f  root_io/tuples/split_tuples/allData_combined.root root_io/tuples/split_tuples/ggH/allData_combined.root root_io/tuples/split_tuples/VBF/allData_combined.root
