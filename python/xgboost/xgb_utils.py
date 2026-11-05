"""BDT input variables, tuple scoring and plotting helpers for train.py."""
import os
import shutil
import subprocess
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import pandas as pd
import ROOT as root
import uproot
import xgboost as xgb
from matplotlib.lines import Line2D

import xgb_kfold as kf

plt.style.use(hep.style.CMS)
root.gROOT.SetBatch(True)
root.gStyle.SetOptStat(0)

utils_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "plot_macros", "utils")
if utils_dir not in sys.path:
    sys.path.append(utils_dir)

import labels
try:
    luminosity = labels.luminosity
except ImportError as e:
    print(f"[WARNING] plot_macros/utils/labels.py lumi info not importable ({e}); using predefined set")
    luminosity = {
    "2022": 7.9804,
    "2022EE": 26.6717,
    "2022Combined": 34.6521,
    "2023": 17.794,
    "2023BPix": 9.451,
    "2023Combined": 27.245,
    "2024": 109.08,
    "Combined": 170.905,
    }

# ---------------------------------------------------------------------------
# Input variables
# ---------------------------------------------------------------------------
# Jet variables that lib/CreateTuple.h pads with 0/-1 when the jet(s) do not exist. They are
# set to NaN so XGBoost treats them as missing instead of as a physical value.
DIJET_VARIABLES = frozenset({
    "subleading_jet_pt", "subleading_jet_eta", "diJet_mass", "delta_eta_diJet", "delta_phi_diJet",
    "z_zeppenfeld", "pt_balance", "pt_centrality", "subleading_jet_btagPNetQvG",
    "subleading_jet_nConstituents",
})
SINGLE_JET_VARIABLES = frozenset({
    "leading_jet_pt", "leading_jet_eta", "min_delta_eta_diMuon_jet", "min_delta_phi_diMuon_jet",
    "leading_jet_btagPNetQvG", "leading_jet_nConstituents",
})
# PNet QvG is -10 when the tagger gave no score for an existing jet
TAGGER_FAILURE_VALUE = -10.0
TAGGER_VARIABLES = frozenset({"leading_jet_btagPNetQvG", "subleading_jet_btagPNetQvG"})


def mask_undefined_jet_features(df):
    """In place: NaN out padded jet variables (dijet vars if n_jet < 2, leading-jet vars if
    n_jet < 1) and tagger-failure values. No-op without an n_jet column."""
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


# inputs added after the pre-K-fold (Matias's) BDT; --stage legacy trains without them
LEGACY_EXCLUDED_INPUTS = ("subleading_jet_eta", "leading_jet_btagPNetQvG", "subleading_jet_btagPNetQvG",
                          "leading_jet_nConstituents", "subleading_jet_nConstituents", "mc_campaign")


def get_variables(channel_US, use_bsConstrain, legacy_inputs=False):
    """[[branch, branch, label], ...]: the BDT inputs, followed by exactly three service
    columns (mass, relative mass error, weight) -- callers rely on `[:-3]` being the inputs.
    legacy_inputs: the input set of the pre-K-fold BDT (Matias's: 18 ggH / 22 VBF inputs, same
    order), i.e. without LEGACY_EXCLUDED_INPUTS."""
    inputs = [
        ("diMuon_rapidity", r"$y_{\mu\mu}$"),
        ("mu1_eta", r"$\eta_{\mu 1}$"),
        ("mu2_eta", r"$\eta_{\mu 2}$"),
        ("phi_CS", r"$\phi_{CS}$"),
        ("cos_theta_CS", r"$cos(\theta_{CS})$"),
        ("n_jet", r"$N_{jets}$"),
        ("leading_jet_pt", r"$p_T^{j1}$"),
        ("leading_jet_eta", r"$\eta_{j1}$"),
        ("subleading_jet_pt", r"$p_T^{j2}$ [GeV]"),
        ("subleading_jet_eta", r"$\eta_{j2}$"),
        ("diJet_mass", r"$m_{jj}$ [GeV]"),
        ("delta_eta_diJet", r"$\Delta\eta_{jj}$"),
        ("delta_phi_diJet", r"$\Delta\phi_{jj}$ [rad]"),
        ("z_zeppenfeld", r"$Z^{*} Zeppendfeld$"),
        ("min_delta_eta_diMuon_jet", r"min$|\Delta\eta_{\mu\mu,j}|$"),
        ("min_delta_phi_diMuon_jet", r"min$|\Delta\phi_{\mu\mu,j}|$ [rad]"),
        ("leading_jet_btagPNetQvG", r"$PNet QvsG_{j1}$"),
        ("subleading_jet_btagPNetQvG", r"$PNet QvsG_{j2}$"),
        ("leading_jet_nConstituents", r"$nConstituents_{j1}$"),
        ("subleading_jet_nConstituents", r"$nConstituents_{j2}$"),
        ("mc_campaign", r"campaign"),  # era index 1-6, never standardized
    ]
    if use_bsConstrain:
        inputs += [
            ("diMuon_bsConstrainedPt", r"$p_T^{\mu\mu}$ [GeV] (bsC)"),
            ("mu1_bsConstrainedPt_mass_ratio", r"$p_T^{\mu 1}/m_{\mu\mu} (bsC)$"),
            ("mu2_bsConstrainedPt_mass_ratio", r"$p_T^{\mu 2}/m_{\mu\mu} (bsC)$"),
        ]
    else:
        inputs += [
            ("diMuon_pt", r"$p_T^{\mu\mu}$ [GeV]"),
            ("mu1_pt_mass_ratio", r"$p_T^{\mu 1}/m_{\mu\mu}$"),
            ("mu2_pt_mass_ratio", r"$p_T^{\mu 2}/m_{\mu\mu}$"),
        ]
    if channel_US == "VBF":
        inputs += [
            ("pt_balance", r"$R(p_T)$"),
            ("pt_centrality", r"$p_{T}-centrality$"),
            ("n_SoftJet_pt2", r"$N_{2}^{soft}$"),
            ("HT", r"$H_{T}^{2}(soft)$"),
        ]
    if legacy_inputs:
        inputs = [row for row in inputs if row[0] not in LEGACY_EXCLUDED_INPUTS]
    # service columns, in this order: mass, relative mass error, weight
    mass = "diMuon_bsConstrainedMass" if use_bsConstrain else "diMuon_mass"
    service = [mass, f"relative_{mass}_error", "weight"]
    return [[name, name, label] for name, label in inputs] + [[name, name, name] for name in service]


# ---------------------------------------------------------------------------
# Scoring the tuples
# ---------------------------------------------------------------------------
SCORE_CHUNK_ROWS = 2_000_000  # rows held in memory at once while scoring (~150 MB)
SKIM_MASS_WINDOW = (100, 180)

# Hardcoded to another user's EOS area (a known rough edge, see CLAUDE.md); override with
# the `systematics_dir` argument of append_BDT_score_to_sys.
SYSTEMATICS_TUPLE_DIR = ("/eos/uscms/store/user/lpchmumu/mbarrial/"
                         "analyzer_HiggsMuMu_v2.0/tuples_v2.0.0/systematics/")
SYSTEMATIC_ERAS = ["2022", "2022EE", "2023", "2023BPix", "2024", "2025"]

# CopyTree is single threaded, so large skims are split into entry ranges copied by parallel
# subprocesses and merged with hadd (~4x faster). Each subprocess costs a few hundred MB.
SKIM_CHUNKS = max(1, min(6, (os.cpu_count() or 2) - 2))
SKIM_CHUNK_MIN_ENTRIES = 200_000
# run with `python3 -c` so the workers do not inherit this process's ROOT/XGBoost/OpenMP state
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


def systematic_names():
    """Muon scale/smearing plus every JES/JER source, each with _up and _down."""
    jes_sources = ["FlavorQCD", "RelativeBal", "HF", "BBEC1", "EC2", "Absolute"]
    jes_per_era = ["BBEC1", "RelativeSample", "EC2", "HF", "Absolute"]
    jer_bins = ["eta0to1p93_pt0toInf", "eta1p93to2p5_pt0toInf", "eta2p5to3p0_pt0to50",
                "eta2p5to3p0_pt50toInf", "eta3to5_pt0to50", "eta3to5_pt50toInf"]
    jet = ([f"CMS_scale_j_{s}" for s in jes_sources]
           + [f"CMS_scale_j_{s}_{era}" for era in SYSTEMATIC_ERAS for s in jes_per_era]
           + [f"CMS_res_j_{b}_{era}" for era in SYSTEMATIC_ERAS for b in jer_bins])
    return (["scale_up", "scale_down", "smearing_up", "smearing_down"]
            + [f"{name}_{d}" for name in jet for d in ("up", "down")])


def skim_cut(channel_US, category_var, use_bsConstrain):
    mass = "diMuon_bsConstrainedMass" if use_bsConstrain else "diMuon_mass"
    return (f"{mass} > {SKIM_MASS_WINDOW[0]} && {mass} < {SKIM_MASS_WINDOW[1]} "
            f"&& is_{channel_US}{category_var} == 1")


def copy_and_skim_tree(source_path, skim_path, cuts):
    """Copy the entries of `source_path` passing `cuts` into `skim_path`, in the original
    entry order (parallel entry ranges merged by hadd for big files)."""
    print(f"[INFO] skim {source_path} -> {skim_path}\n[INFO] cut: {cuts}")
    source = root.TFile.Open(source_path)
    if not source or source.IsZombie():
        raise RuntimeError(f"could not open {source_path} with ROOT")
    n_entries = int(source.Get("tree_output").GetEntries())
    if SKIM_CHUNKS == 1 or n_entries < SKIM_CHUNK_MIN_ENTRIES:
        skim = root.TFile.Open(skim_path, "RECREATE")
        source.Get("tree_output").CopyTree(cuts).Write("tree_output")
        skim.Close()
        source.Close()
        return
    source.Close()
    if shutil.which("hadd") is None:
        raise RuntimeError("hadd is not on PATH (run inside cmsenv)")
    edges = np.linspace(0, n_entries, SKIM_CHUNKS + 1).astype(np.int64)
    parts = [(f"{skim_path}.part{i}", int(edges[i]), int(edges[i + 1] - edges[i]))
             for i in range(SKIM_CHUNKS)]
    try:
        workers = [subprocess.Popen([sys.executable, "-c", _SKIM_CHUNK_PROGRAM, source_path, out, cuts,
                                     str(first), str(n)], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
                   for out, first, n in parts]
        for (_, first, n), worker in zip(parts, workers):
            _, stderr = worker.communicate()
            if worker.returncode != 0:
                raise RuntimeError(f"skim of entries [{first}, {first + n}) of {source_path} "
                                   f"failed:\n{stderr.strip()}")
        # hadd appends in argument order, which is entry order
        subprocess.run(["hadd", "-f", skim_path] + [out for out, _, _ in parts], check=True)
    finally:
        for out, _, _ in parts:
            if os.path.exists(out):
                os.remove(out)


def score_skim_in_chunks(file_name, names, bundles, legacy=False):
    """Fold-matched scores for every row of `file_name`, read in SCORE_CHUNK_ROWS blocks, for
    each bundle of `bundles` ({branch name: bundle}, all scoring the same rows from one read).
    Each row's fold comes from its own `event` (read as an integer, never as a feature).
    With legacy=True the single legacy model scores every row. Returns ({name: scores}, folds)."""
    with uproot.open(file_name, **kf.uproot_open_options()) as f:
        n_rows = f["tree_output"].num_entries
        if not legacy and kf.EVENT_ID not in f["tree_output"]:
            raise RuntimeError(f"{file_name} has no {kf.EVENT_ID!r} branch: re-make the tuples "
                               "with it, the fold of each row is unknown otherwise")
    branches = list(names) + ([] if legacy else [kf.EVENT_ID])

    scores = {name: np.empty(n_rows, dtype=np.float32) for name in bundles}
    folds = np.empty(n_rows, dtype=np.int8)
    start = 0
    for arrays in uproot.iterate({file_name: "tree_output"}, branches, library="np",
                                 step_size=SCORE_CHUNK_ROWS, **kf.uproot_open_options()):
        block = mask_undefined_jet_features(pd.DataFrame(arrays, columns=list(names)))
        x = block.to_numpy(dtype=np.float32)
        stop = start + len(x)
        folds[start:stop] = 0 if legacy else kf.fold_of_event(arrays[kf.EVENT_ID])
        for name, bundle in bundles.items():
            scores[name][start:stop] = kf.predict_by_fold(x, folds[start:stop], bundle)
        start = stop
    if start != n_rows:
        raise RuntimeError(f"{file_name}: scored {start} of {n_rows} rows")
    return scores, folds


def score_tuple_into(source_dir, source_name, out_dir, out_name, channel_US, category_var,
                     use_bsConstrain, names, bundles, tag, legacy=False):
    """Skim one tuple into out_dir/out_name and append one score branch per entry of `bundles`
    ({branch name, e.g. BDT_<channel>: bundle}) and BDT_fold, skimming and reading it once.
    The single scoring path for the nominal and the systematic tuples. Every bundle is
    fold-matched on the same `event % N_FOLDS`, so one BDT_fold serves all of them. Legacy
    scores are written with BDT_fold = -1 (not fold-matched: in-sample for the legacy model's
    train set)."""
    os.makedirs(out_dir, exist_ok=True)
    file_name = out_dir + out_name
    t0 = time.time()
    copy_and_skim_tree(source_dir + source_name, file_name,
                       skim_cut(channel_US, category_var, use_bsConstrain))
    t1 = time.time()
    scores, folds = score_skim_in_chunks(file_name, names, bundles, legacy=legacy)
    n_folds = max(len(b) for b in bundles.values())
    print(f"[INFO] {tag}: {len(folds)} events" + ("" if legacy else
          f", per fold {np.bincount(folds, minlength=n_folds).tolist()}"))
    t2 = time.time()
    branches = {name: ("F", values) for name, values in scores.items()}
    branches["BDT_fold"] = ("I", (np.full(len(folds), -1) if legacy else folds).astype(np.int32))
    append_branches(file_name, branches)
    print(f"[TIME ] {tag}: skim {t1 - t0:.1f} s, score {t2 - t1:.1f} s, append {time.time() - t2:.1f} s")
    return file_name


def scoring_paths(file_type, channel_US, era, signal_subset, background_subset, use_reCategorization,
                  legacy=False, dir_suffix=""):
    """Input tuple and output BDT_score file of one nominal sample. `dir_suffix` is appended to
    the BDT_score/<channel> directory (e.g. "optimized") so it does not overwrite the default."""
    subset_title = f"B{background_subset}_S{signal_subset}"
    file_append, category_var, root_append = ("reCat", "_categoryBDT", "_categorized") \
        if use_reCategorization else ("", "_category", "")
    if legacy:
        file_append += "legacy"  # a sibling BDT_score/<channel>legacy/ tree
    file_append += dir_suffix
    tuple_path = "../../root_io/tuples/"
    return dict(
        subset_title=subset_title, category_var=category_var, tuple_path=tuple_path,
        tuple_name=f"{file_type}_{era}_tuples{root_append}.root",
        BDT_path=f"{tuple_path}BDT_score/{channel_US}{file_append}/{subset_title}/",
        BDT_name=f"{file_type}_{era}_{subset_title}.root",
    )


def _check_variables(variables, bundle):
    names = [var[0] for var in variables]
    if names != list(bundle[0]["meta"]["variables"]):
        raise RuntimeError("input variables differ from the ones the fold models were trained with")
    return names


def append_BDT_score(file_type, channel_US, era, signal_subset, background_subset, variables,
                     bundle, use_bsConstrain, use_reCategorization, legacy=False, dir_suffix=""):
    """Score one nominal tuple into root_io/tuples/BDT_score/..."""
    names = _check_variables(variables, bundle)
    p = scoring_paths(file_type, channel_US, era, signal_subset, background_subset,
                      use_reCategorization, legacy=legacy, dir_suffix=dir_suffix)
    score_tuple_into(p["tuple_path"], p["tuple_name"], p["BDT_path"], p["BDT_name"], channel_US,
                     p["category_var"], use_bsConstrain, names, {f"BDT_{channel_US}": bundle},
                     tag=f"{file_type}_{era}", legacy=legacy)


def append_BDT_scores_multi(file_type, channel_US, era, signal_subset, background_subset, variables,
                            bundles, use_bsConstrain, use_reCategorization, dir_suffix="compare"):
    """Score one nominal tuple with several fold-model sets ({branch name: bundle}) into a single
    skimmed copy, root_io/tuples/BDT_score/<channel><dir_suffix>/..."""
    names = None
    for branch, bundle in bundles.items():
        try:
            names = _check_variables(variables, bundle)
        except RuntimeError as error:
            raise RuntimeError(f"{branch}: {error}") from None
    p = scoring_paths(file_type, channel_US, era, signal_subset, background_subset,
                      use_reCategorization, dir_suffix=dir_suffix)
    score_tuple_into(p["tuple_path"], p["tuple_name"], p["BDT_path"], p["BDT_name"], channel_US,
                     p["category_var"], use_bsConstrain, names, bundles, tag=f"{file_type}_{era}")


def append_BDT_score_to_sys(file_type, channel_US, era, signal_subset, background_subset, variables,
                            bundle, use_bsConstrain, systematics_dir=SYSTEMATICS_TUPLE_DIR,
                            dir_suffix=""):
    """Score every systematic tuple of one sample. A varied event keeps its `event`, so it
    lands in the same fold -- and is scored by the same model -- as its nominal self."""
    names = _check_variables(variables, bundle)
    out_dir = f"{systematics_dir}BDT_score/{channel_US}{dir_suffix}/B{background_subset}_S{signal_subset}/"
    systematics = systematic_names()
    done, missing, failed = [], [], []
    for i, systematic in enumerate(systematics, start=1):
        tuple_name = f"{file_type}_{era}_{systematic}_tuples.root"
        print(f"\n[INFO] Systematic {i}/{len(systematics)}: {systematic}")
        if not os.path.exists(systematics_dir + tuple_name):
            print(f"[WARNING] {systematics_dir + tuple_name} does not exist, skipped")
            missing.append(systematic)
            continue
        try:
            score_tuple_into(systematics_dir, tuple_name, out_dir, tuple_name, channel_US,
                             "_category", use_bsConstrain, names, {f"BDT_{channel_US}": bundle},
                             tag=f"{file_type}_{era}_{systematic}")
            done.append(systematic)
        except Exception as error:
            print(f"[ERROR] {systematic}: {error}")
            failed.append((systematic, str(error)))
    print(f"\n[INFO] systematics done: {len(done)} scored, {len(missing)} missing, "
          f"{len(failed)} failed -> {out_dir}")
    for systematic, error in failed:
        print(f"[ERROR]   {systematic}: {error}")
    return dict(successful=done, missing=missing, failed=failed)


def selection_mask(tuple_file, channel_US, category_var, use_bsConstrain):
    """Mask over all entries of a tuple reproducing the skim cut (for audit_no_leakage.py)."""
    mass = "diMuon_bsConstrainedMass" if use_bsConstrain else "diMuon_mass"
    category = f"is_{channel_US}{category_var}"
    with uproot.open(tuple_file, **kf.uproot_open_options()) as f:
        a = f["tree_output"].arrays([mass, category], library="np")
    return (a[mass] > SKIM_MASS_WINDOW[0]) & (a[mass] < SKIM_MASS_WINDOW[1]) & (a[category] == 1)


def append_branches(file_name, branches):
    """Append {name: ('F' or 'I', values)} as new branches of tree_output."""
    root_file = root.TFile.Open(file_name, "UPDATE")
    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"Could not open {file_name} with ROOT")
    tree = root_file.Get("tree_output")
    n_entries = tree.GetEntries()
    filled = []
    for name, (code, values) in branches.items():
        if len(values) != n_entries:
            root_file.Close()
            raise RuntimeError(f"{name}: {len(values)} values for {n_entries} entries in {file_name}")
        holder = np.zeros(1, dtype=np.float32 if code == "F" else np.int32)
        filled.append((tree.Branch(name, holder, f"{name}/{code}"), holder, values))
    # No tree.GetEntry(i) here: Fill() reads from the holder, and reading every entry back
    # would decompress all ~110 branches for nothing (~45 min per ggH apply).
    t0, step = time.time(), max(1, n_entries // 10)
    for i in range(n_entries):
        for branch, holder, values in filled:
            holder[0] = values[i]
            branch.Fill()
        if i and i % step == 0:
            print(f"[INFO] appending {'+'.join(branches)}: {100 * i // n_entries}% "
                  f"({time.time() - t0:.0f} s)")
    tree.Write("", root.TObject.kOverwrite)
    root_file.Close()


# ---------------------------------------------------------------------------
# Plot helpers
# ---------------------------------------------------------------------------
def _cms_label(ax, era):
    hep.cms.label(data=True, label="", year=era, com="13.6", lumi=str(luminosity.get(era, "")), ax=ax)


def _save(fig, path):
    """Save `path`.pdf and `path`.png (creating the directory) and close the figure."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{path}.{ext}", bbox_inches="tight")
    plt.close(fig)


# CMS-recommended Petroff 6-colour palette
CMS_COLORS = ["#5790fc", "#f89c20", "#e42536", "#964a8b", "#9c9ca1", "#7a21dd"]


def _fold_colors(n):
    # hex strings: the CMSSW mplhep mistakes an RGBA array for a list of colours
    return [matplotlib.colors.to_hex(c) for c in plt.cm.viridis(np.linspace(0, 0.9, n))]


# ---------------------------------------------------------------------------
# Training / performance plots
# ---------------------------------------------------------------------------
def significance_scan(fpr, tpr, thr, test_name, signal_events, bkg_events):
    """S/sqrt(B) along the ROC curve. Also writes roc/<test_name>_roc.txt (read by
    plot_macros/plot_roc_space.py). Returns (significance, eff_signal, eff_bkg, thresholds)."""
    keep = (fpr > 1e-5) & (tpr > 1e-5)
    fpr, tpr, thr = fpr[keep], tpr[keep], thr[keep]
    with open(f"roc/{test_name}_roc.txt", "w") as f:
        for t, fp, tp in zip(thr, fpr, tpr):
            f.write(f"thr = {str(t)}, fpr = {str(fp)}, tpr = {str(tp)} \n")  # str() keeps float32 short
    significance = signal_events * tpr / np.sqrt(fpr * bkg_events)
    return significance, tpr, fpr, thr


def draw_roc_curve(fpr, tpr, test_name, plot_path, era, auc):
    fig, ax = plt.subplots()
    ax.plot(fpr, tpr, color="darkorange", lw=2, label="ROC curve")
    ax.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Background Efficiency")
    ax.set_ylabel("Signal Efficiency")
    ax.text(0.5, 0.3, f"AUC = {auc:.4f}")
    _cms_label(ax, era)
    _save(fig, f"{plot_path}training/myroc_{test_name}")


def plot_roc_train_test(curves, era, path, title=""):
    """ROC curves of several samples in one plot (e.g. untouched test vs training sample).
    curves = [(fpr, tpr, label, auc), ...]; title names the weights / region used."""
    fig, ax = plt.subplots()
    for (fpr, tpr, label, auc), color, ls in zip(curves, ("darkorange", "tab:purple", "tab:green"), ("-", "--", ":")):
        ax.plot(fpr, tpr, color=color, lw=2, ls=ls, label=f"{label}: AUC = {auc:.4f}")
    ax.plot([0, 1], [0, 1], color="navy", lw=1.5, linestyle="--")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Background Efficiency")
    ax.set_ylabel("Signal Efficiency")
    ax.legend(loc="lower right", fontsize=13, title=title, title_fontsize=13)
    _cms_label(ax, era)
    _save(fig, path)


def plot_discriminator(y_eval, p_eval, y_train, p_train, w_eval, w_train, era, plot_path,
                       scale="log", eval_name="test", train_name="train", file_tag="", note=None):
    """BDT output for signal and background on an evaluation sample and on the training
    sample. Only call the evaluation sample "test" if it is the untouched test sample.
    note: text shown as the legend title (e.g. the train-vs-test AUC and KS numbers)."""
    fig, ax = plt.subplots()
    for cls, cls_name in ((1, "Signal"), (0, "Bkg")):
        for y, p, w, name in ((y_eval, p_eval, w_eval, eval_name),
                              (y_train, p_train, w_train, train_name)):
            m = y == cls
            ax.hist(p[m], weights=w[m], bins=100, density=True, histtype="step", lw=2,
                    label=f"{cls_name} - {name}")
    ax.set_yscale(scale)
    if scale == "log":
        ax.set_ylim(0.001, 1000.0)
    ax.set_xlim(0, 1)
    if scale == "linear" and note:  # room for the legend and its note above the histograms
        ax.set_ylim(top=ax.get_ylim()[1] * 1.6)
    ax.set_xlabel("BDT response")
    ax.set_ylabel("Events")
    ax.legend(loc="upper right", title=note, title_fontsize=11 if note else None, fontsize=12 if note else None)
    _cms_label(ax, era)
    _save(fig, f"{plot_path}training/mydiscriminator{file_tag}_{scale}Y")


def plot_BDT_sculpting(bdt_score, mass, weights, channel_US, era, plot_path, bdt_divisions=10, tag=""):
    """Normalized background mass shape for BDT > x (nested cuts, so the curves are correlated)."""
    fig, ax = plt.subplots()
    in_window = (mass > 115) & (mass < 135)
    for cut in np.linspace(0, 1 - 1 / bdt_divisions, bdt_divisions):
        m = in_window & (bdt_score > cut)
        if weights[m].sum() <= 0:
            continue
        counts, err, bins = kf.normalized_hist(mass[m], weights[m], bins=20, range=(115, 135))
        print(f"[INFO] sculpting BDT > {cut:.2f}: {m.sum()} events, "
              f"N_eff = {kf.effective_entries(weights[m]):.0f}")
        hep.histplot(counts, bins=bins, ax=ax, yerr=err, label=f"BDT > {cut:.2f}")
    ax.set_xlabel(r"$M_{\mu\mu}$")
    ax.set_ylabel("Normalized Events")
    ax.set_title(f"BDT Sculpting {channel_US}" + (f" ({tag})" if tag else ""), y=-0.15)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    _cms_label(ax, era)
    _save(fig, f"{plot_path}training/BDTsculpting{'_' + tag if tag else ''}_{channel_US}_{era}")


def plot_flat_reweighting(mass, w_before, w_after, edges, era, plot_path, tag):
    """Background mass spectrum with the training weights before and after reweight_to_flat."""
    fig, ax = plt.subplots()
    for w, label, color in ((w_before, "before reweighting", CMS_COLORS[0]),
                            (w_after, "after reweighting", CMS_COLORS[1])):
        counts, _ = np.histogram(mass, bins=edges, weights=w)
        var, _ = np.histogram(mass, bins=edges, weights=w ** 2)
        hep.histplot(counts, bins=edges, ax=ax, yerr=np.sqrt(var), color=color, label=label)
    ax.set_xlim(edges[0], edges[-1])
    ax.set_ylim(bottom=0)
    ax.set_xlabel(r"$M_{\mu\mu}$ [GeV]")
    ax.set_ylabel("Background training weight / bin")
    ax.legend(loc="lower left")
    _cms_label(ax, era)
    _save(fig, f"{plot_path}training/bkg_mass_flat_reweight_{tag}")


def plot_mass_weight_comparison(mass, weights, edges, era, plot_path, tag, sample):
    """Unit-area M_mumu shape under each weighting in `weights` ({label: w}), with a lower panel
    of the per-bin relative error (sqrt(sum w^2) propagated through the normalization)."""
    fig, (ax, ax_r) = plt.subplots(2, 1, sharex=True, gridspec_kw=dict(height_ratios=(3, 1), hspace=0.05))
    for (label, w), color in zip(weights.items(), CMS_COLORS):
        counts, err, _ = kf.normalized_hist(mass, w, bins=edges)
        print(f"[INFO] {sample} M_mumu with {label} weights: N_eff = {kf.effective_entries(w):.0f}")
        hep.histplot(counts, bins=edges, ax=ax, yerr=err, color=color, label=label)
        rel = np.divide(err, np.abs(counts), out=np.zeros_like(err), where=counts != 0)
        ax_r.stairs(rel, edges, color=color, lw=1.5)
    ax.set_xlim(edges[0], edges[-1])
    ax.set_ylim(bottom=0)
    ax.set_ylabel(f"Normalized events / {edges[1] - edges[0]:g} GeV")
    ax.set_xlabel("")
    ax.legend(loc="lower left", fontsize=14, title=sample)
    _cms_label(ax, era)
    ax_r.set_ylim(bottom=0)
    ax_r.set_xlabel(r"$M_{\mu\mu}$ [GeV]")
    ax_r.set_ylabel("Rel. error")
    _save(fig, f"{plot_path}training/mass_weight_comparison_{sample}_{tag}")


def _variant_style(result):
    """train.py --stage compare: colour by training weights, line style by parameter set
    (solid DEFAULT_PARAMS, dashed AUC Optuna; the Asimov-Optuna variants are purple dotted (raw
    background MC) and brown dash-dot (fitted background))."""
    colors = {"mass_res": CMS_COLORS[0], "weight+flat": CMS_COLORS[1], "mass_res+flatMassRes": CMS_COLORS[2]}
    if result.get("opt_tag") == "asimov":  # Asimov-Optuna config: its own colour, dotted
        return dict(color=CMS_COLORS[3], ls=":", lw=2.5)
    if result.get("opt_tag") == "asimovFit":
        return dict(color="#a96b59", ls="-.", lw=2.5)
    return dict(color=colors.get(result["training_weights"], CMS_COLORS[4]),
                ls="--" if result["optimized"] else "-", lw=2)


def plot_variant_roc_overlay(results, era, plot_path, channel_US):
    """Signal-region ROC (physics weights) of every --stage compare variant: background vs
    signal efficiency, log y."""
    fig, ax = plt.subplots()
    for r in results:
        ax.plot(r["tpr"], r["fpr"], label=f"{r['label']} (AUC {r['auc_w_phys']:.4f})", **_variant_style(r))
    ax.set_yscale("log")
    ax.set_xlim(0, 1)
    ax.set_ylim(1e-4, 1)
    ax.set_xlabel("Signal efficiency")
    ax.set_ylabel("Background efficiency")
    ax.set_title(channel_US + r": OOF, $M_{\mu\mu}$ signal region", y=-0.2, fontsize=14)
    ax.legend(loc="lower right", fontsize=12)
    _cms_label(ax, era)
    _save(fig, f"{plot_path}comparison/roc_variants_{channel_US}_{era}")


def plot_variant_significance_scan(results, era, plot_path, channel_US, zoom_margin=0.1):
    """S/sqrt(B) in the signal region vs signal efficiency for every --stage compare variant,
    with each variant's maximum marked. The lower panel zooms on the maxima: signal efficiency
    from the smallest to the largest maximum's, +- zoom_margin, and S/sqrt(B) from 90% of the
    lowest maximum to just above the highest (the rising edge of the curves is cut off)."""
    fig, (ax, ax_z) = plt.subplots(2, 1, figsize=(10, 12),
                                   gridspec_kw=dict(height_ratios=(3, 2), hspace=0.08))
    best_eff = [r["working_points"]["Max"]["eff_signal"] for r in results]
    lo, hi = max(0.0, min(best_eff) - zoom_margin), min(1.0, max(best_eff) + zoom_margin)
    best_sig = [r["working_points"]["Max"]["significance"] for r in results]
    for r in results:
        scan, best = r["scan"], r["working_points"]["Max"]
        style = _variant_style(r)
        for axis, label in ((ax, f"{r['label']} (max {best['significance']:.3f})"), (ax_z, None)):
            axis.plot(scan["eff_signal"], scan["significance"], label=label, **style)
            axis.plot(best["eff_signal"], best["significance"], marker="o", color=style["color"], ls="none")
    ax.axvspan(lo, hi, color="grey", alpha=0.15, lw=0)
    ax.set_xlim(0, 1)
    ax.set_ylim(bottom=0)
    ax.set_ylabel(r"$S/\sqrt{B}$")
    ax.legend(loc="lower center", fontsize=12)
    _cms_label(ax, era)
    ax_z.set_xlim(lo, hi)
    ax_z.set_ylim(0.9 * min(best_sig), max(best_sig) + 0.05 * (max(best_sig) - 0.9 * min(best_sig)))
    ax_z.set_xlabel("Signal efficiency")
    ax_z.set_ylabel(r"$S/\sqrt{B}$ (zoom)")
    _save(fig, f"{plot_path}comparison/significance_variants_{channel_US}_{era}")


def plot_variant_tight_mass(results, mass, weights, cut, era, plot_path, channel_US, bin_width=1.0):
    """Unit-area background M_mumu in the tight category (BDT > cut) of every --stage compare
    variant (`results[i]["oof_bkg"]`, row-aligned with `mass`/`weights`), against the inclusive
    background shape, with the ratio to inclusive below (error: the tight-category one only)."""
    edges = np.arange(kf.TRAIN_REGION[0], kf.TRAIN_REGION[1] + bin_width / 2, bin_width)
    fig, (ax, ax_r) = plt.subplots(2, 1, sharex=True, figsize=(10, 11),
                                   gridspec_kw=dict(height_ratios=(3, 1), hspace=0.05))
    inclusive, _, _ = kf.normalized_hist(mass, weights, bins=edges)
    hep.histplot(inclusive, bins=edges, ax=ax, color="grey", histtype="fill", alpha=0.35,
                 label="inclusive")
    for r in results:
        passed = r["oof_bkg"] > cut
        eff = weights[passed].sum() / weights.sum()
        print(f"[INFO] {r['label']} BDT > {cut:g}: background eff {eff:.4f}, "
              f"N_eff = {kf.effective_entries(weights[passed]):.0f}")
        if weights[passed].sum() <= 0:
            print(f"[WARNING] {r['label']}: no background weight above BDT {cut:g}, skipped in the plot")
            continue
        counts, err, _ = kf.normalized_hist(mass[passed], weights[passed], bins=edges)
        style = _variant_style(r)
        hep.histplot(counts, bins=edges, ax=ax, yerr=err, color=style["color"], ls=style["ls"], lw=2,
                     label=f"{r['label']} (eff {eff:.3g})")
        ok = inclusive > 0
        ratio = np.divide(counts, inclusive, out=np.full_like(counts, np.nan), where=ok)
        ratio_err = np.divide(err, inclusive, out=np.zeros_like(err), where=ok)
        hep.histplot(ratio, bins=edges, ax=ax_r, yerr=ratio_err, color=style["color"], ls=style["ls"], lw=2)
    ax_r.axhline(1, color="grey", lw=1)
    ax.set_xlim(edges[0], edges[-1])
    ax.set_ylim(bottom=0, top=ax.get_ylim()[1] * 1.3)
    ax.set_ylabel(f"Normalized events / {bin_width:g} GeV")
    ax.set_xlabel("")
    ax.legend(loc="upper right", fontsize=12, ncol=2, title=f"{channel_US} background, BDT > {cut:g}",
              title_fontsize=12)
    _cms_label(ax, era)
    ax_r.set_ylim(0.5, 1.5)
    ax_r.set_xlabel(r"$M_{\mu\mu}$ [GeV]")
    ax_r.set_ylabel("Tight / incl.")
    cut_tag = f"{cut:.2f}".replace(".", "p")
    _save(fig, f"{plot_path}comparison/tight_mass_variants_BDTgt{cut_tag}_{channel_US}_{era}")


def plot_asimov_trial(number, params, infos, era, path, pruned_after=None, fitted=False, infeasible=False):
    """One Optuna trial of --objective asimov: Asimov Z vs boosting round per CV validation fold
    with the fold average and the chosen checkpoint (top), and the per-category Z of every fold
    at that checkpoint (bottom; a fold that stopped earlier shows its last round). A pruned trial
    shows the folds done before it was stopped. fitted: the Z of --objective asimov_fit;
    infeasible: the trial failed the mass-sculpting constraint."""
    best_round, best_z, mean_curve = kf.mean_z_curve(infos, full=True)
    fig, (ax, ax_c) = plt.subplots(2, 1, figsize=(12, 13), gridspec_kw=dict(height_ratios=(3, 2)), layout="constrained")
    colors = _fold_colors(kf.N_FOLDS)
    for info in infos:
        rounds = sorted(info["z_curve"])
        ax.plot(rounds, [info["z_curve"][r] for r in rounds], marker="o", ms=3, lw=1.5,
                color=colors[info["fold"]], label=f"fold {info['fold']}")
    rounds = sorted(mean_curve)
    ax.plot(rounds, [mean_curve[r] for r in rounds], color="black", lw=3, label="fold average")
    ax.axvline(best_round, color="grey", ls="--", lw=1.5, label=f"chosen: round {best_round}")
    ax.set_xlabel("Boosting round", fontsize=20)
    ax.set_ylabel("Binned Asimov Z (validation fold" + (", fitted bkg)" if fitted else ")"), fontsize=20)
    state = (f"pruned after fold {pruned_after}" if pruned_after is not None
             else f"mean Z = {best_z:.4f} at round {best_round}")
    ax.set_title(f"trial {number}: {state}" + (" -- INFEASIBLE (mass sculpting)" if infeasible else ""),
                 fontsize=16, color="#e42536" if infeasible else "black")
    ax.legend(loc="lower right", fontsize=11, ncol=2)
    ax.text(0.02, 0.97, "\n".join(f"{k} = {v:.4g}" for k, v in params.items()), transform=ax.transAxes,
            va="top", fontsize=10, family="monospace",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8, edgecolor="grey"))

    def tightness(label):  # "0-2%" -> 0 ... "70-100%" -> 70; "cat<k>" fallbacks after them
        return float(label.split("-")[0]) if label.endswith("%") else 1000 - float(label[3:])

    per_fold = {}
    for info in infos:
        r = kf.fold_round(info, best_round)
        per_fold[info["fold"]] = dict(info["z_categories"][r]) if r is not None else {}
    labels = sorted({label for cats in per_fold.values() for label in cats}, key=tightness)
    width = 0.8 / max(len(per_fold), 1)
    for j, (fold, cats) in enumerate(sorted(per_fold.items())):
        ax_c.bar(np.arange(len(labels)) + (j - (len(per_fold) - 1) / 2) * width,
                 [cats.get(label, 0.0) for label in labels], width=width, color=colors[fold],
                 label=f"fold {fold}")
    ax_c.set_xticks(np.arange(len(labels)))
    ax_c.set_xticklabels(labels, fontsize=20)
    ax_c.set_xlabel("Category (top fraction of the signal)", fontsize=20)
    ax_c.set_ylabel(f"Z at round {best_round}", fontsize=20)
    ax_c.legend(fontsize=11, ncol=len(per_fold))
    _save(fig, f"{path}trial_{number:03d}")
    return best_round


def _trial_names(number):
    """(title, file stem) of a trial plot: an Optuna trial number, or a name such as "test"."""
    if isinstance(number, (int, np.integer)):
        return f"trial {number}", f"trial_{number:03d}"
    return str(number), str(number)


def _edge_labels(n_inner):
    """Label of each inner category edge (ascending score): the signal fraction above it."""
    fractions = kf.ASIMOV_SIGNAL_FRACTIONS[:-1][::-1]  # ascending score = decreasing fraction
    return [f"{100 * f:g}%" for f in fractions] if n_inner == len(fractions) else [""] * n_inner


def plot_asimov_trial_scores(number, infos, best_round, era, path, sample="validation folds, out-of-fold"):
    """BDT probability of the CV validation folds together (out-of-fold) at the trial's chosen
    round, signal and background each normalized to unit area, with the category edges (the mean
    over the folds, the band their min-max; each fold's categories are its own signal quantiles).
    The lower panel zooms on the tight categories (from the 20% edge up). number: the trial, or a
    name (e.g. "test" with a single-sample `infos`, xgb_kfold.single_sample_info); sample: wording."""
    title, stem = _trial_names(number)
    hists, fold_edges = {0: 0.0, 1: 0.0}, []
    for info in infos:
        r = kf.fold_round(info, best_round)
        if r is None:
            continue
        for cls in (0, 1):
            hists[cls] = hists[cls] + info["score_hists"][r][cls]
        fold_edges.append(np.asarray(info["cat_edges_prob"][r]))
    n_bins = kf.SCORE_HIST_BINS
    fine = np.linspace(0, 1, n_bins + 1)
    norm = {cls: hists[cls] / hists[cls].sum() if np.sum(hists[cls]) > 0 else np.zeros(n_bins) for cls in (0, 1)}
    n_inner = max(len(e) for e in fold_edges)
    full = np.array([e for e in fold_edges if len(e) == n_inner])
    mean_edges, lo_edges, hi_edges = full.mean(axis=0), full.min(axis=0), full.max(axis=0)
    labels = _edge_labels(n_inner)

    fig, (ax, ax_z) = plt.subplots(2, 1, figsize=(12, 13), gridspec_kw=dict(height_ratios=(1, 1)), layout="constrained")
    styles = {1: dict(color=CMS_COLORS[2], label="signal"), 0: dict(color=CMS_COLORS[0], label="background")}

    def draw(axis, x_lo, x_hi, max_bins, annotate):
        first, last = int(np.floor(x_lo * n_bins)), int(np.ceil(x_hi * n_bins))
        group = max(1, (last - first) // max_bins)
        last = min(n_bins, first + group * -(-(last - first) // group))  # whole groups
        first = last - group * ((last - first) // group)
        edges = fine[first:last + 1:group]
        for cls in (1, 0):
            h = norm[cls][first:last].reshape(-1, group).sum(axis=1)
            hep.histplot(h, edges, ax=axis, lw=2, **styles[cls])
        top = axis.get_ylim()[1]
        for j, (m, lo, hi) in enumerate(zip(mean_edges, lo_edges, hi_edges)):
            if not edges[0] <= m <= edges[-1]:
                continue
            axis.axvspan(lo, hi, color="grey", alpha=0.25, lw=0)
            axis.axvline(m, color="black", ls="--", lw=1.2)
            if annotate:
                axis.text(m, top * 0.98, labels[j], rotation=90, ha="right", va="top", fontsize=11)
        axis.set_xlim(edges[0], edges[-1])
        axis.set_ylabel(f"Fraction of events / {group / n_bins:.4g}")

    draw(ax, 0.0, 1.0, 50, annotate=False)
    ax.set_xlabel(f"BDT probability ({sample})", fontsize=20)
    ax.set_title(f"{title}: round {best_round}", fontsize=16)
    ax.legend(loc="upper center", fontsize=12, title_fontsize=11,
              title="dashed: category edges" + (" (fold mean, band: fold min-max)" if len(fold_edges) > 1 else ""))
    zoom_index = labels.index("20%") if "20%" in labels else max(n_inner - 4, 0)
    filled = np.flatnonzero((hists[0] != 0) | (hists[1] != 0))
    x_hi = fine[filled[-1] + 1] if len(filled) else 1.0  # up to the highest filled bin
    x_lo = max(0.0, lo_edges[zoom_index] - 0.1 * (x_hi - lo_edges[zoom_index]))
    draw(ax_z, x_lo, x_hi, 80, annotate=True)
    ax_z.set_xlabel("BDT probability (zoom on the tight categories; labels: signal fraction above)", fontsize=20)
    _save(fig, f"{path}{stem}_scores")


def plot_asimov_trial_sculpting(number, sculpt, best_round, era, path, rebin=5, sample="validation folds"):
    """Mass-sculpting check of one trial (xgb_kfold.combine_sculpt at its chosen round), one panel
    per fixed category, validation folds summed, normalized to the category's background MC:
    black = category background MC; grey = inclusive background (the prediction's reference shape);
    blue dashed = sideband prediction (per fold: inclusive shape x exp(-lambda m), lambda fitted on
    the category's 115-120 and 130-135 GeV MC, normalized to its sideband yield). Lower panel:
    MC / prediction with the window prediction uncertainty. The text gives the numbers behind the
    decision: window MC vs prediction (fold sums), the tilt, the per-fold pulls and their
    combination sum/sqrt(n), which the constraint compares with SCULPT_MAX_PULL in the tight
    categories (kf.sculpt_is_tight); the prediction, ratio and window numbers use only the folds
    with enough sideband MC for a pull;
    the KS p-value (category vs rest of the background) is information only. number: the trial, or
    a name (e.g. "test" for a single sample); sample: wording of the footnote."""
    from matplotlib.gridspec import GridSpec
    title, stem = _trial_names(number)
    edges = sculpt["hist_edges"]
    cats = sculpt["categories"]
    if edges is None or not cats:
        return
    n = (len(edges) - 1) // rebin * rebin
    coarse = edges[:n + 1:rebin]
    centres = (coarse[1:] + coarse[:-1]) / 2

    def tightness(label):  # "a-b%" -> (a, b): tight first; merged ranges after their narrower ones
        lo, hi = label.rstrip("%").split("-")
        return float(lo), float(hi)

    def rb(values):
        return np.asarray(values, dtype=float)[:n].reshape(-1, rebin).sum(axis=1)

    def steps(ax, values, **kwargs):  # step line over the full range, no drop to zero at the edges
        ax.step(coarse, np.append(values, values[-1]), where="post", **kwargs)

    red = "#e42536"
    labels = sorted(cats, key=tightness)
    handles = legend_labels = None
    n_rows = max(1, -(-len(labels) // 4))  # merged categories (tied scores) can give more than 8
    fig = plt.figure(figsize=(26, 7.5 * n_rows))
    grid = GridSpec(3 * n_rows - 1, 4, figure=fig, height_ratios=([3, 1, 0.5] * n_rows)[:-1], hspace=0.06,
                    wspace=0.22)
    for i, label in enumerate(labels):
        row, col = 3 * (i // 4), i % 4
        ax, ax_r = fig.add_subplot(grid[row, col]), fig.add_subplot(grid[row + 1, col])
        c = cats[label]
        h, h2, incl = rb(c["hist"]), rb(c["hist2"]), rb(c["incl"])
        total = h.sum()
        if total <= 0:
            ax.set_title(f"{label}: no background", fontsize=13)
            continue
        for a in (ax, ax_r):
            a.axvspan(*kf.SCULPT_WINDOW, color="grey", alpha=0.12, lw=0)
            a.set_xlim(coarse[0], coarse[-1])
        if incl.sum() > 0:
            steps(ax, incl / incl.sum(), color="grey", lw=1.8, label="inclusive background (reference shape)")
        pred = rb(c["pred"]) if c["pred"] is not None else None
        if pred is not None:
            h_fit, h2_fit = rb(c["hist_fit"]), rb(c["hist2_fit"])  # the folds with a prediction
            steps(ax, pred / h_fit.sum() if h_fit.sum() > 0 else pred * 0, color=CMS_COLORS[0], lw=2, ls="--",
                  label=r"sideband fit: inclusive $\times e^{-\lambda m}$ (115-120, 130-135)")
        err = np.sqrt(np.clip(h2, 0, None))
        ax.errorbar(centres, h / total, yerr=err / total, fmt="o", ms=3.5, color="black",
                    label="category background MC")
        pull = c["pull"]
        tight = kf.sculpt_is_tight(label)
        flagged = tight and pull is not None and pull > kf.SCULPT_MAX_PULL
        color = red if flagged else "black"
        if pred is not None:  # ratio panel
            ok = pred > 0
            ratio = np.divide(h_fit, pred, out=np.full_like(h_fit, np.nan), where=ok)
            err_fit = np.sqrt(np.clip(h2_fit, 0, None))
            ax_r.errorbar(centres[ok], ratio[ok], yerr=err_fit[ok] / pred[ok], fmt="o", ms=3, color="black")
            ax_r.axhline(1, color=CMS_COLORS[0], lw=1.5, ls="--")
            if c["B_pred_sum"]:
                rel = c["B_pred_err_sum"] / c["B_pred_sum"]
                ax_r.fill_between(kf.SCULPT_WINDOW, 1 - rel, 1 + rel, color=CMS_COLORS[0], alpha=0.25, lw=0)
            finite = ratio[ok & np.isfinite(ratio)]
            lo = min(0.8, np.nanmin(finite) - 0.05) if len(finite) else 0.8
            hi = max(1.2, np.nanmax(finite) + 0.05) if len(finite) else 1.2
            ax_r.set_ylim(max(lo, 0.0), min(hi, 3.0))
        ax_r.set_ylabel("MC / pred", fontsize=12)
        ax_r.set_xlabel(r"$M_{\mu\mu}$ [GeV]", fontsize=13)
        ax.tick_params(labelbottom=False, labelsize=11)
        ax_r.tick_params(labelsize=11)
        if pull is not None and c["n_folds_all"] == 1:  # a single sample: no fold combination
            text = (f"window MC {c['B_win_sum']:.4g} vs pred {c['B_pred_sum']:.4g} $\\pm$ {c['B_pred_err_sum']:.2g}"
                    f" ({100 * c['excess']:+.1f}%)\n"
                    f"tilt $\\lambda$ = {c['fold_lam'][0]:+.4f} /GeV\n"
                    f"pull = {pull:+.2f}")
        elif pull is not None:
            text = (f"window MC {c['B_win_sum']:.4g} vs pred {c['B_pred_sum']:.4g} $\\pm$ {c['B_pred_err_sum']:.2g}"
                    f" ({100 * c['excess']:+.1f}%)\n"
                    f"tilt $\\lambda$ = {np.mean(c['fold_lam']):+.4f} /GeV (fold mean)\n"
                    "fold pulls: " + " ".join(f"{p:+.1f}" for p in c["fold_pulls"])
                    + (f" ({c['n_folds']} of {c['n_folds_all']} folds)" if c["n_folds"] < c["n_folds_all"] else "")
                    + "\n"
                    f"combined pull $\\Sigma/\\sqrt{{n}}$ = {pull:+.2f}")
        else:
            text = "too few sideband MC events: no pull"
        if c["ks_p"] is not None:
            text += f"\nKS p (vs rest) = {c['ks_p']:.2g}"
        ax.text(0.97, 0.96, text, transform=ax.transAxes, ha="right", va="top", fontsize=10.5, color=color,
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor="grey"))
        ax.set_title(label + (" (constraint)" if tight else ""), fontsize=14, color=color)
        if flagged:
            for a in (ax, ax_r):
                for spine in a.spines.values():
                    spine.set_edgecolor(red)
                    spine.set_linewidth(3)
        ax.set_ylim(bottom=0, top=ax.get_ylim()[1] * 1.45)
        if col == 0:
            ax.set_ylabel(f"Fraction / {rebin * kf.SCULPT_HIST_BIN:g} GeV", fontsize=13)
        if handles is None:
            handles, legend_labels = ax.get_legend_handles_labels()
    single = all(c["n_folds_all"] == 1 for c in cats.values())
    state = "INFEASIBLE" if sculpt["constraint"] > 0 else "feasible"
    if single:  # e.g. the test sample: the constraint is only applied in the CV
        checked = any(kf.sculpt_is_tight(l) and c["pull"] is not None for l, c in cats.items())
        state = ("no tight-category pull (too few sideband MC events)" if not checked
                 else "fails the CV constraint (information)" if sculpt["constraint"] > 0 else "passes the CV constraint")
    if handles:
        from matplotlib.patches import Patch
        band = Patch(color=CMS_COLORS[0], alpha=0.25,
                     label=r"ratio panel: window prediction uncertainty $\pm\sigma_{pred}/B_{pred}$")
        fig.legend(list(handles) + [band], list(legend_labels) + [band.get_label()], loc="upper center",
                   bbox_to_anchor=(0.5, 0.965), ncol=2, fontsize=13, frameon=False)
    fig.suptitle(f"{title}, round {best_round}: mass sculpting {state}", fontsize=17, y=0.99,
                 color=red if sculpt["constraint"] > 0 else "black")
    fig.text(0.5, 0.055, f"{sample}{'' if single else ', per fold'}: pull = (MC - pred) / sqrt($\\Sigma w^2$ + $\\sigma_{{pred}}^2$) in "
             f"{kf.SCULPT_WINDOW[0]:g}-{kf.SCULPT_WINDOW[1]:g} GeV;  constraint: $\\Sigma$ pulls / $\\sqrt{{n}}$ > "
             f"{kf.SCULPT_MAX_PULL:g} in a category within the top {100 * kf.SCULPT_TIGHT_MAX_FRACTION:g}% of the signal -> infeasible."
             + ("" if single else "  Window numbers are fold sums (display)."), ha="center", fontsize=13)
    _save(fig, f"{path}{stem}_sculpting")


def plot_asimov_trial_bkg_fit(number, infos, best_round, era, path, sample="validation-fold MC"):
    """--objective asimov_fit: the tightest category's background MC of every validation fold at the
    trial's chosen round, with the exponential fit that enters the Asimov Z (band: its fit
    uncertainty) and the pulls. Unscaled validation-fold MC. number: the trial, or a name (e.g.
    "test" with a single-sample `infos`: one panel); sample: wording."""
    from matplotlib.gridspec import GridSpec
    title, stem = _trial_names(number)
    colors = _fold_colors(kf.N_FOLDS)
    if len(infos) == 1:  # one sample: fit and pull panels with the description beside them
        fig = plt.figure(figsize=(17, 9))
        grid = GridSpec(2, 2, figure=fig, height_ratios=(3, 1), width_ratios=(2, 1), hspace=0.08, wspace=0.1)
        slots, text_slot = [(0, 0)], grid[:, 1]
    else:
        fig = plt.figure(figsize=(21, 13))
        grid = GridSpec(5, 3, figure=fig, height_ratios=(3, 1, 0.55, 3, 1), hspace=0.08, wspace=0.25)
        slots, text_slot = [(0, 0), (0, 1), (0, 2), (3, 0), (3, 1)], grid[3:, 2]
    for info, (row, col) in zip(sorted(infos, key=lambda i: i["fold"]), slots):
        r = kf.fold_round(info, best_round)
        if r is None or r not in info.get("tight_fit", {}):
            continue
        fit = info["tight_fit"][r]
        ax, ax_p = fig.add_subplot(grid[row, col]), fig.add_subplot(grid[row + 1, col])
        hist = fit["tight_hist"]
        edges, sumw, err = hist["edges"], hist["sumw"], np.sqrt(hist["sumw2"])
        centres = (edges[1:] + edges[:-1]) / 2
        color = colors[info["fold"]]
        ax.errorbar(centres, sumw, yerr=err, fmt="o", ms=4, color="black", label="background MC")
        if "lam" in fit:
            b, sigma = kf.fitted_background(fit["lam"], fit["B_raw"], np.asarray(fit["cov"]), edges)
            ax.stairs(b, edges, color=color, lw=2.5, label="exponential fit")
            ax.stairs(b + sigma, edges, baseline=b - sigma, fill=True, color=color, alpha=0.3, label="fit unc.")
            # MC variance expected from the fit (b times the mean weight sum(w^2)/sum(w)), so that
            # empty bins of sparse weighted MC get a sensible pull
            mean_w = hist["sumw2"].sum() / sumw.sum() if sumw.sum() > 0 else 0.0
            total = np.sqrt(np.clip(b, 0, None) * mean_w + sigma ** 2)
            pulls = np.divide(sumw - b, total, out=np.zeros_like(b), where=total > 0)
            ax_p.bar(centres, pulls, width=np.diff(edges), color=color, alpha=0.7)
            text = (f"{fit['label']}: $\\lambda$ = {fit['lam']:.4f} $\\pm$ {fit['lam_err']:.4f} /GeV\n"
                    f"MC events {fit['n_events']}, $N_{{eff}}$ = {fit['n_eff']:.1f}\n"
                    f"B (unscaled) = {fit['B_raw']:.3g}, Z = {fit['Z']:.3f}")
        else:
            text = f"{fit['label']}: no fit"
        ax.text(0.97, 0.96, text, transform=ax.transAxes, ha="right", va="top", fontsize=11,
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor="grey"))
        ax.set_title(f"fold {info['fold']}" if len(infos) > 1 else sample, fontsize=14)
        ax.set_ylim(bottom=min(0, ax.get_ylim()[0]), top=ax.get_ylim()[1] * 1.35)
        ax.set_ylabel(f"Events / {kf.ASIMOV_FIT_PLOT_BIN:g} GeV", fontsize=13)
        ax.tick_params(labelbottom=False, labelsize=11)
        ax_p.axhline(0, color="grey", lw=1)
        ax_p.set_ylim(-3.5, 3.5)
        ax_p.set_ylabel("Pull", fontsize=13)
        ax_p.set_xlabel(r"$M_{\mu\mu}$ [GeV]", fontsize=13)
        ax_p.tick_params(labelsize=11)
        for a in (ax, ax_p):
            a.set_xlim(edges[0], edges[-1])
        if (row, col) == (0, 0):
            ax.legend(loc="upper left", fontsize=11)
    ax_t = fig.add_subplot(text_slot)
    ax_t.axis("off")
    ax_t.text(0.0, 0.9, f"{title}, round {best_round}\n\ntightest category after merging,\n"
              f"{sample} (unscaled)\n\nfit: exp(-$\\lambda$ m), unbinned weighted ML\n"
              f"on {kf.TRAIN_REGION[0]:g}-{kf.TRAIN_REGION[1]:g} GeV\n\npull = (MC - fit) / "
              "$\\sqrt{\\sigma_{MC}^2 + \\sigma_{fit}^2}$,\n"
              "$\\sigma_{MC}^2$ = fit $\\times$ $\\Sigma w^2 / \\Sigma w$", va="top", fontsize=15, transform=ax_t.transAxes)
    _save(fig, f"{path}{stem}_bkgfit")


def plot_test_vs_cv_z(test_asimov, cv, n_rounds, era, path):
    """--stage test: binned Asimov Z per category and in total of the refit on the untouched test
    sample (bars: the optimized metric filled, the other one hatched) next to the cross-validation
    folds of the chosen configuration at its round (points: fold mean, bars: fold std). Both are
    scaled to the full MC. The per-category CV values exist only for studies that recorded them
    (cv["fold_z_categories"]); the CV total is the selected maximum over trials and checkpoints,
    so it tends to lie above the test value."""
    def tightness(label):  # "a-b%" -> (a, b); "cat<k>" fallbacks after them
        try:
            lo, hi = label.rstrip("%").split("-")
            return 0, float(lo), float(hi)
        except ValueError:
            return 1, 0.0, 0.0

    optimized = "fit" if test_asimov["objective"] == "asimov_fit" else "raw"
    test = {key: {c["label"]: c["Z"] for c in test_asimov[f"categories_{key}"]} for key in ("raw", "fit")}
    cv_cats = cv.get("fold_z_categories") if cv else None
    labels = {label for values in test.values() for label in values}
    if cv_cats:
        labels |= {label for fold in cv_cats for label in fold}
    labels = sorted(labels, key=tightness) + ["total"]
    for key in ("raw", "fit"):
        test[key]["total"] = test_asimov[f"z_{key}"]
    cv_points = {}
    if cv_cats:
        for label in labels[:-1]:
            values = [fold[label] for fold in cv_cats if label in fold]
            if values:
                cv_points[label] = (np.mean(values), np.std(values), len(values))
    if cv and cv.get("fold_z_curves"):
        totals = []
        for curve in cv["fold_z_curves"]:
            done = [int(r) for r in curve if int(r) <= n_rounds]
            totals.append(curve[str(max(done))] if done else 0.0)
        cv_points["total"] = (np.mean(totals), np.std(totals), len(totals))

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(14, 8))
    for key, offset in (("raw", -0.2), ("fit", 0.2)):
        is_opt = key == optimized
        ax.bar(x + offset, [test[key].get(label, np.nan) for label in labels], width=0.38,
               color=CMS_COLORS[0] if key == "raw" else CMS_COLORS[1], alpha=0.85 if is_opt else 0.35,
               hatch=None if is_opt else "//", edgecolor="black", lw=0.8,
               label=f"test, {'raw' if key == 'raw' else 'fitted'} background" + (" (optimized)" if is_opt else ""))
    if cv_points:
        pts = [(j, *cv_points[label]) for j, label in enumerate(labels) if label in cv_points]
        offset = 0.2 if optimized == "fit" else -0.2
        ax.errorbar([j + offset for j, *_ in pts], [m for _, m, _, _ in pts], yerr=[s for _, _, s, _ in pts],
                    fmt="o", ms=8, color="black", capsize=4, lw=2,
                    label=f"cross-validation ({optimized}): fold mean $\\pm$ std")
    ax.axvline(len(labels) - 1.5, color="grey", lw=1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=14)
    ax.set_xlabel("Category (top fraction of the signal)", fontsize=16)
    ax.set_ylabel("Binned Asimov Z (scaled to the full MC)", fontsize=16)
    ax.set_ylim(0, ax.get_ylim()[1] * 1.25)
    notes = [f"test refit, {n_rounds} rounds"]
    if "total" in cv_points and cv_points["total"][0] > 0:
        ratio = test[optimized]["total"] / cv_points["total"][0]
        notes.append(f"total test / CV ({optimized}) = {ratio:.3f}")
    if not cv_cats:
        notes.append("per-category CV values not stored by this study")
    ax.text(0.02, 0.97, "\n".join(notes), transform=ax.transAxes, va="top", fontsize=13,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor="grey"))
    ax.legend(loc="upper right", fontsize=12)
    _cms_label(ax, era)
    _save(fig, f"{path}test_z_categories")


def plot_feature_importance_kfold(models, variables, tag, plot_path):
    """'weight' and 'gain' importance, mean +/- std over the fold models."""
    labels = [row[2] for row in variables[:-3]]
    for importance_type in ("weight", "gain"):
        mat = np.zeros((len(models), len(labels)))
        for k, model in enumerate(models):
            for name, val in model.get_booster().get_score(importance_type=importance_type).items():
                mat[k, int(name.lstrip("f"))] = val
        mean, std = mat.mean(axis=0), mat.std(axis=0)
        order = np.argsort(mean)
        fig, ax = plt.subplots(figsize=(10, 12))
        ax.barh(np.arange(len(labels)), mean[order], xerr=std[order], color="tab:blue", alpha=0.8)
        ax.set_yticks(np.arange(len(labels)))
        ax.set_yticklabels([labels[i] for i in order])
        ax.set_xlabel(f"{importance_type} (mean $\\pm$ std over {len(models)} fold models)")
        _save(fig, f"{plot_path}training/myImportances_{importance_type}_kfold_{tag}")


def plot_xgb_tree(model, variables, test_name, plot_path):
    """Draw the first tree. Renames the booster's features, so call it last."""
    model.get_booster().feature_names = [row[1] for row in variables[:-3]]
    xgb.plot_tree(model)
    fig = plt.gcf()
    fig.set_size_inches(150, 100)
    _save(fig, f"{plot_path}training/myTree_{test_name}")


def plot_fold_loss_curves(members, plot_path, tag, era, second_label="held-out fold"):
    """Train (dashed) and held-out (solid) log loss per boosting round, one colour per model."""
    fig, ax = plt.subplots()
    colors = _fold_colors(len(members))
    for color, member in zip(colors, members):
        ax.plot(member["train_logloss"], ls="--", color=color)
        ax.plot(member["val_logloss"], ls="-", color=color)
    handles = [Line2D([], [], color=c, lw=1.8, label=f"model {k}") for k, c in enumerate(colors)]
    handles += [Line2D([], [], color="black", lw=1.8, ls="-", label=second_label),
                Line2D([], [], color="black", lw=1.8, ls="--", label="Train")]
    ax.legend(handles=handles, fontsize=12, loc="upper left", bbox_to_anchor=(1.02, 1), frameon=False)
    ax.set_xlabel("Boosting round")
    ax.set_ylabel("Log loss")
    _cms_label(ax, era)
    _save(fig, f"{plot_path}training/loss_folds_{tag}")


def plot_roc_per_fold(y, scores, folds, weights, era, plot_path, tag):
    """One ROC per fold model on its own held-out fold."""
    from sklearn.metrics import roc_auc_score, roc_curve
    n_folds = int(folds.max()) + 1
    fig, ax = plt.subplots()
    aucs = []
    for k, color in enumerate(_fold_colors(n_folds)):
        m = folds == k
        if len(np.unique(y[m])) < 2:
            continue
        fpr, tpr, _ = roc_curve(y[m], scores[m], sample_weight=weights[m])
        aucs.append(roc_auc_score(y[m], scores[m], sample_weight=weights[m]))
        ax.plot(fpr, tpr, lw=2, color=color, label=f"model {k} (AUC = {aucs[-1]:.4f})")
    ax.plot([0, 1], [0, 1], color="grey", lw=1, ls="--")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Background efficiency")
    ax.set_ylabel("Signal efficiency")
    ax.legend(loc="lower right", fontsize=12, title_fontsize=12,
              title=f"mean AUC {np.mean(aucs):.4f} $\\pm$ {np.std(aucs):.4f}" if aucs else None)
    _cms_label(ax, era)
    _save(fig, f"{plot_path}training/roc_per_fold_{tag}")


def plot_discriminator_per_fold(y, scores, folds, weights, era, plot_path, tag):
    """OOF signal/background BDT shapes per fold model: the models must agree on the score
    scale before their outputs are merged into one distribution."""
    colors = _fold_colors(int(folds.max()) + 1)
    edges = np.linspace(0, 1, 51)
    fig, ax = plt.subplots()
    for k, color in enumerate(colors):
        for cls, style in ((1, "-"), (0, "--")):
            m = (folds == k) & (y == cls)
            if m.any():
                h, _, _ = kf.normalized_hist(scores[m], weights[m], bins=edges, density=True)
                hep.histplot(h, edges, ax=ax, color=color, ls=style, lw=1.8)
    handles = [Line2D([], [], color=c, lw=1.8, label=f"model {k}") for k, c in enumerate(colors)]
    handles += [Line2D([], [], color="black", lw=1.8, ls="-", label="signal"),
                Line2D([], [], color="black", lw=1.8, ls="--", label="background")]
    ax.legend(handles=handles, fontsize=12, loc="upper left", bbox_to_anchor=(1.02, 1), frameon=False)
    ax.set_xlim(0, 1)
    ax.set_xlabel("BDT response (out-of-fold)")
    ax.set_ylabel("Normalized events")
    _cms_label(ax, era)
    _save(fig, f"{plot_path}training/discriminator_per_fold_{tag}")


def plot_fold_balance(y, w, folds, plot_path, tag, era, n_folds, rel_tolerance=0.05):
    """Events per fold (left) and each fold's unweighted/weighted share of the sample
    against the ideal 1/n_folds (right)."""
    k = np.arange(n_folds)
    counts = {cls: np.array([((y == cls) & (folds == i)).sum() for i in k]) for cls in (0, 1)}
    yields = {cls: np.array([w[(y == cls) & (folds == i)].sum() for i in k]) for cls in (0, 1)}

    fig, (ax_n, ax_f) = plt.subplots(1, 2, figsize=(18, 7))
    for offset, cls, color, name in ((-0.19, 1, "#5790FC", "signal"), (0.19, 0, "#E42536", "background")):
        n = counts[cls]
        ax_n.bar(k + offset, n, 0.38, color=color,
                 label=f"{name} ({n.sum():,}), spread {100 * (n.max() - n.min()) / n.mean():.2f}%")
    ax_n.set_xticks(k)
    ax_n.set_xlabel(f"Fold  (event % {n_folds})")
    ax_n.set_ylabel("Training events")
    ax_n.set_ylim(0, 1.28 * max(counts[0].max(), counts[1].max()))
    ax_n.legend(fontsize=14, loc="upper right")

    ideal = 1.0 / n_folds
    ax_f.axhline(ideal, color="#9C9CA1", ls="--", lw=1.5)
    ax_f.axhspan(ideal * (1 - rel_tolerance), ideal * (1 + rel_tolerance), color="#9C9CA1", alpha=0.1)
    shares = [(counts[1], "#5790FC", "o", "signal, unweighted"),
              (counts[0], "#E42536", "o", "background, unweighted"),
              (yields[1], "#F89C20", "s", "signal, weighted"),
              (yields[0], "#964A8B", "s", "background, weighted")]
    all_shares = []
    for values, color, marker, label in shares:
        share = values / values.sum()
        all_shares.append(share)
        ax_f.plot(k, share, marker=marker, lw=2, color=color,
                  label=f"{label} (worst {100 * np.abs(share - ideal).max() / ideal:.2f}%)")
    # zoom on the data: the tolerance band is usually much wider than the spread
    all_shares = np.concatenate(all_shares)
    pad = max(0.45 * (all_shares.max() - all_shares.min()), 0.002 * ideal)
    ax_f.set_ylim(all_shares.min() - pad, all_shares.max() + pad)
    ax_f.set_xticks(k)
    ax_f.set_xlabel(f"Fold  (event % {n_folds})")
    ax_f.set_ylabel(f"Share of the sample  (ideal 1/{n_folds})")
    ax_f.legend(fontsize=13, loc="best")
    for ax in (ax_n, ax_f):
        _cms_label(ax, era)
    print(f"[INFO] events per fold: signal {counts[1].tolist()}, background {counts[0].tolist()}")
    _save(fig, f"{plot_path}kFold/fold_balance_{tag}")


# ---------------------------------------------------------------------------
# Input plots
# ---------------------------------------------------------------------------
# plotted with a log y axis (same list as plot_macros/utils/sig_vs_bg.py)
LOG_Y_VARIABLES = frozenset({
    "leading_jet_pt", "subleading_jet_pt", "n_jet", "delta_eta_diJet", "z_zeppenfeld",
    "min_delta_phi_diMuon_jet", "min_delta_eta_diMuon_jet",
})


def _variable_labels():
    """(x_labels, n_bins, x_range) from plot_macros/utils/labels.py, or empty dicts."""
    try:
        return labels.x_labels, labels.n_bins, labels.x_range
    except ImportError as e:
        print(f"[WARNING] plot_macros/utils/labels.py not importable ({e}); using auto-ranges")
        return {}, {}, {}


def plot_input_comparison(x, y, weights, variables, channel_US, era, plot_path):
    """Signal vs background shape of every BDT input, from the exact arrays the training
    uses (masked jet variables, training mass window, training weights)."""
    x_labels, n_bins, x_range = _variable_labels()
    for i, var in enumerate(variables):
        name = var[0]
        sig = (y == 1) & np.isfinite(x[:, i])
        bkg = (y == 0) & np.isfinite(x[:, i])
        if weights[sig].sum() <= 0 or weights[bkg].sum() <= 0:
            print(f"[WARNING] {name}: no finite entries, skipped")
            continue
        key = f"{name}_{channel_US}" if f"{name}_{channel_US}" in x_range else name
        span = x_range.get(key)
        if span is None:
            lo, hi = np.percentile(x[sig | bkg, i], [0.5, 99.5])
            span = (float(lo), float(hi)) if hi > lo else (float(lo) - 1, float(lo) + 1)
        sig_hist, sig_err, edges = kf.normalized_hist(x[sig, i], weights[sig], n_bins.get(key, 50), span)
        bkg_hist, bkg_err, _ = kf.normalized_hist(x[bkg, i], weights[bkg], n_bins.get(key, 50), span)
        if sig_hist.sum() <= 0 or bkg_hist.sum() <= 0:
            print(f"[WARNING] {name}: empty histogram in range {span}, skipped")
            continue

        fig, ax = plt.subplots()
        for hist, err, color, label in ((sig_hist, sig_err, "blue", "signal"),
                                        (bkg_hist, bkg_err, "red", "background")):
            hep.histplot(hist, edges, yerr=False, histtype="fill", label=label, ax=ax, color=color, alpha=0.4)
            hep.histplot(hist, edges, yerr=err, ax=ax, color=color, linewidth=2)
        ax.set_xlabel(x_labels.get(name, var[2]))
        ax.set_ylabel("Events / Total events")
        ax.set_xlim(edges[0], edges[-1])
        if name in LOG_Y_VARIABLES:
            ax.set_yscale("log")
            ax.set_ylim(1e-3, 1.1)
        else:
            ax.set_ylim(0.0, 1.3 * max(sig_hist.max(), bkg_hist.max()))
        ax.legend(frameon=False, loc="upper right")
        _cms_label(ax, era)
        _save(fig, f"{plot_path}variables/{name}_{era}_sig_vs_bkg")
    print(f"[INFO] signal-vs-background input plots written to {plot_path}variables/")


def plot_standardization_check(x_train, x_eval, names, mean_map, std_map, plot_path, era,
                               eval_label="held-out fold", tag=""):
    """Per input, train vs held-out shapes before and after one model's standardization.
    Variables in NO_STANDARDIZE_VARIABLES should look identical before and after."""
    x_train_std = kf.preprocess_features(x_train, names, True, mean_map, std_map)
    x_eval_std = kf.preprocess_features(x_eval, names, True, mean_map, std_map)
    for i, name in enumerate(names):
        for stage, tr, ev in (("prestd", x_train[:, i], x_eval[:, i]),
                              ("poststd", x_train_std[:, i], x_eval_std[:, i])):
            tr = tr[np.isfinite(tr)].astype(np.float64)
            ev = ev[np.isfinite(ev)].astype(np.float64)
            if len(tr) == 0 or len(ev) == 0:
                continue
            lo, hi = np.percentile(np.concatenate([tr, ev]), [0.1, 99.9])
            if not hi > lo:
                lo, hi = lo - 0.5, lo + 0.5
            h_tr, edges = np.histogram(tr, bins=50, range=(lo, hi), density=True)
            h_ev, _ = np.histogram(ev, bins=50, range=(lo, hi), density=True)

            fig, ax = plt.subplots()
            hep.histplot(h_tr, edges, ax=ax, label="train", linewidth=2)
            hep.histplot(h_ev, edges, ax=ax, label=eval_label, linewidth=2, linestyle="--")
            ax.set_xlabel(name)
            ax.set_ylabel("Normalized events")
            ax.set_title("Pre standardization" if stage == "prestd" else "Post standardization", fontsize=15)
            ax.legend(frameon=False)
            if stage == "poststd":
                identity = (mean_map[name], std_map[name]) == (0.0, 1.0)
                ax.text(0.02, 0.95, f"mean {mean_map[name]:.3g}, std {std_map[name]:.3g}"
                        + ("  (not standardized)" if identity else ""),
                        transform=ax.transAxes, fontsize=12, va="top")
            _save(fig, f"{plot_path}standardization/{name}_{stage}{'_' + tag if tag else ''}")
    print(f"[INFO] pre/post-standardization plots written to {plot_path}standardization/")


def draw_correlation_matrix(signal_file_name, bkg_file_name, correlation_vars, plot_path, test_name):
    """Linear correlation matrix of `correlation_vars` for signal and for background (slow)."""
    n = len(correlation_vars)
    labels = [var[2] for var in correlation_vars]
    stops = np.array([0.00, 0.34, 0.61, 0.84, 1.00])
    root.TColor.CreateGradientColorTable(len(stops), stops, np.array([0.50, 0.50, 1.00, 1.00, 1.00]),
                                         np.array([0.50, 1.00, 1.00, 0.60, 0.50]),
                                         np.array([1.00, 1.00, 0.50, 0.40, 0.50]), 255)
    root.gStyle.SetNumberContours(255)
    canvas = root.TCanvas("correlation", "correlation", 200, 10, 900, 800)
    for margin in (canvas.SetLeftMargin, canvas.SetRightMargin, canvas.SetBottomMargin, canvas.SetTopMargin):
        margin(0.12)
    for kind, file_name in (("sig", signal_file_name), ("bkg", bkg_file_name)):
        tfile = root.TFile(file_name)
        tree = tfile.Get("tree_output")
        matrix = root.TH2F(f"h2_corr_{kind}", "", n, 0, n, n, 0, n)
        for i in range(n):
            matrix.GetXaxis().SetBinLabel(i + 1, labels[i])
            matrix.GetYaxis().SetBinLabel(i + 1, labels[i])
            for j in range(n):
                tree.Draw(f"{correlation_vars[i][0]}:{correlation_vars[j][0]}>>temp", "", "goff")
                hist = root.gROOT.FindObject("temp")
                matrix.SetBinContent(i + 1, j + 1, hist.GetCorrelationFactor())
                hist.Delete()
        matrix.GetZaxis().SetRangeUser(-1.0, 1.0)
        matrix.LabelsOption("v", "X")
        matrix.Draw("COLZTEXT")
        canvas.SaveAs(f"{plot_path}variables/{test_name}_correlation_matrix_{kind}.png")
        tfile.Close()


# ---------------------------------------------------------------------------
# Legacy (single 60/40 split) vs K-fold comparison plots
# ---------------------------------------------------------------------------
# colours shared by the comparison plots: K-fold light blue/red, no k-fold orange/purple
KFOLD_SIG, KFOLD_BKG, LEGACY_SIG, LEGACY_BKG = "#5790FC", "#E42536", "#F89C20", "#964A8B"


def plot_legacy_vs_kfold(y, weights, p_legacy, p_kfold, auc_legacy, auc_kfold, era, plot_path):
    """ROC and discriminator of both approaches on the same (held-out 40%) events."""
    from sklearn.metrics import roc_curve
    out_dir = f"{plot_path}comparison/"

    fig, ax = plt.subplots()
    for p, auc, color, label in ((p_legacy, auc_legacy, "tab:red", "no k-fold (single 60/40 split)"),
                                 (p_kfold, auc_kfold, "tab:blue", "K-fold OOF")):
        fpr, tpr, _ = roc_curve(y, p, sample_weight=weights)
        ax.plot(fpr, tpr, lw=2, color=color, label=f"{label} (AUC = {auc:.4f})")
    ax.plot([0, 1], [0, 1], color="grey", lw=1, ls="--")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Background efficiency")
    ax.set_ylabel("Signal efficiency")
    ax.legend(loc="lower right", fontsize=13)
    _cms_label(ax, era)
    _save(fig, f"{out_dir}roc_noKfold_vs_kfold")

    fig, ax = plt.subplots()
    edges = np.linspace(0, 1, 51)
    for p, cls, color, label in ((p_kfold, 1, KFOLD_SIG, "K-fold OOF signal"),
                                 (p_legacy, 1, LEGACY_SIG, "no k-fold signal"),
                                 (p_kfold, 0, KFOLD_BKG, "K-fold OOF background"),
                                 (p_legacy, 0, LEGACY_BKG, "no k-fold background")):
        h, _, _ = kf.normalized_hist(p[y == cls], weights[y == cls], bins=edges, density=True)
        hep.histplot(h, edges, ax=ax, yerr=False, color=color, lw=2, label=label)
    ax.set_xlabel("BDT response")
    ax.set_ylabel("Normalized events")
    ax.legend(fontsize=12, ncol=2)
    _cms_label(ax, era)
    _save(fig, f"{out_dir}discriminator_noKfold_vs_kfold")


def plot_loss_noKfold_vs_kfold(rounds, legacy_train, legacy_heldout, kfold_in_fold, kfold_oof,
                               era, plot_path):
    """Weighted log loss vs tree count. Solid = out-of-sample on the held-out 40%, dashed =
    in-sample on a shared subsample of the train 60%. The K-fold curves are the mean over the
    models with a +/- 1 std band (model-to-model spread, not a statistical error)."""
    fig, ax = plt.subplots()
    for curves, color, ls, label in ((kfold_oof, KFOLD_SIG, "-", "K-fold, out-of-fold"),
                                     (kfold_in_fold, KFOLD_BKG, "--", "K-fold, in-fold")):
        mean, std = curves.mean(axis=0), curves.std(axis=0)
        ax.fill_between(rounds, mean - std, mean + std, color=color, alpha=0.20, lw=0)
        ax.plot(rounds, mean, color=color, lw=2, ls=ls,
                label=f"{label} (mean $\\pm$ std, {len(curves)} models)")
    ax.plot(rounds, legacy_heldout, color=LEGACY_SIG, lw=2, ls="-", label="no k-fold, test 40%")
    ax.plot(rounds, legacy_train, color=LEGACY_BKG, lw=2, ls="--", label="no k-fold, train 60%")
    ax.set_xlim(1, int(rounds[-1]))
    ax.set_xlabel("Boosting round")
    ax.set_ylabel("Weighted log loss")
    ax.legend(fontsize=11, loc="upper right")
    _cms_label(ax, era)
    _save(fig, f"{plot_path}comparison/loss_noKfold_vs_kfold")
