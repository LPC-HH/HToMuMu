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
import json
import math
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


# Matias's (pre-K-fold) preprocessing, for --stage legacy --matias-preprocessing and
# score_external_model.py: padded jet values keep their placeholder (0; -1 for these) and are
# neither standardized nor used for the mean/std
MATIAS_PLACEHOLDER = {"delta_phi_diJet": -1.0, "pt_balance": -1.0}


def matias_raw(x, names):
    """float64 copy with NaN -> the variable's placeholder: undoes
    xgb_utils.mask_undefined_jet_features (the skims store padded jet values as exactly 0 / -1)."""
    out = np.array(x, dtype=np.float64, copy=True)
    for i, name in enumerate(names):
        out[np.isnan(out[:, i]), i] = MATIAS_PLACEHOLDER.get(name, 0.0)
    return out


def matias_standardizer(x, names):
    """mean/std per variable over the entries that are not its placeholder."""
    mean_map, std_map = {}, {}
    for i, name in enumerate(names):
        col = np.asarray(x[:, i], dtype=np.float64)
        col = col[col != MATIAS_PLACEHOLDER.get(name, 0.0)]
        mean_map[name], std_map[name] = float(col.mean()), float(col.std())
    return mean_map, std_map


def matias_preprocess(x, names, mean_map, std_map):
    """Copy of x (same dtype, and the arithmetic in that dtype, as in Matias's code: float64 in his
    training, float32 when he scores the tuples) with every entry that is not its variable's
    placeholder standardized; placeholders stay raw and NaN is kept (XGBoost's missing value).
    The dtype matters: a one-ulp change of an input can move an event across a split threshold."""
    out = np.array(x, copy=True)
    for i, name in enumerate(names):
        if std_map[name] == 0:
            raise ValueError(f"std is zero for {name}")
        keep = out[:, i] != MATIAS_PLACEHOLDER.get(name, 0.0)
        out[keep, i] = (out[keep, i] - mean_map[name]) / std_map[name]
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


def weighted_ks(a, wa, b, wb):
    """Two-sample Kolmogorov-Smirnov test of weighted samples: D = max |CDF_a - CDF_b| of the
    weighted empirical distributions and the asymptotic p-value with Kish effective sizes
    (sum w)^2 / sum w^2. Returns (D, p, n_eff_a, n_eff_b); p is None without positive sizes.
    With large samples p is tiny for any visible difference: D is the size of the difference."""
    from scipy.special import kolmogorov
    a, wa, b, wb = (np.asarray(v, dtype=float) for v in (a, wa, b, wb))
    values = np.concatenate([a, b])
    order = np.argsort(values, kind="stable")
    wa_all = np.concatenate([wa, np.zeros(len(b))])[order]
    wb_all = np.concatenate([np.zeros(len(a)), wb])[order]
    last = np.r_[values[order][1:] != values[order][:-1], True]  # compare the CDFs after tied values
    cdf_a, cdf_b = np.cumsum(wa_all)[last] / wa.sum(), np.cumsum(wb_all)[last] / wb.sum()
    d = float(np.max(np.abs(cdf_a - cdf_b)))
    n_a = wa.sum() ** 2 / np.sum(wa ** 2) if np.sum(wa ** 2) > 0 else 0.0
    n_b = wb.sum() ** 2 / np.sum(wb ** 2) if np.sum(wb ** 2) > 0 else 0.0
    p = float(kolmogorov(d * math.sqrt(n_a * n_b / (n_a + n_b)))) if n_a > 0 and n_b > 0 else None
    return d, p, float(n_a), float(n_b)


def weighted_metrics(y, p, w):
    from sklearn.metrics import log_loss, roc_auc_score
    p = np.clip(p, 1e-7, 1 - 1e-7)
    return dict(auc_w=float(roc_auc_score(y, p, sample_weight=w)),
                auc=float(roc_auc_score(y, p)),
                logloss_w=float(log_loss(y, p, sample_weight=w, labels=[0, 1])),
                logloss=float(log_loss(y, p, labels=[0, 1])))


# ---------------------------------------------------------------------------
# Binned Asimov significance (Optuna --objective asimov, evaluate_metrics.py)
# ---------------------------------------------------------------------------
# fixed categories: cumulative physics-weighted signal fraction from the top of the score
ASIMOV_SIGNAL_FRACTIONS = [0.02, 0.05, 0.10, 0.20, 0.35, 0.50, 0.70, 1.00]
ASIMOV_MASS_BIN = 2.0  # GeV, over TRAIN_REGION
ASIMOV_CHECKPOINT_EVERY = 50  # boosting rounds between Asimov evaluations in the CV
ASIMOV_EARLY_STOPPING_ROUNDS = 200  # logloss early stopping is only a safety cap with asimov


def asimov_z(s, b, sigma_b):
    """Cowan's median discovery significance with background uncertainty sigma_b, per bin
    (reduces to sqrt(2((s+b)ln(1+s/b)-s)) for sigma_b -> 0). Bins with b <= 0 give 0."""
    s = np.clip(np.asarray(s, float), 0, None)
    b, sigma_b = np.asarray(b, float), np.asarray(sigma_b, float)
    z2 = np.zeros_like(b)
    ok = b > 0
    s, b, v = s[ok], b[ok], sigma_b[ok] ** 2
    small = v < 1e-9 * b
    plain = 2 * ((s + b) * np.log1p(s / b) - s)
    with np.errstate(divide="ignore", invalid="ignore"):
        full = 2 * ((s + b) * np.log((s + b) * (b + v) / (b * b + (s + b) * v))
                    - b * b / v * np.log1p(v * s / (b * (b + v))))
    z2[ok] = np.where(small, plain, full)
    return np.sqrt(np.clip(z2, 0, None))


def signal_fraction_edges(scores, w, fractions=ASIMOV_SIGNAL_FRACTIONS):
    """Ascending category edges [-inf, ..., +inf] such that `fractions` of the (weighted) signal
    lies above each inner edge; categories are [edges[k], edges[k+1])."""
    order = np.argsort(-scores)
    cum = np.cumsum(w[order]) / w.sum()
    cuts = [scores[order][min(np.searchsorted(cum, f), len(scores) - 1)] for f in fractions[:-1]]
    return [-np.inf] + sorted(set(cuts)) + [np.inf]


def _merge_nonpositive(s, b, v):
    """Merge bins with b <= 0 into a neighbour (the next bin, the previous one for the last)
    until every bin has b > 0; totals are conserved. Returns the merged (s, b, v) as lists."""
    s, b, v = list(s), list(b), list(v)
    i = 0
    while i < len(b):
        if b[i] > 0 or len(b) == 1:
            i += 1
            continue
        j = i + 1 if i + 1 < len(b) else i - 1
        s[j] += s[i]
        b[j] += b[i]
        v[j] += v[i]
        del s[i], b[i], v[i]
        i = min(i, j)  # re-check the bin that absorbed it
    return s, b, v


def binned_asimov_z(scores, y, mass, w, scale=1.0, details=False):
    """Binned Asimov Z over fixed categories (ASIMOV_SIGNAL_FRACTIONS of the signal) x
    ASIMOV_MASS_BIN bins of TRAIN_REGION, with the raw background MC and its sum(w^2) as
    uncertainty (Cowan). Background bins <= 0 are merged with a neighbour; a category whose
    background is <= 0 is merged into the next looser one. s and b are scaled by `scale`,
    sum(w^2) by scale^2 (e.g. scale = 1 / fraction of the MC in a validation fold).
    `w` are physics weights. Returns Z (and the per-category details)."""
    scores, y, mass, w = (np.asarray(a) for a in (scores, y, mass, w))
    win = (mass > TRAIN_REGION[0]) & (mass < TRAIN_REGION[1])
    sig, bkg = win & (y == 1), win & (y == 0)
    edges = signal_fraction_edges(scores[sig], w[sig])
    mass_edges = np.arange(TRAIN_REGION[0], TRAIN_REGION[1] + ASIMOV_MASS_BIN / 2, ASIMOV_MASS_BIN)
    # (tight, loose) signal-fraction range of category k (k = 0 loosest), e.g. (0, 2) = top 0-2%
    fr = [0.0] + list(ASIMOV_SIGNAL_FRACTIONS)
    n_cat = len(edges) - 1
    if n_cat == len(ASIMOV_SIGNAL_FRACTIONS):
        ranges = [(100 * fr[n_cat - 1 - k], 100 * fr[n_cat - k]) for k in range(n_cat)]
    else:  # duplicate score cuts collapsed some categories
        ranges = [None] * n_cat
    hists = []
    for k in range(n_cat):
        in_s = sig & (scores >= edges[k]) & (scores < edges[k + 1])
        in_b = bkg & (scores >= edges[k]) & (scores < edges[k + 1])
        s_h, _ = np.histogram(mass[in_s], bins=mass_edges, weights=w[in_s])
        b_h, _ = np.histogram(mass[in_b], bins=mass_edges, weights=w[in_b])
        v_h, _ = np.histogram(mass[in_b], bins=mass_edges, weights=w[in_b] ** 2)
        hists.append([s_h * scale, b_h * scale, v_h * scale ** 2, edges[k], edges[k + 1], ranges[k]])
    # categories run loose -> tight; a category without background joins the next looser one
    k = len(hists) - 1
    while k > 0:
        if hists[k][1].sum() <= 0:
            for i in range(3):
                hists[k - 1][i] = hists[k - 1][i] + hists[k][i]
            hists[k - 1][4] = hists[k][4]
            if hists[k - 1][5] is not None and hists[k][5] is not None:
                hists[k - 1][5] = (hists[k][5][0], hists[k - 1][5][1])
            del hists[k]
        k -= 1
    total, info = 0.0, []
    for k, (s_h, b_h, v_h, lo, hi, frac) in enumerate(hists):
        label = f"{frac[0]:g}-{frac[1]:g}%" if frac is not None else f"cat{k}"
        if b_h.sum() <= 0:  # only possible for the loosest category
            info.append(dict(label=label, low=float(lo), high=float(hi), S=float(s_h.sum()),
                             B=float(b_h.sum()), Z=0.0))
            continue
        s_m, b_m, v_m = _merge_nonpositive(s_h, b_h, v_h)
        z2 = float(np.sum(asimov_z(s_m, b_m, np.sqrt(v_m)) ** 2))
        total += z2
        info.append(dict(label=label, low=float(lo), high=float(hi), S=float(s_h.sum()),
                         B=float(b_h.sum()), n_mass_bins=len(b_m), Z=math.sqrt(z2)))
    z = math.sqrt(total)
    return (z, info) if details else z


# Asimov Z with a fitted background (--objective asimov_fit): the background of each category is
# an exponential in M_mumu fitted (unbinned, weighted ML) to all of its MC in TRAIN_REGION instead
# of the raw MC per mass bin, which a few heavy events make jumpy in the tight categories
ASIMOV_FIT_MIN_EVENTS = 10  # fewer background MC events: the category joins the next looser one
ASIMOV_FIT_LAMBDA_RANGE = (-1.0, 1.0)  # 1/GeV, bracket of the exponential slope
ASIMOV_FIT_PLOT_BIN = 0.5  # GeV, background histogram of the tightest category (trial plots)
SCORE_HIST_BINS = 2000  # BDT probability histograms of the validation folds (trial plots)
ASIMOV_OBJECTIVES = ("asimov", "asimov_fit")


def is_asimov(objective):
    return objective in ASIMOV_OBJECTIVES


def _exp_mean_var(lam, length):
    """Mean and variance of x in [0, length] for the density ~ exp(-lam x)."""
    t = lam * length
    if abs(t) < 1e-4:  # flat limit
        return length / 2 - lam * length ** 2 / 12, length ** 2 / 12
    mean = 1 / lam - length / math.expm1(t)
    var = 1 / lam ** 2 - length ** 2 * math.exp(t) / math.expm1(t) ** 2
    return mean, var


def exponential_bin_fractions(lam, edges, origin=TRAIN_REGION[0], length=None):
    """Fractions of the truncated exponential exp(-lam (m - origin)) on [origin, origin + length]
    in the bins `edges` (ascending, inside the range)."""
    length = TRAIN_REGION[1] - TRAIN_REGION[0] if length is None else length
    x = np.asarray(edges, float) - origin
    if abs(lam * length) < 1e-8:
        return np.diff(x) / length
    cdf = np.expm1(-lam * x) / math.expm1(-lam * length)
    return np.diff(cdf)


def fit_exponential(moments, length=None):
    """Weighted unbinned ML fit of exp(-lam x), x = m - TRAIN_REGION[0], from the weighted moments
    (sum w, sum w x, sum w^2, sum w^2 x, sum w^2 x^2). The ML condition is E_lam[x] = weighted
    mean of x (monotonic in lam). Returns (lam, B, cov) with B = sum w and the sandwich
    covariance of (B, lam) for weighted events."""
    length = TRAIN_REGION[1] - TRAIN_REGION[0] if length is None else length
    sw, swx, sw2, sw2x, sw2x2 = moments
    lo, hi = ASIMOV_FIT_LAMBDA_RANGE
    xbar = min(max(swx / sw, _exp_mean_var(hi, length)[0]), _exp_mean_var(lo, length)[0])
    from scipy.optimize import brentq
    try:
        lam = brentq(lambda l: _exp_mean_var(l, length)[0] - xbar, lo, hi, xtol=1e-10)
    except ValueError:  # xbar at a bracket end
        lam = hi if xbar <= _exp_mean_var(hi, length)[0] else lo
    mu, var = _exp_mean_var(lam, length)
    # per-event scores: w (for B) and w (mu - x) (for lam); information sum(w) var
    meat_ll = mu * mu * sw2 - 2 * mu * sw2x + sw2x2
    meat_bl = mu * sw2 - sw2x
    info = sw * var
    cov = np.array([[sw2, meat_bl / info], [meat_bl / info, meat_ll / info ** 2]])
    return lam, sw, cov


def fitted_background(lam, total, cov, edges, scale=1.0):
    """Expected background per mass bin and its uncertainty (fit covariance of (B, lam))."""
    p = exponential_bin_fractions(lam, edges)
    h = 1e-6
    dp = (exponential_bin_fractions(lam + h, edges) - exponential_bin_fractions(lam - h, edges)) / (2 * h)
    b = total * p
    var = p ** 2 * cov[0, 0] + (total * dp) ** 2 * cov[1, 1] + 2 * total * p * dp * cov[0, 1]
    return b * scale, np.sqrt(np.clip(var, 0, None)) * scale


def binned_asimov_z_fit(scores, y, mass, w, scale=1.0, details=False):
    """binned_asimov_z with the background of every category from an exponential fitted to all of
    its background MC in TRAIN_REGION (fit_exponential) and the fit uncertainty as sigma_b; the
    signal stays the raw MC per ASIMOV_MASS_BIN bin. A category with sum(w) <= 0 or fewer than
    ASIMOV_FIT_MIN_EVENTS background MC events joins the next looser one. details adds, per
    category, the fit (lam, its error, N_eff) and, for the tightest one, its background MC on
    ASIMOV_FIT_PLOT_BIN bins (`tight_hist`)."""
    scores, y, mass, w = (np.asarray(a) for a in (scores, y, mass, w))
    win = (mass > TRAIN_REGION[0]) & (mass < TRAIN_REGION[1])
    sig, bkg = win & (y == 1), win & (y == 0)
    edges = signal_fraction_edges(scores[sig], w[sig])
    n_cat = len(edges) - 1
    mass_edges = np.arange(TRAIN_REGION[0], TRAIN_REGION[1] + ASIMOV_MASS_BIN / 2, ASIMOV_MASS_BIN)
    n_mass = len(mass_edges) - 1
    fr = [0.0] + list(ASIMOV_SIGNAL_FRACTIONS)
    if n_cat == len(ASIMOV_SIGNAL_FRACTIONS):
        ranges = [(100 * fr[n_cat - 1 - k], 100 * fr[n_cat - k]) for k in range(n_cat)]
    else:  # duplicate score cuts collapsed some categories
        ranges = [None] * n_cat
    inner = np.asarray(edges[1:-1])

    # signal per (category, mass bin)
    cat_s = np.searchsorted(inner, scores[sig], side="right")
    bin_s = np.clip(np.searchsorted(mass_edges, mass[sig], side="right") - 1, 0, n_mass - 1)
    s_hist = np.bincount(cat_s * n_mass + bin_s, weights=w[sig], minlength=n_cat * n_mass)
    s_hist = s_hist.reshape(n_cat, n_mass)
    # background moments per category (merging categories = adding moments)
    cat_b = np.searchsorted(inner, scores[bkg], side="right")
    xb, wb = mass[bkg] - TRAIN_REGION[0], w[bkg]
    moments = np.stack([np.bincount(cat_b, weights=v, minlength=n_cat)
                        for v in (np.ones_like(wb), wb, wb * xb, wb ** 2, wb ** 2 * xb, wb ** 2 * xb ** 2)], axis=1)
    groups = [dict(cats=[k], s=s_hist[k].copy(), m=moments[k].copy(), lo=edges[k], hi=edges[k + 1],
                   frac=ranges[k]) for k in range(n_cat)]
    # loose -> tight; a category without enough background joins the next looser one
    k = len(groups) - 1
    while k > 0:
        g = groups[k]
        if g["m"][1] <= 0 or g["m"][0] < ASIMOV_FIT_MIN_EVENTS:
            prev = groups[k - 1]
            prev["cats"] += g["cats"]
            prev["s"] = prev["s"] + g["s"]
            prev["m"] = prev["m"] + g["m"]
            prev["hi"] = g["hi"]
            if prev["frac"] is not None and g["frac"] is not None:
                prev["frac"] = (g["frac"][0], prev["frac"][1])
            del groups[k]
        k -= 1
    total, info = 0.0, []
    for k, g in enumerate(groups):
        label = f"{g['frac'][0]:g}-{g['frac'][1]:g}%" if g["frac"] is not None else f"cat{k}"
        n_ev, sw, swx, sw2, sw2x, sw2x2 = g["m"]
        entry = dict(label=label, low=float(g["lo"]), high=float(g["hi"]), S=float(g["s"].sum() * scale),
                     B=float(sw * scale), n_events=int(n_ev), Z=0.0)
        if sw <= 0 or n_ev < 2:  # only possible for the loosest category
            info.append(entry)
            continue
        lam, b_tot, cov = fit_exponential((sw, swx, sw2, sw2x, sw2x2))
        b, sigma_b = fitted_background(lam, b_tot, cov, mass_edges, scale=scale)
        z2 = float(np.sum(asimov_z(g["s"] * scale, b, sigma_b) ** 2))
        total += z2
        entry.update(Z=math.sqrt(z2), lam=float(lam), lam_err=float(math.sqrt(max(cov[1, 1], 0))),
                     n_eff=float(sw ** 2 / sw2) if sw2 > 0 else 0.0, cov=cov.tolist(), B_raw=float(sw))
        info.append(entry)
    z = math.sqrt(total)
    if not details:
        return z
    # background MC of the tightest category for the fit plot (unscaled: the validation fold)
    tight = info[-1]
    in_t = bkg & (scores >= tight["low"]) & (scores < tight["high"])
    plot_edges = np.arange(TRAIN_REGION[0], TRAIN_REGION[1] + ASIMOV_FIT_PLOT_BIN / 2, ASIMOV_FIT_PLOT_BIN)
    tight["tight_hist"] = dict(edges=plot_edges,
                               sumw=np.histogram(mass[in_t], bins=plot_edges, weights=w[in_t])[0],
                               sumw2=np.histogram(mass[in_t], bins=plot_edges, weights=w[in_t] ** 2)[0])
    return z, info


# ---------------------------------------------------------------------------
# Mass-sculpting check of the Asimov Optuna objectives (constraint + trial plot)
# ---------------------------------------------------------------------------
# A BDT that learns m_mumu (its inputs nearly determine it) carves a background bump under the
# signal, which the exponential of binned_asimov_z_fit would smooth away and reward. Per fixed
# category, the mass shape of the fold's inclusive background (the reference: it carries the
# common, not purely exponential Z-tail curvature, and sculpting cannot change it, since it only
# moves events between categories) times an exponential tilt fitted to the category's sideband
# MC predicts the 120-130 GeV window; an excess of the MC over it
# (fold-combined pull > SCULPT_MAX_PULL in a tight category) makes the trial infeasible. A
# different slope is absorbed by the tilt; only a peak counts.
SCULPT_SIDEBANDS = ((115.0, 120.0), (130.0, 135.0))
SCULPT_WINDOW = (120.0, 130.0)
SCULPT_TIGHT_MAX_FRACTION = 0.10  # constraint: categories entirely within the top 10% of the signal
SCULPT_MAX_PULL = 3.0  # one-sided, fold-combined
SCULPT_MIN_EVENTS = 10  # background MC events in the sidebands needed for a pull
SCULPT_HIST_BIN = 0.1  # GeV: category / complement mass histograms (KS test, trial plot)


def _grid(intervals, step=0.005):
    """Integration grid (x = m - TRAIN_REGION[0]) with trapezoid weights over a union of intervals."""
    xs, ws = [], []
    for lo, hi in intervals:
        n = max(int(round((hi - lo) / step)), 2) + 1
        x = np.linspace(lo, hi, n)
        wt = np.full(n, (hi - lo) / (n - 1))
        wt[[0, -1]] /= 2
        xs.append(x)
        ws.append(wt)
    return np.concatenate(xs), np.concatenate(ws)


def _exp_integrals(lam, grid):
    """(integral, mean, variance) of exp(-lam x) over the grid's support (x, weights): integration
    weights, or a reference shape's bin contents (exp(-lam x) is then a tilt of that shape)."""
    x, wt = grid
    c = x.mean()
    dens = np.exp(-lam * (x - c)) * wt  # shifted by c for numerical range; mean/var unaffected
    z = dens.sum()
    mean = (dens * x).sum() / z
    return z * math.exp(-lam * c), mean, (dens * (x - mean) ** 2).sum() / z


def fit_exponential_sidebands(moments, grid):
    """fit_exponential with the density base(x) exp(-lam x) on the support of `grid` (_grid(...)
    of the sideband intervals, x = m - TRAIN_REGION[0], or a reference shape on them): the
    weighted ML condition E_lam[x] = weighted mean of x still holds (exponential family) and is
    monotonic in lam. Returns (lam, B, cov) with B = sum w and the sandwich covariance."""
    sw, swx, sw2, sw2x, sw2x2 = moments
    lo, hi = ASIMOV_FIT_LAMBDA_RANGE
    mean_of = lambda l: _exp_integrals(l, grid)[1]
    xbar = min(max(swx / sw, mean_of(hi)), mean_of(lo))
    from scipy.optimize import brentq
    try:
        lam = brentq(lambda l: mean_of(l) - xbar, lo, hi, xtol=1e-10)
    except ValueError:
        lam = hi if xbar <= mean_of(hi) else lo
    _, mu, var = _exp_integrals(lam, grid)
    info = sw * var
    meat_ll = mu * mu * sw2 - 2 * mu * sw2x + sw2x2
    meat_bl = mu * sw2 - sw2x
    cov = np.array([[sw2, meat_bl / info], [meat_bl / info, meat_ll / info ** 2]])
    return lam, sw, cov


def sideband_prediction(lam, total, cov, g_sb, g_t, var_sb=None, var_t=None):
    """Yield on the target grid `g_t` of the (tilted) shape normalized to `total` on the sideband
    grid `g_sb`, and its uncertainty: fit covariance plus, for a reference shape, its statistical
    uncertainty (var_sb / var_t: sum w^2 per reference bin)."""
    def ratio(l):
        return _exp_integrals(l, g_t)[0] / _exp_integrals(l, g_sb)[0]

    r, h = ratio(lam), 1e-6
    dr = (ratio(lam + h) - ratio(lam - h)) / (2 * h)
    var = r * r * cov[0, 0] + (total * dr) ** 2 * cov[1, 1] + 2 * r * total * dr * cov[0, 1]
    if var_sb is not None:  # reference statistics: R = A / C over independent regions
        tilt_t, tilt_sb = np.exp(-lam * g_t[0]), np.exp(-lam * g_sb[0])
        a, c = float((g_t[1] * tilt_t).sum()), float((g_sb[1] * tilt_sb).sum())
        rel2 = float((var_t * tilt_t ** 2).sum()) / a ** 2 + float((var_sb * tilt_sb ** 2).sum()) / c ** 2
        var += (total * r) ** 2 * rel2
    return total * r, math.sqrt(max(var, 0.0))


def signal_fraction_categories(scores, w, fractions=ASIMOV_SIGNAL_FRACTIONS):
    """signal_fraction_edges plus a label per category (ascending score, loose -> tight) with its
    signal-fraction range, e.g. "2-5%". When tied scores make several cuts coincide, the merged
    category is labelled with its whole range (e.g. "0-5%"), so labels always mean the same
    fractions across folds and trials."""
    scores, w = np.asarray(scores), np.asarray(w)
    order = np.argsort(-scores)
    cum = np.cumsum(w[order]) / w.sum()
    cuts = [scores[order][min(np.searchsorted(cum, f), len(scores) - 1)] for f in fractions[:-1]]
    unique = sorted(set(cuts))
    above = {c: max(f for f, cut in zip(fractions[:-1], cuts) if cut == c) for c in unique}  # fraction >= cut
    bounds = [fractions[-1]] + [above[c] for c in unique] + [0.0]  # loose -> tight
    labels = [f"{100 * bounds[k + 1]:g}-{100 * bounds[k]:g}%" for k in range(len(unique) + 1)]
    return [-np.inf] + unique + [np.inf], labels


def sculpt_is_tight(label):
    """Whether a category label ("a-b%") lies entirely within the top SCULPT_TIGHT_MAX_FRACTION."""
    try:
        return float(label.rstrip("%").split("-")[1]) <= 100 * SCULPT_TIGHT_MAX_FRACTION + 1e-9
    except (IndexError, ValueError):
        return False


def sculpt_prepare(y, mass, w):
    """The round-independent part of sculpt_summary for one validation fold: the background rows
    in TRAIN_REGION and their SCULPT_HIST_BIN mass bin."""
    y, mass, w = (np.asarray(a) for a in (y, mass, w))
    rows = np.flatnonzero((y == 0) & (mass > TRAIN_REGION[0]) & (mass < TRAIN_REGION[1]))
    edges = np.arange(TRAIN_REGION[0], TRAIN_REGION[1] + SCULPT_HIST_BIN / 2, SCULPT_HIST_BIN)
    n_bins = len(edges) - 1
    b = np.clip(((mass[rows] - TRAIN_REGION[0]) / SCULPT_HIST_BIN).astype(np.int64), 0, n_bins - 1)
    centres = (edges[:-1] + edges[1:]) / 2
    in_sb = np.zeros(n_bins, bool)
    for lo, hi in SCULPT_SIDEBANDS:
        in_sb |= (centres > lo) & (centres < hi)
    in_win = (centres > SCULPT_WINDOW[0]) & (centres < SCULPT_WINDOW[1])
    return dict(rows=rows, bin=b, w=np.asarray(w[rows], float), edges=edges, n_bins=n_bins,
                xc=centres - TRAIN_REGION[0], in_sb=in_sb, in_win=in_win)


def sculpt_summary(scores, inner_edges, labels, prep):
    """Per fixed category (inner score edges ascending, loose -> tight; labels from
    signal_fraction_categories) of one validation fold:
    background MC in the window vs the prediction from the sidebands (pull; see SCULPT_* above)
    and the SCULPT_HIST_BIN mass histograms (sum w, sum w^2) for the KS test and the plot. The
    sideband fit uses the moments of the histograms (bin centres; 0.1 GeV bins)."""
    inner = np.asarray(inner_edges)
    n_cat, n_bins = len(inner) + 1, prep["n_bins"]
    cat = np.searchsorted(inner, np.asarray(scores)[prep["rows"]], side="right")
    key, w = cat * n_bins + prep["bin"], prep["w"]
    h = np.bincount(key, weights=w, minlength=n_cat * n_bins).reshape(n_cat, n_bins)
    h2 = np.bincount(key, weights=w * w, minlength=n_cat * n_bins).reshape(n_cat, n_bins)
    xc, in_sb, in_win = prep["xc"], prep["in_sb"], prep["in_win"]
    n_rows = np.bincount(cat * n_bins + prep["bin"], minlength=n_cat * n_bins).reshape(n_cat, n_bins)
    ref, ref2 = np.clip(h.sum(axis=0), 0, None), np.clip(h2.sum(axis=0), 0, None)  # inclusive background
    g_sb, g_win = (xc[in_sb], ref[in_sb]), (xc[in_win], ref[in_win])
    cats = []
    for k in range(n_cat):
        hs, h2s = h[k][in_sb], h2[k][in_sb]
        n_sb = int(n_rows[k][in_sb].sum())
        b_win, v_win = float(h[k][in_win].sum()), float(h2[k][in_win].sum())
        entry = dict(label=labels[k], n_sideband=n_sb, B_win=b_win, pull=None,
                     hist=h[k].astype(np.float32), hist2=h2[k].astype(np.float32))
        if n_sb >= SCULPT_MIN_EVENTS and hs.sum() > 0 and g_sb[1].sum() > 0 and g_win[1].sum() > 0:
            x = xc[in_sb]
            moments = (hs.sum(), (hs * x).sum(), h2s.sum(), (h2s * x).sum(), (h2s * x * x).sum())
            lam, b_sb, cov = fit_exponential_sidebands(moments, g_sb)
            pred, pred_err = sideband_prediction(lam, b_sb, cov, g_sb, g_win, ref2[in_sb], ref2[in_win])
            denom = math.sqrt(max(v_win, 0.0) + pred_err ** 2)
            tilted = ref * np.exp(-lam * xc)  # predicted mass shape over the whole range (trial plot)
            entry.update(lam=float(lam), B_sideband=float(b_sb), B_pred=float(pred), B_pred_err=float(pred_err),
                         pull=float((b_win - pred) / denom) if denom > 0 else None,
                         pred_hist=(b_sb * tilted / tilted[in_sb].sum()).astype(np.float32))
        cats.append(entry)
    return dict(categories=cats, hist_edges=prep["edges"])


def combine_sculpt(infos, best_round):
    """Fold-combined sculpting check at the trial's round (each fold at its fold_round):
    {label: dict(pull = sum(pulls)/sqrt(n), ks_p, n_folds, ...)}, the constraint value
    max over the tight categories (sculpt_is_tight) of (pull - SCULPT_MAX_PULL) (<= 0: feasible)
    and the summed histograms (`hist_fit`: only the folds with a pull, comparable with `pred`).
    Per category also, for the trial plot and the record: the per-fold pulls, window MC, window
    prediction (+- sigma) and tilt lambda, their fold sums (display only: the decision uses the
    combined pull), and the fold-summed inclusive background (`incl`, the prediction's reference)."""
    from scipy.special import kolmogorov
    per_label, edges = {}, None
    for info in infos:
        r = fold_round(info, best_round)
        if r is None or r not in info.get("sculpt", {}):
            continue
        summary = info["sculpt"][r]
        edges = summary["hist_edges"]
        total = np.sum([c["hist"] for c in summary["categories"]], axis=0)
        total2 = np.sum([c["hist2"] for c in summary["categories"]], axis=0)
        for c in summary["categories"]:
            agg = per_label.setdefault(c["label"], dict(pulls=[], hist=0.0, hist2=0.0, rest=0.0, rest2=0.0,
                                                        incl=0.0, pred=0.0, pred_folds=0, folds=0, b_win=[],
                                                        hist_fit=0.0, hist2_fit=0.0,
                                                        b_pred=[], b_pred_err=[], lam=[]))
            agg["folds"] += 1
            agg["incl"] = agg["incl"] + total
            if c["pull"] is not None:
                agg["pulls"].append(c["pull"])
                agg["pred"] = agg["pred"] + c["pred_hist"]
                agg["pred_folds"] += 1
                agg["hist_fit"] = agg["hist_fit"] + c["hist"]
                agg["hist2_fit"] = agg["hist2_fit"] + c["hist2"]
                for key, name in (("b_win", "B_win"), ("b_pred", "B_pred"), ("b_pred_err", "B_pred_err"),
                                  ("lam", "lam")):
                    agg[key].append(c[name])
            agg["hist"] = agg["hist"] + c["hist"]
            agg["hist2"] = agg["hist2"] + c["hist2"]
            agg["rest"] = agg["rest"] + (total - c["hist"])
            agg["rest2"] = agg["rest2"] + (total2 - c["hist2"])
    out = {}
    for label, agg in per_label.items():
        pulls = agg["pulls"]
        pull = float(np.sum(pulls) / math.sqrt(len(pulls))) if pulls else None
        ks_p = None
        s1, s2 = float(np.sum(agg["hist"])), float(np.sum(agg["rest"]))
        if s1 > 0 and s2 > 0:
            d = float(np.max(np.abs(np.cumsum(agg["hist"]) / s1 - np.cumsum(agg["rest"]) / s2)))
            n1 = s1 ** 2 / float(np.sum(agg["hist2"])) if np.sum(agg["hist2"]) > 0 else 0.0
            n2 = s2 ** 2 / float(np.sum(agg["rest2"])) if np.sum(agg["rest2"]) > 0 else 0.0
            if n1 > 0 and n2 > 0:
                ks_p = float(kolmogorov(d * math.sqrt(n1 * n2 / (n1 + n2))))
        b_win_sum, b_pred_sum = float(np.sum(agg["b_win"])), float(np.sum(agg["b_pred"]))
        out[label] = dict(pull=pull, ks_p=ks_p, n_folds=len(pulls), hist=agg["hist"], hist2=agg["hist2"],
                          rest=agg["rest"], incl=agg["incl"], pred=agg["pred"] if pulls else None,
                          hist_fit=agg["hist_fit"], hist2_fit=agg["hist2_fit"], n_folds_all=agg["folds"],
                          fold_pulls=[float(p) for p in pulls], fold_lam=[float(v) for v in agg["lam"]],
                          B_win_sum=b_win_sum if pulls else None, B_pred_sum=b_pred_sum if pulls else None,
                          B_pred_err_sum=float(math.sqrt(np.sum(np.square(agg["b_pred_err"])))) if pulls else None,
                          excess=(b_win_sum / b_pred_sum - 1) if pulls and b_pred_sum > 0 else None)
    tight = [c["pull"] for l, c in out.items() if sculpt_is_tight(l) and c["pull"] is not None]
    constraint = max(p - SCULPT_MAX_PULL for p in tight) if tight else -SCULPT_MAX_PULL
    return dict(categories=out, constraint=float(constraint), hist_edges=edges)


def sculpt_attrs(combined):
    """JSON-serializable summary of combine_sculpt for the Optuna trial / config."""
    return dict(constraint=combined["constraint"], max_pull=SCULPT_MAX_PULL,
                categories={label: {k: c[k] for k in ("pull", "ks_p", "n_folds", "fold_pulls", "fold_lam",
                                                      "B_win_sum", "B_pred_sum", "B_pred_err_sum", "excess")}
                            for label, c in combined["categories"].items()})


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


def heldout_summary(margin, base_logit, y, mass, w, sculpt_prep, scale, metric, tight_fit=False):
    """The Asimov Z and trial-plot summaries of one held-out sample at one round (margin without the
    base margin `base_logit`; w = physics weights): `z_curve` (Z of `metric`, binned_asimov_z or
    binned_asimov_z_fit, scaled by `scale`), `z_categories` ([(label, Z), ...]), `score_hists`
    ({0: bkg, 1: signal} on SCORE_HIST_BINS bins of the probability), `cat_edges_prob` (inner
    category edges in probability), `sculpt` (sculpt_summary) and, with tight_fit, `tight_fit`
    (the tightest category's entry of binned_asimov_z_fit, with its background histogram)."""
    z, cats = metric(margin, y, mass, w, scale=scale, details=True)
    prob = 1 / (1 + np.exp(-(margin + base_logit)))
    bins = np.minimum((prob * SCORE_HIST_BINS).astype(np.int64), SCORE_HIST_BINS - 1)
    sig = (y == 1) & (mass > TRAIN_REGION[0]) & (mass < TRAIN_REGION[1])
    edges, labels = signal_fraction_categories(margin[sig], w[sig])
    inner = np.asarray(edges[1:-1])
    out = dict(z_curve=z, z_categories=[(c["label"], c["Z"]) for c in cats],
               score_hists={cls: np.bincount(bins[y == cls], weights=w[y == cls], minlength=SCORE_HIST_BINS)
                            for cls in (0, 1)},
               cat_edges_prob=1 / (1 + np.exp(-(inner + base_logit))),
               sculpt=sculpt_summary(margin, inner, labels, sculpt_prep))
    if tight_fit:
        out["tight_fit"] = dict(cats[-1])
    return out


def single_sample_info(p, y, mass, w, n_rounds, scale, objective):
    """One held-out sample (e.g. the untouched test sample) scored with probabilities `p` by a model
    of `n_rounds` rounds, as a cross_validate fold `info` (fold 0, every summary at round n_rounds),
    so that combine_sculpt, fold_round and the trial plots work on it unchanged. The Z is that of
    `objective` (binned_asimov_z_fit for "asimov_fit", else binned_asimov_z); the exponential fit
    of the tightest category (`tight_fit`) is always computed. w = physics weights."""
    p, y, mass, w = (np.asarray(a, dtype=float) for a in (p, y, mass, w))
    p = np.clip(p, 1e-15, 1 - 1e-15)
    margin = np.log(p) - np.log1p(-p)  # the ranking is all that matters; base margin 0
    metric = binned_asimov_z_fit if objective == "asimov_fit" else binned_asimov_z
    summary = heldout_summary(margin, 0.0, y, mass, w, sculpt_prepare(y, mass, w), scale, metric)
    summary["tight_fit"] = dict(binned_asimov_z_fit(margin, y, mass, w, scale=scale, details=True)[1][-1])
    r = int(n_rounds)
    info = {key: {r: value} for key, value in summary.items()}
    info.update(fold=0, trained_rounds=r, best_z=summary["z_curve"], best_z_round=r)
    return info


# ---------------------------------------------------------------------------
# Cross-validation and Optuna (development stage)
# ---------------------------------------------------------------------------
def cross_validate(x, y, w, cv_folds, standardizers, names, do_standardization, params,
                   n_estimators, early_stopping_rounds, trial=None, label="", progress_every=0,
                   objective="auc_w", asimov_inputs=None, checkpoint_every=ASIMOV_CHECKPOINT_EVERY,
                   asimov_scale=1.0, trial_callback=None):
    """Train on N_FOLDS-1 folds, early-stop on the remaining one, for every fold.
    Returns one dict per fold (validation metrics + best_iteration). With objective="asimov"
    (binned_asimov_z) or "asimov_fit" (binned_asimov_z_fit) each fold also gets `z_curve`: the
    binned Asimov Z of the validation fold (asimov_inputs = (mass, physics weights) of all rows,
    scaled by asimov_scale) every `checkpoint_every` rounds up to the last trained round,
    `z_categories` (round -> [(category label, Z), ...]) and, per round, the summaries of the
    trial plots: `score_hists` ({0: bkg, 1: signal} physics-weighted histograms of the
    probability on SCORE_HIST_BINS bins), `cat_edges_prob` (inner category edges in probability)
    and, with asimov_fit, `tight_fit` (the tightest category's fit and background histogram).
    trial_callback(infos, pruned_after) runs with the folds done right before a trial is pruned."""
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
        if is_asimov(objective):
            mass, w_phys = asimov_inputs
            metric = binned_asimov_z_fit if objective == "asimov_fit" else binned_asimov_z
            trained = int(model.get_booster().num_boosted_rounds())
            rounds = list(range(checkpoint_every, trained + 1, checkpoint_every))
            if not rounds or rounds[-1] != trained:
                rounds.append(trained)
            info["z_curve"], info["z_categories"] = {}, {}
            info["score_hists"], info["cat_edges_prob"], info["tight_fit"], info["sculpt"] = {}, {}, {}, {}
            t_asimov = time.time()
            y_va, m_va, w_va = y[va], mass[va], w_phys[va]
            sculpt_prep = sculpt_prepare(y_va, m_va, w_va)
            # Running raw margin (trees only, base_margin = 0): each checkpoint only adds the trees
            # since the previous one, so all checkpoints together cost one full prediction. Z only
            # depends on the score ranking (categories are signal quantiles), which the margin
            # shares with the probability.
            margin, zero, r_prev = np.zeros(len(va)), np.zeros(len(va)), 0
            base_logit = None
            for r in rounds:
                margin += model.predict(x_va, output_margin=True, base_margin=zero, iteration_range=(r_prev, r))
                r_prev = r
                if base_logit is None:  # the model's base margin, for the probability of the trial plots
                    head = slice(0, min(16, len(va)))
                    full = model.predict(x_va[head], output_margin=True, iteration_range=(0, r))
                    base_logit = float(np.mean(full - margin[head]))
                summary = heldout_summary(margin, base_logit, y_va, m_va, w_va, sculpt_prep, asimov_scale,
                                          metric, tight_fit=objective == "asimov_fit")
                for key, value in summary.items():
                    info[key][r] = value
            info["asimov_seconds"] = time.time() - t_asimov
            best_round = max(info["z_curve"], key=info["z_curve"].get)
            info.update(trained_rounds=trained, best_z=info["z_curve"][best_round], best_z_round=best_round)
        infos.append(info)
        # XGBoost's sklearn wrapper holds reference cycles: free the GPU memory before the next fit
        del x_tr, x_va, model
        gc.collect()
        note = gpu_memory_note()
        asimov_note = (f", best Asimov Z {info['best_z']:.4f} at round {info['best_z_round']} of "
                       f"{info['trained_rounds']} (Asimov evaluation {info['asimov_seconds']:.1f} s)"
                       if is_asimov(objective) else "")
        print(f"[CV   ] {label}fold {k}: {n_trees} trees, weighted validation AUC "
              f"{info['auc_w']:.5f}, logloss {info['logloss_w']:.5f}{asimov_note}"
              + (f" | {note}" if note else ""), flush=True)
        if trial is not None:
            import optuna
            value = (mean_z_curve(infos)[1] if is_asimov(objective)
                     else float(np.mean([i["auc_w"] for i in infos])))
            trial.report(value, step=k)
            if trial.should_prune():
                if trial_callback is not None:
                    trial_callback(infos, k)
                raise optuna.TrialPruned()
    return infos


def fold_round(info, r):
    """The checkpoint of `info` used for round r: r itself, or the fold's last one before it if
    the fold stopped earlier (its model has no more trees); None if it has none <= r."""
    done = [c for c in info["z_curve"] if c <= r]
    return max(done) if done else None


def mean_z_curve(infos, full=False):
    """(best checkpoint, its mean Z) of the fold-averaged Asimov Z curve (plus the whole curve
    {round: mean Z} with full=True). A fold that stopped before a checkpoint contributes its Z
    at its last trained round (its model has no more trees)."""
    checkpoints = sorted({r for i in infos for r in i["z_curve"]})
    mean = {}
    for r in checkpoints:
        values = []
        for i in infos:
            c = fold_round(i, r)
            values.append(i["z_curve"][c] if c is not None else 0.0)
        mean[r] = float(np.mean(values))
    best = max(mean, key=mean.get)
    return (best, mean[best], mean) if full else (best, mean[best])


# Optuna search space: name -> (kind, low, high, log)
SEARCH_SPACE = {
    "max_depth": ("int", 2, 7, False),
    "learning_rate": ("float", 0.01, 0.2, True),
    "min_child_weight": ("float", 1.0, 20.0, True),
    "subsample": ("float", 0.6, 1.0, False),
    "colsample_bytree": ("float", 0.4, 1.0, False),
    "reg_lambda": ("float", 0.1, 10.0, True),
    "reg_alpha": ("float", 1e-4, 1.0, True),
}
MAX_CONSECUTIVE_FAILURES = 3  # failed trials in a row that stop the study (e.g. a broken setup)


def search_space_json():
    return {name: list(spec) for name, spec in SEARCH_SPACE.items()}


def trial_constraint(trial):
    """Optuna constraints_func: <= 0 is feasible; trials without a sculpting check count as feasible."""
    return trial.user_attrs.get("constraint", [0.0])


def best_feasible_trial(study):
    """(best COMPLETE trial with constraint <= 0, True), or (best COMPLETE trial, False) if no
    trial is feasible, or (None, False) without completed trials."""
    from optuna.trial import TrialState
    done = [t for t in study.get_trials(deepcopy=False, states=(TrialState.COMPLETE,))]
    if not done:
        return None, False
    feasible = [t for t in done if max(trial_constraint(t)) <= 0]
    pool = feasible or done
    return max(pool, key=lambda t: t.value), bool(feasible)


def _setup_differences(stored, current):
    """Keys whose (JSON-normalized) values differ between two setup dicts."""
    a, b = json.loads(json.dumps(stored or {}, default=float)), json.loads(json.dumps(current or {}, default=float))
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def run_optuna_cv(x, y, w, cv_folds, names, do_standardization, n_trials, seed, device,
                  n_estimators, early_stopping_rounds, progress_every=0, objective="auc_w",
                  asimov_inputs=None, asimov_scale=1.0, checkpoint_every=ASIMOV_CHECKPOINT_EVERY,
                  trial_callback=None, timeout=None, storage=None, study_name=None, resume=False,
                  setup=None, on_trial_done=None):
    """Optuna study maximizing the mean weighted validation AUC over the CV folds, or with
    objective="asimov"/"asimov_fit" the best fold-averaged binned Asimov Z over the boosting
    checkpoints, subject to the mass-sculpting constraint (combine_sculpt; infeasible trials are
    never chosen by best_feasible_trial).
    trial_callback(number, params, infos, pruned_after) runs at the end of every asimov trial
    (pruned_after = the last fold done if Optuna pruned it, else None), e.g. a diagnostic plot;
    an exception in it is only reported. `timeout` (seconds): no new trial starts after it (the
    running one finishes), so a long study still ends with a best trial.
    storage / study_name: an Optuna storage URL (e.g. sqlite) keeping every trial on disk. A new
    study is created unless resume=True, which continues the stored one: its `setup` user attribute
    must equal `setup`, trials left RUNNING by a crash are marked FAIL, and n_trials is the total
    (completed + pruned) to reach. on_trial_done(study, trial) runs after every finished trial
    (e.g. writing the best-so-far configuration). A trial that raises is recorded as FAIL and the
    study goes on, unless MAX_CONSECUTIVE_FAILURES trials in a row fail."""
    import optuna
    from optuna.trial import TrialState

    asimov = is_asimov(objective)

    def make_sampler(sampler_seed):
        kwargs = dict(seed=sampler_seed)
        if asimov:
            kwargs["constraints_func"] = trial_constraint
        try:
            return optuna.samplers.TPESampler(**kwargs)
        except TypeError:  # an Optuna without constraints_func: best_feasible_trial still applies it
            print("[WARNING] this Optuna version has no TPESampler(constraints_func): the sampler ignores "
                  "the sculpting constraint (the best trial is still chosen among feasible ones)", flush=True)
            kwargs.pop("constraints_func")
            return optuna.samplers.TPESampler(**kwargs)

    pruner = optuna.pruners.MedianPruner(n_startup_trials=10, n_warmup_steps=1)
    n_remaining = n_trials
    if resume:
        probe = optuna.load_study(study_name=study_name, storage=storage)
        differences = _setup_differences(probe.user_attrs.get("setup"), setup)
        if differences:
            raise SystemExit(f"[ERROR] the stored study {study_name} was made with a different setup "
                             f"({', '.join(differences)}): it cannot be resumed. Run without --optuna-resume "
                             "to start a new study (the stored one is archived).")
        stale = probe.get_trials(deepcopy=False, states=(TrialState.RUNNING,))
        for t in stale:  # left RUNNING by the crash
            probe._storage.set_trial_state_values(t._trial_id, state=TrialState.FAIL)
        states = [t.state for t in probe.get_trials(deepcopy=False)]
        n_done = sum(st in (TrialState.COMPLETE, TrialState.PRUNED) for st in states)
        n_remaining = max(0, n_trials - n_done)
        print(f"[OPTUNA] resuming {study_name}: {states.count(TrialState.COMPLETE)} completed, "
              f"{states.count(TrialState.PRUNED)} pruned, {states.count(TrialState.FAIL)} failed trials "
              f"({len(stale)} left running by the interruption, now failed); {n_remaining} more to reach "
              f"{n_trials}", flush=True)
        # a new sampler seed: the random startup trials of the first run are not repeated
        study = optuna.load_study(study_name=study_name, storage=storage,
                                  sampler=make_sampler(seed + len(states)), pruner=pruner)
    else:
        study = optuna.create_study(study_name=study_name, storage=storage, direction="maximize",
                                    sampler=make_sampler(seed), pruner=pruner)
        if setup is not None:
            study.set_user_attr("setup", json.loads(json.dumps(setup, default=float)))

    standardizers = [fit_standardizer(x[tr], names) if do_standardization else ({}, {})
                     for tr, _ in cv_folds]
    trial_progress = max(1, n_estimators // 10) if progress_every else 0
    print(f"[OPTUNA] {n_remaining} trials x {N_FOLDS} folds, up to {n_estimators} rounds (early "
          f"stopping {early_stopping_rounds}), objective {objective}, device={device}"
          + (f", timeout {timeout / 3600:.2f} h" if timeout else "")
          + (f", storage {storage}" if storage else "")
          + f" | {gpu_memory_note() or 'no GPU readout'}", flush=True)

    def objective_fn(trial):
        tag = f"trial {trial.number + 1} "
        params = dict(base_xgb_params(device))
        for name, (kind, low, high, log) in SEARCH_SPACE.items():
            params[name] = (trial.suggest_int(name, low, high) if kind == "int"
                            else trial.suggest_float(name, low, high, log=log))
        print(f"[OPTUNA] {tag}start: " + ", ".join(f"{k}={v:.4g}" for k, v in trial.params.items()),
              flush=True)
        t0 = time.time()

        def report(infos, pruned_after):
            if trial_callback is None or not asimov:
                return
            try:
                trial_callback(trial.number, dict(trial.params), infos, pruned_after)
            except Exception as error:  # a diagnostic plot must never stop the study
                print(f"[WARNING] {tag}trial callback failed: {error}", flush=True)

        infos = cross_validate(x, y, w, cv_folds, standardizers, names, do_standardization, params,
                               n_estimators, early_stopping_rounds, trial=trial, label=tag,
                               progress_every=trial_progress, objective=objective,
                               asimov_inputs=asimov_inputs, asimov_scale=asimov_scale,
                               checkpoint_every=checkpoint_every, trial_callback=report)
        for key in ("auc_w", "logloss_w", "best_iteration"):
            trial.set_user_attr(f"fold_{key}", [i[key] for i in infos])
        if asimov:
            best_round, value = mean_z_curve(infos)
            trial.set_user_attr("best_checkpoint", int(best_round))
            trial.set_user_attr("fold_z_curves", [{str(r): z for r, z in i["z_curve"].items()} for i in infos])
            trial.set_user_attr("fold_best_z", [i["best_z"] for i in infos])
            # per-category Z of every fold at the chosen round (the CV side of --stage test's comparison)
            trial.set_user_attr("fold_z_categories", [dict(i["z_categories"][fold_round(i, best_round)])
                                                      for i in infos if fold_round(i, best_round) is not None])
            sculpt = sculpt_attrs(combine_sculpt(infos, best_round))
            trial.set_user_attr("sculpt", sculpt)
            trial.set_user_attr("constraint", [sculpt["constraint"]])
            report(infos, None)
            tight = {l: c["pull"] for l, c in sculpt["categories"].items() if sculpt_is_tight(l) and c["pull"] is not None}
            max_pull = f"{max(tight.values()):+.2f}" if tight else "n/a (too few sideband MC events)"
            print(f"[OPTUNA] {tag}done in {time.time() - t0:.1f} s: mean Asimov Z {value:.4f} at round "
                  f"{best_round} (mean weighted AUC {np.mean([i['auc_w'] for i in infos]):.5f}); sculpting: "
                  f"max tight-category window pull {max_pull} -> "
                  f"{'feasible' if sculpt['constraint'] <= 0 else 'INFEASIBLE'}", flush=True)
            return value
        mean_auc = float(np.mean([i["auc_w"] for i in infos]))
        print(f"[OPTUNA] {tag}done in {time.time() - t0:.1f} s: mean weighted validation AUC "
              f"{mean_auc:.5f}", flush=True)
        return mean_auc

    def after_trial(study, trial):
        if trial.state == TrialState.FAIL:
            print(f"[WARNING] trial {trial.number + 1} failed; the study goes on", flush=True)
            recent = study.get_trials(deepcopy=False)[-MAX_CONSECUTIVE_FAILURES:]
            if len(recent) == MAX_CONSECUTIVE_FAILURES and all(t.state == TrialState.FAIL for t in recent):
                print(f"[ERROR] {MAX_CONSECUTIVE_FAILURES} trials in a row failed: stopping the study", flush=True)
                study.stop()
        if on_trial_done is not None:
            try:
                on_trial_done(study, trial)
            except Exception as error:
                print(f"[WARNING] writing the best-so-far configuration failed: {error!r}", flush=True)

    if n_remaining > 0:
        study.optimize(objective_fn, n_trials=n_remaining, timeout=timeout, callbacks=[after_trial],
                       catch=(Exception,))
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
        _restore_base_score(booster, f"{models_dir}/model_{base}.json")
        bundle.append(dict(booster=booster, meta=meta, fold=k))
    if len({tuple(b["meta"]["variables"]) for b in bundle}) != 1:
        raise RuntimeError("fold models were trained with different variable lists")
    return bundle


def _base_score_of(learner):
    """base_score of a learner JSON block: "5.04E-1" (xgboost < 3) or "[5.04E-1]" (>= 3)."""
    return float(str(learner["learner_model_param"]["base_score"]).strip("[]").split(",")[0])


def _restore_base_score(booster, model_path):
    """Give the booster back the base_score the model was saved with, when the running xgboost
    loaded a different one. xgboost 1.7.5 (cmsenv on LPC / Condor) drops the base_score that
    >= 2.0 estimates and stores (~0.504 for the K-fold models) and uses 0.5, which shifts every
    score by up to ~4.5e-3. A no-op when they agree (e.g. on EAF, where the models were trained).
    Verified on 1.7.5: scores then match the EAF (3.2.0) ones bit for bit."""
    with open(model_path) as f:
        learner = json.load(f)["learner"]
    saved = _base_score_of(learner)
    loaded = _base_score_of(json.loads(booster.save_config())["learner"])
    if saved == loaded:
        return
    objective = learner["objective"]["name"]
    if objective != "binary:logistic":
        raise RuntimeError(f"{model_path}: base_score restore only checked for binary:logistic, "
                           f"not {objective}; score in the xgboost version the model was trained with")
    print(f"[WARNING] {model_path}: running xgboost loaded base_score {loaded:.7g} instead of the "
          f"saved {saved:.7g}; restoring it")
    booster.set_param({"base_score": saved})


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
