import matplotlib

# Never open an X11/GUI backend (slow over ssh -X); plots are only saved to disk
matplotlib.use("Agg")

import argparse
import os
import sys

import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np

import utils.ewk_comparison as ewk
from utils.colors import get_color_list
from utils.dy_stitching import weighted_ratio
from utils.helper import get_canvas, save_figure

sys.path.append("../condor/utils")
import version as v

# Generator-level comparison of the EWK Z+2j samples (utils/ewk_comparison.py), from the histograms the analyzer
# Usage: python3 plot_EWK_comparison_genlevel.py [era] [--analyzer-version X.Y]
parser = argparse.ArgumentParser()
parser.add_argument("era", nargs="?", default="2024", choices=ewk.ERAS)
parser.add_argument("--analyzer-version", default=v.ANALYZER_VERSION_NUMBER.lstrip("v"),
                    help="analyzer version of the SumGenWeight.root files (default: condor/utils/version.py)")
args = parser.parse_args()
era = args.era
directory = ewk.analyzer_directory(args.analyzer_version.lstrip("v"))

cross_sections = ewk.read_cross_sections()
samples = {}
for label, base in ewk.SAMPLES.items():
    sums = ewk.read_sample_sums(directory, base, era)
    if sums is None:
        print(f"[WARNING] {label}: no SumGenWeight.root for any of {ewk.dataset_names(base, era)} in {directory} "
              "(analyzer + ComputeWeights.py not run yet?), left out")
        continue
    if base not in cross_sections:
        print(f"[ERROR] No cross section for {base} in lib/Run3Constants.h (CROSS_SECTION)")
        exit(1)
    sums["sigma"] = cross_sections[base]
    sums["scale"] = sums["sigma"] / sums["total"]  # pb per unit of genWeight
    samples[label] = sums
if not samples:
    print(f"[ERROR] None of the EWK samples has a SumGenWeight.root in {directory}")
    exit(1)

reference = next(iter(samples))
edges = samples[reference]["edges"]
for label, sums in samples.items():
    if not np.array_equal(sums["edges"], edges):
        print(f"[ERROR] {label}: h_sumOfgenWeight_genMll binning differs from {reference}")
        exit(1)
in_window = (edges[:-1] >= ewk.LHE_WINDOW[0] - 1e-6) & (edges[1:] <= ewk.LHE_WINDOW[1] + 1e-6)

# Cross sections in the LHE window, with the statistical uncertainty from the cell sums of genWeight^2
for label, sums in samples.items():
    scale = sums["scale"]
    sums["sigma_window"] = scale * np.sum(sums["cells"][ewk.WINDOW_CELLS])
    sums["sigma_window_error"] = scale * np.sqrt(np.sum(sums["cells_w2"][ewk.WINDOW_CELLS]))
    sums["sigma_window_R"] = scale * np.sum(sums["mll_R"][in_window])
    # Both are sum(genWeight) over 105 <= LHE mll < 160 (1 GeV bins aligned with the window): must agree
    from_mll = scale * np.sum(sums["mll"][in_window])
    if abs(from_mll - sums["sigma_window"]) > 1e-6 * max(abs(from_mll), 1e-12):
        print(f"[WARNING] {label}: sigma in the window from the mll histogram ({from_mll:.6g} pb) != from the "
              f"stitching cells ({sums['sigma_window']:.6g} pb)")

window_label = f"LHE m_mumu {ewk.LHE_WINDOW[0]:.0f}-{ewk.LHE_WINDOW[1]:.0f}"
ref = samples[reference]
lines = [f"EWK Z+2j generator-level cross sections, era {era} (analyzer v{args.analyzer_version.lstrip('v')}, "
         f"cross sections from lib/Run3Constants.h, stat. uncertainties only)",
         f"{'sample':<10}{'sigma [pb]':>12}{'sum genWeight':>16}"
         f"{'sigma(' + window_label + ') [pb]':>36}{'fraction':>10}{'  + gen mjj>300 [pb]':>22}"
         f"{'ratio to ' + reference:>26}"]
for label, sums in samples.items():
    ratio, ratio_error = weighted_ratio(np.array([sums["sigma_window"]]), np.array([sums["sigma_window_error"] ** 2]),
                                        np.array([ref["sigma_window"]]), np.array([ref["sigma_window_error"] ** 2]))
    if label == reference:
        ratio_error = np.array([0.0])
    lines.append(f"{label:<10}{sums['sigma']:>12.5g}{sums['total']:>16.6g}"
                 f"{sums['sigma_window']:>24.5g} +- {sums['sigma_window_error']:<8.2g}"
                 f"{sums['sigma_window'] / sums['sigma']:>10.4f}{sums['sigma_window_R']:>22.5g}"
                 f"{ratio[0]:>18.4f} +- {ratio_error[0]:.4f}")
lines.append("")
for label, sums in samples.items():
    lines.append(f"{label}: {', '.join(sums['datasets'])}; generator cuts: "
                 + ewk.GENERATOR_CUTS[label].replace("$", "").replace("\\mu", "mu").replace("\\ell", "l"))
lines.append(f"{'H7 2L2J'} is only comparable to the 2Mu2J samples in the window (it also has ee and tautau); "
             "P8 2Mu2J has M2J > 120 at generator level, H7 2Mu2J only the mass window")

output_directory = f"../plots/EWK_comparison/{era}/genlevel/"
os.makedirs(output_directory, exist_ok=True)
table_path = output_directory + f"xs_table_{era}.txt"
with open(table_path, "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
print(f"\nTable written to {table_path}")

plt.style.use(hep.style.CMS)
colors = get_color_list(len(samples))


def draw(key, file_name, title):
    """d(sigma)/bin of LHE mumu mll for every sample (histogram `key`), with the ratio to the reference.
    The mll histograms are filled without sum w^2, so no per-bin uncertainty is drawn."""
    fig, (ax, ratio_ax) = get_canvas(draw_ratio=True)
    curves = {label: sums[key] * sums["scale"] for label, sums in samples.items()}
    zeros = np.zeros(len(edges) - 1)
    for (label, xs), color in zip(curves.items(), colors):
        hep.histplot(xs, edges, yerr=False, ax=ax, color=color, linewidth=2,
                     label=f"{label}: {ewk.GENERATOR_CUTS[label]}")
        if label != reference:
            ratio, _ = weighted_ratio(xs, zeros, curves[reference], zeros)
            hep.histplot(np.nan_to_num(ratio), edges, yerr=False, ax=ratio_ax, color=color, linewidth=2)
    hep.cms.label(data=False, label="", year=era, com="13.6", ax=ax)
    ax.set_yscale("log")
    ax.set_ylim(top=ax.get_ylim()[1] * 50)
    x_range = (90, 175)
    ax.set_xlim(*x_range)
    ax.set_ylabel(r"$\sigma$ / bin [pb]")
    ax.legend(frameon=False, loc="upper right", fontsize=13, title=title, title_fontsize=13)
    ax.tick_params(labelbottom=False)
    for boundary in ewk.LHE_WINDOW:
        ax.axvline(boundary, color="gray", linestyle=":")
        ratio_ax.axvline(boundary, color="gray", linestyle=":")
    ratio_ax.set_xlim(*x_range)
    ratio_ax.set_ylim(0, 2)
    ratio_ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ratio_ax.set_ylabel(f"/ {reference}")
    ratio_ax.set_xlabel(r"LHE $m_{\mu\mu}$ [GeV]")
    save_figure(fig, output_directory, f"{file_name}_{era}")
    plt.close()


draw("mll", "genmll", "All events")
draw("mll_R", "genmll_R", r"Gen $m_{jj}>300$ GeV (VBF-filter emulation)")
print(f"Plots written to {output_directory}")
