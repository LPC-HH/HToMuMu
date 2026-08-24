//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Mon Aug 27 15:49:34 2018 by ROOT version 6.10/09
// from TTree Events/Events
// found on file:
// root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAOD/GluGluHToMuMu_M-125_13TeV_powheg_pythia8/NANOAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/00000/AA4BF847-3785-E811-B130-001E67DFFF5F.root
//////////////////////////////////////////////////////////

#ifndef HmmAnalyzer_h
#define HmmAnalyzer_h

#include <TChain.h>
#include <TFile.h>
#include <TROOT.h>
#include <cmath>
#include <fstream>
#include <iostream>
#include <map>
#include <math.h>
#include <algorithm>
#include <cctype>
#include <stdexcept>
#include <memory>
// Header file for the classes stored in the TTree if any.
#include "../src/BTagCalibrationStandalone.cpp"
#include "BTagCalibrationStandalone.h"
#include "LeptonEfficiencyCorrector.h"
#include "MainEvent.h"
#include "TAxis.h"
#include "TF1.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TH3F.h"
#include "TLorentzVector.h"
#include "TRandom.h"
#include <string>
#include <vector>
#ifdef __CINT__

#pragma link C++ class vector < float> + ;
#pragma link C++ class vector < int> + ;
#pragma link C++ class vector < bool> + ;
#endif
// Header file for the classes stored in the TTree if any.

// NULL_FLOAT_VALUE = -999.
constexpr float MUON_MASS = 0.1056583745;
constexpr float FLOAT_NULL_VALUE = -999.;
constexpr int INT_NULL_VALUE = -999;

inline const std::map<TString, TString> NANOAOD_VERSION = {
    {"2022", "v12"}, {"2022EE", "v12"},  {"2023", "v12"}, {"2023BPix", "v12"}, {"2024", "v15"}, {"2025", "v15"}
};

inline std::string GetJercYear(const std::string &year) {
    if (year == "2022")
        return "2022Pre";
    else if (year == "2022EE")
        return "2022Post";
    else if (year == "2023")
        return "2023Pre";
    else if (year == "2023BPix")
        return "2023Post";
    else if (year == "2024")
        return "2024";
    else if (year == "2025")
        return "2025";
    else
        throw std::runtime_error("Unsupported JERC year: " + year);
}

inline std::string GetJercEra(const std::string &jec_year) {
    if (jec_year == "2022Pre")
        return "Era2022PreAll";
    if (jec_year == "2022Post")
        return "Era2022PostAll";
    if (jec_year == "2023Pre")
        return "Era2023PreAll";
    if (jec_year == "2023Post")
        return "Era2023PostAll";
    if (jec_year == "2024")
        return "Era2024All";
    if (jec_year == "2025")
        return "Era2025All";
    throw std::runtime_error("Unsupported JEC era year: " + jec_year);
}


inline const std::vector<std::string> jet_jes_syst_names = {
    "CMS_scale_j_FlavorQCD",
    "CMS_scale_j_RelativeBal",
    "CMS_scale_j_HF",
    "CMS_scale_j_BBEC1",
    "CMS_scale_j_EC2",
    "CMS_scale_j_Absolute",
   
    "CMS_scale_j_BBEC1_2022",
    "CMS_scale_j_RelativeSample_2022",
    "CMS_scale_j_EC2_2022",
    "CMS_scale_j_HF_2022",
    "CMS_scale_j_Absolute_2022",
    
    "CMS_scale_j_BBEC1_2022EE",
    "CMS_scale_j_RelativeSample_2022EE",
    "CMS_scale_j_EC2_2022EE",
    "CMS_scale_j_HF_2022EE",
    "CMS_scale_j_Absolute_2022EE",

    "CMS_scale_j_BBEC1_2023",
    "CMS_scale_j_RelativeSample_2023",
    "CMS_scale_j_EC2_2023",
    "CMS_scale_j_HF_2023",
    "CMS_scale_j_Absolute_2023",
    
    "CMS_scale_j_BBEC1_2023BPix",
    "CMS_scale_j_RelativeSample_2023BPix",
    "CMS_scale_j_EC2_2023BPix",
    "CMS_scale_j_HF_2023BPix",
    "CMS_scale_j_Absolute_2023BPix",

    "CMS_scale_j_BBEC1_2024",
    "CMS_scale_j_RelativeSample_2024",
    "CMS_scale_j_EC2_2024",
    "CMS_scale_j_HF_2024",
    "CMS_scale_j_Absolute_2024",

    "CMS_scale_j_BBEC1_2025",
    "CMS_scale_j_RelativeSample_2025",
    "CMS_scale_j_EC2_2025",
    "CMS_scale_j_HF_2025",
    "CMS_scale_j_Absolute_2025",

};

inline const std::vector<std::string> jes_directions = {
    "Up",
    "Down"
};

inline const std::vector<std::string> jet_jer_syst_names = {
    "CMS_res_j_eta0to1p93_pt0toInf_2022",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2022",
    "CMS_res_j_eta2p5to3p0_pt0to50_2022",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2022",
    "CMS_res_j_eta3to5_pt0to50_2022",
    "CMS_res_j_eta3to5_pt50toInf_2022",

    "CMS_res_j_eta0to1p93_pt0toInf_2022EE",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2022EE",
    "CMS_res_j_eta2p5to3p0_pt0to50_2022EE",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2022EE",
    "CMS_res_j_eta3to5_pt0to50_2022EE",
    "CMS_res_j_eta3to5_pt50toInf_2022EE",

    "CMS_res_j_eta0to1p93_pt0toInf_2023",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2023",
    "CMS_res_j_eta2p5to3p0_pt0to50_2023",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2023",
    "CMS_res_j_eta3to5_pt0to50_2023",
    "CMS_res_j_eta3to5_pt50toInf_2023",

    "CMS_res_j_eta0to1p93_pt0toInf_2023BPix",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2023BPix",
    "CMS_res_j_eta2p5to3p0_pt0to50_2023BPix",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2023BPix",
    "CMS_res_j_eta3to5_pt0to50_2023BPix",
    "CMS_res_j_eta3to5_pt50toInf_2023BPix",

    "CMS_res_j_eta0to1p93_pt0toInf_2024",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2024",
    "CMS_res_j_eta2p5to3p0_pt0to50_2024",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2024",
    "CMS_res_j_eta3to5_pt0to50_2024",
    "CMS_res_j_eta3to5_pt50toInf_2024",

    "CMS_res_j_eta0to1p93_pt0toInf_2025",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2025",
    "CMS_res_j_eta2p5to3p0_pt0to50_2025",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2025",
    "CMS_res_j_eta3to5_pt0to50_2025",
    "CMS_res_j_eta3to5_pt50toInf_2025",

};

inline const std::vector<std::string> jer_directions = {
    "Up",
    "Down"
};

inline std::string ToLower(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(),
                   [](unsigned char c) { return std::tolower(c); });
    return s;
}


inline std::string NormalizeMuonPtSyst(std::string syst) {
    syst = ToLower(syst);

    if (syst == "nominal" || syst == "none") {
        return "nominal";
    }
    if (syst == "scale_up" || syst == "scale_down" ||
        syst == "smearing_up" || syst == "smearing_down") {
        return syst;
    }

    throw std::runtime_error(
        "Unsupported muon pT systematic: " + syst +
        ". Use nominal, scale_up, scale_down, smearing_up, or smearing_down.");
}

inline bool IsMuonScaleSyst(const std::string &syst) {
    return syst == "scale_up" || syst == "scale_down";
}

inline bool IsMuonSmearingSyst(const std::string &syst) {
    return syst == "smearing_up" || syst == "smearing_down";
}

inline std::string MuonSystDirection(const std::string &syst) {
    if (syst.size() >= 3 && syst.substr(syst.size() - 3) == "_up") {
        return "up";
    }
    if (syst.size() >= 5 && syst.substr(syst.size() - 5) == "_down") {
        return "down";
    }
    return "nominal";
}

inline std::string JetPtJesSystBranchName(const std::string &syst_name,
                                const std::string &direction) {
    return "t_Jet_pt_" + syst_name + "_" + ToLower(direction);
}

inline std::string JetPtJerSystBranchName(const std::string &syst_name,
                                   const std::string &direction) {
    return "t_Jet_pt_" + syst_name + "_" + ToLower(direction);
}

inline std::string JetMassJesSystBranchName(const std::string &syst_name,
                                            const std::string &direction) {
    return "t_Jet_mass_" + syst_name + "_" + ToLower(direction);
}

inline std::string JetMassJerSystBranchName(const std::string &syst_name,
                                            const std::string &direction) {
    return "t_Jet_mass_" + syst_name + "_" + ToLower(direction);
}

inline bool IsYearLabel(const std::string &label) {
    static const std::vector<std::string> valid_year_labels = {
        "2022",
        "2022EE",
        "2023",
        "2023BPix",
        "2024",
        "2025"
    };

    return std::find(valid_year_labels.begin(),
                     valid_year_labels.end(),
                     label) != valid_year_labels.end();
}

inline std::string GetSuffixAfterLastUnderscore(const std::string &name) {
    const size_t pos = name.find_last_of('_');

    if (pos == std::string::npos || pos + 1 >= name.size()) {
        return "";
    }

    return name.substr(pos + 1);
}

inline bool JecSystAppliesToYear(const std::string &syst_name,
                          const std::string &yearst) {
    const std::string suffix = GetSuffixAfterLastUnderscore(syst_name);

    if (!IsYearLabel(suffix)) {
        return true;
    }

    return suffix == yearst;
}





class HmmAnalyzer : public MainEvent {
  public:
    HmmAnalyzer(const TString &inputFileList = "foo.txt",
                const char *outFileName = "histo.root",
                TString dataset = "data", bool is_data_input = false,
                TString year_num = "2017",  bool include_Z_ = false, bool include_H_ = true);
    virtual ~HmmAnalyzer();
    // void Analyze(bool is_data, int option, string outputFileName, string
    // label);

    Bool_t FillChain(TChain *chain, const TString &inputFileList);
    Long64_t LoadTree(Long64_t entry);
    void getPileupHistograms();
    float getPileupWeight(int);
    float getPileupWeightUp(int);
    float getPileupWeightDown(int);
    //bool passesJetPtSelection(int index, float corrected_pt);
    bool isValidJet(int index, float corrected_pt);
    void EventLoop();

    //read run3 muon efficiency json file


    void clearTreeVectors();
    void BookTreeBranches();
    bool is_data;
    TString year;
    bool include_Z; /**< Flag indicating if save Z region. */
    bool include_H; /**< Flag indicating if save H region. */
    std::string muon_pt_syst;
    bool apply_muon_pt_syst_to_signal;
    std::string yearst;
    std::map<std::string, float> muon_pt_cut;
    std::map<std::string, float> btagLoose_cut;
    std::map<std::string, float> btagMedium_cut;

    TH1D *h_sumOfgw = new TH1D("h_sumOfgenWeight", "h_sumOfgenWeight", 1, 0, 1);
    TH1D *h_sumOfgpw =
        new TH1D("h_sumOfgenpuWeight", "h_sumOfgenpuWeight", 1, 0, 1);
    TH1D *h_pileup = new TH1D("h_pileup", "h_pileup", 99, 0, 99);
    TH1D *h_pileup_nTrue = new TH1D("h_pileup_nTrue", "h_pileup_nTrue", 99, 0, 99);

    TFile *pileupWeightFile;
    TH1F *pileupWeightHist, *pileupWeightSysUpHist, *pileupWeightSysDownHist;

    std::vector<std::string> muon_effSF_TRIG_files, muon_effSF_ID_files,
        muon_effSF_ISO_files;
    std::vector<std::string> histo_names_TRIG, histo_names_ID,
        histo_names_ID_stat, histo_names_ID_syst, histo_names_ISO,
        histo_names_ISO_stat, histo_names_ISO_syst;

    //synchronization histograms
    TH1D *h_nEntries = new TH1D("h_nEntries", "h_nEntries", 1, 0, 1);
    TH1D *h_nTrigger = new TH1D("h_nTrigger", "h_nTrigger", 1, 0, 1);
    TH1D *h_nTwoMuons = new TH1D("h_nTwoMuons", "h_nTwoMuons", 1, 0, 1);
    TH1D *h_nNoExtraMuon = new TH1D("h_nNoExtraMuon", "h_nNoExtraMuon", 1, 0, 1);
    TH1D *h_nNoExtraElectron = new TH1D("h_nNoExtraElectron", "h_nNoExtraElectron", 1, 0, 1);
    TH1D *h_nTriggerMatch = new TH1D("h_nTriggerMatch", "h_nTriggerMatch", 1, 0, 1);
    TH1D *h_nInMassRegion = new TH1D("h_nInMassRegion", "h_nInMassRegion", 1, 0, 1);
    TH1D *h_nBjetRejection = new TH1D("h_nBjetRejection", "h_nBjetRejection", 1, 0, 1);
    TH1D *h_nInZPeak= new TH1D("h_nInZPeak", "h_nInZPeak", 1, 0, 1);

    //jet test histograms
    TH1D *h_nJets = new TH1D("h_nJets", "h_nJets", 1, 0, 1);
    TH1D *h_nValidJets = new TH1D("h_nValidJets", "h_nValidJets", 1, 0, 1);
    TH1D *h_nValidSeperatedJets = new TH1D("h_nValidSeperatedJets", "h_nValidSeperatedJets", 1, 0, 1);
    TH1D *h_nValidNotVetoedJets = new TH1D("h_nValidNotVetoedJets", "h_nValidNotVetoedJets", 1, 0, 1);

    TFile *oFile;
    // TFile *ohistFile;
    TTree *tree;
    uint t_run;
    uint t_luminosityBlock;
    ulong t_event;
    float t_genWeight;
    float t_pileup;
    float t_puWeight;
    float t_puWeightUp;
    float t_puWeightDown;
    float t_PrefireWeight;
    float t_PrefireWeight_Up;
    float t_PrefireWeight_Down;
    int t_mu1;
    int t_mu2;
    int t_index_trigm_mu;
    std::vector<int> *t_El_genPartIdx;
    std::vector<UChar_t> *t_El_genPartFlav;
    std::vector<int> *t_El_charge;
    std::vector<float> *t_El_pt;
    std::vector<float> *t_El_phi;
    std::vector<float> *t_El_eta;
    std::vector<float> *t_El_mass;
    std::vector<int> *t_El_cutBased;
    std::vector<int> *t_El_tightCharge;
    std::vector<bool> *t_El_cutBased_HEEP;
    std::vector<bool> *t_El_isPFcand;
    std::vector<float> *t_El_pfRelIso03_all;
    std::vector<float> *t_El_pfRelIso03_chg;
    std::vector<float> *t_El_miniPFRelIso_all;
    std::vector<float> *t_El_miniPFRelIso_chg;
    std::vector<float> *t_El_dxy;
    std::vector<float> *t_El_dxyErr;
    std::vector<float> *t_El_dz;
    std::vector<float> *t_El_dzErr;
    std::vector<float> *t_El_sip3d;
    std::vector<float> *t_Electron_mvaFall17Iso;
    std::vector<bool> *t_Electron_mvaFall17Iso_WP80; //[nElectron]
    std::vector<bool> *t_Electron_mvaFall17Iso_WP90; //[nElectron]
    std::vector<bool> *t_Electron_mvaFall17Iso_WPL;  //[nElectron]
    std::vector<float> *t_Electron_mvaFall17noIso;
    std::vector<bool> *t_Electron_mvaFall17noIso_WP80; //[nElectron]
    std::vector<bool> *t_Electron_mvaFall17noIso_WP90; //[nElectron]
    std::vector<bool> *t_Electron_mvaFall17noIso_WPL;  //[nElectron]

    std::vector<int> *t_Mu_genPartIdx;
    std::vector<UChar_t> *t_Mu_genPartFlav;
    std::vector<int> *t_Mu_charge;
    //std::vector<float> *t_Mu_EffSF_TRIG;
    //std::vector<float> *t_Mu_EffSF_TRIG_up;
    //std::vector<float> *t_Mu_EffSF_TRIG_down;
    std::vector<float> *t_Mu_EffTRIG_DATA;
    std::vector<float> *t_Mu_EffTRIG_DATA_up;
    std::vector<float> *t_Mu_EffTRIG_DATA_down;
    std::vector<float> *t_Mu_EffTRIG_MC;
    std::vector<float> *t_Mu_EffTRIG_MC_up;
    std::vector<float> *t_Mu_EffTRIG_MC_down;

    std::vector<float> *t_Mu_EffSF_ID;
    std::vector<float> *t_Mu_EffSF_ID_up;
    std::vector<float> *t_Mu_EffSF_ID_down;
    std::vector<float> *t_Mu_EffSF_ISO;
    std::vector<float> *t_Mu_EffSF_ISO_up;
    std::vector<float> *t_Mu_EffSF_ISO_down;
    std::vector<float> *t_Mu_pt;
    std::vector<float> *t_Mu_ptErr;
    std::vector<float> *t_Mu_bsConstrainedPt;
    std::vector<float> *t_Mu_bsConstrainedPtErr;
    std::vector<float> *t_Mu_bsConstrainedPt_nanoAOD;
    std::vector<float> *t_Mu_bsConstrainedPtErr_nanoAOD;
    std::vector<float> *t_Mu_phi;
    std::vector<float> *t_Mu_eta;
    std::vector<float> *t_Mu_mass;
    std::vector<float> *t_Mu_dxy;
    std::vector<float> *t_Mu_dxyErr;
    std::vector<float> *t_Mu_dz;
    std::vector<float> *t_Mu_dzErr;
    std::vector<float> *t_Mu_sip3d;
    std::vector<float> *t_Mu_pfRelIso03_all;
    std::vector<float> *t_Mu_pfRelIso03_chg;
    std::vector<float> *t_Mu_pfRelIso04_all;
    std::vector<float> *t_Mu_miniPFRelIso_all;
    std::vector<float> *t_Mu_miniPFRelIso_chg;
    std::vector<int> *t_Mu_tightCharge;
    std::vector<bool> *t_Mu_isPFcand;
    std::vector<bool> *t_Mu_istracker;
    std::vector<bool> *t_Mu_isglobal;
    std::vector<bool> *t_Mu_looseId;
    std::vector<bool> *t_Mu_mediumId;
    std::vector<bool> *t_Mu_softId;
    std::vector<bool> *t_Mu_tightId;
    std::vector<int> *t_Mu_nStations;
    std::vector<int> *t_Mu_nTrackerLayers;

    float t_diMuon_pt;
    float t_diMuon_bsConstrainedPt;
    float t_diMuon_eta;
    float t_diMuon_phi;
    float t_diMuon_mass;
    float t_diMuon_bsConstrainedMass;

    float t_PuppiMET_phi;
    float t_PuppiMET_pt;
    float t_PuppiMET_sumEt;

    std::vector<float> *t_FatJet_area;
    std::vector<float> *t_FatJet_btagCMVA;
    std::vector<float> *t_FatJet_btagCSVV2;
    std::vector<float> *t_FatJet_btagDeepB;
    std::vector<float> *t_FatJet_eta;
    std::vector<float> *t_FatJet_mass;
    std::vector<float> *t_FatJet_msoftdrop;
    std::vector<float> *t_FatJet_n2b1;
    std::vector<float> *t_FatJet_n3b1;
    std::vector<float> *t_FatJet_phi;
    std::vector<float> *t_FatJet_pt;
    std::vector<float> *t_FatJet_tau1;
    std::vector<float> *t_FatJet_tau2;
    std::vector<float> *t_FatJet_tau3;
    std::vector<float> *t_FatJet_tau4;
    //std::vector<int> *t_FatJet_jetId;
    std::vector<int> *t_FatJet_subJetIdx1;
    std::vector<int> *t_FatJet_subJetIdx2;

    std::vector<float> *t_SubJet_btagCMVA;
    std::vector<float> *t_SubJet_btagCSVV2;
    std::vector<float> *t_SubJet_btagDeepB;
    std::vector<float> *t_SubJet_eta;
    std::vector<float> *t_SubJet_mass;
    std::vector<float> *t_SubJet_n2b1;
    std::vector<float> *t_SubJet_n3b1;
    std::vector<float> *t_SubJet_phi;
    std::vector<float> *t_SubJet_pt;
    std::vector<float> *t_SubJet_tau1;
    std::vector<float> *t_SubJet_tau2;
    std::vector<float> *t_SubJet_tau3;
    std::vector<float> *t_SubJet_tau4;
    

    int t_leadJet_idx;
    int t_subleadJet_idx;

    int t_nJet;
    std::vector<float> *t_Jet_area;
    // std::vector<float>         *t_Jet_btagCMVA;
    // std::vector<float>         *t_Jet_btagCSVV2;
    std::vector<float> *t_Jet_btagDeepB;
    std::vector<float> *t_Jet_btagPNetB;
    // std::vector<float>         *t_Jet_btagDeepC;
    // std::vector<float>         *t_Jet_btagDeepFlavB;
    std::vector<float> *t_Jet_chEmEF;
    std::vector<float> *t_Jet_chHEF;
    std::vector<float> *t_Jet_eta;
    std::vector<float> *t_Jet_mass;
    std::vector<float> *t_Jet_mass_nanoAOD;
    std::vector<float> *t_Jet_neEmEF;
    std::vector<float> *t_Jet_neHEF;
    std::vector<float> *t_Jet_phi;
    std::vector<float> *t_Jet_pt;
    std::map<std::string, std::vector<float> *> t_Jet_pt_jes_syst;
    std::map<std::string, std::vector<float> *> t_Jet_pt_jer_syst;
    std::map<std::string, std::vector<float> *> t_Jet_mass_jes_syst;
    std::map<std::string, std::vector<float> *> t_Jet_mass_jer_syst;
    std::vector<float> *t_Jet_pt_nanoAOD;
    std::vector<float> *t_Jet_qgl;
    std::vector<int> *t_Jet_jetId;
    std::vector<int> *t_Jet_chMultiplicity;
    std::vector<int> *t_Jet_neMultiplicity;
    std::vector<int> *t_Jet_nConstituents;
    std::vector<int> *t_Jet_nElectrons;
    std::vector<int> *t_Jet_nMuons;
    std::vector<int> *t_Jet_puId;

    int t_nSoftActivityJet;
    int t_SoftActivityJetNjets10;
    int t_SoftActivityJetNjets2;
    int t_SoftActivityJetNjets5;
    float t_SoftActivityJetHT;
    float t_SoftActivityJetHT10;
    float t_SoftActivityJetHT2;
    float t_SoftActivityJetHT5;
    float t_diJet_pt;
    float t_diJet_eta;
    float t_diJet_phi;
    float t_diJet_mass;
    float t_diJet_mass_mo;

    int t_nbJet;
    int t_nbJet_Loose;
    std::vector<float> *t_bJet_area;
    std::vector<float> *t_bJet_btagDeepB;
    std::vector<float> *t_bJet_btagPNetB;
    std::vector<float> *t_bJet_chEmEF;
    std::vector<float> *t_bJet_chHEF;
    std::vector<float> *t_bJet_eta;
    std::vector<float> *t_bJet_mass;
    std::vector<float> *t_bJet_neEmEF;
    std::vector<float> *t_bJet_neHEF;
    std::vector<float> *t_bJet_phi;
    std::vector<float> *t_bJet_pt;
    std::vector<float> *t_bJet_qgl;
    std::vector<int> *t_bJet_jetId;
    std::vector<int> *t_bJet_chMultiplicity;
    std::vector<int> *t_bJet_neMultiplicity;
    std::vector<int> *t_bJet_nConstituents;
    std::vector<int> *t_bJet_nElectrons;
    std::vector<int> *t_bJet_nMuons;
    std::vector<int> *t_bJet_puId;
    std::vector<double> *t_bJet_SF;
    std::vector<double> *t_bJet_SFup;
    std::vector<double> *t_bJet_SFdown;

    float t_PV_ndof;
    float t_PV_x;
    float t_PV_y;
    float t_PV_z;
    int t_PV_npvs;
    int t_PV_npvsGood;

    float t_Rho; // Rho_fixedGridRhoFastjetAll

    std::vector<float> *t_GenPart_eta;
    std::vector<float> *t_GenPart_mass;
    std::vector<float> *t_GenPart_phi;
    std::vector<float> *t_GenPart_pt;
    std::vector<int> *t_GenPart_genPartIdxMother;
    std::vector<int> *t_GenPart_pdgId;
    std::vector<int> *t_GenPart_status;

    std::vector<float> *t_GenJet_eta;
    std::vector<float> *t_GenJet_mass;
    std::vector<float> *t_GenJet_phi;
    std::vector<float> *t_GenJet_pt;

};

#endif

#ifdef HmmAnalyzer_cxx
HmmAnalyzer::HmmAnalyzer(const TString &inputFileList, const char *outFileName,
                         TString dataset, bool is_data_input, TString year_num, 
                         bool include_Z_, bool include_H_) {
    // if parameter tree is not specified (or zero), connect the file
    // used to generate this class and read the Tree.

    is_data = is_data_input;
    year = year_num;
    include_Z = include_Z_;
    include_H = include_H_;
    muon_pt_syst = "nominal";
    apply_muon_pt_syst_to_signal = false;
    yearst = std::string(year.Data());
    
    if(include_Z){
        std::cout << "Z range included" << std::endl;
    }
    if(include_H){
        std::cout << "H range included" << std::endl;
    }


    h_sumOfgw->SetBinContent(1, 0.0);
    h_sumOfgpw->SetBinContent(1, 0.0);
    h_pileup->SetBinContent(1, 0.0);
    h_pileup_nTrue->SetBinContent(1, 0.0);

    // muon pT selection
    muon_pt_cut["2016"] = 26.0;
    // muon_pt_cut["2017"] = 29.0;
    // muon_pt_cut["2018"] = 26.0;
    muon_pt_cut["2022"] = 26.0;
    muon_pt_cut["2022EE"] = 26.0;
    muon_pt_cut["2023"] = 26.0;
    muon_pt_cut["2023BPix"] = 26.0;
    muon_pt_cut["2024"] = 26.0;
    muon_pt_cut["2025"] = 26.0;

    // Define b-tagging scores
    // b-tag particleNet LOOSE score selection
    btagLoose_cut["2022"] = 0.047;
    btagLoose_cut["2022EE"] = 0.0499;
    btagLoose_cut["2023"] = 0.0358;
    btagLoose_cut["2023BPix"] = 0.0359;
    btagLoose_cut["2024"] = 0.0365;
    btagLoose_cut["2025"] = 0.0365;// 2025 values NEED to be checked

    // b-tag deepFlav MEDIUM score selection
    btagMedium_cut["2016"] = 0.6321;
    // btagMedium_cut["2017"] = 0.4941;
    // btagMedium_cut["2018"] = 0.4184;
    // b-tag particleNet MEDIUM score selection
    btagMedium_cut["2022"] = 0.245;
    btagMedium_cut["2022EE"] = 0.2605;
    btagMedium_cut["2023"] = 0.1917;
    btagMedium_cut["2023BPix"] = 0.1919;
    btagMedium_cut["2024"] = 0.1990;
    btagMedium_cut["2025"] = 0.1990; // 2025 values NEED to be checked

    if (!is_data) {
        getPileupHistograms();
    }

    TChain *tree = new TChain("Events");

    if (!FillChain(tree, inputFileList)) {
        std::cerr << "Cannot get the tree " << std::endl;
    } else {
        std::cout << "Initiating analysis of dataset " << dataset << std::endl;
        if (is_data)
            std::cout << "Initiating analysis on Data" << endl;
        else
            std::cout << "Initiating analysis on MC" << endl;
    }

    std::cout << "NanoAOD Version: " << NANOAOD_VERSION.at(year) << std::endl;
    MainEvent::Init(tree, NANOAOD_VERSION.at(year));
    //tree->Scan("Jet_jetId","","",5);
    if (!is_data) {
        MainEvent::InitSimulationVariables(tree);
    }
    oFile = new TFile(outFileName, "recreate");
    TString histname(outFileName);
    // ohistFile = new TFile("hist_"+histname, "recreate");
    BookTreeBranches();
}

void HmmAnalyzer::getPileupHistograms() {
    std::cout << "Looking for pileup hists file\n";
    if (yearst == "2022") {
        pileupWeightFile =
            new TFile("./data/pileup/PileupReweight_Summer22.root");
    } else if (yearst == "2022EE") {
        pileupWeightFile =
            new TFile("./data/pileup/PileupReweight_Summer22EE.root");
    } else if (yearst == "2023") {
        pileupWeightFile =
            new TFile("./data/pileup/PileupReweight_Summer23.root");
    } else if (yearst == "2023BPix") {
        pileupWeightFile =
            new TFile("./data/pileup/PileupReweight_Summer23BPix.root");
    } else if (yearst == "2024") {
        pileupWeightFile =
            new TFile("./data/pileup/PileupReweight_Summer24.root");
    } else if (yearst == "2025") {
        pileupWeightFile =
            new TFile("./data/pileup/PileupReweight_Summer25.root");
    }
    if (pileupWeightFile) {
        pileupWeightHist = (TH1F *)pileupWeightFile->Get("npu_nominal");
        pileupWeightSysUpHist = (TH1F *)pileupWeightFile->Get("npu_up");
        pileupWeightSysDownHist = (TH1F *)pileupWeightFile->Get("npu_down");
    } else {
        std::cerr << "Pileup file didn't found" << std::endl;
    }
    std::cout << "Done with getting pileup histograms!\n";
}

float HmmAnalyzer::getPileupWeight(int NPU) {
    if (pileupWeightHist) {
        return pileupWeightHist->GetBinContent(
            pileupWeightHist->GetXaxis()->FindFixBin(NPU));
    } else {
        std::cout
            << "error: pileup weight requested, but no histogram available!"
            << std::endl;
        return 0;
    }
}

float HmmAnalyzer::getPileupWeightUp(int NPU) {
    if (pileupWeightSysUpHist) {
        return pileupWeightSysUpHist->GetBinContent(
            pileupWeightSysUpHist->GetXaxis()->FindFixBin(NPU));
    } else {
        std::cout << "error: 'up' pileup weight requested, but no histogram "
                     "available!"
                  << std::endl;
        return 0;
    }
}

float HmmAnalyzer::getPileupWeightDown(int NPU) {
    if (pileupWeightSysDownHist) {
        return pileupWeightSysDownHist->GetBinContent(
            pileupWeightSysDownHist->GetXaxis()->FindFixBin(NPU));
    } else {
        std::cout << "error: 'down' pileup weight requested, but no histogram "
                     "available!"
                  << std::endl;
        return 0;
    }
}

//bool HmmAnalyzer::passesJetPtSelection(int index, float corrected_pt) {
    //if (yearst == "2022" || yearst == "2022EE" || yearst == "2023" || yearst == "2023BPix"){
        //if (fabs(Jet_eta[index]) < 2.5){
            //return true;
        //}
        //else if (fabs(Jet_eta[index]) < 5){
            //return (corrected_pt > 50);
        //}

    //} else if (yearst == "2024"){
        //if (fabs(Jet_eta[index]) < 2.5){ //TODO: Fix this
            //return true;
        //}
        //else if (fabs(Jet_eta[index]) < 3){
            //return (corrected_pt > 50);
        //}
        //else {
            //return true;
        //}
    //} else if (yearst == "2025"){
        //return true;

    //} else {
        //std::cerr << "Jet pT era not found" << std::endl;
        //return false;
    //}
//}

bool HmmAnalyzer::isValidJet(int index, float corrected_pt) {
    bool Jet_passJetIdTight = false;
    bool Jet_passJetIdTightLepVeto = false;
    if(NANOAOD_VERSION.at(year) == "v12"){ //nanoAODv12
        //std::cout << "Running v12" << std::endl;
        if (fabs(Jet_eta[index]) <= 2.7) Jet_passJetIdTight = Jet_jetId[index] & (1 << 1);
        else if (fabs(Jet_eta[index]) > 2.7 && fabs(Jet_eta[index]) <= 3.0) Jet_passJetIdTight = (Jet_jetId[index] & (1 << 1)) && (Jet_neHEF[index] < 0.99);
        else if (fabs(Jet_eta[index]) > 3.0) Jet_passJetIdTight = (Jet_jetId[index] & (1 << 1)) && (Jet_neEmEF[index] < 0.4);
        
        if (abs(Jet_eta[index]) <= 2.7) Jet_passJetIdTightLepVeto = Jet_passJetIdTight && (Jet_muEF[index] < 0.8) && (Jet_chEmEF[index] < 0.8);
        else Jet_passJetIdTightLepVeto = Jet_passJetIdTight;
    }

    else{ //nanoAODv15
        //std::cout << "Running v15" << std::endl;
        if (fabs(Jet_eta[index]) <= 2.6){
            Jet_passJetIdTight = (Jet_neHEF[index] < 0.99) && (Jet_neEmEF[index] < 0.9) && (Jet_chMultiplicity[index]+Jet_neMultiplicity[index] > 1) && 
             (Jet_chHEF[index] > 0.01) && (Jet_chMultiplicity[index] > 0);
        }
        else if (fabs(Jet_eta[index]) > 2.6 && abs(Jet_eta[index]) <= 2.7){
            Jet_passJetIdTight = (Jet_neHEF[index] < 0.90) && (Jet_neEmEF[index] < 0.99);
        }
        else if (fabs(Jet_eta[index]) > 2.7 && fabs(Jet_eta[index]) <= 3.0){
            Jet_passJetIdTight = (Jet_neHEF[index] < 0.99);
        }
        else if (fabs(Jet_eta[index]) > 3.0){
            Jet_passJetIdTight = (Jet_neMultiplicity[index] >= 2) && (Jet_neEmEF[index] < 0.4);
        }
        
        if (abs(Jet_eta[index]) <= 2.7) 
           Jet_passJetIdTightLepVeto = Jet_passJetIdTight && (Jet_muEF[index] < 0.8) && (Jet_chEmEF[index] < 0.8);
        else 
           Jet_passJetIdTightLepVeto = Jet_passJetIdTight;
    }

    return (corrected_pt > 15. && fabs(Jet_eta[index]) < 4.7 &&
            Jet_passJetIdTightLepVeto /* && Jet_puId[index]>=1 */);
}

bool HmmAnalyzer::FillChain(TChain *chain, const TString &inputFileList) {

    ifstream infile(inputFileList, ifstream::in);
    std::string buffer;

    if (!infile.is_open()) {
        std::cerr << "** ERROR: Can't open '" << inputFileList << "' for input"
                  << std::endl;
        return kFALSE;
    }

    std::cout << "TreeUtilities : FillChain " << std::endl;

    while (getline(infile, buffer)) {
        std::cout << "Adding tree from " << buffer.c_str() << std::endl;
        chain->Add(buffer.c_str());
        // if(!is_data){
        //   std::string friend_buffer = "";

        //   std::string delimiter = "/";

        //   size_t pos = 0;
        //   std::string buffer_f =
        //   "/storage/user/nlu/Hmm/puJEC/"+yearst+"/17July_v1/";
        //   //"/mnt/hadoop/store/user/nlu/Hmm/ntuple/2016/Nano14Dec2018/MC/puJEC/16June_v1/";
        //   std::string buffer_tmp = buffer;
        //   int dataname_pos = 7;
        //   if(buffer.find("storage")!=std::string::npos) dataname_pos = 8;
        //   int cout=0;
        //   while ((pos = buffer_tmp.find(delimiter)) != std::string::npos) {
        //      cout++;
        //      friend_buffer = buffer_tmp.substr(0, pos);
        //      std::cout <<"friend_buffer: "<<friend_buffer << std::endl;
        //      if(cout==dataname_pos){ //8 for storage
        //             buffer_f +=friend_buffer;
        //      }
        //      buffer_tmp.erase(0, pos + delimiter.length());
        //   }
        //   std::cout << friend_buffer << std::endl;
        //   std::cout << "buffer_tmp: "<<buffer_tmp << std::endl;

        //   buffer_f += buffer_tmp;
        //   std::cout << "Adding friend tree from " << buffer_f.c_str() <<
        //   std::endl; chain->AddFriend("Friends",buffer_f.c_str());
        // }
    }
    infile.close();

    std::cout << "No. of Entries in this tree : " << chain->GetEntries()
              << std::endl;

    return kTRUE;
}

HmmAnalyzer::~HmmAnalyzer() {
    if (!fChain)
        return;
    delete fChain->GetCurrentFile();
    oFile->cd();
    h_sumOfgw->Write();
    h_sumOfgpw->Write();
    h_pileup->Write();
    h_pileup_nTrue->Write();

    h_nEntries->Write();
    h_nTrigger->Write();
    h_nTwoMuons->Write();
    h_nNoExtraMuon->Write();
    h_nNoExtraElectron->Write();
    h_nTriggerMatch->Write();
    h_nInMassRegion->Write();
    h_nBjetRejection->Write();
    h_nInZPeak->Write();

    //jet tests
    h_nJets->Write();
    h_nValidJets->Write();
    h_nValidSeperatedJets->Write();
    h_nValidNotVetoedJets->Write();
    
    oFile->Write();
    oFile->Close();
    if (!is_data) {
        pileupWeightFile->Close();
    }
}

Long64_t HmmAnalyzer::LoadTree(Long64_t entry) {
    // Set the environment to read one entry
    if (!fChain)
        return -5;
    Long64_t centry = fChain->LoadTree(entry);
    if (centry < 0)
        return centry;
    if (fChain->GetTreeNumber() != fCurrent) {
        fCurrent = fChain->GetTreeNumber();
        Notify();
    }
    return centry;
}

void HmmAnalyzer::clearTreeVectors() {
    t_run = 0;
    t_luminosityBlock = 0;
    t_event = 0;
    t_genWeight = FLOAT_NULL_VALUE;
    t_pileup = FLOAT_NULL_VALUE;
    t_puWeight = FLOAT_NULL_VALUE;
    t_puWeightUp = FLOAT_NULL_VALUE;
    t_puWeightDown = FLOAT_NULL_VALUE;
    t_PrefireWeight = 1.0;
    t_PrefireWeight_Up = 1.0;
    t_PrefireWeight_Down = 1.0;
    t_mu1 = FLOAT_NULL_VALUE;
    t_mu2 = FLOAT_NULL_VALUE;
    t_index_trigm_mu = FLOAT_NULL_VALUE;
    t_nJet = 0;
    t_nbJet = 0;
    t_nbJet_Loose = 0;
    t_nSoftActivityJet = INT_NULL_VALUE;
    t_SoftActivityJetNjets10 = INT_NULL_VALUE;
    t_SoftActivityJetNjets2 = INT_NULL_VALUE;
    t_SoftActivityJetNjets5 = INT_NULL_VALUE;
    t_SoftActivityJetHT = FLOAT_NULL_VALUE;
    t_SoftActivityJetHT10 = FLOAT_NULL_VALUE;
    t_SoftActivityJetHT2 = FLOAT_NULL_VALUE;
    t_SoftActivityJetHT5 = FLOAT_NULL_VALUE;
    t_El_genPartIdx->clear();
    t_El_genPartFlav->clear();
    t_El_charge->clear();
    t_El_pt->clear();
    t_El_phi->clear();
    t_El_eta->clear();
    t_El_mass->clear();
    t_El_cutBased->clear();
    t_El_tightCharge->clear();
    t_El_cutBased_HEEP->clear();
    t_El_isPFcand->clear();
    t_El_pfRelIso03_all->clear();
    t_El_pfRelIso03_chg->clear();
    t_El_miniPFRelIso_all->clear();
    t_El_miniPFRelIso_chg->clear();
    t_El_dxy->clear();
    t_El_dxyErr->clear();
    t_El_dz->clear();
    t_El_dzErr->clear();
    t_El_sip3d->clear();
    t_Electron_mvaFall17Iso->clear();
    t_Electron_mvaFall17Iso_WP80->clear();
    t_Electron_mvaFall17Iso_WP90->clear();
    t_Electron_mvaFall17Iso_WPL->clear();
    t_Electron_mvaFall17noIso->clear();
    t_Electron_mvaFall17noIso_WP80->clear();
    t_Electron_mvaFall17noIso_WP90->clear();
    t_Electron_mvaFall17noIso_WPL->clear();

    t_Mu_genPartIdx->clear();
    t_Mu_genPartFlav->clear();
    t_Mu_charge->clear();
    //t_Mu_EffSF_TRIG->clear();
    //t_Mu_EffSF_TRIG_up->clear();
    //t_Mu_EffSF_TRIG_down->clear();
    
    t_Mu_EffTRIG_DATA->clear();
    t_Mu_EffTRIG_DATA_up->clear();
    t_Mu_EffTRIG_DATA_down->clear();
    t_Mu_EffTRIG_MC->clear();
    t_Mu_EffTRIG_MC_up->clear();
    t_Mu_EffTRIG_MC_down->clear();

    t_Mu_EffSF_ID->clear();
    t_Mu_EffSF_ID_up->clear();
    t_Mu_EffSF_ID_down->clear();
    t_Mu_EffSF_ISO->clear();
    t_Mu_EffSF_ISO_up->clear();
    t_Mu_EffSF_ISO_down->clear();
    t_Mu_pt->clear();
    t_Mu_ptErr->clear();
    t_Mu_bsConstrainedPt->clear();
    t_Mu_bsConstrainedPtErr->clear();
    t_Mu_bsConstrainedPt_nanoAOD->clear();
    t_Mu_bsConstrainedPtErr_nanoAOD->clear();
    t_Mu_phi->clear();
    t_Mu_eta->clear();
    t_Mu_mass->clear();
    t_Mu_dxy->clear();
    t_Mu_dxyErr->clear();
    t_Mu_dz->clear();
    t_Mu_dzErr->clear();
    t_Mu_sip3d->clear();
    t_Mu_pfRelIso03_all->clear();
    t_Mu_pfRelIso03_chg->clear();
    t_Mu_pfRelIso04_all->clear();
    t_Mu_miniPFRelIso_all->clear();
    t_Mu_miniPFRelIso_chg->clear();
    t_Mu_tightCharge->clear();
    t_Mu_isPFcand->clear();
    t_Mu_isglobal->clear();
    t_Mu_istracker->clear();
    t_Mu_looseId->clear();
    t_Mu_mediumId->clear();
    t_Mu_softId->clear();
    t_Mu_tightId->clear();
    t_Mu_nStations->clear();
    t_Mu_nTrackerLayers->clear();

    t_diMuon_pt = FLOAT_NULL_VALUE;
    t_diMuon_bsConstrainedPt = FLOAT_NULL_VALUE;
    t_diMuon_eta = FLOAT_NULL_VALUE;
    t_diMuon_phi = FLOAT_NULL_VALUE;
    t_diMuon_mass = FLOAT_NULL_VALUE;
    t_diMuon_bsConstrainedMass = FLOAT_NULL_VALUE;

    t_PuppiMET_phi = FLOAT_NULL_VALUE;
    t_PuppiMET_pt = FLOAT_NULL_VALUE;
    t_PuppiMET_sumEt = FLOAT_NULL_VALUE;

    t_FatJet_area->clear();
    t_FatJet_btagCMVA->clear();
    t_FatJet_btagCSVV2->clear();
    t_FatJet_btagDeepB->clear();
    t_FatJet_eta->clear();
    t_FatJet_mass->clear();
    t_FatJet_msoftdrop->clear();
    t_FatJet_n2b1->clear();
    t_FatJet_n3b1->clear();
    t_FatJet_phi->clear();
    t_FatJet_pt->clear();
    t_FatJet_tau1->clear();
    t_FatJet_tau2->clear();
    t_FatJet_tau3->clear();
    t_FatJet_tau4->clear();
    //t_FatJet_jetId->clear();
    t_FatJet_subJetIdx1->clear();
    t_FatJet_subJetIdx2->clear();

    t_SubJet_btagCMVA->clear();
    t_SubJet_btagCSVV2->clear();
    t_SubJet_btagDeepB->clear();
    t_SubJet_eta->clear();
    t_SubJet_mass->clear();
    t_SubJet_n2b1->clear();
    t_SubJet_n3b1->clear();
    t_SubJet_phi->clear();
    t_SubJet_pt->clear();
    t_SubJet_tau1->clear();
    t_SubJet_tau2->clear();
    t_SubJet_tau3->clear();
    t_SubJet_tau4->clear();


    t_leadJet_idx = INT_NULL_VALUE;
    t_subleadJet_idx = INT_NULL_VALUE;
    t_Jet_area->clear();
    // t_Jet_btagCMVA->clear();
    // t_Jet_btagCSVV2->clear();
    t_Jet_btagDeepB->clear();
    t_Jet_btagPNetB->clear();
    // t_Jet_btagDeepC->clear();
    // t_Jet_btagDeepFlavB->clear();
    t_Jet_chEmEF->clear();
    t_Jet_chHEF->clear();
    t_Jet_eta->clear();
    t_Jet_mass->clear();
    t_Jet_mass_nanoAOD->clear();
    t_Jet_neEmEF->clear();
    t_Jet_neHEF->clear();
    t_Jet_phi->clear();
    t_Jet_pt->clear();
    for (auto &entry : t_Jet_pt_jes_syst) {
        entry.second->clear();
    }
    for (auto &entry : t_Jet_pt_jer_syst) {
        entry.second->clear();
    }
    for (auto &entry : t_Jet_mass_jes_syst) {
        entry.second->clear();
    }
    for (auto &entry : t_Jet_mass_jer_syst) {
        entry.second->clear();
    }
    t_Jet_pt_nanoAOD->clear();
    t_Jet_qgl->clear();
    t_Jet_jetId->clear();
    t_Jet_chMultiplicity->clear();
    t_Jet_neMultiplicity->clear();
    t_Jet_nConstituents->clear();
    t_Jet_nElectrons->clear();
    t_Jet_nMuons->clear();
    t_Jet_puId->clear();

    t_diJet_pt = FLOAT_NULL_VALUE;
    t_diJet_eta = FLOAT_NULL_VALUE;
    t_diJet_phi = FLOAT_NULL_VALUE;
    t_diJet_mass = FLOAT_NULL_VALUE;
    t_diJet_mass_mo = FLOAT_NULL_VALUE;

    t_bJet_area->clear();
    t_bJet_btagDeepB->clear();
    t_bJet_btagPNetB->clear();
    t_bJet_chEmEF->clear();
    t_bJet_chHEF->clear();
    t_bJet_eta->clear();
    t_bJet_mass->clear();
    t_bJet_neEmEF->clear();
    t_bJet_neHEF->clear();
    t_bJet_phi->clear();
    t_bJet_pt->clear();
    t_bJet_qgl->clear();
    t_bJet_jetId->clear();
    t_bJet_chMultiplicity->clear();
    t_bJet_neMultiplicity->clear();
    t_bJet_nConstituents->clear();
    t_bJet_nElectrons->clear();
    t_bJet_nMuons->clear();
    t_bJet_puId->clear();
    t_bJet_SF->clear();
    t_bJet_SFup->clear();
    t_bJet_SFdown->clear();

    // SoftActivityJetHT5
    // SoftActivityJetNjets5

    t_PV_ndof = -1000;
    t_PV_x = -1000;
    t_PV_y = -1000;
    t_PV_z = -1000;
    t_PV_npvs = -1000;
    t_PV_npvsGood = -1000;

    t_Rho = FLOAT_NULL_VALUE;

    t_GenPart_eta->clear();
    t_GenPart_mass->clear();
    t_GenPart_phi->clear();
    t_GenPart_pt->clear();
    t_GenPart_genPartIdxMother->clear();
    t_GenPart_pdgId->clear();
    t_GenPart_status->clear();

    t_GenJet_eta->clear();
    t_GenJet_mass->clear();
    t_GenJet_phi->clear();
    t_GenJet_pt->clear();
}

void HmmAnalyzer::BookTreeBranches() {
    tree = new TTree("tree", "tree");
    tree->SetAutoSave(10000);

    tree->Branch("t_run", &t_run, "t_run/i");
    tree->Branch("t_luminosityBlock", &t_luminosityBlock,
                 "t_luminosityBlock/i");
    tree->Branch("t_event", &t_event, "t_event/l");
    tree->Branch("t_genWeight", &t_genWeight, "t_genWeight/F");
    tree->Branch("t_pileup", &t_pileup, "t_pileup/F");
    tree->Branch("t_puWeight", &t_puWeight, "t_puWeight/F");
    tree->Branch("t_puWeightUp", &t_puWeightUp, "t_puWeightUp/F");
    tree->Branch("t_puWeightDown", &t_puWeightDown, "t_puWeightDown/F");
    // tree->Branch("t_pileupWeight", &t_pileupWeight,"t_pileupWeight/F");
    // tree->Branch("t_pileupupWeight", &t_pileupupWeight,"t_pileupupWeight/F");
    // tree->Branch("t_pileupdnWeight", &t_pileupdnWeight,"t_pileupdnWeight/F");
    tree->Branch("t_PrefireWeight", &t_PrefireWeight, "t_PrefireWeight/F");
    tree->Branch("t_PrefireWeight_Up", &t_PrefireWeight_Up,
                 "t_PrefireWeight_Up/F");
    tree->Branch("t_PrefireWeight_Down", &t_PrefireWeight_Down,
                 "t_PrefireWeight_Down/F");
    tree->Branch("t_mu1", &t_mu1, "t_mu1/I");
    tree->Branch("t_mu2", &t_mu2, "t_mu2/I");
    tree->Branch("t_index_trigm_mu", &t_index_trigm_mu, "t_index_trigm_mu/I");

    t_El_genPartIdx = new std::vector<int>();
    t_El_genPartFlav = new std::vector<UChar_t>();
    t_El_charge = new std::vector<int>();
    t_El_pt = new std::vector<float>();
    t_El_phi = new std::vector<float>();
    t_El_eta = new std::vector<float>();
    t_El_mass = new std::vector<float>();
    t_El_cutBased = new std::vector<int>();
    t_El_tightCharge = new std::vector<int>();
    t_El_cutBased_HEEP = new std::vector<bool>();
    t_El_isPFcand = new std::vector<bool>();
    t_El_pfRelIso03_all = new std::vector<float>();
    t_El_pfRelIso03_chg = new std::vector<float>();
    t_El_miniPFRelIso_all = new std::vector<float>();
    t_El_miniPFRelIso_chg = new std::vector<float>();
    t_El_dxy = new std::vector<float>();
    t_El_dxyErr = new std::vector<float>();
    t_El_dz = new std::vector<float>();
    t_El_dzErr = new std::vector<float>();
    t_El_sip3d = new std::vector<float>();
    t_Electron_mvaFall17Iso = new std::vector<float>();
    t_Electron_mvaFall17Iso_WP80 = new std::vector<bool>(); //[nElectron]
    t_Electron_mvaFall17Iso_WP90 = new std::vector<bool>(); //[nElectron]
    t_Electron_mvaFall17Iso_WPL = new std::vector<bool>();  //[nElectron]
    t_Electron_mvaFall17noIso = new std::vector<float>();
    t_Electron_mvaFall17noIso_WP80 = new std::vector<bool>(); //[nElectron]
    t_Electron_mvaFall17noIso_WP90 = new std::vector<bool>(); //[nElectron]
    t_Electron_mvaFall17noIso_WPL = new std::vector<bool>();  //[nElectron]

    tree->Branch("t_El_genPartIdx", "vector<int>", &t_El_genPartIdx);
    tree->Branch("t_El_genPartFlav", "vector<UChar_t>", &t_El_genPartFlav);
    tree->Branch("t_El_charge", "vector<int>", &t_El_charge);
    tree->Branch("t_El_pt", "vector<float>", &t_El_pt);
    tree->Branch("t_El_phi", "vector<float>", &t_El_phi);
    tree->Branch("t_El_eta", "vector<float>", &t_El_eta);
    tree->Branch("t_El_mass", "vector<float>", &t_El_mass);
    tree->Branch("t_El_cutBased", "vector<int>", &t_El_cutBased);
    tree->Branch("t_El_tightCharge", "vector<int>", &t_El_tightCharge);
    tree->Branch("t_El_cutBased_HEEP", "vector<bool>", &t_El_cutBased_HEEP);
    tree->Branch("t_El_isPFcand", "vector<bool>", &t_El_isPFcand);
    tree->Branch("t_El_pfRelIso03_all", "vector<float>", &t_El_pfRelIso03_all);
    tree->Branch("t_El_pfRelIso03_chg", "vector<float>", &t_El_pfRelIso03_chg);
    tree->Branch("t_El_miniPFRelIso03_all", "vector<float>",
                 &t_El_miniPFRelIso_all);
    tree->Branch("t_El_miniPFRelIso03_chg", "vector<float>",
                 &t_El_miniPFRelIso_chg);
    tree->Branch("t_El_dxy", "vector<float>", &t_El_dxy);
    tree->Branch("t_El_dxyErr", "vector<float>", &t_El_dxyErr);
    tree->Branch("t_El_dz", "vector<float>", &t_El_dz);
    tree->Branch("t_El_dzErr", "vector<float>", &t_El_dzErr);
    tree->Branch("t_El_sip3d", "vector<float>", &t_El_sip3d);
    tree->Branch("t_Electron_mvaFall17Iso", "vector<float>",
                 &t_Electron_mvaFall17Iso);
    tree->Branch("t_Electron_mvaFall17Iso_WP80", "vector<bool>",
                 &t_Electron_mvaFall17Iso_WP80);
    tree->Branch("t_Electron_mvaFall17Iso_WP90", "vector<bool>",
                 &t_Electron_mvaFall17Iso_WP90);
    tree->Branch("t_Electron_mvaFall17Iso_WPL", "vector<bool>",
                 &t_Electron_mvaFall17Iso_WPL);
    tree->Branch("t_Electron_mvaFall17noIso", "vector<float>",
                 &t_Electron_mvaFall17noIso);
    tree->Branch("t_Electron_mvaFall17noIso_WP80", "vector<bool>",
                 &t_Electron_mvaFall17noIso_WP80);
    tree->Branch("t_Electron_mvaFall17noIso_WP90", "vector<bool>",
                 &t_Electron_mvaFall17noIso_WP90);
    tree->Branch("t_Electron_mvaFall17noIso_WPL", "vector<bool>",
                 &t_Electron_mvaFall17noIso_WPL);

    t_Mu_genPartIdx = new std::vector<int>();
    t_Mu_genPartFlav = new std::vector<UChar_t>();
    t_Mu_charge = new std::vector<int>();
    //t_Mu_EffSF_TRIG = new std::vector<float>();
    //t_Mu_EffSF_TRIG_up = new std::vector<float>();
    //t_Mu_EffSF_TRIG_down = new std::vector<float>();
  
    t_Mu_EffTRIG_DATA = new std::vector<float>();
    t_Mu_EffTRIG_DATA_up = new std::vector<float>();
    t_Mu_EffTRIG_DATA_down = new std::vector<float>();
    t_Mu_EffTRIG_MC = new std::vector<float>();
    t_Mu_EffTRIG_MC_up = new std::vector<float>();
    t_Mu_EffTRIG_MC_down = new std::vector<float>();

    t_Mu_EffSF_ID = new std::vector<float>();
    t_Mu_EffSF_ID_up = new std::vector<float>();
    t_Mu_EffSF_ID_down = new std::vector<float>();
    t_Mu_EffSF_ISO = new std::vector<float>();
    t_Mu_EffSF_ISO_up = new std::vector<float>();
    t_Mu_EffSF_ISO_down = new std::vector<float>();
    t_Mu_pt = new std::vector<float>();
    t_Mu_ptErr = new std::vector<float>();
    t_Mu_bsConstrainedPt = new std::vector<float>();
    t_Mu_bsConstrainedPtErr = new std::vector<float>();
    t_Mu_bsConstrainedPt_nanoAOD = new std::vector<float>();
    t_Mu_bsConstrainedPtErr_nanoAOD = new std::vector<float>();
    t_Mu_phi = new std::vector<float>();
    t_Mu_eta = new std::vector<float>();
    t_Mu_mass = new std::vector<float>();
    t_Mu_dxy = new std::vector<float>();
    t_Mu_dxyErr = new std::vector<float>();
    t_Mu_dz = new std::vector<float>();
    t_Mu_dzErr = new std::vector<float>();
    t_Mu_sip3d = new std::vector<float>();
    t_Mu_pfRelIso03_all = new std::vector<float>();
    t_Mu_pfRelIso03_chg = new std::vector<float>();
    t_Mu_pfRelIso04_all = new std::vector<float>();
    t_Mu_miniPFRelIso_all = new std::vector<float>();
    t_Mu_miniPFRelIso_chg = new std::vector<float>();
    t_Mu_tightCharge = new std::vector<int>();
    t_Mu_isPFcand = new std::vector<bool>();
    t_Mu_isglobal = new std::vector<bool>();
    t_Mu_istracker = new std::vector<bool>();
    t_Mu_looseId = new std::vector<bool>();
    t_Mu_mediumId = new std::vector<bool>();
    t_Mu_softId = new std::vector<bool>();
    t_Mu_tightId = new std::vector<bool>();
    t_Mu_nStations = new std::vector<int>();
    t_Mu_nTrackerLayers = new std::vector<int>();

    tree->Branch("t_Mu_genPartIdx", "vector<int>", &t_Mu_genPartIdx);
    tree->Branch("t_Mu_genPartFlav", "vector<UChar_t>", &t_Mu_genPartFlav);
    tree->Branch("t_Mu_charge", "vector<int>", &t_Mu_charge);
    //tree->Branch("t_Mu_EffSF_TRIG", "vector<float>", &t_Mu_EffSF_TRIG);
    //tree->Branch("t_Mu_EffSF_TRIG_up", "vector<float>", &t_Mu_EffSF_TRIG_up);
    //tree->Branch("t_Mu_EffSF_TRIG_down", "vector<float>", &t_Mu_EffSF_TRIG_down);
   
    tree->Branch("t_Mu_EffTRIG_DATA", "vector<float>", &t_Mu_EffTRIG_DATA);
    tree->Branch("t_Mu_EffTRIG_DATA_up", "vector<float>", &t_Mu_EffTRIG_DATA_up);
    tree->Branch("t_Mu_EffTRIG_DATA_down", "vector<float>", &t_Mu_EffTRIG_DATA_down);
    tree->Branch("t_Mu_EffTRIG_MC", "vector<float>", &t_Mu_EffTRIG_MC);
    tree->Branch("t_Mu_EffTRIG_MC_up", "vector<float>", &t_Mu_EffTRIG_MC_up);
    tree->Branch("t_Mu_EffTRIG_MC_down", "vector<float>", &t_Mu_EffTRIG_MC_down);

    tree->Branch("t_Mu_EffSF_ID", "vector<float>", &t_Mu_EffSF_ID);
    tree->Branch("t_Mu_EffSF_ID_up", "vector<float>", &t_Mu_EffSF_ID_up);
    tree->Branch("t_Mu_EffSF_ID_down", "vector<float>", &t_Mu_EffSF_ID_down);
    tree->Branch("t_Mu_EffSF_ISO", "vector<float>", &t_Mu_EffSF_ISO);
    tree->Branch("t_Mu_EffSF_ISO_up", "vector<float>", &t_Mu_EffSF_ISO_up);
    tree->Branch("t_Mu_EffSF_ISO_down", "vector<float>", &t_Mu_EffSF_ISO_down);
    tree->Branch("t_Mu_pt", "vector<float>", &t_Mu_pt);
    tree->Branch("t_Mu_ptErr", "vector<float>", &t_Mu_ptErr);
    tree->Branch("t_Mu_bsConstrainedPt", "vector<float>", &t_Mu_bsConstrainedPt);
    tree->Branch("t_Mu_bsConstrainedPtErr", "vector<float>", &t_Mu_bsConstrainedPtErr);
    tree->Branch("t_Mu_bsConstrainedPt_nanoAOD", "vector<float>", &t_Mu_bsConstrainedPt_nanoAOD);
    tree->Branch("t_Mu_bsConstrainedPtErr_nanoAOD", "vector<float>", &t_Mu_bsConstrainedPtErr_nanoAOD);
    tree->Branch("t_Mu_phi", "vector<float>", &t_Mu_phi);
    tree->Branch("t_Mu_eta", "vector<float>", &t_Mu_eta);
    tree->Branch("t_Mu_mass", "vector<float>", &t_Mu_mass);
    tree->Branch("t_Mu_dxy", "vector<float>", &t_Mu_dxy);
    tree->Branch("t_Mu_dxyErr", "vector<float>", &t_Mu_dxyErr);
    tree->Branch("t_Mu_dz", "vector<float>", &t_Mu_dz);
    tree->Branch("t_Mu_dzErr", "vector<float>", &t_Mu_dzErr);
    tree->Branch("t_Mu_sip3d", "vector<float>", &t_Mu_sip3d);
    tree->Branch("t_Mu_pfRelIso03_all", "vector<float>", &t_Mu_pfRelIso03_all);
    tree->Branch("t_Mu_pfRelIso03_chg", "vector<float>", &t_Mu_pfRelIso03_chg);
    tree->Branch("t_Mu_pfRelIso04_all", "vector<float>", &t_Mu_pfRelIso04_all);
    tree->Branch("t_Mu_miniPFRelIso_all", "vector<float>",
                 &t_Mu_miniPFRelIso_all);
    tree->Branch("t_Mu_miniPFRelIso_chg", "vector<float>",
                 &t_Mu_miniPFRelIso_chg);
    tree->Branch("t_Mu_tightCharge", "vector<int>", &t_Mu_tightCharge);
    tree->Branch("t_Mu_isPFcand", "vector<bool>", &t_Mu_isPFcand);
    tree->Branch("t_Mu_isglobal", "vector<bool>", &t_Mu_isglobal);
    tree->Branch("t_Mu_istracker", "vector<bool>", &t_Mu_istracker);
    tree->Branch("t_Mu_looseId", "vector<bool>", &t_Mu_looseId);
    tree->Branch("t_Mu_mediumId", "vector<bool>", &t_Mu_mediumId);
    tree->Branch("t_Mu_softId", "vector<bool>", &t_Mu_softId);
    tree->Branch("t_Mu_tightId", "vector<bool>", &t_Mu_tightId);
    tree->Branch("t_Mu_nStations", "vector<int>", &t_Mu_nStations);
    tree->Branch("t_Mu_nTrackerLayers", "vector<int>", &t_Mu_nTrackerLayers);

    tree->Branch("t_diMuon_pt", &t_diMuon_pt, "t_diMuon_pt/F");
    tree->Branch("t_diMuon_bsConstrainedPt", &t_diMuon_bsConstrainedPt, "t_diMuon_bsConstrainedPt/F");
    tree->Branch("t_diMuon_eta", &t_diMuon_eta, "t_diMuon_eta/F");
    tree->Branch("t_diMuon_phi", &t_diMuon_phi, "t_diMuon_phi/F");
    tree->Branch("t_diMuon_mass", &t_diMuon_mass, "t_diMuon_mass/F");
    tree->Branch("t_diMuon_bsConstrainedMass", &t_diMuon_bsConstrainedMass, "t_diMuon_bsConstrainedMass/F");

    tree->Branch("t_PuppiMET_phi", &t_PuppiMET_phi, "t_PuppiMET_phi/F");
    tree->Branch("t_PuppiMET_pt", &t_PuppiMET_pt, "t_PuppiMET_pt/F");
    tree->Branch("t_PuppiMET_sumEt", &t_PuppiMET_sumEt, "t_PuppiMET_sumEt/F");

    t_FatJet_area = new std::vector<float>();
    t_FatJet_btagCMVA = new std::vector<float>();
    t_FatJet_btagCSVV2 = new std::vector<float>();
    t_FatJet_btagDeepB = new std::vector<float>();
    t_FatJet_eta = new std::vector<float>();
    t_FatJet_mass = new std::vector<float>();
    t_FatJet_msoftdrop = new std::vector<float>();
    t_FatJet_n2b1 = new std::vector<float>();
    t_FatJet_n3b1 = new std::vector<float>();
    t_FatJet_phi = new std::vector<float>();
    t_FatJet_pt = new std::vector<float>();
    t_FatJet_tau1 = new std::vector<float>();
    t_FatJet_tau2 = new std::vector<float>();
    t_FatJet_tau3 = new std::vector<float>();
    t_FatJet_tau4 = new std::vector<float>();
    //t_FatJet_jetId = new std::vector<int>();
    t_FatJet_subJetIdx1 = new std::vector<int>();
    t_FatJet_subJetIdx2 = new std::vector<int>();

    tree->Branch("t_FatJet_area", "vector<float>", &t_FatJet_area);
    tree->Branch("t_FatJet_btagCMVA", "vector<float>", &t_FatJet_btagCMVA);
    tree->Branch("t_FatJet_btagCSVV2", "vector<float>", &t_FatJet_btagCSVV2);
    tree->Branch("t_FatJet_btagDeepB", "vector<float>", &t_FatJet_btagDeepB);
    tree->Branch("t_FatJet_eta", "vector<float>", &t_FatJet_eta);
    tree->Branch("t_FatJet_mass", "vector<float>", &t_FatJet_mass);
    tree->Branch("t_FatJet_msoftdrop", "vector<float>", &t_FatJet_msoftdrop);
    tree->Branch("t_FatJet_n2b1", "vector<float>", &t_FatJet_n2b1);
    tree->Branch("t_FatJet_n3b1", "vector<float>", &t_FatJet_n3b1);
    tree->Branch("t_FatJet_phi", "vector<float>", &t_FatJet_phi);
    tree->Branch("t_FatJet_pt", "vector<float>", &t_FatJet_pt);
    tree->Branch("t_FatJet_tau1", "vector<float>", &t_FatJet_tau1);
    tree->Branch("t_FatJet_tau2", "vector<float>", &t_FatJet_tau2);
    tree->Branch("t_FatJet_tau3", "vector<float>", &t_FatJet_tau3);
    tree->Branch("t_FatJet_tau4", "vector<float>", &t_FatJet_tau4);
    //tree->Branch("t_FatJet_jetId", "vector<int>", &t_FatJet_jetId);
    tree->Branch("t_FatJet_subJetIdx1", "vector<int>", &t_FatJet_subJetIdx1);
    tree->Branch("t_FatJet_subJetIdx2", "vector<int>", &t_FatJet_subJetIdx2);

    t_SubJet_btagCMVA = new std::vector<float>();
    t_SubJet_btagCSVV2 = new std::vector<float>();
    t_SubJet_btagDeepB = new std::vector<float>();
    t_SubJet_eta = new std::vector<float>();
    t_SubJet_mass = new std::vector<float>();
    t_SubJet_n2b1 = new std::vector<float>();
    t_SubJet_n3b1 = new std::vector<float>();
    t_SubJet_phi = new std::vector<float>();
    t_SubJet_pt = new std::vector<float>();
    t_SubJet_tau1 = new std::vector<float>();
    t_SubJet_tau2 = new std::vector<float>();
    t_SubJet_tau3 = new std::vector<float>();
    t_SubJet_tau4 = new std::vector<float>();

    tree->Branch("t_SubJet_btagCMVA", "vector<float>", &t_SubJet_btagCMVA);
    tree->Branch("t_SubJet_btagCSVV2", "vector<float>", &t_SubJet_btagCSVV2);
    tree->Branch("t_SubJet_btagDeepB", "vector<float>", &t_SubJet_btagDeepB);
    tree->Branch("t_SubJet_eta", "vector<float>", &t_SubJet_eta);
    tree->Branch("t_SubJet_mass", "vector<float>", &t_SubJet_mass);
    tree->Branch("t_SubJet_n2b1", "vector<float>", &t_SubJet_n2b1);
    tree->Branch("t_SubJet_n3b1", "vector<float>", &t_SubJet_n3b1);
    tree->Branch("t_SubJet_phi", "vector<float>", &t_SubJet_phi);
    tree->Branch("t_SubJet_pt", "vector<float>", &t_SubJet_pt);
    tree->Branch("t_SubJet_tau1", "vector<float>", &t_SubJet_tau1);
    tree->Branch("t_SubJet_tau2", "vector<float>", &t_SubJet_tau2);
    tree->Branch("t_SubJet_tau3", "vector<float>", &t_SubJet_tau3);
    tree->Branch("t_SubJet_tau4", "vector<float>", &t_SubJet_tau4);

    t_Jet_area = new std::vector<float>();
    // t_Jet_btagCMVA= new std::vector<float>();
    // t_Jet_btagCSVV2= new std::vector<float>();
    t_Jet_btagDeepB = new std::vector<float>();
    t_Jet_btagPNetB = new std::vector<float>();
    // t_Jet_btagDeepC= new std::vector<float>();
    // t_Jet_btagDeepFlavB= new std::vector<float>();
    t_Jet_chEmEF = new std::vector<float>();
    t_Jet_chHEF = new std::vector<float>();
    t_Jet_eta = new std::vector<float>();
    t_Jet_mass = new std::vector<float>();
    t_Jet_mass_nanoAOD = new std::vector<float>();
    t_Jet_neEmEF = new std::vector<float>();
    t_Jet_neHEF = new std::vector<float>();
    t_Jet_phi = new std::vector<float>();
    t_Jet_pt = new std::vector<float>();

    for (const auto &syst_name : jet_jes_syst_names) {
        for (const auto &direction : jes_directions) {
            const std::string branch_name =
                JetPtJesSystBranchName(syst_name, direction);

            t_Jet_pt_jes_syst[branch_name] = new std::vector<float>();

            const std::string mass_branch_name =
                JetMassJesSystBranchName(syst_name, direction);

            t_Jet_mass_jes_syst[mass_branch_name] = new std::vector<float>();
        }
    }
    for (const auto &syst_name : jet_jer_syst_names) {
        for (const auto &direction : jer_directions) {
            const std::string branch_name =
                JetPtJerSystBranchName(syst_name, direction);

            t_Jet_pt_jer_syst[branch_name] = new std::vector<float>();

            const std::string mass_branch_name =
                JetMassJerSystBranchName(syst_name, direction);

            t_Jet_mass_jer_syst[mass_branch_name] = new std::vector<float>();
        }
    }
    t_Jet_pt_nanoAOD = new std::vector<float>();
    t_Jet_qgl = new std::vector<float>();
    t_Jet_jetId = new std::vector<int>();
    t_Jet_chMultiplicity = new std::vector<int>();
    t_Jet_neMultiplicity = new std::vector<int>();
    t_Jet_nConstituents = new std::vector<int>();
    t_Jet_nElectrons = new std::vector<int>();
    t_Jet_nMuons = new std::vector<int>();
    t_Jet_puId = new std::vector<int>();

    tree->Branch("t_nSoftActivityJet", &t_nSoftActivityJet,
                 "t_nSoftActivityJet/I");
    tree->Branch("t_SoftActivityJetNjets10", &t_SoftActivityJetNjets10,
                 "t_SoftActivityJetNjets10/I");
    tree->Branch("t_SoftActivityJetNjets2", &t_SoftActivityJetNjets2,
                 "t_SoftActivityJetNjets2/I");
    tree->Branch("t_SoftActivityJetNjets5", &t_SoftActivityJetNjets5,
                 "t_SoftActivityJetNjets5/I");
    tree->Branch("t_SoftActivityJetHT", &t_SoftActivityJetHT,
                 "t_SoftActivityJetHT/F");
    tree->Branch("t_SoftActivityJetHT10", &t_SoftActivityJetHT10,
                 "t_SoftActivityJetHT10/F");
    tree->Branch("t_SoftActivityJetHT2", &t_SoftActivityJetHT2,
                 "t_SoftActivityJetHT2/F");
    tree->Branch("t_SoftActivityJetHT5", &t_SoftActivityJetHT5,
                 "t_SoftActivityJetHT5/F");
    tree->Branch("t_nJet", &t_nJet, "t_nJet/I");
    tree->Branch("t_Jet_area", "vector<float>", &t_Jet_area);
    // tree->Branch("t_Jet_btagCMVA"    , "vector<float>" ,&t_Jet_btagCMVA);
    // tree->Branch("t_Jet_btagCSVV2"    , "vector<float>" ,&t_Jet_btagCSVV2);
    tree->Branch("t_Jet_btagDeepB", "vector<float>", &t_Jet_btagDeepB);
    tree->Branch("t_Jet_btagPNetB", "vector<float>", &t_Jet_btagPNetB);
    // tree->Branch("t_Jet_btagDeepC"    , "vector<float>" ,&t_Jet_btagDeepC);
    // tree->Branch("t_Jet_btagDeepFlavB"    , "vector<float>"
    // ,&t_Jet_btagDeepFlavB);



    tree->Branch("leadJet_idx", &t_leadJet_idx);
    tree->Branch("subleadJet_idx", &t_subleadJet_idx);
    tree->Branch("t_Jet_chEmEF", "vector<float>", &t_Jet_chEmEF);
    tree->Branch("t_Jet_chHEF", "vector<float>", &t_Jet_chHEF);
    tree->Branch("t_Jet_eta", "vector<float>", &t_Jet_eta);
    tree->Branch("t_Jet_mass", "vector<float>", &t_Jet_mass);
    tree->Branch("t_Jet_mass_nanoAOD", "vector<float>", &t_Jet_mass_nanoAOD);
    tree->Branch("t_Jet_neEmEF", "vector<float>", &t_Jet_neEmEF);
    tree->Branch("t_Jet_neHEF", "vector<float>", &t_Jet_neHEF);
    tree->Branch("t_Jet_phi", "vector<float>", &t_Jet_phi);
    tree->Branch("t_Jet_pt", "vector<float>", &t_Jet_pt);
    for (auto &entry : t_Jet_pt_jes_syst) {
        const std::string &branch_name = entry.first;
        std::vector<float> *&branch_vector = entry.second;

        tree->Branch(branch_name.c_str(), "vector<float>", &branch_vector);
    }
    for (auto &entry : t_Jet_pt_jer_syst) {
        const std::string &branch_name = entry.first;
        std::vector<float> *&branch_vector = entry.second;

        tree->Branch(branch_name.c_str(), "vector<float>", &branch_vector);
    }
    for (auto &entry : t_Jet_mass_jes_syst) {
        const std::string &branch_name = entry.first;
        std::vector<float> *&branch_vector = entry.second;

        tree->Branch(branch_name.c_str(), "vector<float>", &branch_vector);
    }
    for (auto &entry : t_Jet_mass_jer_syst) {
        const std::string &branch_name = entry.first;
        std::vector<float> *&branch_vector = entry.second;

        tree->Branch(branch_name.c_str(), "vector<float>", &branch_vector);
    }
    tree->Branch("t_Jet_pt_nanoAOD", "vector<float>", &t_Jet_pt_nanoAOD);
    tree->Branch("t_Jet_qgl", "vector<float>", &t_Jet_qgl);
    tree->Branch("t_Jet_jetId", "vector<int>", &t_Jet_jetId);
    tree->Branch("t_Jet_chMultiplicity", "vector<int>", &t_Jet_chMultiplicity);
    tree->Branch("t_Jet_neMultiplicity", "vector<int>", &t_Jet_neMultiplicity);
    tree->Branch("t_Jet_nConstituents", "vector<int>", &t_Jet_nConstituents);
    tree->Branch("t_Jet_nElectrons", "vector<int>", &t_Jet_nElectrons);
    tree->Branch("t_Jet_nMuons", "vector<int>", &t_Jet_nMuons);
    tree->Branch("t_Jet_puId", "vector<int>", &t_Jet_puId);

    tree->Branch("t_diJet_pt", &t_diJet_pt, "t_diJet_pt/F");
    tree->Branch("t_diJet_eta", &t_diJet_eta, "t_diJet_eta/F");
    tree->Branch("t_diJet_phi", &t_diJet_phi, "t_diJet_phi/F");
    tree->Branch("t_diJet_mass", &t_diJet_mass, "t_diJet_mass/F");
    tree->Branch("t_diJet_mass_mo", &t_diJet_mass_mo, "t_diJet_mass_mo/F");

    tree->Branch("t_nbJet", &t_nbJet, "t_nbJet/I");
    tree->Branch("t_nbJet_Loose", &t_nbJet_Loose, "t_nbJet_Loose/I");
    t_bJet_area = new std::vector<float>();
    t_bJet_btagDeepB = new std::vector<float>();
    t_bJet_btagPNetB = new std::vector<float>();
    t_bJet_chEmEF = new std::vector<float>();
    t_bJet_chHEF = new std::vector<float>();
    t_bJet_eta = new std::vector<float>();
    t_bJet_mass = new std::vector<float>();
    t_bJet_neEmEF = new std::vector<float>();
    t_bJet_neHEF = new std::vector<float>();
    t_bJet_phi = new std::vector<float>();
    t_bJet_pt = new std::vector<float>();
    t_bJet_qgl = new std::vector<float>();
    t_bJet_jetId = new std::vector<int>();
    t_bJet_chMultiplicity = new std::vector<int>();
    t_bJet_neMultiplicity = new std::vector<int>();
    t_bJet_nConstituents = new std::vector<int>();
    t_bJet_nElectrons = new std::vector<int>();
    t_bJet_nMuons = new std::vector<int>();
    t_bJet_puId = new std::vector<int>();
    t_bJet_SF = new std::vector<double>();
    t_bJet_SFup = new std::vector<double>();
    t_bJet_SFdown = new std::vector<double>();

    tree->Branch("t_bJet_area", "vector<float>", &t_bJet_area);
    tree->Branch("t_bJet_btagDeepB", "vector<float>", &t_bJet_btagDeepB);
    tree->Branch("t_bJet_btagPNetB", "vector<float>", &t_bJet_btagPNetB);
    tree->Branch("t_bJet_chEmEF", "vector<float>", &t_bJet_chEmEF);
    tree->Branch("t_bJet_chHEF", "vector<float>", &t_bJet_chHEF);
    tree->Branch("t_bJet_eta", "vector<float>", &t_bJet_eta);
    tree->Branch("t_bJet_mass", "vector<float>", &t_bJet_mass);
    tree->Branch("t_bJet_neEmEF", "vector<float>", &t_bJet_neEmEF);
    tree->Branch("t_bJet_neHEF", "vector<float>", &t_bJet_neHEF);
    tree->Branch("t_bJet_phi", "vector<float>", &t_bJet_phi);
    tree->Branch("t_bJet_pt", "vector<float>", &t_bJet_pt);
    tree->Branch("t_bJet_qgl", "vector<float>", &t_bJet_qgl);
    tree->Branch("t_bJet_jetId", "vector<int>", &t_bJet_jetId);
    tree->Branch("t_bJet_chMultiplicity", "vector<int>", &t_bJet_chMultiplicity);
    tree->Branch("t_bJet_neMultiplicity", "vector<int>", &t_bJet_neMultiplicity);
    tree->Branch("t_bJet_nConstituents", "vector<int>", &t_bJet_nConstituents);
    tree->Branch("t_bJet_nElectrons", "vector<int>", &t_bJet_nElectrons);
    tree->Branch("t_bJet_nMuons", "vector<int>", &t_bJet_nMuons);
    tree->Branch("t_bJet_puId", "vector<int>", &t_bJet_puId);
    tree->Branch("t_bJet_SF", "vector<double>", &t_bJet_SF);
    tree->Branch("t_bJet_SFup", "vector<double>", &t_bJet_SFup);
    tree->Branch("t_bJet_SFdown", "vector<double>", &t_bJet_SFdown);

    tree->Branch("t_PV_ndof", &t_PV_ndof, "t_PV_ndof/F");
    tree->Branch("t_PV_x", &t_PV_x, "t_PV_x/F");
    tree->Branch("t_PV_y", &t_PV_y, "t_PV_y/F");
    tree->Branch("t_PV_z", &t_PV_z, "t_PV_z/F");
    tree->Branch("t_PV_npvs", &t_PV_npvs, "t_PV_npvs/I");
    tree->Branch("t_PV_npvsGood", &t_PV_npvsGood, "t_PV_npvsGood/I");

    tree->Branch("t_Rho", &t_Rho, "t_Rho/F");

    t_GenPart_eta = new std::vector<float>();
    t_GenPart_mass = new std::vector<float>();
    t_GenPart_phi = new std::vector<float>();
    t_GenPart_pt = new std::vector<float>();
    t_GenPart_genPartIdxMother = new std::vector<int>();
    t_GenPart_pdgId = new std::vector<int>();
    t_GenPart_status = new std::vector<int>();

    t_GenJet_eta = new std::vector<float>();
    t_GenJet_mass = new std::vector<float>();
    t_GenJet_phi = new std::vector<float>();
    t_GenJet_pt = new std::vector<float>();

    tree->Branch("t_GenPart_eta", "vector<float>", &t_GenPart_eta);
    tree->Branch("t_GenPart_mass", "vector<float>", &t_GenPart_mass);
    tree->Branch("t_GenPart_phi", "vector<float>", &t_GenPart_phi);
    tree->Branch("t_GenPart_pt", "vector<float>", &t_GenPart_pt);
    tree->Branch("t_GenPart_genPartIdxMother", "vector<int>",
                 &t_GenPart_genPartIdxMother);
    tree->Branch("t_GenPart_pdgId", "vector<int>", &t_GenPart_pdgId);
    tree->Branch("t_GenPart_status", "vector<int>", &t_GenPart_status);

    tree->Branch("t_GenJet_eta", "vector<float>", &t_GenJet_eta);
    tree->Branch("t_GenJet_mass", "vector<float>", &t_GenJet_mass);
    tree->Branch("t_GenJet_phi", "vector<float>", &t_GenJet_phi);
    tree->Branch("t_GenJet_pt", "vector<float>", &t_GenJet_pt);
}
#endif // #ifdef HmmAnalyzer_cxx
