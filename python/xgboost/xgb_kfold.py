"""K-fold / out-of-fold (OOF) machinery for the H->mumu XGBoost BDT.

Vocabulary:
  train       events used to fit one particular model
  validation  events used for early stopping and Optuna model selection
  test        untouched sample, evaluated once after the configuration is frozen
  OOF         score of an MC event from the model that EXCLUDED its fold

The rule enforced here: an event in fold i is only ever scored by model i, which never
trained on it. The fold is `event % N_FOLDS`, a property of the event itself.
"""
import gc
import os
import pickle
import subprocess
import time
import warnings

import numpy as np

N_FOLDS = 5
TRAIN_REGION = (115.0, 135.0)  # skim window, see src/SkimTuples*.cc
MASS_BSC = "diMuon_bsConstrainedMass"
EVENT_ID = "event"
SKIM_KIND = {"Full": "background", "NottH": "signal"}  # which hadded skim holds each subset

# Inputs left in their raw units (identity mean/std): integer counts/categoricals and scores
# that already live on a bounded scale. Trees are invariant to the transform anyway; this only
# keeps split thresholds and plots readable.
NO_STANDARDIZE_VARIABLES = frozenset({
    "mc_campaign", "n_jet", "n_SoftJet_pt2",
    "leading_jet_nConstituents", "subleading_jet_nConstituents",
    "leading_jet_btagPNetQvG", "subleading_jet_btagPNetQvG",
    "pt_balance", "cos_theta_CS",
})


# ---------------------------------------------------------------------------
# Folds and input files
# ---------------------------------------------------------------------------
def fold_of_event(event):
    """The fold rule: event % N_FOLDS. `event` must be the integer branch -- as a float32
    it would be corrupted (Data event numbers reach ~6.5e9)."""
    event = np.asarray(event)
    if event.dtype.kind not in "ui":
        raise TypeError(f"the fold rule needs the integer {EVENT_ID!r} branch, got {event.dtype}")
    return (event.astype(np.uint64) % np.uint64(N_FOLDS)).astype(np.int8)


def training_region_mask(mass):
    """Events the BDT trains on: strictly inside TRAIN_REGION (the skim keeps the edges)."""
    mass = np.asarray(mass)
    return (mass > TRAIN_REGION[0]) & (mass < TRAIN_REGION[1])


def skim_path(skim_dir, era, subset):
    if subset not in SKIM_KIND:
        raise NotImplementedError(f"unknown skim subset {subset!r} (have {list(SKIM_KIND)})")
    return f"{skim_dir}{SKIM_KIND[subset]}_{era}_skim_{subset}.root"


def uproot_open_options():
    """Read big files in chunks instead of memory-mapping them (the LPC 16 GiB virtual
    memory limit is otherwise exhausted by the mapping alone)."""
    import uproot
    return dict(file_handler=uproot.MultithreadedFileSource)


def read_columns(path, branches):
    import uproot
    with uproot.open(path, **uproot_open_options()) as f:
        return f["tree_output"].arrays(branches, library="np")


def read_event_ids(path):
    """The `event` branch of one file, as its native unsigned integer."""
    import uproot
    with uproot.open(path, **uproot_open_options()) as f:
        tree = f["tree_output"]
        if EVENT_ID not in tree:
            raise RuntimeError(
                f"{path} has no {EVENT_ID!r} branch, so the fold of each row is unknown. Add it "
                "to the branch whitelist in src/SkimTuplesggH.cc / src/SkimTuples_VBF.cc, "
                "rebuild and re-make the skim.")
        return tree[EVENT_ID].array(library="np")


def fold_summary(y, w, folds, label="fold", rel_tolerance=0.05):
    """Print counts and weighted yields per fold; warn if a fold's weighted share is off."""
    tot_s, tot_b = w[y == 1].sum(), w[y == 0].sum()
    print(f"[INFO] {label} summary (n_sig, n_bkg | w_sig, w_bkg | share of w_sig, w_bkg)")
    for k in range(N_FOLDS):
        sig, bkg = (y == 1) & (folds == k), (y == 0) & (folds == k)
        share_s, share_b = w[sig].sum() / tot_s, w[bkg].sum() / tot_b
        print(f"   {label} {k}: {sig.sum():>9d} {bkg.sum():>9d} | {w[sig].sum():.4g} "
              f"{w[bkg].sum():.4g} | {share_s:.3f} {share_b:.3f}")
        for name, share in (("sig", share_s), ("bkg", share_b)):
            if abs(share * N_FOLDS - 1.0) > rel_tolerance:
                warnings.warn(f"{label} {k}: weighted {name} share {share:.3f} is more than "
                              f"{rel_tolerance:.0%} away from 1/{N_FOLDS}")


# ---------------------------------------------------------------------------
# Weighted-histogram statistics
# ---------------------------------------------------------------------------
def normalized_hist(values, weights, bins, range=None, density=False):
    """Unit-area weighted histogram and its error, propagated through the normalization
    (var(n_i) = [var_i (1 - 2 n_i) + n_i^2 sum_j var_j] / S^2). Returns (n, err, edges)."""
    counts, edges = np.histogram(values, bins=bins, range=range, weights=weights)
    var, _ = np.histogram(values, bins=bins, range=range, weights=np.asarray(weights) ** 2)
    total = counts.sum()
    if total <= 0:
        return counts.astype(float), np.zeros(len(counts)), edges
    n = counts / total
    err = np.sqrt(np.clip((var * (1 - 2 * n) + n ** 2 * var.sum()) / total ** 2, 0, None))
    if density:
        n, err = n / np.diff(edges), err / np.diff(edges)
    return n, err, edges


def effective_entries(weights):
    """(sum w)^2 / sum(w^2)."""
    w = np.asarray(weights, dtype=np.float64)
    sum_w2 = (w ** 2).sum()
    return float(w.sum() ** 2 / sum_w2) if sum_w2 > 0 else 0.0


# ---------------------------------------------------------------------------
# Standardization (fitted per model on that model's training rows only)
# ---------------------------------------------------------------------------
def fit_standardizer(x, names):
    """mean/std per variable over finite entries; identity for NO_STANDARDIZE_VARIABLES,
    empty and constant columns."""
    mean_map, std_map = {}, {}
    for i, name in enumerate(names):
        col = np.asarray(x[:, i], dtype=np.float64)
        col = col[np.isfinite(col)]
        if name in NO_STANDARDIZE_VARIABLES or len(col) == 0:
            mean_map[name], std_map[name] = 0.0, 1.0
        else:
            mean_map[name], std_map[name] = float(col.mean()), float(col.std()) or 1.0
    return mean_map, std_map


def preprocess_features(x, names, do_standardization, mean_map=None, std_map=None):
    """float32 copy of x with +/-inf -> NaN (XGBoost's missing value) and, optionally,
    finite entries z-scored with the GIVEN maps."""
    out = np.array(x, dtype=np.float32, copy=True)
    out[~np.isfinite(out)] = np.nan
    if do_standardization:
        for i, name in enumerate(names):
            finite = np.isfinite(out[:, i])
            out[finite, i] = (out[finite, i] - mean_map[name]) / std_map[name]
    return out


# ---------------------------------------------------------------------------
# Splits
# ---------------------------------------------------------------------------
def split_dev_test(y, test_fraction, seed):
    """Stratified development / untouched-test split (deterministic in the seed)."""
    from sklearn.model_selection import train_test_split
    dev, test = train_test_split(np.arange(len(y)), test_size=test_fraction,
                                 random_state=seed, stratify=y)
    return np.sort(dev), np.sort(test)


def cv_fold_indices(y, seed):
    """[(train_idx, validation_idx), ...] for Optuna's cross-validation."""
    from sklearn.model_selection import StratifiedKFold
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
    return list(skf.split(np.zeros(len(y)), y))


def legacy_split(n_events, test_fraction, seed):
    """The pre-K-fold split: one unstratified random train/test partition."""
    from sklearn.model_selection import train_test_split
    train_idx, test_idx = train_test_split(np.arange(int(n_events)), train_size=1.0 - test_fraction,
                                           test_size=test_fraction, random_state=seed)
    return np.sort(train_idx), np.sort(test_idx)


def subsample(rows, max_rows=None, seed=0):
    """Sorted random subset of `rows` with at most max_rows entries (all of them if None)."""
    rows = np.asarray(rows)
    if not max_rows or len(rows) <= max_rows:
        return rows
    pick = np.random.default_rng(seed).choice(len(rows), size=int(max_rows), replace=False)
    return rows[np.sort(pick)]


# ---------------------------------------------------------------------------
# Training helpers
# ---------------------------------------------------------------------------
def base_xgb_params(device="cuda", n_jobs=4):
    # XGBoost early-stops on the LAST metric, so logloss drives early stopping
    return dict(objective="binary:logistic", eval_metric=["auc", "logloss"], device=device,
                n_jobs=n_jobs, verbosity=0, missing=np.nan)


def make_config(device, tuned_params, n_rounds, source):
    """A frozen training configuration (JSON-safe)."""
    params = dict(base_xgb_params(device), **tuned_params)
    params["missing"] = "nan"
    return dict(source=source, params=params, n_rounds=int(n_rounds))


def params_from_config(config, device=None):
    params = dict(config["params"], missing=np.nan)
    if device:
        params["device"] = device
    return params


def choose_n_rounds(best_iterations, scale=1.0):
    """Rounds for the final models: median over CV folds of (best_iteration + 1), scaled."""
    return max(1, int(round(float(np.median(np.asarray(best_iterations) + 1)) * scale)))


def weighted_metrics(y, p, w):
    from sklearn.metrics import log_loss, roc_auc_score
    p = np.clip(p, 1e-7, 1 - 1e-7)
    return dict(auc_w=float(roc_auc_score(y, p, sample_weight=w)),
                auc=float(roc_auc_score(y, p)),
                logloss_w=float(log_loss(y, p, sample_weight=w, labels=[0, 1])),
                logloss=float(log_loss(y, p, labels=[0, 1])))


def make_progress_callback(label, total, every):
    """XGBoost callback printing round, rate, ETA and metrics every `every` rounds."""
    import xgboost as xgb

    class Progress(xgb.callback.TrainingCallback):
        t0 = time.time()

        def after_iteration(self, model, epoch, evals_log):
            n = epoch + 1
            if n == 1 or n % every == 0 or n == total:
                elapsed = time.time() - self.t0
                rate = n / max(elapsed, 1e-9)
                metrics = ", ".join(f"{d}-{m}={v[-1]:.5f}" for d, ms in evals_log.items()
                                    for m, v in ms.items())
                print(f"[PROGRESS] {label}: round {n}/{total} | {elapsed:.0f}s | "
                      f"{rate:.2f} rounds/s | ETA {(total - n) / rate:.0f}s | {metrics}", flush=True)
            return False

    return Progress()


_gpu_readout_available = None


def gpu_memory_note():
    """'gpu0 used/total MiB, ...' from nvidia-smi, or '' if there is no GPU readout.
    (Not pynvml: in CMSSW it links a stub library that spams stderr.)"""
    global _gpu_readout_available
    if _gpu_readout_available is False:
        return ""
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total",
                              "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=10, check=True).stdout
        parts = [f"gpu{i} {used.strip()}/{total.strip()} MiB"
                 for i, (used, total) in enumerate(line.split(",")[:2] for line in out.splitlines())]
        _gpu_readout_available = bool(parts)
        return ", ".join(parts)
    except Exception:
        _gpu_readout_available = False
        return ""


def _fit(params, n_estimators, x, y, w, eval_sets, label, progress_every, **kwargs):
    """Fit one XGBClassifier. eval_sets = [(x, y, w), ...] (monitoring / early stopping)."""
    import xgboost as xgb
    callbacks = [make_progress_callback(label, n_estimators, progress_every)] if progress_every else None
    model = xgb.XGBClassifier(**params, n_estimators=int(n_estimators), callbacks=callbacks, **kwargs)
    model.fit(x, y, sample_weight=w, eval_set=[(ex, ey) for ex, ey, _ in eval_sets],
              sample_weight_eval_set=[ew for _, _, ew in eval_sets], verbose=False)
    model.callbacks = None  # the local callback class cannot be pickled
    return model


def predict(model, x, n_trees):
    return model.predict_proba(x, iteration_range=(0, int(n_trees)))[:, 1]


# ---------------------------------------------------------------------------
# Cross-validation and Optuna (development stage)
# ---------------------------------------------------------------------------
def cross_validate(x, y, w, cv_folds, standardizers, names, do_standardization, params,
                   n_estimators, early_stopping_rounds, trial=None, label="", progress_every=0):
    """Train on N_FOLDS-1 folds, early-stop on the remaining one, for every fold.
    Returns one dict per fold (validation metrics + best_iteration)."""
    params = dict(params, eval_metric=["logloss"])  # only the early-stopping metric is needed
    infos = []
    for k, ((tr, va), (mean_map, std_map)) in enumerate(zip(cv_folds, standardizers)):
        x_tr = preprocess_features(x[tr], names, do_standardization, mean_map, std_map)
        x_va = preprocess_features(x[va], names, do_standardization, mean_map, std_map)
        model = _fit(params, n_estimators, x_tr, y[tr], w[tr], [(x_va, y[va], w[va])],
                     f"CV fold {k}", progress_every, early_stopping_rounds=early_stopping_rounds)
        n_trees = int(model.best_iteration) + 1
        info = weighted_metrics(y[va], predict(model, x_va, n_trees), w[va])
        info.update(fold=k, best_iteration=n_trees - 1)
        infos.append(info)
        # XGBoost's sklearn wrapper holds reference cycles: free the GPU memory before the next fit
        del x_tr, x_va, model
        gc.collect()
        note = gpu_memory_note()
        print(f"[CV   ] {label}fold {k}: {n_trees} trees, weighted validation AUC "
              f"{info['auc_w']:.5f}, logloss {info['logloss_w']:.5f}" + (f" | {note}" if note else ""),
              flush=True)
        if trial is not None:
            import optuna
            trial.report(float(np.mean([i["auc_w"] for i in infos])), step=k)
            if trial.should_prune():
                raise optuna.TrialPruned()
    return infos


def run_optuna_cv(x, y, w, cv_folds, names, do_standardization, n_trials, seed, device,
                  n_estimators, early_stopping_rounds, progress_every=0):
    """Optuna study maximizing the mean weighted validation AUC over the CV folds."""
    import optuna

    standardizers = [fit_standardizer(x[tr], names) if do_standardization else ({}, {})
                     for tr, _ in cv_folds]
    trial_progress = max(1, n_estimators // 10) if progress_every else 0
    print(f"[OPTUNA] {n_trials} trials x {N_FOLDS} folds, up to {n_estimators} rounds (early "
          f"stopping {early_stopping_rounds}), device={device} | {gpu_memory_note() or 'no GPU readout'}",
          flush=True)

    def objective(trial):
        tag = f"trial {trial.number + 1}/{n_trials} "
        params = dict(base_xgb_params(device),
                      max_depth=trial.suggest_int("max_depth", 2, 5),
                      learning_rate=trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
                      min_child_weight=trial.suggest_float("min_child_weight", 1.0, 20.0, log=True),
                      subsample=trial.suggest_float("subsample", 0.6, 1.0),
                      colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 1.0),
                      reg_lambda=trial.suggest_float("reg_lambda", 0.1, 10.0, log=True),
                      reg_alpha=trial.suggest_float("reg_alpha", 1e-4, 1.0, log=True))
        print(f"[OPTUNA] {tag}start: " + ", ".join(f"{k}={v:.4g}" for k, v in trial.params.items()),
              flush=True)
        t0 = time.time()
        infos = cross_validate(x, y, w, cv_folds, standardizers, names, do_standardization, params,
                               n_estimators, early_stopping_rounds, trial=trial, label=tag,
                               progress_every=trial_progress)
        for key in ("auc_w", "logloss_w", "best_iteration"):
            trial.set_user_attr(f"fold_{key}", [i[key] for i in infos])
        mean_auc = float(np.mean([i["auc_w"] for i in infos]))
        print(f"[OPTUNA] {tag}done in {time.time() - t0:.1f} s: mean weighted validation AUC "
              f"{mean_auc:.5f}", flush=True)
        return mean_auc

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed),
                                pruner=optuna.pruners.MedianPruner(n_startup_trials=10, n_warmup_steps=1))
    study.optimize(objective, n_trials=n_trials)
    return study


# ---------------------------------------------------------------------------
# Fixed-round models (test refit, final K-fold models, legacy single model)
# ---------------------------------------------------------------------------
def train_model(x, y, w, train_idx, heldout_idx, names, do_standardization, params, n_rounds,
                fold=0, seed=0, label="model", progress_every=0, monitor_max_rows=None,
                in_sample_max_rows=None, monitor_heldout=True):
    """Train one model on `train_idx` with a fixed number of rounds (no early stopping) and
    predict `heldout_idx`. The held-out rows are only a monitoring curve (omitted entirely
    with monitor_heldout=False) and can never influence the fit.

    Returns (member, p_heldout, in_sample) where `member` has the same `meta` layout as a
    load_fold_bundle entry, and `in_sample` = dict(idx, p) on at most in_sample_max_rows of
    the train rows (None when in_sample_max_rows is 0/None)."""
    mean_map, std_map = fit_standardizer(x[train_idx], names) if do_standardization else ({}, {})
    x_tr = preprocess_features(x[train_idx], names, do_standardization, mean_map, std_map)
    x_ho = preprocess_features(x[heldout_idx], names, do_standardization, mean_map, std_map)

    def monitor(x_part, rows, pos_seed):
        pos = subsample(np.arange(len(rows)), monitor_max_rows, pos_seed)
        return x_part[pos], y[rows][pos], w[rows][pos]

    eval_sets = [monitor(x_tr, train_idx, seed)]
    if monitor_heldout:
        eval_sets.append(monitor(x_ho, heldout_idx, 100 + seed))
    print(f"[INFO] training {label}: {len(train_idx)} train events, {len(heldout_idx)} held out, "
          f"{int(n_rounds)} rounds, device={params.get('device')}", flush=True)
    model = _fit(params, n_rounds, x_tr, y[train_idx], w[train_idx], eval_sets, label, progress_every)

    p_heldout = predict(model, x_ho, n_rounds).astype(np.float64)
    in_sample = None
    if in_sample_max_rows:
        pos = subsample(np.arange(len(train_idx)), in_sample_max_rows, 200 + seed)
        in_sample = dict(idx=train_idx[pos], p=predict(model, x_tr[pos], n_rounds))
    curves = model.evals_result()
    member = dict(
        model=model, fold=fold, n_train=int(len(train_idx)), n_heldout=int(len(heldout_idx)),
        meta=dict(variables=list(names), mean_map=mean_map, std_map=std_map,
                  do_standardization=bool(do_standardization), fold=fold, n_trees=int(n_rounds)),
        train_logloss=list(curves["validation_0"]["logloss"]),
        val_logloss=list(curves["validation_1"]["logloss"]) if monitor_heldout else [],
        heldout_metrics=weighted_metrics(y[heldout_idx], p_heldout, w[heldout_idx]),
    )
    return member, p_heldout, in_sample


def train_final_kfold(x, y, w, folds, names, do_standardization, params, n_rounds,
                      on_model_done=None, **kwargs):
    """The N_FOLDS analysis models on ALL MC: model i trains on fold != i and gives the
    events of fold i their OOF score. `on_model_done(member)` runs right after each fit
    (train.py saves the model there). Returns (members, oof, in_sample_per_model)."""
    members, in_sample = [], []
    oof = np.full(len(y), np.nan)
    for i in range(N_FOLDS):
        tr, ho = np.flatnonzero(folds != i), np.flatnonzero(folds == i)
        member, oof[ho], ins = train_model(x, y, w, tr, ho, names, do_standardization, params,
                                           n_rounds, fold=i, seed=i,
                                           label=f"final model {i + 1}/{N_FOLDS}", **kwargs)
        members.append(member)
        in_sample.append(ins)
        if on_model_done is not None:
            on_model_done(member)
        print(f"[INFO] final model {i + 1}/{N_FOLDS} (held out fold {i}): held-out weighted AUC = "
              f"{member['heldout_metrics']['auc_w']:.4f}", flush=True)
    if np.isnan(oof).any():
        raise RuntimeError("some events did not receive an OOF prediction")
    return members, oof, in_sample


# ---------------------------------------------------------------------------
# Saving, loading and scoring
# ---------------------------------------------------------------------------
def save_fold_models(members, test_name, use_bsConstrain, params, seed, n_folds=N_FOLDS,
                     models_dir="models", extra_meta=None):
    """model_<name>_fold<k>[_bsC].{pkl,json} + preprocessing_<name>_fold<k>[_bsC].pkl."""
    import xgboost
    os.makedirs(models_dir, exist_ok=True)
    suffix = "_bsC" if use_bsConstrain else ""
    params = {k: ("nan" if k == "missing" else v) for k, v in params.items()}
    for mem in members:
        base = f"{models_dir}/%s_{test_name}_fold{mem['fold']}{suffix}"
        with open(base % "model" + ".pkl", "wb") as f:
            pickle.dump(mem["model"], f)
        mem["model"].get_booster().save_model(base % "model" + ".json")  # version-stable format
        meta = dict(mem["meta"], n_folds=int(n_folds), seed=seed, params=params,
                    xgboost_version=xgboost.__version__, n_train=mem["n_train"],
                    heldout_metrics=mem["heldout_metrics"], **(extra_meta or {}))
        with open(base % "preprocessing" + ".pkl", "wb") as f:
            pickle.dump(meta, f)


def load_fold_bundle(test_name, use_bsConstrain, models_dir="models"):
    """All models of a set as native Boosters with their own preprocessing metadata.
    Works for a 5-fold set and for the 1-model legacy set (n_folds is read from fold 0)."""
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
        try:  # trained on GPU, but scoring must work on CPU-only nodes
            booster.set_param({"device": "cpu"})
        except Exception:
            pass
        bundle.append(dict(booster=booster, meta=meta, fold=k))
    if len({tuple(b["meta"]["variables"]) for b in bundle}) != 1:
        raise RuntimeError("fold models were trained with different variable lists")
    return bundle


def _booster_and_dmatrix(member, x_raw):
    import xgboost as xgb
    meta = member["meta"]
    x = preprocess_features(x_raw, meta["variables"], meta["do_standardization"],
                            meta["mean_map"], meta["std_map"])
    booster = member["booster"] if "booster" in member else member["model"].get_booster()
    return booster, xgb.DMatrix(x, missing=np.nan, feature_names=booster.feature_names)


def score_member(member, x_raw, n_trees=None):
    """Score raw features with ONE model (a bundle entry or a train_model member)."""
    booster, dmatrix = _booster_and_dmatrix(member, x_raw)
    n = int(member["meta"]["n_trees"] if n_trees is None else n_trees)
    return np.asarray(booster.predict(dmatrix, iteration_range=(0, n)), dtype=np.float32)


def predict_by_fold(x_raw, folds, bundle):
    """The analysis scoring rule: event in fold i -> model i."""
    folds = np.asarray(folds)
    scores = np.full(len(x_raw), np.nan, dtype=np.float32)
    for member in bundle:
        sel = folds == member["fold"]
        if sel.any():
            scores[sel] = score_member(member, x_raw[sel])
    if np.isnan(scores).any():
        raise RuntimeError("some events were not scored (fold ids outside 0..N_FOLDS-1?)")
    return scores


# ---------------------------------------------------------------------------
# Log loss vs boosting round, recomputed from trained models (--stage legacy)
# ---------------------------------------------------------------------------
def round_grid(n_rounds, step):
    """Tree counts to evaluate: 1, every `step`-th round, and n_rounds. Never 0 -- XGBoost
    reads an iteration_range end of 0 as 'all trees'."""
    if int(n_rounds) < 1:
        raise ValueError(f"n_rounds must be >= 1, got {n_rounds}")
    return np.array(sorted({1, *range(step, int(n_rounds) + 1, step), int(n_rounds)}))


def curve_on_rows(member, x_raw, y, w, rows, rounds, max_rows=None, seed=0, label=""):
    """Weighted log loss of one model vs tree count, on (a subsample of) `rows`. `w` should
    be the training weights so the scale matches XGBoost's own curves."""
    from sklearn.metrics import log_loss
    rows = subsample(rows, max_rows, seed)
    if len(np.unique(y[rows])) < 2:
        raise RuntimeError(f"{label}: need both classes to compute a log loss ({len(rows)} rows)")
    t0 = time.time()
    booster, dmatrix = _booster_and_dmatrix(member, x_raw[rows])
    curve = np.array([log_loss(y[rows], np.clip(booster.predict(dmatrix, iteration_range=(0, int(r))),
                                                1e-7, 1 - 1e-7),
                               sample_weight=w[rows], labels=[0, 1]) for r in rounds])
    print(f"[PROGRESS] loss curve: {label:28s} | {len(rows)} rows (N_eff "
          f"{effective_entries(w[rows]):.0f}) | {time.time() - t0:.0f}s", flush=True)
    return curve


def kfold_logloss_curves(bundle, x_raw, y, w, folds, oof_idx, in_fold_idx, rounds, max_rows=None,
                         seed=900):
    """Per fold model k: loss curve on the rows of `oof_idx` it excluded (fold == k) and on
    the rows of `in_fold_idx` it trained on (fold != k). Returns dict(oof, in_fold) arrays of
    shape (n_models, len(rounds))."""
    curves = dict(oof=[], in_fold=[])
    for member in bundle:
        k = int(member["fold"])
        pools = dict(oof=oof_idx[folds[oof_idx] == k], in_fold=in_fold_idx[folds[in_fold_idx] != k])
        for j, (name, pool) in enumerate(pools.items()):
            curves[name].append(curve_on_rows(member, x_raw, y, w, pool, rounds, max_rows,
                                              seed + 10 * k + j, label=f"fold {k} {name}"))
    return {name: np.asarray(c) for name, c in curves.items()}
