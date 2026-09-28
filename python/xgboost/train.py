#!/usr/bin/env python
"""K-fold BDT training for H->mumu.

Usage:
  python3 train.py <channel> <era> [--stage dev|test|final|apply|all|legacy]
                   [--do-systematics] [--use-recategorization]
                   [--bkg-subset Full] [--sig-subset NottH]
                   [--plots-only] [--no-apply] [--use-optuna] [--force-retest] [--smoke]
                   [--device cuda|cpu] [--optuna-trials N]

Stages:
  dev     split off an untouched 20% test sample, run Optuna with 5-fold CV on the other 80%
          and write the best configuration to models/dev/config_optuna_<name>.json
  test    refit on the 80% and evaluate on the untouched test sample -- run it ONCE
  final   train the five analysis models on all MC (model i holds out fold i = event % 5)
          and make the out-of-fold (OOF) plots
  apply   append the fold-matched BDT scores to the nominal (and, with --do-systematics,
          the systematic) tuples
  all     final + apply (default)
  legacy  the pre-K-fold single 60/40 split model, compared with the K-fold models on the
          same held-out 40%, then scored into BDT_score/<channel>legacy/ (needs `final`)

test/final/legacy train with DEFAULT_PARAMS unless --use-optuna is given.
--plots-only draws the input and standardization plots and stops.
--no-apply skips writing scored tuples. --smoke is a quick run on 5% of the events.
"""
import argparse
import json
import math
import os
import resource
import shutil
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd
import uproot
from sklearn.metrics import roc_auc_score, roc_curve

import xgb_kfold as kf
import xgb_utils

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DRAW_CORRELATIONS = False  # slow
PLOT_INPUT_COMPARISON = True  # signal vs background shape of every input
PLOT_STANDARDIZATION = True  # train vs held-out, before and after standardization
DO_STANDARDIZATION = True
USE_WEIGHT = False
USE_WEIGHT_MASS_RES = True  # mutually exclusive with USE_WEIGHT
APPEND_VARIABLES = True
USE_BSCONSTRAIN = True
PLOT_LOSS = True
SEED = 7
TEST_FRACTION = 0.2
SIGNAL_REGION = (121., 129.)

# hyperparameters used unless --use-optuna
DEFAULT_PARAMS = dict(max_depth=3, learning_rate=0.1, reg_lambda=1.0)
DEFAULT_N_ROUNDS = 400

N_OPTUNA_TRIALS = 50
MAX_ESTIMATORS = 2000  # cap on rounds in the CV (early stopping on the validation fold)
EARLY_STOPPING_ROUNDS = 50
N_ROUNDS_SCALE = 1.0  # final rounds = median(best_iteration + 1) * scale

PROGRESS_EVERY = 10  # print boosting progress every N rounds (0 = silent)
MONITOR_MAX_ROWS = 1_000_000  # events per loss-monitoring curve during training
IN_SAMPLE_MAX_ROWS = 1_000_000  # training events kept for the train-vs-held-out plots

LEGACY_TEST_FRACTION = 0.4
LEGACY_SEED = 7
LOSS_CURVE_ROUND_STEP = 10  # legacy loss curves: evaluate every N trees...
LOSS_CURVE_MAX_ROWS = 250_000  # ...on at most this many events per curve
LOSS_CURVE_SEED = 900

SMOKE_FRACTION = 0.05
SMOKE_TRIALS = 3
SMOKE_ROUNDS = 20

STAGES = ("dev", "test", "final", "apply", "all", "legacy")
NOMINAL_TUPLES = ["Data", "DY", "EWK", "TT", "DiBoson", "ggH", "VBF"]


def parse_cli(argv):
    p = argparse.ArgumentParser(description="K-fold BDT training for H->mumu (see module docstring).")
    p.add_argument("channel", help="channel under study, e.g. ggH or VBF")
    p.add_argument("era", help="e.g. Combined")
    p.add_argument("--stage", default="all", choices=STAGES)
    p.add_argument("--do-systematics", action="store_true",
                   help="with --stage apply/all: also score the systematic tuples")
    p.add_argument("--use-recategorization", action="store_true", help="use the reCat skims/outputs")
    p.add_argument("--bkg-subset", default="Full", help="background subset (default: Full)")
    p.add_argument("--sig-subset", default="NottH", help="signal subset (default: NottH)")
    p.add_argument("--device", default="cuda", choices=("cuda", "cpu"))
    p.add_argument("--optuna-trials", type=int, default=None)
    for flag in ("--force-retest", "--smoke", "--use-optuna", "--plots-only", "--no-apply"):
        p.add_argument(flag, action="store_true")
    opts = vars(p.parse_args(argv[1:]))
    if opts["no_apply"] and opts["stage"] == "apply":
        sys.exit("[ERROR] --no-apply with --stage apply leaves nothing to do.")
    if opts["smoke"] and opts["stage"] in ("apply", "all") and not opts["plots_only"]:
        # smoke models would overwrite the real BDT_score tuples
        sys.exit("[ERROR] --smoke cannot be combined with --stage apply/all.")
    return opts


OPTS = parse_cli(sys.argv)
channel_US, era = OPTS["channel"], OPTS["era"]
doSystematics = OPTS["do_systematics"]
useRecategorization = OPTS["use_recategorization"]
background_subset = OPTS["bkg_subset"]
signal_subset = OPTS["sig_subset"]
if OPTS["plots_only"]:
    PLOT_INPUT_COMPARISON = PLOT_STANDARDIZATION = True
if OPTS["no_apply"]:
    APPEND_VARIABLES = False
if USE_WEIGHT and USE_WEIGHT_MASS_RES:
    sys.exit("[ERROR] USE_WEIGHT and USE_WEIGHT_MASS_RES are mutually exclusive")

variables = xgb_utils.get_variables(channel_US, USE_BSCONSTRAIN)  # inputs + (mass, mass error, weight)
names = [v[0] for v in variables[:-3]]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
file_append = "reCat" if useRecategorization else ""
subset_title = f"B{background_subset}_S{signal_subset}"
run_tag = "_smoke" if OPTS["smoke"] else ""
test_name = f"{channel_US}{file_append}_{era}_{subset_title}{run_tag}"
plot_path = f"../../plots/xgboost/{channel_US}{file_append}/{subset_title}{run_tag}/"
data_directory = f"../../root_io/skim/{channel_US}{file_append}/"
signal_file_name = f"{data_directory}signal_{era}_skim_{signal_subset}.root"
bkg_file_name = f"{data_directory}background_{era}_skim_{background_subset}.root"
mass_var_name = variables[-3][0]
DEV_DIR = "models/dev"
# Optuna config: written by --stage dev, read only with --use-optuna (tracked in git)
optuna_config_path = f"{DEV_DIR}/config_optuna_{test_name}.json"
test_marker_path = f"{DEV_DIR}/test_evaluated_{test_name}.json"

for subdir in ["training", "results", "scores", "variables", "comparison", "kFold"]:
    os.makedirs(plot_path + subdir, exist_ok=True)
    shutil.copy("../index.php", plot_path + subdir)
for directory in ("models", DEV_DIR, "roc"):
    os.makedirs(directory, exist_ok=True)

print(f"[INFO] channel {channel_US}, era {era}, {subset_title}, stage {OPTS['stage']}, "
      f"device {OPTS['device']}, smoke {OPTS['smoke']}, recategorization {useRecategorization}, "
      f"systematics {doSystematics}")
print(f"[INFO] {len(names)} input variables: {', '.join(names)}")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_training_data():
    """Background + signal skims as training arrays (background rows first, y = 0 / 1).

    Signal weights are scaled so both classes have the same total weight. `w_phys` keeps the
    physics weights; `w_fit` is what the BDT trains with (see USE_WEIGHT*)."""
    frames = []
    for path in (bkg_file_name, signal_file_name):
        print(f"[INFO] reading {path}")
        with uproot.open(path) as f:
            df = pd.DataFrame(f["tree_output"].arrays([v[0] for v in variables], library="np"))
        frames.append(xgb_utils.mask_undefined_jet_features(df))
    df_bkg, df_sig = frames
    print(f"[INFO] {len(df_sig)} signal and {len(df_bkg)} background rows")

    # fold = event % N_FOLDS, read from the same rows (as integers, never as a feature)
    events = np.concatenate([kf.read_event_ids(bkg_file_name), kf.read_event_ids(signal_file_name)])
    if len(events) != len(df_bkg) + len(df_sig):
        raise RuntimeError(f"{len(events)} event ids for {len(df_bkg) + len(df_sig)} skim rows")
    folds = kf.fold_of_event(events)

    def signal_region_yield(df):
        return df["weight"][(df[mass_var_name] > SIGNAL_REGION[0]) & (df[mass_var_name] < SIGNAL_REGION[1])].sum()

    signal_events, bkg_events = signal_region_yield(df_sig), signal_region_yield(df_bkg)
    print(f"[INFO] S = {signal_events:.3f}; B = {bkg_events:.3f}; "
          f"S/sqrt(B) = {signal_events / math.sqrt(bkg_events):.3f}")
    signal_scale = df_bkg["weight"].sum() / df_sig["weight"].sum()
    df_sig["weight"] *= signal_scale

    # features as float32 (their type in the skim); mass, mass error and weight as float64
    service = [v[0] for v in variables[-3:]]
    x = np.concatenate([df[names].to_numpy(dtype=np.float32) for df in frames])
    mass, rel_err, w_norm = np.concatenate([df[service].to_numpy(dtype=np.float64) for df in frames]).T
    y = np.concatenate([np.zeros(len(df_bkg)), np.ones(len(df_sig))]).astype(np.int8)
    del frames, df_bkg, df_sig

    keep = np.flatnonzero(kf.training_region_mask(mass))
    if OPTS["smoke"]:
        rng = np.random.default_rng(SEED)
        keep = keep[np.sort(rng.choice(len(keep), size=int(SMOKE_FRACTION * len(keep)), replace=False))]
    x, y, folds = x[keep], y[keep], folds[keep]
    mass, rel_err, w_norm = mass[keep], rel_err[keep], w_norm[keep]
    print(f"[INFO] {len(y)} rows in the training region" + (" (smoke subsample)" if OPTS["smoke"] else ""))

    w_phys = np.where(y == 1, w_norm / signal_scale, w_norm)
    if USE_WEIGHT_MASS_RES:
        w_fit = np.abs(w_norm) / rel_err
    elif USE_WEIGHT:
        w_fit = np.abs(w_norm)
    else:
        w_fit = np.ones(len(y))

    if DRAW_CORRELATIONS:
        xgb_utils.draw_correlation_matrix(signal_file_name, bkg_file_name, variables[:-2], plot_path, test_name)
    if PLOT_INPUT_COMPARISON:
        xgb_utils.plot_input_comparison(x, y, np.abs(w_norm), variables[:-3], channel_US, era, plot_path)
    xgb_utils.plot_fold_balance(y, w_fit, folds, plot_path, test_name, era, kf.N_FOLDS)
    report_peak_memory("after loading the training data")
    return SimpleNamespace(x=x, y=y, folds=folds, mass=mass, w_fit=w_fit, w_phys=w_phys,
                           signal_events=signal_events, bkg_events=bkg_events)


def report_peak_memory(label):
    print(f"[MEM  ] {label}: peak RSS {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.2f} GB")


def frozen_config():
    """DEFAULT_PARAMS, or the Optuna configuration with --use-optuna."""
    if not OPTS["use_optuna"]:
        print(f"[INFO] using DEFAULT_PARAMS {DEFAULT_PARAMS}, {DEFAULT_N_ROUNDS} rounds")
        return kf.make_config(OPTS["device"], DEFAULT_PARAMS, DEFAULT_N_ROUNDS, "default_fixed")
    if not os.path.exists(optuna_config_path):
        sys.exit(f"[ERROR] --use-optuna given but {optuna_config_path} does not exist: run "
                 "`--stage dev` first, or `git pull` the committed config.")
    with open(optuna_config_path) as f:
        config = json.load(f)
    print(f"[INFO] using {optuna_config_path}: {config['params']}, {config['n_rounds']} rounds")
    return config


def training_setup():
    """(config, params, n_rounds) for the fixed-round stages."""
    config = frozen_config()
    n_rounds = SMOKE_ROUNDS if OPTS["smoke"] else int(config["n_rounds"])
    return config, kf.params_from_config(config, OPTS["device"]), n_rounds


# ---------------------------------------------------------------------------
# Shared reporting
# ---------------------------------------------------------------------------
def report_working_points(y, p, w_phys, mass, name, d):
    """Signal-region ROC with physics weights: maximum S/sqrt(B) and the 90%/80% signal
    efficiency working points."""
    sr = (mass > SIGNAL_REGION[0]) & (mass < SIGNAL_REGION[1])
    fpr, tpr, thr = roc_curve(y[sr], p[sr], sample_weight=w_phys[sr])
    significance, eff_sig, eff_bkg, thresholds = xgb_utils.significance_scan(
        fpr, tpr, thr, name, d.signal_events, d.bkg_events)
    points = [("Max", np.argmax(significance))]
    points += [(f"WP{int(100 * wp)}", np.argmin(np.abs(eff_sig - wp))) for wp in (0.90, 0.80)]
    for label, i in points:
        print(f"[INFO] {label}: significance = {significance[i]:.4f}, threshold = {thresholds[i]:.4f}, "
              f"signal eff = {eff_sig[i]:.4f}, background eff = {eff_bkg[i]:.4f}")
    return fpr, tpr


def make_oof_plots(y, p, w_fit, w_phys, mass, in_sample, tag, eval_name, d, models,
                   train_name="in-fold (train)"):
    """ROC, discriminator, sculpting and feature importance from held-out predictions.
    `in_sample` = (y, p, w) of training events, for the train-vs-held-out overlay."""
    auc, auc_w = roc_auc_score(y, p), roc_auc_score(y, p, sample_weight=w_fit)
    print(f"[INFO] {tag}: AUC = {auc:.5f}; weighted AUC = {auc_w:.5f}")
    fpr, tpr = report_working_points(y, p, w_phys, mass, f"{test_name}_{tag}", d)
    xgb_utils.draw_roc_curve(fpr, tpr, f"{tag}_{test_name}", plot_path, era, auc)
    xgb_utils.draw_roc_curve(fpr, tpr, f"weighted_{tag}_{test_name}", plot_path, era, auc_w)
    for scale in ("log", "linear"):
        xgb_utils.plot_discriminator(y, p, *in_sample[:2], w_phys, in_sample[2], era, plot_path,
                                     scale=scale, eval_name=eval_name, train_name=train_name,
                                     file_tag=f"_{tag}")
    bkg = y == 0
    xgb_utils.plot_BDT_sculpting(p[bkg], mass[bkg], w_phys[bkg], channel_US, era, plot_path,
                                 bdt_divisions=6, tag=tag)
    xgb_utils.plot_feature_importance_kfold(models, variables, f"{tag}_{test_name}", plot_path)
    return dict(auc=auc, auc_w=auc_w)


def make_standardization_plots(x, folds):
    """Model 0's actual standardization (fitted on fold != 0), before any training."""
    if PLOT_STANDARDIZATION and DO_STANDARDIZATION:
        train, heldout = folds != 0, folds == 0
        mean_map, std_map = kf.fit_standardizer(x[train], names)
        xgb_utils.plot_standardization_check(x[train], x[heldout], names, mean_map, std_map,
                                             plot_path, era, eval_label="held-out fold 0")


# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------
def stage_plots():
    d = load_training_data()
    kf.fold_summary(d.y, d.w_fit, d.folds)
    make_standardization_plots(d.x, d.folds)
    print(f"[INFO] --plots-only: done, nothing trained. Plots are under {plot_path}")


def stage_dev():
    """Optuna with 5-fold CV on the development sample (the test sample is never touched)."""
    d = load_training_data()
    dev_idx, test_idx = kf.split_dev_test(d.y, TEST_FRACTION, SEED)
    print(f"[INFO] development sample {len(dev_idx)} events; untouched test sample {len(test_idx)}")
    x, y, w = d.x[dev_idx], d.y[dev_idx], d.w_fit[dev_idx]
    del d
    cv_folds = kf.cv_fold_indices(y, SEED)
    validation_fold = np.empty(len(y), dtype=np.int8)
    for k, (_, va) in enumerate(cv_folds):
        validation_fold[va] = k
    kf.fold_summary(y, w, validation_fold, label="CV validation fold")

    device = OPTS["device"]
    n_trials = OPTS["optuna_trials"] or (SMOKE_TRIALS if OPTS["smoke"] else N_OPTUNA_TRIALS)
    max_estimators = SMOKE_ROUNDS if OPTS["smoke"] else MAX_ESTIMATORS
    esr = 5 if OPTS["smoke"] else EARLY_STOPPING_ROUNDS
    study = kf.run_optuna_cv(x, y, w, cv_folds, names, DO_STANDARDIZATION, n_trials, SEED, device,
                             max_estimators, esr, progress_every=PROGRESS_EVERY)
    report_peak_memory("after the Optuna study")

    optuna_plot_path = f"optunaPlots/{channel_US}{file_append}/{test_name}/"
    os.makedirs(optuna_plot_path, exist_ok=True)
    try:
        import optuna.visualization as vis
        vis.plot_optimization_history(study).write_html(optuna_plot_path + "optimization_history.html")
        vis.plot_param_importances(study).write_html(optuna_plot_path + "param_importance.html")
        vis.plot_slice(study).write_html(optuna_plot_path + "optuna_slice.html")
    except Exception as e:  # plotly is optional
        print(f"[WARNING] Optuna plots skipped: {e}")

    best = study.best_trial
    n_rounds = kf.choose_n_rounds(best.user_attrs["fold_best_iteration"], N_ROUNDS_SCALE)
    config = kf.make_config(device, study.best_params, n_rounds, "optuna")
    config.update(
        n_folds=kf.N_FOLDS, seed=SEED, test_fraction=TEST_FRACTION,
        n_rounds_policy=f"median(best_iteration+1) over the CV folds * {N_ROUNDS_SCALE}",
        cv=dict(mean_auc_w=best.value, **{k: best.user_attrs[k] for k in
                                          ("fold_auc_w", "fold_logloss_w", "fold_best_iteration")}),
        training_weights="mass_res" if USE_WEIGHT_MASS_RES else ("weight" if USE_WEIGHT else "none"),
        standardization=DO_STANDARDIZATION, variables=names, smoke=OPTS["smoke"])
    with open(optuna_config_path, "w") as f:
        json.dump(config, f, indent=2, default=float)
    print(f"[INFO] best mean weighted validation AUC {best.value:.5f} with {study.best_params}, "
          f"{n_rounds} rounds")
    print(f"[INFO] written to {optuna_config_path} (used by test/final only with --use-optuna). "
          "Next: run `--stage test` ONCE, then `--stage final`.")


def stage_test():
    """Refit the frozen configuration on the development sample and evaluate it on the
    untouched test sample. Do not change anything based on the result."""
    if os.path.exists(test_marker_path) and not OPTS["force_retest"]:
        sys.exit(f"[ERROR] {test_marker_path} exists: the test sample was already evaluated. "
                 "Use --force-retest only if the configuration did NOT change because of it.")
    config, params, n_rounds = training_setup()
    d = load_training_data()
    dev_idx, test_idx = kf.split_dev_test(d.y, TEST_FRACTION, SEED)  # the split --stage dev used
    member, p_test, _ = kf.train_model(d.x, d.y, d.w_fit, dev_idx, test_idx, names, DO_STANDARDIZATION,
                                       params, n_rounds, label="refit on the development sample",
                                       progress_every=PROGRESS_EVERY, monitor_max_rows=MONITOR_MAX_ROWS,
                                       monitor_heldout=False)  # the test sample never enters fit()
    metrics = member["heldout_metrics"]
    print(f"\n[TEST] untouched test sample ({len(test_idx)} events), {n_rounds} rounds:")
    for k, v in metrics.items():
        print(f"[TEST]   {k:10s} = {v:.5f}")
    cv = config.get("cv")
    if cv:
        print(f"[CV  ] cross-validation: weighted AUC {np.mean(cv['fold_auc_w']):.5f} +/- "
              f"{np.std(cv['fold_auc_w']):.5f}, weighted logloss {np.mean(cv['fold_logloss_w']):.5f}")
    with open(f"{plot_path}results/test_evaluation_{test_name}.json", "w") as f:
        json.dump(dict(test=metrics, cv=cv, n_test=len(test_idx), n_rounds=n_rounds,
                       config_source=config["source"]), f, indent=2, default=float)
    with open(test_marker_path, "w") as f:
        json.dump(dict(evaluated=True, test=metrics), f, default=float)
    fpr, tpr, _ = roc_curve(d.y[test_idx], p_test, sample_weight=d.w_fit[test_idx])
    xgb_utils.draw_roc_curve(fpr, tpr, f"test_{test_name}", plot_path, era, metrics["auc_w"])


def stage_final():
    """The five analysis models on all MC, and the OOF plots."""
    config, params, n_rounds = training_setup()
    d = load_training_data()
    kf.fold_summary(d.y, d.w_fit, d.folds, label="final fold")
    make_standardization_plots(d.x, d.folds)

    def save_model(member):  # right after each fit, so a later crash cannot lose it
        kf.save_fold_models([member], test_name, USE_BSCONSTRAIN, params, SEED,
                            extra_meta=dict(config_source=config["source"]))

    members, oof, in_sample = kf.train_final_kfold(
        d.x, d.y, d.w_fit, d.folds, names, DO_STANDARDIZATION, params, n_rounds, on_model_done=save_model,
        progress_every=PROGRESS_EVERY, monitor_max_rows=MONITOR_MAX_ROWS, in_sample_max_rows=IN_SAMPLE_MAX_ROWS)
    print(f"[INFO] saved {kf.N_FOLDS} models: models/model_{test_name}_fold<k>"
          f"{'_bsC' if USE_BSCONSTRAIN else ''}.{{pkl,json}}")

    # each training event appears in N_FOLDS-1 models' training sets
    idx = np.concatenate([s["idx"] for s in in_sample])
    in_p = np.concatenate([s["p"] for s in in_sample])
    summary = make_oof_plots(d.y, oof, d.w_fit, d.w_phys, d.mass,
                             (d.y[idx], in_p, d.w_phys[idx] / (kf.N_FOLDS - 1)),
                             "OOF", "OOF (held-out fold)", d, [m["model"] for m in members])
    xgb_utils.plot_roc_per_fold(d.y, oof, d.folds, d.w_fit, era, plot_path, test_name)
    xgb_utils.plot_discriminator_per_fold(d.y, oof, d.folds, d.w_phys, era, plot_path, test_name)
    if PLOT_LOSS:
        xgb_utils.plot_fold_loss_curves(members, plot_path, test_name, era,
                                        second_label="held-out fold (monitoring only)")
    try:
        xgb_utils.plot_xgb_tree(members[0]["model"], variables, f"{test_name}_fold0", plot_path)
    except Exception as e:  # graphviz is optional
        print(f"[WARNING] tree plot skipped: {e}")

    per_fold = [dict(fold=m["fold"], **m["heldout_metrics"]) for m in members]
    aucs = np.array([r["auc_w"] for r in per_fold])
    print(f"[INFO] per-fold held-out weighted AUC: {np.round(aucs, 5).tolist()} "
          f"(mean {aucs.mean():.5f} +/- {aucs.std():.5f})")
    with open(f"{plot_path}results/kfold_final_{test_name}.json", "w") as f:
        json.dump(dict(oof=summary, folds=per_fold, n_rounds=n_rounds, config_source=config["source"]),
                  f, indent=2, default=float)
    np.savez(f"models/oof_{test_name}.npz", oof=oof, y=d.y, fold=d.folds, mass=d.mass, w_phys=d.w_phys)


def stage_legacy():
    """The pre-K-fold approach (one unstratified 60/40 split, one model), compared with the
    K-fold OOF scores on the identical held-out 40%, where both are out-of-sample."""
    config, params, n_rounds = training_setup()
    try:
        bundle = kf.load_fold_bundle(test_name, USE_BSCONSTRAIN)
    except FileNotFoundError:
        sys.exit(f"[ERROR] no K-fold models for {test_name}: run `--stage final` first.")
    d = load_training_data()
    train_idx, test_idx = kf.legacy_split(len(d.y), LEGACY_TEST_FRACTION, LEGACY_SEED)

    member, p_legacy, in_sample = kf.train_model(
        d.x, d.y, d.w_fit, train_idx, test_idx, names, DO_STANDARDIZATION, params, n_rounds,
        label="legacy model", progress_every=PROGRESS_EVERY, monitor_max_rows=MONITOR_MAX_ROWS,
        in_sample_max_rows=IN_SAMPLE_MAX_ROWS)
    kf.save_fold_models([member], f"{test_name}_legacy", USE_BSCONSTRAIN, params, LEGACY_SEED, n_folds=1,
                        extra_meta=dict(config_source=config["source"], legacy_split=True))
    p_kfold = kf.predict_by_fold(d.x[test_idx], d.folds[test_idx], bundle)

    y, w_fit, w_phys, mass = d.y[test_idx], d.w_fit[test_idx], d.w_phys[test_idx], d.mass[test_idx]
    m_legacy, m_kfold = kf.weighted_metrics(y, p_legacy, w_fit), kf.weighted_metrics(y, p_kfold, w_fit)
    print(f"\n[COMPARE] both approaches on the same {len(test_idx)} held-out events")
    print(f"[COMPARE] {'metric':12s} {'no k-fold 60/40':>16s} {'K-fold OOF':>14s}")
    for k in m_legacy:
        print(f"[COMPARE] {k:12s} {m_legacy[k]:16.5f} {m_kfold[k]:14.5f}")

    make_oof_plots(y, p_legacy, w_fit, w_phys, mass,
                   (d.y[in_sample["idx"]], in_sample["p"], d.w_phys[in_sample["idx"]]),
                   "noKfold", "no k-fold (held-out 40%)", d, [member["model"]],
                   train_name="no k-fold (train 60%)")
    report_working_points(y, p_kfold, w_phys, mass, f"{test_name}_kfoldOOF", d)
    xgb_utils.plot_legacy_vs_kfold(y, w_phys, p_legacy, p_kfold, m_legacy["auc_w"], m_kfold["auc_w"],
                                   era, plot_path)

    loss_curves = None
    if PLOT_LOSS:
        # Every curve is recomputed from the trained models on a common round grid.
        # Out-of-sample curves share the held-out 40%; in-sample curves share one
        # subsample of the train 60%, so each pair is a like-for-like comparison.
        rounds = kf.round_grid(n_rounds, LOSS_CURVE_ROUND_STEP)
        s60 = kf.subsample(train_idx, LOSS_CURVE_MAX_ROWS, LOSS_CURVE_SEED)
        legacy_in = kf.curve_on_rows(member, d.x, d.y, d.w_fit, s60, rounds, label="no k-fold in-sample")
        legacy_out = kf.curve_on_rows(member, d.x, d.y, d.w_fit, test_idx, rounds,
                                      label="no k-fold out-of-sample")
        kfold = kf.kfold_logloss_curves(bundle, d.x, d.y, d.w_fit, d.folds, oof_idx=test_idx,
                                        in_fold_idx=s60, rounds=rounds, max_rows=LOSS_CURVE_MAX_ROWS,
                                        seed=LOSS_CURVE_SEED)
        print(f"\n[COMPARE] weighted log loss at round {rounds[-1]}: in-sample / out-of-sample")
        print(f"[COMPARE]   no k-fold (60% train):    {legacy_in[-1]:.5f} / {legacy_out[-1]:.5f}")
        print(f"[COMPARE]   K-fold (mean of {len(bundle)} models): {kfold['in_fold'][:, -1].mean():.5f} / "
              f"{kfold['oof'][:, -1].mean():.5f}")
        xgb_utils.plot_loss_noKfold_vs_kfold(rounds, legacy_in, legacy_out, kfold["in_fold"], kfold["oof"],
                                             era, plot_path)
        loss_curves = dict(rounds=rounds.tolist(), legacy_train=legacy_in.tolist(),
                           legacy_heldout=legacy_out.tolist(), kfold_in_fold=kfold["in_fold"].tolist(),
                           kfold_oof=kfold["oof"].tolist())

    with open(f"{plot_path}comparison/legacy_vs_kfold_{test_name}.json", "w") as f:
        json.dump(dict(n_test=len(test_idx), n_legacy_train=len(train_idx), legacy=m_legacy,
                       kfold_oof=m_kfold, n_rounds=n_rounds, config_source=config["source"],
                       legacy_split=dict(seed=LEGACY_SEED, test_fraction=LEGACY_TEST_FRACTION),
                       loss_curves=loss_curves), f, indent=2, default=float)

    if APPEND_VARIABLES:
        # NOT fold-matched: in-sample for the 60% the legacy model trained on -- comparison only
        print(f"\n[INFO] scoring the tuples with the legacy model -> BDT_score/{channel_US}legacy/")
        legacy_bundle = kf.load_fold_bundle(f"{test_name}_legacy", USE_BSCONSTRAIN)
        for file_type in NOMINAL_TUPLES:
            xgb_utils.append_BDT_score(file_type, channel_US, era, signal_subset, background_subset,
                                       variables[:-3], legacy_bundle, USE_BSCONSTRAIN, useRecategorization,
                                       legacy=True)
        print(f"[INFO] next: `bash scripts/hadd_bdt.sh {channel_US} legacy` then "
              f"`python3 plot_BDT_Categories.py {channel_US} {era} legacy`")


def stage_apply():
    """Fold-matched scores (event in fold i -> model i) for the nominal and systematic tuples."""
    bundle = kf.load_fold_bundle(test_name, USE_BSCONSTRAIN)
    if not APPEND_VARIABLES:
        print("[INFO] --no-apply: BDT score was not added to the trees")
        return
    for file_type in NOMINAL_TUPLES:
        xgb_utils.append_BDT_score(file_type, channel_US, era, signal_subset, background_subset,
                                   variables[:-3], bundle, USE_BSCONSTRAIN, useRecategorization)
    if doSystematics:
        for file_type in NOMINAL_TUPLES[1:]:  # no Data variations
            xgb_utils.append_BDT_score_to_sys(file_type, channel_US, era, signal_subset, background_subset,
                                              variables[:-3], bundle, USE_BSCONSTRAIN)


def stage_all():
    stage_final()
    stage_apply()


if __name__ == "__main__":
    if OPTS["plots_only"]:
        stage_plots()
    else:
        dict(dev=stage_dev, test=stage_test, final=stage_final, apply=stage_apply, all=stage_all,
             legacy=stage_legacy)[OPTS["stage"]]()
