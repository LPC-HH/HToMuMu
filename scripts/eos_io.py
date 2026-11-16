"""
Safe ROOT file I/O on EOS for the weight scripts (ComputeWeights.py, compute_DY_stitching.py, ...).

Writing ROOT files with uproot straight onto the /eos/uscms FUSE mount corrupted SumGenWeight.root files
(zombie files, unreadable keys) in v2.8. So:
  - recreate_on_eos(path) writes to a local temp file, copies it with xrdcp (end-to-end adler32 checksum),
    then re-opens the EOS copy over xrootd and checks every key against the local file. Raises on any failure.
  - open_eos(path) reads over xrootd instead of FUSE, so a freshly replaced file is never read back stale.
Paths are given as /eos/uscms/store/... (as everywhere in the scripts) and converted internally.
"""
import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager

import numpy as np
import uproot

EOS_FUSE_PREFIX = "/eos/uscms/store/"
XROOTD_PREFIX = "root://cmseos.fnal.gov//store/"


def to_xrootd(path):
    """/eos/uscms/store/... -> root://cmseos.fnal.gov//store/..."""
    path = os.path.normpath(path)
    if not path.startswith(EOS_FUSE_PREFIX):
        raise ValueError(f"{path} is not under {EOS_FUSE_PREFIX}: cannot convert it to an xrootd URL")
    return XROOTD_PREFIX + path[len(EOS_FUSE_PREFIX):]


def open_eos(path):
    """uproot.open of an EOS file over xrootd (the XRootD python bindings, not FUSE)"""
    return uproot.open(to_xrootd(path), handler=uproot.source.xrootd.XRootDSource)


def _contents(f):
    """{name: (values, edges)} of every key; reading each object decompresses it, so corruption raises here"""
    out = {}
    for key in f.keys(cycle=False):
        obj = f[key]
        out[key] = (np.asarray(obj.values()), np.asarray(obj.axis().edges())) if hasattr(obj, "values") else None
    return out


def _verify(local, path):
    with uproot.open(local) as f:
        expected = _contents(f)
    with open_eos(path) as f:
        found = _contents(f)
    if set(found) != set(expected):
        raise RuntimeError(f"{path}: keys on EOS {sorted(found)} differ from the written ones {sorted(expected)}")
    for key, value in expected.items():
        if value is not None and not all(np.array_equal(a, b) for a, b in zip(value, found[key])):
            raise RuntimeError(f"{path}: {key} on EOS differs from the written one")


@contextmanager
def recreate_on_eos(path):
    """Drop-in for `with uproot.recreate(path) as f:` with path on EOS (see the module docstring)"""
    tmp_dir = tempfile.mkdtemp(prefix="eos_io_")
    local = os.path.join(tmp_dir, os.path.basename(path))
    try:
        with uproot.recreate(local) as f:
            yield f
        subprocess.run(["xrdcp", "-f", "-s", "--cksum", "adler32:source", local, to_xrootd(path)], check=True)
        _verify(local, path)
        print(f"  {path}: copied with xrdcp and verified")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
