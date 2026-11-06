#!/usr/bin/env python3
"""Print the --setParameterRanges value for the unbounded background norms of the Run 2 cards.

Those norms are stored with zero error and a range of +-1e30, and without a finite range the fit fails with exit code 0.
Prints nothing if a workspace has none. Usage: norm_ranges.py <workspace.root> <fractional half-width>
"""
import sys

import ROOT

ROOT.gErrorIgnoreLevel = ROOT.kFatal
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
workspace = ROOT.TFile.Open(sys.argv[1]).Get("w")
width = float(sys.argv[2])
print(":".join(
    "%s=%g,%g" % (v.GetName(), v.getVal() * (1 - width), v.getVal() * (1 + width))
    for v in workspace.allVars()
    if v.GetName().endswith("__norm") and v.getMax() > 1e29
))
