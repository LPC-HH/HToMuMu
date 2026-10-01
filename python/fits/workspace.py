"""Assemble a pyhf workspace from the signal + background models.

One pyhf *channel* per BDT category. Samples per channel:

    sig_ggH, sig_VBF  -- parametric-fit signal templates, split by expected
                         yield, sharing the POI `mu`; each carries the common
                         signal normsys, its own cross-section normsys, and the
                         MassScale / MassReso histosys.
    background         -- from model A (sideband fit) or model B (MC template);
                         free per-category normfactor `bkg_norm_<cat>` plus
                         shape nuisances (and `staterror` for model B).

The Asimov observation for each channel is  b_i + s_i(mu=1)  -- i.e. the median
expected dataset with SM signal present, used for the expected discovery
significance.
"""

from __future__ import annotations

import numpy as np

from . import fit_config as cfg
from .background_model import BackgroundModel
from .signal_model import SignalShape

_FLOOR = 1e-9


def _lst(a):
    return [float(x) for x in np.asarray(a, dtype=float)]


def _signal_samples(sh: SignalShape):
    ytot = sh.yield_total
    frac_ggh = sh.yield_ggh / ytot if ytot > 0 else 0.5
    fracs = {"sig_ggH": frac_ggh, "sig_VBF": 1.0 - frac_ggh}

    samples = []
    for sname, frac in fracs.items():
        nom = np.clip(sh.nominal * frac, _FLOOR, None)
        mods = [{"name": "mu", "type": "normfactor", "data": None}]
        for nname, (dn, up) in cfg.SIGNAL_NORMSYS.items():
            mods.append({"name": nname, "type": "normsys",
                         "data": {"hi": up, "lo": dn}})
        xs_name, (xdn, xup) = cfg.SIGNAL_XS_NORMSYS[sname]
        mods.append({"name": xs_name, "type": "normsys",
                     "data": {"hi": xup, "lo": xdn}})
        mods.append({"name": "MassScale", "type": "histosys",
                     "data": {"hi_data": _lst(np.clip(sh.scale_up * frac, _FLOOR, None)),
                              "lo_data": _lst(np.clip(sh.scale_dn * frac, _FLOOR, None))}})
        mods.append({"name": "MassReso", "type": "histosys",
                     "data": {"hi_data": _lst(np.clip(sh.reso_up * frac, _FLOOR, None)),
                              "lo_data": _lst(np.clip(sh.reso_dn * frac, _FLOOR, None))}})
        samples.append({"name": sname, "data": _lst(nom), "modifiers": mods})
    return samples


def _background_sample(bm: BackgroundModel):
    cat = bm.category
    mods = [{"name": f"bkg_norm_{cat}", "type": "normfactor", "data": None}]
    for name, up, dn in zip(bm.shape_names, bm.shape_up, bm.shape_dn):
        mods.append({"name": name, "type": "histosys",
                     "data": {"hi_data": _lst(up), "lo_data": _lst(dn)}})
    if bm.staterror is not None:
        mods.append({"name": f"staterror_{cat}", "type": "staterror",
                     "data": _lst(np.clip(bm.staterror, 0.0, None))})
    return {"name": "background", "data": _lst(np.clip(bm.nominal, _FLOOR, None)),
            "modifiers": mods}


def build_spec(
    signals: dict[str, SignalShape],
    backgrounds: dict[str, BackgroundModel],
    categories=None,
    poi_bounds=(-5.0, 25.0),
    bkg_norm_bounds=(0.0, 10.0),
):
    categories = categories or list(signals)
    channels, observations = [], []
    for cat in categories:
        sh, bm = signals[cat], backgrounds[cat]
        samples = _signal_samples(sh) + [_background_sample(bm)]
        channels.append({"name": cat, "samples": samples})

        asimov = np.clip(bm.nominal, _FLOOR, None) + np.clip(sh.nominal, _FLOOR, None)
        observations.append({"name": cat, "data": _lst(asimov)})

    params = [{"name": "mu", "bounds": [list(poi_bounds)], "inits": [1.0]}]
    for cat in categories:
        params.append({"name": f"bkg_norm_{cat}",
                       "bounds": [list(bkg_norm_bounds)], "inits": [1.0]})

    spec = {
        "channels": channels,
        "observations": observations,
        "measurements": [{
            "name": "mu_inclusive",
            "config": {"poi": "mu", "parameters": params},
        }],
        "version": "1.0.0",
    }
    return spec


def build_model_and_data(spec, categories=None):
    """Return (model, data) for the full spec or a category subset."""
    import pyhf

    if categories is not None:
        keep = set(categories)
        spec = {
            **spec,
            "channels": [c for c in spec["channels"] if c["name"] in keep],
            "observations": [o for o in spec["observations"] if o["name"] in keep],
        }
        used = {"mu"} | {f"bkg_norm_{c}" for c in keep}
        spec["measurements"] = [{
            **spec["measurements"][0],
            "config": {
                "poi": "mu",
                "parameters": [p for p in spec["measurements"][0]["config"]["parameters"]
                               if p["name"] in used],
            },
        }]

    ws = pyhf.Workspace(spec)
    model = ws.model(
        measurement_name="mu_inclusive",
        modifier_settings={
            "normsys": {"interpcode": "code4"},
            "histosys": {"interpcode": "code4p"},
        },
    )
    data = ws.data(model)
    return model, data
