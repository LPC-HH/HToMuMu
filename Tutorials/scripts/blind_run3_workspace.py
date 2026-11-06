#!/usr/bin/env python3
"""Make a copy of a workspace with no real Run 3 events: data_obs holds real Run 2 events and Asimov (S+B, r=1) for Run 3.

Also sets the Run 3 background norms to their sideband-scaled values, replacing the prefit values that count blinded events.
With both done, any fit of the output, --toysFrequentist included, can't depend on blinded Run 3 events.
Run 3 channels are the ones whose name starts with "run3" if there are any, otherwise all of them. Run 3 totals aren't
printed, because next to full-range data counts they would reveal the signal-region count.

Usage: blind_run3_workspace.py <workspace.root> <GenerateOnly output.root> <output.root> <name=value,...>
"""
import sys

import ROOT

ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")

workspace_path, toy_path, out_path, norms = sys.argv[1:5]
workspace_file = ROOT.TFile.Open(workspace_path)
workspace = workspace_file.Get("w")
toy_file = ROOT.TFile.Open(toy_path)
toy = toy_file.Get("toys/toy_asimov")
data = workspace.data("data_obs")

for item in norms.split(","):
    name, value = item.split("=")
    variable = workspace.var(name)
    if not variable:
        sys.exit("no variable %s in %s" % (name, workspace_path))
    variable.setVal(float(value))

channel = workspace.cat("CMS_channel")
labels = [channel.lookupName(i) for i in range(channel.numTypes())] if channel else []
labelled = any(label.startswith("run3") for label in labels)


def is_run3(label):
    return label.startswith("run3") or not labelled


def cut(label):
    return "CMS_channel==CMS_channel::%s" % label


if labelled:
    merged = None
    for label in labels:
        part = (toy if is_run3(label) else data).reduce(cut(label))
        if merged is None:
            merged = part
        else:
            merged.append(part)
else:
    merged = toy

run2_counts = {label: data.sumEntries(cut(label)) for label in labels if not is_run3(label)}
data.reset()
data.append(merged)
workspace.writeToFile(out_path)

# Read the file back: channel by channel it must equal the Asimov dataset (Run 3) or the original events (Run 2).
check_file = ROOT.TFile.Open(out_path)
check = check_file.Get("w").data("data_obs")
failed = 0
for label in labels or [None]:
    selection = cut(label) if label else ""
    got = check.sumEntries(selection) if selection else check.sumEntries()
    if label in run2_counts:
        expected = run2_counts[label]
    else:
        expected = toy.sumEntries(selection) if selection else toy.sumEntries()
    ok = abs(got - expected) < 1e-3 * max(1, expected)
    failed += not ok
    status = "ok" if ok else "MISMATCH"
    print("%-40s data %12.2f %s" % (label, got, status) if label in run2_counts else "%-40s asimov %s" % (label or "all", status))
datasets = [d.GetName() for d in check_file.Get("w").allData()]
print("datasets in the workspace:", datasets)
if datasets != ["data_obs"]:
    failed += 1
    print("ERROR: expected data_obs only")
sys.exit(1 if failed else 0)
