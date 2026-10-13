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
It writes the best configuration (parameters, number of rounds and the per-fold CV results) to
`models/dev/config_optuna_<name>.json` and the Optuna history/importance plots to `optunaPlots/`.
The training mass window is `TRAIN_REGION` in `xgb_kfold.py`.
# 2. Optuna test
Only run this ONCE after the optuna development since this looks at the held out 20% of events to validate the optuna created model. Information from this should not be used to further tune the model.
Before doing the optimization, set N_OPTUNA_TRIALS, MAX_ESTIMATORS, EARLY_STOPPING ROUNDS to whichever values you'd like
```bash
python3 train.py higgs_channel era --stage test
#e.g. python3 train.py ggH Combined --stage test
```
It refits the configuration on the 80% development sample, prints the test-sample AUC/log loss next to
the CV numbers and writes `results/test_evaluation_<name>.json`. A marker file then refuses a second
evaluation unless `--force-retest` is given.

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
If you'd like to compare with the 60/40 train/test legacy model without k-folding, just use --stage legacy (it trains on the pre-K-fold input set, the same as Matias's BDT: 22 VBF / 18 ggH inputs, i.e. without `subleading_jet_eta`, the PNet QvG and nConstituents jet variables and `mc_campaign`; see `xgb_utils.LEGACY_EXCLUDED_INPUTS`. The training weights still come from the flags or `--weights`; use `--weights massRes` to match his |w|/err weights). Add `--matias-preprocessing` to also use his preprocessing in the legacy training and tuple scoring (padded jet values kept at 0 / -1, standardization over the other entries only, no NaN masking; a Matias-format pickle `models/preprocessing_<name>_legacy_matias_bsC.pkl` is saved for `score_external_model.py`). This matters for ggH (0/1-jet events) but not VBF; reproducing his trees exactly also needs his xgboost version (2.1.1), since the histogram bin edges differ between versions. To score the tuples with an external single model and its own preprocessing convention (e.g. Matias's model file), use `python3 score_external_model.py <ch> <model.xgb> <preprocessing.pkl> [--out-suffix matiasModel]`; it writes `BDT_score/<ch><suffix>/`, then `bash scripts/hadd_bdt.sh <ch> <suffix>` and `python3 plot_BDT_Categories.py <ch> Combined --variant <suffix>`
```bash
python3 train.py higgs_channel era --stage legacy
```
If you just want to look at the model without evaluating the BDT scores and creating new tuples, just apply the argument --no-apply
```bash
python3 train.py higgs_channel era --stage legacy --no-apply
```

# 4. Compare the six training variants (one command)
`--stage compare` trains (or reuses) six 5-fold model sets per channel and appends all six scores to one skimmed copy of each nominal tuple in `root_io/tuples/BDT_score/<channel>compare/BFull_SNottH/`. It ignores the module weight flags (`USE_WEIGHT*`, `REWEIGHT_BKG_FLAT`, `FLAT_BEFORE_MASS_RES`).

**Choosing the training weights.** Every other stage uses the module weight flags at the top of `train.py`, or `--weights` to override them without editing the file:
- `massRes`: |w| / rel_err;
- `flat`: background |w| flat in M_mumu, signal |w|;
- `flatMassRes`: flat |w|, then / rel_err. The Asimov objectives require it.

The weights are part of the output names (`_flat`, `_flatMassRes`), so different schemes never overwrite each other. For example:
```
python3 train.py VBF Combined --stage all --weights massRes --do-systematics                                    # base model, |w|/err
python3 train.py VBF Combined --stage all --weights flatMassRes --objective asimov_fit --use-optuna --do-systematics   # asimov-fit config
```

| variant | parameters | training weights | branch | models |
|---|---|---|---|---|
| base | DEFAULT_PARAMS | \|w\|/rel_err | `BDT_<ch>` | `model_<ch>_Combined_BFull_SNottH_fold<k>` |
| optimized | Optuna `config_optuna_<ch>_..._SNottH.json` | \|w\|/rel_err | `BDT_<ch>_optimized` | `..._optimized_fold<k>` |
| flat | DEFAULT_PARAMS | background \|w\| flat in mass, signal \|w\| | `BDT_<ch>_flat` | `..._flat_fold<k>` |
| optimized_flat | Optuna `..._flat.json` | same as flat | `BDT_<ch>_optimized_flat` | `..._flat_optimized_fold<k>` |
| flatMassRes | DEFAULT_PARAMS | background \|w\| flat, then everything / rel_err | `BDT_<ch>_flatMassRes` | `..._flatMassRes_fold<k>` |
| optimized_flatMassRes | Optuna `..._flatMassRes.json` | same as flatMassRes | `BDT_<ch>_optimized_flatMassRes` | `..._flatMassRes_optimized_fold<k>` |

All six share one `BDT_fold` branch (the fold is `event % 5` for every variant). A variant's saved models are reused when they exist and match the current input variables, the number of trees in the configuration, the hyper-parameters of the configuration (device, threads, verbosity and eval metrics are ignored) and (if recorded) the training weights; otherwise that variant is retrained, and the log says why (e.g. `hyper-parameters differ (max_depth 5 -> 7, ...)`). So after a new `--stage dev` study, only the variants whose configuration changed are retrained. `--retrain` retrains all of them. Overlay ROC and S/sqrt(B) plots of the OOF scores (signal region, physics weights) and a JSON summary go to `plots/xgboost/<ch>compare/BFull_SNottH/`. The S/sqrt(B) plot has a lower panel zoomed on the six maxima, and `tight_mass_variants_BDTgt<cut>_*` compares the background M_mumu shape in the tight category (BDT > `--tight-cut`, default `TIGHT_CATEGORY_CUT = 0.9` in train.py) of every variant with the inclusive shape, to compare sculpting. Each reused variant's own `plots/xgboost/<ch><variant>/.../training/BDTsculpting_OOF_<ch>_<era>` (background M_mumu for BDT > 0, 0.1, ..., 0.9; spacing set by `SCULPTING_DIVISIONS` in train.py) is redrawn from the same scores. `--plots-only` redraws all of this without training or writing tuples (it stops with an error if a variant has no reusable models). It reads the six scores straight from the per-sample compare tuples (`BDT_score/<ch>compare/`, no hadd needed; the training-region rows of those tuples are exactly the training skim's events, with the same fold-matched scores), which skips evaluating 30 models. It falls back to evaluating the models on the training skims when a compare tuple is missing, lacks a score branch, or is older than any variant's models; `--rescore` forces that, and `--smoke` implies it.

The `flat` and `flatMassRes` Optuna configs in `models/dev/` are currently copies of the base Optuna study (so their `training_weights` field still says `mass_res`). Only `params` and `n_rounds` are read.

```bash
bash run_compare.sh               # ggH + VBF, then hadd both BDT_score/<ch>compare/ dirs
bash run_compare.sh --categories  # ... and plot_BDT_Categories.py for every variant
bash run_compare.sh --categories-only  # only plot_BDT_Categories.py for every variant, on the existing hadded compare tuples
bash run_compare.sh --retrain     # retrain every variant
bash run_compare.sh --plots-only  # only redraw the comparison plots from the saved models
bash run_compare.sh --plots-only --tight-cut 0.85  # ... with another tight-category cut
bash run_compare.sh --plots-only --rescore  # ... evaluating the models instead of reading the tuples
# one channel by hand, no tuple writing:
python3 train.py ggH Combined --stage compare --no-apply
# categories of one variant (saved under the key <ch>compare_<variant>):
cd ../../plot_macros && python3 plot_BDT_Categories.py ggH Combined --compare --score optimized_flatMassRes
```

# 5. Choosing the Optuna metric
`evaluate_metrics.py` computes candidate Optuna objectives for the six compare variants of a channel from the hadded compare tuples (no model evaluation, runs on LPC): physics-weighted AUC, max S/sqrt(B), signal efficiency at 1% background efficiency, and a binned Asimov significance over fixed BDT categories x M_mumu bins with the background from a fit to the background MC (`asimov_mc`), to the Data sidebands (`asimov_data`, 120-130 GeV never read), and with the real `plot_BDT_Categories.py` boundaries (`asimov_actual_cats`, once `run_compare.sh --categories-only` has run).
```bash
python3 evaluate_metrics.py ggH
python3 evaluate_metrics.py VBF --combine-json combine_VBF.json  # {"base": Z, "optimized": Z, ...}
python3 evaluate_metrics.py VBF --plot-fits                     # also plot every category's background fit
```
Fill the combine JSON by hand from the flashggFinalFit/combine expected significance of each variant; the script then prints the rank correlation of every metric with combine. Results: `plots/xgboost/<ch>compare/BFull_SNottH/results/metric_validation_<ch>_<era>.json` and `comparison/metric_validation_<ch>_<era>`.

# 6. Asimov Optuna objective
`--objective asimov` (flatMassRes training weights only) makes `--stage dev` maximize the binned Asimov significance instead of the weighted AUC:
- per CV validation fold: 8 fixed categories (top 2/5/10/20/35/50/70/100% of the physics-weighted signal) x 2 GeV M_mumu bins over 115-135 GeV, signal and **raw background MC** with physics weights, scaled to the full sample (x N_FOLDS / (1 - TEST_FRACTION)); background bins <= 0 are merged with a neighbour (a background-free category into the next looser one) and each bin's sqrt(sum w^2) enters Cowan's Z_A as the background uncertainty; Z = sqrt(sum of Z_bin^2). No Data is used.
- Z is evaluated every 50 boosting rounds (`ASIMOV_CHECKPOINT_EVERY`); a trial's value is the best fold-averaged Z and its checkpoint becomes `n_rounds`. Logloss early stopping is only a safety cap (patience 200, `ASIMOV_EARLY_STOPPING_ROUNDS`).
- Outputs carry `_asimov`: `models/dev/config_optuna_<ch>_Combined_BFull_SNottH_flatMassRes_asimov.json`, its own test marker, models `..._flatMassRes_asimov_fold<k>`. The existing (AUC) configs are untouched.
```bash
python3 train.py <ch> Combined --stage dev --objective asimov
python3 train.py <ch> Combined --stage test --use-optuna --objective asimov   # ONCE
bash run_compare.sh            # trains + scores the 7th compare variant asimov_flatMassRes (re-skims the tuples)
python3 evaluate_metrics.py <ch> [--combine-json ...]
```
`evaluate_metrics.py` reports the objective itself on the full OOF tuples as `asimov_objective`.
`--stage test --use-optuna --objective asimov` (or `asimov_fit`) also reports both Asimov Z (raw and fitted background MC, scaled by 1/TEST_FRACTION) of the development-sample refit on the untouched test sample, per category, next to the CV mean Z of the chosen configuration (also in `results/test_evaluation_<name>.json` under `test_asimov`). The CV value is taken at the best checkpoint of the best trial, so it typically sits somewhat above the test value; the test value is the unbiased one.

`--stage test` also draws diagnostics of the refit on the test sample (MC only):

| plot | where | variants |
|---|---|---|
| ROC of the test and training samples: training weights over 115-135 GeV, and physics weights in the 121-129 GeV signal region (with the physics-weighted working points printed) | `training/myroc_test_<name>`, `training/myroc_test_physSR_<name>` | all |
| training-vs-test score overlay (overtraining), log and linear, with the train/test AUC and the weighted KS D and p per class (also printed and in the json under `train_vs_test`) | `training/mydiscriminator_test_{log,linear}Y` | all |
| background mass shape for nested BDT cuts | `training/BDTsculpting_test_*` | all |
| sideband-pull sculpting check of the fixed categories (the Optuna constraint, information only here; also in the json under `test_sculpting`) | `test/test_sculpting` | all |
| score distribution with the category edges | `test/test_scores` | Asimov |
| tightest category's exponential background fit | `test/test_bkgfit` | Asimov |
| Asimov Z per category and total, test (raw and fit) vs the CV folds | `test/test_z_categories` | Asimov |

The KS p-value uses Kish effective sizes; with the full samples it is tiny for any visible difference, so read D (the largest CDF difference) as the size of the effect. A training AUC above the test AUC shows memorization of the training events; what matters for the analysis is that the test AUC / Z agree with the CV values. The per-category CV points need `cv.fold_z_categories` in the config, which studies record from now on; older configs show the CV total only. To draw the plots for a configuration already tested, rerun with `--force-retest` (fine as long as the configuration is not changed because of what you see).
`--optuna-timeout HOURS` (any `--stage dev`) stops starting new trials after that time: the running trial finishes and the best configuration is still written (the config records `n_trials_completed` and `timed_out`). Use it for overnight runs, e.g. ggH then VBF on one GPU within 17 h:
```bash
nohup sh -c 'python3 train.py ggH Combined --stage dev --objective asimov --optuna-trials 60 --optuna-timeout 13.5 > ggHAsimovOpt.log 2>&1; python3 train.py VBF Combined --stage dev --objective asimov --optuna-trials 100 --optuna-timeout 3 > VBFAsimovOpt.log 2>&1' &
```
Every trial (pruned ones included) writes `optunaPlots/<ch>/<name>_asimov/trials/trial_<NNN>.{png,pdf}`: Z vs boosting round per validation fold with the fold average and the chosen checkpoint, and the per-category Z of each fold at that checkpoint. `trial_<NNN>_scores.{png,pdf}` shows the BDT probability of the validation folds together (out-of-fold) at the chosen round, signal and background normalized to unit area, with the category edges (dashed: mean over the folds, band: their min-max) and a zoom on the tight categories.

# 7. Asimov objective with a fitted background
`--objective asimov_fit` is `--objective asimov` with the background of every category taken from an **exponential fitted to all of the category's background MC** in 115-135 GeV (`xgb_kfold.binned_asimov_z_fit`) instead of the raw background MC per 2 GeV bin. In the tight categories a few heavily weighted MC events per bin made the raw Z jump between checkpoints and folds.
- Fit: unbinned weighted maximum likelihood of exp(-lambda m) on 115-135 GeV (closed-form moments + a 1D root), normalized to the category's sum(w); its sandwich covariance (weighted events) gives sigma_b per bin in Cowan's Z (bin-to-bin correlation ignored). Signal stays the raw MC. A category with sum(w) <= 0 or fewer than `ASIMOV_FIT_MIN_EVENTS` (10) background MC events joins the next looser one. Categories, mass bins and scaling as for `asimov`.
- Outputs carry `_asimovFit`: `config_optuna_<ch>_Combined_BFull_SNottH_flatMassRes_asimovFit.json`, models `..._flatMassRes_asimovFit_fold<k>`, compare variant/branch `asimovFit_flatMassRes` / `BDT_<ch>_asimovFit_flatMassRes` (brown dash-dot in the compare plots). The raw-MC `asimov` outputs are untouched.
- The Z values are not comparable in absolute terms with `asimov`: without sigma_b both agree (ggH 3.275 vs 3.276), but the raw metric's per-bin sqrt(sum w^2) is a much larger penalty (ggH background MC has sum(w^2)/sum(w) = 1.2), e.g. 2.18 (raw) vs 2.81 (fit) on the ggH asimov OOF scores. Compare trials of one objective with each other, and both objectives through `evaluate_metrics.py` (`asimov_objective`, `asimov_fit_objective`).
- Trial plots: as `asimov`, plus `trial_<NNN>_bkgfit.{png,pdf}`: the tightest category's background MC of every validation fold at the chosen round with the fit, its uncertainty band and the pulls.
```bash
python3 train.py <ch> Combined --stage dev --objective asimov_fit [--optuna-trials N --optuna-timeout HOURS]
python3 train.py <ch> Combined --stage test --use-optuna --objective asimov_fit   # ONCE
python3 train.py <ch> Combined --stage final --use-optuna --objective asimov_fit
bash run_compare.sh --categories   # adds the asimovFit_flatMassRes variant (re-skims the tuples)
```
Noise check (LPC, seconds for VBF, ~3 min for ggH): the MC-statistical spread of both objectives over bootstrap resamples (with replacement) of one fold's background MC, from the OOF scores of a finished variant (`models/oof_<name>.npz`):
```bash
python3 evaluate_metrics.py <ch> --noise-check [flatMassRes_asimov] [--n-boot 100]
```
On the asimov models the fit cuts the spread of the total Z from 6.0% to 2.7% (VBF) and from 1.8% to 0.66% (ggH), mostly in the tight categories. Results: `plots/xgboost/<ch>compare/BFull_SNottH/{results,comparison}/asimov_noise_<name>*`.

# 8. Optuna search space, mass-sculpting constraint and crash-safe studies
- Search space (`xgb_kfold.SEARCH_SPACE`): `max_depth` 2-7 (every earlier config sat at the old bound 5), `colsample_bytree` 0.4-1.0, the rest unchanged; `MAX_ESTIMATORS` = 3000 (`train.py`). Both are recorded in the config.
- **Mass-sculpting constraint** (both Asimov objectives): the inputs (p_T^mumu, p_T/m of both muons, eta, y, CS angles) nearly determine M_mumu, so a BDT can learn "M ~ 125 -> signal" and carve a background bump under the peak (which the exponential of `asimov_fit` would even reward). For every trial, at its chosen round, per fixed category and validation fold, the fold's inclusive background mass shape (sculpting cannot change it: it only moves events between categories; it carries the not purely exponential Z-tail curvature) times an exponential tilt fitted to the category's sidebands (115-120, 130-135 GeV) predicts the 120-130 GeV window; pull = (MC - prediction) / sqrt(sum w^2 + sigma_pred^2), combined over the folds as sum/sqrt(n). A trial with a pull > 3 in a category within the top 10% of the signal (0-2/2-5/5-10%; when tied scores merge categories, the merged range, e.g. 0-5%, labels and counts too) is **infeasible**: `TPESampler(constraints_func)` steers away from it and it is never chosen (`kf.best_feasible_trial`; the config records `sculpting`, `sculpting_feasible`, `n_trials_infeasible`). On the existing OOF scores: VBF models all within ~1 sigma; ggH default/asimov models 1-4% window excess (feasible); the AUC-optimized ggH models +5 to +13% in the 10-70% categories (`ggH_optimized`: up to 25 sigma) and infeasible.
- Trial plot `trial_<NNN>_sculpting.{png,pdf}`, one panel per category (validation folds summed, normalized to the category's background MC): black = the category's background MC; grey = the inclusive background (the reference shape of the prediction); blue dashed = the sideband prediction (inclusive shape x exp(-lambda m), lambda fitted to the category's 115-120 and 130-135 GeV MC, normalized to its sideband yield). The lower panel shows MC / prediction with the window prediction uncertainty as a band. The text box gives the numbers behind the decision: window MC vs prediction +- sigma (fold sums, with the excess in %), the tilt lambda, the per-fold pulls and their combination sum/sqrt(n) (the value the constraint uses), and a weighted KS p-value (category vs the rest of the background; information only: at ggH statistics any shape difference gives p ~ 0). Infeasible tight categories are framed red; infeasible trials are also marked red in `trial_<NNN>.png` and the log. The config's `sculpting` block records the same numbers.
- **Studies on disk**: every trial is stored in `optunaStudies/<name>.db` (sqlite, gitignored), and the best-so-far configuration is rewritten after every finished trial (`partial: true` until the study ends; test/final warn about a partial config). A trial that raises (e.g. GPU out of memory) is recorded as failed and the study goes on (it stops after 3 failures in a row).
- **Resuming is explicit**: without `--optuna-resume`, `--stage dev` always starts a NEW study and archives (renames, never deletes) an existing `.db` and `trials/` plot folder with their timestamp. After a crash, rerun the same command with `--optuna-resume`: the stored study must have the same setup (objective, search space, MAX_ESTIMATORS, early stopping, checkpoints, seed, smoke, events, weights, variables; otherwise it refuses), trials left running by the crash are marked failed, `--optuna-trials` is the total to reach and `--optuna-timeout` counts from the restart.
```bash
# weekend: ggH then VBF (one GPU)
nohup sh -c 'python3 train.py ggH Combined --stage dev --objective asimov_fit --optuna-trials 150 --optuna-timeout 46 > ggHAsimovFitOpt.log 2>&1; python3 train.py VBF Combined --stage dev --objective asimov_fit --optuna-trials 250 --optuna-timeout 10 > VBFAsimovFitOpt.log 2>&1' &
# after a crash, e.g. of ggH (adjust the timeout to the time left):
nohup python3 train.py ggH Combined --stage dev --objective asimov_fit --optuna-trials 150 --optuna-timeout 20 --optuna-resume > ggHAsimovFitOpt_resume.log 2>&1 &
```

## Running systematics
**WIP**
