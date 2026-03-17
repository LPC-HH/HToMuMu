from utils.sim_vs_data import draw_data_and_simul_and_ratio
import sys

if len(sys.argv) == 2:
    production_channel = sys.argv[1]
    bdt_subset = "BFull_SNottH"
    print("You selected " + production_channel + " channel")

else:
    print("Producion channel was not selected. Using all the events")
    production_channel = ""
    bdt_subset = ""

# use_ggH = False if sys.argv[1] != "ggH" else True
# use_VBF = False if sys.argv[1] != "VBF" else True

# if not use_ggH and not use_VBF:
# print("Using no category selection as default.")

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
    "ttH",
]
bdt_selections = {
    "ggH": {
        # "BFull_SNottH": [0.0, 0.06461538461538464, 0.16153846153846155, 1.0],
        ##"BFull_SNottH": [0.0, 0.19730769230769193, 0.4384615384615378, 1.0],
        "BFull_SNottH": [0.0, 0.46000000000000024, 0.6100000000000003, 0.7400000000000004, 0.8300000000000005, 0.9000000000000006, 1.0],
    },
    "VBF": {
        ##"BFull_SNottH": [0.0, 0.30789150000000015, 0.6283500000000011, 0.8850000000000007, 1.0],
        #"BNoDY50_SNottH": [0.0, 0.546, 0.935, 0.985, 1.0],
        "BFull_SNottH":[0.0, 0.6200000000000001, 0.7933333333333346, 0.8933333333333352, 0.9266666666666687, 0.9600000000000023, 1.0],
    },
    "": {"":""},
}

variables = [
    ## DiMuon variables
    "diMuon_mass",
    # "diMuon_mass_full_range",
     "diMuon_bsConstrainedMass",
    # "diMuon_mass_Z",
    # "diMuon_bsConstrainedMass_Z",
    "diMuon_rapidity",
    "diMuon_eta",
    "diMuon_pt",
    "diMuon_bsConstrainedPt",
    "diMuon_phi",
    "relative_diMuon_mass_error",
    "relative_diMuon_bsConstrainedMass_error",
    ## Muon variables
    "mu1_pt_mass_ratio",
    "mu2_pt_mass_ratio",
    "mu1_bsConstrainedPt_mass_ratio",
    "mu2_bsConstrainedPt_mass_ratio",
    "mu1_eta",
    "mu2_eta",
    "phi_CS",
    "cos_theta_CS",
    "mu1_pt",
    "mu2_pt",
    "mu1_ptErr",
    "mu2_ptErr",
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
    "n_SoftJet_pt5",
    "n_SoftJet_pt10",
    "HT",
    "HT_pt2",
    "HT_pt5",
    "HT_pt10",
]

#variables = ["leading_jet_eta"]#, "subleading_jet_eta"]
#variables = ["diMuon_bsConstrainedMass"]
#variables = []

# eras = ["2022EE", "2022", "2023", "2023BPix", "2024"]#, "2025"]
eras = ["2022", "2022EE", "2023", "2023BPix", "2024", "2025", "Combined"]
# eras = ["2022", "2022EE"]
# eras = ["2023", "2023BPix"]
#eras = ["2023BPix"]
#eras = ["2024", "Combined"]
#eras = ["Combined"]
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
            bdt_selections[production_channel][bdt_subset],
            bdt_subset,
            jet_pT_study=False
        )
    
    draw_data_and_simul_and_ratio(
        "leading_jet_pt",
        era,
        background_sources,
        signal_sources,
        True,
        production_channel,
        bdt_selections[production_channel][bdt_subset],
        bdt_subset,
        jet_pT_study=True
    )
    
    draw_data_and_simul_and_ratio(
        "subleading_jet_pt",
        era,
        background_sources,
        signal_sources,
        True,
        production_channel,
        bdt_selections[production_channel][bdt_subset],
        bdt_subset,
        jet_pT_study=True
    )
    '''
    draw_data_and_simul_and_ratio(
            "diMuon_bsConstrainedMass",
            era,
            background_sources,
            signal_sources,
            True,
            production_channel,
            bdt_selections[production_channel][bdt_subset],
            bdt_subset,
            True,
        )'''
    #draw_data_and_simul_and_ratio(
    #        "diMuon_bsConstrainedMass",
    #        era,
    #        background_sources,
    #        signal_sources,
    #        True,
    #        production_channel,
    #        bdt_selections[production_channel][bdt_subset],
    #        bdt_subset,
    #        False,
    #    )

    # draw_data_and_simul_and_ratio("PV", era, background_sources, signal_sources)
    # draw_data_and_simul_and_ratio("rho", era, background_sources, signal_sources)
    # draw_data_and_simul_and_ratio(
        # "PV", era, background_sources, signal_sources, use_puweight=False
    # )
    # draw_data_and_simul_and_ratio(
       # "rho", era, background_sources, signal_sources, use_puweight=False
    # )
