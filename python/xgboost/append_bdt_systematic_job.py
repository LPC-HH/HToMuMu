#!/usr/bin/env python3

import os
import sys
import pickle
import subprocess
from array import array

import numpy as np
import uproot
import ROOT as root
import xgboost as xgb

import xgb_utils


def run_command(command):
    print("[COMMAND]", " ".join(command))
    subprocess.run(command, check=True)


if len(sys.argv) != 8:
    print(
        "Usage: python3 append_bdt_systematic_job.py "
        "<channel> <era> <model_era> <tuple_type> "
        "<systematic> <bkg_subset> <sig_subset>"
    )
    sys.exit(1)


channel_US = sys.argv[1]
era = sys.argv[2]
model_era = sys.argv[3]
tuple_type = sys.argv[4]
systematic = sys.argv[5]
background_subset = sys.argv[6]
signal_subset = sys.argv[7]


DO_STANDARDIZATION = True
USE_BSCONSTRAIN = True

ANALYZER_VERSION = "v2.1"
TUPLES_VERSION = "v2.1.0"

subset_title = f"B{background_subset}_S{signal_subset}"

user = os.environ["USER"]

XROOTD = "root://cmseos.fnal.gov"

# Change "group" to "user" here if your systematic tuples
# are actually in /store/user/lpchmumu/...
EOS_DIR = (
    f"/store/group/lpchmumu/{user}/"
    f"analyzer_HiggsMuMu_{ANALYZER_VERSION}/"
    f"tuples_{TUPLES_VERSION}/systematics"
)

EOS_OUTPUT_DIR = (
    f"{EOS_DIR}/BDT_score/"
    f"{channel_US}/{subset_title}"
)

tuple_name = (
    f"{tuple_type}_{era}_{systematic}_tuples.root"
)

local_input = "input.root"
local_output = tuple_name

input_url = f"{XROOTD}/{EOS_DIR}/{tuple_name}"
output_url = f"{XROOTD}/{EOS_OUTPUT_DIR}/{tuple_name}"


print("=" * 80)
print(f"Channel:       {channel_US}")
print(f"Era:           {era}")
print(f"Model era:     {model_era}")
print(f"Tuple type:    {tuple_type}")
print(f"Systematic:    {systematic}")
print(f"Input:         {input_url}")
print(f"Output:        {output_url}")
print("=" * 80)


# ----------------------------------------------------------------------
# Input
# ----------------------------------------------------------------------

print("[INFO] Copying input ROOT file from EOS")

run_command([
    "xrdcp",
    "-f",
    input_url,
    local_input,
])


# ----------------------------------------------------------------------
# Load BDT configuration
# ----------------------------------------------------------------------

variables = xgb_utils.get_variables(
    channel_US,
    USE_BSCONSTRAIN,
)

variables = variables[:-3]
variable_names = [var[0] for var in variables]


model_name = (
    f"model_{channel_US}_{model_era}_"
    f"{subset_title}"
)

preprocessing_name = (
    f"preprocessing_{channel_US}_{model_era}_"
    f"{subset_title}"
)

if USE_BSCONSTRAIN:
    model_name += "_bsC"
    preprocessing_name += "_bsC"

model_file = model_name + ".pkl"
preprocessing_file = preprocessing_name + ".pkl"


print(f"[INFO] Loading model: {model_file}")
print(f"[INFO] Loading preprocessing: {preprocessing_file}")


with open(model_file, "rb") as f:
    model = pickle.load(f)


with open(preprocessing_file, "rb") as f:
    preprocessing = pickle.load(f)


mean_map = preprocessing["mean_map"]
std_map = preprocessing["std_map"]

training_variables = preprocessing["variables"]


if training_variables != variable_names:
    raise RuntimeError(
        "Variable list in preprocessing file does not "
        "match current xgb_utils.get_variables()"
    )


# ----------------------------------------------------------------------
# Skim
# ----------------------------------------------------------------------

print("[INFO] Skimming tuple")

xgb_utils.copy_and_skim_tree(
    "./",
    local_input,
    "./",
    local_output,
    channel_US,
    USE_BSCONSTRAIN,
)


# ----------------------------------------------------------------------
# Read BDT variables
# ----------------------------------------------------------------------

print("[INFO] Reading BDT variables")

with uproot.open(local_output) as f:

    if "tree_output" not in f:
        raise RuntimeError(
            f"tree_output not found in {local_output}"
        )

    arrays = f["tree_output"].arrays(
        variable_names,
        library="np",
    )


if len(variable_names) > 0:
    x_test = np.column_stack(
        [arrays[name] for name in variable_names]
    ).astype(np.float32)
else:
    x_test = np.empty((0, 0), dtype=np.float32)


number_of_events = len(x_test)

print(
    f"[INFO] Number of events after skimming: "
    f"{number_of_events}"
)


# ----------------------------------------------------------------------
# Standardization
# ----------------------------------------------------------------------

if DO_STANDARDIZATION and number_of_events > 0:

    for i, variable in enumerate(variables):

        variable_name = variable[0]

        null_value = 0.0

        if variable_name in [
            "delta_phi_diJet",
            "pt_balance",
        ]:
            null_value = -1.0

        if variable_name not in mean_map:
            raise KeyError(
                f"Mean missing for {variable_name}"
            )

        if variable_name not in std_map:
            raise KeyError(
                f"Std missing for {variable_name}"
            )

        if std_map[variable_name] == 0:
            raise ValueError(
                f"Std is zero for {variable_name}"
            )

        mask = x_test[:, i] != null_value

        x_test[mask, i] = (
            x_test[mask, i]
            - mean_map[variable_name]
        ) / std_map[variable_name]


# ----------------------------------------------------------------------
# BDT prediction
# ----------------------------------------------------------------------

if number_of_events > 0:

    booster = model.get_booster()

    booster_feature_names = booster.feature_names

    if (
        booster_feature_names is not None
        and len(booster_feature_names)
        != x_test.shape[1]
    ):
        raise RuntimeError(
            "Number of variables does not match model: "
            f"model={len(booster_feature_names)}, "
            f"input={x_test.shape[1]}"
        )

    if booster_feature_names is not None:
        dtest = xgb.DMatrix(
            x_test,
            feature_names=booster_feature_names,
        )
    else:
        dtest = xgb.DMatrix(x_test)

    try:
        best_iteration = booster.best_iteration
    except (AttributeError, TypeError):
        best_iteration = None

    if best_iteration is not None:
        y_pred = booster.predict(
            dtest,
            iteration_range=(0, best_iteration + 1),
        )
    else:
        y_pred = booster.predict(dtest)

    y_pred = np.asarray(
        y_pred,
        dtype=np.float32,
    )

else:

    y_pred = np.array(
        [],
        dtype=np.float32,
    )


# ----------------------------------------------------------------------
# Append branch
# ----------------------------------------------------------------------

print("[INFO] Adding BDT branch")

root_file = root.TFile.Open(
    local_output,
    "UPDATE",
)

if not root_file or root_file.IsZombie():
    raise RuntimeError(
        f"Could not open {local_output}"
    )


tree = root_file.Get("tree_output")

if not tree:
    root_file.Close()

    raise RuntimeError(
        "tree_output not found"
    )


n_entries = tree.GetEntries()

if n_entries != len(y_pred):
    root_file.Close()

    raise RuntimeError(
        f"Entry mismatch: "
        f"tree={n_entries}, predictions={len(y_pred)}"
    )


BDT_var_name = f"BDT_{channel_US}"

BDT_value = array("f", [0.0])

new_branch = tree.Branch(
    BDT_var_name,
    BDT_value,
    f"{BDT_var_name}/F",
)


for entry_index in range(n_entries):

    tree.GetEntry(entry_index)

    if entry_index % 10000 == 0:
        print(
            f"[INFO] Processing "
            f"{entry_index}/{n_entries}"
        )

    BDT_value[0] = float(
        y_pred[entry_index]
    )

    new_branch.Fill()


tree.Write(
    "",
    root.TObject.kOverwrite,
)

root_file.Close()


# ----------------------------------------------------------------------
# Copy result to EOS
# ----------------------------------------------------------------------

print("[INFO] Creating EOS output directory")

run_command([
    "xrdfs",
    XROOTD,
    "mkdir",
    "-p",
    EOS_OUTPUT_DIR,
])


print("[INFO] Copying output to EOS")

run_command([
    "xrdcp",
    "-f",
    local_output,
    output_url,
])


print()
print("=" * 80)
print("[INFO] JOB FINISHED SUCCESSFULLY")
print(f"[INFO] {output_url}")
print("=" * 80)
