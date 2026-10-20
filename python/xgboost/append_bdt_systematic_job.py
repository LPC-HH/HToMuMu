#!/usr/bin/env python3
"""Score ONE systematic ROOT tuple with the SAME K-fold pipeline as nominal.

Requires the updated xgb_utils.py and xgb_kfold.py used by train.py.

Preserves the nine positional arguments of the original HTCondor job:

    python3 append_bdt_systematic_job_updated.py \
        <channel> <era> <model_era> <tuple_type> <systematic> \
        <bkg_subset> <sig_subset> <version> <user> \
        [--models-dir models] [--eos-area group|user] [--optimized]

Example (five fold models from ``train.py ggH Combined --stage final``):

    python3 append_bdt_systematic_job_updated.py \
        ggH 2023 Combined DY scale_up Full NottH 2.4.2 mbarrial \
        --eos-area user --models-dir models

HTCondor input files must include xgb_utils.py, xgb_kfold.py, plus for
k = 0..4:
    model_<test_name>_fold<k>_bsC.json
    preprocessing_<test_name>_fold<k>_bsC.pkl

``test_name`` follows train.py exactly, e.g. ggH_Combined_BFull_SNottH.
If Condor places the 10 model files in the scratch directory itself,
pass ``--models-dir .``. The model .pkl files are NOT needed for scoring.
"""

import argparse
import subprocess
from pathlib import Path

import numpy as np
import uproot

import xgb_kfold as kf
import xgb_utils

XROOTD = "root://cmseos.fnal.gov"
USE_BSCONSTRAIN = True  # must match the nominal train.py configuration


def run_command(command):
    print("[COMMAND]", " ".join(map(str, command)), flush=True)
    subprocess.run(command, check=True)


def make_test_name(channel, model_era, subset_title, use_recategorization, optimized):
    """Identical to train.py's base_name/test_name construction (no smoke models)."""
    channel_tag = channel + ("reCat" if use_recategorization else "")
    base_name = f"{channel_tag}_{model_era}_{subset_title}"
    return base_name + ("_optimized" if optimized else "")


def load_bundle(args, test_name, names):
    models_dir = Path(args.models_dir)
    bs_suffix = "_bsC" if USE_BSCONSTRAIN else ""
    expected = [
        models_dir / f"{kind}_{test_name}_fold{k}{bs_suffix}.{extension}"
        for k in range(kf.N_FOLDS)
        for kind, extension in (("model", "json"), ("preprocessing", "pkl"))
    ]
    missing = [str(path) for path in expected if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing K-fold model or preprocessing files:\n  "
            + "\n  ".join(missing)
            + "\nSupply the 10 files saved by train.py, and set --models-dir "
              "to the correct Condor scratch directory."
        )

    print(f"[INFO] Loading K-fold bundle '{test_name}' from {models_dir}")
    bundle = kf.load_fold_bundle(
        test_name, USE_BSCONSTRAIN, models_dir=str(models_dir)
    )
    if len(bundle) != kf.N_FOLDS:
        raise RuntimeError(
            f"Expected {kf.N_FOLDS} fold models, loaded {len(bundle)}"
        )
    for index, member in enumerate(bundle):
        if member["fold"] != index:
            raise RuntimeError(f"Unexpected fold ordering in model bundle: {index}")
        trained_names = list(member["meta"]["variables"])
        if trained_names != names:
            raise RuntimeError(
                f"Feature list/order differs from fold {index} training.\n"
                f"Trained: {trained_names}\nCurrent: {names}"
            )
    print(f"[INFO] Loaded {len(bundle)} fold models")
    return bundle


def validate_input(path, channel, names, category_suffix):
    """Catch old/incompatible systematic tuples before expensive skimming."""
    mass = "diMuon_bsConstrainedMass" if USE_BSCONSTRAIN else "diMuon_mass"
    category = f"is_{channel}{category_suffix}"
    required = set(names) | {mass, category, kf.EVENT_ID}
    with uproot.open(str(path), **kf.uproot_open_options()) as source:
        if "tree_output" not in source:
            raise RuntimeError(f"No tree_output in {path}")
        tree = source["tree_output"]
        missing = sorted(required - set(tree.keys()))
        if missing:
            raise RuntimeError(
                "Systematic input is missing branches required by the new "
                "K-fold BDT:\n  " + "\n  ".join(missing)
                + "\nIf these branches are absent in the source tuples, the "
                  "tuples must be regenerated before scoring."
            )
        # EVENT_ID must never be converted to float32: folds would be corrupted.
        event_array = tree[kf.EVENT_ID].array(
            entry_start=0, entry_stop=1, library="np"
        )
        if event_array.dtype.kind not in "ui":
            raise TypeError(
                f"The '{kf.EVENT_ID}' branch must contain integer event IDs, "
                f"got {event_array.dtype}"
            )
        print(f"[INFO] Input events (before skim): {tree.num_entries:,}")
        print(f"[INFO] Skim category: {category}; mass window: "
              f"{xgb_utils.SKIM_MASS_WINDOW}")


def validate_output(path, channel):
    """Confirm output exists and inspect some rows for consistent fold assignment."""
    with uproot.open(str(path), **kf.uproot_open_options()) as source:
        if "tree_output" not in source:
            raise RuntimeError(f"No tree_output in scored file {path}")
        tree = source["tree_output"]
        score_branch = f"BDT_{channel}"
        required = {score_branch, "BDT_fold", kf.EVENT_ID}
        missing = sorted(required - set(tree.keys()))
        if missing:
            raise RuntimeError(f"Output is missing branches: {missing}")
        n = tree.num_entries
        print(f"[INFO] Output events (after skim): {n:,}")
        # Cheap cross-check; the shared scoring routine processes the whole tree.
        if n:
            indices = ((0, min(n, 1000)), (max(0, n - 1000), n))
            for start, stop in set(indices):
                arrays = tree.arrays(
                    [score_branch, "BDT_fold", kf.EVENT_ID],
                    entry_start=start, entry_stop=stop, library="np"
                )
                expected_folds = kf.fold_of_event(arrays[kf.EVENT_ID])
                if not np.array_equal(arrays["BDT_fold"], expected_folds):
                    raise RuntimeError(
                        "Output BDT_fold differs from event % N_FOLDS"
                    )
                if not np.isfinite(arrays[score_branch]).all():
                    raise RuntimeError("Output contains non-finite BDT scores")
        return n


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("channel", choices=("ggH", "VBF"))
    parser.add_argument("era", help="Systematic tuple era, e.g. 2023")
    parser.add_argument("model_era", help="Training era, e.g. Combined")
    parser.add_argument("tuple_type", help="Tuple sample e.g. DY, ggH, VBF")
    parser.add_argument("systematic", help="e.g. scale_up or CMS_scale_j_Absolute_up")
    parser.add_argument("bkg_subset", help="e.g. Full")
    parser.add_argument("sig_subset", help="e.g. NottH")
    parser.add_argument("version", help="Tuple version, e.g. 2.4.2")
    parser.add_argument("user", help="EOS analyzer owner")
    parser.add_argument("--models-dir", default="models",
                        help="Directory containing model JSON and preprocessing PKLs. "
                             "Use '.' for flat Condor transfers (default: models).")
    parser.add_argument("--eos-area", choices=("group", "user"), default="group",
                        help="Input EOS namespace (old job used group)")
    parser.add_argument("--optimized", action="store_true",
                        help="Use train.py --use-optuna model names and output directory")
    parser.add_argument("--use-recategorization", action="store_true",
                        help="Use models trained with train.py --use-recategorization")
    parser.add_argument("--systematic-category", choices=("original", "BDT"), default="original",
                        help="Skim using is_<channel>_category (default, as in "
                             "xgb_utils.append_BDT_score_to_sys) or categoryBDT")
    parser.add_argument("--score-chunk-rows", type=int, default=500_000)
    parser.add_argument("--skim-chunks", type=int, default=1,
                        help="Parallel CopyTree workers; 1 recommended on Condor")
    args = parser.parse_args()

    if args.score_chunk_rows <= 0 or args.skim_chunks <= 0:
        parser.error("--score-chunk-rows and --skim-chunks must be positive")
    parts = args.version.split(".")
    if len(parts) < 2 or not all(part.isdigit() for part in parts):
        parser.error("Version must look like 2.4.2")

    analyzer_version = f"v{parts[0]}.{parts[1]}"
    tuple_version = f"v{args.version}"
    subset_title = f"B{args.bkg_subset}_S{args.sig_subset}"
    test_name = make_test_name(
        args.channel, args.model_era, subset_title,
        args.use_recategorization, args.optimized,
    )
    category_suffix = ("_categoryBDT" if args.systematic_category == "BDT"
                       else "_category")

    eos_dir = (
        f"/store/{args.eos_area}/lpchmumu/{args.user}/"
        f"analyzer_HiggsMuMu_{analyzer_version}/"
        f"tuples_{tuple_version}/systematics"
    )
    # Match the nominal systematic code's usual directory, while keeping
    # reCat output segregated when explicitly selected.
    channel_output = args.channel + ("reCat" if args.use_recategorization else "")
    if args.optimized:
        channel_output += "optimized"
    eos_out_dir = f"{eos_dir}/BDT_score/{channel_output}/{subset_title}"

    tuple_name = f"{args.tuple_type}_{args.era}_{args.systematic}_tuples.root"
    input_url = f"{XROOTD}/{eos_dir}/{tuple_name}"  # double slash before /store
    output_url = f"{XROOTD}/{eos_out_dir}/{tuple_name}"
    local_input = Path("input.root")
    local_output = Path(tuple_name)

    print("=" * 80)
    print(f"Channel:          {args.channel}")
    print(f"Systematic era:   {args.era}")
    print(f"Model era:        {args.model_era}")
    print(f"Model name:       {test_name}")
    print(f"Systematic:       {args.systematic}")
    print(f"Model directory:  {args.models_dir}")
    print(f"Input:            {input_url}")
    print(f"Output:           {output_url}")
    print("=" * 80)

    variables = xgb_utils.get_variables(args.channel, USE_BSCONSTRAIN)[:-3]
    names = [entry[0] for entry in variables]
    bundle = load_bundle(args, test_name, names)

    print("[INFO] Copying systematic ROOT input from EOS")
    run_command(["xrdcp", "-f", input_url, str(local_input)])
    validate_input(local_input, args.channel, names, category_suffix)

    # The SAME function used by train.py and by the nominal K-fold application.
    # It skims, masks missing jets, selects model via event % 5, applies each
    # fold's own standardization, and writes BDT_<channel> plus BDT_fold.
    xgb_utils.SCORE_CHUNK_ROWS = args.score_chunk_rows
    xgb_utils.SKIM_CHUNKS = args.skim_chunks
    xgb_utils.score_tuple_into(
        "./", str(local_input),
        "./", str(local_output),
        args.channel, category_suffix, USE_BSCONSTRAIN,
        names, bundle,
        tag=f"{args.tuple_type}_{args.era}_{args.systematic}",
        legacy=False,
    )
    validate_output(local_output, args.channel)

    print("[INFO] Creating EOS output directory")
    run_command(["xrdfs", XROOTD, "mkdir", "-p", eos_out_dir])
    print("[INFO] Copying scored tuple to EOS")
    run_command(["xrdcp", "-f", str(local_output), output_url])
    print("=" * 80)
    print("[INFO] JOB FINISHED SUCCESSFULLY")
    print(f"[INFO] {output_url}")
    print("=" * 80)


if __name__ == "__main__":
    main()
