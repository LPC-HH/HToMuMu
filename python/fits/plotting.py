"""Plot helpers for the pyhf cross-check notebook / script."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from . import fit_config as cfg
from .fit_inputs import CategoryInputs
from .signal_model import SignalShape
from .background_model import BackgroundModel


def _centers(edges):
    return 0.5 * (edges[1:] + edges[:-1])


def plot_signal_fit(ci: CategoryInputs, sh: SignalShape, edges, ax=None):
    ax = ax or plt.subplots(figsize=(7, 4))[1]
    m = np.concatenate([ci.sig_ggh_mass, ci.sig_vbf_mass])
    w = np.concatenate([ci.sig_ggh_w, ci.sig_vbf_w]) * cfg.BR_HMM
    ax.hist(m, bins=edges, weights=w, histtype="stepfilled", alpha=.35,
            color="crimson", label="signal MC")
    c = _centers(edges)
    ax.plot(c, sh.nominal, color="crimson", lw=2, label=f"{sh.family} fit")
    ax.fill_between(c, sh.reso_dn, sh.reso_up, color="orange", alpha=.3,
                    label="MassReso $\\pm1\\sigma$")
    ax.plot(c, sh.scale_up, "--", color="grey", lw=1)
    ax.plot(c, sh.scale_dn, "--", color="grey", lw=1, label="MassScale $\\pm1\\sigma$")
    ax.axvline(sh.mean, color="k", ls=":", lw=1)
    ax.set_xlabel(r"m$_{\mu\mu}$ [GeV]"); ax.set_ylabel(f"events / {edges[1]-edges[0]:g} GeV")
    ax.set_title(f"{ci.category}: signal model  (mean={sh.mean:.2f}, "
                 f"$\\sigma_{{eff}}$={sh.sigma_eff:.2f} GeV)")
    ax.legend(fontsize=8)
    return ax


def plot_background_fit(ci: CategoryInputs, bm: BackgroundModel, edges, ax=None):
    ax = ax or plt.subplots(figsize=(7, 4))[1]
    counts, _ = np.histogram(ci.data_mass_blinded, bins=edges)
    c = _centers(edges)
    sb = cfg.blind_bin_mask(edges)
    ax.errorbar(c[sb], counts[sb], yerr=np.sqrt(counts[sb]), fmt="o", ms=3,
                color="k", label="data (sidebands, fitted)")
    ax.errorbar(c[~sb], counts[~sb], yerr=np.sqrt(np.maximum(counts[~sb], 0)),
                fmt="o", ms=3, mfc="none", color="grey", label="data (blind, not used)")
    ax.plot(c, bm.nominal, color="crimson", lw=2,
            label=f"{bm.info.get('family', bm.method)} fit")
    for up, dn in zip(bm.shape_up, bm.shape_dn):
        ax.fill_between(c, dn, up, color="crimson", alpha=.12)
    ax.axvspan(*cfg.BLIND_WINDOW, color="grey", alpha=.12)
    ax.set_xlabel(r"m$_{\mu\mu}$ [GeV]"); ax.set_ylabel(f"events / {edges[1]-edges[0]:g} GeV")
    ax.set_title(f"{ci.category}: background model '{bm.method}'")
    ax.legend(fontsize=8)
    return ax


def plot_asimov(model, category_index, edges, ax=None):
    """Pre/post-fit background + signal + Asimov for one channel of a model."""
    import pyhf

    ax = ax or plt.subplots(figsize=(7, 4))[1]
    nb = len(edges) - 1
    sl = slice(category_index * nb, (category_index + 1) * nb)
    c = _centers(edges)

    pars1 = np.array(model.config.suggested_init(), dtype=float)
    pars1[model.config.poi_index] = 1.0
    pars0 = pars1.copy(); pars0[model.config.poi_index] = 0.0
    sb = np.asarray(model.expected_actualdata(pars1))[sl]
    b = np.asarray(model.expected_actualdata(pars0))[sl]

    ax.step(edges[:-1], b, where="post", color="royalblue", label="background (pre-fit)")
    ax.fill_between(c, b, sb, step="pre", color="crimson", alpha=.4, label="signal ($\\mu$=1)")
    ax.plot(c, sb, "k.", ms=4, label="Asimov data")
    ax.axvspan(*cfg.BLIND_WINDOW, color="grey", alpha=.12)
    ax.set_xlabel(r"m$_{\mu\mu}$ [GeV]"); ax.set_ylabel("events")
    ax.legend(fontsize=8)
    return ax


def plot_significance_bars(rows_a, rows_b=None, label_a="sideband fit",
                           label_b="MC template", ax=None):
    ax = ax or plt.subplots(figsize=(9, 4))[1]
    cats = [r["category"] for r in rows_a if r["category"] != "combined"]
    x = np.arange(len(cats))
    za = [r["Z"] for r in rows_a if r["category"] != "combined"]
    w = 0.38 if rows_b else 0.6
    ax.bar(x - (w / 2 if rows_b else 0), za, w, label=label_a, color="crimson")
    if rows_b:
        zb = [r["Z"] for r in rows_b if r["category"] != "combined"]
        ax.bar(x + w / 2, zb, w, label=label_b, color="royalblue")
    ax.set_xticks(x); ax.set_xticklabels(cats, rotation=45, ha="right")
    ax.set_ylabel("expected $Z$ [$\\sigma$]")
    ax.set_title("Per-category expected discovery significance")
    ax.legend()
    return ax
