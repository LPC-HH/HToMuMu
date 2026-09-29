#!/usr/bin/env python3
"""End-to-end pyhf expected-significance cross-check for H->mumu.

Reads the BDT-category-split tuples, fits a parametric signal peak and a
background model (sideband analytic fit and/or MC template), builds a pyhf
workspace, and prints + saves the per-category and combined expected discovery
significance.

Run from the repo root, inside the venv:

    source python/fits/.venv/bin/activate
    python -m python.fits.run_pyhf_fits --background both --channels all

Outputs land in python/fits/outputs/.
"""

from __future__ import annotations

import argparse
import json
import os

import numpy as np

from . import fit_config as cfg
from . import fit_inputs, signal_model, background_model, workspace, significance


def _write_table(rows, path):
    keys = ["category", "s", "b", "s_over_sqrtb", "asimov_Z", "mu_hat", "q0",
            "Z", "p0"]
    with open(path, "w") as fh:
        fh.write(",".join(keys) + "\n")
        for r in rows:
            fh.write(",".join(f"{r.get(k, ''):.6g}" if isinstance(r.get(k), float)
                              else str(r.get(k, "")) for k in keys) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--channels", default="all",
                    choices=["all", "ggH", "VBF"],
                    help="which BDT channel's categories to fit")
    ap.add_argument("--background", default="both",
                    choices=["sideband", "mc", "both"])
    ap.add_argument("--bin-width", type=float, default=cfg.BIN_WIDTH)
    ap.add_argument("--outdir", default=cfg.OUTPUT_DIR)
    ap.add_argument("--save-workspace", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    os.makedirs(args.outdir, exist_ok=True)
    edges = cfg.mass_bins(args.bin_width)

    cats = cfg.resolve_categories(args.channels)
    if not cats:
        raise SystemExit(
            "No categories discovered -- are the split tuples present and "
            "fully written? Checked:\n"
            f"  {cfg.SIG_GGH_FILE}\n  {cfg.SIG_VBF_FILE}\n  {cfg.DATA_FILE}"
        )
    print(f"discovered categories: {cats}")

    print(f"[1/5] loading signal MC + (blinded) data for {len(cats)} categories …")
    inputs = fit_inputs.load_signal(cats)
    print(fit_inputs.summary_table(inputs))

    print("\n[2/5] fitting parametric signal peak per category …")
    signals = signal_model.fit_all_signals(inputs, edges=edges, verbose=args.verbose)
    for c, sh in signals.items():
        print(f"  {c:10s} {sh.family:9s} mean={sh.mean:7.3f} "
              f"sigma_eff={sh.sigma_eff:5.3f} yield={sh.yield_total:8.2f} "
              f"chi2/ndf={sh.chi2ndf:5.2f}")

    need_mc = args.background in ("mc", "both")
    if need_mc:
        print("\n[2b/5] loading MC background (DY/EWK/TT/DiBoson) — this reads the "
              "multi-GB upstream tuples …")
        fit_inputs.load_mc_background(inputs)

    results = {}
    for method in (["sideband", "mc"] if args.background == "both" else [args.background]):
        print(f"\n[3/5] building background model: {method}")
        bkgs = {}
        for c, ci in inputs.items():
            if method == "sideband":
                bkgs[c] = background_model.fit_sideband_background(
                    ci, edges=edges, verbose=args.verbose)
                info = bkgs[c].info
                print(f"  {c:10s} family={info['family']:6s} "
                      f"chi2/ndf={info['chi2ndf']:5.2f} "
                      f"B={bkgs[c].yield_total:10.1f}")
            else:
                bkgs[c] = background_model.mc_template_background(ci, edges=edges)
                print(f"  {c:10s} B={bkgs[c].yield_total:10.1f} "
                      f"(MC entries {bkgs[c].info['mc_entries']})")

        print(f"\n[4/5] building pyhf workspace + fitting ({method}) …")
        spec = workspace.build_spec(signals, bkgs, categories=cats)
        if args.save_workspace:
            wpath = os.path.join(args.outdir, f"workspace_{method}_{args.channels}.json")
            with open(wpath, "w") as fh:
                json.dump(spec, fh, indent=1)
            print(f"  wrote {wpath}")

        rows = significance.significance_table(
            spec, categories=cats, edges=edges, verbose=True)
        results[method] = rows
        _write_table(rows, os.path.join(
            args.outdir, f"significance_{method}_{args.channels}.csv"))

    print("\n[5/5] summary — expected discovery significance (Asimov, mu=1)")
    combined = {m: [r for r in rows if r["category"] == "combined"][0]["Z"]
                for m, rows in results.items()}
    for m, z in combined.items():
        print(f"  {m:10s}  combined Z = {z:.3f} sigma")
    print("\n  (Combine reference, Tutorials/…Combine Sig and Impact.md: "
          "Run3 ggH+VBF ~3.1 sigma for 2022–2024, ~4.8 sigma incl. 2025)")

    with open(os.path.join(args.outdir, f"significance_{args.channels}.json"), "w") as fh:
        json.dump(results, fh, indent=1)


if __name__ == "__main__":
    main()
