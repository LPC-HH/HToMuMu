#!/usr/bin/env python
# coding: utf-8
"""
Migration matrix: kinematic VBF/ggH channel assignment  vs  categorization-BDT
assignment, for the VBF-signal / ggH-signal / background populations.

Answers the reviewer question behind the categorization-BDT study:
  "The BDT moves events between the ggH and VBF channels -- how many, and is the
   VBF signal it pulls in actually worth anything (S/sqrt(B)), or does it just
   drag background along?"

Inputs: root_io/tuples/<DATASET>_Combined_tuples_categorized.root  (tree_output),
which carry BOTH the kinematic flags (is_VBF_category / is_ggH_category, written
by CreateTuple) and the BDT flags (is_VBF_categoryBDT / is_ggH_categoryBDT,
appended by train_VBF_ggH_BDT.py).

Weight convention: in these upstream tuples the signal `weight` already includes
the H->mumu BR (xs*gen_weight*pu*br*1000/SumGenWeight -- see split_tuples.py
line 108), so sum(weight) in a mass window is directly the expected yield.
"""
from __future__ import annotations

import argparse
import os

import numpy as np
import uproot

TUPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "root_io", "tuples")
SIG = {"VBF": "VBF", "ggH": "ggH"}
BKG = ["DY", "EWK", "TT", "DiBoson"]
BRANCHES = ["weight", "is_VBF_category", "is_ggH_category",
            "is_VBF_categoryBDT", "n_jet"]


def asimov_Z(s, b):
    s, b = np.asarray(s, float), np.asarray(b, float)
    out = np.zeros(np.broadcast(s, b).shape)
    m = (b > 0) & (s > 0)
    out = np.where(m, np.sqrt(np.clip(2 * ((s + b) * np.log1p(s / np.where(b > 0, b, 1)) - s), 0, None)), 0.0)
    return float(out) if out.ndim == 0 else out


def load(name, mass_var, window, njet_sel):
    path = os.path.join(TUPLE_DIR, f"{name}_Combined_tuples_categorized.root")
    a = uproot.open(path)["tree_output"].arrays(BRANCHES + [mass_var], library="np")
    m = (a[mass_var] >= window[0]) & (a[mass_var] <= window[1])
    if njet_sel is not None:
        m &= njet_sel(a["n_jet"])
    w = a["weight"][m]
    kin_vbf = a["is_VBF_category"][m] == 1              # kinematic channel = VBF
    bdt_vbf = a["is_VBF_categoryBDT"][m] == 1           # BDT channel = VBF
    # sanity: kinematic flags should partition
    neither = np.count_nonzero((a["is_VBF_category"][m] == 0) & (a["is_ggH_category"][m] == 0))
    both = np.count_nonzero((a["is_VBF_category"][m] == 1) & (a["is_ggH_category"][m] == 1))
    return w, kin_vbf, bdt_vbf, neither, both


def table_2x2(w, kin_vbf, bdt_vbf):
    """rows = kinematic {ggH, VBF}, cols = BDT {ggH, VBF}; weighted yields."""
    t = np.zeros((2, 2))
    for i, kv in enumerate((False, True)):
        for j, bv in enumerate((False, True)):
            t[i, j] = w[(kin_vbf == kv) & (bdt_vbf == bv)].sum()
    return t  # t[0,1] = migrated INTO VBF ; t[1,0] = migrated OUT of VBF


def fmt_2x2(name, t):
    tot = t.sum()
    lines = [f"  {name}",
             f"                 BDT->ggH     BDT->VBF   |     row sum",
             f"    kin->ggH   {t[0,0]:10.3f}   {t[0,1]:10.3f}   | {t[0].sum():10.3f}",
             f"    kin->VBF   {t[1,0]:10.3f}   {t[1,1]:10.3f}   | {t[1].sum():10.3f}",
             f"    col sum    {t[:,0].sum():10.3f}   {t[:,1].sum():10.3f}   | {tot:10.3f}"]
    if tot > 0:
        lines.append(f"    (migrated INTO VBF = {t[0,1]:.3f} = {100*t[0,1]/tot:.2f}% ; "
                     f"OUT of VBF = {t[1,0]:.3f} = {100*t[1,0]/tot:.2f}%)")
    return "\n".join(lines)


def run(mass_var, window, njet_sel, tag):
    print(f"\n{'='*78}\n{tag}   window {window} on {mass_var}\n{'='*78}")

    wV, kvV, bvV, nV, bV = load(SIG["VBF"], mass_var, window, njet_sel)
    wG, kvG, bvG, nG, bG = load(SIG["ggH"], mass_var, window, njet_sel)
    wB_list = [load(n, mass_var, window, njet_sel) for n in BKG]
    wB = np.concatenate([x[0] for x in wB_list])
    kvB = np.concatenate([x[1] for x in wB_list])
    bvB = np.concatenate([x[2] for x in wB_list])

    if nV + nG:
        print(f"  [note] events failing BOTH kinematic flags: "
              f"VBFsig={nV}, ggHsig={nG} -- treated as kin->ggH")

    tV, tG, tB = (table_2x2(wV, kvV, bvV),
                  table_2x2(wG, kvG, bvG),
                  table_2x2(wB, kvB, bvB))

    print("\n--- MIGRATION TABLES (expected weighted yields) ---\n")
    print(fmt_2x2("VBF signal", tV)); print()
    print(fmt_2x2("ggH signal", tG)); print()
    print(fmt_2x2("Background (DY+EWK+TT+DiBoson)", tB))

    # --- the four migration populations, with physics content ---
    print("\n--- MIGRATION POPULATIONS: what is in each corner ---\n")
    hdr = f"  {'population':16s} {'S_VBF':>9s} {'S_ggH':>9s} {'S_tot':>9s} {'B':>11s} {'S/sqrtB':>9s} {'Z_Asimov':>9s}"
    print(hdr); print("  " + "-" * (len(hdr) - 2))
    corners = [("stable VBF",   (1, 1)),
               ("migrated IN",  (0, 1)),
               ("migrated OUT",  (1, 0)),
               ("stable ggH",   (0, 0))]
    for label, (i, j) in corners:
        sV, sG, b = tV[i, j], tG[i, j], tB[i, j]
        s = sV + sG
        soverb = s / np.sqrt(b) if b > 0 else float("nan")
        print(f"  {label:16s} {sV:9.3f} {sG:9.3f} {s:9.3f} {b:11.3f} {soverb:9.3f} {asimov_Z(s, b):9.4f}")

    # --- net: kinematic categories vs BDT categories ---
    print("\n--- NET: two-category significance, kinematic vs BDT split ---\n")
    print(f"  {'scheme':18s} {'S_tot':>9s} {'B':>12s} {'S/sqrtB':>9s} {'Z_Asimov':>9s}")
    print("  " + "-" * 60)

    def cat_row(label, s, b):
        print(f"  {label:18s} {s:9.3f} {b:12.3f} {s/np.sqrt(b) if b>0 else float('nan'):9.3f} {asimov_Z(s, b):9.4f}")
        return asimov_Z(s, b)

    # kinematic: VBF = row 1, ggH = row 0
    zk_v = cat_row("kinematic VBF", tV[1].sum() + tG[1].sum(), tB[1].sum())
    zk_g = cat_row("kinematic ggH", tV[0].sum() + tG[0].sum(), tB[0].sum())
    print(f"  {'kinematic COMBINED':18s} {'':9s} {'':12s} {'':9s} {np.hypot(zk_v, zk_g):9.4f}")
    # BDT: VBF = col 1, ggH = col 0
    zb_v = cat_row("BDT VBF", tV[:, 1].sum() + tG[:, 1].sum(), tB[:, 1].sum())
    zb_g = cat_row("BDT ggH", tV[:, 0].sum() + tG[:, 0].sum(), tB[:, 0].sum())
    print(f"  {'BDT COMBINED':18s} {'':9s} {'':12s} {'':9s} {np.hypot(zb_v, zb_g):9.4f}")

    dZ = np.hypot(zb_v, zb_g) - np.hypot(zk_v, zk_g)
    print(f"\n  >>> delta Z (BDT - kinematic, this 2-cat toy) = {dZ:+.4f} sigma")
    print(f"      (compare to ~0.1 sigma binning/method noise on the full fit)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mass-var", default="diMuon_bsConstrainedMass",
                    choices=["diMuon_bsConstrainedMass", "diMuon_mass"])
    ap.add_argument("--window", type=float, nargs=2, default=(121.0, 129.0))
    ap.add_argument("--by-njet", action="store_true",
                    help="also break down into n_jet == 1 and n_jet >= 2")
    args = ap.parse_args(argv)
    w = tuple(args.window)

    run(args.mass_var, w, None, "ALL n_jet")
    if args.by_njet:
        run(args.mass_var, w, lambda n: n == 1, "n_jet == 1 (only the BDT can promote these to VBF)")
        run(args.mass_var, w, lambda n: n >= 2, "n_jet >= 2")


if __name__ == "__main__":
    main()
