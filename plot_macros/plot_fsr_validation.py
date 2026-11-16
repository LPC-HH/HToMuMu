"""Checks
  1. invariants  : implementation consistency (counts of violations; all 0 expected)
  2. signal      : ggH/VBF dimuon mass resolution, nominal vs FSR, on identical events (truth: gen_mll, the
                   hard-process pre-FSR dimuon mass, ~ m_H)
  3. dy          : Z radiative tail and overcorrection on DY MC (truth: gen_mll, removes the Z lineshape)
  4. dressed     : reco muons vs matched GenDressedLepton (dressing cone 0.1 vs reco FSR cone 0.5!)
  5. photons     : chosen-photon properties; DY MC vs data in the Z control region (data blinded to m < 110 GeV
                   for both the nominal and FSR mass, enforced in utils.fsr_validation.load)

Usage (from any directory):
  python3 plot_fsr_validation.py --era 2024                      # all hadded tuples present for the era
  python3 plot_fsr_validation.py --era 2024 --samples ggH VBF    # signal-only first look
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

import awkward as ak
import numpy as np

from utils import fsr_validation as fv

SCRIPT_DIR = Path(__file__).resolve().parent
TUPLE_DIR = SCRIPT_DIR / "../root_io/tuples"  # hadded CreateTuple outputs
TUPLE_NAME = "{sample}_{era}_tuples.root"  # as written by root_io/tuples/hadd_tuples*.sh
PLOT_DIR = SCRIPT_DIR / "../plots/fsr_validation"  # outputs go to PLOT_DIR/<era>/
SAMPLES = ("ggH", "VBF", "DY", "Data")

SIGNAL_RANGE = (100.0, 150.0)
SIGNAL_BIN_WIDTH = 0.5  # GeV
SIGNAL_FIT_RANGE = (115.0, 135.0)  # DSCB fit window drawn on the mass_* plots
FSR_FRACTION_MIN_MUONS = 100  # muon pT-eta FSR-fraction map: blank bins with fewer muons (unweighted)
SIGNAL_BOOT_RANGE = (100.0, 150.0)
DY_RANGE = (60.0, 120.0)
DY_TRUTH_Z = (81.0, 101.0)  # Born-level on-shell Z for the DY resolution / tail metrics
DY_TAIL = (60.0, 80.0)
DY_PEAK = (86.0, 96.0)
DATA_MC_RANGE = (60.0, fv.DATA_MAX_MASS)

M_NOM = "diMuon_bsConstrainedMass"
M_FSR = "diMuon_bsConstrainedMass_FSR"


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--samples", nargs="+", choices=SAMPLES, default=list(SAMPLES),
                   help="samples to run on (default: all)")
    p.add_argument("--ggh", nargs="*", help="ggH signal ctuple(s) (globs); default: TUPLE_DIR/ggH_<era>_tuples.root")
    p.add_argument("--vbf", nargs="*", help="VBF signal ctuple(s) (globs)")
    p.add_argument("--dy", nargs="*", help="DY MC ctuple(s) (globs); use the stitched set for a Z-region shape")
    p.add_argument("--data", nargs="*", help="Data ctuple(s) (globs); blinded to m < 110 GeV on load")
    p.add_argument("--era", default="2024")
    p.add_argument("--outdir", default=None, help="default: PLOT_DIR/<era>/ (plots/fsr_validation/<era>/)")
    p.add_argument("--max-events", type=int, default=None, help="per sample")
    p.add_argument("--n-bootstrap", type=int, default=100)
    p.add_argument("--match-dr", type=float, default=0.1, help="reco-GenDressedLepton DeltaR")
    return p.parse_args()


def splits(ev):
    n1 = fv.np_(ev, "diMuon_nFSR")
    return {"all": np.ones(len(n1), bool), "withFSR": n1 > 0, "noFSR": n1 == 0}


# --------------------------------------------------------------------------------------------------------- #
# 2. Signal mass resolution
# --------------------------------------------------------------------------------------------------------- #
def resolution_row(sample, split, m, m_fsr, gen, w, n_boot):
    in_tuple = np.isfinite(m) & np.isfinite(m_fsr)
    m, m_fsr, w = m[in_tuple], m_fsr[in_tuple], w[in_tuple]
    gen = gen[in_tuple] if gen is not None else None
    row = {"sample": sample, "split": split, "n_events": int(len(w)), "sum_w": float(np.sum(w))}
    if len(w) == 0 or np.sum(w) <= 0:
        return row
    s_nom, s_fsr = fv.sigma_eff(m, w), fv.sigma_eff(m_fsr, w)
    row.update(
        sigma_eff_nominal=s_nom,
        sigma_eff_fsr=s_fsr,
        improvement=1.0 - s_fsr / s_nom,
        mean_shift=fv.wmean(m_fsr - m, w),
        median_nominal=fv.wmedian(m, w),
        median_fsr=fv.wmedian(m_fsr, w),
        frac_below_120_nominal=fv.wfraction(m < 120, w),
        frac_below_120_fsr=fv.wfraction(m_fsr < 120, w),
        frac_above_130_nominal=fv.wfraction(m > 130, w),
        frac_above_130_fsr=fv.wfraction(m_fsr > 130, w),
    )
    lo, hi = SIGNAL_BOOT_RANGE
    e_nom, e_fsr, e_imp = fv.paired_bootstrap(
        lambda x, rw: fv.sigma_eff_binned(x, rw, lo, hi), m, m_fsr, w, n_boot
    )
    row.update(sigma_eff_nominal_err=e_nom, sigma_eff_fsr_err=e_fsr, improvement_err=e_imp)
    if gen is not None:
        ok = gen > 0
        if np.any(ok):
            r_nom, r_fsr = m[ok] / gen[ok], m_fsr[ok] / gen[ok]
            row.update(
                response_median_nominal=fv.wmedian(r_nom, w[ok]),
                response_median_fsr=fv.wmedian(r_fsr, w[ok]),
                response_sigma_eff_nominal=fv.sigma_eff(r_nom, w[ok]),
                response_sigma_eff_fsr=fv.sigma_eff(r_fsr, w[ok]),
            )
    return row


def signal_study(name, ev, era, outdir, n_boot):
    out = os.path.join(outdir, "signal_resolution", name) + "/"
    m, m_fsr, w = fv.np_(ev, M_NOM), fv.np_(ev, M_FSR), fv.weights(ev)
    gen = fv.np_(ev, "gen_mll")
    gen = np.where(gen > 0, gen, np.nan)
    rows = []
    masks = splits(ev)
    masks["ggH_category"] = fv.np_(ev, "is_ggH_category") > 0
    masks["VBF_category"] = fv.np_(ev, "is_VBF_category") > 0
    for split, mask in masks.items():
        rows.append(resolution_row(name, split, m[mask], m_fsr[mask], gen[mask], w[mask], n_boot))
        if split not in ("all", "withFSR", "noFSR") or not np.any(mask):
            continue
        edges = np.linspace(*SIGNAL_RANGE, int(round((SIGNAL_RANGE[1] - SIGNAL_RANGE[0]) / SIGNAL_BIN_WIDTH)) + 1)
        mass_series = [(m[mask], w[mask], fv.NOMINAL_STYLE, False), (m_fsr[mask], w[mask], fv.FSR_STYLE, False)]
        fits = fv.overlay(
            mass_series, edges, r"$m_{\mu\mu}$ [GeV]", out, f"mass_{split}", era, title=f"{name}, {split}",
            ratio_label="FSR / nom.", fit_range=SIGNAL_FIT_RANGE,
        )
        if split == "all":  # log-scale copy so the low/high-mass tails are visible next to the peak
            fv.overlay(
                mass_series, edges, r"$m_{\mu\mu}$ [GeV]", out, f"mass_{split}_log", era, title=f"{name}, {split}",
                ratio_label="FSR / nom.", fit_range=SIGNAL_FIT_RANGE, logy=True, sigma_eff_band=True,
            )
        for tag, fit in zip(("nominal", "fsr"), fits):
            if fit is not None:
                rows[-1].update({f"dcb_{k}_{tag}": fit[k] for k in ("mu", "mu_err", "sigma", "sigma_err", "chi2ndf")})
        ok = mask & np.isfinite(gen)
        fv.overlay(
            [(m[ok] / gen[ok], w[ok], fv.NOMINAL_STYLE, False), (m_fsr[ok] / gen[ok], w[ok], fv.FSR_STYLE, False)],
            np.linspace(0.92, 1.04, 61), r"$m_{\mu\mu}^{reco} / m_{\mu\mu}^{gen,\ hard\ process}$", out,
            f"mass_response_{split}", era, title=f"{name}, {split}", ratio_label="FSR / nom.",
        )
    has = masks["withFSR"]
    if np.any(has):
        dm = m_fsr - m
        shift_max = 5.0 * np.ceil(np.nanmax(dm[has]) / 5.0)  # full range, rounded up to the next 5 GeV
        fv.overlay(
            [(dm[has], w[has], fv.FSR_STYLE, False)], np.arange(0, shift_max + 0.25, 0.5), r"$m^{FSR} - m$ [GeV]", out,
            "mass_shift", era, title=f"{name}, with FSR", logy=True,
        )
        for mu in ("mu1", "mu2"):
            sel = fv.np_(ev, f"{mu}_hasFSR") > 0
            fv.hist2d(
                fv.np_(ev, f"{mu}_fsrPhoton_pt")[sel], dm[sel], w[sel], np.linspace(2, 40, 39),
                np.linspace(0, 20, 41), rf"$p_T^\gamma$ ({mu}) [GeV]", r"$m^{FSR} - m$ [GeV]", out,
                f"mass_shift_vs_photon_pt_{mu}", era,
            )
            ok = sel & np.isfinite(gen)
            fv.hist2d(
                fv.np_(ev, f"{mu}_fsrPhoton_dR")[ok], (m_fsr[ok] - gen[ok]), w[ok], np.linspace(0, 0.5, 26),
                np.linspace(-8, 8, 41), rf"$\Delta R(\mu,\gamma)$ ({mu})", r"$m^{FSR} - m^{gen}$ [GeV]", out,
                f"fsr_mass_residual_vs_photon_dR_{mu}", era, lines=[("x", fv.DRESSING_CONE)],
            )
            # FSR photon attached to the leading (mu1) vs subleading (mu2) muon; mu1 is pT-ordered leading.
            # Events with a photon on both muons (~0.01%) appear in both plots.
            tag = {"mu1": "lead", "mu2": "sublead"}[mu]
            fv.overlay(
                [(m[ok] / gen[ok], w[ok], fv.NOMINAL_STYLE, False),
                 (m_fsr[ok] / gen[ok], w[ok], fv.FSR_STYLE, False)],
                np.linspace(0.92, 1.04, 61), r"$m_{\mu\mu}^{reco} / m_{\mu\mu}^{gen,\ hard\ process}$", out,
                f"mass_response_withFSR_{tag}", era, title=f"{name}, FSR on {tag}ing muon", ratio_label="FSR / nom.",
            )
            # same split for the dimuon mass itself (same binning and DSCB fit as mass_withFSR)
            fv.overlay(
                [(m[sel], w[sel], fv.NOMINAL_STYLE, False), (m_fsr[sel], w[sel], fv.FSR_STYLE, False)],
                np.linspace(*SIGNAL_RANGE, int(round((SIGNAL_RANGE[1] - SIGNAL_RANGE[0]) / SIGNAL_BIN_WIDTH)) + 1),
                r"$m_{\mu\mu}$ [GeV]", out, f"mass_withFSR_{tag}", era, title=f"{name}, FSR on {tag}ing muon",
                ratio_label="FSR / nom.", fit_range=SIGNAL_FIT_RANGE,
            )
        # FSR-recovered mass response vs photon / muon kinematics, one entry per muon with an FSR photon
        # (mu1 and mu2 pooled; muon pT is the nominal, pre-recovery bsConstrainedPt)
        pool = {k: [] for k in ("resp", "ratio", "gpt", "mupt", "w")}
        for mu in ("mu1", "mu2"):
            sel = (fv.np_(ev, f"{mu}_hasFSR") > 0) & np.isfinite(gen)
            gpt, mupt = fv.np_(ev, f"{mu}_fsrPhoton_pt")[sel], fv.np_(ev, f"{mu}_bsConstrainedPt")[sel]
            pool["resp"].append(m_fsr[sel] / gen[sel])
            pool["ratio"].append(gpt / mupt)
            pool["gpt"].append(gpt)
            pool["mupt"].append(mupt)
            pool["w"].append(w[sel])
        pool = {k: np.concatenate(v) for k, v in pool.items()}
        resp_bins, resp_label = np.linspace(0.85, 1.15, 61), r"$m_{\mu\mu}^{FSR} / m_{\mu\mu}^{gen,\ hard\ process}$"
        for key, xbins, xlabel, tag in (
            ("ratio", np.linspace(0, 0.4, 41), r"$p_T^\gamma / p_T^\mu$", "ptRatio"),
            ("gpt", np.linspace(2, 40, 39), r"$p_T^\gamma$ [GeV]", "photon_pt"),
            ("mupt", np.linspace(20, 200, 37), r"$p_T^\mu$ [GeV]", "muon_pt"),
        ):
            fv.hist2d(pool[key], pool["resp"], pool["w"], xbins, resp_bins, xlabel, resp_label, out,
                      f"fsr_mass_response_vs_{tag}", era, lines=[("y", 1.0)])
    # percentage of muons with an FSR photon, vs muon pT and eta (all muons, mu1 and mu2 pooled; nominal pT)
    mu_pt = np.concatenate([fv.np_(ev, f"{mu}_bsConstrainedPt") for mu in ("mu1", "mu2")])
    mu_eta = np.concatenate([fv.np_(ev, f"{mu}_eta") for mu in ("mu1", "mu2")])
    mu_has = np.concatenate([fv.np_(ev, f"{mu}_hasFSR") > 0 for mu in ("mu1", "mu2")])
    fv.fraction2d(
        mu_pt, mu_eta, np.concatenate([w, w]), mu_has,
        np.array([20, 30, 40, 50, 60, 70, 80, 100, 120, 150, 200, 250, 300, 400]), np.linspace(-2.4, 2.4, 25),
        r"$p_T^\mu$ [GeV]", r"$\eta^\mu$", "muons with FSR recovery [%]", out, "fsr_fraction_vs_muon_pt_eta", era,
        min_entries=FSR_FRACTION_MIN_MUONS,
    )
    return rows


# --------------------------------------------------------------------------------------------------------- #
# 3. DY Z radiative tail
# --------------------------------------------------------------------------------------------------------- #
def dy_study(ev, era, outdir, n_boot):
    out = os.path.join(outdir, "DY_Z_validation") + "/"
    m, m_fsr, w = fv.np_(ev, M_NOM), fv.np_(ev, M_FSR), fv.weights(ev)
    gen = fv.np_(ev, "gen_mll")
    rows = []
    for split, mask in splits(ev).items():
        # identical events, plotted in the broad Z window (no narrow cut that would remove the tail)
        edges = np.linspace(*DY_RANGE, 61)
        fv.overlay(
            [(m[mask], w[mask], fv.NOMINAL_STYLE, False), (m_fsr[mask], w[mask], fv.FSR_STYLE, False)],
            edges, r"$m_{\mu\mu}$ [GeV]", out, f"Z_mass_{split}", era, title=f"DY, {split}", density=False,
            ratio_label="FSR / nom.", logy=True, vlines=(DY_TAIL[1], DY_PEAK[0], DY_PEAK[1]),
        )
        # truth-defined set: Born-level on-shell Z, so migrations in the reco mass do not change the denominator
        z = mask & (gen > DY_TRUTH_Z[0]) & (gen < DY_TRUTH_Z[1])
        row = {"sample": "DY", "split": split, "n_events": int(np.sum(z)), "sum_w": float(np.sum(w[z]))}
        if np.sum(w[z]) > 0:
            for tag, x in (("nominal", m[z]), ("fsr", m_fsr[z])):
                row[f"frac_tail_{tag}"] = fv.wfraction((x > DY_TAIL[0]) & (x < DY_TAIL[1]), w[z])
                row[f"frac_peak_{tag}"] = fv.wfraction((x > DY_PEAK[0]) & (x < DY_PEAK[1]), w[z])
                row[f"frac_above_peak_{tag}"] = fv.wfraction(x > DY_PEAK[1], w[z])
            r_nom, r_fsr = m[z] / gen[z], m_fsr[z] / gen[z]
            row.update(
                response_median_nominal=fv.wmedian(r_nom, w[z]),
                response_median_fsr=fv.wmedian(r_fsr, w[z]),
                response_sigma_eff_nominal=fv.sigma_eff(r_nom, w[z]),
                response_sigma_eff_fsr=fv.sigma_eff(r_fsr, w[z]),
                mean_shift=fv.wmean(m_fsr[z] - m[z], w[z]),
            )
            row["improvement"] = 1.0 - row["response_sigma_eff_fsr"] / row["response_sigma_eff_nominal"]
            _, _, row["improvement_err"] = fv.paired_bootstrap(
                lambda x, rw: fv.sigma_eff_binned(x, rw, 0.5, 1.5), r_nom, r_fsr, w[z], n_boot
            )
            fv.overlay(
                [(r_nom, w[z], fv.NOMINAL_STYLE, False), (r_fsr, w[z], fv.FSR_STYLE, False)],
                np.linspace(0.85, 1.06, 64), r"$m_{\mu\mu}^{reco} / m_{\mu\mu}^{gen,\ hard\ process}$", out,
                f"Z_mass_response_{split}", era, title=f"DY, gen {DY_TRUTH_Z[0]:.0f}-{DY_TRUTH_Z[1]:.0f} GeV, {split}",
                ratio_label="FSR / nom.", logy=True,
            )
        rows.append(row)
    for mu in ("mu1", "mu2"):  # FSR on the leading vs subleading muon
        mask = fv.np_(ev, f"{mu}_hasFSR") > 0
        if np.any(mask):
            fv.overlay(
                [(m[mask], w[mask], fv.NOMINAL_STYLE, False), (m_fsr[mask], w[mask], fv.FSR_STYLE, False)],
                np.linspace(*DY_RANGE, 61), r"$m_{\mu\mu}$ [GeV]", out, f"Z_mass_{mu}_hasFSR", era,
                title=f"DY, FSR on {mu}", density=False, ratio_label="FSR / nom.", logy=True,
            )
    return rows


# --------------------------------------------------------------------------------------------------------- #
# 4. GenDressedLepton comparison
# --------------------------------------------------------------------------------------------------------- #
def dressed_study(name, ev, era, outdir, match_dr):
    out = os.path.join(outdir, "gen_dressed_comparison", name) + "/"
    match = fv.match_dressed(ev, max_dr=match_dr)
    w = fv.weights(ev)
    both = np.isfinite(match["mu1"]["pt"]) & np.isfinite(match["mu2"]["pt"])
    rows = [{"sample": name, "quantity": "matching efficiency (both muons)", "value": fv.wfraction(both, w)}]
    # per-muon response, pooled over mu1 and mu2
    pooled = {k: [] for k in ("nom", "fsr", "deta_nom", "deta_fsr", "dphi_nom", "dphi_fsr", "w", "dr", "has")}
    for mu in ("mu1", "mu2"):
        ok = np.isfinite(match[mu]["pt"])
        g = {v: match[mu][v][ok] for v in ("pt", "eta", "phi")}
        pooled["nom"].append(fv.np_(ev, f"{mu}_bsConstrainedPt")[ok] / g["pt"])
        pooled["fsr"].append(fv.np_(ev, f"{mu}_bsConstrainedPt_FSR")[ok] / g["pt"])
        pooled["deta_nom"].append(fv.np_(ev, f"{mu}_eta")[ok] - g["eta"])
        pooled["deta_fsr"].append(fv.np_(ev, f"{mu}_eta_FSR")[ok] - g["eta"])
        pooled["dphi_nom"].append(fv._delta_phi(fv.np_(ev, f"{mu}_phi")[ok], g["phi"]))
        pooled["dphi_fsr"].append(fv._delta_phi(fv.np_(ev, f"{mu}_phi_FSR")[ok], g["phi"]))
        pooled["w"].append(w[ok])
        pooled["dr"].append(fv.np_(ev, f"{mu}_fsrPhoton_dR")[ok])
        pooled["has"].append(fv.np_(ev, f"{mu}_hasFSR")[ok] > 0)
    p = {k: np.concatenate(v) for k, v in pooled.items()}
    subsets = {
        "all": np.ones(len(p["w"]), bool),
        "withFSR": p["has"],
        f"withFSR_dR<{fv.DRESSING_CONE}": p["has"] & (p["dr"] < fv.DRESSING_CONE),
        f"withFSR_dR>={fv.DRESSING_CONE}": p["has"] & (p["dr"] >= fv.DRESSING_CONE),
    }
    for split, s in subsets.items():
        if not np.any(s):
            continue
        tag = split.replace("<", "lt").replace(">=", "ge")
        fv.overlay(
            [(p["nom"][s], p["w"][s], fv.NOMINAL_STYLE, False), (p["fsr"][s], p["w"][s], fv.FSR_STYLE, False)],
            np.linspace(0.85, 1.15, 61), r"$p_T^{reco} / p_T^{gen\ dressed}$", out, f"pt_response_{tag}", era,
            title=f"{name}, matched muons, {split}", ratio_label="FSR / nom.", logy=True, vlines=(1.0,),
        )
        for var, lab, rng in (("deta", r"$\eta^{reco}-\eta^{gen\ dressed}$", 0.004),
                              ("dphi", r"$\phi^{reco}-\phi^{gen\ dressed}$", 0.004)):
            fv.overlay(
                [(p[f"{var}_nom"][s], p["w"][s], fv.NOMINAL_STYLE, False),
                 (p[f"{var}_fsr"][s], p["w"][s], fv.FSR_STYLE, False)],
                np.linspace(-rng, rng, 41), lab, out, f"{var}_{tag}", era, title=f"{name}, {split}",
                ratio_label="FSR / nom.",
            )
        for tagv, key in (("nominal", "nom"), ("fsr", "fsr")):
            rows.append({"sample": name, "quantity": f"pT response median [{split}] {tagv}",
                         "value": fv.wmedian(p[key][s], p["w"][s])})
            rows.append({"sample": name, "quantity": f"pT response sigma_eff [{split}] {tagv}",
                         "value": fv.sigma_eff(p[key][s], p["w"][s])})
    # dimuon mass vs the dressed dimuon mass
    m_dressed = fv.dressed_dimuon_mass(match)
    for split, mask in splits(ev).items():
        s = mask & both & (m_dressed > 0)
        if not np.any(s):
            continue
        r_nom, r_fsr = fv.np_(ev, M_NOM)[s] / m_dressed[s], fv.np_(ev, M_FSR)[s] / m_dressed[s]
        fv.overlay(
            [(r_nom, w[s], fv.NOMINAL_STYLE, False), (r_fsr, w[s], fv.FSR_STYLE, False)],
            np.linspace(0.92, 1.08, 65), r"$m_{\mu\mu}^{reco} / m_{\mu\mu}^{gen\ dressed}$", out,
            f"mass_over_dressed_{split}", era, title=f"{name}, {split}", ratio_label="FSR / nom.", logy=True,
        )
        for tagv, r in (("nominal", r_nom), ("fsr", r_fsr)):
            rows.append({"sample": name, "quantity": f"m/m_dressed median [{split}] {tagv}",
                         "value": fv.wmedian(r, w[s])})
            rows.append({"sample": name, "quantity": f"m/m_dressed sigma_eff [{split}] {tagv}",
                         "value": fv.sigma_eff(r, w[s])})
    return rows


# --------------------------------------------------------------------------------------------------------- #
# 5. Chosen-photon diagnostics, and DY MC vs data in the Z control region
# --------------------------------------------------------------------------------------------------------- #
PHOTON_VARS = [
    ("fsrPhoton_pt", r"$p_T^\gamma$ [GeV]", np.linspace(0, 40, 41), True),
    ("fsrPhoton_eta", r"$\eta^\gamma$", np.linspace(-2.5, 2.5, 26), False),
    ("fsrPhoton_dR", r"$\Delta R(\mu,\gamma)$", np.linspace(0, 0.5, 26), False),
    ("fsrPhoton_relIso03", r"photon relIso03", np.linspace(0, 1.8, 37), False),
    ("fsrPhoton_dROverEt2", r"$\Delta R / p_{T,\gamma}^2$ [GeV$^{-2}$]", np.linspace(0, 0.012, 25), False),
    ("pt_ratio", r"$p_T^\gamma / p_T^\mu$", np.linspace(0, 0.4, 41), False),
]


def photon_values(ev, var):
    """Pool the chosen photons of mu1 and mu2. Returns (values, weights)."""
    vals, ws = [], []
    w = fv.weights(ev) if fv.WEIGHT_BRANCH in ev.fields else np.ones(len(ev))
    for mu in ("mu1", "mu2"):
        has = fv.np_(ev, f"{mu}_hasFSR") > 0
        if var == "pt_ratio":
            v = fv.np_(ev, f"{mu}_fsrPhoton_pt") / fv.np_(ev, f"{mu}_bsConstrainedPt")
        else:
            v = fv.np_(ev, f"{mu}_{var}")
        vals.append(v[has])
        ws.append(w[has])
    return np.concatenate(vals), np.concatenate(ws)


def fsr_fractions(name, ev):
    w = fv.weights(ev)
    rows = []
    for mu in ("mu1", "mu2"):
        rows.append({"sample": name, "quantity": f"fraction of {mu} with FSR",
                     "value": fv.wfraction(fv.np_(ev, f"{mu}_hasFSR") > 0, w)})
    rows.append({"sample": name, "quantity": "fraction of events with >=1 FSR photon",
                 "value": fv.wfraction(fv.np_(ev, "diMuon_nFSR") > 0, w)})
    rows.append({"sample": name, "quantity": "fraction of events with 2 FSR photons",
                 "value": fv.wfraction(fv.np_(ev, "diMuon_nFSR") == 2, w)})
    return rows


def photon_study(samples, era, outdir):
    out = os.path.join(outdir, "photon_diagnostics") + "/"
    styles = {"ggH": dict(color="#e42536"), "VBF": dict(color="#f89c20"), "DY": dict(color="#3f90da")}
    mc = [(n, ev) for n, ev in samples.items() if n != "Data"]
    for var, label, edges, logy in PHOTON_VARS:
        series = []
        for n, ev in mc:
            v, w = photon_values(ev, var)
            series.append((v, w, dict(label=n, **styles.get(n, {})), False))
        if series:
            fv.overlay(series, edges, label, out, f"photon_{var}", era, title="chosen FSR photons (MC)",
                       ratio_label=f"/ {mc[0][0]}", logy=logy)
    for n, ev in mc:  # 2D with the analysis cut boundaries
        v_pt, w = photon_values(ev, "fsrPhoton_pt")
        v_dr, _ = photon_values(ev, "fsrPhoton_dR")
        v_iso, _ = photon_values(ev, "fsrPhoton_relIso03")
        v_det, _ = photon_values(ev, "fsrPhoton_dROverEt2")
        fv.hist2d(v_dr, v_pt, w, np.linspace(0, 0.5, 26), np.linspace(2, 30, 29), r"$\Delta R(\mu,\gamma)$",
                  r"$p_T^\gamma$ [GeV]", out, f"photon_pt_vs_dR_{n}", era)
        fv.hist2d(v_dr, v_iso, w, np.linspace(0, 0.5, 26), np.linspace(0, 2.0, 41), r"$\Delta R(\mu,\gamma)$",
                  "photon relIso03", out, f"photon_iso_vs_dR_{n}", era, lines=[("y", 1.8)])
        fv.hist2d(v_pt, v_det, w, np.linspace(2, 30, 29), np.linspace(0, 0.05, 51), r"$p_T^\gamma$ [GeV]",
                  r"$\Delta R / p_{T,\gamma}^2$ [GeV$^{-2}$]", out, f"photon_dROverEt2_vs_pt_{n}", era,
                  lines=[("y", 0.012)])


def data_mc_study(dy, data, era, outdir):
    """Shape comparison in the Z control region. Both samples get the same m < 110 GeV cut on both masses."""
    out = os.path.join(outdir, "data_vs_MC") + "/"
    mc_mask = (fv.np_(dy, M_NOM) < fv.DATA_MAX_MASS) & (fv.np_(dy, M_FSR) < fv.DATA_MAX_MASS)
    dy = dy[mc_mask]
    data = _with_unit_weights(data)  # data counted with unit weights
    data_style = dict(color="black", label="Data")
    mc_style = dict(color="#3f90da", label="DY MC")
    wd = np.ones(len(data))
    for var, label, edges, logy in PHOTON_VARS:
        vm, wm = photon_values(dy, var)
        vd, _ = photon_values(data, var)
        fv.overlay([(vm, wm, mc_style, False), (vd, np.ones(len(vd)), data_style, True)], edges, label, out,
                   f"photon_{var}", era, title="Z CR, chosen photons", is_data=True, ratio_label="Data / MC",
                   logy=logy)
    fv.overlay([(fv.np_(dy, "nFsrPhoton"), fv.weights(dy), mc_style, False),
                (fv.np_(data, "nFsrPhoton"), wd, data_style, True)], np.arange(-0.5, 6.5, 1),
               "NanoAOD FsrPhoton candidates / event", out, "nFsrPhoton", era, title="Z CR", is_data=True,
               ratio_label="Data / MC", logy=True)
    fv.overlay([(fv.np_(dy, "diMuon_nFSR"), fv.weights(dy), mc_style, False),
                (fv.np_(data, "diMuon_nFSR"), wd, data_style, True)], np.arange(-0.5, 3.5, 1),
               "accepted FSR photons / event", out, "nFSR", era, title="Z CR", is_data=True,
               ratio_label="Data / MC", logy=True)
    rows = []
    edges = np.linspace(*DATA_MC_RANGE, 51)
    for tag, branch in (("nominal", M_NOM), ("fsr", M_FSR)):
        fv.overlay([(fv.np_(dy, branch), fv.weights(dy), mc_style, False),
                    (fv.np_(data, branch), wd, data_style, True)], edges, rf"$m_{{\mu\mu}}$ ({tag}) [GeV]", out,
                   f"Z_mass_{tag}", era, title="Z CR", is_data=True, ratio_label="Data / MC", logy=True)
        for name, ev, w in (("DY MC", dy, fv.weights(dy)), ("Data", data, wd)):
            x = fv.np_(ev, branch)
            win = (x > DATA_MC_RANGE[0]) & (x < DATA_MC_RANGE[1])
            peak = win & (x > 80) & (x < 100)
            rows.append({"sample": name, "quantity": f"tail fraction 60-80 / 60-110 [{tag}]",
                         "value": fv.wfraction((x < DY_TAIL[1]) & win, np.where(win, w, 0.0))})
            rows.append({"sample": name, "quantity": f"median mass in 80-100 [{tag}]",
                         "value": fv.wmedian(x[peak], w[peak])})
            rows.append({"sample": name, "quantity": f"sigma_eff in 80-100 [{tag}]",
                         "value": fv.sigma_eff(x[peak], w[peak])})
    rows += fsr_fractions("DY MC (Z CR)", dy) + fsr_fractions("Data (Z CR)", data)
    return rows


def _with_unit_weights(data):
    return ak.with_field(data, np.ones(len(data)), fv.WEIGHT_BRANCH)


# --------------------------------------------------------------------------------------------------------- #
def write_table(rows, path_stem):
    if not rows:
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path_stem + ".csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    with open(path_stem + ".json", "w") as f:
        json.dump(rows, f, indent=2, default=float)
    print(f"Written {path_stem}.csv/.json")


def main():
    args = parse_args()
    outdir = args.outdir or str((PLOT_DIR / args.era).resolve())
    os.makedirs(outdir, exist_ok=True)
    print(f"Output directory: {outdir}")
    overrides = {"ggH": args.ggh, "VBF": args.vbf, "DY": args.dy, "Data": args.data}
    samples = {}
    for name in args.samples:
        is_data = name == "Data"
        patterns = overrides[name]
        if not patterns:
            default = (TUPLE_DIR / TUPLE_NAME.format(sample=name, era=args.era)).resolve()
            if not default.exists():
                print(f"skipping {name}: {default} not found")
                continue
            patterns = [str(default)]
        files = fv.expand(patterns)
        if files:
            if name != "Data" and any(fv.looks_like_data(f) for f in files):
                raise ValueError(f"--{name.lower()} got a data-like file name; data must go through --data")
            samples[name] = fv.load(files, is_data=is_data, max_events=args.max_events)
            print(f"{name}: {len(samples[name])} events from {len(files)} file(s)")

    # 1. invariants (data included: these are implementation checks, and data is already blinded)
    inv = {name: fv.invariants(ev) for name, ev in samples.items()}
    with open(os.path.join(outdir, "invariants.json"), "w") as f:
        json.dump(inv, f, indent=2)
    print("\n=== Invariant violations (0 expected) ===")
    for name, counts in inv.items():
        bad = {k: v for k, v in counts.items() if k != "n_events" and v}
        print(f"{name:5s} n={counts['n_events']}: " + ("OK" if not bad else json.dumps(bad)))

    resolution, dy_rows, dressed, fractions = [], [], [], []
    for name in ("ggH", "VBF"):
        if name in samples:
            resolution += signal_study(name, samples[name], args.era, outdir, args.n_bootstrap)
            dressed += dressed_study(name, samples[name], args.era, outdir, args.match_dr)
            fractions += fsr_fractions(name, samples[name])
    if "DY" in samples:
        dy_rows = dy_study(samples["DY"], args.era, outdir, args.n_bootstrap)
        dressed += dressed_study("DY", samples["DY"], args.era, outdir, args.match_dr)
        fractions += fsr_fractions("DY", samples["DY"])
    photon_study(samples, args.era, outdir)
    data_mc = []
    if "DY" in samples and "Data" in samples:
        data_mc = data_mc_study(samples["DY"], samples["Data"], args.era, outdir)

    summary_dir = os.path.join(outdir, "summary")
    os.makedirs(summary_dir, exist_ok=True)
    write_table(resolution, os.path.join(summary_dir, "signal_resolution"))
    write_table(dy_rows, os.path.join(summary_dir, "dy_z_tail"))
    write_table(dressed, os.path.join(summary_dir, "gen_dressed"))
    write_table(fractions + data_mc, os.path.join(summary_dir, "fsr_fractions_and_data_mc"))

    print("\n=== Signal resolution (sigma_eff, GeV) ===")
    for r in resolution:
        if "sigma_eff_nominal" in r:
            print(f"{r['sample']:4s} {r['split']:13s} nom {r['sigma_eff_nominal']:.3f} +- {r['sigma_eff_nominal_err']:.3f}"
                  f"  FSR {r['sigma_eff_fsr']:.3f} +- {r['sigma_eff_fsr_err']:.3f}"
                  f"  improvement {100 * r['improvement']:+.2f} +- {100 * r['improvement_err']:.2f} %")
    print("\n=== DY (Born-level Z, gen_mll 81-101) ===")
    for r in dy_rows:
        if "frac_tail_nominal" in r:
            print(f"{r['split']:8s} tail {r['frac_tail_nominal']:.4f} -> {r['frac_tail_fsr']:.4f}"
                  f"  peak {r['frac_peak_nominal']:.4f} -> {r['frac_peak_fsr']:.4f}"
                  f"  above {r['frac_above_peak_nominal']:.4f} -> {r['frac_above_peak_fsr']:.4f}"
                  f"  response sigma_eff {r['response_sigma_eff_nominal']:.4f} -> {r['response_sigma_eff_fsr']:.4f}")


if __name__ == "__main__":
    main()
