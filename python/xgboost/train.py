#!/usr/bin/env python
# coding: utf-8
"""BDT training with an untouched test sample, 5-fold CV for model development and
final 5-fold out-of-fold (OOF) analysis models.

Vocabulary (kept strictly separate in names and comments):
  train       events used to fit one particular model
  validation  events used for early stopping and Optuna/model selection
  test        untouched 20% sample, evaluated once after the configuration is frozen
  OOF         final-analysis score of an MC event from the model that EXCLUDED its fold

Usage:
  python3 train.py <channel> <era> [--stage dev|test|final|apply|all|legacy]
                   [--do-systematics] [--use-recategorization]
                   [--bkg-subset Full] [--sig-subset NottH]
                   [--plots-only] [--no-apply] [--use-optuna] [--force-retest] [--smoke]
                   [--device cuda|cpu] [--optuna-trials N] [--control-80]

Stages
  dev    Stage 1-2: split off the test sample, 5-fold CV on the development sample
         with Optuna, freeze the configuration (models/dev/config_*.json).
  test   Stage 3: evaluate the frozen configuration on the untouched test sample, once.
  final  Stage 4: train the five analysis models on ALL MC;
         OOF ROC / discriminator / sculpting / working-point plots.
  apply  append fold-matched BDT scores to the nominal MC and Data tuples.
  all    (default) final + apply, i.e. the old one-shot behaviour of run_train.sh.
  legacy the pre-K-fold approach for comparison: one 60/40 split, one model, head-to-head
         against the K-fold OOF scores on the identical 40%, then scores the tuples into a
         separate BDT_score/<channel>legacy/ tree. Needs --stage final to have run.

--plots-only draws the input and standardization plots and stops before any training,
whatever --stage says. Nothing is trained, saved or scored.

--no-apply runs the stage but skips writing the scored tuples. Useful with --stage legacy,
whose tuple scoring is a second full copy of the BDT_score tree (~38 GB for ggH) and is only
needed for the downstream category comparison -- the head-to-head metrics cost nothing.
"""
import argparse
import json
import math
import os
import resource
import shutil
import sys

import numpy as np
import pandas as pd
import uproot
from sklearn.metrics import roc_curve, roc_auc_score

import xgb_kfold as kf
import xgb_utils

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------
DRAW_CORRELATIONS = False # draw correlation matrix (is slow so usually set to false)
PLOT_INPUT_COMPARISON = True  # signal vs background shape of every BDT input variable
PLOT_STANDARDIZATION = True  # per input: train vs held-out, before and after standardization
DO_STANDARDIZATION = True
USE_WEIGHT = False
USE_WEIGHT_MASS_RES = True  # mutually exclusive with USE_WEIGHT
APPEND_VARIABLES = True
USE_BSCONSTRAIN = True
PLOT_LOSS = True
SEED = 7  # dev/test split, CV folds, Optuna sampler
TEST_FRACTION = 0.2  # untouched test sample (Stage 1)
# Hyperparameters of the analysis models. These are the values the current ggH/VBF models
# were trained with; they are used unless --use-optuna asks for an Optuna-tuned config.

DEFAULT_PARAMS = dict(max_depth=3, learning_rate=0.1, reg_lambda=1.0)
DEFAULT_N_ROUNDS = 400

#Previously optimized
#DEFAULT_PARAMS = {'max_depth': 5, 'learning_rate': 0.17065960988185175, 'min_child_weight': 1.258974431208238,
#                            'subsample': 0.9799252299722975, 'colsample_bytree': 0.9857090292326347, 
#                            'reg_lambda': 0.17418443431820596, 'reg_alpha': 0.03970459451078197}
#DEFAULT_N_ROUNDS = 1500

N_OPTUNA_TRIALS = 50 #Set the number of optuna trials (50-500 is reasonable to saturate)
MAX_ESTIMATORS = 2000  # cap for CV with early stopping
EARLY_STOPPING_ROUNDS = 50  # on the VALIDATION fold, CV only
N_ROUNDS_SCALE = 1.0  # final rounds = median(best_iter + 1) * scale
SIGNAL_REGION = (121., 129.)
TRAIN_REGION = (115., 135.)
PROGRESS_EVERY = 10  # print boosting progress every N rounds (0 = silent)
MONITOR_MAX_ROWS = 1_000_000  # train/held-out monitoring curves use at most this many events (None = all)
IN_FOLD_PLOT_MAX_ROWS = 1_000_000  # in-fold predictions kept for the overtraining plot, per model
# the pre-K-fold approach, reproduced for A/B comparison (--stage legacy)
LEGACY_TEST_FRACTION = 0.4  # the original TEST_SIZE
LEGACY_SEED = 7            # the original random_state
# log loss vs boosting round, recomputed from the saved models (--stage legacy only).
# Cost is linear in MAX_ROWS and ~quadratic in 1/ROUND_STEP.
LOSS_CURVE_ROUND_STEP = 10     # evaluate the truncated models every N boosting rounds
LOSS_CURVE_MAX_ROWS = 250_000  # events per fold per curve, drawn from the held-out 40%
LOSS_CURVE_SEED = 900          # subsample seed base, distinct from the 0/1/2/100+i/200+i seeds
# --control-80: one extra single-split model trained on 80%, i.e. EXACTLY the per-model
# training size of a K-fold model, to test whether the K-fold in-fold loss offset is explained
# by training-set size alone. At a fixed seed train_test_split nests, so the 60% train set is a
# subset of the 80% one and both models are in-sample on it (asserted in xgb_kfold._selftest).
CONTROL_TEST_FRACTION = 0.2
SMOKE_FRACTION = 0.05
SMOKE_TRIALS = 3
SMOKE_ROUNDS = 20


def parse_cli(argv):
    p = argparse.ArgumentParser(description="K-fold BDT training for H->mumu (see module docstring).")
    p.add_argument("channel", help="channel under study, e.g. ggH or VBF")
    p.add_argument("era", help="e.g. Combined")
    p.add_argument("--stage", default="all", choices=("dev", "test", "final", "apply", "all", "legacy"))
    p.add_argument("--do-systematics", action="store_true",
                   help="with --stage apply/all: also score the systematic tuples")
    p.add_argument("--use-recategorization", action="store_true", help="use the reCat skims/outputs")
    p.add_argument("--bkg-subset", default="Full", help="background subset (default: Full)")
    p.add_argument("--sig-subset", default="NottH", help="signal subset (default: NottH)")
    p.add_argument("--device", default="cuda", choices=("cuda", "cpu"))
    p.add_argument("--optuna-trials", type=int, default=None)
    for flag in ("--force-retest", "--smoke", "--use-optuna", "--plots-only", "--no-apply", "--control-80"):
        p.add_argument(flag, action="store_true")
    opts = vars(p.parse_args(argv[1:]))
    if opts["control_80"] and opts["stage"] != "legacy":
        sys.exit("[ERROR] --control-80 is a --stage legacy diagnostic: it trains one extra "
                 "single-split model on 80% to test whether the K-fold in-fold loss offset is "
                 "explained by training-set size alone.")
    if opts["no_apply"] and opts["stage"] == "apply":
        sys.exit("[ERROR] --no-apply with --stage apply leaves nothing to do (that stage only "
                 "writes scored tuples). Use it with --stage legacy or --stage all.")
    if opts["smoke"] and opts["stage"] in ("apply", "all") and not opts["plots_only"]:
        # smoke models are throwaway (20 rounds, 5% of events) but the scored-tuple paths are
        # shared with the real ones: never let them overwrite real BDT_score tuples
        sys.exit("[ERROR] --smoke cannot be combined with --stage apply/all (it would write scores from "
                 "throwaway models into the real BDT_score tuples). Use --stage dev, test or final.")
    return opts


OPTS = parse_cli(sys.argv)
channel_US, era = OPTS["channel"], OPTS["era"]
doSystematics = OPTS["do_systematics"]
useRecategorization = OPTS["use_recategorization"]
background_subset = OPTS["bkg_subset"]
signal_subset = OPTS["sig_subset"]

print("Channel under study: ", channel_US)
print("Era: ", era)
print("Do systematics: ", doSystematics)
print("Background subset: ", background_subset)
print("Signal subset: ", signal_subset)
print("Using recatagorization? ", useRecategorization)
print("Stage: ", OPTS["stage"], "| smoke:", OPTS["smoke"], "| device:", OPTS["device"])
if OPTS["plots_only"]:
    # the point of the flag is to get the plots, so it overrides the two constants
    PLOT_INPUT_COMPARISON = PLOT_STANDARDIZATION = True
    print("[INFO] --plots-only: input and standardization plots only, no training or scoring")
if OPTS["no_apply"]:
    APPEND_VARIABLES = False
    print("[INFO] --no-apply: the stage will run but will NOT write any scored tuples")

# doSystematics=T used to be refused here: a systematic tuple's rows do not line up with the
# nominal ones (the b-veto and mass cuts move with the variation), so before the per-event ID a
# varied event could not inherit its nominal event's fold. With fold = event % N_FOLDS
# (xgb_kfold.fold_of_event) a varied event carries the same `event` as its nominal self, so it
# lands in the same fold and is scored by the same out-of-fold model.

variables = xgb_utils.get_variables(channel_US, USE_BSCONSTRAIN)
names = [v[0] for v in variables[:-3]]
print("number of variables", len(variables) - 3)
print("Variables being used in training: ")
for name in names: 
    print(name)

if useRecategorization:
    plot_path = f"../../plots/xgboost/{channel_US}reCat/B{background_subset}_S{signal_subset}/"
    data_directory = f"../../root_io/skim/{channel_US}reCat/"
    file_append = "reCat"
else:
    plot_path = f"../../plots/xgboost/{channel_US}/B{background_subset}_S{signal_subset}/"
    data_directory = f"../../root_io/skim/{channel_US}/"
    file_append = ""

run_tag = "_smoke" if OPTS["smoke"] else ""
test_name = f"{channel_US}{file_append}_{era}_B{background_subset}_S{signal_subset}{run_tag}"
DEV_DIR = "models/dev"
# Written only by `--stage dev`, and read back only with --use-optuna,
# so an Optuna study can never silently replace DEFAULT_PARAMS in the final training.
optuna_config_path = f"{DEV_DIR}/config_optuna_{test_name}.json"
test_marker_path = f"{DEV_DIR}/test_evaluated_{test_name}.json"
if OPTS["smoke"]:
    plot_path = plot_path.rstrip("/") + "_smoke/"

os.makedirs(plot_path, exist_ok=True)
for subdir in ["training", "results", "scores", "variables", "comparison", "kFold"]:
    os.makedirs(os.path.join(plot_path, subdir), exist_ok=True)
    shutil.copy("../index.php", os.path.join(plot_path, subdir))
os.makedirs("models", exist_ok=True)
os.makedirs(DEV_DIR, exist_ok=True)
os.makedirs("roc", exist_ok=True)

signal_file_name = f"{data_directory}signal_{era}_skim_{signal_subset}.root"
bkg_file_name = f"{data_directory}background_{era}_skim_{background_subset}.root"
mass_var_name = "diMuon_bsConstrainedMass" if USE_BSCONSTRAIN else "diMuon_mass"


# ---------------------------------------------------------------------------
# Data loading (physics selections, weights, feature handling as before)
# ---------------------------------------------------------------------------
def load_training_data(need_folds):
    #Read the skim files
    print("[INFO]: Creating data frames")
    print(f"[INFO] Signal File Name: {signal_file_name}")
    print(f"[INFO] Background File Name: {bkg_file_name}")
    with uproot.open(signal_file_name) as file:
        df_signal = pd.DataFrame(file["tree_output"].arrays([var[0] for var in variables], library="np"))
    with uproot.open(bkg_file_name) as file:
        df_bkg = pd.DataFrame(file["tree_output"].arrays([var[0] for var in variables], library="np"))

    print(df_signal)
    print(df_bkg)
    # NaN out dijet/leading-jet variables that lib/CreateTuple.h could only pad
    # (n_jet < 2 / n_jet < 1) so the BDT does not read the 0/-1 padding as a
    # physical jet system.
    xgb_utils.mask_undefined_jet_features(df_signal)
    xgb_utils.mask_undefined_jet_features(df_bkg)
    print("[INFO]: Data frames created successfully")

    # fold = event % N_FOLDS, read straight off the rows being trained on. Nothing has to be
    # reconstructed: no hadd order, no per-process re-selection, no positional mapping back to
    # the nominal tuples, and no sensitivity to the skim being re-made. Done on every stage so
    # the fold-balance plot below is always drawn; only the stages that actually score by fold
    # (need_folds) treat a missing `event` branch as fatal.
    folds = None
    try:
        events = np.concatenate([kf.read_event_ids(bkg_file_name),
                                 kf.read_event_ids(signal_file_name)])
        if len(events) != len(df_bkg) + len(df_signal):
            raise RuntimeError(
                f"{len(events)} event ids but {len(df_bkg) + len(df_signal)} skim rows")
        folds = kf.fold_of_event(events)
        print(f"[INFO] folds from {kf.EVENT_ID} % {kf.N_FOLDS}: "
              f"{np.bincount(folds, minlength=kf.N_FOLDS).tolist()} rows per fold")
    except RuntimeError:
        if need_folds:
            raise
        print(f"[WARNING] no usable {kf.EVENT_ID} branch in the skims: fold-balance plot "
              "skipped. This stage does not score by fold, so it can still run -- but "
              "`--stage final` will refuse until the skims are re-made with it.")

    bkg_events = df_bkg["weight"][(df_bkg[mass_var_name] > SIGNAL_REGION[0])
                                  & (df_bkg[mass_var_name] < SIGNAL_REGION[1])].sum()
    signal_events = df_signal["weight"][(df_signal[mass_var_name] > SIGNAL_REGION[0])
                                        & (df_signal[mass_var_name] < SIGNAL_REGION[1])].sum()

    ####  weight normalization (signal sum scaled to background sum for training)
    signal_weight_sum = df_signal["weight"].sum()
    bkg_weight_sum = df_bkg["weight"].sum()
    signal_scale = bkg_weight_sum / signal_weight_sum
    df_signal["weight"] = df_signal["weight"] * signal_scale

    print(f"[INFO]: S = {signal_events:.3f}; B = {bkg_events:.3f}; S/sqrt(B) = {signal_events / math.sqrt(bkg_events):.3f}")
    print(f"[INFO]: Signal sample size: {len(df_signal)}")
    print(f"[INFO]: Bkg sample size: {len(df_bkg)}")

    # The feature matrix is read as float32 and the three service columns (mass, relative
    # mass error, weight) as float64, instead of letting `.values` upcast everything to
    # float64. Every FEATURE branch is a >f4 already and preprocess_features / the DMatrix
    # are float32 downstream, so float32 features are exact -- and on ggH it takes the
    # biggest array in the job from 3.9 GB to 2.0 GB. `weight` on the other hand is a >f8
    # in the skim, and w_fit = |weight| / rel_err feeds every weighted metric, so the
    # service columns must NOT be narrowed.
    feature_names = [var[0] for var in variables[:-3]]
    service_names = [var[0] for var in variables[-3:]]   # mass, relative mass error, weight
    n_bkg, n_signal = len(df_bkg), len(df_signal)
    features = np.concatenate([df_bkg[feature_names].to_numpy(dtype=np.float32),
                               df_signal[feature_names].to_numpy(dtype=np.float32)])
    service = np.concatenate([df_bkg[service_names].to_numpy(dtype=np.float64),
                              df_signal[service_names].to_numpy(dtype=np.float64)])
    del df_bkg, df_signal  # ~2 GB of pandas on ggH, not used again
    y = np.concatenate([np.zeros(n_bkg), np.ones(n_signal)]).astype(np.int8)

    ### Apply dimuon mass cut (training region)
    print("len y pred cut:", len(y))
    region = kf.training_region_mask(service[:, 0])
    features, service, y = features[region], service[region], y[region]
    if folds is not None:
        folds = folds[region]
    print("len y post cut:", len(y))

    if OPTS["smoke"]:
        rng = np.random.default_rng(SEED)
        keep = np.sort(rng.choice(len(y), size=int(SMOKE_FRACTION * len(y)), replace=False))
        features, service, y = features[keep], service[keep], y[keep]
        folds = folds[keep] if folds is not None else None
        print(f"[SMOKE] using {len(y)} rows")

    if DRAW_CORRELATIONS:
        xgb_utils.draw_correlation_matrix(signal_file_name, bkg_file_name, variables[:-2], plot_path, test_name)
    if PLOT_INPUT_COMPARISON:
        xgb_utils.plot_input_comparison(features, y, np.absolute(service[:, 2]), variables[:-3],
                                        channel_US, era, plot_path)

    # contiguous copies, as before, so the strided views of `service` can be released
    mass, rel_err = service[:, 0].copy(), service[:, 1].copy()
    w_norm = service[:, 2].copy()  # signal-normalized weight
    del service
    w_phys = w_norm.copy()  # physics weight ("Go back to the normal signal weight")
    w_phys[y == 1] = w_phys[y == 1] / signal_scale

    if USE_WEIGHT and USE_WEIGHT_MASS_RES:
        raise ValueError("USE_WEIGHT and USE_WEIGHT_MASS_RES are mutually exclusive")
    if USE_WEIGHT_MASS_RES:
        print("[Info]: Training with mass_res weights")
        w_fit = np.absolute(w_norm) / rel_err
    elif USE_WEIGHT:
        print("[Info]: Training with regular weights")
        w_fit = np.absolute(w_norm)
    else:
        print("[Info]: Training without weights")
        w_fit = np.ones(len(y))

    if folds is not None:
        # the fold rule hashes an externally assigned event number, so how evenly it splits
        # THIS sample is a property of the data: draw it from the rows about to be trained on
        xgb_utils.plot_fold_balance(y, w_fit, folds, plot_path, test_name, era, kf.N_FOLDS)

    return dict(x=features, y=y, mass=mass, w_fit=w_fit, w_phys=w_phys, w_norm=w_norm,
                signal_events=signal_events, bkg_events=bkg_events, folds=folds)


def report_peak_memory(label):
    """Peak resident set size so far. `--stage dev` on ggH used to grow past the node's
    memory and freeze the whole session with no output at all; these lines say where it
    stands before anything is lost."""
    peak_gb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6  # ru_maxrss is in KB
    print(f"[MEM  ] {label}: peak RSS {peak_gb:.2f} GB")
    return peak_gb


# ---------------------------------------------------------------------------
# Shared reporting
# ---------------------------------------------------------------------------
def report_working_points(y, p, w_phys, mass, name, signal_events, bkg_events):
    """ROC in the signal region with physics weights and the significance / working
    point study. Only ever called on validation-OOF or final-OOF predictions (never
    on the test sample, and never used to move the test-sample-based decisions)."""
    sr = (mass > SIGNAL_REGION[0]) & (mass < SIGNAL_REGION[1])
    fpr, tpr, thr = roc_curve(y[sr], p[sr], sample_weight=w_phys[sr])
    significance, effSignal, effBkg, thresholds = xgb_utils.extrac_information_from_roc_curve(
        fpr, tpr, thr, name, signal_events, bkg_events)
    idx_max = np.argmax(np.array(significance))
    print(f"[INFO]: S = {signal_events:.3f}; B = {bkg_events:.3f}; S/sqrt(B) = {signal_events / math.sqrt(bkg_events):.3f}")
    print(f"[INFO]: Max: Significance = {significance[idx_max]}")
    print(f"[INFO]: Max: Threshold = {thresholds[idx_max]}")
    print(f"[INFO]: Max: Signal Efficiency = {effSignal[idx_max]}")
    print(f"[INFO]: Max: Background Efficiency ={effBkg[idx_max]}")
    for wp in [0.90, 0.80]:
        idx = np.argmin(np.abs(np.array(effSignal) - wp))
        print(f"[INFO]: WP{int(wp * 100)}: Significance = {significance[idx]}")
        print(f"[INFO]: WP{int(wp * 100)}: Threshold = {thresholds[idx]}")
        print(f"[INFO]: WP{int(wp * 100)}: Signal Efficiency = {effSignal[idx]}")
        print(f"[INFO]: WP{int(wp * 100)}: Background Efficiency ={effBkg[idx]}")
    return fpr, tpr


def make_oof_plots(y, p_oof, w_fit, w_phys, mass, in_fold_y, in_fold_p, in_fold_w, tag,
                   eval_name, signal_events, bkg_events, models_for_importance,
                   train_name="in-fold (train)"):
    """ROC (weighted/unweighted), discriminator, sculpting, feature importance and loss
    plots built from the CONCATENATED out-of-fold predictions (not from one fold)."""
    auc = roc_auc_score(y, p_oof)
    auc_w = roc_auc_score(y, p_oof, sample_weight=w_fit)
    print(f"[INFO] {tag}: AUC = {auc:.5f}; weighted AUC = {auc_w:.5f}")
    fpr, tpr = report_working_points(y, p_oof, w_phys, mass, f"{test_name}_{tag}", signal_events, bkg_events)
    xgb_utils.draw_roc_curve(fpr, tpr, f"{tag}_{test_name}", plot_path, era, auc)
    xgb_utils.draw_roc_curve(fpr, tpr, f"weighted_{tag}_{test_name}", plot_path, era, auc_w)
    for scale in ("log", "linear"):
        xgb_utils.plot_discriminator(
            y, p_oof, in_fold_y, in_fold_p, w_phys, in_fold_w, era, plot_path, scale=scale,
            eval_name=eval_name, train_name=train_name, file_tag=f"_{tag}")
    bkg = y == 0
    xgb_utils.plot_BDT_sculpting(p_oof[bkg], mass[bkg], w_phys[bkg], channel_US, era, plot_path,
                                 bdt_divisions=6, tag=tag)
    if models_for_importance:
        xgb_utils.plot_feature_importance_kfold(models_for_importance, variables, f"{tag}_{test_name}", plot_path)
    return dict(auc=auc, auc_w=auc_w)


# ---------------------------------------------------------------------------
# Stage 1-2: development (split, CV, Optuna, freeze)
# ---------------------------------------------------------------------------
def make_standardization_plots(x, folds):
    """Train vs held-out, before and after standardization, for every input.

    Called BEFORE any training so the inputs can be inspected without waiting for the fit.
    Model 0's map is fit_standardizer over the rows whose fold != 0, exactly what
    train_final_kfold computes for it, so this shows the real transformation."""
    if not (PLOT_STANDARDIZATION and DO_STANDARDIZATION):
        return
    tr, ho = np.flatnonzero(folds != 0), np.flatnonzero(folds == 0)
    mean_map, std_map = kf.fit_standardizer(x[tr], names)
    xgb_utils.plot_standardization_check(x[tr], x[ho], names, mean_map, std_map, plot_path, era,
                                         eval_label="held-out fold 0")


def stage_plots():
    """--plots-only: the input and standardization plots, then stop."""
    d = load_training_data(need_folds=True)  # the input comparison is drawn inside
    kf.fold_summary(d["y"], d["w_fit"], d["folds"], label="fold")
    make_standardization_plots(d["x"], d["folds"])
    print(f"[INFO] --plots-only: done, nothing trained. Plots are under {plot_path}")


def stage_dev():
    d = load_training_data(need_folds=False)
    x, y, mass, w_fit, w_phys = d["x"], d["y"], d["mass"], d["w_fit"], d["w_phys"]
    print(f"[INFO] development input: {len(y)} rows x {x.shape[1]} features ({x.dtype}), "
          f"{x.nbytes / 1e9:.2f} GB")
    report_peak_memory("after load_training_data")

    # Stage 1: independent test sample (stratified by class; deterministic in SEED, so
    # --stage test recomputes exactly this split rather than reading it back from disk)
    dev_idx, test_idx = kf.split_dev_test(y, TEST_FRACTION, SEED)
    print(f"[INFO] development sample: {len(dev_idx)} events; untouched test sample: {len(test_idx)} events "
          "(NOT used below)")

    # Stage 2: CV inside the development sample
    x_dev, y_dev, w_dev, wp_dev, m_dev = x[dev_idx], y[dev_idx], w_fit[dev_idx], w_phys[dev_idx], mass[dev_idx]
    folds = kf.cv_fold_indices(y_dev, SEED)
    fold_of_row = np.empty(len(y_dev), dtype=np.int8)
    for k, (_, va) in enumerate(folds):
        fold_of_row[va] = k
    kf.fold_summary(y_dev, w_dev, fold_of_row, label="CV validation fold")
    cv_data = kf.prepare_cv_data(x_dev, y_dev, w_dev, folds, names, DO_STANDARDIZATION)
    report_peak_memory("after prepare_cv_data")

    device = OPTS["device"]
    max_estimators = SMOKE_ROUNDS if OPTS["smoke"] else MAX_ESTIMATORS
    esr = min(EARLY_STOPPING_ROUNDS, 5) if OPTS["smoke"] else EARLY_STOPPING_ROUNDS
    n_trials = OPTS["optuna_trials"] or (SMOKE_TRIALS if OPTS["smoke"] else N_OPTUNA_TRIALS)
    optimization_plot_path = f"optunaPlots/{channel_US}{file_append}/{test_name}/"
    os.makedirs(optimization_plot_path, exist_ok=True)
    study = kf.run_optuna_cv(cv_data, n_trials, SEED, device, max_estimators, esr,
                             monitor_max_rows=MONITOR_MAX_ROWS,
                             progress_every=PROGRESS_EVERY)
    report_peak_memory("after the Optuna study")
    print("Best mean weighted validation AUC:", study.best_value)
    print("Best parameters:", study.best_params)
    try:
        import optuna.visualization as vis
        vis.plot_optimization_history(study).write_html(optimization_plot_path + "optimization_history.html")
        vis.plot_param_importances(study).write_html(optimization_plot_path + "param_importance.html")
        vis.plot_slice(study, params=["max_depth", "learning_rate", "min_child_weight", "subsample",
                                      "colsample_bytree", "reg_lambda", "reg_alpha"]
                       ).write_html(optimization_plot_path + "optuna_slice.html")
    except Exception as e:  # plotly/kaleido optional
        print(f"[WARNING] Optuna plots skipped: {e}")
    params = kf.base_xgb_params(device)
    params.update(study.best_params)
    best_iters = study.best_trial.user_attrs["fold_best_iteration"]
    n_rounds = kf.choose_n_rounds(best_iters, N_ROUNDS_SCALE)
    source = "optuna"

    # Re-run the frozen parameters once: per-fold validation metrics, best iterations,
    # models and the validation ("dev OOF") predictions used for the dev-stage plots.
    cv = kf.cross_validate_config(cv_data, params, max_estimators, esr, keep_models=True,
                                  progress_every=PROGRESS_EVERY, monitor_max_rows=MONITOR_MAX_ROWS)
    infos = cv["infos"]
    report_peak_memory("after the frozen-configuration CV")
    it_summary = kf.summarize_best_iterations([i["best_iteration"] for i in infos])
    print("[INFO] per-fold weighted validation AUC:", [round(i["auc_w"], 5) for i in infos])
    print(f"[INFO] mean weighted validation AUC = {cv['mean_auc_w']:.5f} +/- {cv['std_auc_w']:.5f}")
    print("[INFO] per-fold weighted validation logloss:", [round(i["logloss_w"], 5) for i in infos])
    print(f"[INFO] best iterations per fold: {it_summary['best_iterations']} "
          f"(mean {it_summary['mean']:.1f}, median {it_summary['median']:.1f})")
    print(f"[INFO] final boosting rounds ({source}): {n_rounds} = median(best_iter+1) * {N_ROUNDS_SCALE}")

    config = dict(source=source, params=kf.jsonable_params(params), n_rounds=int(n_rounds),
                  n_folds=kf.N_FOLDS, seed=SEED, test_fraction=TEST_FRACTION,
                  n_rounds_policy=f"median(best_iteration+1) over the CV folds * {N_ROUNDS_SCALE}",
                  cv=dict(mean_auc_w=cv["mean_auc_w"], std_auc_w=cv["std_auc_w"],
                          best_iterations=it_summary,
                          fold_auc_w=[i["auc_w"] for i in infos], fold_logloss_w=[i["logloss_w"] for i in infos],
                          fold_auc=[i["auc"] for i in infos], fold_logloss=[i["logloss"] for i in infos]),
                  training_weights="mass_res" if USE_WEIGHT_MASS_RES else ("weight" if USE_WEIGHT else "none"),
                  standardization=DO_STANDARDIZATION, variables=names, smoke=OPTS["smoke"])
    kf.save_frozen_config(optuna_config_path, config)
    print(f"[INFO] Optuna configuration written to {optuna_config_path}")
    print("[INFO] it is NOT used by --stage test/final unless you pass --use-optuna; "
          "DEFAULT_PARAMS in train.py stay the default")

    # save the five dev CV models (used by --stage test and compare_scoring_schemes.py)
    members = [dict(model=m, fold=i["fold"], mean_map=fd["mean_map"], std_map=fd["std_map"],
                    n_trees=i["n_trees_used"], n_train=i["n_train"],
                    heldout_metrics={k: i[k] for k in ("auc_w", "auc", "logloss_w", "logloss")})
               for m, i, fd in zip(cv["models"], infos, cv_data)]
    kf.save_fold_models(members, f"{test_name}_devcv", USE_BSCONSTRAIN, names, DO_STANDARDIZATION,
                        params, SEED, models_dir=DEV_DIR)

    # ---- dev-stage plots from the concatenated validation (dev OOF) predictions
    p_oof = np.empty(len(y_dev))
    for fd, p in zip(cv_data, cv["preds"]):
        p_oof[fd["va_idx"]] = p
    in_y, in_p, in_w = [], [], []
    for fd, m, i in zip(cv_data, cv["models"], infos):
        # rebuilt one fold at a time: cv_data no longer carries the matrices
        mats = kf.fold_matrices(fd)
        in_y.append(mats["y_tr"])
        in_p.append(kf.predict_model(m, mats["x_tr"], i["n_trees_used"]))
        in_w.append(wp_dev[fd["tr_idx"]] / (kf.N_FOLDS - 1))  # each event is in train of K-1 models
        del mats
    make_oof_plots(y_dev, p_oof, w_dev, wp_dev, m_dev, np.concatenate(in_y), np.concatenate(in_p),
                   np.concatenate(in_w), "devCV", "validation (dev CV OOF)", d["signal_events"], d["bkg_events"],
                   cv["models"])
    xgb_utils.plot_kfold_summary(infos, plot_path, test_name, era)
    xgb_utils.plot_fold_loss_curves(infos, plot_path, test_name, era, second_label="validation")
    with open(f"{plot_path}results/kfold_dev_{test_name}.json", "w") as f:
        json.dump(dict(config=config, folds=[{k: v for k, v in i.items() if not isinstance(v, list)} for i in infos]),
                  f, indent=2, default=float)
    print("[INFO] Stage 1-2 done. Inspect the CV results, then run `--stage test` ONCE, then `--stage final`.")


# ---------------------------------------------------------------------------
# Stage 3: independent test evaluation (once)
# ---------------------------------------------------------------------------
def frozen_config():
    """The configuration the test/final stages train with: the Optuna result only when
    --use-optuna is given (and then it must exist), otherwise DEFAULT_PARAMS."""
    ifUseOptimize = OPTS["use_optuna"]
    if not ifUseOptimize:
        print(f"[INFO] using DEFAULT_PARAMS from train.py: {DEFAULT_PARAMS}, "
              f"{DEFAULT_N_ROUNDS} rounds (pass --use-optuna to use an Optuna result instead)")
        return kf.make_config(OPTS["device"], DEFAULT_PARAMS, DEFAULT_N_ROUNDS, "default_fixed")
    if not os.path.exists(optuna_config_path):
        sys.exit(f"[ERROR] --use-optuna given but {optuna_config_path} does not exist: run "
                 "`--stage dev` first, or `git pull` the committed config.")
    config = kf.load_frozen_config(optuna_config_path)
    print(f"[INFO] using the Optuna configuration {optuna_config_path}: {config['params']}, "
          f"{config['n_rounds']} rounds")
    return config


def stage_test():
    kf.guard_test_evaluation(test_marker_path, OPTS["force_retest"])
    config = frozen_config()
    d = load_training_data(need_folds=False)
    x, y, mass, w_fit, w_phys = d["x"], d["y"], d["mass"], d["w_fit"], d["w_phys"]
    dev_idx, test_idx = kf.split_dev_test(y, TEST_FRACTION, SEED)  # same seed -> same split as --stage dev
    dev_bundle = kf.load_fold_bundle(f"{test_name}_devcv", USE_BSCONSTRAIN, DEV_DIR)

    res = kf.evaluate_on_test(x, y, w_fit, dev_idx, test_idx, names, DO_STANDARDIZATION, config,
                              OPTS["device"], dev_bundle)
    cv = config.get("cv")  # only an Optuna config carries the CV summary
    print("\n[TEST] ===== independent test sample (evaluated once) =====")
    print(f"[TEST] refit on full dev sample, {config['n_rounds']} rounds:")
    for k in ("auc_w", "auc", "logloss_w", "logloss"):
        print(f"[TEST]   {k:10s} = {res['refit'][k]:.5f}")
    if cv:
        print(f"[CV  ] cross-validation:   weighted AUC = {cv['mean_auc_w']:.5f} +/- {cv['std_auc_w']:.5f}; "
              f"weighted logloss = {np.mean(cv['fold_logloss_w']):.5f}; AUC = {np.mean(cv['fold_auc']):.5f}")
    else:
        print(f"[CV  ] cross-validation numbers: see {plot_path}results/kfold_dev_{test_name}.json")
    for r in res["cv_models_on_test"]:
        print(f"[TEST]   dev CV model {r['fold']}: weighted AUC = {r['auc_w']:.5f}, AUC = {r['auc']:.5f}, "
              f"weighted logloss = {r['logloss_w']:.5f}")
    out = dict(refit=res["refit"], cv=cv, cv_models_on_test=[{k: v for k, v in r.items() if k != "p_test"}
                                                             for r in res["cv_models_on_test"]],
               n_test=int(len(test_idx)), config_source=config["source"])
    with open(f"{plot_path}results/test_evaluation_{test_name}.json", "w") as f:
        json.dump(out, f, indent=2, default=float)
    with open(test_marker_path, "w") as f:
        json.dump(dict(evaluated=True, refit=res["refit"]), f)
    # test-sample ROC (reporting only)
    fpr, tpr, _ = roc_curve(y[test_idx], res["p_test"], sample_weight=w_fit[test_idx])
    xgb_utils.draw_roc_curve(fpr, tpr, f"test_{test_name}", plot_path, era, res["refit"]["auc_w"])

    print("[TEST] The test sample must not be used to change the model, features, rounds or working points.")


# ---------------------------------------------------------------------------
# Stage 4: final K-fold analysis models with OOF predictions
# ---------------------------------------------------------------------------
def stage_final():
    config = frozen_config()
    n_rounds = SMOKE_ROUNDS if OPTS["smoke"] else int(config["n_rounds"])
    params = kf.params_from_config(config, OPTS["device"])

    d = load_training_data(need_folds=True)
    x, y, mass, w_fit, w_phys, folds = d["x"], d["y"], d["mass"], d["w_fit"], d["w_phys"], d["folds"]
    kf.fold_summary(y, w_fit, folds, label="final fold")
    make_standardization_plots(x, folds)

    def save_model_now(member):
        # saved as soon as it is trained (BEFORE any plotting helper touches the booster)
        kf.save_fold_models([member], test_name, USE_BSCONSTRAIN, names, DO_STANDARDIZATION, params,
                            SEED, extra_meta=dict(config_source=config["source"]))
        print(f"[INFO] saved fold model {member['fold']} to models/", flush=True)

    members, oof, p_in_fold = kf.train_final_kfold(x, y, w_fit, folds, names, DO_STANDARDIZATION, params,
                                                   n_rounds, progress_every=PROGRESS_EVERY,
                                                   monitor_max_rows=MONITOR_MAX_ROWS,
                                                   in_fold_max_rows=IN_FOLD_PLOT_MAX_ROWS,
                                                   on_model_done=save_model_now)
    print(f"[INFO] saved {kf.N_FOLDS} fold models: models/model_{test_name}_fold<k>{'_bsC' if USE_BSCONSTRAIN else ''}.{{pkl,json}}")

    in_y = np.concatenate([y[m["idx"]] for m in p_in_fold])
    in_p = np.concatenate([m["p"] for m in p_in_fold])
    in_w = np.concatenate([w_phys[m["idx"]] / (kf.N_FOLDS - 1) for m in p_in_fold])
    summary = make_oof_plots(y, oof, w_fit, w_phys, mass, in_y, in_p, in_w, "OOF", "OOF (held-out fold)",
                             d["signal_events"], d["bkg_events"], [m["model"] for m in members])
    # per-model views of the same OOF scores: each model on the fold it held out
    xgb_utils.plot_roc_per_fold(y, oof, folds, w_fit, era, plot_path, test_name)
    xgb_utils.plot_discriminator_per_fold(y, oof, folds, w_phys, era, plot_path, test_name)

    per_fold = [dict(fold=m["fold"], **m["heldout_metrics"]) for m in members]
    print("[INFO] per-fold held-out (OOF) weighted AUC:", [round(r["auc_w"], 5) for r in per_fold])
    aucs = np.array([r["auc_w"] for r in per_fold])
    print(f"[INFO] mean +/- std over folds: {aucs.mean():.5f} +/- {aucs.std():.5f}")
    if PLOT_LOSS:
        xgb_utils.plot_fold_loss_curves(members, plot_path, test_name, era,
                                        second_label="held-out fold (monitoring only)")
    try:
        xgb_utils.plot_xgb_tree(members[0]["model"], variables, f"{test_name}_fold0", plot_path)
    except Exception as e:  # graphviz is optional
        print(f"[WARNING] tree plot skipped: {e}")
    with open(f"{plot_path}results/kfold_final_{test_name}.json", "w") as f:
        json.dump(dict(oof=summary, folds=per_fold, n_rounds=n_rounds, config_source=config["source"]),
                  f, indent=2, default=float)
    np.savez(f"models/oof_{test_name}.npz", oof=oof, y=y, fold=folds, mass=mass, w_phys=w_phys)


# ---------------------------------------------------------------------------
# Apply: fold-matched scoring of the tuples
# ---------------------------------------------------------------------------
def stage_legacy():
    """The pre-K-fold approach, reproduced for an A/B against K-fold.

    One unstratified 60/40 split (the original seed and fractions), one model trained on the
    60%, then both approaches evaluated on the IDENTICAL 40% -- where both are out-of-sample,
    so the only difference left is that the legacy model saw 60% of the data and each K-fold
    model 80%. Finally the legacy model scores the tuples into a separate tree.
    """
    config = frozen_config()
    n_rounds = SMOKE_ROUNDS if OPTS["smoke"] else int(config["n_rounds"])
    params = kf.params_from_config(config, OPTS["device"])

    d = load_training_data(need_folds=True)
    x, y, mass, w_fit, w_phys, folds = d["x"], d["y"], d["mass"], d["w_fit"], d["w_phys"], d["folds"]

    train_idx, test_idx = kf.legacy_split(len(y), LEGACY_TEST_FRACTION, LEGACY_SEED)
    print(f"[INFO] legacy split (seed {LEGACY_SEED}, unstratified): {len(train_idx)} train / "
          f"{len(test_idx)} test ({len(test_idx) / len(y):.1%})")

    member, p_legacy, in_fold = kf.train_single_model(
        x, y, w_fit, train_idx, test_idx, names, DO_STANDARDIZATION, params, n_rounds,
        progress_every=PROGRESS_EVERY, monitor_max_rows=MONITOR_MAX_ROWS,
        in_fold_max_rows=IN_FOLD_PLOT_MAX_ROWS)
    kf.save_fold_models([member], f"{test_name}_legacy", USE_BSCONSTRAIN, names, DO_STANDARDIZATION,
                        params, LEGACY_SEED, n_folds=1,
                        extra_meta=dict(config_source=config["source"], legacy_split=True))
    print(f"[INFO] saved the legacy model: models/model_{test_name}_legacy_fold0"
          f"{'_bsC' if USE_BSCONSTRAIN else ''}.{{pkl,json}}")

    # the K-fold OOF prediction for those same events: each scored by the model that excluded it
    try:
        bundle = kf.load_fold_bundle(test_name, USE_BSCONSTRAIN)
    except FileNotFoundError:
        sys.exit(f"[ERROR] no K-fold models for {test_name}: run `--stage final` first, "
                 "otherwise there is nothing to compare against.")
    p_kfold = kf.predict_by_fold(x[test_idx], folds[test_idx], bundle)

    m_legacy = kf.weighted_metrics(y[test_idx], p_legacy, w_fit[test_idx])
    m_kfold = kf.weighted_metrics(y[test_idx], p_kfold, w_fit[test_idx])
    print(f"\n[COMPARE] ===== both approaches on the identical {len(test_idx)} test events =====")
    print(f"[COMPARE] {'metric':12s} {'no k-fold 60/40':>16s} {'K-fold OOF':>14s}")
    for k in ("auc_w", "auc", "logloss_w", "logloss"):
        print(f"[COMPARE] {k:12s} {m_legacy[k]:16.5f} {m_kfold[k]:14.5f}")
    print("[COMPARE] both are out-of-sample for these events; the no-k-fold model trained on "
          f"{len(train_idx)} events, each K-fold model on ~{int(0.8 * len(y))}.")

    # the standard plot set for the single model: ROC, discriminator, sculpting, importances,
    # working points (tagged noKfold so nothing collides with the K-fold versions)
    make_oof_plots(y[test_idx], p_legacy, w_fit[test_idx], w_phys[test_idx], mass[test_idx],
                   y[in_fold["idx"]], in_fold["p"], w_phys[in_fold["idx"]], "noKfold",
                   "no k-fold (held-out 40%)", d["signal_events"], d["bkg_events"],
                   [member["model"]], train_name="no k-fold (train 60%)")
    if PLOT_LOSS:
        # the pre-K-fold loss plot: a single Train/Test pair, no per-fold curves, since
        # there is only one model here
        xgb_utils.plot_loss(member["val_logloss"], member["train_logloss"],
                            f"{test_name}_noKfold", plot_path, era)
    # the K-fold OOF working points on the same 40%, for the numbers (its own plots come
    # from --stage final, over all MC)
    report_working_points(y[test_idx], p_kfold, w_phys[test_idx], mass[test_idx],
                          f"{test_name}_kfoldOOF", d["signal_events"], d["bkg_events"])
    xgb_utils.plot_legacy_vs_kfold(y[test_idx], w_phys[test_idx], p_legacy, p_kfold,
                                   m_legacy["auc_w"], m_kfold["auc_w"], era, plot_path)

    # log loss vs boosting round for both approaches. --stage final writes no per-round
    # arrays (save_fold_models stores only the final-round scalars), so the K-fold curves
    # are recomputed here by truncating each SAVED booster to r trees -- nothing is
    # retrained. Both out-of-sample curves land on the same held-out 40%.
    loss_curves = None
    if PLOT_LOSS:
        # Weighted log loss vs boosting round. --stage final writes no per-round arrays, so
        # EVERY curve here is recomputed by truncating a model to r trees -- one code path,
        # one subsampling rule, one round grid, so the curves are comparable by construction.
        #
        # Pools are matched: all out-of-sample curves on the held-out 40% (test_idx), all
        # in-sample curves on the SAME subsample S60 of the train 60%. Because the in-sample
        # curves share rows, the differences between them are a PAIRED measurement and the
        # subsampling noise largely cancels.
        rounds = kf.round_grid(n_rounds, LOSS_CURVE_ROUND_STEP)
        s60 = kf.subsample_rows(train_idx, LOSS_CURVE_MAX_ROWS, LOSS_CURVE_SEED)
        legacy_member = kf.as_member(member, names, DO_STANDARDIZATION)
        print(f"[INFO] recomputing the loss curves at {len(rounds)} tree counts (every "
              f"{LOSS_CURVE_ROUND_STEP} rounds); in-sample on {len(s60)} shared events of the "
              f"train 60%, out-of-sample on the held-out 40%", flush=True)

        leg_in, n_leg_in, neff_leg_in = kf.curve_on_rows(
            legacy_member, x, y, w_fit, s60, rounds, label="no k-fold @60% in-sample")
        leg_out, n_leg_out, neff_leg_out = kf.curve_on_rows(
            legacy_member, x, y, w_fit, test_idx, rounds, label="no k-fold @60% out-of-sample")
        cv = kf.kfold_logloss_curves(bundle, x, y, w_fit, folds, oof_idx=test_idx,
                                     in_fold_idx=s60, rounds=rounds,
                                     max_rows=LOSS_CURVE_MAX_ROWS, seed=LOSS_CURVE_SEED)

        # the control: same trainer, same params, same rounds, 80% of the events -- exactly
        # the per-model training size of a K-fold model. Diagnostic only, never saved.
        ctrl_curve = control = ctrl_member = None
        if OPTS["control_80"]:
            ctrl_train_idx, ctrl_test_idx = kf.legacy_split(len(y), CONTROL_TEST_FRACTION,
                                                            LEGACY_SEED)
            # These hold because sklearn's ShuffleSplit draws ONE permutation per seed and
            # both partitions are exhaustive, so a smaller test fraction gives a strictly
            # larger train set carved from the same ordering. If a future sklearn changes
            # that, the control silently stops being a control -- fail loudly instead.
            assert np.setdiff1d(train_idx, ctrl_train_idx).size == 0, \
                "the legacy 60% train set is not nested inside the control's 80%"
            assert np.setdiff1d(ctrl_test_idx, test_idx).size == 0, \
                "the control's held-out set is not inside the legacy held-out 40%"
            assert np.intersect1d(ctrl_test_idx, ctrl_train_idx).size == 0
            # NOT test_idx: at this seed the control trains on half of test_idx, so passing
            # it as eval_idx would make train_single_model report a "held-out" metric that is
            # 50% in-sample. The control's own held-out set is the only clean choice.
            print(f"\n[CONTROL] training one single-split model on {len(ctrl_train_idx)} events "
                  f"(80%) -- the K-fold per-model training size -- to isolate training-set size",
                  flush=True)
            bundle_params = bundle[0]["meta"].get("params", {})
            if bundle_params.get("device") != params.get("device"):
                print(f"[WARNING] the saved fold models were trained with device="
                      f"{bundle_params.get('device')!r} but this run uses "
                      f"{params.get('device')!r}. GPU and CPU 'hist' build different trees, so "
                      "the control would differ from the fold models by BACKEND as well as by "
                      "training-set size. Re-run with a matching --device for a clean answer.")
            control, _, _ = kf.train_single_model(
                x, y, w_fit, ctrl_train_idx, ctrl_test_idx, names, DO_STANDARDIZATION, params,
                n_rounds, progress_every=PROGRESS_EVERY, monitor_max_rows=MONITOR_MAX_ROWS,
                in_fold_max_rows=IN_FOLD_PLOT_MAX_ROWS)
            ctrl_member = kf.as_member(control, names, DO_STANDARDIZATION)
            ctrl_curve, n_ctrl, neff_ctrl = kf.curve_on_rows(
                ctrl_member, x, y, w_fit, s60, rounds, label="no k-fold @80% in-sample")

        end_oof = float(cv["oof"][:, -1].mean())
        end_in = float(cv["in_fold"][:, -1].mean())
        sem_in = float(cv["in_fold"][:, -1].std() / np.sqrt(cv["in_fold"].shape[0]))
        print(f"\n[COMPARE] ===== final-round weighted log loss (round {int(rounds[-1])}) =====")
        print(f"[COMPARE] {'curve':34s} {'in-sample':>11s} {'out-of-sample':>14s}")
        print(f"[COMPARE] {'no k-fold @60% train':34s} {leg_in[-1]:11.5f} {leg_out[-1]:14.5f}")
        print(f"[COMPARE] {'K-fold @80% train (mean of 5)':34s} {end_in:11.5f} {end_oof:14.5f}")
        print(f"[COMPARE] generalization gap: no k-fold {leg_out[-1] - leg_in[-1]:.5f}, "
              f"K-fold {end_oof - end_in:.5f}")
        print(f"[CHECK  ] recomputed K-fold OOF endpoint {end_oof:.5f} vs the [COMPARE] table's "
              f"{m_kfold['logloss_w']:.5f} (different subsets: agreement to statistics)")

        verdict, frac, paired = None, None, None
        if ctrl_curve is not None:
            # PAIRED test. The unpaired per-fold spread (std of the in-fold endpoints) is
            # dominated by evaluation-subsample noise, not by model-to-model variation: with
            # N_eff ~ 10k it is itself ~0.004, so an unpaired tolerance is WIDER than the
            # ~0.007 effect and cannot settle the question. Comparing per-event losses on
            # IDENTICAL rows makes the large event-to-event spread cancel in the difference.
            offs, resids, o_ses, r_ses = [], [], [], []
            for mem_k in bundle:
                k = int(mem_k["fold"])
                rows = s60[folds[s60] != k]          # in-sample for ALL THREE models
                wk = w_fit[rows]
                l_leg = kf.per_event_logloss(legacy_member, x[rows], y[rows])
                l_ctl = kf.per_event_logloss(ctrl_member, x[rows], y[rows])
                l_kf = kf.per_event_logloss(mem_k, x[rows], y[rows])
                o, o_se, _ = kf.weighted_mean_and_error(l_kf - l_leg, wk)   # offset to explain
                r, r_se, _ = kf.weighted_mean_and_error(l_kf - l_ctl, wk)   # residual
                offs.append(o); resids.append(r); o_ses.append(o_se); r_ses.append(r_se)
            offset = float(np.mean(offs))
            residual = float(np.mean(resids))
            # measurement error of the mean residual, plus genuine fold-to-fold spread
            sigma = float(np.sqrt(np.mean(np.square(r_ses)) / len(resids)
                                  + np.var(resids, ddof=1) / len(resids)))
            frac = float(1 - residual / offset) if abs(offset) > 1e-9 else None
            frac_err = abs(sigma / offset) if abs(offset) > 1e-9 else None

            print(f"\n[CONTROL] ===== does training-set size explain the in-fold offset? =====")
            print(f"[CONTROL] no k-fold @60% trains on {len(train_idx)}, "
                  f"control @80% on {len(ctrl_train_idx)}, each K-fold model on "
                  f"~{int((1 - 1 / kf.N_FOLDS) * len(y))}")
            print(f"[CONTROL] all three scored on the SAME rows, paired per event:")
            print(f"[CONTROL]   offset   (K-fold - no k-fold@60) = {offset:+.5f}")
            print(f"[CONTROL]   residual (K-fold - control@80)   = {residual:+.5f} +/- {sigma:.5f}")
            if frac is None:
                verdict = "no offset"
                print("[CONTROL] there is no in-sample offset to explain.")
            else:
                verdict = ("confirmed" if abs(residual) < 3 * sigma or frac >= 0.8 else
                           "refuted" if frac <= 0.2 else "partial")
                print(f"[CONTROL]   fraction explained by size = {100 * frac:.0f}% "
                      f"+/- {100 * frac_err:.0f}%")
                print(f"[CONTROL] VERDICT: {verdict.upper()}")
                if verdict == "confirmed":
                    print("[CONTROL] a single-split model trained on the SAME number of events "
                          "as a K-fold model reproduces the K-fold in-fold loss. The offset is "
                          "training-set size at fixed capacity -- more data, less memorization, "
                          "higher in-sample loss. Not a bug.")
                elif verdict == "refuted":
                    print("[CONTROL] training-set size does NOT explain the offset -- re-examine "
                          "the in-fold slice and the fold routing.")
                else:
                    print("[CONTROL] size explains part of it; the residual exceeds 3 sigma. The "
                          "control and the K-fold models train on different 80% subsets, which "
                          "accounts for some but evidently not all of it.")
            print(f"[CHECK  ] unpaired per-fold endpoint spread is {cv['in_fold'][:, -1].std():.5f} "
                  f"-- comparable to the offset itself, which is why this test is paired "
                  f"(paired error {sigma:.5f}, {cv['in_fold'][:, -1].std() / max(sigma, 1e-12):.0f}x smaller)")
            paired = dict(offset=offset, residual=residual, sigma=sigma,
                          fraction_explained=frac, fraction_error=frac_err,
                          per_fold_offset=offs, per_fold_residual=resids,
                          method=("per-event log losses differenced on identical rows, then "
                                  "weighted-averaged; error = sum(w^2 (v-m)^2)^0.5 / sum(w) "
                                  "combined with the fold-to-fold spread"))

        neff = float(np.mean(cv["n_eff_oof"]))
        xgb_utils.plot_loss_noKfold_vs_kfold(
            rounds, leg_in, leg_out, cv["in_fold"], cv["oof"], era, plot_path,
            control=ctrl_curve,
            n_eff_note=(f"in-sample curves share {len(s60)} events of the train 60% "
                        f"(paired); OOF N_eff ~ {neff:.0f}"))

        loss_curves = dict(
            rounds=[int(r) for r in rounds],
            weight="w_fit -- the same vector the models were trained with",
            method=("every curve recomputed with kf.logloss_vs_rounds by truncating a model to "
                    "r trees; no XGBoost evals_result monitors are used, so all curves share "
                    "one subsampling rule and one round grid"),
            legacy_train=list(leg_in), legacy_heldout=list(leg_out),
            control_80_train=(list(ctrl_curve) if ctrl_curve is not None else None),
            kfold_in_fold=dict(per_fold=cv["in_fold"].tolist(),
                               mean=cv["in_fold"].mean(axis=0).tolist(),
                               std=cv["in_fold"].std(axis=0).tolist()),
            kfold_oof=dict(per_fold=cv["oof"].tolist(), mean=cv["oof"].mean(axis=0).tolist(),
                           std=cv["oof"].std(axis=0).tolist()),
            provenance=dict(max_rows=LOSS_CURVE_MAX_ROWS, round_step=LOSS_CURVE_ROUND_STEP,
                            seed=LOSS_CURVE_SEED, n_shared_in_sample_rows=int(len(s60)),
                            n_rows_legacy_train=n_leg_in, n_eff_legacy_train=neff_leg_in,
                            n_rows_legacy_heldout=n_leg_out, n_eff_legacy_heldout=neff_leg_out,
                            n_rows_oof=cv["n_rows_oof"], n_rows_in_fold=cv["n_rows_in_fold"],
                            n_eff_oof=cv["n_eff_oof"], n_eff_in_fold=cv["n_eff_in_fold"],
                            n_rows_control=(n_ctrl if ctrl_curve is not None else None),
                            n_eff_control=(neff_ctrl if ctrl_curve is not None else None)),
            event_sets=dict(
                legacy_train="shared subsample S60 of the train 60% (train_idx)",
                legacy_heldout="the held-out 40% (test_idx)",
                kfold_in_fold="the part of that same S60 each model trained on (fold != k)",
                kfold_oof="test_idx events whose fold the scoring model excluded",
                control_80_train=("the same S60; the control's 80% train set is a superset of "
                                  "train_idx at a fixed seed, so S60 is in-sample for it too")),
            control=(dict(test_fraction=CONTROL_TEST_FRACTION,
                          n_train=int(len(ctrl_train_idx)),
                          kfold_n_train_per_model=int((1 - 1 / kf.N_FOLDS) * len(y)),
                          endpoint=float(ctrl_curve[-1]), kfold_in_fold_endpoint=end_in,
                          no_kfold_in_sample_endpoint=float(leg_in[-1]),
                          kfold_in_fold_sem=sem_in, verdict=verdict,
                          fraction_of_offset_explained_by_size=frac, paired_test=paired,
                          question=("does training-set size alone explain the K-fold in-fold "
                                    "loss sitting above the no-k-fold train loss?"))
                     if ctrl_curve is not None else None),
            crosscheck=dict(
                kfold_heldout_logloss_w_from_stage_final=[
                    b["meta"]["heldout_metrics"]["logloss_w"] for b in bundle],
                note=("the stage-final values are over each model's FULL held-out fold (all "
                      "MC); the curve endpoints are over the held-out 40% only, so they agree "
                      "to statistics, not exactly")),
            note=("in-sample and out-of-sample curves are on different pools by necessity (the "
                  "no-k-fold model has no training events inside its held-out 40%), but WITHIN "
                  "each of those two pools every model is evaluated on the same events, so "
                  "both the in-sample comparison and the out-of-sample comparison are "
                  "like-for-like"))

    os.makedirs(f"{plot_path}comparison/", exist_ok=True)
    with open(f"{plot_path}comparison/legacy_vs_kfold_{test_name}.json", "w") as f:
        json.dump(dict(n_test=int(len(test_idx)), n_legacy_train=int(len(train_idx)),
                       legacy=m_legacy, kfold_oof=m_kfold, n_rounds=n_rounds,
                       config_source=config["source"],
                       legacy_split=dict(seed=LEGACY_SEED, test_fraction=LEGACY_TEST_FRACTION,
                                         stratified=False),
                       loss_curves=loss_curves,
                       caveat=("legacy MC scores over the full sample are in-sample for the 60% "
                               "the model trained on and are optimistically biased; only these "
                               "numbers, on the held-out 40%, are a fair comparison")),
                  f, indent=2, default=float)

    if APPEND_VARIABLES:
        print("\n[INFO] scoring the tuples with the legacy model -> BDT_score/"
              f"{channel_US}legacy/  (NOT fold-matched: in-sample for 60% of the MC)")
        legacy_bundle = kf.load_fold_bundle(f"{test_name}_legacy", USE_BSCONSTRAIN)
        for file_type in ["Data", "DY", "EWK", "TT", "DiBoson", "ggH", "VBF"]:
            xgb_utils.append_BDT_score(
                file_type, channel_US, era, signal_subset, background_subset, variables[:-3],
                legacy_bundle, USE_BSCONSTRAIN, useRecategorization, legacy=True)
        print(f"[INFO] next: `bash scripts/hadd_bdt.sh {channel_US} legacy` then "
              f"`python3 plot_BDT_Categories.py {channel_US} {era} legacy`")


def stage_apply():
    bundle = kf.load_fold_bundle(test_name, USE_BSCONSTRAIN)
    print(f"[INFO] loaded {len(bundle)} fold models; scoring rule: event in fold i -> model i, "
          f"with fold = {kf.EVENT_ID} % n_folds (identical for MC, Data and the systematics)")
    if not APPEND_VARIABLES:
        print("[INFO]: BDT score was not added to the trees")
        return
    print("[INFO]: Adding BDT score to the nominal tuples")
    for file_type in ["Data", "DY", "EWK", "TT", "DiBoson", "ggH", "VBF"]:
        xgb_utils.append_BDT_score(
            file_type, channel_US, era, signal_subset, background_subset, variables[:-3], bundle,
            USE_BSCONSTRAIN, useRecategorization)
    if doSystematics:
        # possible only because the fold is a property of the event: a varied event keeps the
        # fold -- and therefore the out-of-fold model -- of its nominal self
        print("[INFO]: Adding fold-matched BDT scores to the systematic tuples")
        for file_type in ["DY", "EWK", "TT", "DiBoson", "ggH", "VBF"]:  # no Data variations
            xgb_utils.append_BDT_score_to_sys(
                file_type, channel_US, era, signal_subset, background_subset, variables[:-3],
                bundle, USE_BSCONSTRAIN)


stage = OPTS["stage"]
if OPTS["plots_only"]:
    stage_plots()
elif stage == "dev":
    stage_dev()
elif stage == "test":
    stage_test()
elif stage == "final":
    stage_final()
elif stage == "apply":
    stage_apply()
elif stage == "legacy":
    stage_legacy()
else:  # all: old one-shot behaviour
    stage_final()
    stage_apply()
