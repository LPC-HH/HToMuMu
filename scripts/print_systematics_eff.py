#!/usr/bin/env python3

from pathlib import Path
import numpy as np
import uproot

from systematics_config import (
    BDT_CUTS,
    MASS_MIN,
    MASS_MAX,
    CHANNELS,
    PROCESSES,
    DATACARD_CATEGORY_ORDER,
    SUBSET,
    TREE_NAME,
)

OUTPUT_PROC_KEYS = {
    "ggH": "ggH",
    "VBF": "qqH",
}

TUPLE_BASE = Path(
    "./root_io/tuples"
)
NOMINAL_BASE = TUPLE_BASE / "BDT_score"

SYSTEMATICS = {
    "mu_trig_eff": {
        "title": "CMS_mu_trig_eff",
        "nominal": "mu_trig_eff_SF",
        "up": "mu_trig_eff_SF_up",
        "down": "mu_trig_eff_SF_down",
    },
    "mu_ID_eff": {
        "title": "CMS_mu_ID_eff",
        "nominal": "mu_ID_eff_SF",
        "up": "mu_ID_eff_SF_up",
        "down": "mu_ID_eff_SF_down",
    },
    "mu_ISO_eff": {
        "title": "CMS_mu_ISO_eff",
        "nominal": "mu_ISO_eff_SF",
        "up": "mu_ISO_eff_SF_up",
        "down": "mu_ISO_eff_SF_down",
    },
}


def get_categories(channel):
    intervals = list(zip(BDT_CUTS[channel][:-1], BDT_CUTS[channel][1:]))
    intervals.reverse()
    return [
        {
            "name": f"{channel}cat{i}",
            "low": low,
            "high": high,
            "highest": i == 1,
        }
        for i, (low, high) in enumerate(intervals, start=1)
    ]


def category_order():
    out = []
    for channel in DATACARD_CATEGORY_ORDER:
        out.extend(cat["name"] for cat in get_categories(channel))
    return out


def make_mask(bdt, topology, mass, weight, category):
    low = category["low"]
    high = category["high"]

    if category["highest"]:
        bdt_mask = (bdt >= low) & (bdt <= high)
    else:
        bdt_mask = (bdt >= low) & (bdt < high)

    return (
        (topology == 1)
        & bdt_mask
        & (mass > MASS_MIN)
        & (mass < MASS_MAX)
        & np.isfinite(mass)
        & np.isfinite(bdt)
        & np.isfinite(weight)
    )


def nominal_file(channel, process):
    return (
        NOMINAL_BASE
        / channel
        / SUBSET
        / f"{process}_Combined_{SUBSET}.root"
    )


def calculate_file(channel, process):
    path = nominal_file(channel, process)
    if not path.is_file():
        raise FileNotFoundError(f"Missing nominal file:\n{path}")

    bdt_branch = f"BDT_{channel}"
    topology_branch = f"is_{channel}_category"
    mass_branch = "diMuon_bsConstrainedMass"

    branches = ["weight", mass_branch, bdt_branch, topology_branch]
    for cfg in SYSTEMATICS.values():
        branches.extend([cfg["nominal"], cfg["up"], cfg["down"]])
    branches = list(dict.fromkeys(branches))

    results = {}
    for category in get_categories(channel):
        results[category["name"]] = {
            "events": 0,
            "nominal": 0.0,
            **{
                syst: {"up": 0.0, "down": 0.0}
                for syst in SYSTEMATICS
            },
        }

    for arrays in uproot.iterate(
        f"{path}:{TREE_NAME}",
        branches,
        library="np",
        step_size="500 MB",
    ):
        weight = np.asarray(arrays["weight"], dtype=np.float64)
        mass = np.asarray(arrays[mass_branch], dtype=np.float64)
        bdt = np.asarray(arrays[bdt_branch], dtype=np.float64)
        topology = np.asarray(arrays[topology_branch])

        varied_weights = {}
        for syst, cfg in SYSTEMATICS.items():
            sf_nom = np.asarray(arrays[cfg["nominal"]], dtype=np.float64)
            sf_up = np.asarray(arrays[cfg["up"]], dtype=np.float64)
            sf_down = np.asarray(arrays[cfg["down"]], dtype=np.float64)

            valid_sf = (
                np.isfinite(sf_nom)
                & np.isfinite(sf_up)
                & np.isfinite(sf_down)
                & (sf_nom != 0.0)
            )
            if not np.all(valid_sf):
                n_bad = np.count_nonzero(~valid_sf)
                raise RuntimeError(
                    f"{path}: {syst} has {n_bad} invalid SF entries"
                )

            varied_weights[syst] = {
                "up": weight * sf_up / sf_nom,
                "down": weight * sf_down / sf_nom,
            }

        for category in get_categories(channel):
            name = category["name"]
            mask = make_mask(bdt, topology, mass, weight, category)

            results[name]["events"] += int(np.count_nonzero(mask))
            results[name]["nominal"] += float(np.sum(weight[mask]))

            for syst in SYSTEMATICS:
                results[name][syst]["up"] += float(
                    np.sum(varied_weights[syst]["up"][mask])
                )
                results[name][syst]["down"] += float(
                    np.sum(varied_weights[syst]["down"][mask])
                )

    return path, results


def calculate_all():
    ratios = {syst: {} for syst in SYSTEMATICS}

    for channel in CHANNELS:
        for process in PROCESSES:
            path, process_results = calculate_file(channel, process)
            print(f"Read: {path}")

            for category in get_categories(channel):
                cat = category["name"]
                nominal = process_results[cat]["nominal"]
                if nominal == 0.0:
                    print(f"[WARNING] zero nominal yield: {cat} / {process}")
                    continue

                for syst in SYSTEMATICS:
                    ratios[syst].setdefault(cat, {})
                    up = process_results[cat][syst]["up"]
                    down = process_results[cat][syst]["down"]
                    ratios[syst][cat][process] = {
                        "nominal": nominal,
                        "up_yield": up,
                        "down_yield": down,
                        "up": up / nominal,
                        "down": down / nominal,
                    }

    return ratios


def print_detailed(ratios):
    print("\n" + "#" * 100)
    print("# DETAILED RESULTS")
    print("#" * 100)

    for syst, cfg in SYSTEMATICS.items():
        print(f"\n{syst} ({cfg['title']})")
        for cat in category_order():
            print(f"\n  {cat}")
            for process, dc_process in PROCESSES.items():
                if cat not in ratios[syst] or process not in ratios[syst][cat]:
                    print(f"    {dc_process}: MISSING")
                    continue
                r = ratios[syst][cat][process]
                print(f"    {dc_process}")
                print(f"      nominal yield = {r['nominal']:.10f}")
                print(f"      down yield    = {r['down_yield']:.10f}")
                print(f"      up yield      = {r['up_yield']:.10f}")
                print(f"      datacard      = {r['down']:.4f}/{r['up']:.4f}")


def print_python_dictionary(ratios):
    print("\n" + "#" * 100)
    print("# COPY/PASTE INTO systematics.py")
    print("#" * 100)
    print()
    print("experimental_systematics = [")

    for syst, cfg in SYSTEMATICS.items():
        print("    {")
        print(f'        "name": "{syst}",')
        print(f'        "title": "{cfg["title"]}",')
        print('        "type": "constant",')
        print('        "prior": "lnN",')
        print('        "correlateAcrossYears": 1,')
        print('        "value": "-",')
        print('        "valueByCatAndProc": {')

        for cat in category_order():
            vals = {}

            for process in PROCESSES:
                proc_key = OUTPUT_PROC_KEYS[process]

                if cat in ratios[syst] and process in ratios[syst][cat]:
                    r = ratios[syst][cat][process]
                    vals[proc_key] = f"{r['down']:.4f}/{r['up']:.4f}"
                else:
                    vals[proc_key] = "-"

            print(
                f'            "{cat}": '
                f'{{"ggH": "{vals["ggH"]}", "qqH": "{vals["qqH"]}"}},'
            )

        print("        },")
        print("    },")

    print("]")

def print_google_sheets(ratios):
    print("\n" + "#" * 100)
    print("# GOOGLE SHEETS — TAB-SEPARATED")
    print("#" * 100)
    print("Systematic\tCategory\tggH_combined_hgg\tqqH_combined_hgg")

    for syst, cfg in SYSTEMATICS.items():
        for cat in category_order():
            values = []
            for process in PROCESSES:
                if cat in ratios[syst] and process in ratios[syst][cat]:
                    r = ratios[syst][cat][process]
                    values.append(f"{r['down']:.4f}/{r['up']:.4f}")
                else:
                    values.append("MISSING")
            print("\t".join([cfg["title"], cat] + values))


def print_datacard_lines(ratios):
    print("\n" + "#" * 100)
    print("# DATACARD LINES")
    print("# Per category: ggH_combined_hgg, qqH_combined_hgg, bkg_mass")
    print("#" * 100)

    for syst, cfg in SYSTEMATICS.items():
        values = []
        complete = True
        for cat in category_order():
            for process in PROCESSES:
                if cat not in ratios[syst] or process not in ratios[syst][cat]:
                    complete = False
                    values.append("MISSING")
                else:
                    r = ratios[syst][cat][process]
                    values.append(f"{r['down']:.4f}/{r['up']:.4f}")
            values.append("-")

        if complete:
            print(f"{cfg['title']} lnN " + " ".join(values))
        else:
            print(f"# {cfg['title']} incomplete; not printing an active line")
            print("# " + " ".join(values))


def main():
    print("Muon efficiency-SF normalization systematics")
    print(f"Mass window: {MASS_MIN} < diMuon_bsConstrainedMass < {MASS_MAX}")
    print("ggH and VBF signal processes are calculated separately.")

    ratios = calculate_all()
    # print_detailed(ratios)
    print_python_dictionary(ratios)
    print_google_sheets(ratios)
    print_datacard_lines(ratios)


if __name__ == "__main__":
    main()
