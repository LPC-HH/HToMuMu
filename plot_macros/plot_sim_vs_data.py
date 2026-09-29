from utils.sim_vs_data import draw_data_and_simul_and_ratio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))
from bdt_categories_io import load_bdt_categories, get_bdt_cuts

production_channel = ""
bdt_subset = ""
use_categories = False
version = "2.2.2"

if len(sys.argv) >= 2:
    production_channel = sys.argv[1]

    if production_channel not in ["ggH", "VBF", "ggHreCat", "VBFreCat"]:
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
bdt_categories_info = load_bdt_categories()
bdt_mass_variable = "diMuon_bsConstrainedMass"

variablesBDT = [
    ## DiMuon variables
    #"diMuon_mass",
    # "diMuon_mass_full_range",
     "diMuon_bsConstrainedMass",
    "diMuon_rapidity",
    "diMuon_eta",
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
    "mu1_bsConstrainedPt",
    "mu2_bsConstrainedPt",
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
    "HT",
]

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
    "leading_jet_eta",
    "leading_jet_mass",
    "leading_jet_area",
    "leading_jet_btagPNetQvG",
    "leading_jet_btagUParTAK4QvG"   ,
    "leading_jet_btagDeepFlavQG",
    "leading_jet_chEmEF",
    "leading_jet_chHEF",
    "leading_jet_neEmEF",
    "leading_jet_neHEF",
    "leading_jet_nConstituents",
    "leading_jet_chMultiplicity",
    "leading_jet_neMultiplicity",
    ## subleading
    "subleading_jet_pt",
    "subleading_jet_eta",
    "subleading_jet_mass",
    "subleading_jet_area",
    "subleading_jet_btagPNetQvG",
    "subleading_jet_btagUParTAK4QvG",
    "subleading_jet_btagDeepFlavQG",
    "subleading_jet_chEmEF",
    "subleading_jet_chHEF",
    "subleading_jet_neEmEF",
    "subleading_jet_neHEF",
    "subleading_jet_nConstituents",
    "subleading_jet_chMultiplicity",
    "subleading_jet_neMultiplicity",
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
#variables = ["diMuon_bsConstrainedMass"]
#variables = variablesBDT




# eras = ["2022EE", "2022", "2023", "2023BPix", "2024"]#, "2025"]
# eras = ["2025","2024", "Combined"]
# eras = ["Combined", "2025", "2024"]
eras = ["Combined"]

for era in eras:
    if production_channel == "":
        bdt_cuts = []
    elif use_categories:
        bdt_cuts = get_bdt_cuts(
            bdt_categories_info, production_channel, era, bdt_subset, bdt_mass_variable
        )
    for variable in variables:
        print(production_channel)
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
