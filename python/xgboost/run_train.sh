#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "Use Channel Under Study and ifReCat as arguments only!"
    exit
fi
HIGGS_CHANNEL=$1
useRecategorization=$2

## declare an array variable
declare -a bkg_subset=("Full")
#declare -a bkg_subset=("Full" "NoDY50")
# declare -a sig_subset=("Full" "NottH" "VBF")
declare -a sig_subset=("NottH")
#declare -a sig_subset=(${HIGGS_CHANNEL})
#declare -a eras=("2022Combined" "2023Combined" "2024" "2025")
declare -a eras=("Combined")
#declare -a eras=("2024")

#declare -a tuples=("Data" "DY" "DY120to200" "EWK" "TT" "Top" "DiBoson" "TriBoson" "ggH" "VBF" "ttH" "VH")

#standard
declare -a tuples=("Data" "DY" "EWK" "TT" "DiBoson" "ggH" "VBF")

#declare -a tuples=("ggH" "VBF")

recat_flag=""
if [[ "${useRecategorization}" == "T" ]]; then
    recat_flag="--use-recategorization"
fi

echo "Higgs Channel: ${HIGGS_CHANNEL}"
echo "Eras: ${eras}"
echo "Use BDT ReCat? ${useRecategorization}"

# now loop through the above array
for bs in "${bkg_subset[@]}"; do
    for ss in "${sig_subset[@]}"; do
        echo "--------- B ${bs} - S ${ss} ---------"
        for era in "${eras[@]}"; do
            echo "python3 train.py ${HIGGS_CHANNEL} ${era} ${recat_flag} --bkg-subset ${bs} --sig-subset ${ss}"
            python3 train.py ${HIGGS_CHANNEL} ${era} ${recat_flag} --bkg-subset ${bs} --sig-subset ${ss}

            #for type in "signal" "background" "data"; do
                #echo "         --- ${era} Skim ${type} ---"
                #python3 append_xgboost_discriminator_to_tree.py ${HIGGS_CHANNEL} ${era} Combined ${type} ${bs} ${ss} --skim
            #done

            # Add BDT to tuples
            #for type in "${tuples[@]}"; do
            #    echo "--- ${era} Tuples ${type} ---"
            #   	python3 append_xgboost_discriminator_to_tree.py ${HIGGS_CHANNEL} ${era} Combined ${type} ${bs} ${ss}
            #done
        done
    done
done
