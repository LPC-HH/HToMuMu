#!/usr/bin/env python
"""K-fold BDT training for H->mumu.

Usage:
  python3 train.py <channel> <era> [--stage dev|test|final|apply|all|legacy|compare]
                   [--do-systematics] [--use-recategorization]
                   [--bkg-subset Full] [--sig-subset NottH]
                   [--plots-only] [--no-apply] [--use-optuna] [--force-retest] [--smoke]
                   [--retrain] [--device cuda|cpu] [--optuna-trials N] [--optuna-timeout HOURS]
                   [--objective auc_w|asimov|asimov_fit] [--optuna-resume]

Stages:
  dev     split off an untouched 20% test sample, run Optuna with 5-fold CV on the other 80%
          and write the best configuration to models/dev/config_optuna_<name>.json
  test    refit on the 80% and evaluate on the untouched test sample -- run it ONCE
  final   train the five analysis models on all MC (model i holds out fold i = event % 5)
          and make the out-of-fold (OOF) plots
  apply   append the fold-matched BDT scores to the nominal (and, with --do-systematics,
          the systematic) tuples; with --use-optuna they go to BDT_score/<channel>optimized/
  all     final + apply (default)
  legacy  the pre-K-fold single 60/40 split model, compared with the K-fold models on the
          same held-out 40%, then scored into BDT_score/<channel>legacy/ (needs `final`)
  compare the COMPARE_VARIANTS ({DEFAULT_PARAMS, AUC Optuna} x {mass_res, flat, flatMassRes}
          training weights, plus the Asimov-Optuna flatMassRes variants once their configs exist)
          in one go: reuse each variant's fold models if they exist (else
          train them; --retrain forces it)

test/final/legacy train with DEFAULT_PARAMS unless --use-optuna is given.
--objective asimov (flatMassRes training weights only): --stage dev maximizes the fold-averaged
binned Asimov Z (xgb_kfold.binned_asimov_z: fixed signal-fraction categories x 2 GeV M_mumu bins,
raw background MC) and writes config_optuna_<name>_asimov.json; test/final/apply/all use it with
--use-optuna --objective asimov, under their own "_asimov" names (models, plots,
BDT_score/<ch>asimov...). --objective asimov_fit is the same with the background of every category
from an exponential fitted to its MC (xgb_kfold.binned_asimov_z_fit), under "_asimovFit" names.
--plots-only draws the input and standardization plots and stops (compare: see above).
--no-apply skips writing scored tuples. --smoke is a quick run on 5% of the events.
"""

import argparse
import json
import math
import pickle
import os
import resource
import shutil
import sys
import time
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
PLOT_INPUT_COMPARISON = False  # signal vs background shape of every input
PLOT_STANDARDIZATION = False  # train vs held-out, before and after standardization
DO_STANDARDIZATION = True
USE_WEIGHT = False
USE_WEIGHT_MASS_RES = True  # mutually exclusive with USE_WEIGHT
REWEIGHT_BKG_FLAT = True  # background w_fit flat in mass (signal untouched)
FLAT_BEFORE_MASS_RES = True  # with USE_WEIGHT_MASS_RES: flatten |w| first, then divide by rel_err
FLAT_BIN_WIDTH = 0.5  # GeV, bin width of the flattening factors
PLOT_MASS_WEIGHTS = True  # M_mumu shape under physical / flat / uniform / mass-res weights
APPEND_VARIABLES = True
USE_BSCONSTRAIN = True
PLOT_LOSS = True
SEED = 7
TEST_FRACTION = 0.2
SIGNAL_REGION = (121., 129.)
TIGHT_CATEGORY_CUT = 0.9  # --stage compare: BDT > cut is the tight category of the sculpting plot
SCULPTING_DIVISIONS = 10  # BDTsculpting plots: background M_mumu for BDT > 0, 1/N, ..., (N-1)/N

# hyperparameters used unless --use-optuna
DEFAULT_PARAMS = dict(max_depth=3, learning_rate=0.1, reg_lambda=1.0)
DEFAULT_N_ROUNDS = 400

N_OPTUNA_TRIALS = 3 #can also be set by --optuna-trials N
MAX_ESTIMATORS = 3000  # cap on rounds in the CV (early stopping on the validation fold)
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

STAGES = ("dev", "test", "final", "apply", "all", "legacy", "compare")
NOMINAL_TUPLES = ["Data", "DY", "EWK", "TT", "DiBoson", "ggH", "VBF"]
# --stage compare --plots-only reads these per-sample compare tuples instead of re-scoring the
# training skims; they must be the samples hadded into the skims (root_io/skim/<ch>/hadd_skim.sh)
COMPARE_SAMPLES = {"background": ["DY", "EWK", "TT", "DiBoson"], "signal": ["ggH", "VBF"]}

# Training-weight schemes (see compute_w_fit), keyed by the weight tag used in the output names
WEIGHT_SCHEMES = {
    "": dict(use_weight=False, mass_res=True, flat=False, flat_before_mass_res=True),  # |w|/rel_err
    "flat": dict(use_weight=True, mass_res=False, flat=True, flat_before_mass_res=True),  # bkg |w| flat, sig |w|
    "flatMassRes": dict(use_weight=False, mass_res=True, flat=True, flat_before_mass_res=True),  # flat |w|, / rel_err
}
# --stage compare: (weight tag, use the Optuna config) of every variant, in plotting order
# opt_tag "" = DEFAULT_PARAMS, "optimized" = AUC Optuna config, "asimov" / "asimovFit" = Asimov
# Optuna config with the raw / fitted background MC
# --weights value -> WEIGHT_SCHEMES tag
WEIGHT_CLI = {"massRes": "", "flat": "flat", "flatMassRes": "flatMassRes"}
COMPARE_VARIANTS = [(tag, opt) for opt in ("", "optimized") for tag in ("", "flat", "flatMassRes")] \
    + [("flatMassRes", "asimov"), ("flatMassRes", "asimovFit")]
OBJECTIVE_OPT_TAG = {"asimov": "asimov", "asimov_fit": "asimovFit"}  # --objective -> opt_tag
COMPARE_DIR = "compare"


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
    p.add_argument("--optuna-timeout", type=float, default=None, metavar="HOURS",
                   help="with --stage dev: start no new Optuna trial after this many hours (the running "
                        "one finishes and the best configuration is still written)")
    p.add_argument("--optuna-resume", action="store_true",
                   help="with --stage dev: continue the study stored in optunaStudies/ (after a crash); "
                        "without it a new study is started and a stored one is archived")
    for flag in ("--force-retest", "--smoke", "--use-optuna", "--plots-only", "--no-apply"):
        p.add_argument(flag, action="store_true")
    p.add_argument("--retrain", action="store_true",
                   help="with --stage compare: retrain every variant even if its models exist")
    p.add_argument("--objective", default="auc_w", choices=("auc_w", "asimov", "asimov_fit"),
                   help="Optuna objective of --stage dev, and which Optuna config --use-optuna reads")
    p.add_argument("--matias-preprocessing", action="store_true",
                   help="with --stage legacy: Matias's preprocessing (padded jet values kept at 0 / -1, "
                        "standardization over the other entries only, no NaN masking) in training and tuple scoring")
    p.add_argument("--rescore", action="store_true",
                   help="with --stage compare --plots-only: evaluate the models on the training skims "
                        "instead of reading the scores from the compare tuples")
    p.add_argument("--weights", choices=sorted(WEIGHT_CLI),
                   help="training weights, overriding the module flags (USE_WEIGHT_MASS_RES, REWEIGHT_BKG_FLAT, ...): "
                        "massRes = |w|/rel_err, flat = background |w| flat in mass, flatMassRes = flat |w| then "
                        "/rel_err (default: the module flags)")
    p.add_argument("--tight-cut", type=float, default=TIGHT_CATEGORY_CUT,
                   help=f"with --stage compare: BDT cut of the tight category (default {TIGHT_CATEGORY_CUT})")
    opts = vars(p.parse_args(argv[1:]))
    if opts["no_apply"] and opts["stage"] == "apply":
        sys.exit("[ERROR] --no-apply with --stage apply leaves nothing to do.")
    if opts["stage"] == "compare":
        if opts["weights"]:
            sys.exit("[ERROR] --stage compare trains every weight scheme itself: drop --weights.")
        if opts["use_optuna"] or opts["do_systematics"]:
            sys.exit("[ERROR] --stage compare runs both parameter sets itself and scores only the nominal "
                     "tuples: drop --use-optuna / --do-systematics.")
        if opts["plots_only"]:
            if opts["retrain"]:
                sys.exit("[ERROR] --plots-only with --stage compare only reuses saved models: drop --retrain.")
            opts["no_apply"] = True  # redraw the comparison plots, never write tuples
            if opts["smoke"] and not opts["rescore"]:
                print("[INFO] --smoke implies --rescore: the compare tuples hold the full models' scores")
                opts["rescore"] = True
        if opts["smoke"] and not opts["no_apply"]:
            sys.exit("[ERROR] --smoke with --stage compare needs --no-apply (or --plots-only).")
        if not 0 < opts["tight_cut"] < 1:
            sys.exit("[ERROR] --tight-cut must be between 0 and 1.")
    elif opts["retrain"]:
        sys.exit("[ERROR] --retrain only applies to --stage compare.")
    if opts["matias_preprocessing"] and opts["stage"] != "legacy":
        sys.exit("[ERROR] --matias-preprocessing only applies to --stage legacy.")
    if opts["optuna_resume"] and opts["stage"] != "dev":
        sys.exit("[ERROR] --optuna-resume only applies to --stage dev.")
    if opts["objective"] != "auc_w":
        if opts["stage"] in ("compare", "legacy"):
            sys.exit(f"[ERROR] --objective {opts['objective']} applies to --stage dev/test/final/apply/all "
                     "(compare includes the Asimov variants by itself).")
        if opts["stage"] != "dev" and not opts["use_optuna"]:
            sys.exit(f"[ERROR] --objective {opts['objective']} selects its Asimov Optuna config: "
                     "add --use-optuna.")
    if opts["rescore"] and not (opts["stage"] == "compare" and opts["plots_only"]):
        sys.exit("[ERROR] --rescore only applies to --stage compare --plots-only.")
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
if OPTS["plots_only"] and OPTS["stage"] != "compare":
    PLOT_INPUT_COMPARISON = PLOT_STANDARDIZATION = True
if OPTS["no_apply"]:
    APPEND_VARIABLES = False
if USE_WEIGHT and USE_WEIGHT_MASS_RES and not OPTS["weights"]:
    sys.exit("[ERROR] USE_WEIGHT and USE_WEIGHT_MASS_RES are mutually exclusive")


def weight_tag_of(scheme):
    """Output-name tag of a weight scheme (flat-reweighted trainings get their own names)."""
    if not scheme["flat"]:
        return ""
    if scheme["mass_res"]:  # flatten |w| then divide by rel_err, or flatten |w|/rel_err itself
        return "flatMassRes" if scheme["flat_before_mass_res"] else "massResFlat"
    return "flat"


def training_weights_of(scheme):
    tag = weight_tag_of(scheme)
    return ("mass_res" if scheme["mass_res"] else ("weight" if scheme["use_weight"] else "none")) \
        + (f"+{tag}" if tag else "")


# the scheme of every stage except compare: --weights, else the module flags
if OPTS["weights"]:
    FLAG_SCHEME = dict(WEIGHT_SCHEMES[WEIGHT_CLI[OPTS["weights"]]])
else:
    FLAG_SCHEME = dict(use_weight=USE_WEIGHT, mass_res=USE_WEIGHT_MASS_RES, flat=REWEIGHT_BKG_FLAT,
                       flat_before_mass_res=FLAT_BEFORE_MASS_RES)
weight_tag = weight_tag_of(FLAG_SCHEME)
training_weights = training_weights_of(FLAG_SCHEME)

variables = xgb_utils.get_variables(channel_US, USE_BSCONSTRAIN)  # inputs + (mass, mass error, weight)
names = [v[0] for v in variables[:-3]]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
file_append = "reCat" if useRecategorization else ""
subset_title = f"B{background_subset}_S{signal_subset}"
run_tag = "_smoke" if OPTS["smoke"] else ""
data_directory = f"../../root_io/skim/{channel_US}{file_append}/"
signal_file_name = f"{data_directory}signal_{era}_skim_{signal_subset}.root"
bkg_file_name = f"{data_directory}background_{era}_skim_{background_subset}.root"
mass_var_name = variables[-3][0]
DEV_DIR = "models/dev"
STUDY_DIR = "optunaStudies"  # --stage dev: every Optuna study on disk (sqlite), see --optuna-resume


def make_plot_dirs(path):
    for subdir in ["training", "results", "scores", "variables", "comparison", "kFold", "test"]:
        os.makedirs(path + subdir, exist_ok=True)
        shutil.copy("../index.php", path + subdir)


def make_variant(w_tag, opt_tag):
    """Names of one (training weights, parameter set) variant; opt_tag is "" (DEFAULT_PARAMS),
    "optimized" (AUC Optuna config), "asimov" or "asimovFit" (Asimov Optuna config, raw or
    fitted background).
    Optuna outputs (models, plots, scored tuples) get their own names so they never overwrite
    the DEFAULT_PARAMS ones; the AUC dev config and test marker are shared (base_name), the
    Asimov ones carry "_<opt_tag>". The weight tag is part of base_name: the Optuna objective
    depends on the training weights."""
    base = f"{channel_US}{file_append}_{era}_{subset_title}" + (f"_{w_tag}" if w_tag else "") + run_tag
    suffix = opt_tag + w_tag  # BDT_score/<channel><suffix>/ and plots/xgboost/<channel><suffix>/
    label = "_".join(t for t in (opt_tag, w_tag) if t) or "base"
    dev_tag = f"_{opt_tag}" if opt_tag in OBJECTIVE_OPT_TAG.values() else ""
    return SimpleNamespace(
        weight_tag=w_tag, opt_tag=opt_tag, optimized=bool(opt_tag), label=label, base_name=base, dev_tag=dev_tag,
        test_name=base + (f"_{opt_tag}" if opt_tag else ""), dir_suffix=suffix,
        plot_path=f"../../plots/xgboost/{channel_US}{file_append}{suffix}/{subset_title}{run_tag}/",
        # Optuna config: written by --stage dev, read only with --use-optuna (tracked in git)
        optuna_config_path=f"{DEV_DIR}/config_optuna_{base}{dev_tag}.json",
        test_marker_path=f"{DEV_DIR}/test_evaluated_{base}{dev_tag}.json",
        branch=f"BDT_{channel_US}" + ("" if label == "base" else f"_{label}"))


if OPTS["objective"] != "auc_w":
    if weight_tag != "flatMassRes":
        sys.exit(f"[ERROR] --objective {OPTS['objective']} is set up for the flatMassRes training weights, not "
                 f"'{weight_tag or 'massRes'}': add --weights flatMassRes (or set REWEIGHT_BKG_FLAT, "
                 "USE_WEIGHT_MASS_RES, FLAT_BEFORE_MASS_RES to True).")
    opt_append = OBJECTIVE_OPT_TAG[OPTS["objective"]]
else:
    opt_append = "optimized" if OPTS["use_optuna"] else ""
# --stage dev writes the config of its objective; only --use-optuna reads one
VARIANT = make_variant(weight_tag, opt_append)
base_name, test_name, dir_suffix = VARIANT.base_name, VARIANT.test_name, VARIANT.dir_suffix
plot_path, optuna_config_path = VARIANT.plot_path, VARIANT.optuna_config_path
test_marker_path = VARIANT.test_marker_path
compare_plot_path = f"../../plots/xgboost/{channel_US}{file_append}{COMPARE_DIR}/{subset_title}{run_tag}/"

if OPTS["stage"] == "compare":
    training_weights = "per variant"
    make_plot_dirs(compare_plot_path)
else:
    make_plot_dirs(plot_path)
for directory in ("models", DEV_DIR, "roc"):
    os.makedirs(directory, exist_ok=True)

print(f"[INFO] channel {channel_US}, era {era}, {subset_title}, stage {OPTS['stage']}, "
      f"device {OPTS['device']}, smoke {OPTS['smoke']}, recategorization {useRecategorization}, "
      f"systematics {doSystematics}, training weights {training_weights}")
print(f"[INFO] {len(names)} input variables: {', '.join(names)}")


def reweight_to_flat(mass, w, is_bkg, bin_width=FLAT_BIN_WIDTH, window=kf.TRAIN_REGION):
    """Background weights times a per-bin factor so their mass histogram is flat over `window`;
    the total background weight is preserved and all other rows are unchanged.
    Returns (w_new, edges, factors)."""
    edges = np.arange(window[0], window[1] + bin_width / 2, bin_width)
    n_bins = len(edges) - 1
    content, _ = np.histogram(mass[is_bkg], bins=edges, weights=w[is_bkg])
    target = content.sum() / n_bins
    empty = content <= 0
    if empty.any():
        print(f"[WARN ] reweight_to_flat: {empty.sum()} bins with non-positive content keep factor 1")
    factors = np.where(empty, 1.0, target / np.where(empty, 1.0, content))

    idx = np.clip(np.digitize(mass, edges) - 1, 0, n_bins - 1)
    w_new = w.copy()
    w_new[is_bkg] *= factors[idx[is_bkg]]
    # restore the total background weight (only differs if a bin was left at factor 1)
    w_new[is_bkg] *= w[is_bkg].sum() / w_new[is_bkg].sum()

    n_eff = [kf.effective_entries(w[is_bkg][idx[is_bkg] == i]) for i in range(n_bins)]
    print(f"[INFO] flat background reweighting: {n_bins} bins of {bin_width} GeV over {window}, "
          f"factor {factors.min():.3f}-{factors.max():.3f}, per-bin N_eff {min(n_eff):.0f}-{max(n_eff):.0f}, "
          f"total background weight {w[is_bkg].sum():.4g} -> {w_new[is_bkg].sum():.4g}")
    return w_new, edges, factors


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def compute_w_fit(scheme, d, path, tag):
    """The training weights of one WEIGHT_SCHEMES entry (signal weights already scaled so both
    classes have the same total |w|); with a flat scheme also plots the background reweighting."""
    w_abs, rel_err, mass, y = d.w_abs, d.rel_err, d.mass, d.y
    if scheme["mass_res"]:
        w_fit = w_abs / rel_err
    elif scheme["use_weight"]:
        w_fit = w_abs.copy()
    else:
        w_fit = np.ones(len(y))
    if scheme["flat"]:
        is_bkg = y == 0
        w_before = w_fit
        if scheme["mass_res"] and scheme["flat_before_mass_res"]:
            w_flat, edges, _ = reweight_to_flat(mass, w_abs, is_bkg)
            w_fit = np.where(is_bkg, w_flat / rel_err, w_fit)
            # keep the background total of |w|/rel_err, so the class balance is unchanged
            w_fit[is_bkg] *= w_before[is_bkg].sum() / w_fit[is_bkg].sum()
        else:
            w_fit, edges, _ = reweight_to_flat(mass, w_fit, is_bkg)
        xgb_utils.plot_flat_reweighting(mass[is_bkg], w_before[is_bkg], w_fit[is_bkg], edges, era, path, tag)
    return w_fit


def plot_mass_weights(d, path, tag):
    """M_mumu shape of background and signal under physical / flat / uniform / mass-res weights."""
    edges = np.arange(kf.TRAIN_REGION[0], kf.TRAIN_REGION[1] + FLAT_BIN_WIDTH / 2, FLAT_BIN_WIDTH)
    w_mass_res = d.w_abs / d.rel_err
    w_flat = reweight_to_flat(d.mass, d.w_abs, d.y == 0)[0]
    for sample, sel in (("background", d.y == 0), ("signal", d.y == 1)):
        weights = {"physical": d.w_phys[sel]}
        if sample == "background":
            weights["flat"] = w_flat[sel]
        weights["uniform"] = np.ones(sel.sum())
        weights["mass_res"] = w_mass_res[sel]
        if sample == "background":
            weights["flat / rel_err"] = w_flat[sel] / d.rel_err[sel]
        xgb_utils.plot_mass_weight_comparison(d.mass[sel], weights, edges, era, path, tag, sample)


def load_training_data(scheme=FLAG_SCHEME):
    """Background + signal skims as training arrays (background rows first, y = 0 / 1).

    Signal weights are scaled so both classes have the same total weight. `w_phys` keeps the
    physics weights; `w_fit` is what the BDT trains with (see compute_w_fit). With scheme=None
    (--stage compare) w_fit is left to the caller, one per variant."""
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
    w_abs = np.abs(w_norm)
    d = SimpleNamespace(x=x, y=y, folds=folds, mass=mass, rel_err=rel_err, w_abs=w_abs, w_phys=w_phys,
                        w_fit=None, signal_events=signal_events, bkg_events=bkg_events)
    path, tag = (plot_path, test_name) if scheme is not None else (compare_plot_path, f"{channel_US}_compare")
    if scheme is not None:
        d.w_fit = compute_w_fit(scheme, d, path, tag)

    if PLOT_MASS_WEIGHTS:
        plot_mass_weights(d, path, tag)

    if DRAW_CORRELATIONS:
        xgb_utils.draw_correlation_matrix(signal_file_name, bkg_file_name, variables[:-2], path, tag)
    if PLOT_INPUT_COMPARISON:
        xgb_utils.plot_input_comparison(x, y, w_abs, variables[:-3], channel_US, era, path)
    if scheme is not None:
        xgb_utils.plot_fold_balance(y, d.w_fit, folds, plot_path, test_name, era, kf.N_FOLDS)
    report_peak_memory("after loading the training data")
    return d


def report_peak_memory(label):
    print(f"[MEM  ] {label}: peak RSS {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.2f} GB")


def frozen_config(variant=VARIANT):
    """DEFAULT_PARAMS, or the variant's Optuna configuration (--use-optuna)."""
    if not variant.optimized:
        print(f"[INFO] using DEFAULT_PARAMS {DEFAULT_PARAMS}, {DEFAULT_N_ROUNDS} rounds")
        return kf.make_config(OPTS["device"], DEFAULT_PARAMS, DEFAULT_N_ROUNDS, "default_fixed")
    path = variant.optuna_config_path
    if OPTS["smoke"] and not os.path.exists(path):  # smoke runs only need its parameters
        path = path.replace(run_tag, "")
    if not os.path.exists(path):
        sys.exit(f"[ERROR] the Optuna configuration {path} does not exist: run "
                 "`--stage dev` first, or `git pull` the committed config.")
    with open(path) as f:
        config = json.load(f)
    print(f"[INFO] using {path}: {config['params']}, {config['n_rounds']} rounds")
    if config.get("partial"):
        print(f"[WARNING] {path} is a best-so-far configuration of an Optuna study that did not finish "
              f"({config.get('n_trials_completed')} trials completed); resume it with --stage dev --optuna-resume.")
    if config.get("sculpting_feasible") is False:
        print(f"[WARNING] {path}: no trial passed the mass-sculpting constraint; this configuration sculpts.")
    return config


def training_setup(variant=VARIANT):
    """(config, params, n_rounds) for the fixed-round stages."""
    config = frozen_config(variant)
    n_rounds = SMOKE_ROUNDS if OPTS["smoke"] else int(config["n_rounds"])
    return config, kf.params_from_config(config, OPTS["device"]), n_rounds


# ---------------------------------------------------------------------------
# Shared reporting
# ---------------------------------------------------------------------------
def report_working_points(y, p, w_phys, mass, name, d, return_scan=False):
    """Signal-region ROC with physics weights: maximum S/sqrt(B) and the 90%/80% signal
    efficiency working points."""
    sr = (mass > SIGNAL_REGION[0]) & (mass < SIGNAL_REGION[1])
    fpr, tpr, thr = roc_curve(y[sr], p[sr], sample_weight=w_phys[sr])
    significance, eff_sig, eff_bkg, thresholds = xgb_utils.significance_scan(
        fpr, tpr, thr, name, d.signal_events, d.bkg_events)
    points = [("Max", np.argmax(significance))]
    points += [(f"WP{int(100 * wp)}", np.argmin(np.abs(eff_sig - wp))) for wp in (0.90, 0.80)]
    summary = {}
    for label, i in points:
        print(f"[INFO] {label}: significance = {significance[i]:.4f}, threshold = {thresholds[i]:.4f}, "
              f"signal eff = {eff_sig[i]:.4f}, background eff = {eff_bkg[i]:.4f}")
        summary[label] = dict(significance=significance[i], threshold=thresholds[i],
                              eff_signal=eff_sig[i], eff_bkg=eff_bkg[i])
    if return_scan:
        return fpr, tpr, summary, dict(significance=significance, eff_signal=eff_sig, eff_bkg=eff_bkg,
                                       thresholds=thresholds)
    return fpr, tpr


def make_oof_plots(y, p, w_fit, w_phys, mass, in_sample, tag, eval_name, d, models,
                   train_name="in-fold (train)", variant=VARIANT, variables_used=None):
    """ROC, discriminator, sculpting and feature importance from held-out predictions.
    `in_sample` = (y, p, w) of training events, for the train-vs-held-out overlay;
    `variables_used`: the models' variable list (default: the module's `variables`)."""
    test_name, plot_path = variant.test_name, variant.plot_path
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
                                 bdt_divisions=SCULPTING_DIVISIONS, tag=tag)
    xgb_utils.plot_feature_importance_kfold(models, variables_used or variables, f"{tag}_{test_name}", plot_path)
    return dict(auc=auc, auc_w=auc_w)


def make_standardization_plots(x, folds, plot_path=plot_path):
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
    try:  # the on-disk study storage (sqlite) needs them: fail now, not after loading the data
        import alembic  # noqa: F401
        import sqlalchemy  # noqa: F401
        import optuna  # noqa: F401
    except ImportError as error:
        sys.exit(f"[ERROR] --stage dev needs optuna with its sqlite storage ({error}); install it in this "
                 "environment (e.g. micromamba install -c conda-forge optuna).")
    d = load_training_data()
    dev_idx, test_idx = kf.split_dev_test(d.y, TEST_FRACTION, SEED)
    print(f"[INFO] development sample {len(dev_idx)} events; untouched test sample {len(test_idx)}")
    x, y, w = d.x[dev_idx], d.y[dev_idx], d.w_fit[dev_idx]
    asimov = kf.is_asimov(OPTS["objective"])
    # binned Asimov Z of a validation fold, scaled to the full sample: a fold holds
    # (1 - TEST_FRACTION) / N_FOLDS (x SMOKE_FRACTION) of the MC
    asimov_inputs = (d.mass[dev_idx], d.w_phys[dev_idx]) if asimov else None
    asimov_scale = kf.N_FOLDS / (1 - TEST_FRACTION) / (SMOKE_FRACTION if OPTS["smoke"] else 1.0)
    del d
    cv_folds = kf.cv_fold_indices(y, SEED)
    validation_fold = np.empty(len(y), dtype=np.int8)
    for k, (_, va) in enumerate(cv_folds):
        validation_fold[va] = k
    kf.fold_summary(y, w, validation_fold, label="CV validation fold")

    device = OPTS["device"]
    n_trials = OPTS["optuna_trials"] or (SMOKE_TRIALS if OPTS["smoke"] else N_OPTUNA_TRIALS)
    max_estimators = SMOKE_ROUNDS if OPTS["smoke"] else MAX_ESTIMATORS
    esr = 5 if OPTS["smoke"] else (kf.ASIMOV_EARLY_STOPPING_ROUNDS if asimov else EARLY_STOPPING_ROUNDS)
    checkpoint_every = 5 if OPTS["smoke"] else kf.ASIMOV_CHECKPOINT_EVERY
    optuna_plot_path = f"optunaPlots/{channel_US}{file_append}/{base_name}{VARIANT.dev_tag}/"
    trial_plot_path = optuna_plot_path + "trials/"

    # every trial is stored on disk; a stored study is only continued with --optuna-resume
    study_name = f"{base_name}{VARIANT.dev_tag}"
    db_path = f"{STUDY_DIR}/{study_name}.db"
    os.makedirs(STUDY_DIR, exist_ok=True)
    if OPTS["optuna_resume"]:
        if not os.path.exists(db_path):
            sys.exit(f"[ERROR] --optuna-resume: {db_path} does not exist (nothing to resume).")
        print(f"[INFO] resuming the Optuna study stored in {db_path}")
    else:  # a new study: archive, never delete, the previous one and its trial plots
        old_plots = os.path.isdir(trial_plot_path) and os.listdir(trial_plot_path)
        if os.path.exists(db_path) or old_plots:
            source = db_path if os.path.exists(db_path) else trial_plot_path
            stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(os.path.getmtime(source)))
            moved = []
            if os.path.exists(db_path):
                os.rename(db_path, f"{STUDY_DIR}/{study_name}_{stamp}.db")
                moved.append(f"{STUDY_DIR}/{study_name}_{stamp}.db")
            if old_plots:
                os.rename(trial_plot_path, f"{optuna_plot_path}trials_{stamp}/")
                moved.append(f"{optuna_plot_path}trials_{stamp}/")
            print(f"[INFO] a previous study existed: archived as {' and '.join(moved)}. Starting a NEW study "
                  "(use --optuna-resume to continue a stored one).")
    setup = dict(objective=OPTS["objective"], search_space=kf.search_space_json(), max_estimators=max_estimators,
                 early_stopping_rounds=esr, checkpoint_every=checkpoint_every, seed=SEED, smoke=OPTS["smoke"],
                 n_dev_events=int(len(y)), training_weights=training_weights, variables=list(names),
                 sculpting=dict(sidebands=kf.SCULPT_SIDEBANDS, window=kf.SCULPT_WINDOW, tight_max_fraction=kf.SCULPT_TIGHT_MAX_FRACTION,
                                max_pull=kf.SCULPT_MAX_PULL) if asimov else None)

    trial_callback = None
    if asimov:  # diagnostic plots of every trial (pruned trials included)
        os.makedirs(trial_plot_path, exist_ok=True)
        fitted = OPTS["objective"] == "asimov_fit"

        def trial_callback(number, params, infos, pruned_after):
            best_round = kf.mean_z_curve(infos)[0]
            sculpt = kf.combine_sculpt(infos, best_round)
            plots = [lambda: xgb_utils.plot_asimov_trial(number, params, infos, era, trial_plot_path,
                                                         pruned_after=pruned_after, fitted=fitted,
                                                         infeasible=sculpt["constraint"] > 0),
                     lambda: xgb_utils.plot_asimov_trial_scores(number, infos, best_round, era, trial_plot_path),
                     lambda: xgb_utils.plot_asimov_trial_sculpting(number, sculpt, best_round, era,
                                                                   trial_plot_path)]
            if fitted:
                plots.append(lambda: xgb_utils.plot_asimov_trial_bkg_fit(number, infos, best_round, era,
                                                                         trial_plot_path))
            for plot in plots:  # one failing plot must not skip the others
                try:
                    plot()
                except Exception as error:
                    print(f"[WARNING] trial {number}: plot failed: {error!r}", flush=True)

    def write_dev_config(study, partial):
        """The configuration of the best feasible trial so far (partial=True while the study runs)."""
        import optuna
        best, feasible = kf.best_feasible_trial(study)
        if best is None:
            return None
        states = [t.state for t in study.get_trials(deepcopy=False)]
        cv = {k: best.user_attrs[k] for k in ("fold_auc_w", "fold_logloss_w", "fold_best_iteration")}
        if asimov:
            n_rounds = int(best.user_attrs["best_checkpoint"])
            policy = (f"Asimov checkpoint (every {checkpoint_every} rounds) with the best "
                      "fold-averaged Z")
            if "fold_z_categories" in best.user_attrs:  # studies from before it was recorded lack it
                cv.update(fold_z_categories=best.user_attrs["fold_z_categories"])
            cv.update(mean_z=best.value, fold_best_z=best.user_attrs["fold_best_z"],
                      fold_z_curves=best.user_attrs["fold_z_curves"], asimov_scale=asimov_scale,
                      asimov_signal_fractions=kf.ASIMOV_SIGNAL_FRACTIONS, asimov_mass_bin=kf.ASIMOV_MASS_BIN,
                      asimov_background=("exponential_fit" if OPTS["objective"] == "asimov_fit" else "raw_mc"))
            if OPTS["objective"] == "asimov_fit":
                cv.update(asimov_fit_min_events=kf.ASIMOV_FIT_MIN_EVENTS)
        else:
            n_rounds = kf.choose_n_rounds(best.user_attrs["fold_best_iteration"], N_ROUNDS_SCALE)
            policy = f"median(best_iteration+1) over the CV folds * {N_ROUNDS_SCALE}"
            cv.update(mean_auc_w=best.value)
        config = kf.make_config(device, best.params, n_rounds,
                                f"optuna_{OPTS['objective']}" if asimov else "optuna")
        complete = [t for t in study.get_trials(deepcopy=False, states=(optuna.trial.TrialState.COMPLETE,))]
        config.update(
            partial=partial, best_trial=best.number, n_trials_requested=n_trials,
            n_trials_completed=len(complete), n_trials_pruned=states.count(optuna.trial.TrialState.PRUNED),
            n_trials_failed=states.count(optuna.trial.TrialState.FAIL),
            n_trials_infeasible=sum(max(kf.trial_constraint(t)) > 0 for t in complete),
            optuna_timeout_hours=OPTS["optuna_timeout"], study_storage=db_path, study_name=study_name,
            objective=OPTS["objective"], n_folds=kf.N_FOLDS, seed=SEED, test_fraction=TEST_FRACTION,
            n_rounds_policy=policy, early_stopping_rounds=esr, max_estimators=max_estimators,
            search_space=kf.search_space_json(), cv=cv, training_weights=training_weights,
            standardization=DO_STANDARDIZATION, variables=names, smoke=OPTS["smoke"])
        if asimov:
            config.update(sculpting=best.user_attrs.get("sculpt"), sculpting_feasible=feasible)
        with open(optuna_config_path, "w") as f:
            json.dump(config, f, indent=2, default=float)
        return best, feasible, config

    def on_trial_done(study, trial):
        if write_dev_config(study, partial=True) is not None:
            print(f"[INFO] best-so-far configuration written to {optuna_config_path}", flush=True)

    study = kf.run_optuna_cv(x, y, w, cv_folds, names, DO_STANDARDIZATION, n_trials, SEED, device,
                             max_estimators, esr, progress_every=PROGRESS_EVERY,
                             objective=OPTS["objective"], asimov_inputs=asimov_inputs,
                             asimov_scale=asimov_scale,
                             checkpoint_every=checkpoint_every, trial_callback=trial_callback,
                             timeout=OPTS["optuna_timeout"] * 3600 if OPTS["optuna_timeout"] else None,
                             storage=f"sqlite:///{db_path}", study_name=study_name,
                             resume=OPTS["optuna_resume"], setup=setup, on_trial_done=on_trial_done)
    report_peak_memory("after the Optuna study")

    os.makedirs(optuna_plot_path, exist_ok=True)
    try:
        import optuna.visualization as vis
        vis.plot_optimization_history(study).write_html(optuna_plot_path + "optimization_history.html")
        vis.plot_param_importances(study).write_html(optuna_plot_path + "param_importance.html")
        vis.plot_slice(study).write_html(optuna_plot_path + "optuna_slice.html")
    except Exception as e:  # plotly is optional
        print(f"[WARNING] Optuna plots skipped: {e}")

    result = write_dev_config(study, partial=False)
    if result is None:
        sys.exit(f"[ERROR] no Optuna trial completed (see the log); nothing written. The trials are kept in "
                 f"{db_path} (continue with --optuna-resume).")
    best, feasible, config = result
    n_done = config["n_trials_completed"] + config["n_trials_pruned"]
    timed_out = n_done < n_trials
    config["timed_out"] = timed_out
    with open(optuna_config_path, "w") as f:
        json.dump(config, f, indent=2, default=float)
    print(f"[INFO] {config['n_trials_completed']} trials completed, {config['n_trials_pruned']} pruned, "
          f"{config['n_trials_failed']} failed"
          + (f", {config['n_trials_infeasible']} infeasible (mass sculpting)" if asimov else "")
          + (f" (stopped before {n_trials} trials: --optuna-timeout or failures)" if timed_out else ""))
    if asimov and not feasible:
        print("[WARNING] NO trial passed the mass-sculpting constraint: the configuration below is the best "
              "INFEASIBLE trial (sculpting_feasible: false in the config). Check its trial_*_sculpting plot.")
    print(f"[INFO] best {'mean Asimov Z' if asimov else 'mean weighted validation AUC'} {best.value:.5f} "
          f"(trial {best.number}) with {best.params}, {config['n_rounds']} rounds")
    flags = "--use-optuna" + (f" --objective {OPTS['objective']}" if asimov else "")
    print(f"[INFO] written to {optuna_config_path} (used by test/final only with {flags}). "
          f"Next: run `--stage test {flags}` ONCE, then `--stage final {flags}`.")


def stage_test():
    """Refit the frozen configuration on the development sample and evaluate it on the
    untouched test sample. Do not change anything based on the result."""
    if os.path.exists(test_marker_path) and not OPTS["force_retest"]:
        sys.exit(f"[ERROR] {test_marker_path} exists: the test sample was already evaluated. "
                 "Use --force-retest only if the configuration did NOT change because of it.")
    config, params, n_rounds = training_setup()
    d = load_training_data()
    dev_idx, test_idx = kf.split_dev_test(d.y, TEST_FRACTION, SEED)  # the split --stage dev used
    member, p_test, in_sample = kf.train_model(d.x, d.y, d.w_fit, dev_idx, test_idx, names, DO_STANDARDIZATION,
                                               params, n_rounds, label="refit on the development sample",
                                               progress_every=PROGRESS_EVERY, monitor_max_rows=MONITOR_MAX_ROWS,
                                               in_sample_max_rows=IN_SAMPLE_MAX_ROWS,
                                               monitor_heldout=False)  # the test sample never enters fit()
    metrics = member["heldout_metrics"]
    print(f"\n[TEST] untouched test sample ({len(test_idx)} events), {n_rounds} rounds:")
    for k, v in metrics.items():
        print(f"[TEST]   {k:10s} = {v:.5f}")
    cv = config.get("cv")
    if cv:
        print(f"[CV  ] cross-validation: weighted AUC {np.mean(cv['fold_auc_w']):.5f} +/- "
              f"{np.std(cv['fold_auc_w']):.5f}, weighted logloss {np.mean(cv['fold_logloss_w']):.5f}")
    test_asimov = test_asimov_z(d, test_idx, p_test, cv) if kf.is_asimov(OPTS["objective"]) else None
    diagnostics = {}
    try:  # the diagnostics must never cost the test result: the json and the marker follow
        diagnostics = test_plots(d, test_idx, p_test, in_sample, n_rounds, cv, test_asimov)
    except Exception as error:
        print(f"[WARNING] test-stage diagnostics failed: {error!r}", flush=True)
    with open(f"{plot_path}results/test_evaluation_{test_name}.json", "w") as f:
        json.dump(dict(test=metrics, cv=cv, n_test=len(test_idx), n_rounds=n_rounds,
                       config_source=config["source"], test_asimov=test_asimov,
                       test_sculpting=diagnostics.get("sculpting"), train_vs_test=diagnostics.get("train_vs_test")),
                  f, indent=2, default=float)
    marker = dict(evaluated=True, test=metrics)
    if test_asimov:
        marker.update(z_raw=test_asimov["z_raw"], z_fit=test_asimov["z_fit"])
    with open(test_marker_path, "w") as f:
        json.dump(marker, f, default=float)


def test_scale():
    """Yield scale from the test sample to the full MC."""
    return 1 / TEST_FRACTION / (SMOKE_FRACTION if OPTS["smoke"] else 1.0)


def train_vs_test(d, test_idx, p_test, in_sample):
    """Overtraining check of the refit: the AUC of the untouched test sample and of the refit's own
    training events (in_sample, a subsample of the development sample) with the training weights
    over the whole training window and with physics weights in SIGNAL_REGION, and the weighted
    KS test of the test vs training score distributions per class (physics weights, as in the
    discriminator plot). Returns (numbers, ROC curves {"fit"/"phys_sr": [(fpr, tpr, label, auc)]})."""
    samples = [("test (untouched)", test_idx, p_test)]
    if in_sample is not None:
        samples.append(("train (development sample)", in_sample["idx"], np.asarray(in_sample["p"], float)))
    numbers, curves = {}, {"fit": [], "phys_sr": []}
    for label, idx, p in samples:
        key = "test" if label.startswith("test") else "train"
        y, mass = d.y[idx], d.mass[idx]
        sr = (mass > SIGNAL_REGION[0]) & (mass < SIGNAL_REGION[1])
        for kind, rows, w in (("fit", slice(None), d.w_fit[idx]), ("phys_sr", sr, d.w_phys[idx])):
            fpr, tpr, _ = roc_curve(y[rows], p[rows], sample_weight=w[rows])
            # trapezoid integral: = roc_auc_score for positive weights, and defined when negative
            # generator weights make the physics-weighted curve non-monotone (roc_auc_score raises)
            auc = float(np.sum(np.diff(fpr) * (tpr[1:] + tpr[:-1]) / 2))
            numbers[f"auc_{kind}_{key}"] = float(auc)
            curves[kind].append((fpr, tpr, label, auc))
    if in_sample is not None:
        tr = in_sample["idx"]
        for cls, name in ((1, "signal"), (0, "background")):
            a, b = d.y[test_idx] == cls, d.y[tr] == cls
            ks_d, ks_p, n_test, n_train = kf.weighted_ks(p_test[a], d.w_phys[test_idx][a],
                                                         np.asarray(in_sample["p"], float)[b], d.w_phys[tr][b])
            numbers.update({f"ks_d_{name}": ks_d, f"ks_p_{name}": ks_p, f"n_eff_test_{name}": n_test,
                            f"n_eff_train_{name}": n_train})
    for kind, title in (("fit", "training weights, 115-135 GeV"),
                        ("phys_sr", f"physics weights, {SIGNAL_REGION[0]:g}-{SIGNAL_REGION[1]:g} GeV")):
        test_auc, train_auc = numbers[f"auc_{kind}_test"], numbers.get(f"auc_{kind}_train")
        gap = f", train {train_auc:.5f} (train - test = {train_auc - test_auc:+.5f})" if train_auc is not None else ""
        print(f"[TEST]   AUC ({title}): test {test_auc:.5f}{gap}")
    for name in ("signal", "background"):
        if f"ks_d_{name}" in numbers:
            ks_p = numbers[f"ks_p_{name}"]
            print(f"[TEST]   KS test vs train, {name:10s}: D = {numbers[f'ks_d_{name}']:.4f}, p = "
                  + ("n/a" if ks_p is None else f"{ks_p:.3g}")
                  + f" (N_eff test {numbers[f'n_eff_test_{name}']:.0f}, train {numbers[f'n_eff_train_{name}']:.0f}; "
                    "physics weights)")
    return numbers, curves


def test_plots(d, test_idx, p_test, in_sample, n_rounds, cv, test_asimov):
    """Diagnostics of the refit on the untouched test sample (MC only). In <plot_path>training/
    ("_test"): the ROC of the test and training samples with the training weights and with physics
    weights in SIGNAL_REGION, the training-vs-test score overlay (with the AUC and KS numbers of
    train_vs_test) and the nested-cut mass shapes. In <plot_path>test/: the sideband-pull check of
    the Optuna sculpting constraint on the fixed categories and, for the Asimov objectives, the
    score distribution with the categories, the tightest category's background fit and the
    per-category Z of test vs CV. Each plot may fail on its own. Returns the sculpting summary
    (kf.sculpt_attrs) and the train_vs_test numbers for the test json."""
    test_path = f"{plot_path}test/"
    numbers, curves = train_vs_test(d, test_idx, p_test, in_sample)
    print("[TEST]   physics-weighted working points of the test sample in the signal region:")
    report_working_points(d.y[test_idx], p_test, d.w_phys[test_idx], d.mass[test_idx], f"{test_name}_test", d)
    note = None
    if "ks_d_signal" in numbers:
        def ks(name):
            p_ks = numbers[f"ks_p_{name}"]
            return f"D = {numbers[f'ks_d_{name}']:.3f} (p = {'n/a' if p_ks is None else f'{p_ks:.2g}'})"
        note = (f"AUC test {numbers['auc_fit_test']:.4f}, train {numbers['auc_fit_train']:.4f} (training weights)\n"
                f"KS test vs train: signal {ks('signal')}\nKS test vs train: bkg {ks('background')}")
    y, p, w, mass = d.y[test_idx], p_test, d.w_phys[test_idx], d.mass[test_idx]
    objective = OPTS["objective"]
    info = kf.single_sample_info(p, y, mass, w, n_rounds, test_scale(), objective)
    combined = kf.combine_sculpt([info], n_rounds)
    sculpt = kf.sculpt_attrs(combined)
    for label, c in sorted(sculpt["categories"].items()):
        if kf.sculpt_is_tight(label):
            pull = "n/a (too few sideband MC events)" if c["pull"] is None else f"{c['pull']:+.2f}"
            print(f"[TEST]   sculpting {label:>7s}: window pull {pull}")
    tight_pulls = [c["pull"] for l, c in sculpt["categories"].items() if kf.sculpt_is_tight(l) and c["pull"] is not None]
    verdict = ("cannot be checked (no tight category has enough sideband MC)" if not tight_pulls
               else "FAILS the CV constraint" if sculpt["constraint"] > 0 else "passes the CV constraint")
    print(f"[TEST]   sculpting: {verdict} (tight-category pull <= {kf.SCULPT_MAX_PULL:g}); information only, the "
          f"test sample has {100 * TEST_FRACTION:g}% of the MC")
    sample = "untouched test sample"
    plots = []
    if in_sample is not None:
        idx = in_sample["idx"]
        plots += [lambda scale=scale: xgb_utils.plot_discriminator(
            y, p, d.y[idx], in_sample["p"], w, d.w_phys[idx], era, plot_path, scale=scale,
            eval_name="test (untouched)", train_name="train (development sample)", file_tag="_test", note=note)
            for scale in ("log", "linear")]
    plots += [lambda: xgb_utils.plot_roc_train_test(curves["fit"], era, f"{plot_path}training/myroc_test_{test_name}",
                                                    title="training weights, 115-135 GeV"),
              lambda: xgb_utils.plot_roc_train_test(
                  curves["phys_sr"], era, f"{plot_path}training/myroc_test_physSR_{test_name}",
                  title=f"physics weights, {SIGNAL_REGION[0]:g}-{SIGNAL_REGION[1]:g} GeV")]
    bkg = y == 0
    plots += [lambda: xgb_utils.plot_BDT_sculpting(p[bkg], mass[bkg], w[bkg], channel_US, era, plot_path,
                                                   bdt_divisions=SCULPTING_DIVISIONS, tag="test"),
              lambda: xgb_utils.plot_asimov_trial_sculpting("test", combined, n_rounds, era, test_path,
                                                            sample=sample)]
    if test_asimov is not None:
        plots += [lambda: xgb_utils.plot_asimov_trial_scores("test", [info], n_rounds, era, test_path, sample=sample),
                  lambda: xgb_utils.plot_asimov_trial_bkg_fit("test", [info], n_rounds, era, test_path,
                                                              sample="test-sample MC"),
                  lambda: xgb_utils.plot_test_vs_cv_z(test_asimov, cv, n_rounds, era, test_path)]
    for plot in plots:  # one failing plot must not skip the others
        try:
            plot()
        except Exception as error:
            print(f"[WARNING] test plot failed: {error!r}", flush=True)
    print(f"[INFO] test-sample diagnostics in {test_path} and {plot_path}training/*_test*")
    return dict(sculpting=sculpt, train_vs_test=numbers)


def test_asimov_z(d, test_idx, p_test, cv):
    """Both binned Asimov Z (raw and fitted background MC) of the refit on the untouched test
    sample, scaled to the full sample, next to the CV value the configuration was chosen on."""
    scale = test_scale()
    args = (p_test, d.y[test_idx], d.mass[test_idx], d.w_phys[test_idx])
    z_raw, cats_raw = kf.binned_asimov_z(*args, scale=scale, details=True)
    z_fit, cats_fit = kf.binned_asimov_z_fit(*args, scale=scale, details=True)
    cats_fit[-1].pop("tight_hist", None)
    optimized = "fit" if OPTS["objective"] == "asimov_fit" else "raw"
    mark = {k: " <- optimized" if k == optimized else "" for k in ("raw", "fit")}
    print(f"[TEST]   Asimov Z (raw background MC)   = {z_raw:.4f}{mark['raw']}")
    print(f"[TEST]   Asimov Z (fitted background)   = {z_fit:.4f}{mark['fit']}")
    cv_mean_z = cv.get("mean_z") if cv else None
    if cv_mean_z is not None:
        fold_z = cv.get("fold_best_z", [])
        print(f"[CV  ] cross-validation {optimized} Asimov Z {cv_mean_z:.4f} (fold best Z "
              f"{np.mean(fold_z):.4f} +/- {np.std(fold_z):.4f}); taken at the best checkpoint of the best "
              "trial, so typically somewhat above the test value (within MC statistics)")
    fit_by_label = {c["label"]: c["Z"] for c in cats_fit}
    print(f"[TEST]   {'category':>9s} {'Z raw':>8s} {'Z fit':>8s}")
    for c in cats_raw:  # merged categories may differ between the two metrics
        print(f"[TEST]   {c['label']:>9s} {c['Z']:8.4f} {fit_by_label.get(c['label'], float('nan')):8.4f}")
    for label in fit_by_label.keys() - {c["label"] for c in cats_raw}:
        print(f"[TEST]   {label:>9s} {'-':>8s} {fit_by_label[label]:8.4f}")
    return dict(objective=OPTS["objective"], scale=scale, z_raw=z_raw, z_fit=z_fit,
                categories_raw=cats_raw, categories_fit=cats_fit, cv_mean_z=cv_mean_z)


def stage_final():
    """The five analysis models on all MC, and the OOF plots."""
    config, params, n_rounds = training_setup()
    d = load_training_data()
    train_variant(d, d.w_fit, VARIANT, training_weights, config, params, n_rounds)


def train_variant(d, w_fit, variant, weights_label, config, params, n_rounds):
    """Train and save the five fold models of one variant, and make its OOF plots.
    Returns the members (as kf.train_final_kfold) and the OOF scores."""
    test_name, plot_path = variant.test_name, variant.plot_path
    kf.fold_summary(d.y, w_fit, d.folds, label="final fold")
    make_standardization_plots(d.x, d.folds, plot_path)

    def save_model(member):  # right after each fit, so a later crash cannot lose it
        kf.save_fold_models([member], test_name, USE_BSCONSTRAIN, params, SEED,
                            extra_meta=dict(config_source=config["source"], training_weights=weights_label))

    members, oof, in_sample = kf.train_final_kfold(
        d.x, d.y, w_fit, d.folds, names, DO_STANDARDIZATION, params, n_rounds, on_model_done=save_model,
        progress_every=PROGRESS_EVERY, monitor_max_rows=MONITOR_MAX_ROWS, in_sample_max_rows=IN_SAMPLE_MAX_ROWS)
    print(f"[INFO] saved {kf.N_FOLDS} models: models/model_{test_name}_fold<k>"
          f"{'_bsC' if USE_BSCONSTRAIN else ''}.{{pkl,json}}")

    # each training event appears in N_FOLDS-1 models' training sets
    idx = np.concatenate([s["idx"] for s in in_sample])
    in_p = np.concatenate([s["p"] for s in in_sample])
    summary = make_oof_plots(d.y, oof, w_fit, d.w_phys, d.mass,
                             (d.y[idx], in_p, d.w_phys[idx] / (kf.N_FOLDS - 1)),
                             "OOF", "OOF (held-out fold)", d, [m["model"] for m in members], variant=variant)
    xgb_utils.plot_roc_per_fold(d.y, oof, d.folds, w_fit, era, plot_path, test_name)
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
        json.dump(dict(oof=summary, folds=per_fold, n_rounds=n_rounds, config_source=config["source"],
                       training_weights=weights_label), f, indent=2, default=float)
    np.savez(f"models/oof_{test_name}.npz", oof=oof, y=d.y, fold=d.folds, mass=d.mass, w_phys=d.w_phys)
    return members, oof


def stage_legacy():
    """The pre-K-fold approach (one unstratified 60/40 split, one model, on the pre-K-fold
    input variables: xgb_utils.get_variables(legacy_inputs=True), as Matias's BDT), compared with
    the K-fold OOF scores (all current inputs) on the identical held-out 40%, where both are
    out-of-sample. --matias-preprocessing: his preprocessing (kf.matias_*) instead of ours, in the
    training and in the tuple scoring (score_external_model.score_nominal_tuples)."""
    config, params, n_rounds = training_setup()
    try:
        bundle = kf.load_fold_bundle(test_name, USE_BSCONSTRAIN)
    except FileNotFoundError:
        sys.exit(f"[ERROR] no K-fold models for {test_name}: run `--stage final` first.")
    d = load_training_data()
    train_idx, test_idx = kf.legacy_split(len(d.y), LEGACY_TEST_FRACTION, LEGACY_SEED)
    # the legacy model's inputs are a subset of the current ones: select their columns
    legacy_variables = xgb_utils.get_variables(channel_US, USE_BSCONSTRAIN, legacy_inputs=True)
    legacy_names = [v[0] for v in legacy_variables[:-3]]
    x_legacy = d.x[:, [names.index(n) for n in legacy_names]]
    print(f"[INFO] legacy inputs (pre-K-fold / Matias's set, {len(legacy_names)}): {', '.join(legacy_names)}")
    matias = OPTS["matias_preprocessing"]
    extra_meta = dict(config_source=config["source"], legacy_split=True, preprocessing="matias" if matias else "ours")
    if matias:
        # his convention: raw padded values (our NaN masking undone), mean/std over the train rows'
        # non-placeholder entries, float64 arithmetic as in his training; the model gets them as-is
        x_raw = kf.matias_raw(x_legacy, legacy_names)
        mean_map, std_map = kf.matias_standardizer(x_raw[train_idx], legacy_names)
        x_legacy = kf.matias_preprocess(x_raw, legacy_names, mean_map, std_map)
        extra_meta.update(matias_mean_map=mean_map, matias_std_map=std_map)
        print("[INFO] legacy preprocessing: Matias's (placeholders kept, no NaN masking)")

    member, p_legacy, in_sample = kf.train_model(
        x_legacy, d.y, d.w_fit, train_idx, test_idx, legacy_names, DO_STANDARDIZATION and not matias, params,
        n_rounds, label="legacy model", progress_every=PROGRESS_EVERY, monitor_max_rows=MONITOR_MAX_ROWS,
        in_sample_max_rows=IN_SAMPLE_MAX_ROWS)
    kf.save_fold_models([member], f"{test_name}_legacy", USE_BSCONSTRAIN, params, LEGACY_SEED, n_folds=1,
                        extra_meta=extra_meta)
    matias_prep = None
    if matias:
        matias_prep = dict(variables=legacy_names, mean_map=mean_map, std_map=std_map)
        prep_path = f"models/preprocessing_{test_name}_legacy_matias{'_bsC' if USE_BSCONSTRAIN else ''}.pkl"
        with open(prep_path, "wb") as f:
            pickle.dump(matias_prep, f)
        print(f"[INFO] Matias-format preprocessing saved to {prep_path} (for score_external_model.py)")
        check_matias_scoring(member, x_raw[test_idx], p_legacy, matias_prep)
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
                   train_name="no k-fold (train 60%)", variables_used=legacy_variables)
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
        legacy_in = kf.curve_on_rows(member, x_legacy, d.y, d.w_fit, s60, rounds, label="no k-fold in-sample")
        legacy_out = kf.curve_on_rows(member, x_legacy, d.y, d.w_fit, test_idx, rounds,
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
                       legacy_inputs=legacy_names, legacy_preprocessing=extra_meta["preprocessing"],
                       loss_curves=loss_curves), f, indent=2, default=float)

    if APPEND_VARIABLES:
        # NOT fold-matched: in-sample for the 60% the legacy model trained on -- comparison only
        print(f"\n[INFO] scoring the tuples with the legacy model -> BDT_score/{channel_US}legacy/")
        if matias:
            import score_external_model
            score_external_model.score_nominal_tuples(channel_US, member["model"].get_booster(), matias_prep, era,
                                                      signal_subset, background_subset, legacy=True)
        else:
            legacy_bundle = kf.load_fold_bundle(f"{test_name}_legacy", USE_BSCONSTRAIN)
            for file_type in NOMINAL_TUPLES:
                xgb_utils.append_BDT_score(file_type, channel_US, era, signal_subset, background_subset,
                                           legacy_variables[:-3], legacy_bundle, USE_BSCONSTRAIN,
                                           useRecategorization, legacy=True)
        print(f"[INFO] next: `bash scripts/hadd_bdt.sh {channel_US} legacy` then "
              f"`python3 plot_BDT_Categories.py {channel_US} {era} --legacy`")


def check_matias_scoring(member, x_raw_rows, p_expected, prep, n_max=200_000):
    """The tuple-scoring path of score_external_model (float32 inputs, Matias's preprocessing,
    plain booster) must reproduce the training-time predictions of the same rows. As in his code,
    training standardizes in float64 and scoring in float32, so events sitting at a split threshold
    can differ (expected, also for his own tuples); a bug would shift most events."""
    import score_external_model
    import xgboost as xgb
    rows = np.arange(min(len(x_raw_rows), n_max))
    names = prep["variables"]
    x = score_external_model.preprocess({n: x_raw_rows[rows, i].astype(np.float32) for i, n in enumerate(names)},
                                        names, prep["mean_map"], prep["std_map"])
    booster = member["model"].get_booster()
    p = booster.predict(xgb.DMatrix(x, feature_names=booster.feature_names),
                        iteration_range=(0, booster.num_boosted_rounds()))
    diff = np.abs(p - p_expected[rows])
    print(f"[INFO] tuple-scoring path vs training predictions on {len(rows)} held-out rows: median |diff| "
          f"{np.median(diff):.1e}, max {diff.max():.1e}, {100 * np.mean(diff > 1e-3):.3f}% of rows above 1e-3 "
          "(float32 scoring vs float64 training preprocessing, as in Matias's code)")
    if np.median(diff) > 1e-5:
        print("[WARNING] the tuple-scoring path does not reproduce the legacy model's predictions: check the "
              "preprocessing.")


def stage_apply():
    """Fold-matched scores (event in fold i -> model i) for the nominal and systematic tuples."""
    bundle = kf.load_fold_bundle(test_name, USE_BSCONSTRAIN)
    if not APPEND_VARIABLES:
        print("[INFO] --no-apply: BDT score was not added to the trees")
        return
    for file_type in NOMINAL_TUPLES:
        xgb_utils.append_BDT_score(file_type, channel_US, era, signal_subset, background_subset,
                                   variables[:-3], bundle, USE_BSCONSTRAIN, useRecategorization,
                                   dir_suffix=dir_suffix)
    if doSystematics:
        for file_type in NOMINAL_TUPLES[1:]:  # no Data variations
            xgb_utils.append_BDT_score_to_sys(file_type, channel_US, era, signal_subset, background_subset,
                                              variables[:-3], bundle, USE_BSCONSTRAIN,
                                              dir_suffix=dir_suffix)
    if dir_suffix:
        print(f"[INFO] next: `bash scripts/hadd_bdt.sh {channel_US} {dir_suffix}` then "
              f"`python3 plot_BDT_Categories.py {channel_US} {era} --variant {VARIANT.label}` then "
              f"`bash scripts/run_splitting.sh -v {VARIANT.label}`")


def stage_all():
    stage_final()
    stage_apply()


# training settings that do not change the trained model (e.g. GPU-trained models score on CPU)
REUSE_IGNORED_PARAMS = {"device", "n_jobs", "verbosity", "eval_metric", "missing"}


def param_differences(saved, wanted):
    """["key saved -> wanted", ...] for the model-relevant XGBoost parameters that differ between
    a saved model's meta["params"] and the configuration (a missing key shows as `default`)."""
    out = []
    for key in sorted((set(saved) | set(wanted)) - REUSE_IGNORED_PARAMS):
        a, b = saved.get(key, "default"), wanted.get(key, "default")
        numbers = all(isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool) for v in (a, b))
        if not (math.isclose(a, b, rel_tol=1e-9) if numbers else a == b):
            out.append(f"{key} {a:.4g} -> {b:.4g}" if numbers else f"{key} {a} -> {b}")
    return out


def reusable_bundle(variant, weights_label, n_rounds, params):
    """The variant's saved fold models if they can be reused for --stage compare (same number of
    folds, trees, variables, training weights and hyper-parameters), else None."""
    if OPTS["retrain"]:
        return None
    try:
        bundle = kf.load_fold_bundle(variant.test_name, USE_BSCONSTRAIN)
    except FileNotFoundError:
        print(f"[INFO] no saved models for {variant.test_name}" + ("" if OPTS["plots_only"] else ": training them"))
        return None
    meta = bundle[0]["meta"]
    problems = []
    if len(bundle) != kf.N_FOLDS:
        problems.append(f"{len(bundle)} models instead of {kf.N_FOLDS}")
    if list(meta["variables"]) != names:
        problems.append("trained with a different input variable list")
    if meta.get("training_weights", weights_label) != weights_label:
        problems.append(f"trained with {meta['training_weights']} weights, not {weights_label}")
    if int(meta["n_trees"]) != n_rounds:
        problems.append(f"{meta['n_trees']} trees, the configuration asks for {n_rounds}")
    if "params" not in meta:
        problems.append("no stored hyper-parameters")
    else:
        differences = sorted({d for b in bundle for d in param_differences(b["meta"]["params"], params)})
        if differences:
            problems.append(f"hyper-parameters differ ({', '.join(differences)})")
    if problems:
        print(f"[WARNING] not reusing the models of {variant.test_name} ({'; '.join(problems)})"
              + ("" if OPTS["plots_only"] else ": retraining"))
        return None
    note = "" if "training_weights" in meta else " (saved without training_weights: weights not verified)"
    print(f"[INFO] reusing the saved models of {variant.test_name}{note}")
    return bundle


def tight_category_summary(d, scores, cut):
    """Physics-weighted efficiencies of BDT > cut over the training region, and S/sqrt(B) in the
    signal region (scaled like significance_scan: S and B from the full skims)."""
    passed = scores > cut
    sr = (d.mass > SIGNAL_REGION[0]) & (d.mass < SIGNAL_REGION[1])
    out = {}
    for label, cls in (("signal", 1), ("bkg", 0)):
        sel = d.y == cls
        out[f"eff_{label}"] = d.w_phys[sel & passed].sum() / d.w_phys[sel].sum()
        out[f"eff_{label}_SR"] = d.w_phys[sel & sr & passed].sum() / d.w_phys[sel & sr].sum()
    out["significance"] = (d.signal_events * out["eff_signal_SR"] / math.sqrt(d.bkg_events * out["eff_bkg_SR"])
                           if out["eff_bkg_SR"] > 0 else float("nan"))
    out["cut"] = cut
    return out


def compare_tuple_source(variants):
    """{"background": [paths], "signal": [paths]} of the per-sample compare tuples, if they exist,
    carry every variant's score branch and are newer than every variant's models; else None."""
    files = {}
    for label, samples in COMPARE_SAMPLES.items():
        files[label] = []
        for sample in samples:
            p = xgb_utils.scoring_paths(sample, channel_US, era, signal_subset, background_subset,
                                        useRecategorization, dir_suffix=COMPARE_DIR)
            path = p["BDT_path"] + p["BDT_name"]
            if not os.path.exists(path):
                print(f"[INFO] compare tuple {path} not found: re-evaluating the models")
                return None
            files[label].append(path)
    paths = [path for group in files.values() for path in group]
    suffix = "_bsC" if USE_BSCONSTRAIN else ""
    models = [f"models/model_{v.test_name}_fold{k}{suffix}.json" for v in variants for k in range(kf.N_FOLDS)]
    newest_model = max((os.path.getmtime(m) for m in models if os.path.exists(m)), default=0)
    stale = [path for path in paths if os.path.getmtime(path) < newest_model]
    if stale:
        print(f"[INFO] {len(stale)} compare tuples (e.g. {stale[0]}) are older than the models: "
              "re-evaluating the models")
        return None
    for path in paths:
        with uproot.open(path, **kf.uproot_open_options()) as f:
            missing = [v.branch for v in variants if v.branch not in f["tree_output"]]
        if missing:
            print(f"[INFO] {path} has no {', '.join(missing)}: re-evaluating the models")
            return None
    return files


def load_compare_tuples(files, branches):
    """The training-region rows of the compare tuples with their stored (fold-matched, so OOF)
    scores, in the layout of load_training_data plus `scores` ({branch: scores}). The tuples hold
    the skim's events (same samples and category, 100-180 GeV), so the training-region mask
    selects exactly the rows the models were trained and OOF-scored on."""
    mass_name, rel_err_name, weight_name = (v[0] for v in variables[-3:])
    columns = [mass_name, rel_err_name, weight_name] + list(branches)
    parts = []
    for label in ("background", "signal"):  # background rows first, as load_training_data
        chunks = {c: [] for c in columns}
        for arrays in uproot.iterate({path: "tree_output" for path in files[label]}, columns, library="np",
                                     step_size=xgb_utils.SCORE_CHUNK_ROWS, **kf.uproot_open_options()):
            keep = kf.training_region_mask(arrays[mass_name])
            for c in columns:
                chunks[c].append(arrays[c][keep])
        part = {c: np.concatenate(v) for c, v in chunks.items()}
        print(f"[INFO] {label}: {len(part[mass_name])} rows in the training region from {len(files[label])} "
              "compare tuples")
        parts.append(part)
    bkg, sig = parts

    def signal_region_yield(part):
        m = part[mass_name]
        return part[weight_name][(m > SIGNAL_REGION[0]) & (m < SIGNAL_REGION[1])].sum()

    signal_events, bkg_events = signal_region_yield(sig), signal_region_yield(bkg)
    print(f"[INFO] S = {signal_events:.3f}; B = {bkg_events:.3f}; "
          f"S/sqrt(B) = {signal_events / math.sqrt(bkg_events):.3f}")
    signal_scale = bkg[weight_name].sum() / sig[weight_name].sum()
    y = np.concatenate([np.zeros(len(bkg[mass_name])), np.ones(len(sig[mass_name]))]).astype(np.int8)
    mass, rel_err, w_phys = (np.concatenate([bkg[c], sig[c]]).astype(np.float64)
                             for c in (mass_name, rel_err_name, weight_name))
    d = SimpleNamespace(y=y, mass=mass, rel_err=rel_err, w_phys=w_phys,
                        w_abs=np.abs(np.where(y == 1, w_phys * signal_scale, w_phys)),
                        signal_events=signal_events, bkg_events=bkg_events,
                        scores={b: np.concatenate([bkg[b], sig[b]]) for b in branches})
    if PLOT_MASS_WEIGHTS:
        plot_mass_weights(d, compare_plot_path, f"{channel_US}_compare")
    report_peak_memory("after reading the compare tuples")
    return d


def stage_compare():
    """Train or reuse every COMPARE_VARIANTS model set, compare their OOF scores, and append all
    of their scores to one skimmed copy of each nominal tuple."""
    variants = []
    for w_tag, opt_tag in COMPARE_VARIANTS:
        variant = make_variant(w_tag, opt_tag)
        if opt_tag in OBJECTIVE_OPT_TAG.values() and not os.path.exists(variant.optuna_config_path) \
                and not (OPTS["smoke"] and os.path.exists(variant.optuna_config_path.replace(run_tag, ""))):
            print(f"[WARNING] {variant.optuna_config_path} does not exist: variant {variant.label} skipped "
                  f"(run `python3 train.py {channel_US} {era} --stage dev --objective "
                  f"{dict((v, k) for k, v in OBJECTIVE_OPT_TAG.items())[opt_tag]}` first)")
            continue
        variants.append(variant)
    d, score_source = None, "model"
    if OPTS["plots_only"] and not OPTS["rescore"]:
        files = compare_tuple_source(variants)
        if files is not None:
            d, score_source = load_compare_tuples(files, [v.branch for v in variants]), "compare_tuples"
            print(f"[INFO] plots-only: scores read from {os.path.dirname(files['signal'][0])}/ "
                  "(use --rescore to re-evaluate the models)")
    if d is None:
        d = load_training_data(scheme=None)
    is_bkg = d.y == 0
    tight_cut = OPTS["tight_cut"]
    bundles, results = {}, []
    for variant in variants:
        w_tag, optimized = variant.weight_tag, variant.optimized
        params_source = dict(optimized="AUC Optuna", asimov="Asimov Optuna",
                             asimovFit="Asimov-fit Optuna").get(variant.opt_tag, "DEFAULT_PARAMS")
        scheme = WEIGHT_SCHEMES[w_tag]
        weights_label = training_weights_of(scheme)
        print(f"\n[INFO] ===== variant {variant.label}: {params_source}, "
              f"{weights_label} training weights -> {variant.branch} =====")
        config, params, n_rounds = training_setup(variant)
        bundle = reusable_bundle(variant, weights_label, n_rounds, params)
        if bundle is None and OPTS["plots_only"]:
            sys.exit(f"[ERROR] --plots-only: no reusable models for variant {variant.label} "
                     f"({variant.test_name}); run without --plots-only to train them.")
        trained = bundle is None
        if trained:
            make_plot_dirs(variant.plot_path)
            w_fit = compute_w_fit(scheme, d, variant.plot_path, variant.test_name)
            train_variant(d, w_fit, variant, weights_label, config, params, n_rounds)
            del w_fit
            bundle = kf.load_fold_bundle(variant.test_name, USE_BSCONSTRAIN)
        bundles[variant.branch] = bundle

        # event in fold i -> model i: out-of-fold for every training event, saved or fresh models
        # (the compare tuples store exactly these fold-matched scores)
        if score_source == "compare_tuples":
            oof = d.scores[variant.branch]
        else:
            oof = kf.predict_by_fold(d.x, d.folds, bundle)
        # compared with the physics weights: the training weights differ between the variants
        auc, auc_w = roc_auc_score(d.y, oof), roc_auc_score(d.y, oof, sample_weight=d.w_abs)
        print(f"[INFO] {variant.label} OOF: AUC = {auc:.5f}; |physics|-weighted AUC = {auc_w:.5f}")
        fpr, tpr, points, scan = report_working_points(d.y, oof, d.w_phys, d.mass,
                                                       f"{variant.test_name}_compare", d, return_scan=True)
        if not trained:  # a fresh training already drew it in make_oof_plots
            make_plot_dirs(variant.plot_path)
            xgb_utils.plot_BDT_sculpting(oof[is_bkg], d.mass[is_bkg], d.w_phys[is_bkg], channel_US, era,
                                         variant.plot_path, bdt_divisions=SCULPTING_DIVISIONS, tag="OOF")
        tight = tight_category_summary(d, oof, tight_cut)
        print(f"[INFO] {variant.label} BDT > {tight_cut:g}: signal eff {tight['eff_signal']:.4f}, "
              f"background eff {tight['eff_bkg']:.4f}, S/sqrt(B) {tight['significance']:.4f}")
        results.append(dict(label=variant.label, branch=variant.branch, optimized=optimized,
                            opt_tag=variant.opt_tag,
                            training_weights=weights_label, n_rounds=n_rounds,
                            config_source=bundle[0]["meta"].get("config_source"), score_source=score_source,
                            auc=auc, auc_w_phys=auc_w, working_points=points, tight_category=tight,
                            fpr=fpr, tpr=tpr, scan=scan, oof_bkg=oof[is_bkg]))
        report_peak_memory(f"after variant {variant.label}")

    xgb_utils.plot_variant_roc_overlay(results, era, compare_plot_path, channel_US)
    xgb_utils.plot_variant_significance_scan(results, era, compare_plot_path, channel_US)
    xgb_utils.plot_variant_tight_mass(results, d.mass[is_bkg], d.w_phys[is_bkg], tight_cut, era,
                                      compare_plot_path, channel_US)
    summary_path = f"{compare_plot_path}results/compare_{channel_US}{file_append}_{era}_{subset_title}{run_tag}.json"
    with open(summary_path, "w") as f:
        json.dump([{k: v for k, v in r.items() if k not in ("fpr", "tpr", "scan", "oof_bkg")} for r in results],
                  f, indent=2, default=float)
    cut_column = f"S/sqrtB@{tight_cut:g}"
    print(f"\n[INFO] {'variant':24s} {'AUC':>8s} {'AUC w':>8s} {'max S/sqrtB':>12s} {'threshold':>10s} "
          f"{cut_column:>13s}")
    for r in results:
        best = r["working_points"]["Max"]
        print(f"[INFO] {r['label']:24s} {r['auc']:8.5f} {r['auc_w_phys']:8.5f} "
              f"{best['significance']:12.4f} {best['threshold']:10.4f} "
              f"{r['tight_category']['significance']:13.4f}")
    print(f"[INFO] comparison plots and {summary_path} written under {compare_plot_path}")
    del d

    if not APPEND_VARIABLES:
        print("[INFO] --no-apply: BDT scores were not added to the trees")
        return
    for file_type in NOMINAL_TUPLES:
        xgb_utils.append_BDT_scores_multi(file_type, channel_US, era, signal_subset, background_subset,
                                          variables[:-3], bundles, USE_BSCONSTRAIN, useRecategorization,
                                          dir_suffix=COMPARE_DIR)
    print(f"[INFO] branches {', '.join(bundles)} + BDT_fold written to "
          f"root_io/tuples/BDT_score/{channel_US}{file_append}{COMPARE_DIR}/{subset_title}/")
    print(f"[INFO] next (after both channels): `bash scripts/hadd_bdt.sh {channel_US} {COMPARE_DIR}` then "
          f"`python3 plot_BDT_Categories.py {channel_US} {era} --{COMPARE_DIR} --score <variant>`")


if __name__ == "__main__":
    if OPTS["plots_only"] and OPTS["stage"] != "compare":
        stage_plots()
    else:
        dict(dev=stage_dev, test=stage_test, final=stage_final, apply=stage_apply, all=stage_all,
             legacy=stage_legacy, compare=stage_compare)[OPTS["stage"]]()
