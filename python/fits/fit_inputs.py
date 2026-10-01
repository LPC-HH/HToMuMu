"""Load the per-BDT-category mass distributions for the pyhf fit.

Three sources:
  * data     -- unweighted events from allData_combined.root  (BLINDED)
  * signal   -- weighted ggH + VBF MC from the two signal files
  * mc_bkg   -- weighted DY/EWK/TT/DiBoson from the upstream BDT-scored tuples
                (only needed for background model B)

Blinding contract
-----------------
`load_data()` *always* drops events with 120 <= m <= 130 GeV before returning
anything, and asserts that none survive. Downstream code therefore physically
cannot see blinded data. Signal MC and MC background are not blinded.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import uproot

from . import fit_config as cfg


# --------------------------------------------------------------------------- #
@dataclass
class CategoryInputs:
    category: str
    # signal MC (mass, weight) -- weight still has BR divided out
    sig_ggh_mass: np.ndarray
    sig_ggh_w: np.ndarray
    sig_vbf_mass: np.ndarray
    sig_vbf_w: np.ndarray
    # data, ALREADY blinded (only |m - 125| region outside 120-130 kept)
    data_mass_blinded: np.ndarray
    # optional MC background (filled by load_mc_background)
    bkg_mass: np.ndarray | None = None
    bkg_w: np.ndarray | None = None
    bkg_w2: np.ndarray | None = None  # sum-w^2 ingredients kept per event as w**2

    def signal_yield(self, br: float = cfg.BR_HMM, window=None) -> dict:
        """Physical expected signal yield (mu = 1) in a mass window."""
        lo, hi = cfg.FIT_RANGE if window is None else window
        mg = (self.sig_ggh_mass >= lo) & (self.sig_ggh_mass <= hi)
        mv = (self.sig_vbf_mass >= lo) & (self.sig_vbf_mass <= hi)
        return {
            "ggH": float(self.sig_ggh_w[mg].sum() * br),
            "VBF": float(self.sig_vbf_w[mv].sum() * br),
        }


# --------------------------------------------------------------------------- #
def _in_range(mass: np.ndarray) -> np.ndarray:
    lo, hi = cfg.FIT_RANGE
    return (mass >= lo) & (mass <= hi)


def load_signal(categories=None) -> dict[str, CategoryInputs]:
    """Read signal MC + blinded data for the requested categories."""
    categories = categories or cfg.discover_categories()
    fg = uproot.open(cfg.SIG_GGH_FILE)
    fv = uproot.open(cfg.SIG_VBF_FILE)
    fd = uproot.open(cfg.DATA_FILE)

    out: dict[str, CategoryInputs] = {}
    for cat in categories:
        gg = fg[cfg.sig_ggh_tree(cat)].arrays([cfg.MASS_BRANCH, "weight"], library="np")
        vb = fv[cfg.sig_vbf_tree(cat)].arrays([cfg.MASS_BRANCH, "weight"], library="np")
        dd = fd[cfg.data_tree(cat)].arrays([cfg.MASS_BRANCH], library="np")

        gg_m, gg_w = gg[cfg.MASS_BRANCH], gg["weight"]
        vb_m, vb_w = vb[cfg.MASS_BRANCH], vb["weight"]
        d_m = dd[cfg.MASS_BRANCH]

        # --- BLINDING: remove 120-130 GeV data before it can be looked at ---
        blo, bhi = cfg.BLIND_WINDOW
        keep = _in_range(d_m) & ~((d_m >= blo) & (d_m <= bhi))
        d_m = d_m[keep]
        assert not np.any((d_m >= blo) & (d_m <= bhi)), "blinding failed"

        mg, mv = _in_range(gg_m), _in_range(vb_m)
        out[cat] = CategoryInputs(
            category=cat,
            sig_ggh_mass=gg_m[mg], sig_ggh_w=gg_w[mg],
            sig_vbf_mass=vb_m[mv], sig_vbf_w=vb_w[mv],
            data_mass_blinded=d_m,
        )
    return out


def load_mc_background(inputs: dict[str, CategoryInputs]) -> None:
    """Fill `bkg_mass` / `bkg_w` on each CategoryInputs from the upstream
    per-sample tuples, re-applying the same BDT-score + category selection that
    scripts/split_tuples.py uses. Mutates `inputs` in place.

    Reads only the branches needed and iterates in chunks to keep memory low
    (the DY file is multi-GB).
    """
    lo, hi = cfg.FIT_RANGE
    # group categories by channel so we open each big file once
    by_channel: dict[str, list[str]] = {"ggH": [], "VBF": []}
    for cat in inputs:
        by_channel[cfg.channel_of(cat)].append(cat)

    for channel, cats in by_channel.items():
        if not cats:
            continue
        bdt_branch = f"BDT_{channel}"
        cat_flag = f"is_{channel}_categoryBDT"
        windows = {c: cfg.bdt_window(c) for c in cats}
        acc = {c: {"m": [], "w": []} for c in cats}

        for sample in cfg.MC_BKG_SAMPLES:
            path = cfg.mc_bkg_file(channel, sample)
            branches = ["diMuon_bsConstrainedMass", bdt_branch, cat_flag, "weight"]
            for chunk in uproot.iterate(
                f"{path}:tree_output", branches, library="np", step_size="200 MB"
            ):
                m = chunk["diMuon_bsConstrainedMass"]
                score = chunk[bdt_branch]
                flag = chunk[cat_flag] == 1
                w = chunk["weight"]
                base = flag & (m >= lo) & (m <= hi)
                for c in cats:
                    blo, bhi = windows[c]
                    sel = base & (score >= blo) & (score < bhi)
                    acc[c]["m"].append(m[sel])
                    acc[c]["w"].append(w[sel])

        for c in cats:
            mm = np.concatenate(acc[c]["m"]) if acc[c]["m"] else np.array([])
            ww = np.concatenate(acc[c]["w"]) if acc[c]["w"] else np.array([])
            inputs[c].bkg_mass = mm
            inputs[c].bkg_w = ww
            inputs[c].bkg_w2 = ww ** 2


# --------------------------------------------------------------------------- #
def summary_table(inputs: dict[str, CategoryInputs]) -> str:
    """Human-readable per-category yield table (safe: data shown as sideband
    count only)."""
    edges = cfg.mass_bins()
    lo_y, hi_y = cfg.YIELD_WINDOW
    rows = [
        f"{'category':10s} {'S_ggH':>9s} {'S_VBF':>9s} {'S_tot':>9s} "
        f"{'S(win)':>9s} {'data_SB':>10s}"
    ]
    for cat, ci in inputs.items():
        y = ci.signal_yield()
        yw = ci.signal_yield(window=cfg.YIELD_WINDOW)
        n_sb = int(len(ci.data_mass_blinded))
        rows.append(
            f"{cat:10s} {y['ggH']:9.2f} {y['VBF']:9.2f} {y['ggH'] + y['VBF']:9.2f} "
            f"{yw['ggH'] + yw['VBF']:9.2f} {n_sb:10d}"
        )
    return "\n".join(rows)
