"""Parametric signal model for the H->mumu peak.

For each category we fit a double-sided Crystal Ball (DSCB) to the *weighted*
ggH+VBF signal MC (falling back to a sum of two Gaussians if the DSCB fit is
unstable). The fitted shape is then sampled into the analysis bins and scaled to
the physical mu = 1 yield (sum(weight) * BR_HMM), giving:

    nominal          -- binned signal template
    mass-scale hi/lo  -- peak mean shifted by +/- MASS_SCALE_REL
    mass-reso  hi/lo  -- width scaled by 1 +/- MASS_RESO_REL

All three are returned as absolute per-bin yields (what pyhf `histosys` wants).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from iminuit import Minuit
from iminuit.cost import LeastSquares

from . import fit_config as cfg
from .fit_inputs import CategoryInputs


# --------------------------------------------------------------------------- #
# shape functions (return an UN-normalised density; normalisation done numerically)
# --------------------------------------------------------------------------- #
def _dscb_unnorm(x, mu, sigma, aL, nL, aR, nR):
    t = (x - mu) / sigma
    out = np.empty_like(t, dtype=float)
    core = (t >= -aL) & (t <= aR)
    left = t < -aL
    right = t > aR
    out[core] = np.exp(-0.5 * t[core] ** 2)
    AL = (nL / aL) ** nL * np.exp(-0.5 * aL ** 2)
    BL = nL / aL - aL
    out[left] = AL * (BL - t[left]) ** (-nL)
    AR = (nR / aR) ** nR * np.exp(-0.5 * aR ** 2)
    BR = nR / aR - aR
    out[right] = AR * (BR + t[right]) ** (-nR)
    return out


def _twogauss_unnorm(x, mu, s1, s2, frac):
    g1 = np.exp(-0.5 * ((x - mu) / s1) ** 2) / s1
    g2 = np.exp(-0.5 * ((x - mu) / s2) ** 2) / s2
    return frac * g1 + (1.0 - frac) * g2


_FINE = None


def _fine_grid():
    global _FINE
    if _FINE is None:
        lo, hi = cfg.FIT_RANGE
        _FINE = np.linspace(lo, hi, int((hi - lo) / 0.02) + 1)
    return _FINE


def _normalised(func, params):
    """Return a callable pdf(x) normalised to unit integral over the fit range."""
    grid = _fine_grid()
    dens = func(grid, *params)
    area = np.trapz(dens, grid)
    return lambda x: func(np.asarray(x, dtype=float), *params) / area


def _binned_template(pdf, edges, yield_):
    """Integrate a normalised pdf over each analysis bin (fine sub-sampling),
    scale to `yield_`."""
    out = np.empty(len(edges) - 1)
    for i in range(len(edges) - 1):
        sub = np.linspace(edges[i], edges[i + 1], 9)
        out[i] = np.trapz(pdf(sub), sub)
    out = np.clip(out, 0.0, None)
    s = out.sum()
    return out * (yield_ / s) if s > 0 else out


# --------------------------------------------------------------------------- #
@dataclass
class SignalShape:
    category: str
    family: str            # "dscb" or "twogauss"
    params: dict
    mean: float
    sigma_eff: float        # effective sigma (68% shortest interval)
    yield_ggh: float
    yield_vbf: float
    nominal: np.ndarray
    scale_up: np.ndarray
    scale_dn: np.ndarray
    reso_up: np.ndarray
    reso_dn: np.ndarray
    chi2ndf: float

    @property
    def yield_total(self) -> float:
        return self.yield_ggh + self.yield_vbf


def _effective_sigma(pdf, mean):
    grid = _fine_grid()
    d = pdf(grid)
    d = d / np.trapz(d, grid)
    order = np.argsort(np.abs(grid - mean))
    # widen a symmetric-ish interval until it holds 68.27%
    cdf_grid = np.concatenate([[0.0], np.cumsum(0.5 * (d[1:] + d[:-1]) * np.diff(grid))])
    from numpy import interp

    lo = interp(0.5 - 0.6827 / 2, cdf_grid, grid)
    hi = interp(0.5 + 0.6827 / 2, cdf_grid, grid)
    return 0.5 * (hi - lo)


# --------------------------------------------------------------------------- #
def fit_signal(ci: CategoryInputs, edges=None, verbose=False) -> SignalShape:
    edges = cfg.mass_bins() if edges is None else edges

    mass = np.concatenate([ci.sig_ggh_mass, ci.sig_vbf_mass])
    w = np.concatenate([ci.sig_ggh_w, ci.sig_vbf_w])
    y_ggh = float(ci.sig_ggh_w.sum() * cfg.BR_HMM)
    y_vbf = float(ci.sig_vbf_w.sum() * cfg.BR_HMM)

    # fine histogram for the shape fit
    lo, hi = cfg.FIT_RANGE
    fedges = np.linspace(lo, hi, int((hi - lo) / 0.25) + 1)
    n, _ = np.histogram(mass, bins=fedges, weights=w)
    n2, _ = np.histogram(mass, bins=fedges, weights=w ** 2)
    centers = 0.5 * (fedges[1:] + fedges[:-1])
    bw = fedges[1] - fedges[0]
    err = np.sqrt(np.maximum(n2, (0.05 * n.max()) ** 2))

    mean0 = float(np.average(mass, weights=w))
    rms0 = float(np.sqrt(np.average((mass - mean0) ** 2, weights=w)))
    norm0 = n.sum() * bw

    family, params, chi2ndf = "dscb", None, np.inf

    # ---- try DSCB -----------------------------------------------------------
    def dscb_model(x, N, mu, sigma, aL, nL, aR, nR):
        pdf = _normalised(_dscb_unnorm, (mu, sigma, aL, nL, aR, nR))
        return N * pdf(x)

    try:
        ls = LeastSquares(centers, n, err, dscb_model)
        m = Minuit(ls, N=norm0, mu=mean0, sigma=0.7 * rms0,
                   aL=1.4, nL=3.0, aR=1.6, nR=4.0)
        m.limits["sigma"] = (0.2, 5.0)
        m.limits["aL"] = (0.3, 5.0)
        m.limits["aR"] = (0.3, 5.0)
        m.limits["nL"] = (1.01, 40.0)
        m.limits["nR"] = (1.01, 40.0)
        m.limits["mu"] = (mean0 - 3, mean0 + 3)
        m.migrad()
        if m.valid:
            params = dict(mu=m.values["mu"], sigma=m.values["sigma"],
                          aL=m.values["aL"], nL=m.values["nL"],
                          aR=m.values["aR"], nR=m.values["nR"])
            chi2ndf = m.fval / max(len(centers) - m.nfit, 1)
    except Exception as exc:  # noqa: BLE001
        if verbose:
            print(f"  [{ci.category}] DSCB failed: {exc}")

    # ---- fall back to sum of two Gaussians --------------------------------
    if params is None or chi2ndf > 8.0:
        def tg_model(x, N, mu, s1, s2, frac):
            pdf = _normalised(_twogauss_unnorm, (mu, s1, s2, frac))
            return N * pdf(x)

        ls = LeastSquares(centers, n, err, tg_model)
        m = Minuit(ls, N=norm0, mu=mean0, s1=0.6 * rms0, s2=1.6 * rms0, frac=0.7)
        m.limits["s1"] = (0.2, 4.0)
        m.limits["s2"] = (0.4, 8.0)
        m.limits["frac"] = (0.0, 1.0)
        m.limits["mu"] = (mean0 - 3, mean0 + 3)
        m.migrad()
        family = "twogauss"
        params = dict(mu=m.values["mu"], s1=m.values["s1"],
                      s2=m.values["s2"], frac=m.values["frac"])
        chi2ndf = m.fval / max(len(centers) - m.nfit, 1)

    # ---- build templates -------------------------------------------------
    def make_pdf(p):
        if family == "dscb":
            return _normalised(_dscb_unnorm,
                               (p["mu"], p["sigma"], p["aL"], p["nL"], p["aR"], p["nR"]))
        return _normalised(_twogauss_unnorm, (p["mu"], p["s1"], p["s2"], p["frac"]))

    def scaled(p, dmu=0.0, fsig=1.0):
        q = dict(p)
        q["mu"] = p["mu"] * (1.0 + dmu)
        if family == "dscb":
            q["sigma"] = p["sigma"] * fsig
        else:
            q["s1"] = p["s1"] * fsig
            q["s2"] = p["s2"] * fsig
        return q

    ytot = y_ggh + y_vbf
    nominal_pdf = make_pdf(params)
    nominal = _binned_template(nominal_pdf, edges, ytot)
    scale_up = _binned_template(make_pdf(scaled(params, dmu=+cfg.MASS_SCALE_REL)), edges, ytot)
    scale_dn = _binned_template(make_pdf(scaled(params, dmu=-cfg.MASS_SCALE_REL)), edges, ytot)
    reso_up = _binned_template(make_pdf(scaled(params, fsig=1.0 + cfg.MASS_RESO_REL)), edges, ytot)
    reso_dn = _binned_template(make_pdf(scaled(params, fsig=1.0 - cfg.MASS_RESO_REL)), edges, ytot)

    return SignalShape(
        category=ci.category, family=family, params=params,
        mean=float(params["mu"]),
        sigma_eff=float(_effective_sigma(nominal_pdf, params["mu"])),
        yield_ggh=y_ggh, yield_vbf=y_vbf,
        nominal=nominal, scale_up=scale_up, scale_dn=scale_dn,
        reso_up=reso_up, reso_dn=reso_dn, chi2ndf=float(chi2ndf),
    )


def fit_all_signals(inputs: dict[str, CategoryInputs], edges=None, verbose=False):
    return {c: fit_signal(ci, edges=edges, verbose=verbose) for c, ci in inputs.items()}
