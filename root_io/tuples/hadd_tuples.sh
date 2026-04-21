ANALYZER_VERSION="v1.5"
TUPLES_VERSION="v1.5.0"
inEOS_PATH="/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_$ANALYZER_VERSION/tuples_$TUPLES_VERSION/"

############  2022Combined  ###########
hadd Data_2022Combined_tuples.root Data_2022_tuples.root Data_2022EE_tuples.root
hadd DY_2022Combined_tuples.root DY_2022_tuples.root DY_2022EE_tuples.root
hadd EWK_2022Combined_tuples.root EWK_2022_tuples.root EWK_2022EE_tuples.root
hadd TT_2022Combined_tuples.root TT_2022_tuples.root TT_2022EE_tuples.root
hadd DiBoson_2022Combined_tuples.root DiBoson_2022_tuples.root DiBoson_2022EE_tuples.root
hadd ggH_2022Combined_tuples.root ggH_2022_tuples.root ggH_2022EE_tuples.root
hadd VBF_2022Combined_tuples.root VBF_2022_tuples.root VBF_2022EE_tuples.root
hadd ttH_2022Combined_tuples.root ttH_2022_tuples.root ttH_2022EE_tuples.root

############  2023Combined  ###########
hadd Data_2023Combined_tuples.root Data_2023_tuples.root Data_2023BPix_tuples.root

hadd DY_2023Combined_tuples.root DY_2023_tuples.root DY_2023BPix_tuples.root
hadd EWK_2023Combined_tuples.root EWK_2023_tuples.root EWK_2023BPix_tuples.root
hadd TT_2023Combined_tuples.root TT_2023_tuples.root TT_2023BPix_tuples.root
hadd DiBoson_2023Combined_tuples.root DiBoson_2023_tuples.root DiBoson_2023BPix_tuples.root

hadd ggH_2023Combined_tuples.root ggH_2023_tuples.root ggH_2023BPix_tuples.root
hadd VBF_2023Combined_tuples.root VBF_2023_tuples.root VBF_2023BPix_tuples.root
hadd ttH_2023Combined_tuples.root ttH_2023_tuples.root ttH_2023BPix_tuples.root

############  Combined  ###########
hadd Data_Combined_tuples.root Data_2022Combined_tuples.root Data_2023Combined_tuples.root Data_2024_tuples.root Data_2025_tuples.root

hadd DiBoson_Combined_tuples.root DiBoson_2022_tuples.root DiBoson_2022EE_tuples.root DiBoson_2023_tuples.root DiBoson_2023BPix_tuples.root DiBoson_2024_tuples.root

hadd TT_Combined_tuples.root TT_2022_tuples.root TT_2022EE_tuples.root TT_2023_tuples.root TT_2023BPix_tuples.root TT_2024_tuples.root

hadd DY_Combined_tuples.root DY_2022_tuples.root DY_2022EE_tuples.root DY_2023_tuples.root DY_2023BPix_tuples.root DY_2024_tuples.root

hadd EWK_Combined_tuples.root EWK_2022_tuples.root EWK_2022EE_tuples.root EWK_2023_tuples.root EWK_2023BPix_tuples.root EWK_2024_tuples.root

hadd ggH_Combined_tuples.root ggH_2022_tuples.root ggH_2022EE_tuples.root ggH_2023_tuples.root ggH_2023BPix_tuples.root ggH_2024_tuples.root
hadd VBF_Combined_tuples.root VBF_2022_tuples.root VBF_2022EE_tuples.root VBF_2023_tuples.root VBF_2023BPix_tuples.root VBF_2024_tuples.root
hadd ttH_Combined_tuples.root ttH_2022_tuples.root ttH_2022EE_tuples.root ttH_2023_tuples.root ttH_2023BPix_tuples.root ttH_2024_tuples.root

echo eosmkdir ${inEOS_PATH}haddTuples/Combined/
eosmkdir ${inEOS_PATH}haddTuples/Combined/
echo eos cp *_Combined_*.root root://cmseos.fnal.gov//${inEOS_PATH}haddTuples/Combined/
eos cp *_Combined_*.root root://cmseos.fnal.gov//${inEOS_PATH}haddTuples/Combined/