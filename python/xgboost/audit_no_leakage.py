#!/usr/bin/env python
"""Audit of the statistical requirement

    No MC event used to train model i may receive its final analysis BDT score from model i.

Run after `train.py ... --stage final` and `--stage apply`; exits non-zero if a check fails.

  1. each saved fold model was trained on exactly the training rows whose fold != its own;
  2. every scored tuple carries BDT_fold == event % N_FOLDS, i.e. the fold rule that the
     training used (xgb_kfold.fold_of_event);
  3. on a random subset, the stored BDT score is reproduced by model[BDT_fold] and is NOT
     the score of a different model.

Usage: python3 audit_no_leakage.py <channel> <era> [bkg_subset sig_subset] [--reCat] [--n-check N]
"""
import os
import sys

import numpy as np
import pandas as pd
import uproot

import xgb_kfold as kf
import xgb_utils

failures = []


def check(ok, msg):
    print(("[PASS] " if ok else "[FAIL] ") + msg)
    if not ok:
        failures.append(msg)


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    reCat = "--reCat" in sys.argv
    n_check = 20000
    if "--n-check" in sys.argv:
        n_check = int(sys.argv[sys.argv.index("--n-check") + 1])
        argv.remove(str(n_check))
    if len(argv) not in (2, 4):
        sys.exit(__doc__)
    channel, era = argv[0], argv[1]
    bkg, sig = (argv[2], argv[3]) if len(argv) == 4 else ("Full", "NottH")
    use_bsC = True
    file_append = "reCat" if reCat else ""
    test_name = f"{channel}{file_append}_{era}_B{bkg}_S{sig}"
    names = [v[0] for v in xgb_utils.get_variables(channel, use_bsC)[:-3]]
    skim_dir = f"../../root_io/skim/{channel}{file_append}/"
    rng = np.random.default_rng(0)

    bundle = kf.load_fold_bundle(test_name, use_bsC)

    # ---- 1. models were trained on the complement of their own fold.
    # The folds come straight off the `event` branch of the skim rows, then train.py's own
    # (strict) training-region cut, so the handful of events sitting exactly on 115.0/135.0 --
    # which the skim keeps and the training drops -- are not counted here either.
    train_folds, train_mass = [], []
    for subset in (bkg, sig):
        path = kf.skim_path(skim_dir, era, subset)
        train_folds.append(kf.fold_of_event(kf.read_event_ids(path)))
        train_mass.append(kf.read_columns(path, [kf.MASS_BSC])[kf.MASS_BSC])
    train_folds = np.concatenate(train_folds)[kf.training_region_mask(np.concatenate(train_mass))]
    for member in bundle:
        i = member["fold"]
        expected = int((train_folds != i).sum())
        check(member["meta"]["n_train"] == expected,
              f"model {i}: n_train {member['meta']['n_train']} == training rows with fold != {i} ({expected})")

    # ---- 2./3. the scored tuples
    for file_type in ["Data", "DY", "EWK", "TT", "DiBoson", "ggH", "VBF"]:
        p = xgb_utils._scoring_paths(file_type, channel, era, sig, bkg, reCat)
        scored = p["BDT_path"] + p["BDT_name"]
        if not os.path.exists(scored):
            print(f"[SKIP] {scored} not found")
            continue
        n_selected = int(xgb_utils.selection_mask(
            p["tuple_path"] + p["tuple_name"], channel, p["category_var"], use_bsC).sum())
        with uproot.open(scored, **kf.uproot_open_options()) as f:
            tree = f["tree_output"]
            check(tree.num_entries == n_selected,
                  f"{file_type}: {tree.num_entries} scored rows == {n_selected} selected tuple entries")
            # the fold each row SHOULD have, from that row's own event id -- no assumption that
            # the scored file is in the same order as anything else
            expected_folds = kf.fold_of_event(kf.read_event_ids(scored))
            stored_folds = tree["BDT_fold"].array(library="np")
            stored_score = tree[f"BDT_{channel}"].array(library="np")
            # re-predict a random CONTIGUOUS window rather than scattered rows: reading every
            # feature column of a multi-GB tuple would cost GBs of RAM, and since the folds
            # cycle with period N_FOLDS any window of a few thousand rows covers all of them
            start = int(rng.integers(0, max(1, tree.num_entries - n_check)))
            stop = min(start + n_check, tree.num_entries)
            df = pd.DataFrame(tree.arrays(names, entry_start=start, entry_stop=stop, library="np"))
        xgb_utils.mask_undefined_jet_features(df)
        check(np.array_equal(stored_folds, expected_folds),
              f"{file_type}: BDT_fold == {kf.EVENT_ID} % {kf.N_FOLDS} for all "
              f"{len(stored_folds)} rows")

        pick = np.arange(start, stop)
        x, folds_pick = df.to_numpy(dtype=np.float64), stored_folds[pick]
        own = kf.predict_by_fold(x, folds_pick, bundle)
        other = kf.predict_by_fold(x, (folds_pick + 1) % kf.N_FOLDS, bundle)
        check(np.allclose(own, stored_score[pick], atol=1e-6),
              f"{file_type}: stored score reproduced by model[BDT_fold] on rows {start}-{stop}")
        check(np.isclose(other, stored_score[pick], atol=1e-6).mean() < 0.01,
              f"{file_type}: stored score differs from a neighbouring model's score "
              f"({np.isclose(other, stored_score[pick], atol=1e-6).sum()}/{len(pick)} coincidences)")

    print("\n" + ("ALL CHECKS PASSED" if not failures else f"{len(failures)} CHECK(S) FAILED"))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
