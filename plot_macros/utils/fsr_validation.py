"""Helpers for plot_fsr_validation.py: loading, blinding, invariants, metrics, plotting.

Inputs are final CreateTuple outputs (tree ``tree_output``) produced since FSR recovery became the baseline
(un-suffixed kinematics FSR-dressed, bare values in ``*_noFSR``).
Run from ``plot_macros/`` (same convention as the other macros).
"""

from __future__ import annotations

import glob
import os

import awkward as ak
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import uproot as ur

from plot_effective_sigma import effective_sigma
from utils.helper import get_canvas, save_figure

TREE_NAME = "tree_output"
WEIGHT_BRANCH = "weight"
NULL_VALUE = -999.0
MUON_MASS = 0.1056583755

# Blinding (CLAUDE.md): Data events with the nominal or FSR mass in 120-130 GeV must never be inspected. The
# validation only uses the Z control region, so data is cut hard to both masses below this value on load.
DATA_MAX_MASS = 110.0

# Reference DeltaR(mu, gamma) split for the FSR diagnostics: the NanoAOD GenDressedLepton dressing cone
# (lepConeSize = 0.1). Reco FSR recovery accepts photons up to DeltaR < 0.5.
DRESSING_CONE = 0.1

# FSR recovery is the baseline: un-suffixed muon/dimuon kinematics are FSR-dressed, bare ones are *_noFSR
MASS_BRANCHES = ["diMuon_bsConstrainedMass", "diMuon_bsConstrainedMass_noFSR"]
SCALAR_BRANCHES = [
    WEIGHT_BRANCH,
    "PV",
    "is_ggH_category",
    "is_VBF_category",
    *MASS_BRANCHES,
    "diMuon_bsConstrainedPt",
    "diMuon_bsConstrainedPt_noFSR",
    "diMuon_nFSR",
]
for _mu in ("mu1", "mu2"):
    SCALAR_BRANCHES += [
        f"{_mu}_bsConstrainedPt",
        f"{_mu}_bsConstrainedPt_noFSR",
        f"{_mu}_eta",
        f"{_mu}_phi",
        f"{_mu}_hasFSR",
        f"{_mu}_fsrPhoton_pt",
        f"{_mu}_fsrPhoton_dR",
    ]
MC_BRANCHES = ["gen_mll"]


# --------------------------------------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------------------------------------- #
def expand(patterns: list[str] | None) -> list[str]:
    files = []
    for pattern in patterns or []:
        matched = sorted(glob.glob(pattern))
        if not matched:
            raise FileNotFoundError(f"No file matches {pattern}")
        files += matched
    return files


def looks_like_data(path: str) -> bool:
    name = os.path.basename(path).lower()
    return "data" in name or name.startswith("muon")


def load(files: list[str], is_data: bool, max_events: int | None = None) -> ak.Array:
    """Load the validation branches. Data (or any file that looks like data) is blinded on load."""
    if not files:
        return None
    is_data = is_data or any(looks_like_data(f) for f in files)
    branches = SCALAR_BRANCHES + ([] if is_data else MC_BRANCHES)
    arrays = []
    n_read = 0
    for path in files:
        with ur.open(path) as f:
            tree = f[TREE_NAME]
            available = set(tree.keys())
            missing = [b for b in branches if b not in available]
            if missing:
                raise KeyError(f"{path} is missing branches {missing}; produce it with the FSR-recovery CreateTuple")
            stop = None if max_events is None else max(0, max_events - n_read)
            if stop == 0:
                break
            arr = tree.arrays(branches, entry_stop=stop)
            if is_data:
                # Hard blinding mask. Applied before anything else is computed; there is no option to disable it.
                keep = (arr["diMuon_bsConstrainedMass"] < DATA_MAX_MASS) & (
                    arr["diMuon_bsConstrainedMass_noFSR"] < DATA_MAX_MASS
                )
                arr = arr[keep]
            arrays.append(arr)
            n_read += len(arr)
    events = ak.concatenate(arrays) if len(arrays) > 1 else arrays[0]
    if is_data:
        for mass in MASS_BRANCHES:
            assert ak.all(events[mass] < DATA_MAX_MASS)
    return events


def np_(events, branch) -> np.ndarray:
    return ak.to_numpy(events[branch]).astype(float)


def weights(events) -> np.ndarray:
    return np_(events, WEIGHT_BRANCH)


# --------------------------------------------------------------------------------------------------------- #
# Implementation invariants
# --------------------------------------------------------------------------------------------------------- #
def invariants(events, tol=1e-3) -> dict[str, int]:
    """Count violations of properties the FSR implementation must satisfy (0 everywhere is expected)."""
    out = {"n_events": len(events)}
    nfsr = np.zeros(len(events), dtype=int)
    for mu in ("mu1", "mu2"):
        has = ak.to_numpy(events[f"{mu}_hasFSR"]).astype(bool)
        nfsr += has
        pt, pt_bare = np_(events, f"{mu}_bsConstrainedPt"), np_(events, f"{mu}_bsConstrainedPt_noFSR")
        photon_pt, photon_dr = np_(events, f"{mu}_fsrPhoton_pt"), np_(events, f"{mu}_fsrPhoton_dR")
        out[f"{mu}: no FSR but dressed pT != bare pT"] = int(
            np.sum(~has & ~np.isclose(pt, pt_bare, atol=tol, rtol=1e-5))
        )
        out[f"{mu}: hasFSR != (photon pT stored)"] = int(np.sum(has != (photon_pt > 0)))
        out[f"{mu}: chosen photon dR >= 0.5"] = int(np.sum(has & (photon_dr >= 0.5)))
        out[f"{mu}: photon/muon pT ratio >= 0.4"] = int(np.sum(has & (photon_pt >= 0.4 * pt_bare)))
        out[f"{mu}: dressed pT < bare pT - photon pT"] = int(np.sum(has & (pt < pt_bare - photon_pt - tol)))
    out["mu1 dressed pT < mu2 dressed pT"] = int(
        np.sum(np_(events, "mu1_bsConstrainedPt") < np_(events, "mu2_bsConstrainedPt") - tol)
    )
    out["nFSR != mu1_hasFSR + mu2_hasFSR"] = int(np.sum(ak.to_numpy(events["diMuon_nFSR"]) != nfsr))
    m_fsr, m = np_(events, "diMuon_bsConstrainedMass"), np_(events, "diMuon_bsConstrainedMass_noFSR")
    out["mass < mass_noFSR (photon cannot lower m)"] = int(np.sum(m_fsr < m - tol))
    out["nFSR == 0 but mass != mass_noFSR"] = int(np.sum((nfsr == 0) & ~np.isclose(m_fsr, m, atol=tol)))
    return out


# --------------------------------------------------------------------------------------------------------- #
# Metrics (signed weights throughout; a metric with non-positive total weight is NaN)
# --------------------------------------------------------------------------------------------------------- #
def sigma_eff(values, w) -> float:
    """Half-width of the narrowest interval holding 68.3% of the signed weight (plot_effective_sigma.py)."""
    return effective_sigma(np.asarray(values, float), np.asarray(w, float))[2]


def sigma_eff_binned(values, w, lo, hi, n_bins=4000) -> float:
    """Fast binned sigma_eff for bootstrap replicas (bin width (hi-lo)/n_bins)."""
    sumw, edges = np.histogram(values, bins=n_bins, range=(lo, hi), weights=w)
    total = np.sum(sumw)
    if total <= 0:
        return np.nan
    cdf = np.concatenate([[0.0], np.cumsum(sumw)])  # cdf[k] = weight below edges[k]
    # With negative weights the cumulative sum need not be monotonic; at this bin width the running maximum is an
    # adequate approximation (cross-checked against the exact unbinned value on the nominal sample).
    running_max = np.maximum.accumulate(cdf)
    j = np.searchsorted(running_max, cdf + 0.683 * total, side="left")
    ok = j < len(cdf)
    if not np.any(ok):
        return np.nan
    return 0.5 * float(np.min(edges[j[ok]] - edges[np.arange(len(cdf))[ok]]))


def wfraction(mask, w) -> float:
    total = np.sum(w)
    return float(np.sum(w[mask]) / total) if total > 0 else np.nan


def wmean(values, w) -> float:
    total = np.sum(w)
    return float(np.sum(values * w) / total) if total > 0 else np.nan


def wmedian(values, w) -> float:
    order = np.argsort(values)
    cum = np.cumsum(w[order])
    if cum[-1] <= 0:
        return np.nan
    return float(values[order][np.searchsorted(cum, 0.5 * cum[-1])])


def paired_bootstrap(metric, nominal, fsr, w, n_boot, seed=1234):
    """Bootstrap the improvement 1 - metric(fsr)/metric(nominal) with the SAME Poisson(1) replica weights for both,
    so the strong event-by-event correlation is kept. Returns (std of metric(nominal), std of metric(fsr),
    std of improvement)."""
    if n_boot <= 0 or len(w) == 0:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    a, b, imp = [], [], []
    for _ in range(n_boot):
        rw = w * rng.poisson(1.0, size=len(w))
        ma, mb = metric(nominal, rw), metric(fsr, rw)
        a.append(ma)
        b.append(mb)
        imp.append(1.0 - mb / ma if ma > 0 else np.nan)
    return float(np.nanstd(a)), float(np.nanstd(b)), float(np.nanstd(imp))


def whist(values, w, edges, density=False):
    sumw, _ = np.histogram(values, bins=edges, weights=w)
    sumw2, _ = np.histogram(values, bins=edges, weights=w * w)
    err = np.sqrt(sumw2)
    if density:
        norm = np.sum(sumw) * np.diff(edges)
        norm = np.where(norm != 0, norm, 1.0)
        sumw, err = sumw / norm, err / norm
    return sumw, err


# --------------------------------------------------------------------------------------------------------- #
# Double-sided Crystal Ball fit
# --------------------------------------------------------------------------------------------------------- #
def dscb(x, N, mu, sigma, aL, nL, aR, nR):
    """N x unnormalised DSCB; same shape as python/fits/signal_model.py::_dscb_unnorm (copied, since that
    package uses relative imports and an iminuit API not available in the CMSSW python)."""
    t = (np.asarray(x, dtype=float) - mu) / sigma
    out = np.empty_like(t)
    core = (t >= -aL) & (t <= aR)
    left, right = t < -aL, t > aR
    out[core] = np.exp(-0.5 * t[core] ** 2)
    AL, BL = (nL / aL) ** nL * np.exp(-0.5 * aL**2), nL / aL - aL
    AR, BR = (nR / aR) ** nR * np.exp(-0.5 * aR**2), nR / aR - aR
    out[left] = AL * (BL - t[left]) ** (-nL)
    out[right] = AR * (BR + t[right]) ** (-nR)
    return N * out


def fit_dscb(h, err, edges, fit_range):
    """Binned chi2 DSCB fit of a histogram as drawn (whist output) over the bins with centres in fit_range.

    Returns dict(mu, mu_err, sigma, sigma_err, chi2ndf, params) or None if the fit fails."""
    from scipy.optimize import curve_fit

    centers = 0.5 * (edges[1:] + edges[:-1])
    lo, hi = fit_range
    sel = (centers >= lo) & (centers <= hi) & (err > 0)
    x, y, e = centers[sel], h[sel], err[sel]
    if len(x) < 10 or np.sum(y) <= 0:
        return None
    mu0 = float(x[np.argmax(y)])
    rms0 = float(np.sqrt(np.average((x - np.average(x, weights=y)) ** 2, weights=y)))
    p0 = [float(y.max()), mu0, max(0.7 * rms0, 0.3), 1.5, 3.0, 1.5, 5.0]
    bounds = ([0.0, lo, 0.2, 0.3, 1.01, 0.3, 1.01], [np.inf, hi, 10.0, 10.0, 100.0, 10.0, 100.0])
    try:
        popt, pcov = curve_fit(dscb, x, y, p0=p0, sigma=e, absolute_sigma=True, bounds=bounds, maxfev=20000)
    except (RuntimeError, ValueError):
        return None
    perr = np.sqrt(np.clip(np.diag(pcov), 0, None))
    chi2 = float(np.sum(((y - dscb(x, *popt)) / e) ** 2))
    return dict(mu=float(popt[1]), mu_err=float(perr[1]), sigma=float(popt[2]), sigma_err=float(perr[2]),
                chi2ndf=chi2 / max(len(x) - len(popt), 1), params=popt)


# --------------------------------------------------------------------------------------------------------- #
# Plotting
# --------------------------------------------------------------------------------------------------------- #
NOMINAL_STYLE = dict(color="#3f90da", label="Nominal")
FSR_STYLE = dict(color="#e42536", label="FSR recovered")


def cms_label(ax, era, is_data):
    # mplhep prepends "Simulation" itself when data=False. No luminosity: every comparison here is a shape or a
    # fraction, and the inputs may be a partial dataset.
    hep.cms.label("Preliminary", data=is_data, year=era, com="13.6", fontsize=20, ax=ax)


def overlay(
    series,
    edges,
    xlabel,
    outdir,
    name,
    era,
    title=None,
    density=True,
    is_data=False,
    ratio_label="Ratio",
    logy=False,
    vlines=(),
    fit_range=None,
    sigma_eff_band=False,
):
    """Overlay weighted histograms; the ratio panel divides every series by the first one.

    series: list of (values, weights, style dict, draw_as_points).
    fit_range: if set, fit each series with a DSCB in this window, draw the fit and print its mu and sigma.
    sigma_eff_band: if True, print each series' sigma_eff (unbinned, all values, as in the summary tables) and draw
    vertical lines at the edges of its narrowest 68.3% interval.
    Returns the list of fit results (fit_dscb output, one per series; empty if fit_range is None)."""
    plt.style.use(hep.style.CMS)
    fig, (ax, rax) = get_canvas(draw_ratio=True)
    hists, fits = [], []
    n_text = 0

    def add_text(text, color):
        nonlocal n_text
        ax.text(0.04, 0.89 - 0.05 * n_text, text, transform=ax.transAxes, va="top", fontsize=13, color=color)
        n_text += 1

    for values, w, style, points in series:
        h, e = whist(values, w, edges, density=density)
        hists.append((h, e))
        if points:
            centers = 0.5 * (edges[1:] + edges[:-1])
            ax.errorbar(centers, h, yerr=e, fmt="o", ms=4, **style)
        else:
            hep.histplot(h, edges, yerr=e, ax=ax, histtype="step", linewidth=1.6, flow=None, **style)
        if fit_range is not None:
            fit = fit_dscb(h, e, edges, fit_range)
            fits.append(fit)
            label = style.get("label", "")
            if fit is None:
                text = f"{label}: DCB fit failed"
            else:
                grid = np.linspace(*fit_range, 400)
                ax.plot(grid, dscb(grid, *fit["params"]), color=style["color"], ls="--", lw=1.4)
                text = (rf"{label}: $\mu$ = {fit['mu']:.3f} $\pm$ {fit['mu_err']:.3f} GeV, "
                        rf"$\sigma$ = {fit['sigma']:.3f} $\pm$ {fit['sigma_err']:.3f} GeV")
            add_text(text, style["color"])
        if sigma_eff_band:
            lo, hi, s_eff = effective_sigma(np.asarray(values, float), np.asarray(w, float))[:3]
            if np.isfinite(s_eff):
                ls = ":" if len(hists) == 1 else "--"  # distinguishable when the two bands nearly coincide
                for x in (lo, hi):
                    ax.axvline(x, color=style["color"], ls=ls, lw=1.4, ymax=0.6)  # stop below the text block
                add_text(rf"{style.get('label', '')}: $\sigma_{{eff}}$ = {s_eff:.3f} GeV  [{lo:.2f}, {hi:.2f}]",
                         style["color"])
    if fit_range is not None or sigma_eff_band:  # headroom for the text lines
        top = max(np.nanmax(h + e) for h, e in hists)
        if logy:
            pos = np.concatenate([h[h > 0] for h, _ in hists])
            ax.set_ylim(0.5 * pos.min() if len(pos) else 1e-6, top * (1e3 if sigma_eff_band else 60))
        else:
            ax.set_ylim(0, 1.35 * top)
    ref, ref_err = hists[0]
    for (h, e), (_, _, style, points) in zip(hists[1:], series[1:]):
        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.where(ref != 0, h / ref, np.nan)
            re = np.where(ref != 0, e / np.abs(ref), np.nan)
        centers = 0.5 * (edges[1:] + edges[:-1])
        rax.errorbar(centers, r, yerr=re, fmt="o", ms=3, color=style["color"])
    rax.axhline(1.0, color="gray", lw=1, ls="--")
    rax.set_ylim(0.5, 1.5)
    rax.set_ylabel(ratio_label, fontsize=16)
    rax.set_xlabel(xlabel)
    ax.set_xlim(edges[0], edges[-1])
    rax.set_xlim(edges[0], edges[-1])
    ax.set_ylabel("Normalized to unit area" if density else "Events / bin")
    if logy:
        ax.set_yscale("log")
    for x in vlines:
        ax.axvline(x, color="gray", ls=":", lw=1)
    ax.tick_params(labelbottom=False)
    if title:
        ax.text(0.04, 0.95, title, transform=ax.transAxes, va="top", fontsize=16)
    ax.legend(fontsize=15, loc="upper right")
    cms_label(ax, era, is_data)
    save_figure(fig, outdir, name)
    plt.close(fig)
    return fits


def fraction2d(x, y, w, passed, xbins, ybins, xlabel, ylabel, zlabel, outdir, name, era, min_entries=0):
    """2D map of the weighted percentage of entries with passed=True in each (x, y) bin.

    Bins with no (or non-positive) total weight, or fewer than min_entries unweighted entries, are left empty."""
    plt.style.use(hep.style.CMS)
    fig, ax = get_canvas()
    tot, xe, ye = np.histogram2d(x, y, bins=(xbins, ybins), weights=w)
    num, _, _ = np.histogram2d(x[passed], y[passed], bins=(xbins, ybins), weights=w[passed])
    with np.errstate(divide="ignore", invalid="ignore"):
        pct = np.where(tot > 0, 100.0 * num / tot, np.nan)
    if min_entries > 0:
        n_raw, _, _ = np.histogram2d(x, y, bins=(xbins, ybins))
        pct = np.where(n_raw >= min_entries, pct, np.nan)
    art = hep.hist2dplot(pct, xe, ye, ax=ax, cmap="viridis", cbarextend=False, flow=None)
    if art.cbar is not None:
        art.cbar.set_label(zlabel)
    if min_entries > 0:
        ax.text(0.98, 0.02, f"bins with < {min_entries} entries not shown", transform=ax.transAxes,
                ha="right", va="bottom", fontsize=13, color="black",
                bbox=dict(facecolor="white", alpha=0.8, edgecolor="none"))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    cms_label(ax, era, False)
    save_figure(fig, outdir, name)
    plt.close(fig)
    return pct


def hist2d(x, y, w, xbins, ybins, xlabel, ylabel, outdir, name, era, lines=()):
    plt.style.use(hep.style.CMS)
    fig, ax = get_canvas()
    h, xe, ye = np.histogram2d(x, y, bins=(xbins, ybins), weights=w)
    hep.hist2dplot(h, xe, ye, ax=ax, cmap="viridis", cbarextend=False, flow=None)
    for kind, value in lines:
        (ax.axvline if kind == "x" else ax.axhline)(value, color="white", ls="--", lw=1.2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    cms_label(ax, era, False)
    save_figure(fig, outdir, name)
    plt.close(fig)
