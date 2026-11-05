"""Central configuration for the pyhf H->mumu expected-significance cross-check.

Everything that the notebook / scripts need to agree on lives here: file paths,
the category list, the mass binning, the blinding window, and the (currently
placeholder) systematic sizes.

Nothing in this module reads ROOT files or builds models -- it is pure config.
"""

from __future__ import annotations

import os

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
# Repository root (…/CMSSW_15_0_9/src/HToMuMu). This file is python/fits/fit_config.py
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

SPLIT_DIR = os.path.join(REPO_ROOT, "root_io", "tuples", "split_tuples")

# Trees split by BDT category (produced by scripts/split_tuples.py)
DATA_FILE = os.path.join(SPLIT_DIR, "allData_combined.root")
SIG_GGH_FILE = os.path.join(SPLIT_DIR, "ggH", "output_signal_M125_13TeV_cats_pythia8.root")
SIG_VBF_FILE = os.path.join(SPLIT_DIR, "VBF", "output_signal_M125_13TeV_cats_pythia8.root")

# Upstream per-sample BDT-scored tuples, used only for background model B (MC templates).
# One directory per channel; each has its own BDT_<channel> branch.
BDT_SCORE_DIR = os.path.join(REPO_ROOT, "root_io", "tuples", "BDT_score")


def mc_bkg_file(channel: str, sample: str) -> str:
    """Path to an upstream MC background tuple, e.g. mc_bkg_file('ggH', 'DY')."""
    return os.path.join(
        BDT_SCORE_DIR, channel, "BFull_SNottH", f"{sample}_Combined_BFull_SNottH.root"
    )


MC_BKG_SAMPLES = ["DY", "EWK", "TT", "DiBoson"]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")

# --------------------------------------------------------------------------- #
# Categories  (DISCOVERED at runtime -- the BDT category count changes whenever
# plot_macros/plot_BDT_Categories.py is re-run. cat1 = most signal-like.)
# --------------------------------------------------------------------------- #
def channel_of(category: str) -> str:
    """'ggH' or 'VBF' -- which BDT channel a category name belongs to."""
    return "ggH" if category.startswith("ggH") else "VBF"


def _cat_sort_key(name: str):
    ch = channel_of(name)
    return (0 if ch == "ggH" else 1, int(name.replace(ch + "cat", "")))


def discover_categories(channel: str | None = None) -> list[str]:
    """Category names that actually exist in BOTH signal files and the data file.

    `channel` -> 'ggH', 'VBF', or None for all. Sorted cat1..catN.
    """
    import uproot

    def trees_matching(path, prefix):
        try:
            return {k.split(";")[0].split("13TeV_")[-1]
                    for k in uproot.open(path).keys()
                    if "13TeV_" in k and k.split("13TeV_")[-1].startswith(prefix)}
        except Exception:  # noqa: BLE001
            return set()

    prefixes = ["ggHcat", "VBFcat"] if channel is None else [f"{channel}cat"]
    found = None
    for path, tag in ((SIG_GGH_FILE, "ggh"), (SIG_VBF_FILE, "vbf"), (DATA_FILE, "Data")):
        cats = set()
        for p in prefixes:
            cats |= {c for c in trees_matching(path, p)}
        found = cats if found is None else (found & cats)
    cats = sorted(found or [], key=_cat_sort_key)
    return cats


def resolve_categories(which="all") -> list[str]:
    """Map 'all' / 'ggH' / 'VBF' / an explicit list to discovered categories."""
    if isinstance(which, (list, tuple)):
        return list(which)
    return discover_categories(None if which == "all" else which)


# Tree names inside the split ROOT files
def data_tree(category: str) -> str:
    return f"Data_13TeV_{category}"


def sig_ggh_tree(category: str) -> str:
    return f"ggh_125_13TeV_{category}"


def sig_vbf_tree(category: str) -> str:
    return f"vbf_125_13TeV_{category}"


# BDT-score category boundaries: read live from root_io/bdt_categories.json via
# the repo's own loader (python/bdt_categories_io.py). diMuon_bsConstrainedMass
# rows, era "Combined", subset "BFull_SNottH" -- matches scripts/split_tuples.py.
# Needed only to re-cut the upstream tuples for background model B.
BDT_ERA = "Combined"
BDT_SUBSET = "BFull_SNottH"
BDT_MASS_VAR = "diMuon_bsConstrainedMass"


def bdt_boundaries(channel: str) -> list[float]:
    import sys

    if os.path.join(REPO_ROOT, "python") not in sys.path:
        sys.path.insert(0, os.path.join(REPO_ROOT, "python"))
    from bdt_categories_io import get_bdt_cuts, load_bdt_categories

    return get_bdt_cuts(load_bdt_categories(), channel, BDT_ERA, BDT_SUBSET, BDT_MASS_VAR)


def bdt_window(category: str) -> tuple[float, float]:
    """(lo, hi) BDT-score window for a category, from bdt_categories.json."""
    ch = channel_of(category)
    edges = bdt_boundaries(ch)
    ncat = len(edges) - 1
    n = int(category.replace(ch + "cat", ""))  # 1 = most signal-like
    idx_from_low = ncat - n  # cat1 -> highest interval
    return edges[idx_from_low], edges[idx_from_low + 1]


# --------------------------------------------------------------------------- #
# Observable / binning
# --------------------------------------------------------------------------- #
MASS_BRANCH = "CMS_hgg_mass"          # == diMuon_bsConstrainedMass in the split trees
FIT_RANGE = (110.0, 150.0)           # GeV, matches scripts/split_tuples.py
BIN_WIDTH = 0.5                      # GeV  (80 bins); override in studies

# Data blinding: real data with dimuon mass in this window must never be
# histogrammed, printed or otherwise inspected. Expected significance uses an
# Asimov dataset so blinded data is never needed.
BLIND_WINDOW = (120.0, 130.0)

# Narrow window used only for printing S, B, S/sqrt(B) summaries
# (matches plot_macros/plot_BDT_Categories.py signal_region).
YIELD_WINDOW = (122.5, 127.5)

# --------------------------------------------------------------------------- #
# Physics constants
# --------------------------------------------------------------------------- #
# H->mumu branching ratio -- lib/Run3Constants.h H_TO_MUMU_BRANCHING_RATIO.
# The signal `weight` branch in the split trees has this divided back OUT
# (scripts/split_tuples.py line 108, reweight=1), so physical signal yield
# = sum(weight) * BR_HMM.
BR_HMM = 2.176e-4

# The split tuples correspond to the full 2022+2022EE+2023+2023BPix+2024+2025
# dataset  ~ 281.7 fb^-1  (root_io/tuples/hadd_tuples.sh hadds all six eras;
# the 281.7 / 170.97 constants in split_tuples.py confirm it). mu = 1 therefore
# means "SM H->mumu at ~281.7 fb^-1". Do NOT rescale with xgb_utils.py's stale
# luminosity["Combined"] = 170.905.
LUMI_FB = 281.7

# --------------------------------------------------------------------------- #
# Systematic sizes (PLACEHOLDERS -- see README; replace with real values from
# the systematic weight branches once split_tuples.py is extended to carry them)
# --------------------------------------------------------------------------- #
# Signal normalisation systematics, as fractional lnN (applied to both signal
# processes unless noted). Each entry: name -> (down_factor, up_factor).
SIGNAL_NORMSYS = {
    "lumi_run3":   (0.986, 1.014),   # 1.4%  integrated-lumi
    "br_hmm":      (0.990, 1.010),   # ~1%   H->mumu BR (PDG / LHCHWG)
    "muon_sf":     (0.980, 1.020),   # ~2%   muon ID+iso+trigger SF (placeholder)
    "pileup":      (0.990, 1.010),   # ~1%   pileup reweighting (placeholder)
}
# Per-process cross-section (scale+PDF+alpha_s), lnN.
SIGNAL_XS_NORMSYS = {
    "sig_ggH": ("xs_ggH", (0.961, 1.039)),   # ggF ~ +3.9/-3.9% (LHCHWG YR4)
    "sig_VBF": ("xs_VBF", (0.997, 1.004)),   # VBF ~ sub-percent
}

# Signal shape systematics (histosys, built by signal_model.py):
MASS_SCALE_REL = 0.002    # +/-0.2% shift of the fitted peak mean
MASS_RESO_REL = 0.10      # +/-10% scaling of the fitted width

# --------------------------------------------------------------------------- #
# Fit / inference options
# --------------------------------------------------------------------------- #
# scipy optimizer: ~7x faster than minuit for the many-parameter combined fits
# and identical q0 to 3 decimals. Switch to "minuit" if you want Hesse errors.
PYHF_BACKEND = ("numpy", "scipy")

# Background function families tried in model A (sideband analytic fit).
BKG_FAMILIES = ["exp", "exp2", "pow", "bern3", "bern4", "bern5"]

# Number of covariance eigen-directions turned into background shape nuisances
# in model A (per category). Capped at the number of free shape parameters.
BKG_SHAPE_NUISANCES = 3


def mass_bins(bin_width: float | None = None):
    """Return the bin-edge array for the fit observable."""
    import numpy as np

    bw = BIN_WIDTH if bin_width is None else bin_width
    lo, hi = FIT_RANGE
    n = int(round((hi - lo) / bw))
    return np.linspace(lo, hi, n + 1)


def blind_bin_mask(edges):
    """Boolean mask (len = nbins) True for bins that lie *outside* the blind
    window and are therefore usable for a data-driven background fit."""
    import numpy as np

    centers = 0.5 * (edges[:-1] + edges[1:])
    blo, bhi = BLIND_WINDOW
    return (centers < blo) | (centers > bhi)
