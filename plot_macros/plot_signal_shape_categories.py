"""Signal mass shape per BDT category: beam-spot-constrained mass vs BSC + FSR recovery, each with a DCB fit.
    python3 plot_signal_shape_categories.py ggH|VBF [--variant asimovFit_flatMassRes] [--era Combined]
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import uproot as ur

from plot_effective_sigma import category_intervals, validate_cuts
from utils import fsr_validation as fv
from utils.colors import get_color_list
from utils.helper import get_canvas, save_figure

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))
from bdt_categories_io import get_bdt_cuts, load_bdt_categories, variant_dir_suffix  # noqa: E402

TREE_NAME = "tree_output"
WEIGHT_BRANCH = "weight"
MASS_BSC = "diMuon_bsConstrainedMass"
MASS_FSR = "diMuon_bsConstrainedMass_FSR"
# Category boundaries were optimised on the BSC mass (the only key plot_BDT_Categories.py writes for these variants).
CUTS_MASS_KEY = "diMuon_bsConstrainedMass"
BASE_DIR = Path("../root_io/tuples/BDT_score")
OUTPUT_BASE = Path("../plots/signal_shape_categories")
SIGNAL_FILE_NAME = "signal_Combined.root"
UPROOT_OPEN = dict(file_handler=ur.MultithreadedFileSource)

BSC_STYLE = dict(fv.NOMINAL_STYLE, label="BSC")
FSR_STYLE = dict(fv.FSR_STYLE, label="BSC + FSR")
MASSES = ((MASS_BSC, "BSC"), (MASS_FSR, "BSC+FSR"))


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("channel", choices=["ggH", "VBF"], help="BDT categorisation")
    p.add_argument("--variant", default="asimovFit_flatMassRes",
                   help="train.py variant label of the BDT scores ('base' for BDT_score/<channel>/)")
    p.add_argument("--era", default="Combined")
    p.add_argument("--subset", default="BFull_SNottH")
    p.add_argument("--fit-range", nargs=2, type=float, default=(115.0, 135.0), metavar=("LO", "HI"))
    p.add_argument("--hist-range", nargs=2, type=float, default=(110.0, 140.0), metavar=("LO", "HI"))
    p.add_argument("--bin-width", type=float, default=0.25)
    p.add_argument("--no-sigma-eff", action="store_true",
                   help="do not draw the sigma_eff interval on the per-category plots (it is still in the CSV)")
    p.add_argument("--step-size", default="500 MB")
    return p.parse_args()


def load(path: Path, channel: str, step_size: str):
    """Return (BSC mass, FSR mass, BDT score, weight) for events in the channel's categorisation."""
    if "data" in path.name.lower():
        raise RuntimeError(f"Refusing to open {path}: this macro is signal-MC only (blinding).")
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")
    bdt, cat = f"BDT_{channel}", f"is_{channel}_category"
    branches = [MASS_BSC, MASS_FSR, bdt, cat, WEIGHT_BRANCH]
    with ur.open(path, **UPROOT_OPEN) as f:
        missing = [b for b in branches if b not in f[TREE_NAME].keys()]
    if missing:
        raise KeyError(f"{path} is missing {missing}; it must be scored from FSR-recovery tuples.")

    out = {k: [] for k in ("m", "m_fsr", "bdt", "w")}
    for a in ur.iterate(f"{path}:{TREE_NAME}", expressions=branches, library="np", step_size=step_size,
                        **UPROOT_OPEN):
        m, m_fsr = np.asarray(a[MASS_BSC], float), np.asarray(a[MASS_FSR], float)
        w = np.asarray(a[WEIGHT_BRANCH], float)
        sel = (np.asarray(a[cat]) == 1) & np.isfinite(m) & np.isfinite(m_fsr) & np.isfinite(w)
        out["m"].append(m[sel])
        out["m_fsr"].append(m_fsr[sel])
        out["bdt"].append(np.asarray(a[bdt], float)[sel])
        out["w"].append(w[sel])
    return tuple(np.concatenate(out[k]) for k in ("m", "m_fsr", "bdt", "w"))


def category_masks(bdt, cuts):
    """[(name, title, lo, hi, mask)], inclusive first, then cat1 (highest BDT) ... catN."""
    masks = [("inclusive", "inclusive", np.nan, np.nan, np.ones(bdt.size, bool))]
    finite = np.isfinite(bdt)
    for i, lo, hi, incl_hi in category_intervals(cuts):
        m = finite & (bdt >= lo) & ((bdt <= hi) if incl_hi else (bdt < hi))
        upper = r"$\leq$" if incl_hi else "<"
        masks.append((f"cat{i}", rf"cat{i}: {lo:.3f} $\leq$ BDT {upper} {hi:.3f}", lo, hi, m))
    return masks


def summary_row(channel, name, lo, hi, mass_label, values, w, fit):
    row = dict(channel=channel, category=name, bdt_low=lo, bdt_high=hi, mass=mass_label,
               sum_weight=float(np.sum(w)), n_raw=int(values.size),
               sigma_eff=fv.sigma_eff(values, w))  # same (unbinned, all values) as the plot text
    keys = ("mu", "mu_err", "sigma", "sigma_err", "aL", "nL", "aR", "nR", "chi2ndf")
    if fit is None:
        row.update({k: np.nan for k in keys})
    else:
        row.update({k: fit[k] for k in ("mu", "mu_err", "sigma", "sigma_err", "chi2ndf")})
        row.update(dict(zip(("aL", "nL", "aR", "nR"), map(float, fit["params"][3:]))))
    return row


def plot_vs_category(rows, channel, era, outdir):
    cats = [r["category"] for r in rows if r["mass"] == "BSC" and r["category"] != "inclusive"]
    x = np.arange(len(cats))
    plt.style.use(hep.style.CMS)
    fig, axs = plt.subplots(2, 1, sharex=True, height_ratios=[1, 1])
    fig.subplots_adjust(hspace=0.08)
    for (_, label), style, dx in zip(MASSES, (BSC_STYLE, FSR_STYLE), (-0.08, 0.08)):
        r = {q["category"]: q for q in rows if q["mass"] == label}
        axs[0].errorbar(x + dx, [r[c]["sigma"] for c in cats], yerr=[r[c]["sigma_err"] for c in cats],
                        fmt="o", color=style["color"], label=style["label"])
        axs[1].plot(x + dx, [r[c]["sigma_eff"] for c in cats], "s", color=style["color"], label=style["label"])
        for ax, key in ((axs[0], "sigma"), (axs[1], "sigma_eff")):
            ax.axhline(r["inclusive"][key], color=style["color"], ls=":", lw=1.2)
    axs[0].set_ylabel(r"DCB $\sigma$ [GeV]")
    axs[1].set_ylabel(r"$\sigma_{eff}$ [GeV]")
    axs[1].set_xticks(x, cats)
    axs[1].set_xlabel(f"{channel} BDT category")
    axs[0].text(0.97, 0.95, "cat1 = highest BDT\ndotted = inclusive", transform=axs[0].transAxes,
                ha="right", va="top", fontsize=14)
    axs[0].legend(fontsize=15)
    fv.cms_label(axs[0], era, is_data=False)
    save_figure(fig, f"{outdir}/", f"{channel}_dcb_vs_category")
    plt.close(fig)


def plot_all_categories(cat_masks, values, w, edges, channel, era, outdir, mass_label, name):
    cats = [c for c in cat_masks if c[0] != "inclusive"]
    plt.style.use(hep.style.CMS)
    fig, ax = get_canvas()
    for (cname, _, lo, hi, mask), color in zip(cats, get_color_list(len(cats))):
        h, e = fv.whist(values[mask], w[mask], edges, density=True)
        hep.histplot(h, edges, yerr=e, ax=ax, histtype="step", lw=1.6, color=color, flow=None,
                     label=f"{cname} [{lo:.2f}, {hi:.2f}]")
    ax.set_xlim(edges[0], edges[-1])
    ax.set_xlabel(f"$m_{{\\mu\\mu}}$ ({mass_label}) [GeV]")
    ax.set_ylabel("Normalized to unit area")
    ax.legend(fontsize=14, title=f"{channel} categories", title_fontsize=14)
    fv.cms_label(ax, era, is_data=False)
    save_figure(fig, f"{outdir}/", name)
    plt.close(fig)


def main():
    args = parse_args()
    suffix = variant_dir_suffix(args.variant)
    sample = args.channel + suffix
    path = BASE_DIR / sample / args.subset / SIGNAL_FILE_NAME
    cuts = validate_cuts(get_bdt_cuts(load_bdt_categories(), sample, args.era, args.subset, CUTS_MASS_KEY), sample)
    outdir = OUTPUT_BASE / sample
    fit_range = tuple(args.fit_range)
    lo, hi = args.hist_range
    edges = np.linspace(lo, hi, int(round((hi - lo) / args.bin_width)) + 1)

    print(f"[Info] input {path}\n[Info] {sample} BDT boundaries {list(cuts)}")
    m, m_fsr, bdt, w = load(path, args.channel, args.step_size)
    print(f"[Info] {m.size} signal events in the {args.channel} categorisation, sum(w) = {w.sum():.3f}")

    cat_masks = category_masks(bdt, cuts)
    rows = []
    for name, title, blo, bhi, mask in cat_masks:
        series = [(m[mask], w[mask], BSC_STYLE, False), (m_fsr[mask], w[mask], FSR_STYLE, False)]
        fits = fv.overlay(series, edges, r"$m_{\mu\mu}$ [GeV]", f"{outdir}/", f"{args.channel}_{name}", args.era,
                          title=f"{args.channel} {title}", density=True, ratio_label="FSR / BSC",
                          fit_range=fit_range, sigma_eff_band=not args.no_sigma_eff)
        for (_, label), (vals, ww, _, _), fit in zip(MASSES, series, fits):
            rows.append(summary_row(args.channel, name, blo, bhi, label, vals, ww, fit))
            r = rows[-1]
            print(f"  {name:9s} {label:8s} sumw={r['sum_weight']:9.3f}  mu={r['mu']:.3f}  sigma={r['sigma']:.3f}"
                  f"  sigma_eff={r['sigma_eff']:.3f}  chi2/ndf={r['chi2ndf']:.2f}")
    cat_sumw = sum(r["sum_weight"] for r in rows if r["mass"] == "BSC" and r["category"] != "inclusive")
    print(f"[Check] sum(w) over categories {cat_sumw:.3f} vs inclusive {rows[0]['sum_weight']:.3f}")

    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / f"summary_{args.channel}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"[Info] wrote {outdir / f'summary_{args.channel}.csv'}")

    plot_vs_category(rows, args.channel, args.era, outdir)
    for values, label, tag in ((m, "BSC", "BSC"), (m_fsr, "BSC + FSR", "FSR")):
        plot_all_categories(cat_masks, values, w, edges, args.channel, args.era, outdir, label,
                            f"{args.channel}_shapes_all_categories_{tag}")


if __name__ == "__main__":
    main()
