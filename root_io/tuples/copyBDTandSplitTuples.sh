ANALYZER_VERSION="v1.5"
TUPLES_VERSION="v1.5.0"
inEOS_PATH="/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_$ANALYZER_VERSION/tuples_$TUPLES_VERSION/"

#echo eosmkdir ${inEOS_PATH}BDT_score/
#eosmkdir ${inEOS_PATH}BDT_score/

#echo eosmkdir ${inEOS_PATH}split_tuples/
#eosmkdir ${inEOS_PATH}split_tuples/

echo eos cp -r BDT_score/. root://cmseos.fnal.gov//${inEOS_PATH}
eos cp -r BDT_score/. root://cmseos.fnal.gov//${inEOS_PATH}

echo eos cp -r split_tuples/. root://cmseos.fnal.gov//${inEOS_PATH}
eos cp -r split_tuples/. root://cmseos.fnal.gov//${inEOS_PATH}