#!/usr/bin/env python3

import os
import sys
import subprocess


import xgb_utils


def run_command(command):
    print("[COMMAND]", " ".join(command))
    subprocess.run(command, check=True)


if len(sys.argv) != 10:
    print(
        "Usage: python3 append_bdt_systematic_job.py "
        "<channel> <era> <model_era> <tuple_type> "
        "<systematic> <bkg_subset> <sig_subset> "
        "<version> <user>"
    )
    sys.exit(1)


channel_US = sys.argv[1]
era = sys.argv[2]
model_era = sys.argv[3]
tuple_type = sys.argv[4]
systematic = sys.argv[5]
background_subset = sys.argv[6]
signal_subset = sys.argv[7]
version = sys.argv[8]
user = sys.argv[9]


DO_STANDARDIZATION = True
USE_BSCONSTRAIN = True

version_parts = version.split(".")

if len(version_parts) < 2:
    raise ValueError(
        f"Invalid version '{version}'. Expected something like 2.2.1"
    )

ANALYZER_VERSION = f"v{version_parts[0]}.{version_parts[1]}"
TUPLES_VERSION = f"v{version}"

subset_title = f"B{background_subset}_S{signal_subset}"

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
# Load the fold models, skim, score and append
# ----------------------------------------------------------------------

# Fold-matched, exactly as for the nominal tuples: fold = event % n_folds, so a varied event
# carries the same `event` as its nominal self, lands in the same fold and is scored by the same
# model -- one that was not trained on it. This used to be a single legacy model with a
# hand-rolled standardize / predict / append block, because before the event ID a varied row
# could not be matched to its nominal row's fold. score_tuple_into() raises a clear error if
# the systematic tuple predates the `event` branch.

import xgb_kfold as kf

variables = xgb_utils.get_variables(channel_US, USE_BSCONSTRAIN)[:-3]
variable_names = [var[0] for var in variables]

test_name = f"{channel_US}_{model_era}_{subset_title}"
print(f"[INFO] Loading fold models: {test_name}")
bundle = kf.load_fold_bundle(test_name, USE_BSCONSTRAIN)
if variable_names != list(bundle[0]["meta"]["variables"]):
    raise RuntimeError(
        "xgb_utils.get_variables() does not match the variables the fold models were trained "
        f"with ({len(variable_names)} vs {len(bundle[0]['meta']['variables'])})"
    )
print(f"[INFO] {len(bundle)} fold models, {len(variable_names)} variables")

xgb_utils.score_tuple_into(
    "./",
    local_input,
    "./",
    local_output,
    channel_US,
    "_category",
    USE_BSCONSTRAIN,
    variable_names,
    {f"BDT_{channel_US}": bundle},
    tag=f"{tuple_type}_{era}_{systematic}",
)


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
