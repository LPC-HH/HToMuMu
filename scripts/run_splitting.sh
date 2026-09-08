RECAT_ARG=""
REMOVE_PREVIOUS=false
while getopts "rd" opt; do
    case $opt in
        r)
            RECAT_ARG="-r"
            ;;
        d)
            REMOVE_PREVIOUS=true
            ;;
        *)
            echo "Usage: $0 [-r] [-d]"
            exit 1
            ;;
    esac
done

if $REMOVE_PREVIOUS; then
    if [ -n "$RECAT_ARG" ]; then
        find ./root_io/tuples/split_tuples/ggHreCat/ -type f -name "*.root"
        find ./root_io/tuples/split_tuples/VBFreCat/ -type f -name "*.root"
        ls ./root_io/tuples/split_tuples/allData_combinedreCat.root

        find ./root_io/tuples/split_tuples/ggHreCat/ -type f -name "*.root" -delete
        find ./root_io/tuples/split_tuples/VBFreCat/ -type f -name "*.root" -delete
        rm ./root_io/tuples/split_tuples/allData_combinedreCat.root
    else 
        find ./root_io/tuples/split_tuples/ggH/ -type f -name "*.root"
        find ./root_io/tuples/split_tuples/VBF/ -type f -name "*.root"
        ls ./root_io/tuples/split_tuples/allData_combined.root
        
        find ./root_io/tuples/split_tuples/ggH/ -type f -name "*.root" -delete
        find ./root_io/tuples/split_tuples/VBF/ -type f -name "*.root" -delete
        rm ./root_io/tuples/split_tuples/allData_combined.root
    fi
    exit 1
fi

echo "---------------- Splitting on ggH tuples ---------------- "
python3 scripts/split_tuples.py signal ggH $RECAT_ARG
python3 scripts/split_tuples.py data ggH $RECAT_ARG

echo "---------------- Splitting on VBF tuples ---------------- "
python3 scripts/split_tuples.py signal VBF $RECAT_ARG
python3 scripts/split_tuples.py data VBF $RECAT_ARG

echo "---------------- Hadding the data files  ---------------- "
if [ -n "$RECAT_ARG" ]; then
    hadd -f  root_io/tuples/split_tuples/allData_combinedreCat.root root_io/tuples/split_tuples/ggHreCat/allData_combined.root root_io/tuples/split_tuples/VBFreCat/allData_combined.root
else
    hadd -f  root_io/tuples/split_tuples/allData_combined.root root_io/tuples/split_tuples/ggH/allData_combined.root root_io/tuples/split_tuples/VBF/allData_combined.root
fi
