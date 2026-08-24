from utils.sim_vs_data import draw_data_and_simul_and_ratio
import sys

production_channel = ""
bdt_subset = ""
use_categories = False
version = "2.0.0"

if len(sys.argv) >= 2:
    production_channel = sys.argv[1]

    if production_channel not in ["ggH", "VBF"]:
        print("ERROR: channel must be ggH or VBF")
        sys.exit(1)

    print("You selected " + production_channel + " channel")

    if "--categories" in sys.argv:
        use_categories = True
        bdt_subset = "BFull_SNottH"
        print("Using BDT categories")
    else:
        print("Using inclusive " + production_channel + " category")

else:
    print("Production channel was not selected. Using all the events")


# ordered from bottom to top in the plot, so order it from lower to bigger cross section
background_sources = [
    "EWK",
    "DiBoson",
    "TT",
    "DY",
]

signal_sources = [
    "ggH",
    "VBF",
    #"ttH",
]
bdt_selections = {
    "ggH": {
        "BFull_SNottH": [0.0, 0.4400000000000002, 0.6100000000000003, 0.8100000000000005, 0.9200000000000006, 1.0],
    },
    "VBF": {
        "BFull_SNottH":[0.0, 0.646666666666667, 0.8800000000000018, 0.9466666666666689, 0.9733333333333357, 1.0],
    },
    "": {"":""},
}

bdt_selections = {
    "ggH": {
        "BFull_SNottH": [0.0, 0.45, 0.62, 0.8, 0.91, 1.0],
    },
    "VBF": {
        "BFull_SNottH":[
                0.0,
                0.6400000000000002,
                0.7800000000000011,
                0.8600000000000017,
                0.920000000000002,
                0.9533333333333356,
                0.966666666666669,
                1.0,
            ],
    },
    "": {"":""},
}

if use_categories:
    bdt_cuts = bdt_selections[production_channel][bdt_subset]
else:
    bdt_cuts = []

variables = [
    ## DiMuon variables
    #"diMuon_mass",
    # "diMuon_mass_full_range",
     "diMuon_bsConstrainedMass",
    # "diMuon_mass_Z",
    # "diMuon_bsConstrainedMass_Z",
    "diMuon_rapidity",
    "diMuon_eta",
    #"diMuon_pt",
    "diMuon_bsConstrainedPt",
    "diMuon_phi",
    #"relative_diMuon_mass_error",
    "relative_diMuon_bsConstrainedMass_error",
    ## Muon variables
    #"mu1_pt_mass_ratio",
    #"mu2_pt_mass_ratio",
    "mu1_bsConstrainedPt_mass_ratio",
    "mu2_bsConstrainedPt_mass_ratio",
    "mu1_eta",
    "mu2_eta",
    "phi_CS",
    "cos_theta_CS",
    #"mu1_pt",
    #"mu2_pt",
    #"mu1_ptErr",
    #"mu2_ptErr",
    "mu1_bsConstrainedPt",
    "mu2_bsConstrainedPt",
    "mu1_bsConstrainedPtErr",
    "mu2_bsConstrainedPtErr",
    ## Jet variables
    "n_jet",
    "leading_jet_pt",
    "subleading_jet_pt",
    "leading_jet_eta",
    ## diJet variables
    "diJet_mass",
    "delta_eta_diJet",
    "delta_phi_diJet",
    "z_zeppenfeld",
    "min_delta_eta_diMuon_jet",
    "min_delta_phi_diMuon_jet",
    ## VBF required
    "pt_balance",
    "pt_centrality",
    "n_SoftJet_pt2",
    #"n_SoftJet_pt5",
    #"n_SoftJet_pt10",
    "HT",
    #"HT_pt2",
    #"HT_pt5",
    #"HT_pt10",
]

# variables = ["leading_jet_eta", "subleading_jet_eta", "diMuon_bsConstrainedMass"]
variables = ["diMuon_bsConstrainedMass"]

# eras = ["2022EE", "2022", "2023", "2023BPix", "2024"]#, "2025"]
# eras = ["2022", "2022EE", "2023", "2023BPix", "2024", "2025", "Combined"]
# eras = ["2022", "2022EE"]
# eras = ["2023", "2023BPix"]
#eras = ["2023BPix"]
# eras = ["2025","2024", "Combined"]
eras = ["Combined"]
#eras = ["2025"]

for era in eras:
    for variable in variables:
        draw_data_and_simul_and_ratio(
            variable,
            era,
            background_sources,
            signal_sources,
            True,
            production_channel,
            bdt_cuts,
            bdt_subset,
            jet_pT_study=False,
            version=version,
        )

    # draw_data_and_simul_and_ratio("PV", era, background_sources, signal_sources)
    # draw_data_and_simul_and_ratio("rho", era, background_sources, signal_sources)
    # draw_data_and_simul_and_ratio(
        # "PV", era, background_sources, signal_sources, use_puweight=False
    # )
    # draw_data_and_simul_and_ratio(
       # "rho", era, background_sources, signal_sources, use_puweight=False
    # )
