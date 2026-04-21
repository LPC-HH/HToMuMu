ANALYZER_VERSION="v1.5"
TUPLES_VERSION="v1.5.0"
EOS_PATH="/eos/uscms/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_$ANALYZER_VERSION/tuples_$TUPLES_VERSION/"
inEOS_PATH="/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_$ANALYZER_VERSION/tuples_$TUPLES_VERSION/"

##############  2022  ##############
hadd -f Data_2022_tuples.root ${EOS_PATH}Muon_2022{C..D}/*.root ${EOS_PATH}SingleMuon_2022C/*.root

hadd -f DY_2022_tuples.root ${EOS_PATH}DY50to120_Summer22/*.root ${EOS_PATH}DY120to200_Summer22/*.root
hadd -f EWK_2022_tuples.root ${EOS_PATH}EWK_2L2J_Summer22/*.root
hadd -f TT_2022_tuples.root ${EOS_PATH}TTto2L2Nu_Summer22/*.root ${EOS_PATH}TTtoLNu2Q_Summer22/*.root
hadd -f DiBoson_2022_tuples.root ${EOS_PATH}WZto2L2Q_*22/*.root ${EOS_PATH}WZto3LNu_*22/*.root ${EOS_PATH}ZZto2L2Nu_*22/*.root ${EOS_PATH}ZZto2L2Q_*22/*.root ${EOS_PATH}ZZto4L_*22/*.root ${EOS_PATH}WWto2L2Nu_*22/*.root

hadd -f ggH_2022_tuples.root ${EOS_PATH}ggH_*22/*.root
hadd -f VBF_2022_tuples.root ${EOS_PATH}VBF_*22/*.root
hadd -f ttH_2022_tuples.root ${EOS_PATH}ttH_*22/*.root

###############  2022EE  ##############

hadd -f Data_2022EE_tuples.root ${EOS_PATH}Muon*_2022{E..G}/*.root

hadd -f DY_2022EE_tuples.root ${EOS_PATH}DY50to120_Summer22EE/*.root ${EOS_PATH}DY120to200_Summer22EE/*.root
hadd -f EWK_2022EE_tuples.root ${EOS_PATH}EWK_2L2J_Summer22EE/*.root
hadd -f TT_2022EE_tuples.root ${EOS_PATH}TTto2L2Nu_Summer22EE/*.root ${EOS_PATH}TTtoLNu2Q_Summer22EE/*.root
hadd -f DiBoson_2022EE_tuples.root ${EOS_PATH}WZto2L2Q_*22EE/*.root ${EOS_PATH}WZto3LNu_*22EE/*.root ${EOS_PATH}ZZto2L2Nu_*22EE/*.root ${EOS_PATH}ZZto2L2Q_*22EE/*.root ${EOS_PATH}ZZto4L_*22EE/*.root ${EOS_PATH}WWto2L2Nu_*22EE/*.root

hadd -f ggH_2022EE_tuples.root ${EOS_PATH}ggH_*22EE/*.root
hadd -f VBF_2022EE_tuples.root ${EOS_PATH}VBF_*22EE/*.root
hadd -f ttH_2022EE_tuples.root ${EOS_PATH}ttH_*22EE/*.root

###############  2023  ##############
hadd -f Data_2023_tuples.root ${EOS_PATH}Muon*_2023C*/*.root

hadd -f DY_2023_tuples.root ${EOS_PATH}DY50to120_Summer23/*.root ${EOS_PATH}DY120to200_Summer23/*.root
hadd -f EWK_2023_tuples.root ${EOS_PATH}EWK_2L2J_Summer23/*.root
hadd -f TT_2023_tuples.root ${EOS_PATH}TTto2L2Nu_Summer23/*.root ${EOS_PATH}TTtoLNu2Q_Summer23/*.root
hadd -f DiBoson_2023_tuples.root ${EOS_PATH}WZto2L2Q_*23/*.root ${EOS_PATH}WZto3LNu_*23/*.root ${EOS_PATH}ZZto2L2Nu_*23/*.root ${EOS_PATH}ZZto2L2Q_*23/*.root ${EOS_PATH}ZZto4L_*23/*.root ${EOS_PATH}WWto2L2Nu_*23/*.root

hadd -f ggH_2023_tuples.root ${EOS_PATH}ggH_*23/*.root
hadd -f VBF_2023_tuples.root ${EOS_PATH}VBF_*23/*.root
hadd -f ttH_2023_tuples.root ${EOS_PATH}ttH_*23/*.root

###############  2023BPix  ##############

hadd -f Data_2023BPix_tuples.root ${EOS_PATH}Muon*_2023D*/*.root

hadd -f DY_2023BPix_tuples.root ${EOS_PATH}DY50to120_Summer23BPix/*.root ${EOS_PATH}DY120to200_Summer23BPix/*.root
hadd -f EWK_2023BPix_tuples.root ${EOS_PATH}EWK_2L2J_Summer23BPix/*.root
hadd -f TT_2023BPix_tuples.root ${EOS_PATH}TTto2L2Nu_Summer23BPix/*.root ${EOS_PATH}TTtoLNu2Q_Summer23BPix/*.root
hadd -f DiBoson_2023BPix_tuples.root ${EOS_PATH}WZto2L2Q_*23BPix/*.root ${EOS_PATH}WZto3LNu_*23BPix/*.root ${EOS_PATH}ZZto2L2Nu_*23BPix/*.root ${EOS_PATH}ZZto2L2Q_*23BPix/*.root ${EOS_PATH}ZZto4L_*23BPix/*.root ${EOS_PATH}WWto2L2Nu_*23BPix/*.root

hadd -f ggH_2023BPix_tuples.root ${EOS_PATH}ggH_*23BPix/*.root
hadd -f VBF_2023BPix_tuples.root ${EOS_PATH}VBF_*23BPix/*.root
hadd -f ttH_2023BPix_tuples.root ${EOS_PATH}ttH_*23BPix/*.root


##############  2024  ##############

hadd -f Data_2024_tuples.root ${EOS_PATH}Muon*_2024*/*.root

hadd -f DY_2024_tuples.root ${EOS_PATH}DY50to120_Summer24/*.root ${EOS_PATH}DY120to200_Summer24/*.root
hadd -f EWK_2024_tuples.root ${EOS_PATH}EWK_2L2J_Summer24/*.root
hadd -f TT_2024_tuples.root ${EOS_PATH}TTto2L2Nu_Summer24/*.root ${EOS_PATH}TTtoLNu2Q_Summer24/*.root
hadd -f DiBoson_2024_tuples.root ${EOS_PATH}WZto2L2Q_*24/*.root ${EOS_PATH}WZto3LNu_*24/*.root ${EOS_PATH}ZZto2L2Nu_*24/*.root ${EOS_PATH}ZZto2L2Q_*24/*.root ${EOS_PATH}ZZto4L_*24/*.root ${EOS_PATH}WWto2L2Nu_*24/*.root

hadd -f ggH_2024_tuples.root ${EOS_PATH}ggH_*24/*.root
hadd -f VBF_2024_tuples.root ${EOS_PATH}VBF_*24/*.root
hadd -f ttH_2024_tuples.root ${EOS_PATH}ttH_*24/*.root

##############  2025  ##############

hadd -f Data_2025_tuples.root ${EOS_PATH}Muon*_2025*/*.root


###Copy back to LPC
echo ${inEOS_PATH}
echo eosmkdir ${inEOS_PATH}haddTuples/
eosmkdir ${inEOS_PATH}haddTuples/
echo eos cp *.root root://cmseos.fnal.gov//${inEOS_PATH}haddTuples/
eos cp *.root root://cmseos.fnal.gov//${inEOS_PATH}haddTuples/
