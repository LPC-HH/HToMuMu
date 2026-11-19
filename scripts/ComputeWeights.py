import os
import re
import sys
import uproot
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from eos_io import recreate_on_eos, open_eos, exists_eos  # never write ROOT files through the EOS FUSE mount

sys.path.append('../condor/utils')
import version as v

sys.path.append('../list')
from listDatasets_Run3 import datasets_info

# Usage: python3 ComputeWeights.py [T/F] [n_threads]
#   T/F      : recreate SumGenWeight.root files that already exist
#   n_threads : number of files read in parallel (default 16)
#
# Speed: the run time is dominated by EOS latency (~0.1-0.2 s to open a cold file vs ~10 ms of
# actual reading), so the analyzer outputs of all datasets are read in parallel by a thread pool.
# The per-dataset sums are still accumulated file by file in the os.listdir order, exactly as in
# the serial version, so the SumGenWeight.root contents are bitwise identical.

DEFAULT_N_THREADS = 16

#EOS_PATH = f"/eos/uscms/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_{v.ANALYZER_VERSION_NUMBER}/"

user = os.getenv('LOGNAME')
EOS_PATH = "/eos/uscms/store/group/lpchmumu/" + user + "/analyzer_HiggsMuMu_" + v.ANALYZER_VERSION_NUMBER

# Skip these datasets
skip_dataset = [
    "DoubleMuon_2022A",
    "DoubleMuon_2022B",
    "DoubleMuon_2022C",
    "Muon0_2023B",
    "Muon1_2023B",
    #"TTtoLNu2Q_Summer24",
    #"WZto2L2Q_Summer24",
]
skip_pattern = [
    # "Summer22",
    # "Summer22EE",
    # "_2022",
    "DYJetstoLL",
    "DYto2L-2Jets_Summer",  # old inclusive FxFx entries (the 0J/1J/2J ones are used)
    "TWminusto4Q",
    "TWminustoLNu2Q",
    "Tbar",
    "TQbar",
    "t-channel",
    "s-channel",
    "ZZto2Nu2Q",
    "WWto4Q",
    "v13",
    "DY50to120",
    "DY120to200",
]

list_datasets = datasets_info.keys()
# # Use in case you want to run over a specific list of datasets!
#list_datasets = [
#    "DYto2Mu-2Jets_105to160_Summer23BPix",
#     "DY50to120_Summer24",
#     "DY120to200_Summer24",
     #"WWtoLNu2Q_Summer23BPix",
#]

# Pre-selection gen-mll and stitching-cell sums and generator filter counts, for the DY stitching
stitch_hist_names = ["h_sumOfgenWeight_genMll", "h_sumOfgenWeight_genMll_VBFFilter",
                     "h_sumOfgenWeight_stitchCells", "h_sumOfgenWeight2_stitchCells"]


def read_one(file_path):
    """Read everything ComputeWeights needs from one analyzer output file."""
    try:
        with uproot.open(file_path) as input_file:
            h_gen = input_file["h_sumOfgenWeight"]
            h_pdf = input_file["h_sumOfLHEPdfWeight"]
            h_scale = input_file["h_sumOfLHEScaleWeight"]
            result = {
                "gen": h_gen.values()[0],
                "pdf": (h_pdf.values(), h_pdf.axis().edges()),
                "scale": (h_scale.values(), h_scale.axis().edges()),
                "stitch": {},
                "genFilter": None,
            }

            for name in stitch_hist_names:
                if name not in input_file:
                    continue
                h = input_file[name]
                result["stitch"][name] = (h.values(), h.axis().edges())

            if "LuminosityBlocks" in input_file:
                lumi_tree = input_file["LuminosityBlocks"]
                if "GenFilter_numEventsTotal" in lumi_tree:
                    result["genFilter"] = (
                        int(lumi_tree["GenFilter_numEventsPassed"].array(library="np").sum()),
                        int(lumi_tree["GenFilter_numEventsTotal"].array(library="np").sum()),
                    )
        return result
    except Exception as e:
        raise RuntimeError(f"Failed reading {file_path}: {e}") from e


def find_dataset(dataset_name, recreate_weight_file):
    """Directory lookup for one dataset. Returns (lines to print, FILESDIR, files) with
    FILESDIR = None when the dataset is skipped."""
    lines = ["\n----- %s -----" % (dataset_name)]

    FILESDIR = ""
    for dir_type in ["Data", "MC_background", "MC_signal"]:
        if os.path.exists(EOS_PATH + "/%s/%s" % (dir_type, dataset_name)):
            lines.append("Directory found!")
            FILESDIR = EOS_PATH + "/%s/%s" % (dir_type, dataset_name)
            lines.append(FILESDIR)
            break
    if not FILESDIR:
        lines.append("No folder found for " + dataset_name + " :(. Skipping.")
        return lines, None, []

    analyzer_output_files = [file for file in os.listdir(FILESDIR) if "Higgs" in file]

    SumGenWeight_exists = exists_eos(FILESDIR + "/SumGenWeight.root")
    if SumGenWeight_exists and not recreate_weight_file:
        lines.append("SumGenWeight already exists!")
        return lines, None, []

    return lines, FILESDIR, analyzer_output_files


def sum_dataset(results):
    """Accumulate per-file results in the given (os.listdir) order, with the same numpy
    operations as the original serial loop, so the sums are bitwise identical."""
    totalGenWeight = 0.0

    totalLHEPdfWeight = None
    totalLHEScaleWeight = None

    pdf_edges = None
    scale_edges = None

    stitch_totals = {}
    stitch_edges = {}
    genFilter_passed = 0
    genFilter_total = 0

    for r in results:
        totalGenWeight += r["gen"]

        pdf_values, edges = r["pdf"]
        if totalLHEPdfWeight is None:
            totalLHEPdfWeight = np.zeros_like(pdf_values, dtype=np.float64)
            pdf_edges = edges
        totalLHEPdfWeight += pdf_values

        scale_values, edges = r["scale"]
        if totalLHEScaleWeight is None:
            totalLHEScaleWeight = np.zeros_like(scale_values, dtype=np.float64)
            scale_edges = edges
        totalLHEScaleWeight += scale_values

        for name in stitch_hist_names:
            if name not in r["stitch"]:
                continue
            values, edges = r["stitch"][name]
            if name not in stitch_totals:
                stitch_totals[name] = np.zeros_like(values, dtype=np.float64)
                stitch_edges[name] = edges
            stitch_totals[name] += values

        if r["genFilter"] is not None:
            genFilter_passed += r["genFilter"][0]
            genFilter_total += r["genFilter"][1]

    return {
        "totalGenWeight": totalGenWeight,
        "totalLHEPdfWeight": totalLHEPdfWeight, "pdf_edges": pdf_edges,
        "totalLHEScaleWeight": totalLHEScaleWeight, "scale_edges": scale_edges,
        "stitch_totals": stitch_totals, "stitch_edges": stitch_edges,
        "genFilter_passed": genFilter_passed, "genFilter_total": genFilter_total,
    }


def write_dataset(dataset_name, outputFile, t):
    """Print the summary and write SumGenWeight.root (same content and printout as before)."""
    print(
        f"Total generator weight for {dataset_name}: {t['totalGenWeight']}"
    )

    print(
        f"Number of PDF weights: {len(t['totalLHEPdfWeight'])}"
    )

    print(
        f"Number of scale weights: {len(t['totalLHEScaleWeight'])}"
    )

    # Written only after all files were read: a crash while reading no longer leaves an empty
    # SumGenWeight.root behind (which a later run without T would skip as "already exists").
    with recreate_on_eos(outputFile) as f:

        f["h_sumOfgenWeight"] = np.histogram(
            np.array([0.5]),
            bins=[0, 1],
            weights=[t["totalGenWeight"]]
        )

        f["h_sumOfLHEPdfWeight"] = (
            t["totalLHEPdfWeight"],
            t["pdf_edges"]
        )

        f["h_sumOfLHEScaleWeight"] = (
            t["totalLHEScaleWeight"],
            t["scale_edges"]
        )

        for name, values in t["stitch_totals"].items():
            f[name] = (values, t["stitch_edges"][name])

        genFilter_passed, genFilter_total = t["genFilter_passed"], t["genFilter_total"]
        if genFilter_total > 0:
            print(
                f"GenFilter passed/total for {dataset_name}: {genFilter_passed}/{genFilter_total}"
                f" = {genFilter_passed / genFilter_total:.5f}"
            )
            f["h_genFilter_counts"] = (
                np.array([genFilter_passed, genFilter_total], dtype=np.float64),
                np.array([0.0, 1.0, 2.0])
            )

    print(outputFile + " CREATED")


def write_sample_sums(dataset_names, dir_suffix=""):
    """A dataset and its extensions (<dataset>_ext1, _ext2, ...) are hadded into one sample, so they share one
    normalisation, as for the DY (compute_DY_stitching.py, stitch_sumw): writes the sum of h_sumOfgenWeight over all
    of them as the one-bin h_sumOfgenWeight_sample into each one's SumGenWeight.root, which CreateTuple normalises
    with (equal to h_sumOfgenWeight for a dataset without extensions). dataset_names: the non-skipped datasets.
    Re-tuplise every dataset of a sample whenever its sum changes (e.g. an extension is added)."""
    samples = {}
    for name in dataset_names:
        if datasets_info[name][0] != "T":  # MC only
            samples.setdefault(re.sub(r"_ext\d+$", "", name), []).append(name)

    print("\n===== Sum of gen weights over the extensions (h_sumOfgenWeight_sample) =====")
    for sample, members in samples.items():
        paths = {}
        for name in members:
            for dir_type in ["MC_background", "MC_signal"]:
                path = EOS_PATH + "/%s/%s%s/SumGenWeight.root" % (dir_type, name, dir_suffix)
                if exists_eos(path):
                    paths[name] = path
                    break
        if not paths:
            continue
        sums = {}
        for name, path in paths.items():
            with open_eos(path) as f:
                sums[name] = float(f["h_sumOfgenWeight"].values()[0])
        total = sum(sums.values())
        n_written = 0
        for path in paths.values():
            # No uproot.update on EOS: read everything (over xrootd) and write it back via a local file
            with open_eos(path) as f:
                if "h_sumOfgenWeight_sample" in f and f["h_sumOfgenWeight_sample"].values()[0] == total:
                    continue
                existing = {key.split(";")[0]: f[key] for key in f.keys(cycle=False)
                            if key.split(";")[0] != "h_sumOfgenWeight_sample"}
            with recreate_on_eos(path) as f:
                for key, hist in existing.items():
                    f[key] = hist
                f["h_sumOfgenWeight_sample"] = (np.array([total]), np.array([0.0, 1.0]))
            n_written += 1
        if len(paths) > 1 or n_written:
            parts = ", ".join("%s%s: %.6g" % (name, dir_suffix, value) for name, value in sums.items())
            print("%s%s: %.6g = %s [written to %d file(s)]" % (sample, dir_suffix, total, parts, n_written))
        missing = [name + dir_suffix for name in members if name not in paths]
        if len(paths) > 1 and missing:
            print("  [WARNING] no SumGenWeight.root for " + ", ".join(missing) + ": not included")


def write_signal_lhe_sample_sums(dataset_names):
    """Write shared PDF and scale sums for nominal signal samples and their extensions."""
    samples = {}
    for name in dataset_names:
        if datasets_info[name][3] == "MC_signal":
            path = f"{EOS_PATH}/MC_signal/{name}/SumGenWeight.root"
            if exists_eos(path):
                sample = re.sub(r"_ext\d+$", "", name)
                samples.setdefault(sample, []).append(path)

    lhe_names = ("h_sumOfLHEPdfWeight", "h_sumOfLHEScaleWeight")
    for paths in samples.values():
        totals = {}
        for path in paths:
            with open_eos(path) as f:
                for name in lhe_names:
                    hist = f[name]
                    values = hist.values().astype(np.float64)
                    edges = hist.axis().edges()
                    key = f"{name}_sample"
                    if key in totals:
                        total_values, total_edges = totals[key]
                        if not np.array_equal(edges, total_edges):
                            raise ValueError(f"Inconsistent binning for {name} in {path}")
                        total_values += values
                    else:
                        totals[key] = (values, edges)

        for path in paths:
            with open_eos(path) as f:
                if all(key in f and np.array_equal(f[key].values(), values)
                       and np.array_equal(f[key].axis().edges(), edges)
                       for key, (values, edges) in totals.items()):
                    continue
                existing = {key: f[key] for key in f.keys(cycle=False) if key not in totals}
            with recreate_on_eos(path) as f:
                for key, hist in existing.items():
                    f[key] = hist
                for key, hist in totals.items():
                    f[key] = hist


def main():
    # Arguments
    if (len(sys.argv) == 1):
        recreate_weight_file = False
    elif (len(sys.argv) == 2) and (sys.argv[1] not in ["T", "F"]):
        print("First argument is required! Add T or F if you want to recreate the SumGenWeight file")
        exit()
    else:
        recreate_weight_file = True if (sys.argv[1] == "T") else False

    n_threads = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_N_THREADS

    # 1) Directory lookups (fast), keeping the original dataset order and printout.
    datasets = []
    for dataset_name in list_datasets:
        match_pattern = [True for pattern in skip_pattern if pattern in dataset_name]
        if (dataset_name in skip_dataset) or (True in match_pattern):
            continue
        datasets.append((dataset_name, *find_dataset(dataset_name, recreate_weight_file)))

    # 2) Queue every file of every dataset on one pool, so the reads overlap across datasets.
    with ThreadPoolExecutor(max_workers=n_threads) as pool:
        futures = {}
        for dataset_name, _, FILESDIR, files in datasets:
            if FILESDIR:
                futures[dataset_name] = [pool.submit(read_one, FILESDIR + "/" + fname) for fname in files]

        # 3) Finish datasets in the original order while later ones keep loading.
        try:
            for dataset_name, lines, FILESDIR, files in datasets:
                for line in lines:
                    print(line)
                if not FILESDIR:
                    continue
                results = [fut.result() for fut in futures[dataset_name]]
                write_dataset(dataset_name, FILESDIR + "/SumGenWeight.root", sum_dataset(results))
                sys.stdout.flush()
        except BaseException:
            for futs in futures.values():
                for fut in futs:
                    fut.cancel()
            raise

    # 4) Normalisation shared by a dataset and its extensions, also when nothing was recreated above
    dataset_names = [name for name, *_ in datasets]
    write_sample_sums(dataset_names)
    write_signal_lhe_sample_sums(dataset_names)


if __name__ == "__main__":
    main()
