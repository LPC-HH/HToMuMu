"""
Computes the per-era normalisation and stitching fractions of the all-aMC@NLO (FxFx) DY background:
    J_p : DYto2{L,Mu}-2Jets MLL-50, p = 0J/1J/2J, binned in the Born parton multiplicity (LHE_NpNLO).
          Disjoint, so outside W they are simply added (weight 1).
    U   : DYto2Mu-2Jets_105to160 (+ ext1), only inside W
    F   : DYto2Mu-2Jets_105to160_VBFFilter, only inside W where the emulated VBF filter passes (R)
with W = {LHE mumu mll in [105, 160)}. The cells (lib/DYStitching.h, hardcoded below) are
    0          : outside W or not a mumu event                -> J_p only (fraction 1)
    1 + 2p + R : inside W, p = 0..2, R = emulated filter pass -> J_p, U and (R = 1) F combined
    7          : inside W with p outside 0..2 (empty for FxFx) -> U only
Inside W the samples covering a cell c are combined with effective-luminosity fractions
    f_ic = Leff_ic / sum_j Leff_jc,   Leff_ic = Neff_ic / sigma_ic,   Neff = (sum w)^2 / sum w^2,
i.e. the inverse-variance combination; the prediction does not depend on the fractions as long as they
sum to 1, and samples with more negative weights (2J) get a smaller share.

Normalisation: sigma_Jp from lib/Run3Constants.h. U is matched to J in W:
    sigma_U = sum_p sigma_Jp * sumw(J_p in W) / sumw(J_p)
so that both predict the same cross section in every cell and there is no step at 105/160 GeV.
sigma_F = sigma_U * eps_F, with eps_F the GenFilter efficiency (default) or the in-situ one (--insitu).
F is normalised with sumw over ALL its events (those outside R are dropped by CreateTuple).

Needs SumGenWeight.root from ComputeWeights.py for all the DY datasets of the era (analyzer >= v2.7, with
h_sumOfgenWeight[2]_stitchCells). Writes one-bin stitch_sigma / stitch_sumw and the 8-bin stitch_frac
histograms into each DY dataset's SumGenWeight.root, read by CreateTuple (DO_DY_STITCHING). Re-run whenever
ComputeWeights.py recreates those files.

--coverage also reads the first N_COVERAGE_FILES analyzer files of each sample and prints how the reco VBF
category (approximated by the jet cuts of CreateTuple::isVBFCategory) is distributed over the cells.

Usage: python3 compute_DY_stitching.py [era|all] [--insitu] [--coverage] [--dry-run]
"""
import glob
import os
import re
import sys

import numpy as np
import uproot

sys.path.append('../condor/utils')
import version as v

ALL_ERAS = ["2022", "2022EE", "2023", "2023BPix", "2024", "2025"]
N_CELLS = 8
CELL_OUTSIDE, CELL_UNKNOWN = 0, 7
N_PARTON_BINS = 3
EXTENSIONS = ["", "_ext1", "_ext2"]


def cell(p, R):
    return 1 + 2 * p + R


def cell_label(c):
    if c == CELL_OUTSIDE:
        return "outside W"
    if c == CELL_UNKNOWN:
        return "W, p unknown"
    return f"W, p={(c - 1) // 2}, R={(c - 1) % 2}"


WINDOW_CELLS = list(range(1, N_CELLS))

args = [a for a in sys.argv[1:] if not a.startswith("--")]
use_insitu = "--insitu" in sys.argv
check_coverage = "--coverage" in sys.argv
dry_run = "--dry-run" in sys.argv
N_COVERAGE_FILES = 15
era_arg = args[0] if args else "all"
if era_arg != "all" and era_arg not in ALL_ERAS:
    print(f"Invalid era '{era_arg}'. Allowed: all, " + ", ".join(ALL_ERAS))
    exit(1)
eras = ALL_ERAS if era_arg == "all" else [era_arg]

user = os.getenv('LOGNAME')
# DY_STITCH_EOS_PATH overrides the analyzer output directory (e.g. for tests on a local copy)
EOS_PATH = os.getenv("DY_STITCH_EOS_PATH", "/eos/uscms/store/group/lpchmumu/" + user + "/analyzer_HiggsMuMu_"
                     + v.ANALYZER_VERSION_NUMBER + "/MC_background")


def read_cross_sections():
    """CROSS_SECTION map from lib/Run3Constants.h, so the numbers are not duplicated here"""
    with open("../lib/Run3Constants.h") as f:
        text = f.read()
    block = text[text.index("CROSS_SECTION"):]
    block = block[:block.index("};")]
    return {name: float(value) for name, value in re.findall(r'\{\s*"([^"]+)"\s*,\s*([0-9.eE+-]+)\s*\}', block)}


def read_sums(dataset):
    """Pre-selection sums of genWeight of one dataset: total, per cell, per cell of genWeight^2, GenFilter counts"""
    path = f"{EOS_PATH}/{dataset}/SumGenWeight.root"
    if not os.path.exists(path):
        return None
    with uproot.open(path) as f:
        for name in ["h_sumOfgenWeight_stitchCells", "h_sumOfgenWeight2_stitchCells"]:
            if name not in f:
                print(f"[ERROR] {name} missing in {path}. Re-run the analyzer (>= v2.7) and ComputeWeights.py")
                exit(1)
        return {
            "datasets": [dataset],
            "total": f["h_sumOfgenWeight"].values()[0],
            "cells": f["h_sumOfgenWeight_stitchCells"].values().astype(np.float64),
            "cells_w2": f["h_sumOfgenWeight2_stitchCells"].values().astype(np.float64),
            "genFilter": f["h_genFilter_counts"].values() if "h_genFilter_counts" in f else None,
        }


def read_sample(base, campaign):
    """Sums of a sample combined over its extensions (they are hadded later, so they share one normalisation)"""
    combined = None
    for ext in EXTENSIONS:
        sums = read_sums(f"{base}_{campaign}{ext}")
        if sums is None:
            continue
        if combined is None:
            combined = sums
        else:
            combined["datasets"] += sums["datasets"]
            for key in ["total", "cells", "cells_w2"]:
                combined[key] = combined[key] + sums[key]
    return combined


def neff(sums, c):
    s, s2 = sums["cells"][c], sums["cells_w2"][c]
    return s * s / s2 if s > 0 and s2 > 0 else 0.0


def vbf_category_cells(dataset):
    """sum(genWeight) of the (approximate) reco VBF category per cell, from the first N_COVERAGE_FILES files"""
    import awkward as ak
    import vector
    vector.register_awkward()

    files = sorted(glob.glob(f"{EOS_PATH}/{dataset}/HiggsMuMu_*.root"))[:N_COVERAGE_FILES]
    if not files:
        return None
    branches = ["t_genWeight", "t_pass_VBF_filter", "t_LHE_mll", "t_LHE_NpNLO", "leadJet_idx", "subleadJet_idx",
                "t_Jet_pt", "t_Jet_eta", "t_Jet_phi", "t_Jet_mass"]
    a = ak.concatenate([uproot.open(f)["tree"].arrays(branches) for f in files])

    def jet(index):
        pick = lambda x: ak.firsts(x[ak.local_index(x) == index])
        return vector.zip({"pt": pick(a.t_Jet_pt), "eta": pick(a.t_Jet_eta),
                           "phi": pick(a.t_Jet_phi), "mass": pick(a.t_Jet_mass)})
    jet1, jet2 = jet(a.leadJet_idx), jet(a.subleadJet_idx)
    vbf = ((ak.fill_none(jet1.pt, -1) > 35) & (ak.fill_none(jet2.pt, -1) > 25) &
           (ak.fill_none((jet1 + jet2).mass, -1) >= 400) & (ak.fill_none(abs(jet1.eta - jet2.eta), -1) > 2.5))
    mll, p, R = (ak.to_numpy(a[b]) for b in ["t_LHE_mll", "t_LHE_NpNLO", "t_pass_VBF_filter"])
    in_W = (mll >= 105) & (mll < 160)
    cells = np.where(in_W, np.where((p >= 0) & (p < N_PARTON_BINS), 1 + 2 * p + R, CELL_UNKNOWN), CELL_OUTSIDE)
    w = ak.to_numpy(a.t_genWeight)[ak.to_numpy(vbf)]
    return np.bincount(cells[ak.to_numpy(vbf)], weights=w, minlength=N_CELLS)


def add_stitch_values(dataset, values):
    """Rewrites the dataset's SumGenWeight.root with the stitch_* histograms added (EOS fuse does not
    support uproot.update, so the existing histograms are read and written back)"""
    path = f"{EOS_PATH}/{dataset}/SumGenWeight.root"
    if dry_run:
        return
    with uproot.open(path) as f:
        existing = {key.split(";")[0]: f[key] for key in f.keys(cycle=False) if not key.startswith("stitch_")}
    with uproot.recreate(path) as f:
        for name, hist in existing.items():
            f[name] = hist
        for name, value in values.items():
            value = np.atleast_1d(np.asarray(value, dtype=np.float64))
            f["stitch_" + name] = (value, np.arange(len(value) + 1, dtype=np.float64))
    print(f"  stitch_* histograms written to {path}")


cross_sections = read_cross_sections()

for era in eras:
    campaign = "Summer" + era[2:]
    print(f"\n################ Era {era} ################")

    # 2022-2023 have the jet-binned samples only as DYto2L (ee + mumu + tautau)
    prefix = "DYto2Mu-2Jets" if era in ["2024", "2025"] else "DYto2L-2Jets"
    samples = {f"J{p}": read_sample(f"{prefix}_{p}J", campaign) for p in range(N_PARTON_BINS)}
    samples["U"] = read_sample("DYto2Mu-2Jets_105to160", campaign)
    samples["F"] = read_sample("DYto2Mu-2Jets_105to160_VBFFilter", campaign)
    missing = [name for name, sums in samples.items() if sums is None]
    if missing:
        print(f"[ERROR] Missing SumGenWeight.root for {missing} in {EOS_PATH}, skipping {era}")
        continue

    # ---- Cross sections ----
    sigma = {}
    for p in range(N_PARTON_BINS):
        sigma[f"J{p}"] = cross_sections[f"{prefix}_{p}J"]
    sigma_W_J = sum(sigma[f"J{p}"] * samples[f"J{p}"]["cells"][WINDOW_CELLS].sum() / samples[f"J{p}"]["total"]
                    for p in range(N_PARTON_BINS))
    U, F = samples["U"], samples["F"]
    U_frac_W = U["cells"][WINDOW_CELLS].sum() / U["total"]
    sigma["U"] = sigma_W_J / U_frac_W
    print(f"J: sigma in W = {sigma_W_J:.4f} pb (McM sigma of the 105to160 sample: "
          f"{cross_sections['DYto2Mu-2Jets_105to160']} pb, ratio {sigma_W_J / cross_sections['DYto2Mu-2Jets_105to160']:.4f})")
    print(f"U: fraction of sum(genWeight) in W: {U_frac_W:.5f} (should be 1)")
    if abs(U_frac_W - 1) > 0.01:
        print("[WARNING] U is not contained in W: check the LHE info (t_LHE_mll) of the U sample")

    f_emul = F["cells"][[cell(p, 1) for p in range(N_PARTON_BINS)]].sum() / F["total"]
    eps_genFilter = None
    if F["genFilter"] is not None and F["genFilter"][1] > 0:
        eps_genFilter = F["genFilter"][0] / F["genFilter"][1]
    eps_insitu = (U["cells"][[cell(p, 1) for p in range(N_PARTON_BINS)]].sum() / U["total"]) / f_emul
    print(f"F: fraction passing the filter emulation (f_emul): {f_emul:.5f}")
    print(f"eps_F: GenFilter {eps_genFilter}, in-situ (U fraction in R / f_emul) {eps_insitu:.5f}"
          + (f", in-situ / GenFilter {eps_insitu / eps_genFilter:.4f}" if eps_genFilter else ""))
    if use_insitu:
        eps_F = eps_insitu
    else:
        if eps_genFilter is None:
            print("[ERROR] No GenFilter info for F, use --insitu. Skipping")
            continue
        eps_F = eps_genFilter
    sigma["F"] = sigma["U"] * eps_F
    print("sigma [pb]: " + ", ".join(f"{name} {value:.4f}" for name, value in sigma.items()))

    # ---- Coverage and fractions ----
    covers = {f"J{p}": [cell(p, 0), cell(p, 1)] for p in range(N_PARTON_BINS)}
    covers["U"] = WINDOW_CELLS
    covers["F"] = [cell(p, 1) for p in range(N_PARTON_BINS)]

    leff = {name: np.zeros(N_CELLS) for name in samples}
    sigma_cell = {name: np.zeros(N_CELLS) for name in samples}
    for name, sums in samples.items():
        for c in covers[name]:
            sigma_cell[name][c] = sigma[name] * sums["cells"][c] / sums["total"]
            if sigma_cell[name][c] > 0:
                leff[name][c] = neff(sums, c) / sigma_cell[name][c]
    total_leff = sum(leff.values())
    frac = {name: np.zeros(N_CELLS) for name in samples}
    for name in samples:
        frac[name] = np.divide(leff[name], total_leff, out=np.zeros(N_CELLS), where=total_leff > 0)
    # Outside W only J_p (disjoint): weight 1. U/F events outside W cannot exist (generator cut) and are dropped.
    for p in range(N_PARTON_BINS):
        frac[f"J{p}"][CELL_OUTSIDE] = 1.0
    frac["U"][CELL_UNKNOWN] = 1.0

    names = list(samples)
    print(f"\n{'cell':<16}{'sigma(J) pb':>12}{'sigma(U) pb':>12}{'sigma(F) pb':>12}"
          + "".join(f"{'Leff ' + n:>11}" for n in names) + "".join(f"{'f ' + n:>8}" for n in names))
    for c in range(N_CELLS):
        sigma_J = sum(sigma_cell[f"J{p}"][c] for p in range(N_PARTON_BINS))
        print(f"{cell_label(c):<16}{sigma_J:12.4f}{sigma_cell['U'][c]:12.4f}{sigma_cell['F'][c]:12.4f}"
              + "".join(f"{leff[n][c] / 1000:11.1f}" for n in names) + "".join(f"{frac[n][c]:8.4f}" for n in names))
    print("(Leff in fb^-1; inside W the sigma columns must agree within the MC statistics)")
    for c in WINDOW_CELLS:
        covered = sum(frac[n][c] for n in names)
        if c != CELL_UNKNOWN and abs(covered - 1) > 1e-6 and U["cells"][c] != 0:
            print(f"[WARNING] fractions in cell {cell_label(c)} sum to {covered}")

    if check_coverage:
        print(f"\nReco VBF category per cell (first {N_COVERAGE_FILES} files per sample, sum(genWeight) fractions):")
        for name in names:
            per_cell = vbf_category_cells(samples[name]["datasets"][0])
            if per_cell is not None and per_cell.sum() != 0:
                print(f"  {name:<3}" + "".join(f"{x:8.3f}" for x in per_cell / per_cell.sum()))

    for name, sums in samples.items():
        values = {"sigma": sigma[name], "sumw": sums["total"], "frac": frac[name], "eps_F": eps_F}
        for dataset in sums["datasets"]:
            add_stitch_values(dataset, values)
