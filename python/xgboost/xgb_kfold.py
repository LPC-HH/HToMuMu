"""K-fold / out-of-fold (OOF) machinery for the H->mumu XGBoost BDT.

Vocabulary used everywhere (variable names, docstrings, plot labels):
  train       events used to fit one particular model
  validation  events used for early stopping and Optuna/model selection
  test        untouched sample, only for the final development-stage evaluation
  OOF         final-analysis prediction of an MC event from the model that
              EXCLUDED that event's fold (event in fold i -> model i)

Statistical rule enforced by this module:
  no MC event used to train model i may receive its final analysis BDT score
  from model i.

Pure-numpy helpers can be checked anywhere with `python xgb_kfold.py --selftest`;
sklearn / xgboost / optuna are imported lazily by the training helpers.
"""
import gc
import json
import os
import pickle
import subprocess
import sys
import time
import warnings

import numpy as np

N_FOLDS = 5
TRAIN_REGION = (115.0, 135.0)  # skim window, see src/SkimTuples*.cc
MASS_BSC = "diMuon_bsConstrainedMass"
EVENT_ID = "event"  # the per-event identifier the fold rule is defined on
# Which hadded skim file holds each subset. The hadd PROCESS ORDER that used to live here was
# needed only to rebuild folds positionally; fold = event % N_FOLDS does not care how the skim
# was concatenated.
SKIM_KIND = {"Full": "background", "NottH": "signal"}

# get_variables() names that must NOT be z-scored. fit_standardizer returns the identity
# (mean 0, std 1) for these, so preprocess_features leaves the column untouched and every
# saved preprocessing map records the identity -- training, scoring and the audit therefore
# cannot disagree about them.
#
# This is cosmetic for the model: XGBoost's tree booster splits on sorted feature values and
# `hist` bins by quantiles, both invariant under an affine per-feature transform, so exempting
# a variable changes predictions only at floating-point level. It is done so that split
# thresholds, tree dumps and feature plots stay in units a physicist can read (and so a
# subtract-then-divide cannot quietly cost float32 precision).
NO_STANDARDIZE_VARIABLES = frozenset({
    # categorical / integer counts: a z-scored index or multiplicity is unreadable
    "mc_campaign", "n_jet", "n_SoftJet_pt2",
    "leading_jet_nConstituents", "subleading_jet_nConstituents",
    # scores already on a natural bounded scale, which z-scoring would destroy
    "leading_jet_btagPNetQvG", "subleading_jet_btagPNetQvG",  # PNet quark-vs-gluon, 0-1
    "pt_balance",    # 0-1 by construction
    "cos_theta_CS",  # -1 to 1
})



# ---------------------------------------------------------------------------
# Fold assignment
# ---------------------------------------------------------------------------
def fold_of_event(event):
    """THE single definition of the fold rule: fold = event % N_FOLDS.

    A property of the EVENT, not of where its row happens to sit. The same physical event
    therefore gets the same fold in the training skim, in the nominal tuple, in every
    systematic variation and in Data -- no matter how the files were ordered, hadded, skimmed
    or re-made, and regardless of the 115/135 boundary difference between the skim cut and
    train.py's. Nothing is stored: every consumer recomputes this in one line from the `event`
    branch of the file it is holding.

    `event` is a ULong64_t in the tuples and must be read as an integer, never through the
    float32 feature matrix -- Data reaches ~6.5e9 and TT ~5.0e8, both well past the 2**24
    where float32 stops being exact.

    Measured balance of `event % 5` on the Run 3 tuples: every fold within 0.13% of 1/5 for
    EWK, ggH, VBF, TT and Data, so no hashing is needed. fold_summary() keeps watching it.
    """
    event = np.asarray(event)
    if event.dtype.kind not in "ui":
        raise TypeError(
            f"the fold rule needs the integer `event` branch, got dtype {event.dtype}. Reading "
            "it as a float would corrupt large event numbers (Data reaches ~6.5e9); read the "
            f"{EVENT_ID!r} branch on its own, not as part of the feature matrix.")
    return (event.astype(np.uint64) % np.uint64(N_FOLDS)).astype(np.int8)


def training_region_mask(mass):
    """Events train.py actually trains on: STRICTLY inside the window. The skim keeps the
    boundaries -- src/SkimTuples*.cc cuts `>= 115 && <= 135` -- while train.py has always cut
    `> 115 && < 135`, which drops the handful of events sitting exactly on 115.0 or 135.0.
    Defined once here so the training and anything checking it cannot disagree. (With
    event-based folds this boundary difference no longer affects any fold assignment; it only
    decides which events are trained on.)"""
    return (np.asarray(mass) > TRAIN_REGION[0]) & (np.asarray(mass) < TRAIN_REGION[1])


def skim_path(skim_dir, era, subset):
    """The hadded skim file holding the rows of `subset`."""
    if subset not in SKIM_KIND:
        raise NotImplementedError(f"unknown skim subset {subset!r} (have {list(SKIM_KIND)})")
    return f"{skim_dir}{SKIM_KIND[subset]}_{era}_skim_{subset}.root"


def uproot_open_options():
    """Options for uproot.open on the big tuples and their scored copies (~12 GB).

    uproot's default source memory-maps the whole file, which on its own eats most of the
    16 GiB per-process virtual-memory limit on the LPC login nodes and makes the next
    allocation fail with MemoryError; this handler reads the file in chunks instead.
    Accepted both by the CMSSW uproot (5.0.7) and by current versions."""
    import uproot

    return dict(file_handler=uproot.MultithreadedFileSource)


def read_columns(path, branches):
    import uproot

    with uproot.open(path, **uproot_open_options()) as f:
        return f["tree_output"].arrays(branches, library="np")


def read_event_ids(path):
    """The `event` branch of one file, as its native unsigned integer.

    Kept separate from read_columns so the actionable error lives in one place: the training
    skims are built by src/SkimTuples*.cc, which whitelists branches explicitly, so a skim made
    before `event` was whitelisted simply will not have it -- and reading the fold from anything
    else is exactly what this design removed."""
    import uproot

    with uproot.open(path, **uproot_open_options()) as f:
        tree = f["tree_output"]
        if EVENT_ID not in tree:
            raise RuntimeError(
                f"{path} has no {EVENT_ID!r} branch, so the fold of each row is unknown. Add "
                f"{EVENT_ID!r} to the branch whitelist in src/SkimTuplesggH.cc and "
                "src/SkimTuples_VBF.cc, rebuild (make -j4) and re-make the skim.")
        return tree[EVENT_ID].array(library="np")


def fold_summary(y, w, folds, label="fold", rel_tolerance=0.05):
    """Unweighted counts and weighted yields per fold; warns on imbalance
    (an even split of the counts does not guarantee an even split of the weights)."""
    rows = []
    tot_s, tot_b = w[y == 1].sum(), w[y == 0].sum()
    print(f"[INFO] {label} summary (n_sig, n_bkg | w_sig, w_bkg | frac of total w_sig, w_bkg)")
    for k in range(N_FOLDS):
        m = folds == k
        row = dict(fold=k, n_sig=int(((y == 1) & m).sum()), n_bkg=int(((y == 0) & m).sum()),
                   w_sig=float(w[(y == 1) & m].sum()), w_bkg=float(w[(y == 0) & m].sum()))
        row["frac_w_sig"] = row["w_sig"] / tot_s if tot_s else np.nan
        row["frac_w_bkg"] = row["w_bkg"] / tot_b if tot_b else np.nan
        rows.append(row)
        print(f"   {label} {k}: {row['n_sig']:>9d} {row['n_bkg']:>9d} | "
              f"{row['w_sig']:.4g} {row['w_bkg']:.4g} | {row['frac_w_sig']:.3f} {row['frac_w_bkg']:.3f}")
        for key in ("frac_w_sig", "frac_w_bkg"):
            if abs(row[key] * N_FOLDS - 1.0) > rel_tolerance:
                warnings.warn(f"{label} {k}: weighted {key[7:]} share {row[key]:.3f} deviates by more "
                              f"than {rel_tolerance:.0%} (relative) from 1/{N_FOLDS}")
    return rows


# ---------------------------------------------------------------------------
# Weighted-histogram statistics (shared by the shape plots)
# ---------------------------------------------------------------------------
def normalized_hist(values, weights, bins, range=None, density=False):
    """Area-normalized weighted histogram with its statistical error.

    The per-bin variance of a weighted histogram is the sum of squared weights. The plots
    then normalize to unit area, n_i = c_i / S with S = sum_j c_j, and numerator and
    denominator move together, so the error is propagated through both:

        dn_i/dc_i = (1 - n_i) / S,   dn_i/dc_j = -n_i / S   (j != i)
        var(n_i)  = [ var_i (1 - 2 n_i) + n_i^2 sum_j var_j ] / S^2

    (bins are independent). The common shortcut sqrt(var_i)/S holds S fixed and overestimates
    slightly. Returns (n, err, edges); with density=True both are divided by the bin width.
    """
    counts, edges = np.histogram(values, bins=bins, range=range, weights=weights)
    var, _ = np.histogram(values, bins=bins, range=range, weights=np.asarray(weights) ** 2)
    total = counts.sum()
    if total <= 0:
        return counts.astype(float), np.zeros_like(counts, dtype=float), edges
    n = counts / total
    variance = (var * (1.0 - 2.0 * n) + n ** 2 * var.sum()) / total ** 2
    err = np.sqrt(np.clip(variance, 0.0, None))
    if density:
        width = np.diff(edges)
        n, err = n / width, err / width
    return n, err, edges


def effective_entries(weights):
    """(sum w)^2 / sum(w^2): the unweighted-equivalent number of events, i.e. the real
    statistical power behind a weighted selection."""
    w = np.asarray(weights, dtype=np.float64)
    denom = (w ** 2).sum()
    return float(w.sum() ** 2 / denom) if denom > 0 else 0.0


# ---------------------------------------------------------------------------
# Preprocessing (per model, from that model's train events only)
# ---------------------------------------------------------------------------
def fit_standardizer(x, names):
    """mean/std per variable over FINITE entries of x (inf/NaN excluded, as in the
    original train.py). std == 0 is replaced by 1 so constant columns stay finite, and the
    names in NO_STANDARDIZE_VARIABLES get the identity (0, 1) instead of a fitted map."""
    mean_map, std_map = {}, {}
    skipped = [n for n in names if n in NO_STANDARDIZE_VARIABLES]
    if skipped:
        print(f"[INFO] not standardized (identity mean/std): {skipped}")
    for i, name in enumerate(names):
        if name in NO_STANDARDIZE_VARIABLES:
            mean_map[name], std_map[name] = 0.0, 1.0
            continue
        col = np.asarray(x[:, i], dtype=np.float64)
        finite = np.isfinite(col)
        if not finite.any():
            mean_map[name], std_map[name] = 0.0, 1.0
            continue
        mean_map[name] = float(col[finite].mean())
        std = float(col[finite].std())
        std_map[name] = std if std > 0 else 1.0
    return mean_map, std_map


def preprocess_features(x, names, do_standardization, mean_map=None, std_map=None, dtype=np.float32):
    """Copy of x with +/-inf -> NaN (NaN kept for XGBoost's native missing-value
    handling) and, if requested, finite entries z-scored with the GIVEN mean/std
    (never computed here, so applying to validation/test/data cannot leak)."""
    out = np.array(x, dtype=dtype, copy=True)
    out[~np.isfinite(out)] = np.nan
    if do_standardization:
        for i, name in enumerate(names):
            finite = np.isfinite(out[:, i])
            out[finite, i] = (out[finite, i] - mean_map[name]) / std_map[name]
    return out


# ---------------------------------------------------------------------------
# Development-stage splits (dev/test and CV folds)
# ---------------------------------------------------------------------------
def split_dev_test(y, test_fraction, seed):
    """Stratified (by class) development / untouched-test split. Deterministic in
    (y, test_fraction, seed), so it is recomputed rather than stored."""
    from sklearn.model_selection import train_test_split

    dev, test = train_test_split(np.arange(len(y)), test_size=test_fraction,
                                 random_state=seed, stratify=y)
    return np.sort(dev), np.sort(test)


def cv_fold_indices(y_dev, seed):
    """List of (train_idx, validation_idx) into the dev arrays."""
    from sklearn.model_selection import StratifiedKFold

    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
    return [(tr, va) for tr, va in skf.split(np.zeros(len(y_dev)), y_dev)]


# ---------------------------------------------------------------------------
# Training helpers
# ---------------------------------------------------------------------------
_GPU_NOTE_PROBED = {"usable": None}  # None = not tried yet, False = no readout on this node


def gpu_memory_note():
    """"gpu0 used/total MiB" for the visible GPUs, or "" when there is no way to ask.

    This exists to make a climbing device footprint visible: 50 fits in one process with
    `device="cuda"` is how `--stage dev` wedged the pod. It is probed once per process and the
    "not available" answer is cached, so on a node without a driver it becomes a no-op.

    Deliberately does NOT use pynvml. In the CMSSW environment pynvml imports fine but links a
    stub libnvidia-ml from cvmfs, and nvmlInit() then writes a ten-line banner (plus a `cut:
    write error` from its own internals) straight to this process's stderr at the C level,
    where no try/except can catch it -- 50 calls would bury the log it is meant to clarify.
    `nvidia-smi` runs in a child process whose streams we control.
    """
    if _GPU_NOTE_PROBED["usable"] is False:
        return ""
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, timeout=10, check=True).stdout
        parts = []
        for i, line in enumerate(out.strip().splitlines()):
            used, total = (int(v) for v in line.split(",")[:2])  # raises unless it really parsed
            parts.append(f"gpu{i} {used}/{total} MiB")
        if not parts:
            raise ValueError("nvidia-smi returned no GPU rows")
        _GPU_NOTE_PROBED["usable"] = True
        return ", ".join(parts)
    except Exception:
        _GPU_NOTE_PROBED["usable"] = False
        return ""


def base_xgb_params(device="cuda", n_jobs=4):
    # eval_metric order matters: XGBoost early-stops on the LAST metric of the LAST
    # eval_set, so logloss (as in the original Optuna objective) drives early stopping.
    return dict(objective="binary:logistic", eval_metric=["auc", "logloss"], device=device,
                n_jobs=n_jobs, verbosity=0, missing=np.nan)


def n_trees_used(model, n_estimators):
    try:
        return int(model.best_iteration) + 1
    except (AttributeError, TypeError):
        return int(n_estimators)


def predict_model(model, x, n_trees=None):
    """P(signal) from a fitted XGBClassifier using exactly `n_trees` trees."""
    n_trees = n_trees or n_trees_used(model, model.get_params().get("n_estimators", 0))
    return model.predict_proba(x, iteration_range=(0, int(n_trees)))[:, 1]


def weighted_metrics(y, p, w):
    from sklearn.metrics import log_loss, roc_auc_score

    p = np.clip(p, 1e-7, 1 - 1e-7)
    return dict(
        auc_w=float(roc_auc_score(y, p, sample_weight=w)),
        auc=float(roc_auc_score(y, p)),
        logloss_w=float(log_loss(y, p, sample_weight=w, labels=[0, 1])),
        logloss=float(log_loss(y, p, labels=[0, 1])),
    )


def make_progress_callback(label, total, every):
    """XGBoost callback printing '[PROGRESS] <label>: round n/N | elapsed | rounds/s |
    ETA | metrics' every `every` rounds (and at round 1 and the last round)."""
    import time

    import xgboost as xgb

    class _Progress(xgb.callback.TrainingCallback):
        def __init__(self):
            self.t0 = time.time()

        def after_iteration(self, model, epoch, evals_log):
            n = epoch + 1
            if n == 1 or n % every == 0 or n == total:
                elapsed = time.time() - self.t0
                rate = n / max(elapsed, 1e-9)
                metrics = ", ".join(f"{d}-{m}={v[-1]:.5f}" for d, ms in evals_log.items() for m, v in ms.items())
                print(f"[PROGRESS] {label}: round {n}/{total} | {elapsed:.0f}s | {rate:.2f} rounds/s | "
                      f"ETA {(total - n) / rate:.0f}s | {metrics}", flush=True)
            return False

    return _Progress()


def _subset_index(n, max_rows, seed):
    """Sorted random subset of range(n) with at most max_rows elements; None = use all."""
    if not max_rows or n <= max_rows:
        return None
    return np.sort(np.random.default_rng(seed).choice(n, size=int(max_rows), replace=False))


# ---------------------------------------------------------------------------
# Stage 2: cross-validation on the development sample
# ---------------------------------------------------------------------------
def prepare_cv_data(x, y, w, folds, names, do_standardization):
    """Per-fold DESCRIPTORS: the row indices plus the standardizer fitted on that fold's
    TRAIN events only (no leakage from validation). Independent of the Optuna trial, so it
    is built once and reused by every trial.

    The feature matrices are deliberately NOT built here. Holding all N_FOLDS of them at
    once was 7.9 GB on the ggH development sample (5 x 16.4M rows x 24 features), which is
    what made `--stage dev` exhaust the node. Call fold_matrices(fd) for one fold and drop
    the result before moving to the next; the arrays it returns are exactly the ones this
    function used to return.
    """
    cv = []
    for k, (tr, va) in enumerate(folds):
        mean_map, std_map = fit_standardizer(x[tr], names) if do_standardization else ({}, {})
        cv.append(dict(
            fold=k, tr_idx=tr, va_idx=va, mean_map=mean_map, std_map=std_map,
            n_train=int(len(tr)), n_val=int(len(va)),
            # shared base arrays, not copies: fold_matrices() slices them on demand
            _x=x, _y=y, _w=w, _names=list(names), _do_standardization=bool(do_standardization),
        ))
    return cv


def fold_matrices(fd):
    """One fold's preprocessed train/validation matrices, built on demand from the base
    arrays the descriptor points at. Let the result go out of scope before the next fold."""
    x, names, do_std = fd["_x"], fd["_names"], fd["_do_standardization"]
    tr, va = fd["tr_idx"], fd["va_idx"]
    return dict(
        x_tr=preprocess_features(x[tr], names, do_std, fd["mean_map"], fd["std_map"]),
        y_tr=fd["_y"][tr], w_tr=fd["_w"][tr],
        x_va=preprocess_features(x[va], names, do_std, fd["mean_map"], fd["std_map"]),
        y_va=fd["_y"][va], w_va=fd["_w"][va],
    )


def train_one_fold(fd, mats, params, n_estimators, early_stopping_rounds, verbose=False,
                   progress_every=0, monitor_max_rows=None, lean=False):
    """Fit one model on the fold's train events with eval_set = [train, validation] ONLY
    (no test). Early stopping (if any) uses the FULL validation set. The train entry of
    eval_set is only a monitoring curve, so it may be a random subset of at most
    `monitor_max_rows` events (evaluating AUC on ~10^7 events every round is very costly).

    `mats` is this fold's fold_matrices(fd); it is passed in rather than read off `fd` so
    the caller controls when it is freed.

    `lean` is for Optuna trials, where nothing reads the monitoring curves: it drops the train
    entry of eval_set (one fewer copy of ~10^6 rows on the device, and no per-round metric on
    it) and evaluates logloss only. Neither changes what the trial reports -- early stopping
    uses the LAST eval_set and the LAST metric, which are still the validation fold and
    logloss, and the objective's weighted AUC is computed from the predictions afterwards by
    weighted_metrics(), never from evals_result()."""
    import xgboost as xgb

    x_tr, y_tr, w_tr = mats["x_tr"], mats["y_tr"], mats["w_tr"]
    if lean:
        params = dict(params, eval_metric=["logloss"])
        eval_set = [(mats["x_va"], mats["y_va"])]
        eval_weights = [mats["w_va"]]
    else:
        sel = _subset_index(len(y_tr), monitor_max_rows, seed=fd["fold"])
        x_mon, y_mon, w_mon = (x_tr, y_tr, w_tr) if sel is None else (x_tr[sel], y_tr[sel], w_tr[sel])
        eval_set = [(x_mon, y_mon), (mats["x_va"], mats["y_va"])]
        eval_weights = [w_mon, mats["w_va"]]
    callbacks = [make_progress_callback(f"CV fold {fd['fold']}", n_estimators, progress_every)] \
        if progress_every else None
    model = xgb.XGBClassifier(**params, n_estimators=n_estimators,
                              early_stopping_rounds=early_stopping_rounds, callbacks=callbacks)
    model.fit(x_tr, y_tr, sample_weight=w_tr, eval_set=eval_set,
              sample_weight_eval_set=eval_weights, verbose=verbose)
    # the progress callback is a local (unpicklable) object: detach it. Plain attribute
    # assignment; set_params() on a fitted model would push eval_metric into the booster.
    model.callbacks = None
    return model


def evaluate_one_fold(model, fd, mats, n_estimators):
    """Validation metrics + loss/AUC curves for one trained fold model."""
    n_used = n_trees_used(model, n_estimators)
    p_va = predict_model(model, mats["x_va"], n_used)
    res = model.evals_result()
    # the validation fold is always the LAST eval_set; with lean=True it is the ONLY one, and
    # there is no train monitoring curve to report
    val_key = "validation_1" if "validation_1" in res else "validation_0"
    info = weighted_metrics(mats["y_va"], p_va, mats["w_va"])
    info.update(
        fold=fd["fold"], n_trees_used=n_used, best_iteration=n_used - 1,
        n_train=int(len(mats["y_tr"])), n_val=int(len(mats["y_va"])),
        train_logloss=[] if val_key == "validation_0" else list(res["validation_0"]["logloss"]),
        val_logloss=list(res[val_key]["logloss"]),
    )
    return info, p_va


def cross_validate_config(cv_data, params, n_estimators, early_stopping_rounds, keep_models=False,
                          trial=None, verbose=False, progress_every=0, monitor_max_rows=None,
                          lean=False, label=""):
    """Train on N_FOLDS-1 folds / validate on the remaining one, for every fold. Returns
    the per-fold infos, the mean weighted validation AUC (the Optuna objective) and,
    optionally, the models and their validation predictions (the dev-sample OOF).

    `lean` is passed to train_one_fold for Optuna trials (see there). `label` prefixes the
    per-fold log line."""
    infos, models, preds = [], [], []
    for fd in cv_data:
        # one fold's matrices at a time: all N_FOLDS at once is several GB on ggH
        mats = fold_matrices(fd)
        model = train_one_fold(fd, mats, params, n_estimators, early_stopping_rounds, verbose,
                               progress_every=progress_every, monitor_max_rows=monitor_max_rows,
                               lean=lean)
        info, p_va = evaluate_one_fold(model, fd, mats, n_estimators)
        infos.append(info)
        if keep_models:
            models.append(model)
            preds.append(p_va)
        # Release this fold's device and host memory BEFORE the next fit. XGBoost's sklearn
        # wrapper and the early-stopping callback form reference cycles, so refcounting alone
        # does not return the booster's GPU allocation; with 5 folds x N trials in one process
        # that is what exhausts the device.
        del mats
        if not keep_models:
            del model
        gc.collect()
        if progress_every:
            note = gpu_memory_note()
            print(f"[CV   ] {label}fold {fd['fold']}: {info['n_trees_used']} trees, "
                  f"weighted validation AUC {info['auc_w']:.5f}, logloss {info['logloss_w']:.5f}"
                  + (f" | {note}" if note else ""), flush=True)
        if trial is not None:
            trial.report(float(np.mean([i["auc_w"] for i in infos])), step=fd["fold"])
            if trial.should_prune():
                import optuna
                raise optuna.TrialPruned()
    return dict(infos=infos, mean_auc_w=float(np.mean([i["auc_w"] for i in infos])),
                std_auc_w=float(np.std([i["auc_w"] for i in infos])), models=models, preds=preds)


def run_optuna_cv(cv_data, n_trials, seed, device, n_estimators, early_stopping_rounds,
                  monitor_max_rows=None, progress_every=0):
    """Optuna study whose objective is the MEAN weighted validation AUC over all folds
    (same search space as the original single-split objective).

    This used to run completely silently: on the ggH development sample that meant hours with
    no output and no way to tell a slow trial from a wedged pod. It now logs every trial and
    every fold, with GPU memory where it can be read, and trains the folds in `lean` mode
    (see train_one_fold) -- which changes the cost of a trial, not its reported value.
    """
    import optuna

    # a per-round heartbeat inside a fold, but ~10 lines per fold rather than one per 10 rounds:
    # 10 trials x 5 folds x hundreds of rounds would otherwise bury the log
    trial_progress = max(1, n_estimators // 10) if progress_every else 0
    state = dict(n=0, best=None)
    note = gpu_memory_note()
    print(f"[OPTUNA] {n_trials} trials x {N_FOLDS} folds, up to {n_estimators} rounds "
          f"(early stopping {early_stopping_rounds}), device={device}"
          + (f" | {note}" if note else " | no GPU readout available"), flush=True)

    def objective(trial):
        state["n"] += 1
        tag = f"trial {state['n']}/{n_trials} "
        params = base_xgb_params(device)
        params.update(
            max_depth=trial.suggest_int("max_depth", 2, 5),
            learning_rate=trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            min_child_weight=trial.suggest_float("min_child_weight", 1.0, 20.0, log=True),
            subsample=trial.suggest_float("subsample", 0.6, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 1.0),
            reg_lambda=trial.suggest_float("reg_lambda", 0.1, 10.0, log=True),
            reg_alpha=trial.suggest_float("reg_alpha", 1e-4, 1.0, log=True),
        )
        print(f"[OPTUNA] {tag}start: " + ", ".join(
            f"{k}={v:.4g}" if isinstance(v, float) else f"{k}={v}"
            for k, v in trial.params.items()), flush=True)
        t0 = time.time()
        try:
            res = cross_validate_config(cv_data, params, n_estimators, early_stopping_rounds,
                                        trial=trial, monitor_max_rows=monitor_max_rows,
                                        progress_every=trial_progress, lean=True, label=tag)
        except optuna.TrialPruned:
            print(f"[OPTUNA] {tag}pruned after {time.time() - t0:.1f} s", flush=True)
            raise
        trial.set_user_attr("fold_auc_w", [i["auc_w"] for i in res["infos"]])
        trial.set_user_attr("fold_best_iteration", [i["best_iteration"] for i in res["infos"]])
        state["best"] = res["mean_auc_w"] if state["best"] is None \
            else max(state["best"], res["mean_auc_w"])
        print(f"[OPTUNA] {tag}done in {time.time() - t0:.1f} s: mean weighted validation AUC "
              f"{res['mean_auc_w']:.5f} (best so far {state['best']:.5f})", flush=True)
        return res["mean_auc_w"]

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed),
                               pruner=optuna.pruners.MedianPruner(n_startup_trials=10, n_warmup_steps=1))
    study.optimize(objective, n_trials=n_trials)
    return study


def summarize_best_iterations(best_iterations):
    it = np.asarray(best_iterations, dtype=float)
    return dict(best_iterations=[int(i) for i in it], mean=float(it.mean()),
                median=float(np.median(it)), min=int(it.min()), max=int(it.max()))


def choose_n_rounds(best_iterations, scale=1.0):
    """Proposed policy: median over folds of (best_iteration + 1), times `scale`
    (1.0 = unscaled). The held-out fold of the final models is never used for early
    stopping, so the number of rounds must be fixed beforehand."""
    return max(1, int(round(float(np.median(np.asarray(best_iterations) + 1)) * scale)))


# ---------------------------------------------------------------------------
# Frozen configuration (development stage -> final training)
# ---------------------------------------------------------------------------
def jsonable_params(params):
    return {k: ("nan" if isinstance(v, float) and np.isnan(v) else v) for k, v in params.items()}


def make_config(device, tuned_params, n_rounds, source):
    """A frozen training configuration: the XGBoost params (the shared defaults plus
    `tuned_params`), the fixed number of boosting rounds, and where they came from."""
    params = base_xgb_params(device)
    params.update(tuned_params)
    return dict(source=source, params=jsonable_params(params), n_rounds=int(n_rounds))


def params_from_config(config, device=None):
    params = dict(config["params"])
    params["missing"] = np.nan
    if device:
        params["device"] = device
    return params


def save_frozen_config(path, config):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))


def load_frozen_config(path):
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Stage 3: independent test evaluation (once)
# ---------------------------------------------------------------------------
def guard_test_evaluation(marker_path, force=False):
    if os.path.exists(marker_path) and not force:
        raise RuntimeError(
            f"{marker_path} exists: the untouched test sample was already evaluated for this "
            "configuration. Evaluating it again invites tuning on it; use --force-retest only "
            "if the configuration was NOT changed based on the previous result."
        )


def evaluate_on_test(x, y, w, dev_idx, test_idx, names, do_standardization, config, device,
                     dev_cv_bundle=None):
    """Refit the frozen configuration on ALL of the development sample (fixed number of
    rounds; the test sample is never given to fit) and evaluate it on the test sample
    once. Also scores the test sample with the dev CV models, for comparison."""
    import xgboost as xgb

    mean_map, std_map = fit_standardizer(x[dev_idx], names) if do_standardization else ({}, {})
    x_dev = preprocess_features(x[dev_idx], names, do_standardization, mean_map, std_map)
    x_test = preprocess_features(x[test_idx], names, do_standardization, mean_map, std_map)
    model = xgb.XGBClassifier(**params_from_config(config, device), n_estimators=int(config["n_rounds"]))
    # eval_set = the dev training data ONLY (train-curve monitoring); test never enters fit.
    model.fit(x_dev, y[dev_idx], sample_weight=w[dev_idx],
              eval_set=[(x_dev, y[dev_idx])], sample_weight_eval_set=[w[dev_idx]], verbose=False)
    p_test = predict_model(model, x_test, int(config["n_rounds"]))
    result = dict(refit=weighted_metrics(y[test_idx], p_test, w[test_idx]), p_test=p_test,
                  cv_models_on_test=[])
    for member in dev_cv_bundle or []:
        p = score_member(member, x[test_idx])
        result["cv_models_on_test"].append(dict(fold=member["fold"],
                                                **weighted_metrics(y[test_idx], p, w[test_idx])))
    return result


# ---------------------------------------------------------------------------
# Stage 4: final K-fold analysis models
# ---------------------------------------------------------------------------
def train_final_kfold(x, y, w, folds, names, do_standardization, params, n_rounds, verbose=False,
                      progress_every=0, monitor_max_rows=None, in_fold_max_rows=None,
                      on_model_done=None):
    """Train N_FOLDS analysis models on ALL MC. Model i is trained on every event whose
    fold != i; the events of fold i receive their OOF prediction from model i. Fixed
    number of rounds and NO early stopping (the held-out fold is only passed as eval_set
    to draw loss curves; it cannot influence training).

    Speed: the two monitoring entries of eval_set are random subsets of at most
    `monitor_max_rows` events (curves only; the reported OOF metrics use ALL held-out
    events), and the in-fold predictions kept for the overtraining plot use at most
    `in_fold_max_rows` training events per model. `on_model_done(member)` is called as
    soon as each model is trained (train.py saves it there), so a later failure cannot
    lose models that already took hours to train."""
    import xgboost as xgb

    members, p_in_fold = [], []
    oof = np.full(len(y), np.nan, dtype=np.float64)
    for i in range(N_FOLDS):
        tr, ho = np.flatnonzero(folds != i), np.flatnonzero(folds == i)
        mean_map, std_map = fit_standardizer(x[tr], names) if do_standardization else ({}, {})
        x_tr = preprocess_features(x[tr], names, do_standardization, mean_map, std_map)
        x_ho = preprocess_features(x[ho], names, do_standardization, mean_map, std_map)
        mt, mh = _subset_index(len(tr), monitor_max_rows, i), _subset_index(len(ho), monitor_max_rows, 100 + i)
        xt, yt, wt = (x_tr, y[tr], w[tr]) if mt is None else (x_tr[mt], y[tr][mt], w[tr][mt])
        xh, yh, wh = (x_ho, y[ho], w[ho]) if mh is None else (x_ho[mh], y[ho][mh], w[ho][mh])
        callbacks = [make_progress_callback(f"final model {i + 1}/{N_FOLDS}", int(n_rounds), progress_every)] \
            if progress_every else None

        print(f"[INFO] training final model {i + 1}/{N_FOLDS} (holds out fold {i}): {len(tr)} train "
              f"events, {int(n_rounds)} rounds, device={params.get('device')}", flush=True)
        model = xgb.XGBClassifier(**params, n_estimators=int(n_rounds), callbacks=callbacks)
        model.fit(x_tr, y[tr], sample_weight=w[tr], eval_set=[(xt, yt), (xh, yh)],
                  sample_weight_eval_set=[wt, wh], verbose=verbose)
        model.callbacks = None  # detach the local (unpicklable) progress callback

        oof[ho] = predict_model(model, x_ho, n_rounds)
        pos = _subset_index(len(tr), in_fold_max_rows, 200 + i)
        pos = np.arange(len(tr)) if pos is None else pos
        p_in_fold.append(dict(idx=tr[pos], p=predict_model(model, x_tr[pos], n_rounds)))
        res = model.evals_result()
        members.append(dict(
            model=model, fold=i, mean_map=mean_map, std_map=std_map, n_trees=int(n_rounds),
            n_train=int(len(tr)), n_heldout=int(len(ho)),
            train_logloss=list(res["validation_0"]["logloss"]),
            val_logloss=list(res["validation_1"]["logloss"]),
            heldout_metrics=weighted_metrics(y[ho], oof[ho], w[ho]),
        ))
        if on_model_done is not None:
            on_model_done(members[-1])
        print(f"[INFO] finished final model {i + 1}/{N_FOLDS} (held out fold {i}): trained on {len(tr)} "
              f"events, OOF on {len(ho)}; held-out weighted AUC = "
              f"{members[-1]['heldout_metrics']['auc_w']:.4f}", flush=True)
    if np.isnan(oof).any():
        raise RuntimeError("some events did not receive an OOF prediction")
    return members, oof, p_in_fold


# ---------------------------------------------------------------------------
# Legacy single 60/40 split (the pre-K-fold approach), kept for A/B comparison
# ---------------------------------------------------------------------------
def legacy_split(n_events, test_fraction, seed):
    """The split the analysis used before K-fold: one random, UNSTRATIFIED train/test
    partition. Reproduces the original call
        train_test_split(x, y, train_size=1-f, test_size=f, random_state=seed)
    exactly -- train_test_split permutes by sample count, not by array content, so passing
    an index array yields the same partition the original code got from (x, y)."""
    from sklearn.model_selection import train_test_split

    train_idx, test_idx = train_test_split(np.arange(int(n_events)),
                                           train_size=1.0 - test_fraction,
                                           test_size=test_fraction, random_state=seed)
    return np.sort(train_idx), np.sort(test_idx)


def train_single_model(x, y, w, train_idx, eval_idx, names, do_standardization, params,
                       n_rounds, progress_every=0, monitor_max_rows=None, in_fold_max_rows=None,
                       verbose=False):
    """One model on `train_idx`, the legacy approach. Preprocessing is fitted on the training
    rows only, exactly as for a fold model, so the two differ only in how the rows were split.
    `eval_idx` is passed as eval_set for the loss curve only -- nothing is stopped on it,
    matching the original script, which fixed the number of rounds. Returns the member, its
    predictions on `eval_idx`, and its predictions on (a subset of) its own training rows,
    which the discriminator overlay needs to show train vs held-out."""
    import xgboost as xgb

    mean_map, std_map = fit_standardizer(x[train_idx], names) if do_standardization else ({}, {})
    x_tr = preprocess_features(x[train_idx], names, do_standardization, mean_map, std_map)
    x_ev = preprocess_features(x[eval_idx], names, do_standardization, mean_map, std_map)
    mt = _subset_index(len(train_idx), monitor_max_rows, 0)
    me = _subset_index(len(eval_idx), monitor_max_rows, 1)
    xt, yt, wt = (x_tr, y[train_idx], w[train_idx]) if mt is None else \
        (x_tr[mt], y[train_idx][mt], w[train_idx][mt])
    xe, ye, we = (x_ev, y[eval_idx], w[eval_idx]) if me is None else \
        (x_ev[me], y[eval_idx][me], w[eval_idx][me])
    callbacks = [make_progress_callback("legacy model", int(n_rounds), progress_every)] \
        if progress_every else None

    print(f"[INFO] training the legacy single model on {len(train_idx)} events "
          f"({len(eval_idx)} held out), {int(n_rounds)} rounds, device={params.get('device')}",
          flush=True)
    model = xgb.XGBClassifier(**params, n_estimators=int(n_rounds), callbacks=callbacks)
    model.fit(x_tr, y[train_idx], sample_weight=w[train_idx],
              eval_set=[(xt, yt), (xe, ye)], sample_weight_eval_set=[wt, we], verbose=verbose)
    model.callbacks = None  # detach the local (unpicklable) progress callback

    p_eval = predict_model(model, x_ev, n_rounds)
    pos = _subset_index(len(train_idx), in_fold_max_rows, 2)
    pos = np.arange(len(train_idx)) if pos is None else pos
    in_fold = dict(idx=train_idx[pos], p=predict_model(model, x_tr[pos], n_rounds))
    res = model.evals_result()
    member = dict(model=model, fold=0, mean_map=mean_map, std_map=std_map, n_trees=int(n_rounds),
                  n_train=int(len(train_idx)), n_heldout=int(len(eval_idx)),
                  train_logloss=list(res["validation_0"]["logloss"]),
                  val_logloss=list(res["validation_1"]["logloss"]),
                  heldout_metrics=weighted_metrics(y[eval_idx], p_eval, w[eval_idx]))
    return member, p_eval, in_fold


# ---------------------------------------------------------------------------
# Saving / loading the fold models and scoring with them
# ---------------------------------------------------------------------------
def save_fold_models(members, test_name, use_bsConstrain, names, do_standardization, params,
                     seed, models_dir="models", extra_meta=None, n_folds=None):
    """model_<name>_fold<k>[_bsC].{pkl,json} plus preprocessing_<name>_fold<k>[_bsC].pkl
    (the mean/std derived from that model's own training events). Called before any
    plotting helper renames booster features."""
    import xgboost

    os.makedirs(models_dir, exist_ok=True)
    suffix = "_bsC" if use_bsConstrain else ""
    for mem in members:
        base = f"{test_name}_fold{mem['fold']}{suffix}"
        with open(f"{models_dir}/model_{base}.pkl", "wb") as f:
            pickle.dump(mem["model"], f)
        mem["model"].get_booster().save_model(f"{models_dir}/model_{base}.json")  # native, version-stable
        meta = dict(variables=list(names), mean_map=mem["mean_map"], std_map=mem["std_map"],
                    do_standardization=bool(do_standardization), fold=mem["fold"],
                    n_folds=N_FOLDS if n_folds is None else int(n_folds),
                    seed=seed, n_trees=mem["n_trees"], params=jsonable_params(params),
                    xgboost_version=xgboost.__version__, n_train=mem["n_train"],
                    heldout_metrics=mem["heldout_metrics"], **(extra_meta or {}))
        with open(f"{models_dir}/preprocessing_{base}.pkl", "wb") as f:
            pickle.dump(meta, f)


def load_fold_bundle(test_name, use_bsConstrain, models_dir="models"):
    """All models of a set as native Boosters (robust to xgboost version changes) with their
    own preprocessing. The member count is read from fold 0's metadata, so this loads a
    5-fold analysis set and a 1-model legacy set through the same code."""
    import xgboost as xgb

    suffix = "_bsC" if use_bsConstrain else ""
    with open(f"{models_dir}/preprocessing_{test_name}_fold0{suffix}.pkl", "rb") as f:
        n_models = int(pickle.load(f)["n_folds"])
    bundle = []
    for k in range(n_models):
        base = f"{test_name}_fold{k}{suffix}"
        with open(f"{models_dir}/preprocessing_{base}.pkl", "rb") as f:
            meta = pickle.load(f)
        if meta["fold"] != k or meta["n_folds"] != n_models:
            raise RuntimeError(f"inconsistent fold metadata in preprocessing_{base}.pkl")
        booster = xgb.Booster()
        booster.load_model(f"{models_dir}/model_{base}.json")
        try:  # models are trained on GPU; scoring must also work on CPU-only nodes
            booster.set_param({"device": "cpu"})
        except Exception:
            pass
        bundle.append(dict(booster=booster, meta=meta, fold=k))
    if len({tuple(b["meta"]["variables"]) for b in bundle}) != 1:
        raise RuntimeError("fold models were trained with different variable lists")
    return bundle


def score_member(member, x_raw, n_trees=None):
    """Score raw (unstandardized) features with ONE fold model, using its own preprocessing.

    `n_trees` truncates the model to its first N trees (default: the count it was trained
    with). NOTE: XGBoost reads an `iteration_range` END of 0 as "use every tree", so 0 must
    never be passed here expecting an empty model."""
    import xgboost as xgb

    meta = member["meta"]
    x = preprocess_features(x_raw, meta["variables"], meta["do_standardization"],
                            meta["mean_map"], meta["std_map"])
    booster = member["booster"] if "booster" in member else member["model"].get_booster()
    dmatrix = xgb.DMatrix(x, missing=np.nan, feature_names=booster.feature_names)
    n = int(meta["n_trees"]) if n_trees is None else int(n_trees)
    return np.asarray(booster.predict(dmatrix, iteration_range=(0, n)), dtype=np.float32)


def predict_by_fold(x_raw, folds, bundle):
    """The analysis scoring rule: event in fold i -> model i (which excluded it)."""
    folds = np.asarray(folds)
    scores = np.full(len(x_raw), np.nan, dtype=np.float32)
    for member in bundle:
        sel = folds == member["fold"]
        if sel.any():
            scores[sel] = score_member(member, x_raw[sel])
    if len(scores) and np.isnan(scores).any():
        raise RuntimeError("some events were not scored (fold ids outside 0..N_FOLDS-1?)")
    return scores


# ---------------------------------------------------------------------------
# Log loss vs boosting round, recomputed from the saved models
# ---------------------------------------------------------------------------
def round_grid(n_rounds, step):
    """Tree counts at which a truncated model is evaluated: round 1, every `step`-th round,
    and always the final round.

    The grid NEVER contains 0. XGBoost reads an `iteration_range` end of 0 as "use all
    trees", so a 0 here would silently draw the fully-trained model as if it were round
    zero -- a wrong plot rather than an error."""
    n_rounds, step = int(n_rounds), max(1, int(step))
    if n_rounds < 1:
        raise ValueError(f"n_rounds must be >= 1, got {n_rounds}")
    return np.array(sorted({1, *range(step, n_rounds + 1, step), n_rounds}), dtype=int)


def logloss_vs_rounds(member, x_raw, y, w, rounds, clip=1e-7):
    """Weighted log loss of ONE saved model as a function of the number of trees used.

    `member` is a load_fold_bundle entry (booster + meta). The member's own preprocessing
    and the DMatrix are built ONCE and reused for every entry of `rounds` -- that is the
    point of this helper, and why it does not go through score_member, which would redo
    both for every grid point.

    `w` must be the TRAINING weights (w_fit) so the values land on the same scale as the
    per-round curves XGBoost recorded during training: its `logloss` metric is
    sum(w*l)/sum(w), which is what sklearn's weighted log_loss computes as well."""
    import xgboost as xgb
    from sklearn.metrics import log_loss

    meta = member["meta"]
    x = preprocess_features(x_raw, meta["variables"], meta["do_standardization"],
                            meta["mean_map"], meta["std_map"])
    booster = member["booster"] if "booster" in member else member["model"].get_booster()
    dmatrix = xgb.DMatrix(x, missing=np.nan, feature_names=booster.feature_names)
    out = np.empty(len(rounds), dtype=np.float64)
    for j, r in enumerate(rounds):
        p = np.asarray(booster.predict(dmatrix, iteration_range=(0, int(r))), dtype=np.float64)
        out[j] = log_loss(y, np.clip(p, clip, 1 - clip), sample_weight=w, labels=[0, 1])
    return out


def subsample_rows(rows, max_rows=None, seed=0):
    """Sorted subsample of an index array, or the array itself when it already fits.

    Draw this ONCE at the call site when several models must be compared on the same events:
    evaluating them on identical rows makes the differences between their curves a PAIRED
    measurement, so the subsampling noise largely cancels and the comparison is far tighter
    than each curve's own noise suggests."""
    rows = np.asarray(rows)
    sub = _subset_index(len(rows), max_rows, seed)
    return rows if sub is None else rows[sub]


def curve_on_rows(member, x_raw, y, w, rows, rounds, max_rows=None, seed=0, label="",
                  progress=True):
    """Weighted log loss vs tree count for ONE model on (a subsample of) `rows`.

    Returns (curve, n_rows, n_eff). `n_eff` is the effective entries behind the slice: with
    concentrated weights it is far below n_rows and it, not n_rows, sets the noise floor."""
    import time

    rows = subsample_rows(rows, max_rows, seed)
    if len(rows) == 0:
        raise RuntimeError(f"{label or 'curve'}: no events in the given pool")
    if len(np.unique(y[rows])) < 2:
        raise RuntimeError(f"{label or 'curve'}: only one class in {len(rows)} events -- "
                           "cannot compute a log loss")
    t0 = time.time()
    curve = logloss_vs_rounds(member, x_raw[rows], y[rows], w[rows], rounds)
    n_eff = effective_entries(w[rows])
    if progress:
        print(f"[PROGRESS] loss curve: {label:28s} | {len(rows)} rows (N_eff {n_eff:.0f}) "
              f"| {len(rounds)} grid points | {time.time() - t0:.0f}s", flush=True)
    return curve, int(len(rows)), n_eff


def kfold_logloss_curves(bundle, x_raw, y, w, folds, oof_idx, in_fold_idx, rounds,
                         max_rows=None, seed=900, progress=True):
    """For every fold model, weighted log loss vs tree count on two slices:

      out-of-fold : events of `oof_idx` the model EXCLUDED     (folds == k)
      in-fold     : events of `in_fold_idx` the model TRAINED on (folds != k)

    The two pools are separate arguments on purpose. The out-of-fold pool should be the
    held-out 40% of the single split, so the K-fold and no-k-fold out-of-sample curves land on
    the same events; the in-fold pool should be the single split's own TRAIN 60%, so the
    K-fold and no-k-fold in-sample curves land on the same events too. Using one pool for both
    (an earlier version of this function) silently compared in-sample curves across different
    event pools.

    `oof_idx` / `in_fold_idx` index into the full-length `x_raw`/`y`/`w`/`folds` -- pass those
    whole and let this function index them, so only the <= max_rows subsample is materialized.

    Returns the per-fold matrices rather than means; the caller decides how to summarize."""
    oof_idx, in_fold_idx = np.asarray(oof_idx), np.asarray(in_fold_idx)
    f_oof, f_in = np.asarray(folds)[oof_idx], np.asarray(folds)[in_fold_idx]
    rounds = np.asarray(rounds, dtype=int)
    res = dict(rounds=rounds, oof=[], in_fold=[], n_rows_oof=[], n_rows_in_fold=[],
               n_eff_oof=[], n_eff_in_fold=[], max_rows=max_rows, seed=int(seed))
    for member in bundle:
        k = int(member["fold"])
        slices = (("oof", oof_idx[f_oof == k]), ("in_fold", in_fold_idx[f_in != k]))
        for name, pool in slices:
            # seed base 900 keeps these distinct from the 0/1/2, fold, 100+i and 200+i seeds
            # already used for the training monitor curves
            curve, n_rows, n_eff = curve_on_rows(
                member, x_raw, y, w, pool, rounds, max_rows=max_rows,
                seed=seed + 10 * k + (name == "in_fold"),
                label=f"fold {k} {name}", progress=progress)
            res[name].append(curve)
            res[f"n_rows_{name}"].append(n_rows)
            res[f"n_eff_{name}"].append(n_eff)
    res["oof"] = np.asarray(res["oof"])
    res["in_fold"] = np.asarray(res["in_fold"])
    return res


def per_event_logloss(member, x_raw, y, n_trees=None, clip=1e-7):
    """Unaggregated -log p(y_i) per event for ONE saved model.

    Returned unaggregated so two models can be compared EVENT BY EVENT on identical rows.
    A paired difference of per-event losses has an uncertainty far below that of either
    loss on its own, because the large event-to-event spread of the log loss cancels in the
    difference. With concentrated weights (N_eff ~ 10k behind 250k rows) that is the only
    way to resolve an effect of ~0.007: the UNPAIRED spread across folds is itself ~0.004,
    so an unpaired tolerance is wider than the effect being measured."""
    p = np.clip(np.asarray(score_member(member, x_raw, n_trees=n_trees), dtype=np.float64),
                clip, 1 - clip)
    y = np.asarray(y)
    return -np.where(y == 1, np.log(p), np.log1p(-p))


def weighted_mean_and_error(values, w):
    """(mean, standard error, N_eff) of a weighted mean.

        m     = sum(w v) / sum(w)
        se    = sqrt(sum(w^2 (v - m)^2)) / sum(w)
        N_eff = (sum w)^2 / sum(w^2)

    The exact first-order error for a weighted average of independent events, so no
    bootstrap is needed. Applied to per-event log losses it gives the error on a loss;
    applied to the per-event DIFFERENCE of two models it gives the paired error."""
    v = np.asarray(values, dtype=np.float64)
    w = np.asarray(w, dtype=np.float64)
    sw = w.sum()
    if sw <= 0:
        return float("nan"), float("nan"), 0.0
    m = float((w * v).sum() / sw)
    se = float(np.sqrt((w ** 2 * (v - m) ** 2).sum()) / sw)
    return m, se, effective_entries(w)


def as_member(single, names, do_standardization):
    """Wrap a train_single_model result as a load_fold_bundle-style member, so the curve
    helpers can score it without a save/load round-trip. logloss_vs_rounds falls back to
    member["model"].get_booster() when there is no "booster" key."""
    return dict(model=single["model"], fold=single.get("fold", 0),
                meta=dict(variables=list(names), mean_map=single["mean_map"],
                          std_map=single["std_map"],
                          do_standardization=bool(do_standardization),
                          n_trees=single["n_trees"]))


def _selftest():
    rng = np.random.default_rng(1)

    # fold rule: a function of the EVENT, reproducible, no storage
    events = rng.integers(0, 2**34, size=100003, dtype=np.uint64)
    f = fold_of_event(events)
    assert f.dtype == np.int8 and f.min() >= 0 and f.max() < N_FOLDS
    assert np.array_equal(f, fold_of_event(events)), "the fold rule must be deterministic"
    # the same event gets the same fold however its rows are ordered or subset -- the property
    # that let the positional row mapping and its verification be deleted
    order = rng.permutation(len(events))
    assert np.array_equal(fold_of_event(events[order]), f[order])
    keep = rng.random(len(events)) < 0.3
    assert np.array_equal(fold_of_event(events[keep]), f[keep])
    # uniform event numbers give balanced folds, and a sub-population stays balanced
    assert np.all(np.abs(np.bincount(f, minlength=N_FOLDS) / len(f) - 0.2) < 0.01)
    sub = f[keep]
    assert np.all(np.abs(np.bincount(sub, minlength=N_FOLDS) / len(sub) - 0.2) < 0.02)
    # event numbers past 2**24 must survive: reading them as float32 would not
    big = np.array([6_511_566_984, 6_511_566_985, 499_999_956], dtype=np.uint64)
    assert np.array_equal(fold_of_event(big), (big % N_FOLDS).astype(np.int8))
    assert not np.array_equal(fold_of_event(big),
                              (big.astype(np.float32).astype(np.uint64) % N_FOLDS).astype(np.int8)), \
        "the float32 round trip should mangle these -- that is why event is read as an integer"
    # a float event array must be refused rather than silently truncated
    try:
        fold_of_event(np.array([1.0, 2.0]))
    except TypeError:
        pass
    else:
        raise AssertionError("fold_of_event accepted a float array")

    # standardizer: finite-only, missing values preserved, no leakage through apply
    x = rng.normal(loc=3, scale=2, size=(1000, 3))
    x[::10, 1] = np.nan
    x[5, 2] = np.inf
    names = ["a", "b", "c"]
    mu, sd = fit_standardizer(x, names)
    z = preprocess_features(x, names, True, mu, sd)
    assert abs(np.nanmean(z[:, 0])) < 1e-3 and abs(np.nanstd(z[:, 0]) - 1) < 1e-2
    assert np.isnan(z[0, 1]) and np.isnan(z[5, 2])
    assert fit_standardizer(np.ones((10, 1)), ["c"])[1]["c"] == 1.0

    # every opted-out variable keeps its raw values; anything else is still z-scored
    exempt = sorted(NO_STANDARDIZE_VARIABLES)
    cols = ["leading_jet_pt"] + exempt          # leading_jet_pt must NOT be in the set
    assert cols[0] not in NO_STANDARDIZE_VARIABLES
    raw = np.column_stack([rng.normal(100, 50, 500)]
                          + [rng.uniform(0, 6, 500) for _ in exempt])
    mu, sd = fit_standardizer(raw, cols)
    out = preprocess_features(raw, cols, True, mu, sd)
    for j, name in enumerate(exempt, start=1):
        assert (mu[name], sd[name]) == (0.0, 1.0), name
        assert np.allclose(out[:, j], raw[:, j]), f"{name} must pass through unchanged"
    assert mu[cols[0]] != 0.0 and sd[cols[0]] != 1.0
    assert abs(out[:, 0].mean()) < 1e-5 and abs(out[:, 0].std() - 1) < 1e-4

    # dev/test split: stratified, disjoint, deterministic (needs sklearn)
    try:
        y = (rng.random(5000) < 0.3).astype(np.int8)
        dev, test = split_dev_test(y, 0.2, 7)
        assert len(test) == 1000 and not set(dev) & set(test)
        assert abs(y[test].mean() - y.mean()) < 0.02
        assert np.array_equal(dev, split_dev_test(y, 0.2, 7)[0])
    except ImportError:
        print("[selftest] sklearn not available: skipped the dev/test split check")

    # rounds policy
    assert choose_n_rounds([99, 149, 199, 119, 129]) == 130

    # normalized_hist: in the unit-weight limit the propagated error must equal the exact
    # multinomial sqrt(n(1-n)/N); with weights it must match the spread of pseudo-experiments
    v, n_ev = rng.uniform(115, 135, 20000), 20000
    n_hist, err, _ = normalized_hist(v, np.ones(n_ev), bins=20, range=(115, 135))
    assert np.allclose(err, np.sqrt(n_hist * (1 - n_hist) / n_ev), rtol=1e-6)
    spread = []
    for _ in range(400):
        vv = rng.uniform(115, 135, 3000)
        ww = rng.uniform(0.2, 2.0, 3000)
        nn, ee, _ = normalized_hist(vv, ww, bins=20, range=(115, 135))
        spread.append(nn)
    ratio = ee / np.array(spread).std(axis=0, ddof=1)
    assert 0.9 < ratio.mean() < 1.1, ratio.mean()
    assert effective_entries(np.ones(500)) == 500.0
    assert abs(effective_entries(np.repeat([1.0, 3.0], 250)) - 400.0) < 1e-9

    # the legacy split must reproduce what the original train.py got from (x, y)
    try:
        from sklearn.model_selection import train_test_split
        n = 9973
        xd, yd = rng.normal(size=(n, 3)), (rng.random(n) < 0.3).astype(np.int8)
        xt_o, xe_o, yt_o, ye_o = train_test_split(xd, yd, train_size=0.6, test_size=0.4,
                                                  random_state=7)
        tr, te = legacy_split(n, 0.4, 7)
        assert len(tr) == len(yt_o) and len(te) == len(ye_o), (len(tr), len(yt_o))
        assert not set(tr) & set(te) and len(tr) + len(te) == n
        # same partition: the rows the original kept for training are exactly x[tr]
        assert np.array_equal(np.sort(yt_o), np.sort(yd[tr]))
        assert np.allclose(np.sort(xt_o, axis=0), np.sort(xd[tr], axis=0))
    except ImportError:
        print("[selftest] sklearn not available: skipped the legacy-split check")

    # fold_summary warns on a deliberately imbalanced fold
    folds = fold_of_event(np.arange(10000, dtype=np.uint64))
    w = np.where(folds == 0, 5.0, 1.0)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fold_summary((rng.random(10000) < 0.5).astype(np.int8), w, folds, label="selftest")
    assert caught, "an imbalanced weighted share should warn"

    # round grid for the recomputed loss curves: starts at 1, ends at n_rounds, and NEVER
    # contains 0 -- XGBoost would read an iteration_range end of 0 as "all trees"
    for n_rounds, step in ((400, 10), (20, 10), (400, 5), (7, 10), (1, 10)):
        g = round_grid(n_rounds, step)
        assert g[0] == 1 and g[-1] == n_rounds, (n_rounds, step, g)
        assert 0 not in g, (n_rounds, step, g)
        assert np.all(np.diff(g) > 0), (n_rounds, step, g)
        assert g.max() <= n_rounds, (n_rounds, step, g)
    assert np.array_equal(round_grid(20, 10), [1, 10, 20])   # the --smoke case
    assert np.array_equal(round_grid(7, 10), [1, 7])         # step past the end
    assert np.array_equal(round_grid(1, 10), [1])
    try:
        round_grid(0, 10)
    except ValueError:
        pass
    else:
        raise AssertionError("round_grid(0, ...) must raise, not return an empty grid")

    # the --control-80 diagnostic rests on this: sklearn's train_test_split permutes ONCE per
    # seed, so at a fixed seed a smaller test fraction yields a train set that is a strict
    # SUPERSET of the larger one's. That is what makes the 60% pool in-sample for both the
    # 60%-trained and the 80%-trained model. If a future sklearn changes the permutation
    # behaviour the control silently stops being a control, so assert it here.
    try:
        n = 50_000
        tr60, te40 = legacy_split(n, 0.4, 7)
        tr80, te20 = legacy_split(n, 0.2, 7)
        s60, s80 = set(tr60.tolist()), set(tr80.tolist())
        assert s60 <= s80, f"{len(s60 - s80)} events in the 60% train set are not in the 80% one"
        assert set(te20.tolist()) <= set(te40.tolist()), "control held-out not inside legacy held-out"
        assert len(tr80) == int(round(0.8 * n)), (len(tr80), n)
    except ImportError:
        print("[selftest] sklearn not available: skipped the split-nesting check")

    print("[selftest] xgb_kfold pure-numpy checks passed")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print(__doc__)
