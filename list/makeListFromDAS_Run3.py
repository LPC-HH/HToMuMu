#!/usr/bin/python
"""
Makes <dataset>.list (xrootd paths of all files of the DAS dataset) for the datasets in listDatasets_Run3.py
that do not have a list yet. To regenerate a list, delete it first.

Files whose block has no replica at any site (DAS/Rucio: "No site records found") are valid in DBS but
cannot be read from the grid; jobs reading them fail with "[3011] No servers are available to read the
file". They are dropped from the list and written to <dataset>.lost.

Usage (from list/):
    python3 makeListFromDAS_Run3.py [dataset substrings...]   # default: all datasets
"""
import json
import os
import subprocess
import sys

from listDatasets_Run3 import datasets_info

XROOTD_PREFIX = "root://cmsxrootd.fnal.gov/"

patterns = sys.argv[1:]

_block_replica_cache = {}


def das_query(query, as_json=False):
    output = subprocess.run(["dasgoclient", "-query=" + query] + (["-json"] if as_json else []),
                            capture_output=True, text=True).stdout
    return json.loads(output) if as_json else output


def block_has_replica(block):
    """True if Rucio knows a replica of the block at some site (disk or tape). Without one, DAS only
    prints a WARNING line (and falls back to the original DBS sites, which do not hold the files)"""
    if block not in _block_replica_cache:
        lines = [line for line in das_query("site block=" + block).splitlines() if line.strip()]
        _block_replica_cache[block] = any(not line.startswith("WARNING") for line in lines)
    return _block_replica_cache[block]


for dataset_name in datasets_info.keys():
    if patterns and not any(p in dataset_name for p in patterns):
        continue
    print("\n----- %s -----" % (dataset_name))

    if os.path.exists(dataset_name + ".list"):
        print("Run list already exists. Skipping!")
        continue

    DAS_path = datasets_info[dataset_name][-1]
    print("Querying DAS for " + DAS_path)
    data = das_query("file dataset=" + DAS_path, as_json=True)
    if len(data) == 0:
        print("*************** NO ROOTFILES FOUND ***************")
        sys.exit(1)

    # {file LFN: block name}, in DAS order
    file_blocks = {p["file"][0]["name"]: p["file"][0]["block.name"] for p in data}
    lost_blocks = {block for block in set(file_blocks.values()) if not block_has_replica(block)}

    n_written = 0
    lost = []
    with open(dataset_name + ".list", "w") as outputFile:
        for fileName, blockName in file_blocks.items():
            if blockName in lost_blocks:
                lost.append(fileName)
            else:
                outputFile.write(XROOTD_PREFIX + fileName + "\n")
                n_written += 1
    print("%i files written" % n_written)

    if lost:
        print("[WARNING] %s: dropped %i files in %i blocks with no replica (see %s.lost)"
              % (dataset_name, len(lost), len(lost_blocks), dataset_name))
        with open(dataset_name + ".lost", "w") as lostFile:
            for fileName in lost:
                lostFile.write(fileName + "\n")
