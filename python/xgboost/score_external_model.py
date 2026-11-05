#!/usr/bin/env python
"""Score the nominal tuples with an external, single (non-K-fold) XGBoost model, using that
model's own preprocessing convention instead of ours, e.g. to reproduce a coworker's BDT
(Matias's pre-K-fold train.py) on our tuples.

Usage (from python/xgboost):
  python3 score_external_model.py <channel> <model.xgb> <preprocessing.pkl> [--out-suffix matiasModel]
                                  [--era Combined] [--bkg-subset Full] [--sig-subset NottH]

The preprocessing pickle holds `variables` (input order), `mean_map` and `std_map`. As in
Matias's xgb_utils.append_BDT_score, every input is standardized except entries equal to its
placeholder value (0, or -1 for delta_phi_diJet / pt_balance) and NaN is not masked; all trees
are used (or best_iteration + 1 if the model stores one).

Each nominal tuple is skimmed exactly as train.py --stage apply does (xgb_utils.skim_cut), into
root_io/tuples/BDT_score/<channel><out-suffix>/<subset>/, and gets BDT_<channel> and BDT_fold = -1
(one model, not fold-matched). Then:
  bash scripts/hadd_bdt.sh <channel> <out-suffix>
  python3 plot_BDT_Categories.py <channel> Combined --variant <out-suffix>
"""
import argparse
import os
import pickle
import sys

import numpy as np
import uproot
import xgboost as xgb

import xgb_kfold as kf
import xgb_utils

NOMINAL_TUPLES = ["Data", "DY", "EWK", "TT", "DiBoson", "ggH", "VBF"]
CHUNK_ROWS = 500_000


def preprocess(arrays, variables, mean_map, std_map):
    """float32 inputs standardized as Matias's append_BDT_score (kf.matias_preprocess): entries
    equal to the variable's placeholder are left untouched, NaN is kept (XGBoost's missing value)."""
    x = np.empty((len(arrays[variables[0]]), len(variables)), dtype=np.float32)
    for i, name in enumerate(variables):
        x[:, i] = arrays[name]
    return kf.matias_preprocess(x, variables, mean_map, std_map)  # float32 arithmetic, as his scoring


def score_file(file_name, booster, variables, mean_map, std_map):
    n_rows = uproot.open(file_name)["tree_output"].num_entries
    best = booster.attr("best_iteration")
    iteration_range = (0, int(best) + 1) if best is not None else (0, booster.num_boosted_rounds())
    scores = np.empty(n_rows, dtype=np.float32)
    start = 0
    for arrays in uproot.iterate({file_name: "tree_output"}, variables, library="np", step_size=CHUNK_ROWS,
                                 **kf.uproot_open_options()):
        x = preprocess(arrays, variables, mean_map, std_map)
        dmatrix = xgb.DMatrix(x, feature_names=booster.feature_names)
        scores[start:start + len(x)] = booster.predict(dmatrix, iteration_range=iteration_range)
        start += len(x)
    if start != n_rows:
        raise RuntimeError(f"{file_name}: scored {start} of {n_rows} rows")
    return scores


def score_nominal_tuples(channel, booster, prep, era, sig_subset, bkg_subset, legacy=False, dir_suffix=""):
    """Skim every nominal tuple (as train.py --stage apply) into BDT_score/<channel>[legacy]<dir_suffix>/
    and append BDT_<channel> (booster on Matias-preprocessed inputs; prep = dict(variables,
    mean_map, std_map)) and BDT_fold = -1. Returns the output file names."""
    variables = list(prep["variables"])
    use_bsConstrain = "diMuon_bsConstrainedPt" in variables
    outputs = []
    for file_type in NOMINAL_TUPLES:
        paths = xgb_utils.scoring_paths(file_type, channel, era, sig_subset, bkg_subset, False,
                                        legacy=legacy, dir_suffix=dir_suffix)
        os.makedirs(paths["BDT_path"], exist_ok=True)
        out = paths["BDT_path"] + paths["BDT_name"]
        xgb_utils.copy_and_skim_tree(paths["tuple_path"] + paths["tuple_name"], out,
                                     xgb_utils.skim_cut(channel, paths["category_var"], use_bsConstrain))
        scores = score_file(out, booster, variables, prep["mean_map"], prep["std_map"])
        xgb_utils.append_branches(out, {f"BDT_{channel}": ("F", scores),
                                        "BDT_fold": ("I", np.full(len(scores), -1, dtype=np.int32))})
        print(f"[INFO] {file_type}: {len(scores)} events scored -> {out}")
        outputs.append(out)
    return outputs


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("channel")
    p.add_argument("model", help="the model file (.xgb or .json, loadable by xgb.Booster)")
    p.add_argument("preprocessing", help="pickle with variables, mean_map, std_map")
    p.add_argument("--out-suffix", default="matiasModel",
                   help="output directory BDT_score/<channel><suffix>/ (default: matiasModel)")
    p.add_argument("--era", default="Combined")
    p.add_argument("--bkg-subset", default="Full")
    p.add_argument("--sig-subset", default="NottH")
    opts = p.parse_args(argv[1:])
    if not opts.out_suffix:
        sys.exit("[ERROR] --out-suffix must not be empty: it would overwrite the K-fold BDT_score tuples")

    booster = xgb.Booster()
    booster.load_model(opts.model)
    booster.set_param({"device": "cpu"})
    with open(opts.preprocessing, "rb") as f:
        prep = pickle.load(f)
    variables = list(prep["variables"])
    if booster.num_features() != len(variables):
        sys.exit(f"[ERROR] the model has {booster.num_features()} features, the preprocessing {len(variables)}")
    print(f"[INFO] model {opts.model}: {booster.num_features()} inputs, {booster.num_boosted_rounds()} trees")
    print(f"[INFO] inputs: {', '.join(variables)}")

    score_nominal_tuples(opts.channel, booster, prep, opts.era, opts.sig_subset, opts.bkg_subset,
                         dir_suffix=opts.out_suffix)
    print(f"[INFO] next: `bash scripts/hadd_bdt.sh {opts.channel} {opts.out_suffix}` (from the repository root), "
          f"then `python3 plot_BDT_Categories.py {opts.channel} {opts.era} --variant {opts.out_suffix}` "
          "(from plot_macros)")


if __name__ == "__main__":
    main(sys.argv)
