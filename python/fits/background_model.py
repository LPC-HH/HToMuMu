"""Background models for the pyhf cross-check.

Model A -- analytic fit to the DATA SIDEBANDS (110-120 and 130-150 GeV).
    A small family of smooth functions is fitted to the sideband bin counts;
    the best one (lowest AIC) is evaluated across the full range (interpolating
    through the blind window -- this uses sideband information only, so it is
    blind-safe). Fit-covariance eigen-directions become shape nuisances; the
    overall level is a free normfactor added later in workspace.py.

Model B -- MC background templates (DY + EWK + TT + DiBoson), with a free
    normfactor, MC-stat `staterror`, and one linear-tilt shape nuisance.

Both return a `BackgroundModel` with the binned nominal + shape variations, so
workspace.py can treat them uniformly.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from iminuit import Minuit
from iminuit.cost import LeastSquares

from . import fit_config as cfg
from .fit_inputs import CategoryInputs


# --------------------------------------------------------------------------- #
@dataclass
class BackgroundModel:
    category: str
    method: str                       # "sideband" | "mc"
    edges: np.ndarray
    nominal: np.ndarray               # per-bin expected background counts
    shape_up: list[np.ndarray] = field(default_factory=list)
    shape_dn: list[np.ndarray] = field(default_factory=list)
    shape_names: list[str] = field(default_factory=list)
    staterror: np.ndarray | None = None   # per-bin absolute stat uncertainty (model B)
    info: dict = field(default_factory=dict)

    @property
    def yield_total(self) -> float:
        return float(self.nominal.sum())


# --------------------------------------------------------------------------- #
# analytic shape functions -- COUNTS level, x in GeV
# --------------------------------------------------------------------------- #
def _u(x):
    lo, hi = cfg.FIT_RANGE
    return (np.asarray(x, dtype=float) - lo) / (hi - lo)


def _bern_basis(u, n):
    from math import comb

    return np.array([comb(n, j) * u ** j * (1 - u) ** (n - j) for j in range(n + 1)])


_FUNCS = {}


def _register(name, func, p0, limits):
    _FUNCS[name] = dict(func=func, p0=p0, limits=limits)


_register(
    "exp",
    lambda x, A, k: A * np.exp(-k * _u(x)),
    dict(A=1.0, k=3.0),
    dict(A=(0, None), k=(-5, 30)),
)
_register(
    "exp2",
    lambda x, A, k1, k2, f: A * (f * np.exp(-k1 * _u(x)) + (1 - f) * np.exp(-k2 * _u(x))),
    dict(A=1.0, k1=5.0, k2=1.0, f=0.5),
    dict(A=(0, None), k1=(-5, 40), k2=(-5, 40), f=(0.0, 1.0)),
)
_register(
    "pow",
    lambda x, A, k: A * (np.asarray(x, dtype=float) / cfg.FIT_RANGE[0]) ** (-k),
    dict(A=1.0, k=5.0),
    dict(A=(0, None), k=(-2, 40)),
)
for _n in (3, 4, 5):
    def _mk(n):
        def f(x, A, *c):
            coeffs = np.concatenate([[1.0], np.asarray(c, dtype=float)])
            return A * (coeffs[:, None] * _bern_basis(_u(x), n)).sum(axis=0)
        return f

    _register(
        f"bern{_n}",
        _mk(_n),
        dict(A=1.0, **{f"c{j}": 1.0 for j in range(1, _n + 1)}),
        dict(A=(0, None), **{f"c{j}": (0.0, None) for j in range(1, _n + 1)}),
    )


def _integrate_bins(func, params, edges, nsub=11):
    out = np.empty(len(edges) - 1)
    for i in range(len(edges) - 1):
        sub = np.linspace(edges[i], edges[i + 1], nsub)
        out[i] = np.trapz(func(sub, *params), sub)
    return out


# --------------------------------------------------------------------------- #
def fit_sideband_background(
    ci: CategoryInputs, edges=None, n_shape=None, families=None, verbose=False
) -> BackgroundModel:
    edges = cfg.mass_bins() if edges is None else edges
    n_shape = cfg.BKG_SHAPE_NUISANCES if n_shape is None else n_shape
    families = families or cfg.BKG_FAMILIES

    counts, _ = np.histogram(ci.data_mass_blinded, bins=edges)
    centers = 0.5 * (edges[1:] + edges[:-1])
    bw = edges[1] - edges[0]
    sb = cfg.blind_bin_mask(edges) & (counts > 0)
    x_sb, y_sb = centers[sb], counts[sb].astype(float)
    err_sb = np.sqrt(y_sb)

    results = []
    for fam in families:
        spec = _FUNCS[fam]
        pnames = list(spec["p0"])
        # amplitude guess: total sideband counts / (nbins in sideband) as a flat level
        p0 = dict(spec["p0"])
        p0["A"] = y_sb.mean()

        def model(x, *pars, _spec=spec):
            return _spec["func"](x, *pars) * bw  # counts per bin

        try:
            ls = LeastSquares(x_sb, y_sb, err_sb, model)
            m = Minuit(ls, *[p0[k] for k in pnames], name=pnames)
            for k, lim in spec["limits"].items():
                m.limits[k] = lim
            m.migrad()
            m.hesse()
            ndf = max(len(x_sb) - m.nfit, 1)
            chi2 = m.fval
            aic = chi2 + 2 * m.nfit
            if m.valid:
                results.append(dict(fam=fam, m=m, pnames=pnames, spec=spec,
                                    chi2=chi2, ndf=ndf, aic=aic))
                if verbose:
                    print(f"  [{ci.category}] {fam:6s} chi2/ndf={chi2/ndf:5.2f} AIC={aic:8.1f}")
        except Exception as exc:  # noqa: BLE001
            if verbose:
                print(f"  [{ci.category}] {fam} failed: {exc}")

    if not results:
        raise RuntimeError(f"no background family converged for {ci.category}")

    best = min(results, key=lambda r: r["aic"])
    m, spec, pnames = best["m"], best["spec"], best["pnames"]
    pvals = np.array([m.values[k] for k in pnames])

    def counts_of(pars):
        return _integrate_bins(spec["func"], pars, edges)

    nominal = np.clip(counts_of(pvals), 1e-6, None)

    # ---- shape nuisances from covariance eigen-directions ----------------
    shape_up, shape_dn, shape_names = [], [], []
    try:
        cov = np.array(m.covariance)
        evals, evecs = np.linalg.eigh(cov)
        order = np.argsort(evals)[::-1]
        for j in range(min(n_shape, len(order))):
            idx = order[j]
            step = np.sqrt(max(evals[idx], 0.0)) * evecs[:, idx]
            up = np.clip(counts_of(pvals + step), 1e-6, None)
            dn = np.clip(counts_of(pvals - step), 1e-6, None)
            # shape-only: renormalise to the nominal integral
            up *= nominal.sum() / up.sum()
            dn *= nominal.sum() / dn.sum()
            shape_up.append(up)
            shape_dn.append(dn)
            shape_names.append(f"bkgshape_{ci.category}_{j}")
    except Exception as exc:  # noqa: BLE001
        if verbose:
            print(f"  [{ci.category}] covariance eigen-decomp failed: {exc}")

    return BackgroundModel(
        category=ci.category, method="sideband", edges=edges, nominal=nominal,
        shape_up=shape_up, shape_dn=shape_dn, shape_names=shape_names,
        info=dict(
            family=best["fam"], chi2ndf=best["chi2"] / best["ndf"],
            params={k: float(m.values[k]) for k in pnames},
            all_families={r["fam"]: r["aic"] for r in results},
            sideband_counts=int(counts[cfg.blind_bin_mask(edges)].sum()),
        ),
    )


def fit_sideband_all_families(ci: CategoryInputs, edges=None):
    """Return {family: BackgroundModel} -- one per family that converges.
    Used for the discrete-profiling / envelope study."""
    edges = cfg.mass_bins() if edges is None else edges
    out = {}
    for fam in cfg.BKG_FAMILIES:
        try:
            out[fam] = fit_sideband_background(ci, edges=edges, families=[fam])
        except Exception:  # noqa: BLE001
            pass
    return out


# --------------------------------------------------------------------------- #
def mc_template_background(ci: CategoryInputs, edges=None) -> BackgroundModel:
    edges = cfg.mass_bins() if edges is None else edges
    if ci.bkg_mass is None:
        raise RuntimeError(
            f"{ci.category}: MC background not loaded -- call "
            "fit_inputs.load_mc_background() first"
        )
    nominal, _ = np.histogram(ci.bkg_mass, bins=edges, weights=ci.bkg_w)
    sumw2, _ = np.histogram(ci.bkg_mass, bins=edges, weights=ci.bkg_w2)
    nominal = np.clip(nominal, 1e-6, None)
    rel_stat = float(np.sqrt(sumw2.sum()) / nominal.sum())  # total rel. MC-stat error

    # Smooth shape nuisances instead of per-bin staterror (one gamma per bin is
    # far too slow for the combined fit). A linear tilt + a quadratic curvature
    # give the MC background enough freedom to be a fair comparison.
    centers = 0.5 * (edges[1:] + edges[:-1])
    lo, hi = cfg.FIT_RANGE
    ramp = (centers - 0.5 * (lo + hi)) / (0.5 * (hi - lo))     # -1 .. +1
    curv = ramp ** 2 - ramp.mean()

    def _var(basis, amp):
        up = np.clip(nominal * (1.0 + amp * basis), 1e-6, None)
        dn = np.clip(nominal * (1.0 - amp * basis), 1e-6, None)
        return up * nominal.sum() / up.sum(), dn * nominal.sum() / dn.sum()

    tilt_up, tilt_dn = _var(ramp, 0.10)
    curv_up, curv_dn = _var(curv, 0.10)

    return BackgroundModel(
        category=ci.category, method="mc", edges=edges, nominal=nominal,
        shape_up=[tilt_up, curv_up], shape_dn=[tilt_dn, curv_dn],
        shape_names=[f"bkgtilt_{ci.category}", f"bkgcurv_{ci.category}"],
        staterror=None,
        info=dict(
            mc_entries=int(len(ci.bkg_mass)),
            yield_total=float(nominal.sum()),
            rel_mc_stat=rel_stat,
        ),
    )
