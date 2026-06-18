from utils.sig_vs_bg import draw_sig_and_bg_from_tuple
import sys

if len(sys.argv) != 2:
    print("Include argument with the channel you are studying (ggH or VBF)")
    exit()
channel_US = sys.argv[1]

variables = [
    ## DiMuon variables
    "diMuon_rapidity",
    "diMuon_pt",
    ## Muon variables
    "mu1_pt_mass_ratio",
    "mu2_pt_mass_ratio",
    "mu1_eta",
    "mu2_eta",
    "phi_CS",
    "cos_theta_CS",
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

#variables = ["diMuon_pt", "leading_jet_eta"]

# eras = ["2022", "2022EE"]
# eras = ["2023", "2023BPix"]
# eras = ["2022", "2022EE", "2023", "2023BPix"]
#eras = ["2022", "2022EE", "2022Combined", "2023", "2023BPix", "2023Combined", "2024", "Combined"]
#eras = ["2024", "Combined"]
eras = ["Combined"]
background_subset = ["Full"]
# background_subset = ["NoDY50"]
# signal_subset = ["Full", "NottH", "VBF"]
signal_subset = ["NottH"]
# signal_subset = ["VBF"]

for bsubset in background_subset:
    for ssubset in signal_subset:
        for era in eras:
            for variable in variables:
                draw_sig_and_bg_from_tuple(variable, era, False,
                        channel_US, bsubset, ssubset)
                draw_sig_and_bg_from_tuple(variable, era, True,
                        channel_US, bsubset, ssubset)
