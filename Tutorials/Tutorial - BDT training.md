### Statement
This instruction is from Matias, based on HtoMuMu github branch - main, Yuyang updates it.
# Code Review

This aims to show the complete code workflow in detail. 

In red are some comments on things that should be added or improved in the code, but I haven't had the time to do it.

In orange are some comments on things that I think(Matias) should be good to do, but are not necessary or important.

The main goal is to show how to go from the NanoAOD tuples to the mass fits to obtain the significance and asymptotic limits.



### Analyser tuples 
In /HtoMuMu:

This is the first step. The code takes the NanoAOD tuples and saves the events that pass the selection in the analyser tuples.
The selections are:
- Requieres two opposite charge muons with pt > 20GeV, abs(eta) < 2.4 and pass the medium identidication and loose isolation.
- One of the muons must have pt > 26 and match a HLT trigger muon.

For the Jets, the requirements are:

- pt > 25 GeV.
- abd(eta) < 4.7 
- Pass loose isolation.

This code also checks if some of the jets are B-tagged based on the Particle net selection shown here: [wiki](https://btv-wiki.docs.cern.ch/ScaleFactors/Run3Summer24/#ak4-b-tagging)

To execute the code, you can :

For simulations

```
./bin/HmmAnalyzer runList.txt out.root mc F 2016
```

For data
```
./bin/HmmAnalyzer runList.txt out.root data T 2016
```

To run over all the data sets, look at condor/README.md to run it in condor jobs

By default, these tuples are saved in:
```
/eos/uscms/store/user/lpchmumu/$(USER)/analyzer_HiggsMuMu/(Data/MC_background/MC_signal)
```

### Hadd Analyzer tuples
In order to obtain the weights, it is necessary to hadd the analyzer tuples to calculate the Sum of the generated weights.

Check condor/README.md to see how to hadd all the datasets. You can do that in the terminal using the hadd command, but it is recommended to use the script because it will check if some job failed before hadd the files.  

By default, the hadded tuple is saved 
### Create tuples

This code takes the analyzer tuples and generates a new set of tuples, one for each dataset. 

These tuples save just the variables that are being used now in the analysis, and also calculate variables that were not in the analyzer tuple as:

- weight: Event weight defined as (gen_weight x lumi x XS x pu_weight)/Sum_gen_weights.
- is_(ggH/VBF)_category: This variable is equal to 1 if the events pass the ggH/VBF selections.

Run the code for data/simulation :
```
./bin/CreateTuple analyzer_output.root output_directory era dataset T(data)/F(simulation) T(signal)/F(Bkg-data)
```

To run over all the data sets, look at condor/README.md to run it in condor jobs.   
If you want to run it over a small dataset, look at scripts/README.md
<span style="color:red"> My username(mbarrial) is hardcoded here, so this needs to be updated.

By default, these tuples are saved in:
```
/eos/uscms/store/user/lpchmumu/$(USER)/analyzer_HiggsMuMu/tuples/
```

After you have the tuples, you need to have the sample. For example, you need to hadd all the 2022 Data samples in just one file or all the diBoson backgrounds in just one file. To do that, run

```
cd ./root_io/tuples/
bash hadd_tuples_EOS.sh
bash hadd_tuples.sh
```

<span style="color:Orange"> Probably will be good to have just one hadd script and also clean this one a little.

If you want to add a variable to the tuples, you just need to go to ./lib/CreateTuple.h add the variable to the CreateTuple class, and to the CreateTuple::setBranchesAddressesInput() method.

# Plotting 

## BDT Training 

For the training, you will need a VPN to Fermilab, do that first because it can take some time. See how to do it in ./python/xgboost/README.md

You need to have the tuples before continuing with this.
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

Once you have this, you can run the BDT training, look at ./python/xboost/README.md to see how to do it.

The key variables of this code are in ./python/xgboost/train.py are. 

- DRAW_CORRELATIONS: if True generate a 2D map with the variables correations. (It takes time, so False for default).
- DO_STANDARDIZATION: if True standardize the variables (subtract the mean and divide by the standard deviation).
- USE_WEIGHT: if True add a weight the samples (gen_w * pu_weight * XS * lumi)/ SumGenWeights.
- USE_WEIGHT_MASS_RES: if true, add the mass resolution to the regular weight. <span style="color:red"> Just one of the use_weight variable as true.
- APPEND_VARIABLES: if true, create new tuples with the BDT score saved on them.
- USE_BSCONSTRAIN: if true, use the bsConstrain variables for the training

<span style="color:orange"> Probably will be good to add this as inputs so you can run python3 train.py ggh Combined weight standardization bsConstrain, or something like that 


#### Using calibrated mass resolution in training
If you want to use calibrated dimuon mass resolution as weight or variable in BDT training, then go to HToMuMu/python/xgboost/xgb_utils.py, and find the last 3 variables in **get_variables()**. They should be
*  "diMuon_bsConstrainedMass", "relative_diMuon_bsConstrainedMass_error", "weight" 

You can change "relative_diMuon_bsConstrainedMass_error" to "calibrated_diMuon_bsConstrainedMass_error". 

If you use **USE_WEIGHT_MASS_RES=True**, then the training weight will be *weight/mass_resolution*. If you want to use it as a variable, then set **USE_WEIGHT=True** and add it to previous variables collection.

## After training

The training ```run_train.sh {category}``` code will generate one file containing the model (python/xgboost/models/model_ggH_Combined_BFull_SNottH.xgb), one file containing the roc curve (python/xgboost/roc/ggH_Combined_BFull_SNottH_roc.txt), and will add the BDT score to the tuples.
The tuples with the BDT score added are saved in root_io/tuples/BDT_score/(ggH/VBF)/BFull_SNottH/ 


Again, we need to hadd these tuples. To do this, do 

```
bash scripts/hadd_bdt.sh (ggH/VBF)
```

This will copy the hadd_template.sh file in the directories where the tuples are, so the next time you can just do.

```
cd root_io/tuples/BDT_score/(ggH/VBF)/BFull_SNottH/
bash hadd.sh
```
## Find Categories
Once we have this, we can find the categories. The categories are selected by scanning the cut x < BDT_score < 1 and finding which value maximizes S/sqrt(B) (Signal events divided by the square root of the background events). After this, we repeat the process but looking at x < BDT_score < cat1. This process is done 2 times for ggH and 3 times for VBF. 
<span style="color:Orange"> The number of iterations was chosen by eye, so it could be good to find a most rigorous way to do it.

Run3

```
cd plot_macros
python3 plot_BDT_Categories.py (ggH/VBF) Combined
```

This will generate a plot showing the BDT output and the categories (plots/(ggH/VBF)_category/BDT_categories/BDT_output_Combined_BFull_SNottH.pdf), plots showing the BDT scan (/plots/ggH_category/BDT_categories/cuts), and also will print the categories, like this.

Categories:  [0.0, 0.19184615384615372, 0.44615384615384546, 1.0]

Once you have this list, it is automatically saved to a json file in root_io and read by the tuple splitting code and plot_sim_vs_data

Inside the code, there is a variable called use_bsConstrain. If you train the BDT model using bsConstrain variable, set it to True, if you don't want to use bsConstrain variables set it to False. <span style="color:Orange"> Would be nice to add this as an input parameter.


# Mass fits

Mass fits code based on this code  [Tutorial](https://gitlab.cern.ch/jspah/higgsdna_finalfits_tutorial_24/-/tree/master/07_FinalFits?ref_type=heads)

I just changed a few things to make the code work for Hmumu(Br, xS, Lumi, etc), but the variables are still called `mass_hgg` or things like that.

## Tuples
The code requires a specific format for the tuples. To generate the necessary tuples run (be you that you complete the previous steps):

```
python3 scripts/split_tuples.py signal (ggH/VBF)
python3 scripts/split_tuples.py data (ggH/VBF)
```
Inside the code, there is a variable called use_bsConstrain. If you train the BDT model using bsConstrain variable, set it to True, if you don't want to use bsConstrain variables set it to False. <span style="color:Orange"> Would be nice to add this as an input parameter.

You can now run this together with

```
bash scripts/run_splitting.sh
```

## Copy over to eos
After the tuples have been split, you can copy over the BDT score tuples as well as the split tuples onto the EOS space to save them. There is a bash script for this, but you need to change the analyzer/tuplizer version in it.

```
cd root_io/tuples/
bash copyBDTandSplitTuples.sh
```

## Mass fits code

Once you have the tuples set up, the [mass_fit_repo](https://github.com/MatBarria/flashggFinalFit) using the commands that are in the README

<span style="color:red"> The code is now in my personal git account, you can move it to the organization if you want. However, if you want to change the name of the repo you will have to modify the code because the repo name is hardcoded in some file.

## Fits 
##### If you want to combine run2 and run3 datacards, then you should go to CMSSW_11_3_4, where run2 datacards can be processed properly. I have copied the following section to "Significance_combine.md".
Once you have cloned the code (don't forget to run source setup.sh each time you close your lpc session), you can execute all the mass fits just by running the script. 
<span style="color:red"> IMPORTANT: My paths are still hardcoded here, this must be changed!. For now, update manually the paths in the following files(changes what is before/HToMuMu/)

- ./run_fits.sh : 4 paths, lines 11, 18, 24, 30.
- ./Signal/config_tutorial_combined.py : line 9
- ./Signal/config_tutorial_combined_VBF.py : line 9
- ./Background/config_tutorial.py : line 7
- ./Background/config_tutorial_VBF.py : line 7
- ./Datacard/generate_datacards.sh : line 74, 92

```
bash run_fits.sh 
```

This will generate all the necessary fits and will save them in `flashggFinalFit/Signal/outdir_packaged`, `pflashggFinalFit/Background/outdir_tutorial`, and `flashggFinalFit/Plots/plots_tutorial`. 
Also, will create Datacards in this path: `flashggFinalFit/Datacard`

To understand what the scripts do, please read the whole [Tutorial](https://gitlab.cern.ch/jspah/higgsdna_finalfits_tutorial_24/-/tree/master/07_FinalFits?ref_type=heads) mentioned before. Also, [here]( https://www.notion.so/Higgs-To-MuMu-c33f76b4fe0845869da467b6a4c4da0d?p=1f2b56b1870b8082aa86d1465bc6941c&pm=s ) is a list of all the commands individually in case you want to execute them one by one to debug something

## Significance and Limits.

To calculate the limits, first do:

```
cd Combine
mkdir -p Models/signal
mkdir -p Models/background
cp ../Signal/outdir_packaged/CMS-HGG_sigfit_packaged*.root Models/signal/
cp ../Background/outdir_tutorial/CMS-HGG_multipdf*.root Models/background/
cp ../Datacard/Datacard_tutorial*.txt .
```

This will move the root files with the fits and the datacards to the right directory.

To go from datacarts.txt to datacards.root do:
```
python3 RunText2Workspace.py --mode mu_inclusive --batch local --ext _tutorial_(category)
```

where categorie can be ggH,,ggHcat1, gHcat2, gHcat3, VBF, VBFcat1, VBFcat2, VBFcat3, VBFcat4.

Then obtain the significance by running. 
```
combine -M Significance Datacard_tutorial_(category)_mu_inclusive.root -m 125 -t -1 --expectSignal 1
```

And for the asymptotic limits:
```
combine -M AsymptoticLimits Datacard_tutorial_(category)_mu_inclusive.root -m 125 -t -1 --run blind
```
