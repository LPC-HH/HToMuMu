import matplotlib

matplotlib.use("Agg")

import argparse
import os
import sys

import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import uproot

from utils.colors import get_color_list
from utils.dy_stitching import weighted_ratio
from utils.helper import get_canvas, save_figure

sys.path.append("../condor/utils")
import version as v

# Generator-level closure of the all-aMC@NLO DY stitching (lib/DYStitching.h), from the histograms the
# analyzer fills before any selection (in each dataset's SumGenWeight.root):
#   h_sumOfgenWeight_genMll[_VBFFilter] : sum(genWeight) vs LHE mumu mll (all events / emulated filter pass)
#   h_sumOfgenWeight[2]_stitchCells     : sum(genWeight) [and of genWeight^2] per stitching cell
# and the stitch_sigma / stitch_sumw / stitch_frac values written by scripts/compute_DY_stitching.py:
#   genmll_handoff : d(sigma)/d(LHE mll) of the jet-binned 0J+1J+2J samples (J) vs the 105-160 sample (U),
#                    whose cross section is matched to J in 105-160, so the ratio tests the shape
#   genmll_R       : the same in the filter region R, for J, U and the VBF-filtered sample (F)
#   cell table     : sigma per cell (p, R) from each sample, with stat. uncertainties (sum w^2)
# Usage: python3 plot_DY_stitching_genlevel.py [era]
parser = argparse.ArgumentParser()
parser.add_argument("era", nargs="?", default="2024")
era = parser.parse_args().era
campaign = "Summer" + era[2:]

EOS_PATH = os.getenv("DY_STITCH_EOS_PATH", f"/eos/uscms/store/group/lpchmumu/{os.getenv('LOGNAME')}/"
                     f"analyzer_HiggsMuMu_{v.ANALYZER_VERSION_NUMBER}/MC_background")
MLL_LOW, MLL_HIGH = 105, 160
N_PARTON_BINS = 3
EXTENSIONS = ["", "_ext1", "_ext2"]


def read(dataset):
    path = f"{EOS_PATH}/{dataset}/SumGenWeight.root"
    if not os.path.exists(path):
        return None
    with uproot.open(path) as f:
        out = {"edges": f["h_sumOfgenWeight_genMll"].axis().edges(),
               "mll": f["h_sumOfgenWeight_genMll"].values(),
               "mll_R": f["h_sumOfgenWeight_genMll_VBFFilter"].values(),
               "cells": f["h_sumOfgenWeight_stitchCells"].values(),
               "cells_w2": f["h_sumOfgenWeight2_stitchCells"].values()}
        for key in ["sigma", "sumw"]:
            if "stitch_" + key in f:
                out[key] = f["stitch_" + key].values()[0]
    return out


def read_sample(base):
    """Sums over the sample's extensions (stitch_sigma / stitch_sumw already refer to all of them)"""
    combined = None
    for ext in EXTENSIONS:
        sums = read(f"{base}_{campaign}{ext}")
        if sums is None:
            continue
        if combined is None:
            combined = sums
        else:
            for key in ["mll", "mll_R", "cells", "cells_w2"]:
                combined[key] = combined[key] + sums[key]
    return combined


prefix = "DYto2Mu-2Jets" if era in ["2024", "2025"] else "DYto2L-2Jets"
samples = {f"J{p}": read_sample(f"{prefix}_{p}J") for p in range(N_PARTON_BINS)}
samples["U"] = read_sample("DYto2Mu-2Jets_105to160")
samples["F"] = read_sample("DYto2Mu-2Jets_105to160_VBFFilter")
missing = [name for name, sums in samples.items() if sums is None or "sigma" not in sums]
if missing:
    print(f"[ERROR] Missing SumGenWeight.root or stitch_* values for {missing} in {EOS_PATH}: "
          "run ComputeWeights.py and scripts/compute_DY_stitching.py first")
    exit(1)

edges = samples["U"]["edges"]
in_window = (edges[:-1] >= MLL_LOW) & (edges[1:] <= MLL_HIGH)


def scaled(sums, key):
    """d(sigma) per bin [pb]; the mll histograms are filled without Sumw2, so no per-bin uncertainty"""
    return sums[key] * sums["sigma"] / sums["sumw"], np.zeros(len(sums[key]))


J_xs = sum(scaled(samples[f"J{p}"], "mll")[0] for p in range(N_PARTON_BINS))
J_R = sum(scaled(samples[f"J{p}"], "mll_R")[0] for p in range(N_PARTON_BINS))
U_xs, U_R = scaled(samples["U"], "mll")[0], scaled(samples["U"], "mll_R")[0]
F_R = scaled(samples["F"], "mll_R")[0]
zeros = np.zeros(len(U_xs))

print(f"Era {era}: sigma [pb] " + ", ".join(f"{name} {sums['sigma']:.4f}" for name, sums in samples.items()))
print(f"  sigma in 105-160: J {J_xs[in_window].sum():.4f}, U {U_xs.sum():.4f}")
print(f"  sigma in R      : J {J_R[in_window].sum():.4f}, U {U_R.sum():.4f}, F {F_R.sum():.4f}")
print(f"\n  {'cell':<14}" + "".join(f"{name:>20}" for name in samples) + "   (sigma per cell [pb] +- stat)")
for c in range(1, 2 * N_PARTON_BINS + 1):
    p, R = (c - 1) // 2, (c - 1) % 2
    row = f"  p={p}, R={R}     "
    for name, sums in samples.items():
        scale = sums["sigma"] / sums["sumw"]
        value, error = sums["cells"][c] * scale, np.sqrt(sums["cells_w2"][c]) * scale
        covers = name in ["U"] or (name == "F" and R == 1) or name == f"J{p}"
        row += f"{value:11.4f} +-{error:7.4f}" if covers else f"{'-':>20}"
    print(row)

output_directory = f"../plots/DY_stitching_amcnlo/{era}/genlevel/"
plt.style.use(hep.style.CMS)
colors = get_color_list(4)


def draw(curves, reference, file_name, x_range, ylabel_ratio):
    fig, (ax, ratio_ax) = get_canvas(draw_ratio=True)
    ref_xs, ref_w2 = curves[reference][:2]
    for (label, (xs, w2, style)), color in zip(curves.items(), colors):
        hep.histplot(xs, edges, yerr=np.sqrt(w2), ax=ax, color=color, linewidth=2, linestyle=style,
                     label=label)
        if label != reference:
            ratio, error = weighted_ratio(xs, w2, ref_xs, ref_w2)
            hep.histplot(np.nan_to_num(ratio), edges, yerr=np.nan_to_num(error), ax=ratio_ax, color=color,
                         histtype="errorbar")
    hep.cms.label(data=False, label="", year=era, com="13.6", ax=ax)
    ax.set_yscale("log")
    ax.set_ylim(top=ax.get_ylim()[1] * 50)
    ax.set_xlim(*x_range)
    ax.set_ylabel(r"$\sigma$ / bin [pb]")
    ax.legend(frameon=False, loc="upper right", fontsize=14)
    ax.tick_params(labelbottom=False)
    for boundary in [MLL_LOW, MLL_HIGH]:
        ax.axvline(boundary, color="gray", linestyle=":")
        ratio_ax.axvline(boundary, color="gray", linestyle=":")
    ratio_ax.set_xlim(*x_range)
    ratio_ax.set_ylim(0.8, 1.2)
    ratio_ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ratio_ax.set_ylabel(ylabel_ratio)
    ratio_ax.set_xlabel(r"LHE $m_{\mu\mu}$ [GeV]")
    save_figure(fig, output_directory, f"{file_name}_{era}")
    plt.close()


draw({"aMC@NLO 0J+1J+2J": (J_xs, zeros, "-"),
      "aMC@NLO 105-160": (U_xs, zeros, "-")},
     "aMC@NLO 0J+1J+2J", "genmll_handoff", (90, 175), "/ 0J+1J+2J")
draw({"aMC@NLO 0J+1J+2J in R": (J_R, zeros, "-"),
      "aMC@NLO 105-160 in R": (U_R, zeros, "-"),
      "aMC@NLO VBF-filtered in R": (F_R, zeros, "-")},
     "aMC@NLO 0J+1J+2J in R", "genmll_R", (100, 165), "/ 0J+1J+2J in R")
print(f"Plots written to {output_directory}")
