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

## BDT Training
Look at python/xgboost/README.md

## Plotting 
All plotting codes are located at plot_macros/


## How to Run the Complete Analysis

This section describes the complete workflow, from producing the analyzer tuples to calculating the final systematic uncertainties.

### 1. Set the analysis version

Go to the `condor/` directory:

```bash
cd ./condor/
```

Edit:

```text
./condor/utils/version.py
```

and set the version name you want to use to tag your tuples.

---

### 2. Produce the analyzer tuples

From the `condor/` directory, run:

```bash
python3 create_analyzer_jobs_LPC.py
bash condor_job_sender.sh
```

This creates and submits the analyzer jobs. The resulting tuples will be stored in the EOS space defined by the configuration.

#### Optional: produce muon \(p_T\) systematic tuples

If you also want to produce the muon \(p_T\) systematic variations, run:

```bash
python3 create_analyzer_jobs_LPC_muonsys.py
bash condor_ctuple_job_sender_syst.sh
```

---

### 3. Check the analyzer jobs

Once the jobs have finished, check for failed or missing jobs with:

```bash
bash analyzer_job_checker_rerun.sh version
```

Replace `"version"` with the analysis version you are using. For example:

```bash
bash analyzer_job_checker_rerun.sh 2.2
```

The script will check the submitted jobs and rerun the ones that failed.

---

### 4. Compute the sum of generated weights

To produce the histograms containing the sum of generated weights, go to the `scripts/` directory:

```bash
cd ../scripts/
```

Run:

```bash
python3 ComputeWeights.py
python3 ComputeWeights_muon_sys.py
```

`ComputeWeights.py` computes the nominal generated-weight information, while `ComputeWeights_muon_sys.py` does the same for the muon systematic samples.

---

### 5. Produce the tuples

Return to the `condor/` directory:

```bash
cd ../condor/
```

Create and submit the nominal ctuple jobs:

```bash
python3 create_ctuples_jobs_LPC.py
bash condor_ctuple_job_sender.sh
```

#### Optional: produce muon and jet \(p_T\) systematic ctuples

To produce the ctuples for the muon and jet \(p_T\) systematic variations, run:

```bash
python3 create_ctuples_jobs_LPC_syst.py
bash condor_ctuple_job_sender_syst.sh
```

---

### 6. Check the tuple jobs

After the jobs have finished, check for failed jobs with:

```bash
bash ctuple_job_checker_rerun.sh version
```

For example:

```bash
bash ctuple_job_checker_rerun.sh 2.2.2
```

---

### 7. Merge (`hadd`) the nominal tuples

Go to the tuple directory:

```bash
cd ../root_io/tuples/
```

Run:

```bash
bash hadd_tuples_EOS.sh -eos
bash hadd_tuples
```

This merges the nominal tuples required for the analysis.

---

### 8. Merge the systematic tuples

To merge the systematic tuples using Condor jobs, return to the `condor/` directory:

```bash
cd ../../condor/
```

Then run:

```bash
bash submit_hadd_systematics.sh
```

---

### 9. Add the BDT scores to the systematic tuples

Go to the XGBoost directory:

```bash
cd ../python/xgboost/
```

Submit the jobs that add the BDT scores to the systematic tuples:

```bash
bash submit_bdt_systematics.sh
```

---

### 10. Calculate the systematic uncertainties

Finally, return to the initial project directory and run:

```bash
bash ./scripts/calculate_all_systematics.sh
```
c
This calculates the systematic uncertainties from the nominal and systematic tuples.

---

### Workflow summary

The complete workflow is:

```text
Set version
    ↓
Produce analyzer tuples
    ↓
Check analyzer jobs
    ↓
Compute generated-weight histograms
    ↓
Produce ctuples
    ↓
Check ctuple jobs
    ↓
Hadd nominal tuples
    ↓
Hadd systematic tuples
    ↓
Add BDT scores to systematic tuples
    ↓
Calculate systematic uncertainties
```

The muon and jet systematic steps are optional if only the nominal analysis is needed.
