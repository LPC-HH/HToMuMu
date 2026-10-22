#!/usr/bin/env python3
"""Skim an analyzer tuple down to a chosen set of branches, optionally renaming them.
python3 skim_tree.py input.root output.root [--tree tree] [--cut "<expression>"] [--tuples]
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
    "t_Mu_pfRelIso04_all": "mu_RelIso04",
    "t_Mu_looseId": "mu_looseID",
    "t_Mu_mediumId": "mu_mediumID",
    "t_Mu_tightId": "mu_tightID",
    "t_diMuon_bsConstrainedPt": "dimuon_pt",
    "t_diMuon_mass": "dimuon_mass",
    "t_diMuon_bsConstrainedPt_nanoAOD": "dimuon_pt_preCorr",
    "t_diMuon_bsConstrainedMass_nanoAOD": "dimuon_mass_preCorr",
    "t_nJet": "jet_mult",
    "t_Jet_pt": "jet_pt",
    "t_Jet_pt_nanoAOD": "jet_pt_preCorr",
    "t_Jet_mass": "jet_mass",
    "t_Jet_mass_nanoAOD": "jet_mass_preCorr",
    "t_Jet_eta": "jet_eta",
    "t_Jet_phi": "jet_phi",
    "t_Jet_btagUParTAK4B": "jet_btagUParTAK4B",
    "t_pass_muon_trigger_match": "pass_muon_trigger_match",
    "t_pass_jet_veto": "pass_jet_event_veto",
    #MC info
}

BRANCHES_TUPLES = {
    #event variables
    "run": None,
    "luminosityBlock": None,
    "event": None,
    "is_ggH_category": None,
    "is_VBF_category": None,
    "pass_muon_trigger_match": "event_pass_muon_trigger_match",
    "pass_jet_veto": "event_pass_jet_veto",

    #MC info
    "gen_weight": None,
    "pileup_weight": None,
    #"pileup_weight_up": None,
    #"pileup_weight_down": None,
    "weight": None,
    "scale_factor": None,
    "mu_trig_eff_SF": None,
    #"mu_trig_eff_SF_down": None,
    #"mu_trig_eff_SF_up": None,
    "mu_ID_eff_SF": None,
    #"mu_ID_eff_SF_down": None,
    #"mu_ID_eff_SF_up": None,
    "mu_ISO_eff_SF": None,
    #"mu_ISO_eff_SF_down": None,
    #"mu_ISO_eff_SF_up": None,

    #Physics muon info
    "mu1_bsConstrainedPt": "mu1_bscPt",
    "mu1_bsConstrainedPt_nanoAOD": "mu1_bscPt_noCorr",
    "mu2_bsConstrainedPt": "mu2_bscPt",
    "mu2_bsConstrainedPt_nanoAOD": "mu2_bscPt_noCorr",
    "mu1_eta": None,
    "mu2_eta": None,
    "mu1_phi": None,
    "mu2_phi": None,
    "mu1_RelIso04": None,
    "mu2_RelIso04": None,
    "mu1_looseID": None,
    "mu2_looseID": None,
    "mu1_mediumID": None,
    "mu2_mediumID": None,
    "mu1_tightID": None,
    "mu2_tightID": None,

    #all muon info
    "mu_pt": None,
    "mu_pt_nanoAOD": "mu_pt_noCorr",
    "mu_eta": None,
    "mu_phi": None,
    "mu_RelIso04": None,
    "mu_looseID": None,
    "mu_mediumID": None,
    "mu_tightID": None,

    #diMuon info
    "diMuon_bsConstrainedMass": "diMuon_bscMass",
    "diMuon_bsConstrainedMass_nanoAOD": "diMuon_bscMass_noCorr",
    "diMuon_bsConstrainedPt": "diMuon_bscPt",
    "diMuon_bsConstrainedPt_nanoAOD": "diMuon_bscPt_noCorr",
    "diMuon_eta": None,
    "diMuon_phi": None,

    #physics jet info
    "n_jet": None,
    "leading_jet_index": None,
    "leading_jet_pt": None,
    "leading_jet_pt_nanoAOD": "leading_jet_pt_noCorr",
    "leading_jet_eta": None,
    "leading_jet_phi": None,
    "leading_jet_btagUParTAK4B": None,
    "subleading_jet_index": None,
    "subleading_jet_pt": None,
    "subleading_jet_pt_nanoAOD": "subleading_jet_pt_noCorr",
    "subleading_jet_eta": None,
    "subleading_jet_phi": None,
    "subleading_jet_btagUParTAK4B": None,

    #diJet info
    "diJet_mass": None,
    "diJet_mass_nanoAOD": "diJet_mass_noCorr",
    "diJet_pt": None,
    "diJet_pt_nanoAOD": "diJet_pt_noCorr",
    "diJet_eta": None,
    "diJet_phi": None,
    "delta_eta_diJet": None,
    "delta_phi_diJet": None,

    #all jet info
    "jet_pt": None,
    "jet_pt_nanoAOD": "jet_pt_noCorr",
    "jet_mass": None,
    "jet_mass_nanoAOD": "jet_mass_noCorr",
    "jet_eta": None,
    "jet_phi": None,
    "jet_btagUParTAK4B": None,

    #MET info
    "PuppiMET_phi": None,
    "PuppiMET_pt": None,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="input ROOT file")
    parser.add_argument("output", help="output ROOT file (overwritten)")
    parser.add_argument("--tree", default="tree", help="tree name in input and output (default: tree)")
    parser.add_argument("--cut", default=None, help="optional cut string")
    parser.add_argument("--tuples", default=False, action="store_true", help="optional if skimming tuples files")
    args = parser.parse_args()

    branches = BRANCHES_TUPLES if args.tuples else BRANCHES
    #print(branches)
    #quit()

    df = ROOT.RDataFrame(args.tree, args.input)
    input_columns = set(str(c) for c in df.GetColumnNames())

    missing = [old for old in branches if old not in input_columns]
    if missing:
        sys.exit(f"ERROR: branches not found in {args.input}:{args.tree}: {', '.join(missing)}")

    renames = {old: (new or old) for old, new in branches.items()}
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
        # RDataFrame reads vector branches as RVec<T>, which Snapshot writes with an RVec
        # streamer that JSROOT-based viewers can't decode; write std::vector<T> instead,
        # for both renamed and kept-name columns
        vec = re.fullmatch(r"(?:std::)?vector<(.+)>|ROOT::VecOps::RVec<(.+)>", str(df.GetColumnType(old)))
        if new == old:
            if vec:
                elem = (vec.group(1) or vec.group(2)).strip()
                df = df.Redefine(old, f"std::vector<{elem}>({old}.begin(), {old}.end())")
            continue
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
