from pathlib import Path
from sys import path as sys_path

sys_path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bdt_categories_io import load_bdt_categories, get_bdt_cuts, variant_dir_suffix


MASS_MIN = 110.0
MASS_MAX = 150.0

# ---- Hardcoded locations: edit these ----
# train.py variant label of the BDT (e.g. "base", "asimovFit_flatMassRes"). It selects the
# <channel><suffix> entry of root_io/bdt_categories.json and the nominal BDT_score/<channel><suffix>/
# folder, so it must match the model the systematic tuples were scored with.
BDT_VARIANT = "base"
# flashggFinalFit checkout; the JSONs go to <FLASHGG_PATH>Datacard/experimental_systematics/
FLASHGG_PATH = "/uscms_data/d3/esledge/fits-hmm/CMSSW_14_1_0_pre4/src/flashggFinalFit/"
# Nominal BDT-scored tuples: <dir>/<channel>/<SUBSET>/<process>_Combined_<SUBSET>.root
NOMINAL_BDT_SCORE_DIR = Path("./root_io/tuples/BDT_score")
# Systematic BDT-scored tuples (python/xgboost/submit_bdt_systematics.sh output);
# {user} = $USER, {analyzer_version} = 2.4, {version} = 2.4.2
SYSTEMATICS_BDT_SCORE_DIR = (
    "/eos/uscms/store/user/lpchmumu/{user}/analyzer_HiggsMuMu_v{analyzer_version}/"
    "tuples_v{version}/systematics/BDT_score"
)

CHANNELS = ("ggH", "VBF")

# ROOT sample prefix -> process name used in the datacard
PROCESSES = {
    "ggH": "ggH_combined_hgg",
    "VBF": "qqH_combined_hgg",
}

# Datacard category ordering: VBF categories first, then ggH categories.
DATACARD_CATEGORY_ORDER = ("VBF", "ggH")

SUBSET = "BFull_SNottH"
TREE_NAME = "tree_output"

# BDT_score/ folder and bdt_categories.json key of each channel, e.g. ggHasimovFitflatMassRes
VARIANT_CHANNEL = {
    channel: channel + variant_dir_suffix(BDT_VARIANT) for channel in CHANNELS
}

bdt_categories_info = load_bdt_categories()

BDT_CUTS = {
    channel: get_bdt_cuts(
        bdt_categories_info,
        VARIANT_CHANNEL[channel],
        "Combined",
        SUBSET,
        "diMuon_bsConstrainedMass",
    )
    for channel in CHANNELS
}
