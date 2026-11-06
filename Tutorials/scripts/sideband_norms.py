#!/usr/bin/env python3
"""Print the --setParameters value that sets each Run 3 background norm from its sideband-scaled best-fit pdf.

The prefit norm written by fTest counts all events, signal region included, so a fit with it depends on blinded events.
The values here come from "Bkg Yield Total" in the logs of the blinded Plots/makeMultipdfPlot.py, one plot_<cat>.log per
category. Don't print them next to the prefit norm: the difference reveals the signal-region count.

Usage: sideband_norms.py <log dir> <channel prefix>, for example "run3_" for a card combined with run3=...
"""
import glob
import os
import re
import sys

log_dir, prefix = sys.argv[1:3]
values = []
for path in sorted(glob.glob(os.path.join(log_dir, "plot_*.log"))):
    category = os.path.basename(path)[len("plot_"):-len(".log")]
    with open(path) as log:
        found = re.findall(r"Bkg Yield Total: ([\d.]+)", log.read())
    if not found:
        sys.exit("no 'Bkg Yield Total' in %s" % path)
    values.append("shapeBkg_bkg_mass_%s%s__norm=%s" % (prefix, category, found[-1]))
if not values:
    sys.exit("no plot_*.log in %s" % log_dir)
print(",".join(values))
