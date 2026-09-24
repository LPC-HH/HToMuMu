This code is based in the Run2 Analysis https://github.com/irenedutta23/HmmAna

## Setup

```
cmsrel CMSSW_15_0_19
cd CMSSW_15_0_19/src
cmsenv
git clone git@github.com:LPC-HH/HToMuMu.git
scram b clean
scram b -j 8
cd HToMuMu
make -j4
```

## For jobs and dataset creation
You need to have a CMS GRID certificate established
```
voms-proxy-init -voms cms
```

## Run the analyzer 
The format for running the analyzer is
```
./bin/HmmAnalyzer runList.txt(or .list) out.root mc/data is_data year_num if_include_Z_region if_include_H_region
```
For simulations
```
./bin/HmmAnalyzer runList.txt out.root mc F 2024 F T
```

For data
```
./bin/HmmAnalyzer runList.txt out.root data T 2024 F T
```

To run over all the data sets look at condor/README.md to run it in condor jobs

## Run CreateTuples

This will create a root file with tuples with all the usefull variables and the correspodeting weights;

For data/simulation
```
./bin/CreateTuple analyzer_output.root output_directory era dataset T(data)/F(simulation) T(signal)/F(Bkg-data)
```


To run over all the data sets look at condor/README.md to run it in condor jobs.   
If you want to run it over a small dataset look at scripts/README.md

## Using Condor jobs
Analyzer and tuplizer should be run over all datasets using condor jobs. To do this, look at the README in condor/

## Hadd Tuplizer output
After you have the tuples, you need them locally to plot from and run the BDT on.

```
cd ./root_io/tuples/
bash hadd_tuples_EOS.sh
bash hadd_tuples.sh
```

The second hadd creates combined era tuple files

## Skim tuples 

BDT does not like big files, so we need to generate a tuples that contain just the events from that production mode and the training variables.
To this use src/SkimTuples_VBF.cc  src/SkimTuplesggH.cc and the scripts ./scripts/run_skim_ggH.py ./scripts/run_skim_VBF.py
You can change the datasets by changing the lists `eras`, `background_datasets`, and `signal_datasets` in the script.

Run
```
python3 ./scripts/run_skim_ggH.py
python3 ./scripts/run_skim_VBF.py
```

Once we have the skim tuples, you must hadd to have one background tuple and one signal sample, you can just do

```
cd ./root_io/skim/(ggH/VBF)
bash hadd_skim.sh
```

You can also run the skimming, hadd, and removal of previous tuples at once with:
```bash
bash scripts/run_skim.sh (bdt/kin/both)
```
This logs the scripts for the skimming and hadd in scripts/logs/

## BDT Training
Look at python/xgboost/README.md

## Plotting 
All plotting codes are located at plot_macros/
