#!/usr/bin/env python3

import json
import sys
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
    PROCESSES,
    SUBSET,
    TREE_NAME,
)

OUTPUT_JSON = (
    FLASHGG_PATH + "Datacard/experimental_systematics/pt_systematics.json"
)

# Process keys expected by valueByCatAndProc
OUTPUT_PROC_KEYS = {
    "ggH": "ggH",
    "VBF": "qqH",
}

def save_json(ratios, output_path=OUTPUT_JSON):
    output = {
        "ggH": {"categories": {}},
        "qqH": {"categories": {}},
    }

    for systematic in ALL_SYSTEMATICS:
        for cat in category_order():
            for process in PROCESSES:
                proc_key = OUTPUT_PROC_KEYS[process]

                if (cat not in ratios[systematic]
                    or process not in ratios[systematic][cat]):
                    continue

                r = ratios[systematic][cat][process]

                output[proc_key]["categories"].setdefault(cat, {})

                output[proc_key]["categories"][cat][systematic] = [
                    round(r["down"], 6),
                    round(r["up"], 6),
                ]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(output, f, indent=4)

    print(f"\nSaved JSON: {output_path}")



OUTPUT_TXT = "muon_pt_jet_systematics.txt"


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


TUPLE_BASE = Path(
    "/eos/uscms/store/user/lpchmumu/mbarrial/analyzer_HiggsMuMu_v2.1/tuples_v2.1.0"
)

TUPLE_BASE_NOMINAL = Path("./root_io/tuples/")

NOMINAL_BASE = TUPLE_BASE_NOMINAL / "BDT_score"
SYSTEMATICS_BASE = TUPLE_BASE / "systematics/BDT_score"

MUON_PT_SYSTEMATICS = [
    "scale",
    "smearing",
]

JET_SYSTEMATICS = [
    "CMS_scale_j_FlavorQCD",
    "CMS_scale_j_RelativeBal",
    "CMS_scale_j_HF",
    "CMS_scale_j_BBEC1",
    "CMS_scale_j_EC2",
    "CMS_scale_j_Absolute",
    "CMS_scale_j_BBEC1_2022",
    "CMS_scale_j_RelativeSample_2022",
    "CMS_scale_j_EC2_2022",
    "CMS_scale_j_HF_2022",
    "CMS_scale_j_Absolute_2022",
    "CMS_scale_j_BBEC1_2022EE",
    "CMS_scale_j_RelativeSample_2022EE",
    "CMS_scale_j_EC2_2022EE",
    "CMS_scale_j_HF_2022EE",
    "CMS_scale_j_Absolute_2022EE",
    "CMS_scale_j_BBEC1_2023",
    "CMS_scale_j_RelativeSample_2023",
    "CMS_scale_j_EC2_2023",
    "CMS_scale_j_HF_2023",
    "CMS_scale_j_Absolute_2023",
    "CMS_scale_j_BBEC1_2023BPix",
    "CMS_scale_j_RelativeSample_2023BPix",
    "CMS_scale_j_EC2_2023BPix",
    "CMS_scale_j_HF_2023BPix",
    "CMS_scale_j_Absolute_2023BPix",
    "CMS_scale_j_BBEC1_2024",
    "CMS_scale_j_RelativeSample_2024",
    "CMS_scale_j_EC2_2024",
    "CMS_scale_j_HF_2024",
    "CMS_scale_j_Absolute_2024",
    "CMS_scale_j_BBEC1_2025",
    "CMS_scale_j_RelativeSample_2025",
    "CMS_scale_j_EC2_2025",
    "CMS_scale_j_HF_2025",
    "CMS_scale_j_Absolute_2025",
    "CMS_res_j_eta0to1p93_pt0toInf_2022",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2022",
    "CMS_res_j_eta2p5to3p0_pt0to50_2022",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2022",
    "CMS_res_j_eta3to5_pt0to50_2022",
    "CMS_res_j_eta3to5_pt50toInf_2022",
    "CMS_res_j_eta0to1p93_pt0toInf_2022EE",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2022EE",
    "CMS_res_j_eta2p5to3p0_pt0to50_2022EE",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2022EE",
    "CMS_res_j_eta3to5_pt0to50_2022EE",
    "CMS_res_j_eta3to5_pt50toInf_2022EE",
    "CMS_res_j_eta0to1p93_pt0toInf_2023",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2023",
    "CMS_res_j_eta2p5to3p0_pt0to50_2023",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2023",
    "CMS_res_j_eta3to5_pt0to50_2023",
    "CMS_res_j_eta3to5_pt50toInf_2023",
    "CMS_res_j_eta0to1p93_pt0toInf_2023BPix",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2023BPix",
    "CMS_res_j_eta2p5to3p0_pt0to50_2023BPix",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2023BPix",
    "CMS_res_j_eta3to5_pt0to50_2023BPix",
    "CMS_res_j_eta3to5_pt50toInf_2023BPix",
    "CMS_res_j_eta0to1p93_pt0toInf_2024",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2024",
    "CMS_res_j_eta2p5to3p0_pt0to50_2024",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2024",
    "CMS_res_j_eta3to5_pt0to50_2024",
    "CMS_res_j_eta3to5_pt50toInf_2024",
    "CMS_res_j_eta0to1p93_pt0toInf_2025",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2025",
    "CMS_res_j_eta2p5to3p0_pt0to50_2025",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2025",
    "CMS_res_j_eta3to5_pt0to50_2025",
    "CMS_res_j_eta3to5_pt50toInf_2025",
]

ALL_SYSTEMATICS = MUON_PT_SYSTEMATICS + JET_SYSTEMATICS

DATACARD_TITLES = {
    "scale": "CMS_scale_m",
    "smearing": "CMS_res_m",
}


def datacard_title(systematic):
    return DATACARD_TITLES.get(systematic, systematic)


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
    return NOMINAL_BASE / channel / SUBSET / f"{process}_Combined_{SUBSET}.root"


def systematic_file(channel, process, systematic, direction):
    return (
        SYSTEMATICS_BASE
        / channel
        / SUBSET
        / f"{process}_Combined_{systematic}_{direction}_tuples.root"
    )


def read_category_yields(path, channel):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)

    bdt_branch = f"BDT_{channel}"
    topology_branch = f"is_{channel}_category"
    mass_branch = "diMuon_bsConstrainedMass"
    branches = ["weight", mass_branch, bdt_branch, topology_branch]

    yields = {cat["name"]: 0.0 for cat in get_categories(channel)}
    events = {cat["name"]: 0 for cat in get_categories(channel)}

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

        for category in get_categories(channel):
            name = category["name"]
            mask = make_mask(bdt, topology, mass, weight, category)
            yields[name] += float(np.sum(weight[mask]))
            events[name] += int(np.count_nonzero(mask))

    return yields, events


def calculate_nominal():
    nominal = {}

    for channel in CHANNELS:
        nominal[channel] = {}

        for process in PROCESSES:
            path = nominal_file(channel, process)
            if not path.is_file():
                raise FileNotFoundError(
                    f"Missing nominal file for {channel} / {process}:\n{path}"
                )

            print(f"Nominal {channel} / {process}: {path}")
            yields, events = read_category_yields(path, channel)
            nominal[channel][process] = {
                "path": path,
                "yields": yields,
                "events": events,
            }

    return nominal


def calculate_all(nominal):
    ratios = {syst: {} for syst in ALL_SYSTEMATICS}
    missing = []

    for i_syst, systematic in enumerate(ALL_SYSTEMATICS, start=1):
        print(f"\n[{i_syst}/{len(ALL_SYSTEMATICS)}] {systematic}")

        for channel in CHANNELS:
            for process in PROCESSES:
                up_path = systematic_file(channel, process, systematic, "up")
                down_path = systematic_file(channel, process, systematic, "down")

                if not up_path.is_file() or not down_path.is_file():
                    if not up_path.is_file():
                        missing.append((systematic, channel, process, "up", up_path))
                    if not down_path.is_file():
                        missing.append(
                            (systematic, channel, process, "down", down_path)
                        )
                    print(f"  [MISSING] {channel} / {process}")
                    continue

                up_yields, up_events = read_category_yields(up_path, channel)
                down_yields, down_events = read_category_yields(down_path, channel)
                print(f"  OK {channel} / {process}")

                for category in get_categories(channel):
                    cat = category["name"]
                    nominal_yield = nominal[channel][process]["yields"][cat]

                    if nominal_yield == 0.0:
                        print(
                            f"  [WARNING] zero nominal yield: "
                            f"{systematic} / {cat} / {process}"
                        )
                        continue

                    ratios[systematic].setdefault(cat, {})
                    ratios[systematic][cat][process] = {
                        "nominal": nominal_yield,
                        "nominal_events": nominal[channel][process]["events"][cat],
                        "up_yield": up_yields[cat],
                        "up_events": up_events[cat],
                        "down_yield": down_yields[cat],
                        "down_events": down_events[cat],
                        "up": up_yields[cat] / nominal_yield,
                        "down": down_yields[cat] / nominal_yield,
                    }

    return ratios, missing


def print_detailed(ratios):
    print("\n" + "#" * 100)
    print("# DETAILED RESULTS")
    print("#" * 100)

    for systematic in ALL_SYSTEMATICS:
        print(f"\n{systematic} ({datacard_title(systematic)})")
        for cat in category_order():
            print(f"\n  {cat}")
            for process, dc_process in PROCESSES.items():
                if (
                    cat not in ratios[systematic]
                    or process not in ratios[systematic][cat]
                ):
                    print(f"    {dc_process}: MISSING")
                    continue

                r = ratios[systematic][cat][process]
                print(f"    {dc_process}")
                print(f"      nominal events = {r['nominal_events']}")
                print(f"      down events    = {r['down_events']}")
                print(f"      up events      = {r['up_events']}")
                print(f"      nominal yield  = {r['nominal']:.10f}")
                print(f"      down yield     = {r['down_yield']:.10f}")
                print(f"      up yield       = {r['up_yield']:.10f}")
                print(f"      datacard       = {r['down']:.4f}/{r['up']:.4f}")


def print_python_dictionary(ratios):
    print("\n" + "#" * 100)
    print("# COPY/PASTE INTO systematics.py")
    print("#" * 100)
    print()
    print("experimental_systematics = [")

    for systematic in ALL_SYSTEMATICS:
        print("    {")
        print(f'        "name": "{systematic}",')
        print(f'        "title": "{datacard_title(systematic)}",')
        print('        "type": "constant",')
        print('        "prior": "lnN",')
        print('        "correlateAcrossYears": 1,')
        print('        "value": "-",')
        print('        "valueByCatAndProc": {')

        for cat in category_order():
            vals = {}

            for process in PROCESSES:
                proc_key = OUTPUT_PROC_KEYS[process]

                if cat in ratios[systematic] and process in ratios[systematic][cat]:
                    r = ratios[systematic][cat][process]
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

    for systematic in ALL_SYSTEMATICS:
        for cat in category_order():
            values = []
            for process in PROCESSES:
                if cat in ratios[systematic] and process in ratios[systematic][cat]:
                    r = ratios[systematic][cat][process]
                    values.append(f"{r['down']:.4f}/{r['up']:.4f}")
                else:
                    values.append("MISSING")
            print("\t".join([datacard_title(systematic), cat] + values))


def print_datacard_lines(ratios):
    print("\n" + "#" * 100)
    print("# DATACARD LINES")
    print("# Per category: ggH_combined_hgg, qqH_combined_hgg, bkg_mass")
    print("#" * 100)

    for systematic in ALL_SYSTEMATICS:
        values = []
        complete = True
        for cat in category_order():
            for process in PROCESSES:
                if (
                    cat not in ratios[systematic]
                    or process not in ratios[systematic][cat]
                ):
                    complete = False
                    values.append("MISSING")
                else:
                    r = ratios[systematic][cat][process]
                    values.append(f"{r['down']:.4f}/{r['up']:.4f}")
            values.append("-")

        title = datacard_title(systematic)
        if complete:
            print(f"{title} lnN " + " ".join(values))
        else:
            print(f"# {title} incomplete; not printing an active line")
            print("# " + " ".join(values))


def print_missing(missing):
    print("\n" + "#" * 100)
    print("# MISSING SYSTEMATIC FILES")
    print("#" * 100)

    if not missing:
        print("None")
        return

    for systematic, channel, process, direction, path in missing:
        print(f"{systematic} | {channel} | {process} | " f"{direction} | {path}")


def main():
    original_stdout = sys.stdout

    with open(OUTPUT_TXT, "w") as output_file:
        sys.stdout = Tee(original_stdout, output_file)

        try:
            print("Muon-pT + JES/JER normalization systematics")
            print(f"Mass window: {MASS_MIN} < diMuon_bsConstrainedMass < {MASS_MAX}")
            print("The stored weight is used unchanged in every shifted tuple.")
            print("ggH and VBF signal processes are NEVER summed.")
            print(f"Output saved to: {OUTPUT_JSON}")

            nominal = calculate_nominal()
            ratios, missing = calculate_all(nominal)
            save_json(ratios)
            #print_detailed(ratios)
            print_python_dictionary(ratios)
            print_google_sheets(ratios)
            #print_datacard_lines(ratios)
            print_missing(missing)

        finally:
            sys.stdout = original_stdout

    print(f"\nAll output was saved to: {OUTPUT_TXT}")


if __name__ == "__main__":
    main()
