ANALYZER_VERSION="v2.2"
TUPLES_VERSION="v2.2.1"
inEOS_PATH="/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_$ANALYZER_VERSION/tuples_$TUPLES_VERSION/"

COPY_TO_EOS=false
while getopts "c" opt; do
    case $opt in
        c) COPY_TO_EOS=true ;;
    esac
done

############  2022Combined  ###########
hadd -f Data_2022Combined_tuples.root Data_2022_tuples.root Data_2022EE_tuples.root
hadd -f DY_2022Combined_tuples.root DY_2022_tuples.root DY_2022EE_tuples.root
hadd -f EWK_2022Combined_tuples.root EWK_2022_tuples.root EWK_2022EE_tuples.root
hadd -f TT_2022Combined_tuples.root TT_2022_tuples.root TT_2022EE_tuples.root
hadd -f DiBoson_2022Combined_tuples.root DiBoson_2022_tuples.root DiBoson_2022EE_tuples.root
hadd -f ggH_2022Combined_tuples.root ggH_2022_tuples.root ggH_2022EE_tuples.root
hadd -f VBF_2022Combined_tuples.root VBF_2022_tuples.root VBF_2022EE_tuples.root
hadd -f ttH_2022Combined_tuples.root ttH_2022_tuples.root ttH_2022EE_tuples.root

#####-f #######  2023Combined  ###########
hadd -f Data_2023Combined_tuples.root Data_2023_tuples.root Data_2023BPix_tuples.root

hadd -f DY_2023Combined_tuples.root DY_2023_tuples.root DY_2023BPix_tuples.root
hadd -f EWK_2023Combined_tuples.root EWK_2023_tuples.root EWK_2023BPix_tuples.root
hadd -f TT_2023Combined_tuples.root TT_2023_tuples.root TT_2023BPix_tuples.root
hadd -f DiBoson_2023Combined_tuples.root DiBoson_2023_tuples.root DiBoson_2023BPix_tuples.root

hadd -f ggH_2023Combined_tuples.root ggH_2023_tuples.root ggH_2023BPix_tuples.root
hadd -f VBF_2023Combined_tuples.root VBF_2023_tuples.root VBF_2023BPix_tuples.root
hadd -f ttH_2023Combined_tuples.root ttH_2023_tuples.root ttH_2023BPix_tuples.root

#####-f #######  Combined  ###########
hadd -f Data_Combined_tuples.root Data_2022Combined_tuples.root Data_2023Combined_tuples.root Data_2024_tuples.root Data_2025_tuples.root

hadd -f DiBoson_Combined_tuples.root DiBoson_2022_tuples.root DiBoson_2022EE_tuples.root DiBoson_2023_tuples.root DiBoson_2023BPix_tuples.root DiBoson_2024_tuples.root DiBoson_2025_tuples.root

hadd -f TT_Combined_tuples.root TT_2022_tuples.root TT_2022EE_tuples.root TT_2023_tuples.root TT_2023BPix_tuples.root TT_2024_tuples.root TT_2025_tuples.root

hadd -f DY_Combined_tuples.root DY_2022_tuples.root DY_2022EE_tuples.root DY_2023_tuples.root DY_2023BPix_tuples.root DY_2024_tuples.root DY_2025_tuples.root

hadd -f EWK_Combined_tuples.root EWK_2022_tuples.root EWK_2022EE_tuples.root EWK_2023_tuples.root EWK_2023BPix_tuples.root EWK_2024_tuples.root EWK_2025_tuples.root

hadd -f ggH_Combined_tuples.root ggH_2022_tuples.root ggH_2022EE_tuples.root ggH_2023_tuples.root ggH_2023BPix_tuples.root ggH_2024_tuples.root ggH_2025_tuples.root
hadd -f VBF_Combined_tuples.root VBF_2022_tuples.root VBF_2022EE_tuples.root VBF_2023_tuples.root VBF_2023BPix_tuples.root VBF_2024_tuples.root VBF_2025_tuples.root
hadd -f ttH_Combined_tuples.root ttH_2022_tuples.root ttH_2022EE_tuples.root ttH_2023_tuples.root ttH_2023BPix_tuples.root ttH_2024_tuples.root ttH_2025_tuples.root

if $COPY_TO_EOS; then
    echo eosmkdir ${inEOS_PATH}haddTuples/Combined/
    eosmkdir ${inEOS_PATH}haddTuples/Combined/
    echo eos cp *_Combined_*.root root://cmseos.fnal.gov//${inEOS_PATH}haddTuples/Combined/
    eos cp *_Combined_*.root root://cmseos.fnal.gov//${inEOS_PATH}haddTuples/Combined/
fi
