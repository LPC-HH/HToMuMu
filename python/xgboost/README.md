This code does the BDT training for the ggH and/or VBF Categorization.

## First time only

Go to https://uscms.org/uscms_at_work/computing/setup/gpu.shtml and follow the EAF instructions.

If you are not in Fermilab you will need to setup a vpn. Here are the instructions: https://uscms.org/uscms_at_work/physics/computing/setup/remote.shtml#VPN

Once you have access to the cluster and the grid, go to https://analytics-hub.fnal.gov, create a server (you can request a 20GB el9 workspace in CMS CERN, for instance).

When you are in, do
```bash
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
```bash
micromamba remove xgboost py-xgboost libxgboost
micromamba install -c conda-forge "py-xgboost=*=cuda*"
```

To test xgboost and cuda, run
```bash
python -c "import cupy; print(cupy.cuda.runtime.getDeviceCount())"
python -c "import xgboost; print(xgboost.build_info())"
```

## How to run

Pick your node https://analytics-hub.fnal.gov/hub/home and go to the xgboost directory
```
cd /your_path/HmmAnalysis/python/xgboost
source setup.sh #activates the xgboost_env
```

## K-fold training BDT scoring

*train* (fits one model), *validation* (early stopping / Optuna), *test* (untouched 20%,
evaluated once), *OOF* (score from the model that excluded the event's fold).

One thing to note, there are severable tunable parameters at the set as variables in the beggining of train.py. For example
```python
DRAW_CORRELATIONS = False # draw correlation matrix (is slow so usually set to false)
PLOT_INPUT_COMPARISON = True  # signal vs background shape of every BDT input variable
PLOT_STANDARDIZATION = True  # per input: train vs held-out, before and after standardization
DO_STANDARDIZATION = True
USE_WEIGHT = False
USE_WEIGHT_MASS_RES = True  # mutually exclusive with USE_WEIGHT
USE_BSCONSTRAIN = Tru
PLOT_LOSS = True #Plot loss curves

SIGNAL_REGION = (121., 129.)
TRAIN_REGION = (115., 135.)
PROGRESS_EVERY = 10  # print boosting progress every N rounds (0 = silent)

SMOKE_FRACTION = 0.05
SMOKE_TRIALS = 3
SMOKE_ROUNDS = 20
```
The input options for train.py are:
```bash
python3 train.py <channel> <era> [--stage dev|test|final|apply|all|legacy] \
 [--do-systematics] [--use-recategorization] [--bkg-subset Full] [--sig-subset NottH] \
 [--device cuda|cpu] [--use-optuna] [--smoke] [--no-apply] [--plots-only] ...
```
Only the channel and era are required. The background/signal subsets default to `Full`/`NottH`.
`--stage dev` always runs the Optuna study, and `--stage final`/`all` always retrain.
Run `python3 train.py --help` for the full list.

**The fold rule** is **`event % 5`**
There are 4 stages to the BDT training. However, in each stage running --smoke creates a test run that can be used to debug/make sure the full run will operate smoothly
# 1. Optuna development
In this stage, the optuna study is completed using k-fold validation using a few key parameters set in train.pyIn this stage, the optuna study is completed using k-fold validation using a few key parameters set in train.py
```bash
python3 train.py higgs_channel era --stage dev
#e.g. python3 train.py ggH Combined --stage dev
```
```python
N_OPTUNA_TRIALS = 50 # Set the number of optuna trials (50-500 is reasonable to saturate)
MAX_ESTIMATORS = 2000  # cap for CV with early stopping
EARLY_STOPPING_ROUNDS = 50  # on the VALIDATION fold, CV only
N_ROUNDS_SCALE = 1.0  # final rounds = median(best_iter + 1) * scale
```
# 2. Optuna test
Only run this ONCE after the optuna development since this looks at the held out 20% of events to validate the optuna created model. Information from this should not be used to further tune the model.
Before doing the optimization, set N_OPTUNA_TRIALS, MAX_ESTIMATORS, EARLY_STOPPING ROUNDS to whichever values you'd like
```bash
python3 train.py higgs_channel era --stage test
#e.g. python3 train.py ggH Combined --stage test
```

# 3. Final BDT training
This is the main step that needs to be run for each set of new tuples. If you set --stage final, the model is trained and NOT appended to the tuples.
```bash
python3 train.py higgs_channel era --stage final
#e.g. python3 train.py ggH Combined --stage final
```

# 4. Scoring BDT tuples
Lastly, to apply the tuples, the stage is set to --stage apply. If you want to run the training and apply in the same step, run --stage all or do not specify a stage (all is the default)

```bash
python3 train.py higgs_channel era --stage apply
#e.g. python3 train.py ggH Combined --stage apply
```

# 5. Leakage check
To ensure that the folding and training has been don properly, you finally want to run audit_no_leakage.py
```bash
python3 audit_no_leakage.py channel era
#e.g. python3 audit_no_leakage.py ggH Combined
```

## Basic k-fold BDT pipeline
# 0. Testing
Before running the full training and append, try running --smoke to make sure everything will run smoothly
# 1. Use nominal model
If --use-optuna is not passed, the defaul model parameters of depth=3, LR=0.1, reg_lambda=1.0, trees=400 will automatically be used. The following will train the model and score the BDT tuples
```bash
python3 train.py higgs_channel era
python3 audit_no_leakage.py channel era
```
When running this, if you use --plots-only, only the input/standardization plots will be created without training the model

# 2. Use optimized model
If --use-optuna is passed, the stored optuna configuration in models/dev/config_optuna_<channel>_<era>_<bkg_subset>_<signal_subset>.json will be read and used for the training and optimization. To do this, it is similar to the nominal with just one argument passed
```bash
python3 train.py higgs_channel era --use-optuna
python3 audit_no_leakage.py channel era
```

# 3. LEGACY no k-folding
If you'd like to compare with the 60/40 train/test legacy model without k-folding, just use --stage legacy
```bash
python3 train.py higgs_channel era --stage legacy
```
If you just want to look at the model without evaluating the BDT scores and creating new tuples, just apply the argument --no-apply
```bash
python3 train.py higgs_channel era --stage legacy --no-apply
```

## Running systematics
**WIP**
