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
    write_normalisation_table,
    mass_coverage,
    covers,
    REGIONS,
)
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, as_completed, wait
from utils.helper import get_output_directory
from utils.labels import variables_type
import utils.dy_stitching as dys
import argparse
import glob
import hashlib
import inspect
import os
import pickle
import time

# Validation of the all-aMC@NLO (FxFx) DY stitching (lib/DYStitching.h, scripts/compute_DY_stitching.py):
#  Usage: python3 plot_DY_stitching.py [era|all] [-j N_JOBS] [--stitched-version X.Y.Z] [--data-version X.Y.Z]
all_eras = ["2022", "2022EE", "2023", "2023BPix", "2024", "2025"]
parser = argparse.ArgumentParser()
parser.add_argument("era", nargs="?", default="all", choices=all_eras + ["Combined", "all"])
parser.add_argument("-j", "--jobs", type=int, default=1,
                    help="number of files read in parallel (each job uses ~1 GB; default 1)")
parser.add_argument("--stitched-version", default="2.7.0", help="tuples version of the aMC@NLO DY samples")
parser.add_argument("--data-version", default="2.7.0", help="tuples version of the data")
parser.add_argument("--no-xrootd", action="store_true",
                    help="read /eos/uscms files through the FUSE mount instead of xrootd (root://cmseos.fnal.gov/)")
parser.add_argument("--from-cache", action="store_true",
                    help="draw from the histograms saved by the last full read instead of reading the tuples again")
parser.add_argument("--cache-file", default=None,
                    help="histogram cache (default: ../plots/DY_stitching_amcnlo/cache/histograms_<era>.pkl)")
parser.add_argument("--file-timeout", type=float, default=600,
                    help="with -j > 1: skip a file whose read takes longer than this many seconds (default 600)")
args = parser.parse_args()
era_arg = args.era
eras = all_eras if era_arg in ["all", "Combined"] else [era_arg]
draw_combined = era_arg in ["all", "Combined"]

STITCHED_TUPLES_VERSION = args.stitched_version
DATA_TUPLES_VERSION = args.data_version      # data is not affected by the DY stitching

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
    return groups


COMPONENTS = [view for _, _, views in get_dataset_groups("2024").values() for view in views]

# Legend labels
LABEL_JET_BINNED = "DY aMC@NLO 0J+1J+2J only"
LABEL_STITCHED = "DY aMC@NLO stitched"
LABEL_NP = "{p}J (FxFx), all samples"
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


EOS_FUSE_PREFIX = "/eos/uscms/"
XROOTD_REDIRECTOR = "root://cmseos.fnal.gov//"


def read_path(path):
    """xrootd URL for files under the /eos/uscms FUSE mount (FUSE reads can stall indefinitely; xrootd reads time
    out with an error instead). Other paths (e.g. a local DY_STITCH_TUPLES_BASE) are read as they are."""
    if args.no_xrootd or not path.startswith(EOS_FUSE_PREFIX):
        return path
    return XROOTD_REDIRECTOR + path[len(EOS_FUSE_PREFIX):]


def fill_task(era, group, path, views, is_data):
    try:
        hsets = fill_from_file(read_path(path), f"{era} {group}", branches, categories, variables,
                               neff_jet_variables, is_data=is_data, verbose=False, views=views)
    except Exception as error:
        print(f"[WARNING] Could not read {path}: {error}", flush=True)
        hsets = None
    return era, group, hsets, path


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


def draw_regions(era, category, output_directory, main, stack, stack_np, overlays, data):
    """Every variable (and the mass) in the extra mass regions (utils.dy_stitching.REGIONS), for the regions the
    tuples cover. Samples that do not reach a region (e.g. Higgs-only data tuples) are left out of it."""
    stitched = main[LABEL_STITCHED]
    for region, (low, high) in REGIONS.items():
        if not covers(stitched, region):
            print(f"[INFO] {era} {category}: DY tuples start at {mass_coverage(stitched)} GeV, "
                  f"skipping the {region} ({low:.0f}-{high:.0f} GeV) plots", flush=True)
            continue
        region_data = data if data is not None and covers(data, region) else None
        if data is not None and region_data is None:
            print(f"[INFO] {era} {category}: data tuples do not reach {low:.0f} GeV, no data in the {region} plots")
        region_main = {label: hset for label, hset in main.items() if covers(hset, region)}
        region_overlays = {label: hset for label, hset in overlays.items() if covers(hset, region)}
        directory = output_directory + region + "/"
        suffix = ", 120-130 GeV removed" if region == "full" else ""

        # Mass in the region, by sample and by parton multiplicity
        mass_name = {"full": "mass_wide", "zpeak": "mass_zpeak", "handoff": "mass_handoff"}[region]
        draw_stack(stack, region_overlays, MASS_VARIABLE, category, era, directory, mass_name,
                   data=region_data, file_prefix="stack")
        draw_stack(stack_np, region_overlays, MASS_VARIABLE, category, era, directory, mass_name,
                   data=region_data, file_prefix="stack_np")
        draw_composition(stack, MASS_VARIABLE, category, era, directory, mass_name)
        if region == "full":
            draw_neff(region_main, MASS_VARIABLE, category, era, directory, "mass_wide")

        for i, variable in enumerate(variables):
            print(f"[{era} {category}] {region} variable {i + 1}/{len(variables)}: {variable}", flush=True)
            name = region + "_" + variable
            variable_directory = get_output_directory(variable, directory + "stack/", variables_type)
            draw_stack(stack, region_overlays, variable, category, era, variable_directory, name,
                       data=region_data, label_suffix=suffix, file_prefix="stack")
            draw_stack(stack_np, region_overlays, variable, category, era, variable_directory, name,
                       data=region_data, label_suffix=suffix, file_prefix="stack_np")
            draw_shape(region_main, variable, category, era, directory + "shapes/", data=region_data, name=name)
            draw_composition(stack, variable, category, era,
                             get_output_directory(variable, directory + "composition/", variables_type), name)


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
    stack = {STACK_LABELS["J_out"]: J_out, STACK_LABELS["J_in"]: J_in,
             STACK_LABELS["U"]: c["U"], STACK_LABELS["F"]: c["F"]}
    # The same stitched prediction split by Born parton multiplicity (all samples): tests the 0J:1J:2J mix
    stack_np = {LABEL_NP.format(p=p): sum_sets(c[f"J{p}_out"], c[f"J{p}_in"], c[f"U{p}"], c[f"F{p}"]) for p in ps}
    overlays = {label: hset for label, hset in main.items() if label != LABEL_STITCHED}

    era_directory = "../plots/DY_stitching_amcnlo/" + era + "/"
    coverage = mass_coverage(main[LABEL_STITCHED])
    print(f"[INFO] {era}: DY tuples start at {coverage} GeV"
          + ("" if data is None else f", data tuples at {mass_coverage(data)} GeV"), flush=True)
    # The parton-multiplicity split must add up to the stitched total (cell 7, unknown multiplicity, is empty)
    stitched_sum = sum(main[LABEL_STITCHED].get("inclusive", "mass_wide")[0])
    np_sum = sum(sum(hset.get("inclusive", "mass_wide")[0]) for hset in stack_np.values())
    if stitched_sum and abs(np_sum / stitched_sum - 1) > 1e-6:
        print(f"[WARNING] {era}: 0J+1J+2J split ({np_sum:.6g}) != stitched total ({stitched_sum:.6g})", flush=True)
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

        # Inclusive 50-180, Z peak and 105 GeV hand-off regions (only those covered by the tuples)
        draw_regions(era, category, output_directory, main, stack, stack_np, overlays, data)

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
    if covers(main[LABEL_STITCHED], "zpeak"):
        write_normalisation_table({name: hset for name, hset in main.items() if covers(hset, "zpeak")}, stack_np,
                                  data if data is not None and covers(data, "zpeak") else None,
                                  categories, era, era_directory + f"zpeak_normalisation_{era}.txt")
    else:
        print(f"[INFO] {era}: no Z peak in the tuples, no Z-peak normalisation table", flush=True)
    print(f"[{era}] Drawing done in {time.time() - start:.0f}s", flush=True)


# Decide which files to read
tasks = []
eras_read = []
for era in eras:
    groups = get_dataset_groups(era)
    # Every aMC@NLO sample is needed (its extensions are optional)
    missing = [group for group, (version, datasets, _) in groups.items() if not get_files(version, datasets[:1])]
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

print(f"{'Input' if args.from_cache else 'Reading'} {len(tasks)} files"
      + ("" if args.from_cache else f" with {args.jobs} job(s)")
      + f"; total {sum(os.path.getsize(t[2]) for t in tasks) / 1024**3:.1f} GB", flush=True)
for era in eras_read:
    for group in list(get_dataset_groups(era)) + ["Data"]:
        n_files = sum(1 for task in tasks if task[0] == era and task[1] == group)
        print(f"  {era} {group}: {n_files} files")

total_start = time.time()
results = {}
failed_files = []


def add_result(era, group, hsets, path, n_done):
    if hsets is None:
        failed_files.append(path)
    else:
        for name, hset in hsets.items():
            if (era, name) in results:
                results[(era, name)] += hset
            else:
                results[(era, name)] = hset
    if n_done % 50 == 0 or n_done == len(tasks):
        print(f"==> Files done: {n_done}/{len(tasks)} "
              f"(elapsed {time.time() - total_start:.0f}s)", flush=True)


def fill_parallel():
    """Fills the histograms with a process pool. A file whose read runs longer than --file-timeout is given up on
    (and listed as failed) so one stalled read cannot block the whole run; its worker is killed at the end."""
    pool = ProcessPoolExecutor(max_workers=args.jobs)
    futures = {pool.submit(fill_task, *task): task for task in tasks}
    pending, started, n_done, n_timed_out = set(futures), {}, 0, 0
    while pending:
        done, pending = wait(pending, timeout=10, return_when=FIRST_COMPLETED)
        for future in done:
            n_done += 1
            add_result(*future.result(), n_done)
            # Drop every reference to the finished future: it holds the file's histograms (~2-4 MB), and keeping
            # thousands of them alive after they are merged runs the node out of memory
            del futures[future]
            started.pop(future, None)
        del done
        now = time.time()
        for future in list(pending):
            if not future.running():
                continue
            started.setdefault(future, now)  # time the read was first seen running
            if now - started[future] > args.file_timeout:
                era, group, path = futures[future][:3]
                print(f"[WARNING] {path} still reading after {args.file_timeout:.0f}s, skipping it", flush=True)
                pending.discard(future)
                del futures[future]
                started.pop(future, None)
                n_timed_out += 1
                n_done += 1
                add_result(era, group, None, path, n_done)
    if n_timed_out:
        # The stalled workers never return: kill them so the pool can shut down
        for process in list(pool._processes.values()):
            process.kill()
    pool.shutdown(wait=n_timed_out == 0, cancel_futures=True)


# --------------------------------------------------------------------------------------------------------- #
# Histogram cache: the merged histograms of a full read are saved, and --from-cache draws from them. The cache
# is only used if everything that decides what is filled (input files, versions, selection, binning and the fill
# code in utils/dy_stitching.py) is unchanged; changes to the drawing code do not invalidate it.
# --------------------------------------------------------------------------------------------------------- #
cache_file = args.cache_file or f"../plots/DY_stitching_amcnlo/cache/histograms_{era_arg}.pkl"
FILL_CODE = [dys.fill_from_file, dys._fill_chunk, dys._resolve_view, dys.cell_view, dys._cleaned, dys.select,
             dys.category_mask, dys.mass_window_mask, dys.region_mask, dys.blind_window_mask, dys.weighted_hist,
             dys.get_binning, dys.get_neff_binning, dys.HistogramSet]


def fill_fingerprint():
    """Hash per component of everything that decides the filled histograms (a mismatch names the component)"""
    all_variables = [MASS_VARIABLE] + variables + neff_jet_variables
    binning = [(v, c, dys.get_binning(v, c), dys.get_neff_binning(v, c)) for v in all_variables for c in categories]
    components = {
        "files": sorted((task[2], task[1], os.path.getsize(task[2])) for task in tasks),
        "versions": (STITCHED_TUPLES_VERSION, DATA_TUPLES_VERSION),
        "selection": (categories, variables, neff_jet_variables, branches, sorted(eras_read),
                      [(era, sorted((group, sorted(views.items())) for group, (_, _, views)
                                    in get_dataset_groups(era).items())) for era in sorted(eras_read)]),
        "binning": (binning, dys.MASS_WIDE_BINS, dys.MASS_ZPEAK_BINS, dys.MASS_HANDOFF_BINS, dys.WEIGHT_BINS.tolist(),
                    dys.REGIONS, dys.CATEGORY_CUTS, dys.MASS_WINDOW, dys.BLIND_WINDOW, dys.DATA_BLINDING_CUT),
        "fill_code": [inspect.getsource(obj) for obj in FILL_CODE] + [repr(sorted(dys.VIEWS))],
    }
    return {name: hashlib.sha256(repr(value).encode()).hexdigest() for name, value in components.items()}


def save_cache():
    os.makedirs(os.path.dirname(os.path.abspath(cache_file)), exist_ok=True)
    payload = {"fingerprint": fill_fingerprint(), "created": time.strftime("%Y-%m-%d %H:%M:%S"),
               "results": results, "eras_read": eras_read, "failed_files": failed_files}
    with open(cache_file + ".tmp", "wb") as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
    os.replace(cache_file + ".tmp", cache_file)  # never leaves a half-written cache behind
    print(f"[INFO] Histograms saved to {cache_file} ({os.path.getsize(cache_file) / 1024**2:.1f} MB); "
          "use --from-cache to redraw without reading the tuples", flush=True)


def load_cache():
    if not os.path.exists(cache_file):
        print(f"[ERROR] No histogram cache {cache_file}: run once without --from-cache")
        exit(1)
    with open(cache_file, "rb") as f:
        payload = pickle.load(f)
    expected = fill_fingerprint()
    changed = [name for name in expected if payload["fingerprint"].get(name) != expected[name]]
    if changed:
        print(f"[ERROR] The histogram cache {cache_file} ({payload['created']}) is out of date: "
              f"{', '.join(changed)} changed since it was made. Rerun without --from-cache.")
        exit(1)
    print(f"[INFO] Drawing from the histogram cache {cache_file} ({payload['created']})", flush=True)
    return payload


if args.from_cache:
    cached = load_cache()
    results, eras_read, failed_files = cached["results"], cached["eras_read"], cached["failed_files"]
else:
    if args.jobs > 1:
        fill_parallel()
    else:
        for n_done, task in enumerate(tasks, start=1):
            add_result(*fill_task(*task), n_done)
if failed_files:
    failed_list = f"dy_stitching_failed_files_{era_arg}.txt"
    with open(failed_list, "w") as f:
        f.write("\n".join(failed_files) + "\n")
    print(f"[WARNING] {len(failed_files)} file(s) could not be read and were skipped (listed in {failed_list}); "
          "the yields of their samples are low by that fraction", flush=True)
if not args.from_cache:
    save_cache()

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
