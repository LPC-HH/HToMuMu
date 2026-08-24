#ifndef LIB_RUN3CONTANTS_H
#define LIB_RUN3CONTANTS_H

#include <TString.h>
#include <map>

constexpr float H_TO_MUMU_BRANCHING_RATIO = 2.176e-4;

//// Luminosity in fb-1
const std::map<TString, float> LUMINOSITY = {
    {"2022B", 0.09656},  {"2022C", 5.0104},   {"2022D", 2.9700},
    {"2022E", 5.8070},   {"2022F", 17.7819},  {"2022G", 3.0828},
    {"2022", 7.9804},    {"2022EE", 26.6717}, {"2023", 17.96},
    {"2023BPix", 9.68}, {"2024", 109.82}, {"2025", 110.84}
};

//// Cross section in pb
const std::map<TString, float> CROSS_SECTION = {
    //********************//
    //     Background     //
    //********************//
    // ***** DY ***** //
    // {"DYJetstoLL", 6244.8},
    {"DYto2L-2Jets", 6244.8},
    {"DY50to120", 2219.},
    {"DY120to200", 21.65},
    // ***** EWK ***** //
    {"EWK_2L2J", 1.410},
    // ***** TT ***** //
    {"TTto2L2Nu", 86.61},
    {"TTtoLNu2Q", 358.61},
    {"TWminusto2L2Nu", 35.99},
    // {"TWminusto4Q", 35.99},
    {"TWminustoLNu2Q", 35.99},
    {"TbarWplusto2L2Nu", 36.05},
    // {"TbarWplusto4Q", -1},
    {"TbarWplustoLNu2Q", 36.05},
    // {"TbarQto2Q-t-channel", 78.56},
    {"TbarQtoLNu-t-channel", 78.56},
    // {"TQbarto2Q-t-channel", -1},
    {"TQbartoLNu-t-channel", 130.0},
    {"TBbartoLplusNuBbar-s-channel", 2.278},
    {"TbarBtoLminusNuB-s-channel", 1.430},
    // ***** Diboson ***** //
    {"WWto2L2Nu", 12.178},
    // {"WWto4Q", -1},
    // {"WWtoLNu2Q", -1},
    {"WZto2L2Q", 6.321},
    {"WZto3LNu", 4.658},
    // {"WZtoLNu2Q", 15.87},
    {"ZZto2L2Nu", 0.601},
    {"ZZto2L2Q", 3.696},
    {"ZZto4L", 1.325},
    // ***** TriBoson ***** //
    {"ZZZ", 0.01591},
    {"WZZ", 0.06206},
    {"WWZ_4F", 0.1851},
    {"WWW_4F", 0.2086},

    //********************//
    //       Signal       //
    //********************//
    {"ggH", 52.23 * H_TO_MUMU_BRANCHING_RATIO},
    {"VBF", 4.078 * H_TO_MUMU_BRANCHING_RATIO},
    {"ttH", 0.57 * H_TO_MUMU_BRANCHING_RATIO},
    {"WplusH", 0.8889 * H_TO_MUMU_BRANCHING_RATIO},
    {"WminusH", 0.5677 * H_TO_MUMU_BRANCHING_RATIO},
    {"ZH", 0.9439 * H_TO_MUMU_BRANCHING_RATIO},

    //********************//
    //  Dummy data value  //
    //********************//
    {"Data", -1},
    {"DoubleMuon_2022C", -1},
    {"Muon_2022C", -1},
    {"Muon_2022D", -1},
    {"SingleMuon_2022C", -1},
    {"Muon_2022E", -1},
    {"Muon_2022F", -1},
    {"Muon_2022G", -1},
    {"Muon0_2023B", -1},
    {"Muon0_2023C_v1", -1},
    {"Muon0_2023C_v2", -1},
    {"Muon0_2023C_v3", -1},
    {"Muon0_2023C_v4", -1},
    {"Muon1_2023B", -1},
    {"Muon1_2023C_v1", -1},
    {"Muon1_2023C_v2", -1},
    {"Muon1_2023C_v3", -1},
    {"Muon1_2023C_v4", -1},
    {"Muon0_2023D_v1", -1},
    {"Muon0_2023D_v2", -1},
    {"Muon1_2023D_v1", -1},
    {"Muon1_2023D_v2", -1},
    {"Muon0_2024B", -1},
    {"Muon0_2024C", -1},
    {"Muon0_2024D", -1},
    {"Muon0_2024E", -1},
    {"Muon0_2024F", -1},
    {"Muon0_2024G", -1},
    {"Muon0_2024H", -1},
    {"Muon0_2024I_v1", -1},
    {"Muon0_2024I_v2", -1},
    {"Muon1_2024B", -1},
    {"Muon1_2024C", -1},
    {"Muon1_2024D", -1},
    {"Muon1_2024E", -1},
    {"Muon1_2024F", -1},
    {"Muon1_2024G", -1},
    {"Muon1_2024H", -1},
    {"Muon1_2024I_v1", -1},
    {"Muon1_2024I_v2", -1},
    {"Muon0_2025B", -1},
    {"Muon0_2025C_v1", -1},
    {"Muon0_2025C_v2", -1},
    {"Muon0_2025D", -1},
    {"Muon0_2025E", -1},
    {"Muon0_2025F_v1", -1},
    {"Muon0_2025F_v2", -1},
    {"Muon0_2025G", -1},
    {"Muon1_2025B", -1},
    {"Muon1_2025C_v1", -1},
    {"Muon1_2025C_v2", -1},
    {"Muon1_2025D", -1},
    {"Muon1_2025E", -1},
    {"Muon1_2025F_v1", -1},
    {"Muon1_2025F_v2", -1},
    {"Muon1_2025G", -1},
    {"MuonEG_2024E_v1", -1},
    {"MuonEG_2024E_v2", -1},
    {"MuonEG_2024F", -1},
    {"MuonEG_2024G", -1},
    {"MuonEG_2024H", -1},
    {"MuonEG_2024I_v1", -1},
    {"MuonEG_2024I_v2", -1}
};

#endif // LIB_RUN3CONTANTS_H
