import matplotlib

# Never open an X11/GUI backend (slow over ssh -X); plots are only saved to disk
matplotlib.use("Agg")

from utils.dy_stitching import (
    MASS_VARIABLE,
    HistogramSet,
    selection_view,
    fill_from_file,
    print_summary,
    draw_neff,
    draw_yield,
    draw_weight_distribution,
    draw_shape,
    write_closure_table,
)
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from utils.helper import get_output_directory
from utils.labels import variables_type
import utils.dy_stitching as dys
import utils.ewk_comparison as ewk
import argparse
import glob
import hashlib
import inspect
import os
import pickle
import sys
import time

sys.path.append("../condor/utils")
import version as v

# Reco-level comparison of the EWK Z+2j samples (utils/ewk_comparison.py), modelled on plot_DY_stitching.py:
#   - statistics: N_eff = (sum w)^2 / sum w^2 and the effective luminosity L_eff = L N_eff / sum w per category
#     (inclusive / ggH / VBF), in the tuple mass range and in the 110-150 GeV window (statistics_<era>.txt, N_eff plots
#     vs mass, diJet_mass and delta_eta_diJet), weight distributions
#   - yields and unit-normalised shapes of the BDT inputs in 110-150 GeV, ratio to H7 2Mu2J
#   - closure tables (chi2/ndf per variable): H7 2L2J restricted to LHE mumu 105-160 vs H7 2Mu2J (same generator and
#     phase space: should close; it tests the cross sections and is the input for a later stitching), and P8 2Mu2J vs
#     H7 2Mu2J (shower / hadronisation; P8 also has M2J > 120 at generator level, which the tuples cannot emulate,
#     so outside the VBF category it differs by that acceptance too)
# The extensions of a sample are normalised together (utils/ewk_comparison.py). MC only: no data is read.
#  Usage: python3 plot_EWK_comparison.py [era] [-j N_JOBS] [--tuples-version X.Y.Z] [--max-files N] [--from-cache]
parser = argparse.ArgumentParser()
parser.add_argument("era", nargs="?", default="2024", choices=ewk.ERAS)
parser.add_argument("-j", "--jobs", type=int, default=1,
                    help="number of files read in parallel (each job uses ~1 GB; default 1)")
parser.add_argument("--tuples-version", default=v.TUPLES_VERSION_NUMBER.lstrip("v"),
                    help="tuples version of the EWK samples (default: condor/utils/version.py)")
parser.add_argument("--no-xrootd", action="store_true",
                    help="read /eos/uscms files through the FUSE mount instead of xrootd (root://cmseos.fnal.gov/)")
parser.add_argument("--max-files", type=int, default=None,
                    help="read at most this many files per dataset (quick test; yields are then too low)")
parser.add_argument("--from-cache", action="store_true",
                    help="draw from the histograms saved by the last full read instead of reading the tuples again")
parser.add_argument("--cache-file", default=None,
                    help="histogram cache (default: ../plots/EWK_comparison/cache/histograms_<era>.pkl)")
parser.add_argument("--file-timeout", type=float, default=600,
                    help="with -j > 1: skip a file whose read takes longer than this many seconds (default 600)")
args = parser.parse_args()
era = args.era
TUPLES_VERSION = args.tuples_version.lstrip("v")
ANALYZER_VERSION = ".".join(TUPLES_VERSION.split(".")[:2])

# Legend / output names (plain text: they are also columns of the printed tables)
LABEL_REFERENCE = "H7 2Mu2J"
LABEL_WINDOW = "H7 2L2J (LHE 105-160)"
LABEL_2L2J_ALL = "H7 2L2J (all)"
LABEL_PYTHIA = "P8 2Mu2J"
# Order of the comparison plots; the first available one is the reference of the ratio panels
MAIN_ORDER = [LABEL_REFERENCE, LABEL_WINDOW, LABEL_PYTHIA, LABEL_2L2J_ALL]

categories = [
    "inclusive",
    "ggH",
    "VBF",
]

# BDT input variables (same list as plot_DY_stitching.py / plot_sig_vs_bg.py)
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


def tuples_directory():
    # EWK_COMPARISON_TUPLES_BASE overrides the EOS base directory (e.g. for tests on a local copy)
    base = os.getenv("EWK_COMPARISON_TUPLES_BASE", f"/eos/uscms/store/group/lpchmumu/{os.getenv('USER')}")
    return f"{base}/analyzer_HiggsMuMu_v{ANALYZER_VERSION}/tuples_v{TUPLES_VERSION}/"


EOS_FUSE_PREFIX = "/eos/uscms/"
XROOTD_REDIRECTOR = "root://cmseos.fnal.gov//"


def read_path(path):
    """xrootd URL for files under the /eos/uscms FUSE mount (FUSE reads can stall indefinitely; xrootd reads time
    out with an error instead). Other paths (e.g. a local EWK_COMPARISON_TUPLES_BASE) are read as they are."""
    if args.no_xrootd or not path.startswith(EOS_FUSE_PREFIX):
        return path
    return XROOTD_REDIRECTOR + path[len(EOS_FUSE_PREFIX):]


def fill_task(group, path, views):
    try:
        hsets = fill_from_file(read_path(path), f"{era} {group}", branches, categories, variables,
                               neff_jet_variables, is_data=False, verbose=False, views=views)
    except Exception as error:
        print(f"[WARNING] Could not read {path}: {error}", flush=True)
        hsets = None
    return group, hsets, path


# --------------------------------------------------------------------------------------------------------- #
# Inputs: per sample, the datasets with a SumGenWeight.root (for the extension fractions) and their tuples
# --------------------------------------------------------------------------------------------------------- #
sumgen_directory = ewk.analyzer_directory(ANALYZER_VERSION)
tasks = []
fractions = {}
for label, base in ewk.SAMPLES.items():
    sums = ewk.read_sample_sums(sumgen_directory, base, era)
    if sums is None:
        print(f"[WARNING] {label}: no SumGenWeight.root for {ewk.dataset_names(base, era)} in {sumgen_directory}, "
              "left out")
        continue
    sample_fractions = ewk.extension_fractions(sums, TUPLES_VERSION)
    files = {dataset: sorted(glob.glob(tuples_directory() + dataset + "/*_tuples.root"))
             for dataset in sums["datasets"]}
    if not any(files.values()):
        print(f"[WARNING] {label}: no tuples for {sums['datasets']} in {tuples_directory()}, left out")
        continue
    without_tuples = [dataset for dataset, paths in files.items() if not paths]
    if without_tuples:
        # The extension fractions assume every dataset of the sample is read
        print(f"[ERROR] {label}: {without_tuples} have a SumGenWeight.root but no tuples in {tuples_directory()}; "
              "run CreateTuple for them first (otherwise the sample's yield is too low)")
        exit(1)
    for dataset in sums["datasets"]:
        fraction = sample_fractions[dataset]
        fractions[dataset] = fraction
        views = {label: selection_view(fraction)} if label != "H7 2L2J" else {
            LABEL_2L2J_ALL: selection_view(fraction),
            LABEL_WINDOW: selection_view(fraction, ewk.LHE_WINDOW),
        }
        dataset_files = files[dataset][:args.max_files] if args.max_files else files[dataset]
        tasks += [(label, path, views) for path in dataset_files]
    print(f"  {label}: " + ", ".join(f"{dataset} ({len(files[dataset])} files, fraction {sample_fractions[dataset]:.4f})"
                                     for dataset in sums["datasets"]))
if not tasks:
    print(f"[ERROR] No EWK tuples found for era {era} in {tuples_directory()}")
    exit(1)
if args.max_files:
    print(f"[WARNING] --max-files {args.max_files}: only part of each dataset is read, so the yields (not the shapes "
          "or N_eff per file) are too low")

print(f"{'Input' if args.from_cache else 'Reading'} {len(tasks)} files"
      + ("" if args.from_cache else f" with {args.jobs} job(s)"), flush=True)

total_start = time.time()
results = {}
failed_files = []


def add_result(group, hsets, path, n_done):
    if hsets is None:
        failed_files.append(path)
    else:
        for name, hset in hsets.items():
            if name in results:
                results[name] += hset
            else:
                results[name] = hset
    if n_done % 50 == 0 or n_done == len(tasks):
        print(f"==> Files done: {n_done}/{len(tasks)} (elapsed {time.time() - total_start:.0f}s)", flush=True)


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
            del futures[future]  # the finished future holds the file's histograms
            started.pop(future, None)
        del done
        now = time.time()
        for future in list(pending):
            if not future.running():
                continue
            started.setdefault(future, now)
            if now - started[future] > args.file_timeout:
                group, path = futures[future][:2]
                print(f"[WARNING] {path} still reading after {args.file_timeout:.0f}s, skipping it", flush=True)
                pending.discard(future)
                del futures[future]
                started.pop(future, None)
                n_timed_out += 1
                n_done += 1
                add_result(group, None, path, n_done)
    if n_timed_out:
        for process in list(pool._processes.values()):
            process.kill()
    pool.shutdown(wait=n_timed_out == 0, cancel_futures=True)


# --------------------------------------------------------------------------------------------------------- #
# Histogram cache (as in plot_DY_stitching.py): only used if everything that decides what is filled is unchanged
# --------------------------------------------------------------------------------------------------------- #
cache_file = args.cache_file or f"../plots/EWK_comparison/cache/histograms_{era}.pkl"
FILL_CODE = [dys.fill_from_file, dys._fill_chunk, dys._resolve_view, dys.selection_view, dys._cleaned, dys.select,
             dys.category_mask, dys.mass_window_mask, dys.region_mask, dys.blind_window_mask, dys.weighted_hist,
             dys.get_binning, dys.get_neff_binning, dys.HistogramSet]


def fill_fingerprint():
    """Hash per component of everything that decides the filled histograms (a mismatch names the component)"""
    all_variables = [MASS_VARIABLE] + variables + neff_jet_variables
    binning = [(var, c, dys.get_binning(var, c), dys.get_neff_binning(var, c)) for var in all_variables
               for c in categories]
    components = {
        "files": sorted((task[1], task[0], os.path.getsize(task[1])) for task in tasks),
        "versions": TUPLES_VERSION,
        "normalisation": sorted(fractions.items()),
        "selection": (categories, variables, neff_jet_variables, branches, era,
                      sorted((task[1], sorted(task[2].items())) for task in tasks)),
        "binning": (binning, dys.MASS_WIDE_BINS, dys.WEIGHT_BINS.tolist(), dys.REGIONS, dys.CATEGORY_CUTS,
                    dys.MASS_WINDOW),
        "fill_code": [inspect.getsource(obj) for obj in FILL_CODE],
    }
    return {name: hashlib.sha256(repr(value).encode()).hexdigest() for name, value in components.items()}


def save_cache():
    os.makedirs(os.path.dirname(os.path.abspath(cache_file)), exist_ok=True)
    payload = {"fingerprint": fill_fingerprint(), "created": time.strftime("%Y-%m-%d %H:%M:%S"),
               "results": results, "failed_files": failed_files}
    with open(cache_file + ".tmp", "wb") as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
    os.replace(cache_file + ".tmp", cache_file)  # never leaves a half-written cache behind
    print(f"[INFO] Histograms saved to {cache_file}; use --from-cache to redraw without reading the tuples",
          flush=True)


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
    results, failed_files = cached["results"], cached["failed_files"]
else:
    if args.jobs > 1:
        fill_parallel()
    else:
        for n_done, task in enumerate(tasks, start=1):
            add_result(*fill_task(*task), n_done)
if failed_files:
    failed_list = f"ewk_comparison_failed_files_{era}.txt"
    with open(failed_list, "w") as f:
        f.write("\n".join(failed_files) + "\n")
    print(f"[WARNING] {len(failed_files)} file(s) could not be read and were skipped (listed in {failed_list}); "
          "the yields of their samples are low by that fraction", flush=True)
if not args.from_cache:
    save_cache()


# --------------------------------------------------------------------------------------------------------- #
# Drawing
# --------------------------------------------------------------------------------------------------------- #
def write_statistics_table(samples, path):
    """N raw, sum w, N_eff, effective luminosity L_eff = L N_eff / sum w (the weights are normalised to L, the
    luminosity CreateTuple uses) and negative-weight fraction per category, in the tuple mass range and 110-150 GeV"""
    luminosity = ewk.read_luminosities()[era]
    lines = [f"EWK Z+2j MC statistics, era {era} (tuples v{TUPLES_VERSION}, L = {luminosity} fb^-1 from "
             "lib/Run3Constants.h; L_eff = L N_eff / sum w)"]
    for category in categories:
        lines.append(f"\n[{category}]")
        lines.append(f"  {'sample':<24}{'selection':<12}{'N raw':>10}{'sum w':>12}{'N_eff':>12}{'L_eff [fb-1]':>14}"
                     f"{'L_eff / L':>11}{'neg frac':>10}")
        for selection in ["all mass", "110-150"]:
            for label, hset in samples.items():
                if (category, selection) not in hset.summary:
                    continue
                n_raw, sumw, sumw2, n_neg, _ = hset.summary[(category, selection)]
                neff = sumw**2 / sumw2 if sumw2 > 0 else 0.0
                leff = luminosity * neff / sumw if sumw > 0 else float("nan")
                lines.append(f"  {label:<24}{selection:<12}{int(n_raw):>10d}{sumw:>12.3f}{neff:>12.1f}{leff:>14.1f}"
                             f"{leff / luminosity:>11.2f}{(n_neg / n_raw if n_raw else 0.0):>10.3f}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as output:
        output.write("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)
    print(f"Statistics table written to {path}", flush=True)


def draw_pair(first_label, second_label, output_directory, category):
    """Yields and shapes of two samples (closure / generator comparison)"""
    samples = {first_label: results[first_label], second_label: results[second_label]}
    draw_yield(samples, MASS_VARIABLE, category, era, output_directory)
    for variable in variables:
        draw_shape(samples, variable, category, era, output_directory + "shapes/")
        draw_yield(samples, variable, category, era,
                   get_output_directory(variable, output_directory + "yields/", variables_type),
                   name="shape_" + variable)


main = {label: results[label] for label in MAIN_ORDER if label in results}
era_directory = f"../plots/EWK_comparison/{era}/"
print(f"\n[INFO] Samples: {', '.join(main)}; ratio panels are relative to {next(iter(main))}", flush=True)
write_statistics_table(main, era_directory + f"statistics_{era}.txt")

pairs = []
if LABEL_REFERENCE in results and LABEL_WINDOW in results:
    pairs.append((LABEL_REFERENCE, LABEL_WINDOW, "closure_H7_2L2J_vs_2Mu2J"))
if LABEL_REFERENCE in results and LABEL_PYTHIA in results:
    pairs.append((LABEL_REFERENCE, LABEL_PYTHIA, "pythia_vs_herwig"))
for first, second, name in pairs:
    write_closure_table(first, results[first], second, results[second], categories, variables,
                        era_directory + f"{name}_chi2_{era}.txt")

for category in categories:
    output_directory = era_directory + category + "/"
    print_summary(main, category, era)

    # Statistics
    draw_neff(main, MASS_VARIABLE, category, era, output_directory, "mass")
    for variable in neff_jet_variables:
        draw_neff(main, variable, category, era, output_directory, "neff_" + variable)
    draw_weight_distribution(main, category, era, output_directory)
    draw_yield(main, MASS_VARIABLE, category, era, output_directory)

    # Yields and shapes of every BDT input in 110-150 GeV
    for i, variable in enumerate(variables):
        print(f"[{era} {category}] variable {i + 1}/{len(variables)}: {variable}", flush=True)
        draw_shape(main, variable, category, era, output_directory + "shapes/")
        draw_yield(main, variable, category, era,
                   get_output_directory(variable, output_directory + "yields/", variables_type),
                   name="shape_" + variable)

    # Pairwise comparisons
    for first, second, name in pairs:
        print(f"[{era} {category}] {name}", flush=True)
        draw_pair(first, second, output_directory + name + "/", category)

print(f"\nAll done in {time.time() - total_start:.0f}s; plots in {era_directory}", flush=True)
