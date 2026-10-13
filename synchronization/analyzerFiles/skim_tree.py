#!/usr/bin/env python3
"""Skim an analyzer tuple down to a chosen set of branches, optionally renaming them.
python3 skim_tree.py input.root output.root [--tree tree] [--cut "<expression>"]
"""

import argparse
import re
import sys

import ROOT

# input branch name -> output branch name (None = keep the input name)
BRANCHES = {
    "t_run": "run",
    "t_luminosityBlock": "luminosityBlock",
    "t_event": "event",
    "t_genWeight": "genWeight",
    "t_Mu_bsConstrainedPt": "mu_pt",
    "t_Mu_bsConstrainedPt_nanoAOD": "mu_pt_preCorr",
    "t_Mu_phi": "mu_phi",
    "t_Mu_eta": "mu_eta",
    #muon isolation
    #muonID
    "t_diMuon_bsConstrainedPt": "dimuon_pt",
    "t_diMuon_mass": "dimuon_mass",
    #dimuon pt preCorr
    #diMuon mass preCorr
    "t_nJet": "jet_mult",
    "t_Jet_pt": "jet_pt",
    "t_Jet_pt_nanoAOD": "jet_pt_preCorr",
    "t_Jet_eta": "jet_eta",
    "t_Jet_phi": "jet_phi",
    #jet btag info
    #jet quality flags
    "t_PuppiMET_phi": "puppiMET_phi",
    "t_PuppiMET_pt": "puppiMET_pt",
    #MC info
}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="input ROOT file")
    parser.add_argument("output", help="output ROOT file (overwritten)")
    parser.add_argument("--tree", default="tree", help="tree name in input and output (default: tree)")
    parser.add_argument("--cut", default=None, help="optional C++ selection applied to events")
    args = parser.parse_args()

    df = ROOT.RDataFrame(args.tree, args.input)
    input_columns = set(str(c) for c in df.GetColumnNames())

    missing = [old for old in BRANCHES if old not in input_columns]
    if missing:
        sys.exit(f"ERROR: branches not found in {args.input}:{args.tree}: {', '.join(missing)}")

    renames = {old: (new or old) for old, new in BRANCHES.items()}
    output_names = list(renames.values())
    duplicates = sorted({n for n in output_names if output_names.count(n) > 1})
    if duplicates:
        sys.exit(f"ERROR: duplicate output branch names: {', '.join(duplicates)}")
    # Define() can't reuse a name that already exists in the input tree
    collisions = [new for old, new in renames.items() if new != old and new in input_columns]
    if collisions:
        sys.exit(f"ERROR: output names already exist as input branches: {', '.join(collisions)}")

    n_input = df.Count()
    if args.cut:
        df = df.Filter(args.cut, "cut")
    for old, new in renames.items():
        if new == old:
            continue
        # Define(new, old) on a vector column yields RVec<T>, which Snapshot writes with an
        # RVec streamer that JSROOT-based viewers can't decode; write std::vector<T> instead
        vec = re.fullmatch(r"(?:std::)?vector<(.+)>|ROOT::VecOps::RVec<(.+)>", str(df.GetColumnType(old)))
        if vec:
            elem = (vec.group(1) or vec.group(2)).strip()
            df = df.Define(new, f"std::vector<{elem}>({old}.begin(), {old}.end())")
        else:
            df = df.Define(new, old)

    out = df.Snapshot(args.tree, args.output, output_names)
    print(f"Input entries:  {n_input.GetValue()}")
    print(f"Output entries: {out.Count().GetValue()}")
    print(f"Wrote {len(output_names)} branches to {args.output}:{args.tree}")


if __name__ == "__main__":
    main()
