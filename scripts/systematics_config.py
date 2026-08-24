BDT_CUTS = {
    "ggH": [0.0, 0.45, 0.62, 0.8, 0.91, 1.0],
    "VBF": [
        0.0,
        0.6400000000000002,
        0.7800000000000011,
        0.8600000000000017,
        0.920000000000002,
        0.9533333333333356,
        0.966666666666669,
        1.0,
    ],
}

MASS_MIN = 122.5
MASS_MAX = 127.5

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
