import matplotlib

# Never open an X11/GUI backend (slow over ssh -X); plots are only saved to disk
matplotlib.use("Agg")

from utils.dy_stitching import (
    MASS_VARIABLE,
    HistogramSet,
    cell_view,
    fill_from_file,
    print_summary,
    draw_neff,
    draw_yield,
    draw_weight_distribution,
    draw_shape,
    draw_stack,
    draw_composition,
    sum_sets,
    write_closure_table,
)
from concurrent.futures import ProcessPoolExecutor, as_completed
from utils.helper import get_output_directory
from utils.labels import variables_type
import argparse
import glob
import os
import time

# Validation of the all-aMC@NLO (FxFx) DY stitching (lib/DYStitching.h, scripts/compute_DY_stitching.py):
#  Usage: python3 plot_DY_stitching.py [era|all] [-j N_JOBS]
all_eras = ["2022", "2022EE", "2023", "2023BPix", "2024", "2025"]
parser = argparse.ArgumentParser()
parser.add_argument("era", nargs="?", default="all", choices=all_eras + ["Combined", "all"])
parser.add_argument("-j", "--jobs", type=int, default=1,
                    help="number of files read in parallel (each job uses ~1 GB; default 1)")
args = parser.parse_args()
era_arg = args.era
eras = all_eras if era_arg in ["all", "Combined"] else [era_arg]
draw_combined = era_arg in ["all", "Combined"]

STITCHED_TUPLES_VERSION = "2.7.0"
POWHEG_TUPLES_VERSION = "2.5.0"  # made before any stitching, so the POWHEG samples are complete
DATA_TUPLES_VERSION = "2.6.0"    # data is not affected by the DY stitching

N_PARTON_BINS = 3
WINDOW_CELLS = {p: [1 + 2 * p, 2 + 2 * p] for p in range(N_PARTON_BINS)}
R_CELLS = [2 + 2 * p for p in range(N_PARTON_BINS)]

# Data datasets per era, as in root_io/tuples/hadd_tuples_EOS.sh. 2025 MC is normalized to the
# 2025 + 2026 luminosity in CreateTuple, so the 2026 data is included with 2025.
data_datasets = {
    "2022": ["Muon_2022C", "Muon_2022D", "SingleMuon_2022C"],
    "2022EE": ["Muon*_2022E", "Muon*_2022F", "Muon*_2022G"],
    "2023": ["Muon*_2023C*"],
    "2023BPix": ["Muon*_2023D*"],
    "2024": ["Muon*_2024*"],
    "2025": ["Muon*_2025*", "Muon*_2026*"],
}


def tuples_directory(version):
    analyzer_version = ".".join(version.split(".")[:2])
    # DY_STITCH_TUPLES_BASE overrides the EOS base directory (e.g. for tests on a local copy)
    base = os.getenv("DY_STITCH_TUPLES_BASE", f"/eos/uscms/store/group/lpchmumu/{os.getenv('USER')}")
    return f"{base}/analyzer_HiggsMuMu_v{analyzer_version}/tuples_v{version}/"


def get_files(version, datasets):
    files = []
    for dataset in datasets:
        files += glob.glob(tuples_directory(version) + dataset + "/*_tuples.root")
    return sorted(files)


def with_extensions(dataset):
    return [dataset, dataset + "_ext1", dataset + "_ext2"]


def get_dataset_groups(era):
    """group -> (tuples version, dataset names, {component: view})"""
    campaign = "Summer" + era[2:]
    prefix = "DYto2Mu-2Jets" if era in ["2024", "2025"] else "DYto2L-2Jets"
    groups = {}
    for p in range(N_PARTON_BINS):
        groups[f"aMC@NLO {p}J"] = (STITCHED_TUPLES_VERSION, with_extensions(f"{prefix}_{p}J_{campaign}"), {
            f"J{p}_out": cell_view([0]),
            f"J{p}_in": cell_view(WINDOW_CELLS[p]),
            f"J{p}_in_raw": cell_view(WINDOW_CELLS[p], raw=True),
            f"J{p}_R_raw": cell_view([R_CELLS[p]], raw=True),
        })
    U_views = {"U": "all", "UR_raw": cell_view(R_CELLS, raw=True)}
    for p in range(N_PARTON_BINS):
        U_views[f"U{p}"] = cell_view(WINDOW_CELLS[p])
        U_views[f"U{p}_raw"] = cell_view(WINDOW_CELLS[p], raw=True)
    F_views = {"F": "all", "F_raw": "raw"}
    for p in range(N_PARTON_BINS):
        F_views[f"F{p}"] = cell_view([R_CELLS[p]])
    groups["aMC@NLO 105-160"] = (STITCHED_TUPLES_VERSION,
                                 with_extensions("DYto2Mu-2Jets_105to160_" + campaign), U_views)
    groups["aMC@NLO VBF-filtered"] = (STITCHED_TUPLES_VERSION, ["DYto2Mu-2Jets_105to160_VBFFilter_" + campaign],
                                      F_views)
    groups["POWHEG"] = (POWHEG_TUPLES_VERSION, ["DY50to120_" + campaign, "DY120to200_" + campaign],
                        {"POWHEG_full": "all"})
    return groups


COMPONENTS = [view for _, _, views in get_dataset_groups("2024").values() for view in views]
OPTIONAL_GROUPS = ["POWHEG"]

# Legend labels
LABEL_JET_BINNED = "DY aMC@NLO 0J+1J+2J only"
LABEL_STITCHED = "DY aMC@NLO stitched"
LABEL_POWHEG = "DY POWHEG"
STACK_LABELS = {
    "J_out": r"0J+1J+2J, LHE $m_{\mu\mu}$ outside 105-160",
    "J_in": r"0J+1J+2J in 105-160 $\times f_J$",
    "U": r"105-160 $\times f_U$",
    "F": r"105-160 VBF-filtered $\times f_F$",
}

categories = [
    "inclusive",
    "ggH",
    "VBF",
]

# BDT input variables (same list as plot_sig_vs_bg.py)
variables = [
    "diMuon_rapidity",
    "diMuon_pt",
    "mu1_pt_mass_ratio",
    "mu2_pt_mass_ratio",
    "mu1_eta",
    "mu2_eta",
    "phi_CS",
    "cos_theta_CS",
    "n_jet",
    "leading_jet_pt",
    "subleading_jet_pt",
    "leading_jet_eta",
    "diJet_mass",
    "delta_eta_diJet",
    "delta_phi_diJet",
    "z_zeppenfeld",
    "min_delta_eta_diMuon_jet",
    "min_delta_phi_diMuon_jet",
    "pt_balance",
    "pt_centrality",
    "n_SoftJet_pt2",
    "n_SoftJet_pt5",
    "n_SoftJet_pt10",
    "HT",
    "HT_pt2",
    "HT_pt5",
    "HT_pt10",
]

# Jet variables to bin N_eff in (inside the mass window)
neff_jet_variables = ["diJet_mass", "delta_eta_diJet"]

branches = ["weight", "is_ggH_category", "is_VBF_category", MASS_VARIABLE] + variables


def fill_task(era, group, path, views, is_data):
    try:
        hsets = fill_from_file(path, f"{era} {group}", branches, categories, variables,
                               neff_jet_variables, is_data=is_data, verbose=False, views=views)
    except Exception as error:
        print(f"[WARNING] Could not read {path}: {error}", flush=True)
        hsets = None
    return era, group, hsets


def draw_closure(first_label, first, second_label, second, third, era, category, output_directory):
    """MC-only closure plots of two independent predictions of the same phase space (and the stitched sum)"""
    samples = {first_label: first, second_label: second}
    if third is not None:
        samples.update(third)
    draw_yield(samples, MASS_VARIABLE, category, era, output_directory)
    for variable in variables:
        draw_shape(samples, variable, category, era, output_directory + "shapes/")
        draw_yield(samples, variable, category, era,
                   get_output_directory(variable, output_directory + "yields/", variables_type),
                   name="shape_" + variable)


def draw_era(era, components, data):
    start = time.time()
    print("\n" + "#" * 78 + "\nDrawing era: " + era, flush=True)
    c = components
    ps = range(N_PARTON_BINS)
    J_out = sum_sets(*[c[f"J{p}_out"] for p in ps])
    J_in = sum_sets(*[c[f"J{p}_in"] for p in ps])
    J_in_raw = sum_sets(*[c[f"J{p}_in_raw"] for p in ps])
    main = {
        LABEL_JET_BINNED: sum_sets(J_out, J_in_raw),
        LABEL_STITCHED: sum_sets(J_out, J_in, c["U"], c["F"]),
    }
    if "POWHEG_full" in c:
        main[LABEL_POWHEG] = c["POWHEG_full"]
    stack = {STACK_LABELS["J_out"]: J_out, STACK_LABELS["J_in"]: J_in,
             STACK_LABELS["U"]: c["U"], STACK_LABELS["F"]: c["F"]}
    overlays = {label: hset for label, hset in main.items() if label != LABEL_STITCHED}

    era_directory = "../plots/DY_stitching_amcnlo/" + era + "/"
    for p in ps:
        write_closure_table(f"{p}J standalone in W", c[f"J{p}_in_raw"], f"105-160 standalone, p={p}",
                            c[f"U{p}_raw"], categories, variables, era_directory + f"closure_chi2_p{p}_{era}.txt")
    write_closure_table("105-160 standalone in R", c["UR_raw"], "VBF-filtered standalone", c["F_raw"],
                        categories, variables, era_directory + f"closure_chi2_R_{era}.txt")

    for category in categories:
        output_directory = era_directory + category + "/"
        print_summary(main, category, era)
        print_summary({name: c[name] for name in COMPONENTS if name in c}, category, era)

        # Main comparison
        draw_neff(main, MASS_VARIABLE, category, era, output_directory, "mass")
        draw_yield(main, MASS_VARIABLE, category, era, output_directory, data=data)
        draw_weight_distribution(main, category, era, output_directory)
        draw_weight_distribution(stack, category, era, output_directory + "stack/")
        for variable in neff_jet_variables:
            draw_neff(main, variable, category, era, output_directory, "neff_" + variable)

        # Stacks, hand-off at 105 / 160 GeV and the Z peak
        draw_stack(stack, overlays, MASS_VARIABLE, category, era, output_directory + "stack/", "mass", data=data)
        draw_stack(stack, overlays, MASS_VARIABLE, category, era, output_directory + "handoff/", "mass_wide",
                   data=data, file_prefix="handoff")
        draw_composition(stack, MASS_VARIABLE, category, era, output_directory + "composition/", "mass")

        # Closure inside W, per parton multiplicity and in R (MC only)
        for p in ps:
            print(f"[{era} {category}] closure p={p}", flush=True)
            draw_closure(f"{p}J standalone", c[f"J{p}_in_raw"], "105-160 standalone", c[f"U{p}_raw"],
                         {"Stitched": sum_sets(c[f"J{p}_in"], c[f"U{p}"], c[f"F{p}"])},
                         era, category, output_directory + f"closure_p{p}/")
        print(f"[{era} {category}] closure R", flush=True)
        draw_closure("105-160 standalone in R", c["UR_raw"], "VBF-filtered standalone", c["F_raw"],
                     {"0J+1J+2J standalone in R": sum_sets(*[c[f"J{p}_R_raw"] for p in ps])},
                     era, category, output_directory + "closure_R/")

        for i, variable in enumerate(variables):
            print(f"[{era} {category}] variable {i + 1}/{len(variables)}: {variable}", flush=True)
            # Shapes and yields in the blinded window (same mass region as data)
            draw_shape(main, variable, category, era, output_directory + "shapes/", data=data,
                       name="blinded_" + variable)
            draw_yield(main, variable, category, era,
                       get_output_directory(variable, output_directory + "yields/", variables_type),
                       name="blinded_" + variable, data=data, label_suffix=", 120-130 GeV removed")
            draw_stack(stack, overlays, variable, category, era,
                       get_output_directory(variable, output_directory + "stack/", variables_type),
                       "blinded_" + variable, data=data, label_suffix=", 120-130 GeV removed")
            draw_composition(stack, variable, category, era,
                             get_output_directory(variable, output_directory + "composition/", variables_type),
                             "shape_" + variable)
    print(f"[{era}] Drawing done in {time.time() - start:.0f}s", flush=True)


# Decide which files to read
tasks = []
eras_read = []
for era in eras:
    groups = get_dataset_groups(era)
    # Every sample is needed (its extensions are optional), except the POWHEG comparison
    missing = [group for group, (version, datasets, _) in groups.items()
               if group not in OPTIONAL_GROUPS and not get_files(version, datasets[:1])]
    if missing:
        message = "Missing input tuples for era " + era + ": " + ", ".join(missing)
        if len(eras) == 1:
            print("[ERROR] " + message)
            exit(1)
        print("[WARNING] " + message + " -- skipping")
        continue
    eras_read.append(era)
    for group, (version, datasets, views) in groups.items():
        tasks += [(era, group, path, views, False) for path in get_files(version, datasets)]
    data_files = get_files(DATA_TUPLES_VERSION, data_datasets[era])
    if data_files:
        # 120-130 GeV is removed at read time (blinding); data is compared to DY only
        tasks += [(era, "Data", path, {"Data": "all"}, True) for path in data_files]
    else:
        print("[INFO] No data tuples for era " + era + ", MC-only plots")

if not eras_read:
    print("[ERROR] No era with all the input tuples")
    exit(1)

print(f"Reading {len(tasks)} files with {args.jobs} job(s); "
      f"total {sum(os.path.getsize(t[2]) for t in tasks) / 1024**3:.1f} GB", flush=True)
for era in eras_read:
    for group in list(get_dataset_groups(era)) + ["Data"]:
        n_files = sum(1 for task in tasks if task[0] == era and task[1] == group)
        print(f"  {era} {group}: {n_files} files")

total_start = time.time()
results = {}
n_failed = 0


def add_result(era, group, hsets, n_done):
    global n_failed
    if hsets is None:
        n_failed += 1
    else:
        for name, hset in hsets.items():
            if (era, name) in results:
                results[(era, name)] += hset
            else:
                results[(era, name)] = hset
    if n_done % 50 == 0 or n_done == len(tasks):
        print(f"==> Files done: {n_done}/{len(tasks)} "
              f"(elapsed {time.time() - total_start:.0f}s)", flush=True)


if args.jobs > 1:
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(fill_task, *task) for task in tasks]
        for n_done, future in enumerate(as_completed(futures), start=1):
            add_result(*future.result(), n_done)
else:
    for n_done, task in enumerate(tasks, start=1):
        add_result(*fill_task(*task), n_done)
if n_failed:
    print(f"[WARNING] {n_failed} file(s) could not be read and were skipped")

eras_to_draw = list(eras_read)
if draw_combined:
    print("[INFO] Combined histograms = sum of " + ", ".join(eras_read), flush=True)
    for name in COMPONENTS + ["Data"]:
        combined = HistogramSet()
        for era in eras_read:
            if (era, name) in results:
                combined += results[(era, name)]
        if combined.hists:
            results[("Combined", name)] = combined
    eras_to_draw = (eras_to_draw + ["Combined"]) if era_arg == "all" else ["Combined"]

draw_args = [(era, {name: results[(era, name)] for name in COMPONENTS if (era, name) in results},
              results.get((era, "Data")))
             for era in eras_to_draw]
if args.jobs > 1 and len(draw_args) > 1:
    # Eras are drawn in parallel; output lines are prefixed with the era
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        for future in as_completed([pool.submit(draw_era, *draw_arg) for draw_arg in draw_args]):
            future.result()
else:
    for draw_arg in draw_args:
        draw_era(*draw_arg)

print(f"\nAll done in {time.time() - total_start:.0f}s", flush=True)
