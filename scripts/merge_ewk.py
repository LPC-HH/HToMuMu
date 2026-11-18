#!/usr/bin/env python3
"""
Merge the EWK Z+2j Herwig7 (EWK_2Mu2J, the nominal "EWK") and Pythia8 (EWK_2Mu2J_pythia, "EWK_pythia")
tuples into EWK_merged_<era>_tuples.root, used to train the BDT

CreateTuple normalises each sample to the full sigma x lumi on its own, so a plain hadd would double the EWK
yield. Per MC campaign c (era), the weights are scaled by
    Herwig: f_c      Pythia: 1 - f_c,      f_c = N_eff,H7 / (N_eff,H7 + N_eff,P8),  N_eff = (sum w)^2 / sum w^2

Usage (repo root, inside cmsenv):  python3 scripts/merge_ewk.py [era ...]     (default: Combined)
"""
import os
import subprocess
import sys

import numpy as np
import uproot

TUPLE_DIR = "./root_io/tuples/"
TREE = "tree_output"
WEIGHT_BRANCHES = ["weight", "weight_no_eff_sf", "weight_no_lumi"]
CAMPAIGN_NAMES = {1: "2022", 2: "2022EE", 3: "2023", 4: "2023BPix", 5: "2024", 6: "2025", 7: "2026"}  # lib/CreateTuple.h MC_CAMPAIGN_MAP


def campaign_sums(path):
    """{campaign: (n_entries, sum w, sum w^2)} of one tuple"""
    with uproot.open(path) as f:
        a = f[TREE].arrays(["mc_campaign", "weight"], library="np")
    out = {}
    for c in np.unique(a["mc_campaign"]):
        w = a["weight"][a["mc_campaign"] == c].astype(np.float64)
        out[int(c)] = (len(w), float(w.sum()), float((w * w).sum()))
    return out


def n_eff(sums):
    _, sw, sw2 = sums
    return sw * sw / sw2 if sw2 > 0 else 0.0


def scale_expression(factors):
    """C++ expression mc_campaign -> factor, e.g. (mc_campaign==1 ? 0.4 : (mc_campaign==2 ? 0.5 : 0.0))"""
    expr = "0.0"
    for c, fac in sorted(factors.items(), reverse=True):
        expr = f"(mc_campaign=={c} ? {fac!r} : {expr})"
    return expr


def scale_tuple(src, dst, factors):
    import ROOT
    df = ROOT.RDataFrame(TREE, src)
    factor = scale_expression(factors)
    for b in WEIGHT_BRANCHES:
        df = df.Redefine(b, f"{b} * {factor}")
    opts = ROOT.RDF.RSnapshotOptions()
    opts.fCompressionAlgorithm = ROOT.RCompressionSetting.EAlgorithm.kZSTD
    opts.fCompressionLevel = 5
    df.Snapshot(TREE, dst, "", opts)


def merge_era(era):
    herwig = f"{TUPLE_DIR}EWK_{era}_tuples.root"
    pythia = f"{TUPLE_DIR}EWK_pythia_{era}_tuples.root"
    output = f"{TUPLE_DIR}EWK_merged_{era}_tuples.root"
    for p in (herwig, pythia):
        if not os.path.exists(p):
            sys.exit(f"[ERROR] {p} not found (make it with root_io/tuples/hadd_tuples.sh)")

    print(f"\n===== EWK merge, era {era} =====")
    s_h, s_p = campaign_sums(herwig), campaign_sums(pythia)
    f_h, f_p = {}, {}
    print(f"{'campaign':>14s} {'N H7':>9s} {'sumw H7':>10s} {'Neff H7':>9s} {'N P8':>9s} {'sumw P8':>10s} "
          f"{'Neff P8':>9s} {'f(H7)':>7s}")
    for c in sorted(set(s_h) | set(s_p)):
        name = f"{c} ({CAMPAIGN_NAMES.get(c, '?')})"
        if c not in s_p or c not in s_h:
            only = "Herwig" if c in s_h else "Pythia"
            print(f"[WARNING] campaign {name} only in the {only} sample: kept with weight factor 1")
            (f_h if c in s_h else f_p)[c] = 1.0
            continue
        ne_h, ne_p = n_eff(s_h[c]), n_eff(s_p[c])
        f_h[c] = ne_h / (ne_h + ne_p)
        f_p[c] = 1.0 - f_h[c]
        print(f"{name:>14s} {s_h[c][0]:9d} {s_h[c][1]:10.4g} {ne_h:9.0f} {s_p[c][0]:9d} {s_p[c][1]:10.4g} "
              f"{ne_p:9.0f} {f_h[c]:7.3f}")

    tmp_h, tmp_p = output + ".tmp_herwig.root", output + ".tmp_pythia.root"
    try:
        print(f"[INFO] scaling {herwig}")
        scale_tuple(herwig, tmp_h, f_h)
        print(f"[INFO] scaling {pythia}")
        scale_tuple(pythia, tmp_p, f_p)
        print(f"[INFO] hadd -> {output}")
        subprocess.run(["hadd", "-f", output, tmp_h, tmp_p], check=True, stdout=subprocess.DEVNULL)
    finally:
        for t in (tmp_h, tmp_p):
            if os.path.exists(t):
                os.remove(t)

    # Closure: per campaign, merged sum w == f sum w_H7 + (1 - f) sum w_P8, and all entries kept
    s_m = campaign_sums(output)
    ok = True
    for c in sorted(set(s_h) | set(s_p)):
        exp_n = s_h.get(c, (0, 0, 0))[0] + s_p.get(c, (0, 0, 0))[0]
        exp_w = f_h.get(c, 0) * s_h.get(c, (0, 0, 0))[1] + f_p.get(c, 0) * s_p.get(c, (0, 0, 0))[1]
        n, w, _ = s_m.get(c, (0, 0.0, 0))
        good = n == exp_n and np.isclose(w, exp_w, rtol=1e-6)
        ok &= good
        print(f"[{'PASS' if good else 'FAIL'}] campaign {c}: {n} entries (expected {exp_n}), "
              f"sum w {w:.6g} (expected {exp_w:.6g}; Herwig alone {s_h.get(c, (0, 0, 0))[1]:.6g})")
    if not ok:
        sys.exit(f"[ERROR] closure check failed for {output}")
    print(f"[OK] {output} written")


if __name__ == "__main__":
    for era in sys.argv[1:] or ["Combined"]:
        merge_era(era)
