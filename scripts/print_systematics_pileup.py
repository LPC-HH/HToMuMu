#!/usr/bin/env python3

import json
from pathlib import Path

import numpy as np
import uproot
from systematics_config import (
    BDT_CUTS,
    CHANNELS,
    DATACARD_CATEGORY_ORDER,
    FLASHGG_PATH,
    MASS_MAX,
    MASS_MIN,
    NOMINAL_BDT_SCORE_DIR,
    PROCESSES,
    SUBSET,
    TREE_NAME,
    VARIANT_CHANNEL,
)

OUTPUT_PROC_KEYS = {
    "ggH": "ggH",
    "VBF": "qqH",
}


NOMINAL_BASE = NOMINAL_BDT_SCORE_DIR

OUTPUT_JSON = (
    FLASHGG_PATH + "Datacard/experimental_systematics/pileup_systematics.json"
)


SYSTEMATICS = {
    "pileup": {
        "title": "CMS_pileup",
        "nominal": "pileup_weight",
        "up": "pileup_weight_up",
        "down": "pileup_weight_down",
    },
}


def get_categories(channel):
    intervals = list(
        zip(
            BDT_CUTS[channel][:-1],
            BDT_CUTS[channel][1:],
        )
    )

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


def make_mask(
    bdt,
    topology,
    mass,
    weight,
    category,
):
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
    return NOMINAL_BASE / VARIANT_CHANNEL[channel] / SUBSET / f"{process}_Combined_{SUBSET}.root"


def calculate_file(channel, process):

    path = nominal_file(channel, process)

    if not path.is_file():
        raise FileNotFoundError(f"Missing nominal file:\n{path}")

    bdt_branch = f"BDT_{channel}"
    topology_branch = f"is_{channel}_category"
    mass_branch = "diMuon_bsConstrainedMass"

    branches = [
        "weight",
        mass_branch,
        bdt_branch,
        topology_branch,
        "pileup_weight",
        "pileup_weight_up",
        "pileup_weight_down",
    ]

    results = {}

    for category in get_categories(channel):
        results[category["name"]] = {
            "events": 0,
            "nominal": 0.0,
            "pileup": {
                "up": 0.0,
                "down": 0.0,
            },
        }

    for arrays in uproot.iterate(
        f"{path}:{TREE_NAME}",
        branches,
        library="np",
        step_size="500 MB",
    ):

        weight = np.asarray(
            arrays["weight"],
            dtype=np.float64,
        )

        mass = np.asarray(
            arrays[mass_branch],
            dtype=np.float64,
        )

        bdt = np.asarray(
            arrays[bdt_branch],
            dtype=np.float64,
        )

        topology = np.asarray(arrays[topology_branch])

        pileup_nom = np.asarray(
            arrays["pileup_weight"],
            dtype=np.float64,
        )

        pileup_up = np.asarray(
            arrays["pileup_weight_up"],
            dtype=np.float64,
        )

        pileup_down = np.asarray(
            arrays["pileup_weight_down"],
            dtype=np.float64,
        )

        # ----------------------------------------------------------
        # Check pileup weights
        # ----------------------------------------------------------

        valid_pileup = (
            np.isfinite(pileup_nom)
            & np.isfinite(pileup_up)
            & np.isfinite(pileup_down)
            & (pileup_nom != 0.0)
        )

        if not np.all(valid_pileup):

            n_bad = np.count_nonzero(~valid_pileup)

            raise RuntimeError(f"{path}: pileup has " f"{n_bad} invalid weight entries")

        # ----------------------------------------------------------
        # Construct varied total event weights
        #
        # weight already contains pileup_weight.
        #
        # Therefore:
        #
        #   weight_up =
        #       weight
        #       / pileup_weight
        #       * pileup_weight_up
        #
        # ----------------------------------------------------------

        weight_up = weight * pileup_up / pileup_nom

        weight_down = weight * pileup_down / pileup_nom

        # ----------------------------------------------------------
        # Category yields
        # ----------------------------------------------------------

        for category in get_categories(channel):

            name = category["name"]

            mask = make_mask(
                bdt,
                topology,
                mass,
                weight,
                category,
            )

            results[name]["events"] += int(np.count_nonzero(mask))

            results[name]["nominal"] += float(np.sum(weight[mask]))

            results[name]["pileup"]["up"] += float(np.sum(weight_up[mask]))

            results[name]["pileup"]["down"] += float(np.sum(weight_down[mask]))

    return path, results


def calculate_all():

    ratios = {syst: {} for syst in SYSTEMATICS}

    for channel in CHANNELS:

        for process in PROCESSES:

            path, process_results = calculate_file(
                channel,
                process,
            )

            print(f"Read: {path}")

            for category in get_categories(channel):

                cat = category["name"]

                nominal = process_results[cat]["nominal"]

                if nominal == 0.0:
                    print(f"[WARNING] zero nominal yield: " f"{cat} / {process}")
                    continue

                for syst in SYSTEMATICS:

                    ratios[syst].setdefault(
                        cat,
                        {},
                    )

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

                print(f"      nominal yield = " f"{r['nominal']:.10f}")

                print(f"      down yield    = " f"{r['down_yield']:.10f}")

                print(f"      up yield      = " f"{r['up_yield']:.10f}")

                print(f"      datacard      = " f"{r['down']:.6f}/" f"{r['up']:.6f}")


def save_json(
    ratios,
    output_path=OUTPUT_JSON,
):

    output = {
        "ggH": {"categories": {}},
        "qqH": {"categories": {}},
    }

    for syst in SYSTEMATICS:

        for cat in category_order():

            for process in PROCESSES:

                proc_key = OUTPUT_PROC_KEYS[process]

                if cat not in ratios[syst] or process not in ratios[syst][cat]:
                    continue

                r = ratios[syst][cat][process]

                output[proc_key]["categories"].setdefault(
                    cat,
                    {},
                )

                output[proc_key]["categories"][cat][syst] = [
                    round(r["down"], 6),
                    round(r["up"], 6),
                ]

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(output_path, "w") as f:
        json.dump(
            output,
            f,
            indent=4,
        )

    print(f"\nSaved JSON: {output_path}")


def main():

    print("Pileup normalization systematic")

    print(
        f"Mass window: " f"{MASS_MIN} < " f"diMuon_bsConstrainedMass < " f"{MASS_MAX}"
    )

    print("ggH and VBF signal processes " "are calculated separately.")

    ratios = calculate_all()

    print_detailed(ratios)

    save_json(ratios)


if __name__ == "__main__":
    main()
