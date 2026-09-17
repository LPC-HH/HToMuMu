This code does the BDT training for the ggH and/or VBF Categorization.

## First time only

Go to https://uscms.org/uscms_at_work/computing/setup/gpu.shtml and follow the EAF instructions.

If you are not in Fermilab you will need to setup a vpn. Here are the instructions: https://uscms.org/uscms_at_work/physics/computing/setup/remote.shtml#VPN

Once you have access to the cluster and the grid, go to https://analytics-hub.fnal.gov, create a server (you can request a 20GB el9 workspace in CMS CERN, for instance).

When you are in, do
```
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)
micromamba create -n xgboost_env xgboost python=3.10 krb5 curl cfitsio root tensorflow keras cupy -c conda-forge
cd /<your_path>/python/xgboost
source setup.sh #activates the xgboost_env
pip3 install pandas 
pip3 install uproot
pip3 install matplotlib
pip3 install graphviz
pip3 install mplhep
pip3 install optuna
pip3 install plotly
pip3 install seaborn


```

If you are having issues with xgboost not using cuda, you may need to 
```
micromamba remove xgboost py-xgboost libxgboost
micromamba install -c conda-forge "py-xgboost=*=cuda*"
```

## How to run

Pick your node https://analytics-hub.fnal.gov/hub/home and go to the xgboost directory
```
cd /your_path/HmmAnalysis/python/xgboost
source setup.sh #activates the xgboost_env
```

Run the training (Make sure you generated the skim tuples first)
```
python3 train.py channel era ifRetrain ifUseBDTReCategorization background_sources_subset signal_sources_subset
```

You can append the BDT variable to the tuples running
```
python3 append_xgboost_discriminator_to_tree.py higgs_channel era era_model data_set bkg_src signal_src
```

You can run everything with the following script (the wait makes sure that node memory doesnt fill)
```
bash run_train.sh higgs_channel ifUseBDTReCategorization
bash run_train.sh ggH T & bash run_train.sh ggH F & wait; bash run_train.sh VBF T & bash run_train.sh VBF F
```
