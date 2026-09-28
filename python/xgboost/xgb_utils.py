import sys
import matplotlib
import mplhep as hep
import os
import subprocess
import shutil
import tempfile
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import pickle as pickle
import time
import ROOT as root
import uproot
import xgboost as xgb

root.gROOT.Reset()

# get_variables() branch names that lib/CreateTuple.h can only fill from a real
# jet system; for events with too few jets it leaves them at a 0 (or -1, for
# delta_phi_diJet/pt_balance/pt_centrality) padding value that overlaps the
# physical range. Mask them to NaN so XGBoost treats them as missing rather than
# a physical measurement. Same convention as train_VBF_ggH_BDT.py.
DIJET_VARIABLES = frozenset({
    "subleading_jet_pt", "subleading_jet_eta", "diJet_mass", "delta_eta_diJet", "delta_phi_diJet",
    "z_zeppenfeld", "pt_balance", "pt_centrality", "subleading_jet_btagPNetQvG",
    "subleading_jet_nConstituents",
})
SINGLE_JET_VARIABLES = frozenset({
    "leading_jet_pt", "leading_jet_eta",
    "min_delta_eta_diMuon_jet", "min_delta_phi_diMuon_jet", "leading_jet_btagPNetQvG",
    "leading_jet_nConstituents",
})
# The PNet quark-vs-gluon branches carry TWO sentinels: -1 when the jet does not exist (the
# n_jet masking above covers that) and -10 when the tagger did not produce a score for a jet
# that does exist (~0.1% of jets, which n_jet cannot catch). Neither is a physical score.
TAGGER_FAILURE_VALUE = -10.0
TAGGER_VARIABLES = frozenset({"leading_jet_btagPNetQvG", "subleading_jet_btagPNetQvG"})

# rows of a scored tuple held in memory at once while `--stage apply` scores it. The ggH
# skims are up to 28M rows x 18 features; reading all of them at once peaked around 8 GB,
# which is what made long apply runs die. 2M rows is ~150 MB per copy.
SCORE_CHUNK_ROWS = 2_000_000

# Where the systematic tuples live. Hardcoded into another user's EOS area by the campaign that
# produced them -- one of the per-checkout paths CLAUDE.md flags; append_BDT_score_to_sys takes
# it as an argument so it can be overridden without editing this file.
SYSTEMATICS_TUPLE_DIR = ("/eos/uscms/store/user/lpchmumu/mbarrial/"
                         "analyzer_HiggsMuMu_v2.0/tuples_v2.0.0/systematics/")

# Parallel CopyTree ranges used to build a scored-tuple skim. TTree::CopyTree is a
# single-threaded decompress/recompress of every branch of every entry (~47 us/entry over the
# 108 branches of these tuples), so splitting it over contiguous entry ranges and merging with
# hadd is most of the win: measured 38.0 s -> 8.7 s including the merge on the 1.6M-row ggH TT
# skim. 1 restores the old single-process path. Each range costs its own ROOT process (a few
# hundred MB), which is what the cap is for.
SKIM_CHUNKS = max(1, min(6, (os.cpu_count() or 2) - 2))
# below this many entries the process startup plus the hadd cost more than they save
SKIM_CHUNK_MIN_ENTRIES = 200_000

# Run as `python3 -c` in its own process rather than a forked worker: the parent has ROOT,
# XGBoost (OpenMP) and matplotlib loaded by this point, and none of that should be inherited.
_SKIM_CHUNK_PROGRAM = """
import sys
import ROOT
ROOT.gROOT.SetBatch(True)
src, out, cuts, first, n = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
source = ROOT.TFile.Open(src)
if not source or source.IsZombie():
    sys.exit("could not open " + src)
skim = ROOT.TFile.Open(out, "RECREATE")
selected = source.Get("tree_output").CopyTree(cuts, "", n, first)
rows = selected.GetEntries()
selected.Write("tree_output")
skim.Close()
source.Close()
print(rows)
"""


def mask_undefined_jet_features(df):
    """In-place: NaN out jet variables that are lib/CreateTuple.h padding rather
    than a real measurement (dijet vars when n_jet < 2, leading-jet vars when
    n_jet < 1) so XGBoost's native missing-value handling routes those events
    consistently instead of treating the 0/-1 padding as physical. No-op if
    n_jet is not among the columns. Tagger-failure sentinels are masked regardless."""
    if "n_jet" not in df.columns:
        return df
    dijet = [c for c in df.columns if c in DIJET_VARIABLES]
    single = [c for c in df.columns if c in SINGLE_JET_VARIABLES]
    if dijet:
        df.loc[df["n_jet"] < 2, dijet] = np.nan
    if single:
        df.loc[df["n_jet"] < 1, single] = np.nan
    for column in (c for c in df.columns if c in TAGGER_VARIABLES):
        df.loc[df[column] <= TAGGER_FAILURE_VALUE + 0.1, column] = np.nan
    return df


matplotlib.use("Agg")
plt.style.use(hep.style.CMS)
use_skim = False
root.gROOT.SetBatch(True)
root.gStyle.SetOptStat(0)
root.gStyle.SetOptFit(111)
root.gStyle.SetPaintTextFormat("2.1f")

luminosity = {
    "2022": 7.9804,
    "2022EE": 26.6717,
    "2022Combined": 34.6521,
    "2023": 17.794,
    "2023BPix": 9.451,
    "2023Combined": 27.245,
    "2024": 	109.08,
    # "Combined": 61.897,
    "Combined": 170.905,
}


def copy_and_skim_tree(tuple_path, tuple_name, BDT_path, BDT_name, channel_US, use_bsConstrain,
                       category_var, n_chunks=None):
    """Skim a nominal tuple down to the 100-180 GeV window of one category.

    With n_chunks > 1 (the default, see SKIM_CHUNKS) the copy is split over contiguous entry
    ranges run in parallel and merged with hadd. hadd concatenates trees in the order the files
    are given, so the merged tree holds exactly the rows a single CopyTree would produce, in the
    same order. Nothing depends on that any more -- the fold of a row comes from its own
    `event`, not from where it sits -- but keeping the order makes two runs diffable.
    """
    source_path = tuple_path + tuple_name
    skim_path = BDT_path + BDT_name
    mass_var = "diMuon_bsConstrainedMass" if use_bsConstrain else "diMuon_mass"
    cuts = f"{mass_var} > 100 && {mass_var} < 180 && is_{channel_US}{category_var} == 1"
    print(f"Original file name: {source_path}")
    print("Cutflow: " + cuts)
    print(f"New BDT file name {skim_path}")

    original_file = root.TFile.Open(source_path)
    if not original_file or original_file.IsZombie():
        raise RuntimeError(f"could not open {source_path} with ROOT")
    n_entries = int(original_file.Get("tree_output").GetEntries())
    n_chunks = SKIM_CHUNKS if n_chunks is None else max(1, int(n_chunks))
    if n_chunks > 1 and n_entries >= SKIM_CHUNK_MIN_ENTRIES:
        original_file.Close()
        _copy_and_skim_chunked(source_path, skim_path, cuts, n_entries, n_chunks)
        return
    skim_file = root.TFile.Open(skim_path, "RECREATE")
    skim_tree = original_file.Get("tree_output").CopyTree(cuts)
    skim_tree.Write("tree_output")
    skim_file.Close()
    original_file.Close()


def _copy_and_skim_chunked(source_path, skim_path, cuts, n_entries, n_chunks):
    """CopyTree n_chunks contiguous entry ranges in parallel, then hadd them in range order."""
    if shutil.which("hadd") is None:
        raise RuntimeError("hadd is not on PATH (run inside cmsenv); cannot merge the skim chunks")
    edges = np.linspace(0, n_entries, n_chunks + 1).astype(np.int64)
    jobs = [(f"{skim_path}.part{i}", int(edges[i]), int(edges[i + 1] - edges[i]))
            for i in range(n_chunks)]
    try:
        t0 = time.time()
        running = [subprocess.Popen(
            [sys.executable, "-c", _SKIM_CHUNK_PROGRAM, source_path, out, cuts, str(first), str(n)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for out, first, n in jobs]
        counts = []
        for (out, first, n), process in zip(jobs, running):
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                raise RuntimeError(f"skim of entries [{first}, {first + n}) of {source_path} "
                                   f"failed:\n{stderr.strip()}")
            counts.append(int(stdout.strip().splitlines()[-1]))
        t1 = time.time()
        # order matters: hadd appends trees in argument order, and `jobs` is in entry order
        subprocess.run(["hadd", "-f", skim_path] + [out for out, _, _ in jobs], check=True)
        print(f"[TIME ] skim chunks: {t1 - t0:.1f} s in {n_chunks} processes "
              f"({counts} rows) + {time.time() - t1:.1f} s hadd")
    finally:
        for out, _, _ in jobs:
            if os.path.exists(out):
                os.remove(out)


def score_skim_in_chunks(file_name, names, bundle, chunk_rows=SCORE_CHUNK_ROWS, legacy=False):
    """Fold-matched scores for every row of a scored tuple, read in row blocks.

    Returns (scores, folds), both in file row order. Each block's folds come from that block's
    OWN `event` values (xgb_kfold.fold_of_event), so nothing here depends on row order or on
    the rows lining up with any other file -- which is what makes the same code usable for the
    nominal tuples and for the systematic ones, whose rows do not line up with the nominal.

    `event` is read as its own integer column and deliberately kept out of the feature matrix:
    it is a ULong64_t reaching ~6.5e9 in Data, well past the 2**24 where the float32 matrix
    stops being exact, and it must never become a training input.

    Reading the whole file at once and casting it to float64 peaked near 8 GB on the 28M-row
    ggH DY skim, which is what made long `--stage apply` runs die. Blocks bound that at a few
    hundred MB. Scoring in float32 is not an approximation: every feature branch is already a
    float32 (n_jet is a small int32), `preprocess_features` casts to float32 regardless and the
    DMatrix is float32.

    With legacy=True there is a single model carrying fold id 0, so every row is scored by it.
    """
    import xgb_kfold as kf

    with uproot.open(file_name, **kf.uproot_open_options()) as f:
        tree = f["tree_output"]
        n_rows = tree.num_entries
        if not legacy and kf.EVENT_ID not in tree:
            # same message as kf.read_event_ids, raised before any of the work below
            kf.read_event_ids(file_name)
    wanted = list(names) if legacy else list(names) + [kf.EVENT_ID]

    y_pred = np.empty(n_rows, dtype=np.float32)
    folds = np.empty(n_rows, dtype=np.int8)
    start = 0
    for arrays in uproot.iterate({file_name: "tree_output"}, wanted, library="np",
                                 step_size=chunk_rows, **kf.uproot_open_options()):
        # columns pinned to `names` so the matrix column order is the model's feature order,
        # and so `event` cannot leak into it
        block = pd.DataFrame(arrays, columns=list(names))
        mask_undefined_jet_features(block)
        x = block.to_numpy(dtype=np.float32)
        n = len(x)
        fold_block = (np.zeros(n, dtype=np.int8) if legacy
                      else kf.fold_of_event(arrays[kf.EVENT_ID]))
        del block, arrays
        if start + n > n_rows:
            raise RuntimeError(f"{file_name}: read more than the {n_rows} rows it reports")
        y_pred[start:start + n] = kf.predict_by_fold(x, fold_block, bundle)
        folds[start:start + n] = fold_block
        start += n
    if start != n_rows:
        raise RuntimeError(f"{file_name}: scored {start} of {n_rows} rows")
    return y_pred, folds


def score_tuple_into(source_dir, source_name, out_dir, out_name, channel_US, category_var,
                     use_bsConstrain, names, bundle, tag, legacy=False):
    """Skim one tuple into out_dir/out_name and append BDT_<channel> + BDT_fold to it.

    The one scoring path, shared by the nominal tuples (append_BDT_score) and the systematic
    ones (append_BDT_score_to_sys), so the two cannot disagree about the fold rule.

    Every row is scored by the model that held out its own event's fold, i.e. a model that was
    NOT trained on it (out-of-fold). With legacy=True the `bundle` is the single pre-K-fold
    model, every row is scored by it, and BDT_fold is written as -1 to mark the scores as NOT
    fold-matched -- those MC scores are in-sample for the 60% the legacy model trained on, so
    they are for comparison only, never for a quoted result.
    """
    os.makedirs(out_dir, exist_ok=True)
    file_name = out_dir + out_name
    print(f"[INFO] Creating BDT file: {file_name}")
    t_skim = time.time()
    copy_and_skim_tree(source_dir, source_name, out_dir, out_name, channel_US, use_bsConstrain,
                       category_var)
    print(f"[TIME ] {tag} skim: {time.time() - t_skim:.1f} s")

    t_score = time.time()
    y_pred, folds = score_skim_in_chunks(file_name, names, bundle, legacy=legacy)
    if legacy:
        print(f"[INFO] {tag}: {len(folds)} events, all scored by the single legacy model")
    else:
        print(f"[INFO] {tag}: events per fold "
              f"{np.bincount(folds, minlength=len(bundle)).tolist()}  (fold = event % "
              f"{len(bundle)})")
    print(f"[TIME ] {tag} score: {time.time() - t_score:.1f} s")
    # NOTE: the former debug histogram of y_pred was removed: for Data it covered the
    # blinded 120-130 GeV window (see CLAUDE.md blinding policy).

    t_append = time.time()
    append_branches(file_name, {
        "BDT_" + channel_US: ("F", y_pred),
        "BDT_fold": ("I", (np.full(len(folds), -1) if legacy else folds).astype(np.int32)),
    })
    print(f"[TIME ] {tag} append: {time.time() - t_append:.1f} s "
          f"(total {time.time() - t_skim:.1f} s)")
    return file_name


def append_BDT_score(
    file_type,
    channel_US,
    era,
    signal_subset,
    background_subset,
    variables,
    bundle,
    use_bsConstrain,
    use_reCategorization,
    legacy=False,
):
    """Fold-matched scoring of a nominal tuple: an event in fold i is scored by fold model i,
    which was NOT trained on it (out-of-fold). The fold is `event % n_folds`
    (xgb_kfold.fold_of_event), so MC, Data and every systematic variation follow the identical
    rule and an event keeps its fold between the training skim and here no matter how either
    file was ordered, hadded or re-made.

    Writes BDT_<channel> (float, as before) plus BDT_fold (int) into the same
    root_io/tuples/BDT_score/... file the single-model version wrote.
    """
    p = _scoring_paths(file_type, channel_US, era, signal_subset, background_subset,
                       use_reCategorization, legacy=legacy)
    names = [var[0] for var in variables]
    if names != list(bundle[0]["meta"]["variables"]):
        raise RuntimeError("input variables differ from the ones the fold models were trained with")
    score_tuple_into(p["tuple_path"], p["tuple_name"], p["BDT_path"], p["BDT_name"],
                     channel_US, p["category_var"], use_bsConstrain, names, bundle,
                     tag=f"{file_type}_{era}", legacy=legacy)


def append_BDT_score_to_sys(
    file_type,
    channel_US,
    era,
    signal_subset,
    background_subset,
    variables,
    bundle,
    use_bsConstrain,
    systematics_dir=SYSTEMATICS_TUPLE_DIR,
):
    """Fold-matched scoring of the systematic tuples, through the same path as the nominal ones.

    This used to be single-model and NOT fold-aware, because a systematic tuple's rows do not
    line up with the nominal ones (the b-veto and mass cuts move with the variation), so a
    varied event could not be matched to its nominal event's fold. With fold = event % n_folds
    that problem is gone: a varied event carries the same `event` as its nominal self and so
    lands in the same fold, and is therefore scored by the same model -- one that was not
    trained on it. score_tuple_into() raises a clear error if a systematic tuple predates the
    `event` branch.

    `systematics_dir` defaults to SYSTEMATICS_TUPLE_DIR, which is a hardcoded path into another
    user's EOS area (a known rough edge, see CLAUDE.md); pass it explicitly to point elsewhere.
    """
    subset_title = f"B{background_subset}_S{signal_subset}"

    systematics = [
        "scale_up",
        "scale_down",
        "smearing_up",
        "smearing_down",
    ]

    jet_jes_syst_names = [
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

    for syst_name in jet_jes_syst_names:
        systematics.extend(
            [
                f"{syst_name}_up",
                f"{syst_name}_down",
            ]
        )

    tuple_path = systematics_dir
    BDT_path = f"{tuple_path}BDT_score/{channel_US}/{subset_title}/"
    os.makedirs(BDT_path, exist_ok=True)

    names = [var[0] for var in variables]
    if names != list(bundle[0]["meta"]["variables"]):
        raise RuntimeError("input variables differ from the ones the fold models were trained with")
    print(f"[INFO] {len(bundle)} fold models; systematic tuples from {tuple_path}")

    successful_systematics = []
    missing_systematics = []
    failed_systematics = []

    for syst_index, systematic in enumerate(systematics, start=1):
        tuple_name = f"{file_type}_{era}_{systematic}_tuples.root"
        input_file_name = tuple_path + tuple_name
        # the systematic tuple's filename is preserved inside BDT_score
        output_file_name = BDT_path + tuple_name

        print()
        print("=" * 80)
        print(f"[INFO] Systematic {syst_index}/{len(systematics)}: {systematic}")
        print(f"[INFO] Input:  {input_file_name}")
        print(f"[INFO] Output: {output_file_name}")
        print("=" * 80)

        if not os.path.exists(input_file_name):
            print("[WARNING] Input file does not exist. Skipping.")
            missing_systematics.append(systematic)
            continue

        try:
            score_tuple_into(tuple_path, tuple_name, BDT_path, tuple_name, channel_US,
                             "_category", use_bsConstrain, names, bundle,
                             tag=f"{file_type}_{era}_{systematic}")
            successful_systematics.append(systematic)
            print(f"[INFO] Finished systematic: {systematic}")
        except Exception as error:
            failed_systematics.append((systematic, str(error)))
            print(f"[ERROR] Failed systematic {systematic}: {error}")

    print()
    print("=" * 80)
    print("[INFO] Systematic BDT processing completed")
    print(f"[INFO] Successful: {len(successful_systematics)}")
    print(f"[INFO] Missing:    {len(missing_systematics)}")
    print(f"[INFO] Failed:     {len(failed_systematics)}")
    print(f"[INFO] Output directory: {BDT_path}")
    print("=" * 80)

    if missing_systematics:
        print("[WARNING] Missing systematics:")
        for systematic in missing_systematics:
            print(f"  {systematic}")
    if failed_systematics:
        print("[ERROR] Failed systematics:")
        for systematic, error in failed_systematics:
            print(f"  {systematic}: {error}")
    return dict(successful=successful_systematics, missing=missing_systematics,
                failed=failed_systematics)


def get_variables(channel_US, use_bsConstrain):
    channel_vars = [
        ["diMuon_rapidity", "diMuon_rapidity", r"$y_{\mu\mu}$"],
        ["mu1_eta", "mu1_eta", r"$\eta_{\mu 1}$"],
        ["mu2_eta", "mu2_eta", r"$\eta_{\mu 2}$"],
        ["phi_CS", "phi_CS", r"$\phi_{CS}$"],
        ["cos_theta_CS", "cos_theta_CS", r"$cos(\theta_{CS})$"],
        # # Jet vchannel_vars
        ["n_jet", "n_jet", r"$N_{jets}$"],
        ["leading_jet_pt", "leading_jet_pt", r"$p_T^{j1}$"],
        ["leading_jet_eta", "leading_jet_eta", r"$\eta_{j1}$"],
        ["subleading_jet_pt", "subleading_jet_pt", r"$p_T^{j2}$ [GeV]"],
        ["subleading_jet_eta", "subleading_jet_eta", r"$\eta_{j2}$"],
        ["diJet_mass", "diJet_mass", r"$m_{jj}$ [GeV]"],
        ["delta_eta_diJet", "delta_eta_diJet", r"$\Delta\eta_{jj}$"],
        ["delta_phi_diJet", "delta_phi_diJet", r"$\Delta\phi_{jj}$ [rad]"],
        ["z_zeppenfeld", "z_zeppenfeld", r"$Z^{*} Zeppendfeld$"],
        [
            "min_delta_eta_diMuon_jet",
            "min_delta_eta_diMuon_jet",
            r"min$|\Delta\eta_{\mu\mu,j}|$",
        ],
        [
            "min_delta_phi_diMuon_jet",
            "min_delta_phi_diMuon_jet",
            r"min$|\Delta\phi_{\mu\mu,j}|$ [rad]",
        ],
        [
            "leading_jet_btagPNetQvG",
            "leading_jet_btagPNetQvG",
            r"$PNet QvsG_{j1}$",
        ],
        [
            "subleading_jet_btagPNetQvG",
            "subleading_jet_btagPNetQvG",
            r"$PNet QvsG_{j2}$",
        ],
        [
            "leading_jet_nConstituents",
            "leading_jet_nConstituents",
            r"$nConstituents_{j1}$",
        ],
        [
            "subleading_jet_nConstituents",
            "subleading_jet_nConstituents",
            r"$nConstituents_{j2}$",
        ],
        # Categorical era index (1-6), present in MC and Data; never z-scored, see
        # xgb_kfold.NO_STANDARDIZE_VARIABLES.
        ["mc_campaign", "mc_campaign", r"campaign"],
    ]
    if use_bsConstrain:
        channel_vars += [
            ["diMuon_bsConstrainedPt", "diMuon_bsConstrainedPt", r"$p_T^{\mu\mu}$ [GeV] (bsC)"],
            [
                "mu1_bsConstrainedPt_mass_ratio", 
                "mu1_bsConstrainedPt_mass_ratio", 
                r"$p_T^{\mu 1}/m_{\mu\mu} (bsC)$"
            ],
            [
                "mu2_bsConstrainedPt_mass_ratio", 
                "mu2_bsConstrainedPt_mass_ratio", 
                r"$p_T^{\mu 2}/m_{\mu\mu} (bsC)$"
            ],
        ]
    else: 
        channel_vars += [
            ["diMuon_pt", "diMuon_pt", r"$p_T^{\mu\mu}$ [GeV]"],
            ["mu1_pt_mass_ratio", "mu1_pt_mass_ratio", r"$p_T^{\mu 1}/m_{\mu\mu}$"],
            ["mu2_pt_mass_ratio", "mu2_pt_mass_ratio", r"$p_T^{\mu 2}/m_{\mu\mu}$"],
        ]
    if channel_US == "VBF":
        channel_vars += [
            # VBF specific vchannel_vars
            ["pt_balance", "pt_balance", r"$R(p_T)$"],
            ["pt_centrality", "pt_centrality", r"$p_{T}-centrality$"],
            ["n_SoftJet_pt2", "n_SoftJet_pt2", r"$N_{2}^{soft}$"],
            ["HT", "HT", r"$H_{T}^{2}(soft)$"],
        ]

    # DO NOT CHANGE THE ORDER OF THIS VARIABLES
    if use_bsConstrain:
        channel_vars += [
                        [
                            "diMuon_bsConstrainedMass",
                            "diMuon_bsConstrainedMass", 
                            "diMuon_bsConstrainedMass"
                        ],
                        [
                            "relative_diMuon_bsConstrainedMass_error", 
                            "relative_diMuon_bsConstrainedMass_error", 
                            "relative_diMuon_bsConstrainedMass_error"
                        ],
                        ["weight", "weight", "weight"]]
    else: 
        channel_vars += [["diMuon_mass", "diMuon_mass", "diMuon_mass"],
                        [
                            "relative_diMuon_mass_error",
                            "relative_diMuon_mass_error",
                            "relative_diMuon_mass_error"
                        ],
                        ["weight", "weight", "weight"]]
    return channel_vars

def plot_discriminator(
    y_test,
    y_pred,
    y_train,
    y_pred_train,
    sample_weights_test,
    sample_weights_train,
    era,
    plot_path,
    scale="log",
    eval_name="test",
    train_name="train",
    file_tag="",
):
    """Overlay of the discriminator on an evaluation sample and on the training
    sample. `eval_name`/`train_name` are the legend names: use "OOF (held-out fold)" /
    "in-fold (train)" for the K-fold models, "validation" for validation folds; the
    name "test" must only be used for the untouched test sample."""
    y_frame = pd.DataFrame(
        {"truth": y_test, "disriminator": y_pred, "weight": sample_weights_test}
    )
    y_frame_train = pd.DataFrame(
        {
            "truth": y_train,
            "disriminator": y_pred_train,
            "weight": sample_weights_train,
        }
    )
    discriminator_bkg = y_frame[y_frame["truth"] == 0]["disriminator"].values
    discriminator_bkg_train = y_frame_train[y_frame_train["truth"] == 0][
        "disriminator"
    ].values
    discriminator_signal = y_frame[y_frame["truth"] == 1]["disriminator"].values
    discriminator_signal_train = y_frame_train[y_frame_train["truth"] == 1][
        "disriminator"
    ].values
    weight_bkg = y_frame[y_frame["truth"] == 0]["weight"].values
    weight_bkg_train = y_frame_train[y_frame_train["truth"] == 0]["weight"].values
    weight_signal = y_frame[y_frame["truth"] == 1]["weight"].values
    weight_signal_train = y_frame_train[y_frame_train["truth"] == 1]["weight"].values

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.hist(
        discriminator_signal,
        density=True,
        bins=100,
        alpha=1.0,
        histtype="step",
        lw=2,
        label=f"Signal - {eval_name}",
        weights=weight_signal,
    )
    plt.hist(
        discriminator_signal_train,
        density=True,
        bins=100,
        alpha=1.0,
        histtype="step",
        lw=2,
        label=f"Signal - {train_name}",
        weights=weight_signal_train,
    )

    plt.hist(
        discriminator_bkg,
        density=True,
        bins=100,
        alpha=1.0,
        histtype="step",
        lw=2,
        label=f"Bkg - {eval_name}",
        weights=weight_bkg,
    )
    plt.hist(
        discriminator_bkg_train,
        density=True,
        bins=100,
        alpha=1.0,
        histtype="step",
        lw=2,
        label=f"Bkg - {train_name}",
        weights=weight_bkg_train,
    )
    plt.yscale(scale)
    plt.xlim([0.0, 1.0])

    if scale == "log":
        plt.ylim([0.001, 1000.0])
    plt.xlim([0.0, 1.0])
    plt.legend(loc="upper right")
    plt.xlabel("BDT response")
    plt.ylabel("Events")
    hep.cms.label(
        data="True",
        label="",
        year=era,
        com="13.6",
        lumi=str(luminosity[era]),
    )
    plt.savefig(f"{plot_path}training/mydiscriminator{file_tag}_{scale}Y.pdf")
    plt.savefig(f"{plot_path}training/mydiscriminator{file_tag}_{scale}Y.png")
    plt.close()


def draw_correlation_matrix(
    signal_file_name, bkg_file_name, correlation_vars, plot_path, test_name
):
    signal_file = root.TFile(signal_file_name)
    tree_signal = signal_file.Get("tree_output")
    bkg_file = root.TFile(bkg_file_name)
    tree_bkg = bkg_file.Get("tree_output")
    n_corr = len(correlation_vars)
    h2_corr_sig = root.TH2F(
        "h2_corr_sig", "h2_corr_sig", n_corr, 0, n_corr, n_corr, 0, n_corr
    )
    h2_corr_bkg = root.TH2F(
        "h2_corr_bkg", "h2_corr_bkg", n_corr, 0, n_corr, n_corr, 0, n_corr
    )

    for idx1 in range(n_corr):
        for idx2 in range(n_corr):
            tree_signal.Draw(
                f"{correlation_vars[idx1][0]}:{correlation_vars[idx2][0]}>>temp_sig"
            )
            tree_bkg.Draw(
                f"{correlation_vars[idx1][0]}:{correlation_vars[idx2][0]}>>temp_bkg"
            )
            
            sig_hist = root.gROOT.FindObject("temp_sig")
            bkg_hist = root.gROOT.FindObject("temp_bkg")
                
            if not sig_hist:
                print("Could not find temp_sig")
                continue
            
            if not bkg_hist:
                print("Could not find temp_bkg")
                continue
                
            h2_corr_sig.SetBinContent(
                idx1 + 1, idx2 + 1, sig_hist.GetCorrelationFactor()
            )
            
            h2_corr_bkg.SetBinContent(
                idx1 + 1, idx2 + 1, bkg_hist.GetCorrelationFactor()
            )
            sig_hist.Delete()
            bkg_hist.Delete()
            h2_corr_sig.GetZaxis().SetRangeUser(-1.0, 1.0)
            h2_corr_bkg.GetZaxis().SetRangeUser(-1.0, 1.0)
            for idx in range(n_corr):
                h2_corr_sig.GetXaxis().SetBinLabel(idx + 1, correlation_vars[idx][2])
                h2_corr_sig.GetYaxis().SetBinLabel(idx + 1, correlation_vars[idx][2])
                h2_corr_bkg.GetXaxis().SetBinLabel(idx + 1, correlation_vars[idx][2])
                h2_corr_bkg.GetYaxis().SetBinLabel(idx + 1, correlation_vars[idx][2])

    h2_corr_sig.LabelsOption("v", "X")
    h2_corr_bkg.LabelsOption("v", "X")
    my_canvas = root.TCanvas("my_canvas", "my_canvas", 200, 10, 900, 800)
    my_canvas.SetHighLightColor(2)
    my_canvas.SetFillColor(0)
    my_canvas.SetBorderMode(0)
    my_canvas.SetBorderSize(2)
    my_canvas.SetLeftMargin(0.12)
    my_canvas.SetRightMargin(0.12)
    my_canvas.SetBottomMargin(0.12)
    my_canvas.SetTopMargin(0.12)
    my_canvas.SetFrameBorderMode(0)
    my_canvas.SetFrameBorderMode(0)

    stops = np.array([0.00, 0.34, 0.61, 0.84, 1.00])
    red = np.array([0.50, 0.50, 1.00, 1.00, 1.00])
    green = np.array([0.50, 1.00, 1.00, 0.60, 0.50])
    blue = np.array([1.00, 1.00, 0.50, 0.40, 0.50])
    root.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, 255)
    root.gStyle.SetNumberContours(255)

    h2_corr_sig.Draw("COLZTEXT")
    h2_corr_sig.SetTitle("")
    my_canvas.SaveAs(f"{plot_path}variables/{test_name}_correlation_matrix_sig.png")
    my_canvas.SaveAs(f"{plot_path}variables/{test_name}_correlation_matrix_bkg.png")
    my_canvas.SaveAs(f"{plot_path}variables/{test_name}_correlation_matrix_bkg.C")


def extrac_information_from_roc_curve(
    fpr, tpr, thr, test_name, signal_events, bkg_events
):
    significance = []
    effSignal = []
    effBkg = []
    thresholds = []
    ctr = 0
    f_roc = open(f"roc/{test_name}_roc.txt", "w")
    for i in range(len(fpr)):
        if fpr[i] > 1e-5 and tpr[i] > 1e-5:
            # print(
            # "thr = " + str(thr[i]) + ", fpr = " + str(fpr[i]) + ", tpr = " + str(tpr[i])
            # )
            f_roc.write(
                "thr = "
                + str(thr[i])
                + ", fpr = "
                + str(fpr[i])
                + ", tpr = "
                + str(tpr[i])
                + " \n"
            )
            significance.append(signal_events * tpr[i] / math.sqrt(fpr[i] * bkg_events))
            effSignal.append(tpr[i])
            effBkg.append(fpr[i])
            thresholds.append(thr[i])
            # print significance[ctr], ' ' , fpr[ctr], ' ', tpr[ctr]
            ctr = ctr + 1
    f_roc.close()
    return significance, effSignal, effBkg, thresholds

def draw_roc_curve(fpr, tpr, test_name, plot_path, era, AUC):
    f = plt.figure()
    # ax = f.add_subplot(111)
    lw = 2
    plt.plot(fpr, tpr, color="darkorange", lw=lw, label="ROC curve")
    plt.plot([0, 1], [0, 1], color="navy", lw=lw, linestyle="--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.ylabel("Signal Efficiency")
    plt.xlabel("Background Efficiency")
    # plt.axhline(y=0.9, color="black", linestyle="--")
    # plt.axhline(y=0.8, color="black")
    # plt.text(0.5,0.1,'WP80: bkg eff = %.4f'%WP80_effBkg, fontsize=12)
    # plt.text(0.5,0.2,'WP90: bkg eff = %.4f'%WP90_effBkg, fontsize=12)
    # plt.text(0.5,0.3,'WP90: S/sqrt(B) = %.2f'%WP90_significance, fontsize=12)
    # plt.text(0.5, 0.3, "AUC = %.4f" % AUC, hhhontsize=12)
    plt.text(0.5, 0.3, "AUC = %.4f" % AUC)
    # plt.title('Receiver operating characteristic example')
    # plt.legend(loc="lower right")

    hep.cms.label(
        data="True",
        label="",
        year=era,
        com="13.6",
        lumi=str(luminosity[era]),
    )
    plt.savefig(f"{plot_path}training/myroc_{test_name}.pdf")
    plt.savefig(f"{plot_path}training/myroc_{test_name}.png")
    plt.close()


def plot_feature_importances(model, variables, test_name, plot_path):
    model.get_booster().feature_names = [row[2] for row in variables[:-3]]
    xgb.plot_importance(
        model, max_num_features=len(variables) - 3, xlabel="F score (weight)"
    )
    plt.savefig(
        f"{plot_path}training/myImportances_Fscore_{test_name}.pdf",
        bbox_inches="tight",
    )
    plt.savefig(
        f"{plot_path}training/myImportances_Fscore_{test_name}.png",
        bbox_inches="tight",
    )

def plot_xgb_tree(model, variables, test_name, plot_path):
    model.get_booster().feature_names = [row[1] for row in variables[:-3]]
    xgb.plot_tree(model)
    fig = plt.gcf()
    fig.set_size_inches(150, 100)
    # fig.set_size_inches(500, 50)
    plt.draw()
    plt.savefig(f"{plot_path}training/myTree_{test_name}.pdf")
    plt.savefig(f"{plot_path}training/myTree_{test_name}.png")


def save_model(model, test_name, use_bsConstrain):
    # Pickle dictionary using protocol 0.
    if use_bsConstrain:
        test_name = f"{test_name}_bsC"
    output = open("models/model_" + test_name + ".pkl", "wb")
    pickle.dump(model, output)
    output.close()
    model.get_booster().dump_model(f"models/model_{test_name}.txt")
    model.get_booster().save_model(f"models/model_{test_name}.xgb")

def plot_loss(test_loss, train_loss, test_name, plot_path, era):
    plt.style.use(hep.style.CMS)

    f = plt.figure()
    plt.plot(train_loss, label="Train")
    plt.plot(test_loss, label="Test")
    plt.xlabel("Boosting round")
    plt.ylabel("Log loss")
    plt.legend()
    #hep.cms.label("Preliminary", data=False, lumi=170.905, com=13.6)
    hep.cms.label(
        data="False",
        label="",
        year=era,
        com="13.6",
        lumi=str(luminosity[era]),
    )
    plt.tight_layout()
    plt.show()

    os.makedirs(f"{plot_path}training/", exist_ok=True)
    plt.savefig(f"{plot_path}training/loss_{test_name}.pdf")
    plt.savefig(f"{plot_path}training/loss_{test_name}.png")

def plot_BDT_sculpting(bdt_score, mass, weights, channel_US, era, plot_path, bdt_divisions=10, tag=""):
    """Mass sculpting of the BACKGROUND for cuts BDT > x, from one score per event.
    Pass background events only; for the K-fold models `bdt_score` is the concatenated
    OOF score (every event scored by the model that excluded it).

    Error bars are the statistical error of the area-normalized weighted histogram (see
    normalized_hist). The curves are NESTED subsets -- BDT > x for increasing x -- so their
    fluctuations are correlated and they are not independent measurements of the shape; the
    tightest cut has by far the fewest effective entries, which is printed per curve.

    With the K-fold models every MC event has an OOF score, so this uses 100% of the
    background. The single-split (no k-fold) version can only use its held-out 40% without
    scoring events in-sample, so it is correspondingly noisier."""
    import xgb_kfold as kf

    mass_low, mass_high = 115, 135
    hep.style.use("CMS")
    fig, ax = plt.subplots()

    hep.cms.label(data="False", label="", year=era, com="13.6", lumi=str(luminosity[era]))
    ax.set_xlabel(r'$M_{\mu\mu}$')
    ax.set_ylabel('Normalized Events')
    ax.set_title("BDT Sculpting " + channel_US + (f" ({tag})" if tag else ""), y=-0.15)

    for bdt_low in np.linspace(0, 1 - 1 / bdt_divisions, bdt_divisions):
        mask = (bdt_score > bdt_low) & (mass > mass_low) & (mass < mass_high)
        if weights[mask].sum() <= 0:  # no events above this cut (e.g. a very short smoke training)
            continue
        counts, err, bins = kf.normalized_hist(mass[mask], weights[mask], bins=20,
                                               range=(mass_low, mass_high))
        n_eff = kf.effective_entries(weights[mask])
        print(f"[INFO] sculpting BDT > {bdt_low:.2f}: {int(mask.sum())} events, "
              f"N_eff = {n_eff:.0f}")
        hep.histplot(counts, bins=bins, ax=ax, yerr=err, label=f"BDT > {bdt_low:.2f}")

    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    os.makedirs(f"{plot_path}training/", exist_ok=True)
    name = f"BDTsculpting{'_' + tag if tag else ''}_{channel_US}_{era}"
    plt.savefig(f"{plot_path}training/{name}.pdf", bbox_inches="tight")
    plt.savefig(f"{plot_path}training/{name}.png", bbox_inches="tight")
    plt.close()


def _variable_labels():
    """Axis labels, bin counts and ranges from plot_macros/utils/labels.py (a pure-data
    module, so importing it pulls in no plotting code). Returns empty dicts if the plot
    macros are not next to this package, in which case the plots fall back to auto-ranges."""
    import sys

    utils_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "plot_macros", "utils")
    if utils_dir not in sys.path:
        sys.path.append(utils_dir)
    try:
        import labels
        return labels.x_labels, labels.n_bins, labels.x_range
    except ImportError as e:
        print(f"[WARNING] plot_macros/utils/labels.py not importable ({e}); using auto-ranges")
        return {}, {}, {}


# these are plotted on a log y axis (same list as plot_macros/utils/sig_vs_bg.py)
LOG_Y_VARIABLES = frozenset({
    "leading_jet_pt", "subleading_jet_pt", "n_jet", "delta_eta_diJet", "z_zeppenfeld",
    "min_delta_phi_diMuon_jet", "min_delta_eta_diMuon_jet",
})


def plot_input_comparison(x, y, weights, variables, channel_US, era, plot_path):
    """Signal vs background shape for every BDT input variable, from the arrays the
    training actually uses: after mask_undefined_jet_features (so padded jet variables are
    missing, not 0/-1), after the training-region mass cut, and with the training weights.

    This differs from plot_macros/plot_sig_vs_bg.py, which plots a hand-maintained variable
    list straight from the skims -- that list has drifted from get_variables() and, with
    USE_BSCONSTRAIN, misses the bsConstrained inputs entirely. Binning and axis labels are
    reused from plot_macros/utils/labels.py. One PDF+PNG per variable in <plot_path>variables/.
    """
    import xgb_kfold as kf

    x_labels, n_bins, x_range = _variable_labels()
    out_dir = f"{plot_path}variables/"
    os.makedirs(out_dir, exist_ok=True)
    is_signal, is_bkg = y == 1, y == 0

    for i, var in enumerate(variables):
        name = var[0]
        sig_values, bkg_values = x[is_signal, i], x[is_bkg, i]
        sig_w, bkg_w = weights[is_signal], weights[is_bkg]
        # missing (padded) jet variables are NaN: leave them out of the shape comparison
        sig_ok, bkg_ok = np.isfinite(sig_values), np.isfinite(bkg_values)
        sig_values, sig_w = sig_values[sig_ok], sig_w[sig_ok]
        bkg_values, bkg_w = bkg_values[bkg_ok], bkg_w[bkg_ok]
        if len(sig_values) == 0 or len(bkg_values) == 0:
            print(f"[WARNING] {name}: no finite entries, skipped")
            continue

        key = name if f"{name}_{channel_US}" not in x_range else f"{name}_{channel_US}"
        bins = n_bins.get(key, 50)
        span = x_range.get(key)
        if span is None:  # not in labels.py: use a robust auto-range
            lo, hi = np.percentile(np.concatenate([sig_values, bkg_values]), [0.5, 99.5])
            span = (float(lo), float(hi)) if hi > lo else (float(lo) - 1, float(lo) + 1)

        if sig_w.sum() <= 0 or bkg_w.sum() <= 0:
            print(f"[WARNING] {name}: empty histogram in range {span}, skipped")
            continue
        sig_hist, sig_err, edges = kf.normalized_hist(sig_values, sig_w, bins=bins, range=span)
        bkg_hist, bkg_err, _ = kf.normalized_hist(bkg_values, bkg_w, bins=bins, range=span)
        if sig_hist.sum() <= 0 or bkg_hist.sum() <= 0:
            print(f"[WARNING] {name}: empty histogram in range {span}, skipped")
            continue

        fig, ax = plt.subplots()
        for hist, err, color, label in ((sig_hist, sig_err, "blue", "signal"),
                                        (bkg_hist, bkg_err, "red", "background")):
            hep.histplot(hist, edges, yerr=False, histtype="fill", label=label, ax=ax, color=color, alpha=0.4)
            hep.histplot(hist, edges, yerr=err, ax=ax, color=color, linewidth=2)
        hep.cms.label(data="False", label="", year=era, com="13.6", lumi=str(luminosity[era]), ax=ax)
        ax.set_xlabel(x_labels.get(name, var[2] if len(var) > 2 else name))
        ax.set_ylabel("Events / Total events")
        ax.set_xlim(edges[0], edges[-1])
        if name in LOG_Y_VARIABLES:
            ax.set_yscale("log")
            ax.set_ylim(1e-3, 1.1)
        else:
            ax.set_ylim(0.0, 1.3 * max(sig_hist.max(), bkg_hist.max()))
        ax.legend(frameon=False, loc="upper right")
        fig.savefig(f"{out_dir}{name}_{era}_sig_vs_bkg.pdf", bbox_inches="tight")
        fig.savefig(f"{out_dir}{name}_{era}_sig_vs_bkg.png", bbox_inches="tight")
        plt.close(fig)
    print(f"[INFO] signal-vs-background input plots written to {out_dir}")


def plot_standardization_check(x_train, x_eval, names, mean_map, std_map, plot_path, era,
                               eval_label="held-out fold", tag=""):
    """Per input variable, train vs held-out shapes BEFORE and AFTER standardization
    (BDTOptimizationTests.ipynb cell 22, adapted to the K-fold setup).

    Two things to read off these: the train and held-out curves should lie on top of each
    other (the split is unbiased), and the post-standardization plot should be the same
    shape on a rescaled axis, centred near 0 with unit width. A variable listed in
    xgb_kfold.NO_STANDARDIZE_VARIABLES is expected to look IDENTICAL in both -- that is the
    visual confirmation that the opt-out took effect.

    mean_map/std_map must be the maps of one actual model (fitted on its own training rows),
    so what is drawn is the transformation that model really applied. Histograms are
    area-normalized because the training sample is N_FOLDS-1 times larger than the held-out one.
    """
    import xgb_kfold as kf

    out_dir = f"{plot_path}standardization/"
    os.makedirs(out_dir, exist_ok=True)
    x_train_std = kf.preprocess_features(x_train, names, True, mean_map, std_map)
    x_eval_std = kf.preprocess_features(x_eval, names, True, mean_map, std_map)

    for i, name in enumerate(names):
        for stage, tr_col, ev_col in (("prestd", x_train[:, i], x_eval[:, i]),
                                      ("poststd", x_train_std[:, i], x_eval_std[:, i])):
            tr_col = np.asarray(tr_col, dtype=np.float64)
            ev_col = np.asarray(ev_col, dtype=np.float64)
            tr_col, ev_col = tr_col[np.isfinite(tr_col)], ev_col[np.isfinite(ev_col)]
            if len(tr_col) == 0 or len(ev_col) == 0:
                print(f"[WARNING] {name} ({stage}): no finite entries, skipped")
                continue
            both = np.concatenate([tr_col, ev_col])
            lo, hi = np.percentile(both, [0.1, 99.9])
            if not hi > lo:
                lo, hi = float(both.min()), float(both.max()) or 1.0
            h_tr, edges = np.histogram(tr_col, bins=50, range=(lo, hi), density=True)
            h_ev, _ = np.histogram(ev_col, bins=50, range=(lo, hi), density=True)

            fig, ax = plt.subplots()
            hep.histplot(h_tr, edges, ax=ax, label="train", linewidth=2)
            hep.histplot(h_ev, edges, ax=ax, label=eval_label, linewidth=2, linestyle="--")
            ax.set_xlabel(name)
            ax.set_ylabel("Normalized events")
            ax.set_title("Pre standardization" if stage == "prestd" else "Post standardization",
                         fontsize=15)
            ax.legend(frameon=False)
            if stage == "poststd":
                identity = mean_map.get(name) == 0.0 and std_map.get(name) == 1.0
                ax.text(0.02, 0.95, f"mean {mean_map.get(name, 0):.3g}, std {std_map.get(name, 1):.3g}"
                        + ("  (not standardized)" if identity else ""),
                        transform=ax.transAxes, fontsize=12, va="top")
            name_out = f"{name}_{stage}{'_' + tag if tag else ''}"
            fig.savefig(f"{out_dir}{name_out}.pdf", bbox_inches="tight")
            fig.savefig(f"{out_dir}{name_out}.png", bbox_inches="tight")
            plt.close(fig)
    print(f"[INFO] pre/post-standardization plots written to {out_dir}")


def plot_legacy_vs_kfold(y, weights, p_legacy, p_kfold, auc_legacy, auc_kfold, era, plot_path):
    """Overlaid ROC and discriminator for the two approaches on the SAME events (the 40% test
    set of the single split, where both are out-of-sample). Any difference is down to the
    no-k-fold model having trained on 60% of the data and each K-fold model on 80%.

    The single-split approach is labelled "no k-fold" in every plot; "legacy" survives only in
    the stage name, the BDT_score/<channel>legacy/ path and the file names, which are
    interfaces other scripts depend on."""
    from sklearn.metrics import roc_curve

    import xgb_kfold as kf

    out_dir = f"{plot_path}comparison/"
    os.makedirs(out_dir, exist_ok=True)

    fig, ax = plt.subplots()
    for p, auc, color, label in ((p_legacy, auc_legacy, "tab:red", "no k-fold (single 60/40 split)"),
                                 (p_kfold, auc_kfold, "tab:blue", "K-fold OOF")):
        fpr, tpr, _ = roc_curve(y, p, sample_weight=weights)
        ax.plot(fpr, tpr, lw=2, color=color, label=f"{label} (AUC = {auc:.4f})")
    ax.plot([0, 1], [0, 1], color="grey", lw=1, ls="--")
    ax.set_xlabel("Background efficiency")
    ax.set_ylabel("Signal efficiency")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.05)
    ax.legend(loc="lower right", fontsize=13)
    hep.cms.label(data="False", label="", year=era, com="13.6", lumi=str(luminosity[era]), ax=ax)
    fig.savefig(f"{out_dir}roc_noKfold_vs_kfold.pdf", bbox_inches="tight")
    fig.savefig(f"{out_dir}roc_noKfold_vs_kfold.png", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots()
    edges = np.linspace(0, 1, 51)
    # The four colours of the mydiscriminator plots, hard-coded rather than taken from the
    # style cycle: mplhep's CMS style only gives this (Petroff) palette in the training env,
    # and falls back to tab10 elsewhere, which is what made the two plots disagree. The OOF
    # curves keep exactly the colours they have there -- signal light blue, background red.
    curves = ((p_kfold, 1, "#5790FC", "K-fold OOF signal"),
              (p_legacy, 1, "#F89C20", "no k-fold signal"),
              (p_kfold, 0, "#E42536", "K-fold OOF background"),
              (p_legacy, 0, "#964A8B", "no k-fold background"))
    for p, cls, color, label in curves:
        m = y == cls
        h, _, _ = kf.normalized_hist(p[m], weights[m], bins=edges, density=True)
        hep.histplot(h, edges, ax=ax, yerr=False, color=color, lw=2, label=label)
    #ax.set_yscale("log")
    ax.set_xlabel("BDT response")
    ax.set_ylabel("Normalized events")
    ax.legend(fontsize=12, ncol=2)
    hep.cms.label(data="False", label="", year=era, com="13.6", lumi=str(luminosity[era]), ax=ax)
    fig.savefig(f"{out_dir}discriminator_noKfold_vs_kfold.pdf", bbox_inches="tight")
    fig.savefig(f"{out_dir}discriminator_noKfold_vs_kfold.png", bbox_inches="tight")
    plt.close(fig)
    print(f"[INFO] comparison plots written to {out_dir}")


def plot_loss_noKfold_vs_kfold(rounds, legacy_train, legacy_heldout, kfold_in_fold, kfold_oof,
                               era, plot_path, n_eff_note=None, control=None):
    """Weighted log loss vs boosting round for both approaches on one axis.

    SOLID curves are out-of-sample and are on the SAME events: the no-k-fold model on the
    held-out 40% of the single split, and each K-fold model on the part of that same 40% it
    excluded (out-of-fold). That pair is the like-for-like comparison.

    DASHED curves are in-sample and are on the SAME events too: one shared subsample of the
    single split's train 60%, of which each K-fold model trained on the 4/5 not in its own
    fold. So both the solid pair and the dashed pair are like-for-like; only solid-vs-dashed
    crosses pools, which is unavoidable (the no-k-fold model has no training events inside its
    own held-out 40%).

    Because every in-sample curve is evaluated on the same rows, the differences between them
    are a PAIRED measurement: the subsampling noise largely cancels, so a separation much
    smaller than each curve's own noise is still meaningful.

    `control` (optional) is the in-sample curve of one extra single-split model trained on
    80% -- exactly the per-model training size of a K-fold model. It answers whether the
    K-fold in-fold curve sits above the no-k-fold train curve because of training-set size
    alone: if so it lands on the K-fold in-fold curve, not the no-k-fold one.

    `kfold_in_fold` / `kfold_oof` are (n_models, len(rounds)) arrays; the mean over models is
    drawn with a +/- 1 std band, which is model-to-model spread, NOT a statistical error --
    compare it against the effective entries in `n_eff_note` before reading anything into it.
    All curves are plotted against a 1-based TREE COUNT (note this differs from plot_loss,
    which plots against the bare 0-based index). A curve whose length matches `rounds` is a
    recomputed grid curve and is plotted at those tree counts; a full-length per-round curve
    (e.g. straight out of XGBoost's evals_result) is plotted at 1..n instead. Getting this
    wrong silently squashes the grid curves into the first few rounds."""
    rounds = np.asarray(rounds)
    out_dir = f"{plot_path}comparison/"
    os.makedirs(out_dir, exist_ok=True)

    fig, ax = plt.subplots()
    # same colour->approach mapping as the discriminator panel above, so the two comparison
    # plots read as one set: K-fold light blue/red, no k-fold orange/purple
    for arr, color, label in ((kfold_oof, "#5790FC", "K-fold, out-of-fold"),
                              (kfold_in_fold, "#E42536", "K-fold, in-fold")):
        arr = np.asarray(arr, dtype=float)
        mean, std = arr.mean(axis=0), arr.std(axis=0)
        solid = label.endswith("out-of-fold")
        ax.fill_between(rounds, mean - std, mean + std, color=color, alpha=0.20, lw=0)
        ax.plot(rounds, mean, color=color, lw=2, ls="-" if solid else "--",
                label=f"{label} (mean $\\pm$ std, {arr.shape[0]} models)")
    def _x_for(curve):
        # a grid curve shares its length with `rounds`; a per-round curve does not
        return rounds if len(curve) == len(rounds) else np.arange(1, len(curve) + 1)

    for curve, color, ls, label in ((legacy_heldout, "#F89C20", "-", "no k-fold, test 40%"),
                                    (legacy_train, "#964A8B", "--", "no k-fold, train 60%")):
        curve = np.asarray(curve, dtype=float)
        ax.plot(_x_for(curve), curve, color=color, lw=2, ls=ls, label=label)
    if control is not None:
        # Petroff grey, dotted: a reference line that must recede visually while making a
        # coincidence with the red dashed K-fold in-fold curve unmistakable
        control = np.asarray(control, dtype=float)
        ax.plot(_x_for(control), control, color="#9C9CA1", lw=2.2, ls=":",
                label="no k-fold @80% train, in-sample (control)")

    ax.set_xlabel("Boosting round")
    ax.set_ylabel("Weighted log loss")
    ax.set_xlim(1, int(rounds[-1]))
    ax.legend(fontsize=11, loc="upper right")
    #note = ["solid: out-of-sample, identical held-out 40% for both approaches",
    #        "dashed: in-sample -- no k-fold on its own 60%, K-fold on the 40% it trained on"]
    #if n_eff_note:
    #    note.append(n_eff_note)
    # bottom-left: the curves all start high on the left, so this corner stays clear
    #ax.text(0.02, 0.02, "\n".join(note), transform=ax.transAxes,
    #        fontsize=9, va="bottom", color="0.35")
    hep.cms.label(data="False", label="", year=era, com="13.6", lumi=str(luminosity[era]), ax=ax)
    for ext in ("pdf", "png"):
        fig.savefig(f"{out_dir}loss_noKfold_vs_kfold.{ext}", bbox_inches="tight")
    plt.close(fig)
    print(f"[INFO] loss-vs-round comparison written to {out_dir}loss_noKfold_vs_kfold.pdf")


def plot_roc_per_fold(y, scores, folds, weights, era, plot_path, tag, n_folds=None):
    """One ROC per fold model, each evaluated on its OWN held-out fold -- i.e. on the events
    that model did not train on, which is exactly the OOF sample. The spread between the five
    curves is the model-to-model variation; a single curve lying apart from the rest means that
    fold trained on an unrepresentative sample. AUCs use the training weights, so the legend
    matches the per-fold numbers the final stage prints."""
    from sklearn.metrics import roc_auc_score, roc_curve

    n_folds = int(folds.max()) + 1 if n_folds is None else n_folds
    fig, ax = plt.subplots()
    colors = plt.cm.viridis(np.linspace(0, 0.9, n_folds))
    aucs = []
    for k, color in zip(range(n_folds), colors):
        m = folds == k
        if m.sum() == 0 or len(np.unique(y[m])) < 2:
            print(f"[WARNING] fold {k}: cannot draw a ROC (no events or one class only)")
            continue
        fpr, tpr, _ = roc_curve(y[m], scores[m], sample_weight=weights[m])
        auc = roc_auc_score(y[m], scores[m], sample_weight=weights[m])
        aucs.append(auc)
        ax.plot(fpr, tpr, lw=2, color=color, label=f"model {k} (AUC = {auc:.4f})")
    ax.plot([0, 1], [0, 1], color="grey", lw=1, ls="--")
    ax.set_xlabel("Background efficiency")
    ax.set_ylabel("Signal efficiency")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    # the summary goes in the legend title so it cannot overlap the entries
    title = f"mean AUC {np.mean(aucs):.4f} $\\pm$ {np.std(aucs):.4f}" if aucs else None
    ax.legend(loc="lower right", fontsize=12, title=title, title_fontsize=12)
    hep.cms.label(data="False", label="", year=era, com="13.6", lumi=str(luminosity[era]), ax=ax)
    os.makedirs(f"{plot_path}training/", exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{plot_path}training/roc_per_fold_{tag}.{ext}", bbox_inches="tight")
    plt.close(fig)


def plot_discriminator_per_fold(y, scores, folds, weights, era, plot_path, tag, n_folds=None):
    """Signal and background OOF discriminator shapes, one pair per fold model. The five
    signal curves should lie on top of each other, and likewise the five background curves:
    the models are different fits, so this is the check that they agree on the score scale
    before their outputs are merged into one distribution for the categories."""
    import xgb_kfold as kf

    n_folds = int(folds.max()) + 1 if n_folds is None else n_folds
    fig, ax = plt.subplots()
    # hex strings, not the RGBA arrays the colormap returns: mplhep 0.3.26 (the CMSSW one)
    # mistakes an ndarray colour for a per-histogram list of colours and raises IndexError
    colors = [matplotlib.colors.to_hex(c) for c in plt.cm.viridis(np.linspace(0, 0.9, n_folds))]
    edges = np.linspace(0, 1, 51)
    for k, color in zip(range(n_folds), colors):
        for cls, style, label in ((1, "-", "signal"), (0, "--", "background")):
            m = (folds == k) & (y == cls)
            if m.sum() == 0:
                continue
            h, err, _ = kf.normalized_hist(scores[m], weights[m], bins=edges, density=True)
            hep.histplot(h, edges, ax=ax, color=color, ls=style, lw=1.8)
    #ax.set_yscale("lin")
    ax.set_xlim(0, 1)
    ax.set_xlabel("BDT response (out-of-fold)")
    ax.set_ylabel("Normalized events")
    # colour = model, line style = class: 7 entries instead of 10, and outside the axes so
    # it never sits on top of the histograms
    from matplotlib.lines import Line2D

    handles = [Line2D([], [], color=c, lw=1.8, label=f"model {k}")
               for k, c in enumerate(colors)]
    handles += [Line2D([], [], color="black", lw=1.8, ls="-", label="signal"),
                Line2D([], [], color="black", lw=1.8, ls="--", label="background")]
    ax.legend(handles=handles, fontsize=12, loc="upper left", bbox_to_anchor=(1.02, 1),
              frameon=False)
    hep.cms.label(data="False", label="", year=era, com="13.6", lumi=str(luminosity[era]), ax=ax)
    os.makedirs(f"{plot_path}training/", exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{plot_path}training/discriminator_per_fold_{tag}.{ext}", bbox_inches="tight")
    plt.close(fig)


def plot_fold_balance(y, w, folds, plot_path, tag, era, n_folds, rel_tolerance=0.05):
    """How evenly the fold rule splits the training sample, drawn from the rows about to be
    trained on.

    The fold is `event % n_folds` (xgb_kfold.fold_of_event), which is a hash of an externally
    assigned number rather than a deliberate partition, so its balance is a property of the
    data and worth looking at rather than assuming. Two panels:

      left  -- events per fold, signal and background side by side, with the spread
               (max - min, as a percentage of the mean) quoted per class;
      right -- each fold's SHARE of the sample, unweighted and weighted, against the ideal
               1/n_folds and the same +/- `rel_tolerance` band that xgb_kfold.fold_summary
               warns outside of. The weighted share is the one that matters: with
               USE_WEIGHT_MASS_RES the weights are concentrated, so counts can be even while
               the yields are not.
    """
    y, w, folds = np.asarray(y), np.asarray(w), np.asarray(folds)
    k = np.arange(n_folds)
    sig, bkg = y == 1, y == 0
    n_sig = np.array([int((sig & (folds == i)).sum()) for i in k])
    n_bkg = np.array([int((bkg & (folds == i)).sum()) for i in k])
    w_sig = np.array([float(w[sig & (folds == i)].sum()) for i in k])
    w_bkg = np.array([float(w[bkg & (folds == i)].sum()) for i in k])

    def spread(v):
        """(max - min) / mean, in percent -- 0 for a perfectly even split."""
        return 100.0 * (v.max() - v.min()) / v.mean() if v.mean() else np.nan

    def share(v):
        return v / v.sum() if v.sum() else np.full_like(v, np.nan, dtype=float)

    def compact(v):
        return f"{v / 1000:,.1f}k" if v >= 10_000 else f"{v:,}"

    fig, (ax_n, ax_f) = plt.subplots(1, 2, figsize=(18, 7))
    width = 0.38
    for offset, counts, color, name in ((-width / 2, n_sig, "#5790FC", "signal"),
                                        (+width / 2, n_bkg, "#E42536", "background")):
        ax_n.bar(k + offset, counts, width, color=color,
                 label=f"{name} ({counts.sum():,}), spread {spread(counts):.2f}%")
        for x, v in zip(k + offset, counts):
            ax_n.text(x, v, compact(v), ha="center", va="bottom", fontsize=11)
    ax_n.set_xticks(k)
    ax_n.set_xlabel(f"Fold  (event % {n_folds})")
    ax_n.set_ylabel("Training events")
    ax_n.set_ylim(0, max(n_sig.max(), n_bkg.max()) * 1.28)
    ax_n.legend(fontsize=14, loc="upper right")

    ideal = 1.0 / n_folds
    curves = ((share(n_sig), "#5790FC", "o", "signal, unweighted"),
              (share(n_bkg), "#E42536", "o", "background, unweighted"),
              (share(w_sig), "#F89C20", "s", "signal, weighted"),
              (share(w_bkg), "#964A8B", "s", "background, weighted"))
    band_lo, band_hi = ideal * (1 - rel_tolerance), ideal * (1 + rel_tolerance)
    ax_f.axhline(ideal, color="#9C9CA1", ls="--", lw=1.5)
    worst_overall = 0.0
    for values, color, marker, label in curves:
        worst = 100.0 * np.abs(values - ideal).max() / ideal
        worst_overall = max(worst_overall, worst)
        ax_f.plot(k, values, marker=marker, ls="-", lw=2, color=color,
                  label=f"{label} (worst {worst:.2f}%)")
    # Scale to the DATA, not to the tolerance band. On an even split the band is far wider than
    # the spread, so anchoring the axis to it would flatten every curve into one line -- and
    # shading it would just grey out the whole panel. The band is drawn only when one of its
    # edges is actually in view, i.e. when something is getting close to it; otherwise the
    # legend title carries the number.
    allv = np.concatenate([v for v, _, _, _ in curves])
    pad = max((allv.max() - allv.min()) * 0.45, ideal * 0.002)
    ymin, ymax = allv.min() - pad, allv.max() + pad
    if allv.min() < band_lo or allv.max() > band_hi:
        ymin, ymax = min(ymin, band_lo * 0.998), max(ymax, band_hi * 1.002)
    ax_f.set_ylim(ymin, ymax)
    if ymin < band_lo < ymax or ymin < band_hi < ymax:
        ax_f.axhspan(band_lo, band_hi, color="#9C9CA1", alpha=0.20)
    ax_f.set_xticks(k)
    ax_f.set_xlabel(f"Fold  (event % {n_folds})")
    ax_f.set_ylabel(f"Share of the sample  (ideal 1/{n_folds})")
    ax_f.legend(fontsize=13, loc="best",
                title=f"worst deviation {worst_overall:.2f}%   "
                      f"(fold_summary warns past {rel_tolerance:.0%})",
                title_fontsize=13)

    for ax in (ax_n, ax_f):
        hep.cms.label(data="False", label="", year=era, com="13.6",
                      lumi=str(luminosity.get(era, "")), ax=ax)
    plt.tight_layout()
    out = f"{plot_path}kFold/"
    os.makedirs(out, exist_ok=True)
    plt.savefig(f"{out}fold_balance_{tag}.pdf")
    plt.savefig(f"{out}fold_balance_{tag}.png")
    plt.close()
    print(f"[INFO] fold balance: counts per fold signal {n_sig.tolist()} "
          f"(spread {spread(n_sig):.2f}%), background {n_bkg.tolist()} "
          f"(spread {spread(n_bkg):.2f}%) -> {out}fold_balance_{tag}.pdf")
    return dict(n_sig=n_sig.tolist(), n_bkg=n_bkg.tolist(), w_sig=w_sig.tolist(),
                w_bkg=w_bkg.tolist(), spread_n_sig=spread(n_sig), spread_n_bkg=spread(n_bkg))


def plot_kfold_summary(fold_infos, plot_path, tag, era):
    """Per-fold validation AUC (weighted and unweighted), weighted validation log
    loss and best boosting iteration, with mean +/- std across folds."""
    folds = [i["fold"] for i in fold_infos]
    panels = [
        ("auc_w", "Weighted validation AUC"),
        ("auc", "Unweighted validation AUC"),
        ("logloss_w", "Weighted validation log loss"),
        ("best_iteration", "Best iteration (early stopping)"),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(24, 6))
    for ax, (key, title) in zip(axes, panels):
        vals = np.array([i[key] for i in fold_infos], dtype=float)
        ax.bar(folds, vals, color="tab:blue", alpha=0.8)
        ax.axhline(vals.mean(), color="k", ls="--", label=f"mean = {vals.mean():.4g} $\\pm$ {vals.std():.2g}")
        ax.axhspan(vals.mean() - vals.std(), vals.mean() + vals.std(), color="k", alpha=0.1)
        if key.startswith("auc"):
            lo = max(vals.min() - 4 * max(vals.std(), 1e-4), 0.0)
            ax.set_ylim(lo, min(vals.max() + 4 * max(vals.std(), 1e-4), 1.0))
        ax.set_xlabel("Validation fold")
        ax.set_title(title, fontsize=16)
        ax.legend(fontsize=14)
    plt.tight_layout()
    os.makedirs(f"{plot_path}training/", exist_ok=True)
    plt.savefig(f"{plot_path}training/kfold_summary_{tag}.pdf")
    plt.savefig(f"{plot_path}training/kfold_summary_{tag}.png")
    plt.close()


def plot_fold_loss_curves(folds, plot_path, tag, era, second_label="validation"):
    """Train (dashed) and held-out (solid) log loss per boosting round, one colour per
    fold. `folds` is the list of per-fold dicts from cross_validate_config (second curve
    = validation, early stopping marked) or train_final_kfold (second curve = the
    held-out fold, monitoring only)."""
    fig, ax = plt.subplots()
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(folds)))
    for c, fold in zip(colors, folds):
        ax.plot(fold["train_logloss"], ls="--", color=c)
        ax.plot(fold["val_logloss"], ls="-", color=c, label=f"fold {fold['fold']}")
        if "best_iteration" in fold:
            ax.axvline(fold["best_iteration"], color=c, ls=":", alpha=0.6)
    ax.set_xlabel("Boosting round")
    ax.set_ylabel("Log loss")
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color=c, lw=1.8, label=f"model {k}")
               for k, c in enumerate(colors)]
    handles += [Line2D([], [], color="black", lw=1.8, ls="-", label=second_label),
                Line2D([], [], color="black", lw=1.8, ls="--", label="Train")]
    ax.legend(handles=handles, fontsize=12, loc="upper left", bbox_to_anchor=(1.02, 1),
              frameon=False)
    hep.cms.label(data="False", label="", year=era, com="13.6", lumi=str(luminosity[era]))
    #ax.tight_layout()
    os.makedirs(f"{plot_path}training/", exist_ok=True)
    for ext in ("pdf", "png"):
        plt.savefig(f"{plot_path}training/loss_folds_{tag}.{ext}", bbox_inches="tight")
    plt.close(fig)


def plot_feature_importance_kfold(models, variables, tag, plot_path):
    """Feature importance averaged over the fold models (mean +/- std over folds), for
    'weight' (F score) and 'gain'. Does not rename any booster's feature names."""
    labels = [row[2] for row in variables[:-3]]
    n = len(labels)
    for importance_type in ("weight", "gain"):
        mat = np.zeros((len(models), n))
        for k, model in enumerate(models):
            score = model.get_booster().get_score(importance_type=importance_type)
            for name, val in score.items():
                mat[k, int(name.lstrip("f"))] = val
        mean, std = mat.mean(axis=0), mat.std(axis=0)
        order = np.argsort(mean)
        fig, ax = plt.subplots(figsize=(10, 12))
        ax.barh(np.arange(n), mean[order], xerr=std[order], color="tab:blue", alpha=0.8)
        ax.set_yticks(np.arange(n))
        ax.set_yticklabels([labels[i] for i in order])
        ax.set_xlabel(f"{importance_type} (mean $\\pm$ std over {len(models)} fold models)")
        plt.savefig(f"{plot_path}training/myImportances_{importance_type}_kfold_{tag}.pdf", bbox_inches="tight")
        plt.savefig(f"{plot_path}training/myImportances_{importance_type}_kfold_{tag}.png", bbox_inches="tight")
        plt.close()


# ---------------------------------------------------------------------------
# K-fold scoring: event in fold i -> model i
# ---------------------------------------------------------------------------
def _scoring_paths(file_type, channel_US, era, signal_subset, background_subset, use_reCategorization,
                   legacy=False):
    subset_title = f"B{background_subset}_S{signal_subset}"
    file_append, category_var, root_append = "", "_category", ""
    if use_reCategorization:
        file_append, category_var, root_append = "reCat", "_categoryBDT", "_categorized"
    if legacy:
        # a sibling tree under BDT_score/<channel>legacy/, so the fold-matched scores, the
        # hadd driver (`hadd_bdt.sh <ch> legacy`) and the category store stay separate
        file_append += "legacy"
    tuple_path = "../../root_io/tuples/"
    return dict(
        subset_title=subset_title, category_var=category_var, root_append=root_append,
        tuple_path=tuple_path, tuple_name=f"{file_type}_{era}_tuples{root_append}.root",
        BDT_path=f"{tuple_path}BDT_score/{channel_US}{file_append}/{subset_title}/",
        BDT_name=f"{file_type}_{era}_{subset_title}.root",
    )


def selection_mask(tuple_file, channel_US, category_var, use_bsConstrain):
    """Boolean mask over ALL entries of a tuple that reproduces the cut of
    copy_and_skim_tree, so skim row j is tuple entry flatnonzero(mask)[j].

    The scoring path no longer needs this -- a row's fold comes from its own `event` -- but
    audit_no_leakage.py and plot_macros/utils/muon_eff_sf.py use it to line a scored file up
    with the tuple it came from."""
    import xgb_kfold as kf

    mass_var = "diMuon_bsConstrainedMass" if use_bsConstrain else "diMuon_mass"
    with uproot.open(tuple_file, **kf.uproot_open_options()) as f:
        a = f["tree_output"].arrays([mass_var, f"is_{channel_US}{category_var}"], library="np")
    return (a[mass_var] > 100) & (a[mass_var] < 180) & (a[f"is_{channel_US}{category_var}"] == 1)


def append_branches(file_name, branches):
    """Append branches {name: (typecode 'F' or 'I', array)} to tree_output of a ROOT file."""
    root_file = root.TFile.Open(file_name, "UPDATE")
    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"Could not open {file_name} with ROOT")
    tree = root_file.Get("tree_output")
    n_entries = tree.GetEntries()
    holders, new_branches = {}, {}
    for name, (code, values) in branches.items():
        if len(values) != n_entries:
            root_file.Close()
            raise RuntimeError(f"{name}: {len(values)} values for {n_entries} entries in {file_name}")
        holders[name] = np.zeros(1, dtype=np.float32 if code == "F" else np.int32)
        new_branches[name] = tree.Branch(name, holders[name], f"{name}/{code}")
    # Deliberately NO tree.GetEntry(i) in this loop. Every value is already computed and
    # TBranch::Fill writes from the holder address, not from the tree, so reading the entry
    # back is pure waste: it decompresses all ~110 branches of the tuple once per entry,
    # measured at 50 us/entry -- about 45 minutes per ggH `--stage apply` run for values that
    # are then discarded. Do not put it back.
    items = [(new_branches[name], holders[name], values) for name, (_, values) in branches.items()]
    label = "+".join(branches)
    t0, step = time.time(), max(1, n_entries // 10)
    for i in range(n_entries):
        for branch, holder, values in items:
            holder[0] = values[i]
            branch.Fill()
        if i and i % step == 0:
            print(f"[INFO] appending {label}: {100 * i // n_entries}% "
                  f"({i}/{n_entries}, {time.time() - t0:.0f} s)")
    tree.Write("", root.TObject.kOverwrite)
    root_file.Close()


if __name__ == "__main__":
    sys.exit("xgb_utils is a library module. Train with train.py; append scores with "
             "`train.py --stage apply` (append_xgboost_discriminator_to_tree.py is deprecated).")
