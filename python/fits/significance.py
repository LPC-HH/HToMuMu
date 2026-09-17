"""Expected discovery significance from a pyhf model + Asimov data.

The core quantity is the discovery test statistic q0 (Cowan et al.,
arXiv:1007.1727, eq. 12):

    q0 = 0                                    if mu_hat < 0
       = -2 ln [ L(0, theta_hat_hat(0)) / L(mu_hat, theta_hat) ]   otherwise

evaluated on the Asimov dataset built with signal present at mu = 1. In the
asymptotic regime the median expected discovery significance is simply

    Z = sqrt(q0_Asimov),   p0 = 1 - Phi(Z)

This is the direct analogue of `combine -M Significance -t -1 --expectSignal 1`.

We use pyhf's blessed primitive `pyhf.infer.test_statistics.q0` (which handles
the mu_hat < 0 clipping and knows pyhf's objective is -2 lnL) and also report
mu_hat from an unconditional fit as a closure check (should be ~1 on the mu=1
Asimov).
"""

from __future__ import annotations

import math

import numpy as np
from scipy.stats import norm

from . import fit_config as cfg


def _ensure_backend():
    import pyhf

    if pyhf.tensorlib.name != cfg.PYHF_BACKEND[0]:
        pyhf.set_backend(*cfg.PYHF_BACKEND)


def make_asimov(model, mu=1.0):
    """Asimov dataset (expected data incl. auxdata) with the POI set to `mu`
    and all nuisance parameters at their nominal values."""
    pars = np.array(model.config.suggested_init(), dtype=float)
    pars[model.config.poi_index] = mu
    return model.expected_data(pars)


def discovery_significance(model, data=None, mu_asimov=1.0, verbose=False) -> dict:
    """Median expected discovery significance.

    `data` is ignored if given -- the Asimov dataset at mu = `mu_asimov` is
    always what the expected significance is computed on. (The argument is kept
    so callers can pass the workspace data without harm.)
    """
    import pyhf

    _ensure_backend()

    asimov = make_asimov(model, mu=mu_asimov)
    init = model.config.suggested_init()
    bounds = model.config.suggested_bounds()
    fixed = model.config.suggested_fixed()

    q0 = float(pyhf.infer.test_statistics.q0(0.0, asimov, model, init, bounds, fixed))
    Z = math.sqrt(max(q0, 0.0))
    p0 = float(norm.sf(Z))

    best = pyhf.infer.mle.fit(asimov, model)
    mu_hat = float(best[model.config.poi_index])

    result = dict(mu_hat=mu_hat, q0=q0, Z=Z, p0=p0)
    if verbose:
        print(f"  mu_hat={mu_hat:+.3f}  q0={q0:.3f}  Z={Z:.3f}  p0={p0:.2e}")
    return result


def yield_summary(model, data=None, edges=None, window=cfg.YIELD_WINDOW) -> dict:
    """Naive s, b, s/sqrt(b) in a mass window, summed over the model's channels."""
    import pyhf

    _ensure_backend()
    edges = cfg.mass_bins() if edges is None else edges
    centers = 0.5 * (edges[1:] + edges[:-1])
    win = (centers >= window[0]) & (centers <= window[1])

    # per-channel nominal expectation split into (signal, background)
    pars = model.config.suggested_init()
    s_tot = b_tot = 0.0
    # expected data per bin at mu=1 and mu=0
    exp_sb = np.asarray(model.expected_actualdata(pars))
    pars0 = np.array(pars, dtype=float)
    pars0[model.config.poi_index] = 0.0
    exp_b = np.asarray(model.expected_actualdata(pars0))
    exp_s = exp_sb - exp_b

    nbins = len(centers)
    for i, ch in enumerate(model.config.channels):
        sl = slice(i * nbins, (i + 1) * nbins)
        s_tot += float(exp_s[sl][win].sum())
        b_tot += float(exp_b[sl][win].sum())

    return dict(s=s_tot, b=b_tot,
                s_over_sqrtb=s_tot / math.sqrt(b_tot) if b_tot > 0 else float("nan"),
                asimov_Z=_asimov_simple(s_tot, b_tot))


def _asimov_simple(s, b):
    if b <= 0 or s <= 0:
        return float("nan")
    return math.sqrt(2.0 * ((s + b) * math.log(1.0 + s / b) - s))


def significance_table(spec, categories=None, edges=None, verbose=False):
    """Per-category + combined expected significance for one workspace spec.

    Returns a list of dict rows (one per category, plus a 'combined' row).
    """
    from .workspace import build_model_and_data

    categories = categories or [c["name"] for c in spec["channels"]]
    rows = []
    for cat in categories:
        model, data = build_model_and_data(spec, categories=[cat])
        ds = discovery_significance(model, data, verbose=verbose)
        ys = yield_summary(model, data, edges=edges)
        rows.append(dict(category=cat, **ys, **ds))
        if verbose:
            print(f"{cat:10s}  s={ys['s']:8.2f} b={ys['b']:10.1f} "
                  f"s/sqrtb={ys['s_over_sqrtb']:5.2f}  Z={ds['Z']:.3f}")

    model, data = build_model_and_data(spec, categories=categories)
    ds = discovery_significance(model, data, verbose=verbose)
    ys = yield_summary(model, data, edges=edges)
    rows.append(dict(category="combined", **ys, **ds))
    if verbose:
        print(f"{'COMBINED':10s}  s={ys['s']:8.2f} b={ys['b']:10.1f} "
              f"s/sqrtb={ys['s_over_sqrtb']:5.2f}  Z={ds['Z']:.3f}")
    return rows
