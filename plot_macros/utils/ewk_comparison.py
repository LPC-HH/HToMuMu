"""Shared definitions of the EWK Z+2j (VBF Z) sample comparison
(plot_EWK_comparison.py: reco level from the tuples, plot_EWK_comparison_genlevel.py: generator level from the
SumGenWeight.root files).

The 2024 samples (each with an _ext1):
  H7 2L2J  : EWK-2L2J  MLL>50, MJJ>120          MadGraph + Herwig7, ee/mumu/tautau
  H7 2Mu2J : EWK-2Mu2J MLL 105-160             MadGraph + Herwig7, mumu
  P8 2Mu2J : EWK-2Mu2J M2Mu 105-160, M2J>120   MadGraph + Pythia8, mumu
They overlap for LHE mumu with 105 <= m < 160, the window of the 2Mu2J samples (dy_stitch::InWindow uses the same
bounds), which is where H7 2L2J (restricted with the LHE_mll tuple branch) and H7 2Mu2J can be compared like for like.

Normalisation: from tuples v2.8.1 on, CreateTuple normalises every dataset with the sum of gen weights over the
sample and all its extensions (h_sumOfgenWeight_sample, scripts/ComputeWeights.py), so the datasets of a sample simply
add up. Older tuples used each dataset's own sum, so the nominal sample and its extensions each carried the full yield;
for those each dataset is given the fraction sumw_i / sum_j sumw_j of the sample (extension_fractions).
"""
import os
import re

import numpy as np
import uproot

EXTENSIONS = ["", "_ext1", "_ext2"]

# LHE mumu mass window of the 2Mu2J samples (= dy_stitch::MLL_LOW / MLL_HIGH in lib/DYStitching.h)
LHE_WINDOW = (105.0, 160.0)

# Bin index (0-based) of the pre-selection stitching-cell histograms that hold the events inside the LHE window:
# cells 1..6 need the FxFx parton multiplicity, the LO MadGraph EWK samples have none and land in cell 7
WINDOW_CELLS = list(range(1, 8))

# label -> dataset base name (= CreateTuple channel = CROSS_SECTION key). The first entry is the reference
# of the ratio panels: same generator as H7 2L2J, same mass window as P8 2Mu2J.
SAMPLES = {
    "H7 2Mu2J": "EWK_2Mu2J",
    "H7 2L2J": "EWK_2L2J",
    "P8 2Mu2J": "EWK_2Mu2J_pythia",
}
GENERATOR_CUTS = {
    "H7 2Mu2J": r"$\mu\mu$, $m_{\mu\mu}$ 105-160",
    "H7 2L2J": r"$\ell\ell$, $m_{\ell\ell}>50$, $m_{jj}>120$",
    "P8 2Mu2J": r"$\mu\mu$, $m_{\mu\mu}$ 105-160, $m_{jj}>120$",
}
ERAS = ["2024"]  # eras that have all three samples

RUN3_CONSTANTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../lib/Run3Constants.h")


def campaign(era):
    return "Summer" + era[2:]


def dataset_names(base, era):
    return [f"{base}_{campaign(era)}{ext}" for ext in EXTENSIONS]


def _read_map(name):
    """{key: value} of a `const std::map<TString, float> NAME = {...}` block of lib/Run3Constants.h"""
    with open(RUN3_CONSTANTS) as f:
        text = f.read()
    block = text[text.index(name + " = {"):]
    block = block[:block.index("};")]
    return {key: float(value) for key, value in re.findall(r'\{\s*"([^"]+)"\s*,\s*([0-9.eE+-]+)\s*\}', block)}


def read_cross_sections():
    """CROSS_SECTION [pb] from lib/Run3Constants.h, the values CreateTuple uses"""
    return _read_map("CROSS_SECTION")


def read_luminosities():
    """LUMINOSITY [fb^-1] from lib/Run3Constants.h, the values CreateTuple normalises the MC to"""
    return _read_map("LUMINOSITY")


def analyzer_directory(analyzer_version):
    """MC_background directory of the analyzer outputs (with the SumGenWeight.root files) on EOS.
    EWK_COMPARISON_EOS_PATH overrides it (e.g. for tests on a local copy)."""
    default = (f"/eos/uscms/store/group/lpchmumu/{os.getenv('LOGNAME') or os.getenv('USER')}/"
               f"analyzer_HiggsMuMu_v{analyzer_version}/MC_background")
    return os.getenv("EWK_COMPARISON_EOS_PATH", default)


def read_weight_sums(directory, dataset):
    """Pre-selection sums of the analyzer for one dataset (None if it has no SumGenWeight.root)"""
    path = f"{directory}/{dataset}/SumGenWeight.root"
    if not os.path.exists(path):
        return None
    with uproot.open(path) as f:
        mll = f["h_sumOfgenWeight_genMll"]
        return {
            "total": float(f["h_sumOfgenWeight"].values()[0]),
            "edges": mll.axis().edges(),
            "mll": mll.values().astype(np.float64),
            "mll_R": f["h_sumOfgenWeight_genMll_VBFFilter"].values().astype(np.float64),
            "cells": f["h_sumOfgenWeight_stitchCells"].values().astype(np.float64),
            "cells_w2": f["h_sumOfgenWeight2_stitchCells"].values().astype(np.float64),
        }


def read_sample_sums(directory, base, era):
    """Sums of a sample over its extensions: {"datasets": [...], "per_dataset": {dataset: total}, and the summed
    histograms of read_weight_sums}; None if no dataset of the sample has a SumGenWeight.root"""
    combined = None
    for dataset in dataset_names(base, era):
        sums = read_weight_sums(directory, dataset)
        if sums is None:
            continue
        if combined is None:
            combined = dict(sums, datasets=[dataset], per_dataset={dataset: sums["total"]})
            continue
        if not np.array_equal(combined["edges"], sums["edges"]):
            raise ValueError(f"h_sumOfgenWeight_genMll binning of {dataset} differs from {combined['datasets'][0]}")
        combined["datasets"].append(dataset)
        combined["per_dataset"][dataset] = sums["total"]
        for key in ["total", "mll", "mll_R", "cells", "cells_w2"]:
            combined[key] = combined[key] + sums[key]
    return combined


# First tuples version normalised with the sum over the extensions (h_sumOfgenWeight_sample)
SAMPLE_NORMALISED_TUPLES = (2, 8, 1)


def extension_fractions(sample_sums, tuples_version):
    """{dataset: factor} that turns the CreateTuple weights of the nominal sample and its extensions into one
    prediction: 1 for tuples normalised over the extensions (>= v2.8.1), sumw_i / sum_j sumw_j before"""
    version = tuple(int(x) for x in str(tuples_version).lstrip("v").split("."))
    if version >= SAMPLE_NORMALISED_TUPLES:
        return {dataset: 1.0 for dataset in sample_sums["per_dataset"]}
    return {dataset: total / sample_sums["total"] for dataset, total in sample_sums["per_dataset"].items()}
