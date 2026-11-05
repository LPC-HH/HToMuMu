# Split the hadded BDT_score tuples into the per-category trees of the mass fits (scripts/split_tuples.py).
# Run from the HToMuMu directory:
#   bash scripts/run_splitting.sh [-r] [-d] [-v <variant label>]
#   -r  use the re-categorization BDT (BDT_score/<channel>reCat/)
#   -d  only delete the previous split tuples of this selection and exit
#   -v  train.py variant label of the BDT scores (VARIANT.label, e.g. asimovFit_flatMassRes; default base).
#       Reads BDT_score/<channel><dir suffix>/ where the dir suffix is the label without "_"
#       (asimovFit_flatMassRes -> asimovFitflatMassRes), and needs the cuts of
#       plot_BDT_Categories.py <channel> Combined --variant <label> for both channels.
#       Writes split_tuples/<channel><dir suffix>/ and split_tuples/allData_combined<dir suffix>.root.
RECAT_ARG=""
REMOVE_PREVIOUS=false
VARIANT="base"
while getopts "rdv:" opt; do
    case $opt in
        r)
            RECAT_ARG="-r"
            ;;
        d)
            REMOVE_PREVIOUS=true
            ;;
        v)
            VARIANT="$OPTARG"
            ;;
        *)
            echo "Usage: $0 [-r] [-d] [-v <variant label, e.g. asimovFit_flatMassRes>]"
            exit 1
            ;;
    esac
done

# same naming as split_tuples.py: reCat, then the variant's dir suffix ("" for base)
VARIANT_SUFFIX="${VARIANT//_/}"
[ "$VARIANT" = "base" ] && VARIANT_SUFFIX=""
SUFFIX="${RECAT_ARG:+reCat}${VARIANT_SUFFIX}"
SPLIT_DIR=./root_io/tuples/split_tuples

if $REMOVE_PREVIOUS; then
    find ${SPLIT_DIR}/ggH${SUFFIX}/ -type f -name "*.root"
    find ${SPLIT_DIR}/VBF${SUFFIX}/ -type f -name "*.root"
    ls ${SPLIT_DIR}/allData_combined${SUFFIX}.root

    find ${SPLIT_DIR}/ggH${SUFFIX}/ -type f -name "*.root" -delete
    find ${SPLIT_DIR}/VBF${SUFFIX}/ -type f -name "*.root" -delete
    rm ${SPLIT_DIR}/allData_combined${SUFFIX}.root
    exit 1
fi

echo "---------------- Splitting on ggH tuples (BDT variant ${VARIANT}) ---------------- "
python3 scripts/split_tuples.py signal ggH $RECAT_ARG -v "$VARIANT"
python3 scripts/split_tuples.py data ggH $RECAT_ARG -v "$VARIANT"

echo "---------------- Splitting on VBF tuples (BDT variant ${VARIANT}) ---------------- "
python3 scripts/split_tuples.py signal VBF $RECAT_ARG -v "$VARIANT"
python3 scripts/split_tuples.py data VBF $RECAT_ARG -v "$VARIANT"

echo "---------------- Hadding the data files  ---------------- "
hadd -f ${SPLIT_DIR}/allData_combined${SUFFIX}.root ${SPLIT_DIR}/ggH${SUFFIX}/allData_combined.root ${SPLIT_DIR}/VBF${SUFFIX}/allData_combined.root
