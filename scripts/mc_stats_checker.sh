
#!/bin/bash

BASE="RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2"

datasets=(
  "/EWK-2L2J_Bin-MLL-50-MJJ-120_TuneCH3_13p6TeV_madgraph-herwig7/${BASE}-v2/NANOAODSIM"
  "/EWK-2L2J_Bin-MLL-50-MJJ-120_TuneCH3_13p6TeV_madgraph-herwig7/${BASE}_ext1-v2/NANOAODSIM"
  "/EWK-2Mu2J_Bin-MLL-105to160_TuneCH3_13p6TeV_madgraph-herwig7/${BASE}-v2/NANOAODSIM"
  "/EWK-2Mu2J_Bin-MLL-105to160_TuneCH3_13p6TeV_madgraph-herwig7/${BASE}_ext1-v2/NANOAODSIM"
  "/EWK-2Mu2J_Bin-M2Mu-105to160-M2J-120_TuneCP5_13p6TeV_madgraph-pythia8/${BASE}-v2/NANOAODSIM"
  "/EWK-2Mu2J_Bin-M2Mu-105to160-M2J-120_TuneCP5_13p6TeV_madgraph-pythia8/${BASE}_ext1-v2/NANOAODSIM"
)

labels=(
  "EWK-2L2J"
  "EWK-2L2J ext1"
  "EWK-2Mu2J"
  "EWK-2Mu2J ext1"
  "EWK-2Mu2J_pythia"
  "EWK-2Mu2J_pythia ext1"
)

printf "%-22s %18s %12s\n" "Dataset" "Valid events" "Files"
printf '%s\n' "--------------------------------------------------------"

for i in "${!datasets[@]}"; do
    dataset="${datasets[$i]}"
    #echo $dataset
    nevents=$(dasgoclient -query="file dataset=${dataset} | sum(file.nevents)" 2>/dev/null)
    nfiles=$(dasgoclient -query="file dataset=${dataset} | count(file.name)" 2>/dev/null)

    printf "%-22s %18s %12s\n" \
        "${labels[$i]}" "$nevents" "$nfiles"
done

