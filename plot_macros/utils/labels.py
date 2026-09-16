"""
A dictionary mapping variable names to their LaTeX-formatted x-axis labels for plotting.

Keys:
-----
Each key represents a variable name as a string, which categorizes the type of physical
quantity (e.g., DiMuon, Muon, Jet, DiJet variables).

Values:
------
Each value is a LaTeX-formatted string representing the label to be used on the x-axis
when plotting the corresponding variable.

"""

x_labels = {
    ## Event variables
    "PV": r"$PV$",
    "rho": r"$\rho$",
    ## DiMuon variables
    "diMuon_rapidity": r"$y_{\mu\mu}$",
    "diMuon_pt": r"$p_T^{\mu\mu}$ [GeV]",
    "diMuon_bsConstrainedPt": r"$p_T^{\mu\mu,BSC}$ [GeV]",
    "diMuon_mass": r"$m_{\mu\mu}$ [GeV]",
    "diMuon_bsConstrainedMass": r"$m_{\mu\mu,BSC}$ [GeV]",
    "diMuon_mass_full_range": r"$m_{\mu\mu}$ [GeV]",
    "diMuon_phi": r"$\phi_{\mu\mu}$ [rad]",
    "diMuon_eta": r"$\eta_{\mu\mu}$ ",
    "relative_diMuon_mass_error": r"$\sigma_{\mu\mu}/M_{\mu\mu}$",
    "relative_diMuon_bsConstrainedMass_error": r"$\sigma_{\mu\mu}/M_{\mu\mu} (BSC)$",
    ## Muon variables
    "mu1_pt_mass_ratio": r"$p_T^{\mu 1}/m_{\mu\mu}$",
    "mu2_pt_mass_ratio": r"$p_T^{\mu 2}/m_{\mu\mu}$",
    "mu1_bsConstrainedPt_mass_ratio": r"$p_{T,BSC}^{\mu 1}/m_{\mu\mu,BSC}$",
    "mu2_bsConstrainedPt_mass_ratio": r"$p_{T,BSC}^{\mu 1}/m_{\mu\mu,BSC}$",
    "mu1_eta": r"$\eta_{\mu_1}$",
    "mu2_eta": r"$\eta_{\mu_2}$",
    "phi_CS": r"$\phi_{CS} [rad]$",
    "cos_theta_CS": r"$cos(\theta_{CS})$",
    "mu1_pt": r"$p_T^{\mu_1}$ [GeV]",
    "mu2_pt": r"$p_T^{\mu_2}$ [GeV]",
    "mu1_ptErr": r"$p_{T,err}^{\mu_{1}}$ [GeV]",
    "mu2_ptErr": r"$p_{T,err}^{\mu_{2}}$ [GeV]",
    "mu1_bsConstrainedPt": r"$p_T^{\mu_{1,BSC}}$ [GeV]",
    "mu2_bsConstrainedPt": r"$p_T^{\mu_{2,BSC}}$ [GeV]",
    "mu1_bsConstrainedPtErr": r"$p_{T,err}^{\mu_{1,BSC}}$ [GeV]",
    "mu2_bsConstrainedPtErr": r"$p_{T,err}^{\mu_{2,BSC}}$ [GeV]",
    ## Jet variables
    "n_jet": r"$N_{jets}$",
    "leading_jet_pt": r"$p_T^{j1}$ [GeV]",
    "jet_pt": r"$p_T$ [GeV]",
    "subleading_jet_pt": r"$p_T^{j2}$ [GeV]",
    "leading_jet_eta": r"$\eta_{j1}$ ",
    "subleading_jet_eta": r"$\eta_{j2}$ ",
    "jet_phi": r"$\phi_{jet}$ [rad]",
    "jet_mass": r"$m_{jet}$ [GeV]",
    "delta_eta_diMuon_jet": r"$\Delta\eta_{\mu\mu,j}$",
    "delta_phi_diMuon_jet": r"$\Delta\phi_{\mu\mu,j}$",
    "leading_jet_mass": r"$M_{j1}$",
    "leading_jet_area": r"$Area_{j1}$",
    "leading_jet_btagPNetQvG": r"$PNet QvsG_{j1}$",
    "leading_jet_btagUParTAK4QvG": r"$UParT QvsG_{j1}$",
    "leading_jet_btagDeepFlavQG": r"$Deep QvsG_{j1}$",
    "leading_jet_chEmEF": r"Charged EM EF j1",
    "leading_jet_chHEF": r"Charged H EF j1",
    "leading_jet_neEmEF": r"Neutral EM EF j1",
    "leading_jet_neHEF": r"Neutral H EF j1",
    "leading_jet_nConstituents": r"$nConstituents_{j1}$",
    "leading_jet_chMultiplicity": r"$chMult_{j1}$",
    "leading_jet_neMultiplicity": r"$neMult_{j1}$",
    ##subleading
    "subleading_jet_mass": r"$M_{j2}$",
    "subleading_jet_area": r"$Area_{j2}$",
    "subleading_jet_btagPNetQvG": r"$PNet QvsG_{j2}$",
    "subleading_jet_btagUParTAK4QvG": r"$UParT QvsG_{j2}$",
    "subleading_jet_btagDeepFlavQG": r"$Deep QvsG_{j2}$",
    "subleading_jet_chEmEF": r"Charged EM EF j2",
    "subleading_jet_chHEF": r"Charged H EF j2",
    "subleading_jet_neEmEF": r"Neutral EM EF j2",
    "subleading_jet_neHEF": r"Neutral H EF j2",
    "subleading_jet_nConstituents": r"$nConstituents_{j2}$",
    "subleading_jet_chMultiplicity": r"$chMult_{j2}$",
    "subleading_jet_neMultiplicity": r"$neMult_{j2}$",
    ## DiJet variables
    "diJet_pt": r"$p_T^{jj}$ [GeV]",
    "diJet_eta": r"$\eta_{jj}$ ",
    "diJet_phi": r"$\phi_{jj}$ [rad]",
    "diJet_mass": r"$m_{jj}$ [GeV]",
    "diJet_mass_mo": r"$m_{Dijet highest mass}$ [GeV]",
    "diJet_DeltaEta": r"$\Delta\eta_{jj}$",
    "delta_eta_diJet": r"$|\Delta\eta_{jj}|$",
    "delta_phi_diJet": r"$|\Delta\phi_{jj}|$ [rad]",
    "z_zeppenfeld": r"Z^{*} Zeppenfeld",
    "min_delta_eta_diMuon_jet": r"min$\Delta\eta_{\mu\mu,j}$",
    "min_delta_phi_diMuon_jet": r"min$\Delta\phi_{\mu\mu,j}$ [rad]",
    "pt_balance": r"$R(p_T)$",
    "pt_centrality": r"$p_{T}-centrality$",
    "n_SoftJet_pt2": r"$N_{2}^{soft}$",
    "n_SoftJet_pt5": r"$N_{5}^{soft}$",
    "n_SoftJet_pt10": r"$N_{10}^{soft}$",
    "HT": r"$H_{T}(soft)$",
    "HT_pt2": r"$H_{T}^{2}(soft)$",
    "HT_pt5": r"$H_{T}^{5}(soft)$",
    "HT_pt10": r"$H_{T}^{10}(soft)$",
    "HT_extra": r"$H_{T} - leading jet(soft)$",
    ## BDT_ggh
    "BDT_ggH": "BDT Output",
    "BDT_VBF": "BDT Output",
}

"""
A dictionary specifying the number of histogram bins for each variable in the analysis.

Keys:
-----
Variable name as a string.

Values:
------
Integer values specifying the number of bins use to create a histogram.
"""
n_bins = {
    ## Event variables
    "PV": 70,
    "rho": 100,
    ## DiMuon variables
    "diMuon_rapidity": 50,
    "diMuon_pt": 80,
    "diMuon_bsConstrainedPt": 80,
    "diMuon_bsConstrainedMass":80,
    #"diMuon_bsConstrainedMass_full_range": 200,
    "diMuon_mass": 80,
    # "diMuon_mass_full_range": 200,
    "diMuon_phi": 80,
    "diMuon_eta": 50,
    "relative_diMuon_mass_error": 60,
    "relative_diMuon_bsConstrainedMass_error": 60,
    ## Muon variables
    "mu1_pt_mass_ratio": 50,
    "mu2_pt_mass_ratio": 50,
    "mu1_bsConstrainedPt_mass_ratio": 50,
    "mu2_bsConstrainedPt_mass_ratio": 50,
    "mu1_eta": 50,
    "mu2_eta": 50,
    "phi_CS": 50,
    "cos_theta_CS": 50,
    "mu1_pt": 60,
    "mu2_pt": 60,
    "mu1_ptErr": 80,
    "mu2_ptErr": 80,
    "mu1_bsConstrainedPt": 60,
    "mu2_bsConstrainedPt": 60,
    "mu1_bsConstrainedPtErr": 80,
    "mu2_bsConstrainedPtErr": 80,
    ## Jet variables
    "n_jet": 8,
    "leading_jet_pt": 50,
    "jet_pt": 80,
    "subleading_jet_pt": 50,
    "leading_jet_eta": 50,
    "subleading_jet_eta": 50,
    "jet_phi": 50,
    "jet_mass": 50,
    "delta_eta_diMuon_jet": 50,
    "delta_phi_diMuon_jet": 50,
    "leading_jet_mass": 50,
    "leading_jet_area": 25,
    "leading_jet_btagPNetQvG": 50,
    "leading_jet_btagUParTAK4QvG": 50,
    "leading_jet_btagDeepFlavQG": 50,
    "leading_jet_chEmEF": 50,
    "leading_jet_chHEF": 50,
    "leading_jet_neEmEF": 50,
    "leading_jet_neHEF": 50,
    "leading_jet_nConstituents": 50,
    "leading_jet_chMultiplicity": 50,
    "leading_jet_neMultiplicity": 50,
    ## subleading
    "subleading_jet_mass": 50,
    "subleading_jet_area": 50,
    "subleading_jet_btagPNetQvG": 50,
    "subleading_jet_btagUParTAK4QvG": 50,
    "subleading_jet_btagDeepFlavQG": 50,
    "subleading_jet_chEmEF": 50,
    "subleading_jet_chHEF": 50,
    "subleading_jet_neEmEF": 50,
    "subleading_jet_neHEF": 50,
    "subleading_jet_nConstituents": 50,
    "subleading_jet_chMultiplicity": 50,
    "subleading_jet_neMultiplicity": 50,
    ## DiJet variables
    "diJet_pt": 50,
    "diJet_eta": 50,
    "diJet_phi": 50,
    "diJet_mass": 250,
    "diJet_mass_VBF": 50,
    "diJet_mass_mo": 50,
    "diJet_DeltaEta": 50,
    "delta_eta_diJet": 50,
    "delta_eta_diJet_ggH": 50,
    "delta_eta_diJet_VBF": 50,
    "delta_phi_diJet": 50,
    "z_zeppenfeld": 50,
    "z_zeppenfeld_VBF": 50,
    "min_delta_eta_diMuon_jet": 50,
    "min_delta_phi_diMuon_jet": 50,
    "pt_balance": 40,
    "pt_centrality": 30,
    "n_SoftJet_pt2": 40,
    "n_SoftJet_pt5": 40,
    "n_SoftJet_pt10": 40,
    "HT": 20,
    "HT_pt2": 20,
    "HT_pt5": 20,
    "HT_pt10": 20,
    "HT_extra": 20,
    ## BDT_ggh
    "BDT_ggH": 100,
    "BDT_VBF": 100,
}

"""
A dictionary defining the x-axis range for plotting each variable.

Keys:
-----
Variable name as a string
Values:
------
Tuple of two floats specifying the minimum and maximum range for the x-axis.
"""
x_range = {
    ## Event variables
    "PV": (0, 70),
    "rho": (0, 70),
    ## DiMuon variables
    "diMuon_pt": (0, 250),
    "diMuon_mass": (110, 150),
    "diMuon_bsConstrainedPt": (0, 250),
    "diMuon_bsConstrainedMass": (110, 150),
    "diMuon_phi": (-3.1415, 3.1415),
    "diMuon_eta": (-10, 10),
    "diMuon_rapidity": (-2.5, 2.5),
    #"diMuon_mass_Z": (85, 100),
    "relative_diMuon_mass_error": (0,1.1),
    "relative_diMuon_bsConstrainedMass_error": (0,1.1),
    # "diMuon_mass_full_range": (50, 150),
    ## Muon variables
    "mu1_pt_mass_ratio": (0.19, 1.6),
    "mu2_pt_mass_ratio": (0.19, 1.6),
    "mu1_bsConstrainedPt_mass_ratio": (0.19, 1.6),
    "mu2_bsConstrainedPt_mass_ratio": (0.19, 1.6),
    "mu1_eta": (-2.4, 2.4),
    "mu2_eta": (-2.4, 2.4),
    "phi_CS": (-3.1415, 3.1415),
    "cos_theta_CS": (-1, 1),
    "mu1_pt": (0,1000),
    "mu2_pt": (0,500),
    "mu1_ptErr": (0,100),
    "mu2_ptErr": (0,35),
    "mu1_bsConstrainedPt": (0,1000),
    "mu2_bsConstrainedPt": (0,500),
    "mu1_bsConstrainedPtErr": (0,100),
    "mu2_bsConstrainedPtErr": (0,35),
    ## Jet variables
    "n_jet": (0, 8),
    "leading_jet_pt": (25, 400),
    "jet_pt": (0, 400),
    "subleading_jet_pt": (25, 200),
    "leading_jet_eta": (-5, 5),
    "subleading_jet_eta": (-5, 5),
    "jet_phi": (-3.1415, 3.1415),
    "jet_mass": (0, 120),
    "delta_eta_diMuon_jet": (-10, 10),
    "delta_phi_diMuon_jet": (-5, 5),
    "leading_jet_mass": (0,150),
    "leading_jet_area": (0.2, 1),
    "leading_jet_btagPNetQvG": (0,1),
    "leading_jet_btagUParTAK4QvG": (0,1),
    "leading_jet_btagDeepFlavQG": (0,1),
    "leading_jet_chEmEF": (0,1),
    "leading_jet_chHEF": (0,1),
    "leading_jet_neEmEF": (0,1),
    "leading_jet_neHEF": (0,1),
    "leading_jet_nConstituents": (0,50),
    "leading_jet_chMultiplicity": (0,50),
    "leading_jet_neMultiplicity": (0,50),
    ## subleading
    "subleading_jet_mass": (0,150),
    "subleading_jet_area": (0, 1.5),
    "subleading_jet_btagPNetQvG": (0,1),
    "subleading_jet_btagUParTAK4QvG": (0,1),
    "subleading_jet_btagDeepFlavQG": (0,1),
    "subleading_jet_chEmEF": (0,1),
    "subleading_jet_chHEF": (0,1),
    "subleading_jet_neEmEF": (0,1),
    "subleading_jet_neHEF": (0,1),
    "subleading_jet_nConstituents": (0,50),
    "subleading_jet_chMultiplicity": (0,50),
    "subleading_jet_neMultiplicity": (0,50),
    ## DiJetvariables
    "diJet_pt": (0, 800),
    "diJet_eta": (-10, 10),
    "diJet_phi": (-3.1415, 3.1415),
    "diJet_mass": (0, 2500),
    "diJet_mass_VBF": (300, 900),
    "diJet_mass_mo": (0, 800),
    "diJet_DeltaEta": (-12, 12),
    "delta_eta_diJet": (0, 8.0),
    "delta_eta_diJet_ggH": (0, 8.0),
    "delta_eta_diJet_VBF": (2.0, 8.0),
    "delta_phi_diJet": (0, 3.14),
    "z_zeppenfeld": (-7, 7),
    "z_zeppenfeld_VBF": (-5, 5),
    "min_delta_eta_diMuon_jet": (0, 5),
    "min_delta_phi_diMuon_jet": (0, 3.14),
    "pt_balance": (0, 1),
    "pt_centrality": (0, 12),
    "n_SoftJet_pt2": (0, 40),
    "n_SoftJet_pt5": (0, 40),
    "n_SoftJet_pt10": (0, 40),
    "HT": (0, 400),
    "HT_pt2": (0, 400),
    "HT_pt5": (0, 400),
    "HT_pt10": (0, 400),
    "HT_extra": (0, 400),
    ## BDT_ggh
    "BDT_ggH": (0, 1),
    "BDT_VBF": (0, 1),
}

# y_labels = {
    # "diMuon_mass": r"events",
    # "diMuon_mass_full_range": r"events",
    # "diMuon_rapidity": r"events",
    # "diMuon_pt": r"events",
    # "diMuon_phi": r"events",
    # "diMuon_eta": r"events",
# }

background_labels = {
    ## DY
    "DY50-120": "DY MLL50-120 Bg",
    "DY120-200": "DY MLL120-200 Bg",
    "DY": "DY Background",
    "DYJetstoLL": "DY Background",
    "DYto2L-2Jets": "DY Background",
    "DYNew": "DY Background",
    ## TT
    "TT": "TT Background",
    ## DiBoson
    "DiBoson": "DiBoson Background",
    "ZZto2L2Nu": "ZZto2L2Nu",
    "ZZto4L": "ZZto4L",
    "WWto2L2Nu": "WWto2L2Nu",
    "ZZto2L2QNu": "ZZto2L2QNu",
    "WZto2L2QNu": "WZto2L2QNu",
    ## EWK
    "EWK": "EWK Background",
}

"""
A dictionary storing the integrated luminosity values for different data-taking periods.

Keys:
-----
Year or era as a string(e.g., "2022", "2022EE", "2022Combined".)

Values:
------
String representing the integrated luminosity value for each period in inverse femtobarns.
"""
luminosity = {
    ## LUMINOSITIES
    "2022": "7.98",
    "2022EE": "26.67",
    "2022Combined": "34.65",
    "2023": "17.79",
    "2023BPix": "9.45",
    "2023Combined": "27.24",
    "2024": "109.08",
    "2025": "110.73",
    # "Combined": "61.89",
    # "Combined": "170.97",
    "Combined": "281.7"
}

variables_type = {
    ## Event variables
    "event": [
        "PV",
        "rho",
        "n_SoftJet_pt2",
        "n_SoftJet_pt5",
        "n_SoftJet_pt10",
        "HT",
        "HT_pt2",
        "HT_pt5",
        "HT_pt10",
        "HT_extra",
    ],
    ## DiMuon variables
    "diMuon": [
        "diMuon_rapidity",
        "diMuon_pt",
        "diMuon_mass",
        "diMuon_bsConstrainedPt",
        "diMuon_bsConstrainedMass",
        "diMuon_mass_full_range",
        "diMuon_phi",
        "diMuon_eta",
        "relative_diMuon_mass_error",
        "relative_diMuon_bsConstrainedMass_error",
    ],
    ## Muon variables
    "muon": [
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
    ],
    ## Jet variables
    "jet": [
        "n_jet",
        "leading_jet_pt",
        "subleading_jet_pt",
        "leading_jet_eta",
        "subleading_jet_eta",
        "jet_phi",
        "jet_mass",
        "delta_eta_diMuon_jet",
        "delta_phi_diMuon_jet",
        "leading_jet_mass",
        "leading_jet_area",
        "leading_jet_btagPNetQvG",
        "leading_jet_btagUParTAK4QvG",
        "leading_jet_btagDeepFlavQG",
        "leading_jet_chEmEF",
        "leading_jet_chHEF",
        "leading_jet_neEmEF",
        "leading_jet_neHEF",
        "leading_jet_nConstituents",
        "leading_jet_chMultiplicity",
        "leading_jet_neMultiplicity",
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
    ],
    ## DiJet variables
    "diJet": [
        "diJet_pt",
        "diJet_eta",
        "diJet_phi",
        "diJet_mass",
        "diJet_mass_mo",
        "diJet_DeltaEta",
        "delta_eta_diJet",
        "delta_phi_diJet",
        "z_zeppenfeld",
        "pt_balance",
        "pt_centrality",
        "min_delta_eta_diMuon_jet",
        "min_delta_phi_diMuon_jet",
    ],
    ## BDT
    "BDT_channel": [
        "BDT_ggH",
        "BDT_VBF",
    ],
}
