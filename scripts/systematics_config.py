from pathlib import Path
from sys import path as sys_path

sys_path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bdt_categories_io import load_bdt_categories, get_bdt_cuts


MASS_MIN = 110.0
MASS_MAX = 150.0

FLASHGG_PATH = "/uscms_data/d3/mbarrial/fits_Hmumu/CMSSW_14_1_0_pre4/src/flashggFinalFit/"

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

bdt_categories_info = load_bdt_categories()

BDT_CUTS = {
    channel: get_bdt_cuts(
        bdt_categories_info,
        channel,
        "Combined",
        SUBSET,
        "diMuon_bsConstrainedMass",
    )
    for channel in CHANNELS
}
