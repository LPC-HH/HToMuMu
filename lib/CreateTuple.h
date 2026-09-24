#ifndef LIB_CreateTuple_H
#define LIB_CreateTuple_H

#include "Constants.h"
#include "Run3Constants.h"
#include "TF1.h"
#include "Utils.h"
#include <TChain.h>
#include <TFile.h>
#include <TH1F.h>
#include <TLorentzVector.h>
#include <TString.h>
#include <TSystem.h>
#include <TTree.h>
#include <cmath>
#include <algorithm>
#include <iostream>
#include <map>
#include <math.h>
#include <stdexcept>
#include <string>
#include <vector>

std::map<TString, int> MC_CAMPAIGN_MAP = {{"2022", 1}, {"2022EE", 2},
                                          {"2023", 3}, {"2023BPix", 4},
                                          {"2024", 5}, {"2025", 6}};

/**
 * @class CreateTuple
 * @brief This Class read outputs from HmmAnalyzer and return a smaller
 * tree_input with the variables necessary for the categorization
 */
class CreateTuple {
  public:
    /**
     * @brief Constructor that initializes the CreateTuple class with specified
     * input and output settings.
     *
     * @param input The full path of the input ROOT file containing the data.
     * @param weightFile The full path of the input ROOT file containing the SumWeight.
     * @param output Directory path for the output ROOT file.
     * @param era The data collection era. (e.g. 2022, 2022EE, etc).
     * @param channel Analysis channel (e.g., DY50to120, ggH, 2022F, etc).
     * @param is_data Boolean flag indicating whether the input file is data or
     * simulation.
     *
     * @param is_signal_ Boolean flag indicating if the data pertains to signal
     * or background
     * @param include_Z Boolean flag indicating if include Z region
     * @param include_H Boolean flag indicating if include H region
     */
    CreateTuple(TString input, TString weightFile, TString output, TString era, TString channel,
                bool is_data, bool is_signal_,  bool include_Z, bool include_H,
                TString jet_syst);
    /**
     * @brief Destructor for CreateTuple, cleaning up dynamically allocated
     * objects.
     */
    virtual ~CreateTuple();

    /**
     * @brief Loads the input file and adds its data to the input TChain.
     *
     * @throws std::runtime_error if the input file is not found.
     */
    void fillChain();

    /**
     * @brief Sets up branch addresses for reading variables from the input
     * tree.
     */
    void setBranchesAddressesInput();

    /**
     * @brief Sets up branch addresses for writing variables to the output tree.
     */
    void setBranchesAddressesOutput();

    /**
     * @brief Processes events and fills the output tree with calculated
     * variables.
     */
    void fillOutputTree();

    /**
     * @brief Saves the output tree to a ROOT file in the specified output
     * directory.
     */
    void saveTree();

    int isggHCategory();
    int isVBFCategory();

    static std::string NormalizeJetSyst(TString jet_syst);
    static std::string JetPtBranchName(const std::string &jet_syst);
    static std::string JetMassBranchName(const std::string &jet_pt_branch);
    bool passesJetPtSelection(size_t index) const;

  private:
    TChain *tree_input; /**< Pointer to input TChain. */
    TTree *tree_output; /**< Pointer to output TTree. */
    bool is_signal; /**< Flag indicating if the input file is signal data. */
    bool is_data;
    bool include_Z; /**< Flag indicating if save Z region. */
    bool include_H; /**< Flag indicating if save H region. */
    long double
        gen_weight_sum;     /**< Sum of generator weights for normalization. */
    const float luminosity; /**< Luminosity of the era. */
    const float cross_section; /**< Cross-section of the process. */
    TString input_name;        /**< Path of the input file. */
    TString weight_name;        /**< Path of the weight file. */
    TString output_name;       /**< Name of the output file. */
    TString output_directory;  /**< Directory for saving the output file. */
    TFile *output_file;        /**< Pointer to output TFile. */

    TString analysis_channel;  /**< Directory for saving the output file. */
    std::string jet_syst_name;
    std::string jet_pt_branch_name;
    std::string jet_mass_branch_name;

    /** MC Campaign variable: 1-22, 2-22EE, 3-23, 4-23BPix, 5-24, 6-25 */
    int mc_campaign;

    /** Read event variables */
    float gen_weight, pileup_weight, pileup_weight_up, pileup_weight_down;

    //std::vector<float> *mu_trig_eff_SF_vec, *mu_trig_eff_SF_up_vec,
        //*mu_trig_eff_SF_down_vec;
    
    std::vector<float> *mu_trig_eff_DATA_vec;
    std::vector<float> *mu_trig_eff_DATA_up_vec;
    std::vector<float> *mu_trig_eff_DATA_down_vec;

    std::vector<float> *mu_trig_eff_MC_vec;
    std::vector<float> *mu_trig_eff_MC_up_vec;
    std::vector<float> *mu_trig_eff_MC_down_vec;

    std::vector<float> *mu_ID_eff_SF_vec, *mu_ID_eff_SF_up_vec,
        *mu_ID_eff_SF_down_vec;
    std::vector<float> *mu_ISO_eff_SF_vec, *mu_ISO_eff_SF_up_vec,
        *mu_ISO_eff_SF_down_vec;


    int n_SoftJet_pt2, n_SoftJet_pt5, n_SoftJet_pt10;
    float HT, HT_pt2, HT_pt5, HT_pt10;
    /** Read DiMuon variables */
    float diMuon_mass, diMuon_bsConstrainedMass_nanoAOD, diMuon_bsConstrainedMass, diMuon_pt,
        diMuon_bsConstrainedPt, diMuon_phi, diMuon_eta;

    /** Read MET variables **/
    float PuppiMET_phi, PuppiMET_pt, PuppiMET_sumEt;

    /** Read Muon variables */
    int mu1_index, mu2_index;
    std::vector<int> *mu_charge;
    std::vector<float> *mu_pt, *mu_bsConstrainedPt, *mu_bsConstrainedPt_nanoAOD,
        *mu_phi, *mu_eta, *mu_dz, *mu_dzErr;
    std::vector<float> *mu_ptErr, *mu_bsConstrainedPtErr;

    /** Read electron variables */
    std::vector<float> *elec_pt;

    /** Read LHE variables */
    std::vector<float> *lhe_pdf_weight, *lhe_scale_weight;

    /** Read Jet variables */
    int n_jet, n_bjet, n_bjet_Loose;

    std::vector<float> *jet_mass, *jet_pt, *jet_phi, *jet_eta, *jet_pt_nanoAOD, *jet_area;

    std::vector<float> *jet_btagPNetB, *jet_btagPNetQvG, *jet_btagUParTAK4B, 
                        *jet_btagUParTAK4QvG, *jet_btagDeepFlavQG;

    std::vector<float> *jet_chEmEF, *jet_chHEF, *jet_neEmEF, *jet_neHEF;

    std::vector<int> *jet_nConstituents, *jet_chMultiplicity, *jet_neMultiplicity;

    /** Read Jet variables */
    float diJet_pt, diJet_eta, diJet_phi, diJet_mass, diJet_mass_mo;

    /** New Event variables */
    double scale_factor; // luminosity * cross_section / gen_weight_sum
    Double_t weight, weight_no_eff_sf;
    double weight_no_lumi;
    float mu_trig_eff_SF, mu_trig_eff_SF_down, mu_trig_eff_SF_up;
    float mu_ID_eff_SF, mu_ID_eff_SF_down, mu_ID_eff_SF_up;
    float mu_ISO_eff_SF, mu_ISO_eff_SF_down, mu_ISO_eff_SF_up;

    float rho;
    int pv;
    // int is_data_int, is_signal_int, pv;
    int is_ggH_category, is_VBF_category;

    /** New DiMuon variables*/
    float diMuon_rapidity;

    /** New Muon variables*/
    float mu1_pt_mass_ratio, mu2_pt_mass_ratio, mu1_bsConstrainedPt_mass_ratio,
        mu2_bsConstrainedPt_mass_ratio, mu1_eta, mu2_eta, phi_CS, cos_theta_CS;
    float mu1_pt, mu2_pt, mu1_bsConstrainedPt_nanoAOD,
        mu2_bsConstrainedPt_nanoAOD, mu1_bsConstrainedPt,
        mu2_bsConstrainedPt, mu1_ptErr, mu2_ptErr, mu1_bsConstrainedPtErr,
        mu2_bsConstrainedPtErr, mu1_dz, mu2_dz, mu1_dzErr, mu2_dzErr;
    /** New Error variables*/
    float relative_diMuon_mass_error, relative_diMuon_bsConstrainedMass_error;

    /** New jets variables*/
    float leading_jet_pt, leading_jet_pt_nanoAOD, leading_jet_eta,
            leading_jet_mass, leading_jet_area;

    float leading_jet_btagPNetQvG, leading_jet_btagUParTAK4QvG, leading_jet_btagDeepFlavQG;

    float leading_jet_chEmEF, leading_jet_chHEF, leading_jet_neEmEF, leading_jet_neHEF;

    int leading_jet_nConstituents, leading_jet_chMultiplicity, leading_jet_neMultiplicity;


    float subleading_jet_pt, subleading_jet_pt_nanoAOD, subleading_jet_eta,
            subleading_jet_mass, subleading_jet_area;

    float subleading_jet_btagPNetQvG, subleading_jet_btagUParTAK4QvG, subleading_jet_btagDeepFlavQG;

    float subleading_jet_chEmEF, subleading_jet_chHEF, subleading_jet_neEmEF, subleading_jet_neHEF;

    int subleading_jet_nConstituents, subleading_jet_chMultiplicity, subleading_jet_neMultiplicity;

    /** New DiJets variables*/
    float delta_eta_diJet, delta_phi_diJet, z_zeppenfeld, pt_balance,
        pt_centrality, min_delta_eta_diMuon_jet, min_delta_phi_diMuon_jet;

    /** histograms */
    TH1D *h_nEntries, *h_nTrigger, *h_nTwoMuons, *h_nNoExtraMuon,
        *h_nNoExtraElectron, *h_nTriggerMatch, *h_nBjetRejection, *h_nJets,
        *h_nValidJets, *h_nValidSeperatedJets, *h_nValidNotVetoedJets;
    TH1D *h_nInFinalMassRange = new TH1D("h_nInFinalMassRange", "h_nInFinalMassRange", 1, 0, 1);
    //TH1D *h_nJMEJets = new TH1D("h_nJMEJets", "h_nJMEJets", 1, 0, 1);
    TH1D *h_n2Jets = new TH1D("h_n2Jets", "h_n2Jets", 1, 0, 1);
    TH1D *h_nBothVBFJets = new TH1D("h_nBothVBFJets", "h_nBothVBFJets", 1, 0, 1);
    TH1D *h_nVBFEtaSeperated = new TH1D("h_nVBFEtaSeperated", "h_nVBFEtaSeperated", 1, 0, 1);
    TH1D *h_nggHEtaSeperated = new TH1D("h_nggHEtaSeperated", "h_nggHEtaSeperated", 1, 0, 1);
    TH1D *h_nVBFPtPass = new TH1D("h_nVBFPtPass", "h_nVBFPtPass", 1, 0, 1);
    TH1D *h_nMjjPass = new TH1D("h_nMjjPass", "h_nMjjPass", 1, 0, 1);
    TH1D *h_nggHCat = new TH1D("h_nggHCat", "h_nggHCat", 1, 0, 1);
    TH1D *h_nVBFCat = new TH1D("h_nVBFCat", "h_nVBFCat", 1, 0, 1);
};

inline std::string CreateTuple::JetPtBranchName(const std::string &jet_syst) {
    if (jet_syst.empty()) {
        return "t_Jet_pt";
    }
    return "t_Jet_pt_" + jet_syst;
}

inline std::string CreateTuple::JetMassBranchName(const std::string &jet_syst) {
    if (jet_syst.empty()) {
        return "t_Jet_mass";
    }
    return "t_Jet_mass_" + jet_syst;
}

CreateTuple::CreateTuple(TString input, TString weightFile, TString output, TString era,
                         TString channel, bool is_data_, bool is_signal_, bool include_Z_,
                         bool include_H_, TString jet_syst)
    : luminosity(LUMINOSITY.at(era)), cross_section(CROSS_SECTION.at(channel)) {

    tree_input = new TChain("tree");
    tree_output = new TTree("tree_output", "tree_output");
    input_name = input;
    weight_name = weightFile;
    output_directory = output;
    if( jet_syst =="nominal")  {
        jet_syst = "";
    }
    jet_syst_name = std::string(jet_syst.Data());
    if (!output_directory.EndsWith("/")) {
        output_directory += "/";
    }
    is_signal = is_signal_;
    include_Z = include_Z_;
    include_H = include_H_;
    analysis_channel = channel;
    is_data = is_data_;
    jet_pt_branch_name = JetPtBranchName(jet_syst_name);
    jet_mass_branch_name = JetMassBranchName(jet_syst_name);

    if(include_Z){
        std::cout << "Z range included" << std::endl;
    }
    if(include_H){
        std::cout << "H range included" << std::endl;
    }
    std::cout << "Jet systematic: " << jet_syst_name << std::endl;
    std::cout << "Jet pT input branch: " << jet_pt_branch_name << std::endl;

    output_name = channel + "_" + era + "_tuples.root";
    std::cout << "Luminosity: " << luminosity
              << ", cross section: " << cross_section << std::endl;
    if (!is_data) {
        gen_weight_sum = GetGenWeightSum(weight_name);
        //if(era == "2024"){
            //scale_factor = GetScaleFactor(luminosity + LUMINOSITY.at("2025"), cross_section, gen_weight_sum);
        //}
        //else{
            //scale_factor = GetScaleFactor(luminosity, cross_section, gen_weight_sum);
        //}
        // is_data_int = 0;
        scale_factor = GetScaleFactor(luminosity, cross_section, gen_weight_sum);
        // if (is_signal_) {
        // is_signal_int = 1;
        //} else {
        // is_signal_int = 0;
        //}
    }
    // else {
    // is_data_int = 1;
    //}

    mc_campaign = MC_CAMPAIGN_MAP.at(era);

    mu_charge = nullptr;
    mu_pt = nullptr;
    mu_bsConstrainedPt = nullptr;
    mu_bsConstrainedPt_nanoAOD = nullptr;
    mu_ptErr = nullptr;
    mu_bsConstrainedPtErr = nullptr;
    mu_phi = nullptr;
    mu_eta = nullptr;
    mu_dz = nullptr;
    mu_dzErr = nullptr;
    elec_pt = nullptr;
    lhe_pdf_weight = nullptr;
    lhe_scale_weight = nullptr;

    jet_eta = nullptr;
    jet_pt = nullptr;
    jet_pt_nanoAOD = nullptr;
    jet_phi = nullptr;
    jet_mass = nullptr;

    jet_area = nullptr;

    jet_btagPNetB = nullptr;
    jet_btagPNetQvG = nullptr;

    jet_btagUParTAK4B = nullptr;
    jet_btagUParTAK4QvG = nullptr;

    jet_btagDeepFlavQG = nullptr;

    jet_chEmEF = nullptr;
    jet_chHEF = nullptr;
    jet_neEmEF = nullptr;
    jet_neHEF = nullptr;

    jet_nConstituents = nullptr;
    jet_chMultiplicity = nullptr;
    jet_neMultiplicity = nullptr;

    //mu_trig_eff_SF_vec = nullptr;
    //mu_trig_eff_SF_up_vec = nullptr;
    //mu_trig_eff_SF_down_vec = nullptr;
    
    mu_trig_eff_DATA_vec = nullptr;
    mu_trig_eff_DATA_up_vec = nullptr;
    mu_trig_eff_DATA_down_vec = nullptr;

    mu_trig_eff_MC_vec = nullptr;
    mu_trig_eff_MC_up_vec = nullptr;
    mu_trig_eff_MC_down_vec = nullptr;

    mu_ID_eff_SF_vec = nullptr;
    mu_ID_eff_SF_up_vec = nullptr;
    mu_ID_eff_SF_down_vec = nullptr;
    mu_ISO_eff_SF_vec = nullptr;
    mu_ISO_eff_SF_up_vec = nullptr;
    mu_ISO_eff_SF_down_vec = nullptr;

    TFile *f_input = TFile::Open(input_name);
    h_nEntries = (TH1D*)f_input->Get("h_nEntries");
    h_nEntries->SetDirectory(0);
    std::cout << "nEntries: " << h_nEntries->GetBinContent(1) << std::endl;
    h_nTrigger = (TH1D*)f_input->Get("h_nTrigger");
    h_nTrigger->SetDirectory(0);
    h_nTwoMuons = (TH1D*)f_input->Get("h_nTwoMuons");
    h_nTwoMuons->SetDirectory(0);
    h_nNoExtraMuon = (TH1D*)f_input->Get("h_nNoExtraMuon");
    h_nNoExtraMuon->SetDirectory(0);
    h_nNoExtraElectron = (TH1D*)f_input->Get("h_nNoExtraElectron");
    h_nNoExtraElectron->SetDirectory(0);
    h_nTriggerMatch = (TH1D*)f_input->Get("h_nTriggerMatch");
    h_nTriggerMatch->SetDirectory(0);
    h_nBjetRejection = (TH1D*)f_input->Get("h_nBjetRejection");
    h_nBjetRejection->SetDirectory(0);
    h_nBjetRejection->Reset();
    h_nJets = (TH1D*)f_input->Get("h_nJets");
    h_nJets->SetDirectory(0);
    h_nValidJets = (TH1D*)f_input->Get("h_nValidJets");
    h_nValidJets->SetDirectory(0);
    h_nValidSeperatedJets = (TH1D*)f_input->Get("h_nValidSeperatedJets");
    h_nValidSeperatedJets->SetDirectory(0);
    h_nValidNotVetoedJets = (TH1D*)f_input->Get("h_nValidNotVetoedJets");
    h_nValidNotVetoedJets->SetDirectory(0);
    f_input->Close();

    fillChain();
}

CreateTuple::~CreateTuple() {
    delete tree_input->GetCurrentFile();
    delete tree_output;
    delete output_file;
}

void CreateTuple::fillChain() {
    tree_input->Add(input_name);
    if (!tree_input) {
        throw std::runtime_error("Tuple file not found");
        return;
    }
    std::cout << "Tuple loaded" << std::endl;
}

void CreateTuple::setBranchesAddressesOutput() {

    tree_output->Branch("gen_weight", &gen_weight, "gen_weight/F");
    tree_output->Branch("pileup_weight", &pileup_weight, "pileup_weight/F");
    tree_output->Branch("pileup_weight_up", &pileup_weight_up, "pileup_weight_up/F");
    tree_output->Branch("pileup_weight_down", &pileup_weight_down,
                        "pileup_weight_down/F");
    tree_output->Branch("scale_factor", &scale_factor, "scale_factor/D");
    tree_output->Branch("weight", &weight, "weight/D");
    tree_output->Branch("weight_no_eff_sf", &weight_no_eff_sf, "weight_no_eff_sf/D");
    tree_output->Branch("weight_no_lumi", &weight_no_lumi, "weight_no_lumi/D");
    // tree_output->Branch("is_data", &is_data_int, "is_data/i");
    // tree_output->Branch("is_signal", &is_signal_int, "signal/i");
    tree_output->Branch("rho", &rho, "rho/F");
    tree_output->Branch("PV", &pv, "PV/I");

    tree_output->Branch("mu_trig_eff_SF", &mu_trig_eff_SF, "mu_trig_eff_SF/F");
    tree_output->Branch("mu_trig_eff_SF_down", &mu_trig_eff_SF_down,
                        "mu_trig_eff_SF_down/F");
    tree_output->Branch("mu_trig_eff_SF_up", &mu_trig_eff_SF_up,
                        "mu_trig_eff_SF_up/F");
    tree_output->Branch("mu_ID_eff_SF", &mu_ID_eff_SF, "mu_ID_eff_SF/F");
    tree_output->Branch("mu_ID_eff_SF_down", &mu_ID_eff_SF_down,
                        "mu_ID_eff_SF_down/F");
    tree_output->Branch("mu_ID_eff_SF_up", &mu_ID_eff_SF_up,
                        "mu_ID_eff_SF_up/F");
    tree_output->Branch("mu_ISO_eff_SF", &mu_ISO_eff_SF, "mu_ISO_eff_SF/F");
    tree_output->Branch("mu_ISO_eff_SF_down", &mu_ISO_eff_SF_down,
                        "mu_ISO_eff_SF_down/F");
    tree_output->Branch("mu_ISO_eff_SF_up", &mu_ISO_eff_SF_up,
                        "mu_ISO_eff_SF_up/F");

    tree_output->Branch("n_SoftJet_pt2", &n_SoftJet_pt2, "n_SoftJet_pt2/I");
    tree_output->Branch("n_SoftJet_pt5", &n_SoftJet_pt5, "n_SoftJet_pt5/I");
    tree_output->Branch("n_SoftJet_pt10", &n_SoftJet_pt10, "n_SoftJet_pt10/I");
    tree_output->Branch("HT", &HT, "HT/F");
    tree_output->Branch("HT_pt2", &HT_pt2, "HT_pt2/F");
    tree_output->Branch("HT_pt5", &HT_pt5, "HT_pt5/F");
    tree_output->Branch("HT_pt10", &HT_pt10, "HT_pt10/F");

    tree_output->Branch("is_ggH_category", &is_ggH_category,
                        "is_ggH_category/I");
    tree_output->Branch("is_VBF_category", &is_VBF_category,
                        "is_VBF_category/I");

    tree_output->Branch("mc_campaign", &mc_campaign, "mc_campaign/I");
    tree_output->Branch("channel", &analysis_channel);

    // DiMuon variables
    tree_output->Branch("diMuon_mass", &diMuon_mass, "diMuon_mass/F");
    tree_output->Branch("diMuon_bsConstrainedMass_nanoAOD", &diMuon_bsConstrainedMass_nanoAOD,
                        "diMuon_bsConstrainedMass_nanoAOD/F");
    tree_output->Branch("diMuon_bsConstrainedMass", &diMuon_bsConstrainedMass,
                        "diMuon_bsConstrainedMass/F");
    tree_output->Branch("diMuon_pt", &diMuon_pt, "diMuon_pt/F");
    tree_output->Branch("diMuon_bsConstrainedPt", &diMuon_bsConstrainedPt,
                        "diMuon_bsConstrainedPt/F");
    tree_output->Branch("diMuon_phi", &diMuon_phi, "diMuon_phi/F");
    tree_output->Branch("diMuon_eta", &diMuon_eta, "diMuon_eta/F");
    tree_output->Branch("diMuon_rapidity", &diMuon_rapidity,
                        "diMuon_rapidity/F");

    // MET variables
    tree_output->Branch("PuppiMET_phi", &PuppiMET_phi, "PuppiMET_phi/F");
    tree_output->Branch("PuppiMET_pt", &PuppiMET_pt, "PuppiMET_pt/F");
    tree_output->Branch("PuppiMET_sumEt", &PuppiMET_sumEt, "PuppiMET_sumEt/F");

    // Muon variables
    tree_output->Branch("mu1_pt_mass_ratio", &mu1_pt_mass_ratio,
                        "mu1_pt_mass_ratio/F");
    tree_output->Branch("mu2_pt_mass_ratio", &mu2_pt_mass_ratio,
                        "mu2_pt_mass_ratio/F");
    tree_output->Branch("mu1_bsConstrainedPt_mass_ratio",
                        &mu1_bsConstrainedPt_mass_ratio,
                        "mu1_bsConstrainedPt_mass_ratio/F");
    tree_output->Branch("mu2_bsConstrainedPt_mass_ratio",
                        &mu2_bsConstrainedPt_mass_ratio,
                        "mu2_bsConstrainedPt_mass_ratio/F");
    tree_output->Branch("mu1_eta", &mu1_eta, "mu1_eta/F");
    tree_output->Branch("mu2_eta", &mu2_eta, "mu2_eta/F");
    tree_output->Branch("mu1_pt", &mu1_pt, "mu1_pt/F");
    tree_output->Branch("mu2_pt", &mu2_pt, "mu2_pt/F");
    tree_output->Branch("mu1_bsConstrainedPt_nanoAOD",
                        &mu1_bsConstrainedPt_nanoAOD,
                        "mu1_bsConstrainedPt_nanoAOD/F");
    tree_output->Branch("mu2_bsConstrainedPt_nanoAOD",
                        &mu2_bsConstrainedPt_nanoAOD,
                        "mu2_bsConstrainedPt_nanoAOD/F");
    tree_output->Branch("mu1_bsConstrainedPt", &mu1_bsConstrainedPt,
                        "mu1_bsConstrainedPt/F");
    tree_output->Branch("mu2_bsConstrainedPt", &mu2_bsConstrainedPt,
                        "mu2_bsConstrainedPt/F");
    tree_output->Branch("mu1_ptErr", &mu1_ptErr, "mu1_ptErr/F");
    tree_output->Branch("mu2_ptErr", &mu2_ptErr, "mu2_ptErr/F");
    tree_output->Branch("mu1_bsConstrainedPtErr", &mu1_bsConstrainedPtErr,
                        "mu1_bsConstrainedPtErr/F");
    tree_output->Branch("mu2_bsConstrainedPtErr", &mu2_bsConstrainedPtErr,
                        "mu2_bsConstrainedPtErr/F");
    tree_output->Branch("mu1_dz", &mu1_dz, "mu1_dz/F");
    tree_output->Branch("mu2_dz", &mu2_dz, "mu2_dz/F");
    tree_output->Branch("mu1_dzErr", &mu1_dzErr, "mu1_dzErr/F");
    tree_output->Branch("mu2_dzErr", &mu2_dzErr, "mu2_dzErr/F");
    tree_output->Branch("phi_CS", &phi_CS, "phi_CS/F");
    tree_output->Branch("cos_theta_CS", &cos_theta_CS, "cos_theta_CS/F");

    // Error variables
    tree_output->Branch("relative_diMuon_mass_error",
                        &relative_diMuon_mass_error,
                        "relative_diMuon_mass_error/F");
    tree_output->Branch("relative_diMuon_bsConstrainedMass_error",
                        &relative_diMuon_bsConstrainedMass_error,
                        "relative_diMuon_bsConstrainedMass_error/F");

    // Jet variables
    tree_output->Branch("n_jet", &n_jet, "n_jet/I");
    tree_output->Branch("n_bjet", &n_bjet, "n_bjet/I");
    tree_output->Branch("n_bjet_Loose", &n_bjet_Loose, "n_bjet_Loose/I");
    tree_output->Branch("leading_jet_pt", &leading_jet_pt, "leading_jet_pt/F");
    if (jet_syst_name.empty()) {
        tree_output->Branch("leading_jet_pt_nanoAOD", &leading_jet_pt_nanoAOD,
                            "leading_jet_pt_nanoAOD/F");
    }
    tree_output->Branch("leading_jet_eta", &leading_jet_eta,"leading_jet_eta/F");
    tree_output->Branch("leading_jet_mass", &leading_jet_mass, "leading_jet_mass/F");
    tree_output->Branch("leading_jet_area", &leading_jet_area, "leading_jet_area/F");
    tree_output->Branch("leading_jet_btagPNetQvG", &leading_jet_btagPNetQvG,
                            "leading_jet_btagPNetQvG/F");
    tree_output->Branch("leading_jet_btagUParTAK4QvG",&leading_jet_btagUParTAK4QvG,
                        "leading_jet_btagUParTAK4QvG/F");
    tree_output->Branch("leading_jet_btagDeepFlavQG",&leading_jet_btagDeepFlavQG,
                        "leading_jet_btagDeepFlavQG/F");
    tree_output->Branch("leading_jet_chEmEF", &leading_jet_chEmEF, "leading_jet_chEmEF/F");
    tree_output->Branch("leading_jet_chHEF", &leading_jet_chHEF,"leading_jet_chHEF/F");
    tree_output->Branch("leading_jet_neEmEF", &leading_jet_neEmEF,"leading_jet_neEmEF/F");
    tree_output->Branch("leading_jet_neHEF", &leading_jet_neHEF, "leading_jet_neHEF/F");
    tree_output->Branch("leading_jet_nConstituents", &leading_jet_nConstituents,
                            "leading_jet_nConstituents/I");
    tree_output->Branch("leading_jet_chMultiplicity", &leading_jet_chMultiplicity,
                        "leading_jet_chMultiplicity/I");
    tree_output->Branch("leading_jet_neMultiplicity", &leading_jet_neMultiplicity,
                        "leading_jet_neMultiplicity/I");

    tree_output->Branch("subleading_jet_pt", &subleading_jet_pt,
                        "subleading_jet_pt/F");
    if (jet_syst_name.empty()) {
        tree_output->Branch("subleading_jet_pt_nanoAOD", &subleading_jet_pt_nanoAOD,
                            "subleading_jet_pt_nanoAOD/F");
    }
    tree_output->Branch("subleading_jet_eta", &subleading_jet_eta,
                        "subleading_jet_eta/F");
    tree_output->Branch("subleading_jet_mass", &subleading_jet_mass, "subleading_jet_mass/F");
    tree_output->Branch("subleading_jet_area", &subleading_jet_area, "subleading_jet_area/F");
    tree_output->Branch("subleading_jet_btagPNetQvG", &subleading_jet_btagPNetQvG,
                        "subleading_jet_btagPNetQvG/F");
    tree_output->Branch("subleading_jet_btagUParTAK4QvG", &subleading_jet_btagUParTAK4QvG,
                        "subleading_jet_btagUParTAK4QvG/F");
    tree_output->Branch("subleading_jet_btagDeepFlavQG", &subleading_jet_btagDeepFlavQG,
                        "subleading_jet_btagDeepFlavQG/F");
    tree_output->Branch("subleading_jet_chEmEF", &subleading_jet_chEmEF,
                        "subleading_jet_chEmEF/F");
    tree_output->Branch("subleading_jet_chHEF", &subleading_jet_chHEF, "subleading_jet_chHEF/F");
    tree_output->Branch("subleading_jet_neEmEF", &subleading_jet_neEmEF,
                        "subleading_jet_neEmEF/F");
    tree_output->Branch("subleading_jet_neHEF", &subleading_jet_neHEF, "subleading_jet_neHEF/F");
    tree_output->Branch("subleading_jet_nConstituents", &subleading_jet_nConstituents,
                        "subleading_jet_nConstituents/I");
    tree_output->Branch("subleading_jet_chMultiplicity", &subleading_jet_chMultiplicity,
                        "subleading_jet_chMultiplicity/I");
    tree_output->Branch("subleading_jet_neMultiplicity", &subleading_jet_neMultiplicity,
                        "subleading_jet_neMultiplicity/I");
    // diJet variables
    tree_output->Branch("diJet_mass", &diJet_mass, "diJet_mass/F");
    tree_output->Branch("delta_eta_diJet", &delta_eta_diJet,
                        "delta_eta_diJet/F");
    tree_output->Branch("delta_phi_diJet", &delta_phi_diJet,
                        "delta_phi_diJet/F");
    tree_output->Branch("z_zeppenfeld", &z_zeppenfeld, "z_zeppenfeld/F");
    tree_output->Branch("pt_balance", &pt_balance, "pt_balance/F");
    tree_output->Branch("pt_centrality", &pt_centrality, "pt_centrality/F");
    tree_output->Branch("min_delta_eta_diMuon_jet", &min_delta_eta_diMuon_jet,
                        "min_delta_eta_diMuon_jet/F");
    tree_output->Branch("min_delta_phi_diMuon_jet", &min_delta_phi_diMuon_jet,
                        "min_delta_phi_diMuon_jet/F");
    

    // LHE variables
    //tree_output->Branch("LHEPdfWeight", &lhe_pdf_weight);
    //tree_output->Branch("LHEScaleWeight", &lhe_scale_weight);

    std::cout << "Output Branches addressed setted" << std::endl;
}

void CreateTuple::setBranchesAddressesInput() {

    tree_input->SetBranchStatus("*", 0);

    tree_input->SetBranchStatus("t_puWeight", 1);
    tree_input->SetBranchAddress("t_puWeight", &pileup_weight);
    tree_input->SetBranchStatus("t_puWeightUp", 1);
    tree_input->SetBranchAddress("t_puWeightUp", &pileup_weight_up);
    tree_input->SetBranchStatus("t_puWeightDown", 1);
    tree_input->SetBranchAddress("t_puWeightDown", &pileup_weight_down);
    tree_input->SetBranchStatus("t_genWeight", 1);
    tree_input->SetBranchAddress("t_genWeight", &gen_weight);
    tree_input->SetBranchStatus("t_Mu_EffTRIG_DATA", 1);
    tree_input->SetBranchAddress("t_Mu_EffTRIG_DATA", &mu_trig_eff_DATA_vec);
    tree_input->SetBranchStatus("t_Mu_EffTRIG_DATA_up", 1);
    tree_input->SetBranchAddress("t_Mu_EffTRIG_DATA_up", &mu_trig_eff_DATA_up_vec);
    tree_input->SetBranchStatus("t_Mu_EffTRIG_DATA_down", 1);
    tree_input->SetBranchAddress("t_Mu_EffTRIG_DATA_down",&mu_trig_eff_DATA_down_vec);
    tree_input->SetBranchStatus("t_Mu_EffTRIG_MC", 1);
    tree_input->SetBranchAddress("t_Mu_EffTRIG_MC",&mu_trig_eff_MC_vec);
    tree_input->SetBranchStatus("t_Mu_EffTRIG_MC_up", 1);
    tree_input->SetBranchAddress("t_Mu_EffTRIG_MC_up", &mu_trig_eff_MC_up_vec);
    tree_input->SetBranchStatus("t_Mu_EffTRIG_MC_down", 1);
    tree_input->SetBranchAddress("t_Mu_EffTRIG_MC_down", &mu_trig_eff_MC_down_vec);

    tree_input->SetBranchStatus("t_Mu_EffSF_ID", 1);
    tree_input->SetBranchAddress("t_Mu_EffSF_ID", &mu_ID_eff_SF_vec);
    tree_input->SetBranchStatus("t_Mu_EffSF_ID_up", 1);
    tree_input->SetBranchAddress("t_Mu_EffSF_ID_up", &mu_ID_eff_SF_up_vec);
    tree_input->SetBranchStatus("t_Mu_EffSF_ID_down", 1);
    tree_input->SetBranchAddress("t_Mu_EffSF_ID_down", &mu_ID_eff_SF_down_vec);
    tree_input->SetBranchStatus("t_Mu_EffSF_ISO", 1);
    tree_input->SetBranchAddress("t_Mu_EffSF_ISO", &mu_ISO_eff_SF_vec);
    tree_input->SetBranchStatus("t_Mu_EffSF_ISO_up", 1);
    tree_input->SetBranchAddress("t_Mu_EffSF_ISO_up", &mu_ISO_eff_SF_up_vec);
    tree_input->SetBranchStatus("t_Mu_EffSF_ISO_down", 1);
    tree_input->SetBranchAddress("t_Mu_EffSF_ISO_down", &mu_ISO_eff_SF_down_vec);

    tree_input->SetBranchStatus("t_Rho", 1);
    tree_input->SetBranchAddress("t_Rho", &rho);
    tree_input->SetBranchStatus("t_PV_npvsGood", 1);
    tree_input->SetBranchAddress("t_PV_npvsGood", &pv);
    tree_input->SetBranchStatus("t_SoftActivityJetNjets2", 1);
    tree_input->SetBranchAddress("t_SoftActivityJetNjets2", &n_SoftJet_pt2);
    tree_input->SetBranchStatus("t_SoftActivityJetNjets5", 1);
    tree_input->SetBranchAddress("t_SoftActivityJetNjets5", &n_SoftJet_pt5);
    tree_input->SetBranchStatus("t_SoftActivityJetNjets10", 1);
    tree_input->SetBranchAddress("t_SoftActivityJetNjets10", &n_SoftJet_pt10);
 
    tree_input->SetBranchStatus("t_LHEPdfWeight", 1);
    tree_input->SetBranchAddress("t_LHEPdfWeight", &lhe_pdf_weight);
    tree_input->SetBranchStatus("t_LHEScaleWeight", 1);
    tree_input->SetBranchAddress("t_LHEScaleWeight", &lhe_scale_weight);
    
    tree_input->SetBranchStatus("t_SoftActivityJetHT", 1);
    tree_input->SetBranchAddress("t_SoftActivityJetHT", &HT);
    tree_input->SetBranchStatus("t_SoftActivityJetHT2", 1);
    tree_input->SetBranchAddress("t_SoftActivityJetHT2", &HT_pt2);
    tree_input->SetBranchStatus("t_SoftActivityJetHT5", 1);
    tree_input->SetBranchAddress("t_SoftActivityJetHT5", &HT_pt5);
    tree_input->SetBranchStatus("t_SoftActivityJetHT10", 1);
    tree_input->SetBranchAddress("t_SoftActivityJetHT10", &HT_pt10);

    tree_input->SetBranchStatus("t_genWeight", 1);
    tree_input->SetBranchAddress("t_genWeight", &gen_weight);
    // DiMuon variables
    tree_input->SetBranchStatus("t_diMuon_bsConstrainedMass", 1);
    tree_input->SetBranchAddress("t_diMuon_bsConstrainedMass",
                                 &diMuon_bsConstrainedMass);
    tree_input->SetBranchStatus("t_diMuon_bsConstrainedPt", 1);
    tree_input->SetBranchAddress("t_diMuon_bsConstrainedPt",
                                 &diMuon_bsConstrainedPt);
    tree_input->SetBranchStatus("t_diMuon_mass", 1);
    tree_input->SetBranchAddress("t_diMuon_mass", &diMuon_mass);
    tree_input->SetBranchStatus("t_diMuon_pt", 1);
    tree_input->SetBranchAddress("t_diMuon_pt", &diMuon_pt);
    tree_input->SetBranchStatus("t_diMuon_phi", 1);
    tree_input->SetBranchAddress("t_diMuon_phi", &diMuon_phi);
    tree_input->SetBranchStatus("t_diMuon_eta", 1);
    tree_input->SetBranchAddress("t_diMuon_eta", &diMuon_eta);

    // MET varaibles
    tree_input->SetBranchStatus("t_PuppiMET_phi", 1);
    tree_input->SetBranchAddress("t_PuppiMET_phi", &PuppiMET_phi);
    tree_input->SetBranchStatus("t_PuppiMET_pt", 1);
    tree_input->SetBranchAddress("t_PuppiMET_pt", &PuppiMET_pt);
    tree_input->SetBranchStatus("t_PuppiMET_sumEt", 1);
    tree_input->SetBranchAddress("t_PuppiMET_sumEt", &PuppiMET_sumEt);

    // Muon variables
    tree_input->SetBranchStatus("t_mu1", 1);
    tree_input->SetBranchAddress("t_mu1", &mu1_index);
    tree_input->SetBranchStatus("t_mu2", 1);
    tree_input->SetBranchAddress("t_mu2", &mu2_index);
    tree_input->SetBranchStatus("t_Mu_charge", 1);
    tree_input->SetBranchAddress("t_Mu_charge", &mu_charge);
    tree_input->SetBranchStatus("t_Mu_pt", 1);
    tree_input->SetBranchAddress("t_Mu_pt", &mu_pt);
    tree_input->SetBranchStatus("t_Mu_bsConstrainedPt", 1);
    tree_input->SetBranchAddress("t_Mu_bsConstrainedPt", &mu_bsConstrainedPt);
    tree_input->SetBranchStatus("t_Mu_bsConstrainedPt_nanoAOD", 1);
    tree_input->SetBranchAddress("t_Mu_bsConstrainedPt_nanoAOD",
                                 &mu_bsConstrainedPt_nanoAOD);
    tree_input->SetBranchStatus("t_Mu_ptErr", 1);
    tree_input->SetBranchAddress("t_Mu_ptErr", &mu_ptErr);
    tree_input->SetBranchStatus("t_Mu_bsConstrainedPtErr", 1);
    tree_input->SetBranchAddress("t_Mu_bsConstrainedPtErr",
                                 &mu_bsConstrainedPtErr);
    tree_input->SetBranchStatus("t_Mu_phi", 1);
    tree_input->SetBranchAddress("t_Mu_phi", &mu_phi);
    tree_input->SetBranchStatus("t_Mu_eta", 1);
    tree_input->SetBranchAddress("t_Mu_eta", &mu_eta);
    tree_input->SetBranchStatus("t_Mu_dz", 1);
    tree_input->SetBranchAddress("t_Mu_dz", &mu_dz);
    tree_input->SetBranchStatus("t_Mu_dzErr", 1);
    tree_input->SetBranchAddress("t_Mu_dzErr", &mu_dzErr);

    // Electron variables
    tree_input->SetBranchStatus("t_El_pt", 1);
    tree_input->SetBranchAddress("t_El_pt", &elec_pt);

    // Jet variables
    //tree_input->SetBranchStatus("t_nbJet", 1);
    //tree_input->SetBranchAddress("t_nbJet", &n_bjet);
    //tree_input->SetBranchStatus("t_nbJet_Loose", 1);
    //tree_input->SetBranchAddress("t_nbJet_Loose", &n_bjet_Loose);
    //tree_input->SetBranchStatus("t_nJet", 1);
    //tree_input->SetBranchAddress("t_nJet", &n_jet);
    if (!tree_input->GetBranch(jet_pt_branch_name.c_str())) {
        throw std::runtime_error("Jet pT branch not found: " + jet_pt_branch_name);
    }
    tree_input->SetBranchStatus(jet_pt_branch_name.c_str(), 1);
    tree_input->SetBranchAddress(jet_pt_branch_name.c_str(), &jet_pt);

    if (!tree_input->GetBranch(jet_mass_branch_name.c_str())) {
        throw std::runtime_error("Jet Mass branch not found: " + jet_mass_branch_name);
    }
    tree_input->SetBranchStatus(jet_mass_branch_name.c_str(), 1);
    tree_input->SetBranchAddress(jet_mass_branch_name.c_str(), &jet_mass);
    tree_input->SetBranchStatus("t_Jet_phi", 1);
    tree_input->SetBranchAddress("t_Jet_phi", &jet_phi);
    tree_input->SetBranchStatus("t_Jet_eta", 1);
    tree_input->SetBranchAddress("t_Jet_eta", &jet_eta);
    tree_input->SetBranchStatus("t_Jet_btagPNetB", 1);
    tree_input->SetBranchAddress("t_Jet_btagPNetB", &jet_btagPNetB);
    if (jet_syst_name.empty()) {
        if (!tree_input->GetBranch("t_Jet_pt_nanoAOD")) {
            throw std::runtime_error("Jet nanoAOD pT branch not found: t_Jet_pt_nanoAOD");
        }
        tree_input->SetBranchStatus("t_Jet_pt_nanoAOD", 1);
        tree_input->SetBranchAddress("t_Jet_pt_nanoAOD", &jet_pt_nanoAOD);
    }
    tree_input->SetBranchStatus("t_Jet_area", 1);
    tree_input->SetBranchAddress("t_Jet_area", &jet_area);
    tree_input->SetBranchStatus("t_Jet_btagPNetQvG", 1);
    tree_input->SetBranchAddress("t_Jet_btagPNetQvG", &jet_btagPNetQvG);
    tree_input->SetBranchStatus("t_Jet_btagUParTAK4B", 1);
    tree_input->SetBranchAddress("t_Jet_btagUParTAK4B", &jet_btagUParTAK4B);
    tree_input->SetBranchStatus("t_Jet_btagUParTAK4QvG", 1);
    tree_input->SetBranchAddress("t_Jet_btagUParTAK4QvG", &jet_btagUParTAK4QvG);
    tree_input->SetBranchStatus("t_Jet_btagDeepFlavQG", 1);
    tree_input->SetBranchAddress("t_Jet_btagDeepFlavQG", &jet_btagDeepFlavQG);
    tree_input->SetBranchStatus("t_Jet_chEmEF", 1);
    tree_input->SetBranchAddress("t_Jet_chEmEF", &jet_chEmEF);
    tree_input->SetBranchStatus("t_Jet_chHEF", 1);
    tree_input->SetBranchAddress("t_Jet_chHEF", &jet_chHEF);
    tree_input->SetBranchStatus("t_Jet_neEmEF", 1);
    tree_input->SetBranchAddress("t_Jet_neEmEF", &jet_neEmEF);
    tree_input->SetBranchStatus("t_Jet_neHEF", 1);
    tree_input->SetBranchAddress("t_Jet_neHEF", &jet_neHEF);
    tree_input->SetBranchStatus("t_Jet_nConstituents", 1);
    tree_input->SetBranchAddress("t_Jet_nConstituents", &jet_nConstituents);
    tree_input->SetBranchStatus("t_Jet_chMultiplicity", 1);
    tree_input->SetBranchAddress("t_Jet_chMultiplicity", &jet_chMultiplicity);
    tree_input->SetBranchStatus("t_Jet_neMultiplicity", 1);
    tree_input->SetBranchAddress("t_Jet_neMultiplicity", &jet_neMultiplicity);

    // DiJet variables
    tree_input->SetBranchStatus("t_diJet_mass", 1);
    tree_input->SetBranchAddress("t_diJet_mass", &diJet_mass);
    tree_input->SetBranchStatus("t_diJet_mass_mo", 1);
    tree_input->SetBranchAddress("t_diJet_mass_mo", &diJet_mass_mo);
    tree_input->SetBranchStatus("t_diJet_pt", 1);
    tree_input->SetBranchAddress("t_diJet_pt", &diJet_pt);
    tree_input->SetBranchStatus("t_diJet_phi", 1);
    tree_input->SetBranchAddress("t_diJet_phi", &diJet_phi);
    tree_input->SetBranchStatus("t_diJet_eta", 1);
    tree_input->SetBranchAddress("t_diJet_eta", &diJet_eta);

    std::cout << "Input Branches addressed setted" << std::endl;
}

void CreateTuple::fillOutputTree() {

    std::cout << "Filling Output Tree" << std::endl;
    double total_entries = tree_input->GetEntries();
    std::cout << "Entries: " << total_entries << std::endl;
    TLorentzVector mu1_vector;
    TLorentzVector mu2_vector;
    TLorentzVector mu1BSC_vector;
    TLorentzVector mu2BSC_vector;
    TLorentzVector mu1BSC_nanoAOD_vector;
    TLorentzVector mu2BSC_nanoAOD_vector;
    std::pair<float, float> angles_CS;
    std::cout << include_Z << std::endl;
    std::cout << include_H << std::endl;
    for (int event_index = 0; event_index < total_entries; event_index++) {
        tree_input->GetEntry(event_index);
        if ((include_Z && include_H) || (!include_Z && !include_H)){
            if (diMuon_bsConstrainedMass < 70 || diMuon_bsConstrainedMass > 180)
                continue;
        }
        else if (include_Z){
            if(diMuon_bsConstrainedMass < 76 || diMuon_bsConstrainedMass > 106)
                continue;
        }
        else{
            // in Higgs region
            if(diMuon_bsConstrainedMass < 100 || diMuon_bsConstrainedMass > 180)
                continue;
        }
        // if (diMuon_mass < 110 || diMuon_mass > 150)
        // if (diMuon_mass < 100 || diMuon_mass > 180)
        if (diMuon_bsConstrainedMass < 70 || diMuon_bsConstrainedMass > 180)
            continue;

        h_nInFinalMassRange->Fill(0.5);

        if ((*mu_bsConstrainedPt)[mu1_index] < (*mu_bsConstrainedPt)[mu2_index]) {
            std::swap(mu1_index, mu2_index);
        }


        if (!is_data) {

            // Trigger efficiency: DATA
            const float trig_eff_data_mu1 = (*mu_trig_eff_DATA_vec)[mu1_index];
            const float trig_eff_data_mu2 = (*mu_trig_eff_DATA_vec)[mu2_index];

            const float trig_eff_data_event = 1.0 -
                (1.0 - trig_eff_data_mu1) * (1.0 - trig_eff_data_mu2);


            // Trigger efficiency: MC
            const float trig_eff_mc_mu1 = (*mu_trig_eff_MC_vec)[mu1_index];

            const float trig_eff_mc_mu2 = (*mu_trig_eff_MC_vec)[mu2_index];

            const float trig_eff_mc_event = 1.0 -
                (1.0 - trig_eff_mc_mu1) * (1.0 - trig_eff_mc_mu2);


            // Final event trigger SF
            if (trig_eff_mc_event > 0.0) {
                mu_trig_eff_SF = trig_eff_data_event / trig_eff_mc_event;
            } else {
                mu_trig_eff_SF = 1.0;
            }


            // Trigger systematic UP
            const float trig_eff_data_mu1_up = (*mu_trig_eff_DATA_up_vec)[mu1_index];
            const float trig_eff_data_mu2_up = (*mu_trig_eff_DATA_up_vec)[mu2_index];
            const float trig_eff_data_event_up = 1.0 -
                (1.0 - trig_eff_data_mu1_up) * (1.0 - trig_eff_data_mu2_up);

            const float trig_eff_mc_mu1_up = (*mu_trig_eff_MC_up_vec)[mu1_index];
            const float trig_eff_mc_mu2_up = (*mu_trig_eff_MC_up_vec)[mu2_index];
            const float trig_eff_mc_event_up = 1.0 -
                (1.0 - trig_eff_mc_mu1_up) * (1.0 - trig_eff_mc_mu2_up);


            if (trig_eff_mc_event_up > 0.0) {
                mu_trig_eff_SF_up = trig_eff_data_event_up / trig_eff_mc_event_up;
            } else {
                mu_trig_eff_SF_up = 1.0;
            }


            // Trigger systematic DOWN
            const float trig_eff_data_mu1_down = (*mu_trig_eff_DATA_down_vec)[mu1_index];
            const float trig_eff_data_mu2_down = (*mu_trig_eff_DATA_down_vec)[mu2_index];
            const float trig_eff_data_event_down = 1.0 -
                (1.0f - trig_eff_data_mu1_down) * (1.0 - trig_eff_data_mu2_down);

            const float trig_eff_mc_mu1_down = (*mu_trig_eff_MC_down_vec)[mu1_index];
            const float trig_eff_mc_mu2_down = (*mu_trig_eff_MC_down_vec)[mu2_index];
            const float trig_eff_mc_event_down = 1.0 -
                (1.0f - trig_eff_mc_mu1_down) * (1.0 - trig_eff_mc_mu2_down);


            if (trig_eff_mc_event_down > 0.0) {
                mu_trig_eff_SF_down = trig_eff_data_event_down / trig_eff_mc_event_down;
            } else {
                mu_trig_eff_SF_down = 1.0;
            }



            mu_ISO_eff_SF = (*mu_ISO_eff_SF_vec)[mu1_index] *
                            (*mu_ISO_eff_SF_vec)[mu2_index];
            mu_ISO_eff_SF_down = (*mu_ISO_eff_SF_down_vec)[mu1_index] *
                                 (*mu_ISO_eff_SF_down_vec)[mu2_index];
            mu_ISO_eff_SF_up = (*mu_ISO_eff_SF_up_vec)[mu1_index] *
                               (*mu_ISO_eff_SF_up_vec)[mu2_index];

            mu_ID_eff_SF = (*mu_ID_eff_SF_vec)[mu1_index] *
                           (*mu_ID_eff_SF_vec)[mu2_index];
            mu_ID_eff_SF_down = (*mu_ID_eff_SF_down_vec)[mu1_index] *
                                (*mu_ID_eff_SF_down_vec)[mu2_index];
            mu_ID_eff_SF_up = (*mu_ID_eff_SF_up_vec)[mu1_index] *
                              (*mu_ID_eff_SF_up_vec)[mu2_index];

            weight =
                GetEventWeight(gen_weight, pileup_weight, scale_factor,
                               mu_trig_eff_SF, mu_ID_eff_SF, mu_ISO_eff_SF);
            weight_no_eff_sf =
                GetEventWeight(gen_weight, pileup_weight, scale_factor,
                               1, 1, 1);
            weight_no_lumi = weight / luminosity;

        } else {

            mu_trig_eff_SF = 1;
            mu_ID_eff_SF = 1;
            mu_ISO_eff_SF = 1;
            mu_trig_eff_SF_down = 1;
            mu_ID_eff_SF_down= 1;
            mu_ISO_eff_SF_down= 1;
            mu_trig_eff_SF_up = 1;
            mu_ID_eff_SF_up= 1;
            mu_ISO_eff_SF_up= 1;
            
            weight = 1;
            weight_no_lumi = 1;
            weight_no_eff_sf= 1;
        
        }
        
        // Muon variables
        mu1_vector.SetPtEtaPhiM((*mu_pt)[mu1_index], (*mu_eta)[mu1_index],
                                (*mu_phi)[mu1_index], MUON_MASS);
        mu2_vector.SetPtEtaPhiM((*mu_pt)[mu2_index], (*mu_eta)[mu2_index],
                                (*mu_phi)[mu2_index], MUON_MASS);
        mu1BSC_vector.SetPtEtaPhiM((*mu_bsConstrainedPt)[mu1_index],
                                   (*mu_eta)[mu1_index], (*mu_phi)[mu1_index],
                                   MUON_MASS);
        mu2BSC_vector.SetPtEtaPhiM((*mu_bsConstrainedPt)[mu2_index],
                                   (*mu_eta)[mu2_index], (*mu_phi)[mu2_index],
                                   MUON_MASS);

        diMuon_rapidity = (mu1BSC_vector + mu2BSC_vector).Rapidity();

        mu1_pt = (*mu_pt)[mu1_index];
        mu2_pt = (*mu_pt)[mu2_index];
        mu1_bsConstrainedPt_nanoAOD = (*mu_bsConstrainedPt_nanoAOD)[mu1_index];
        mu2_bsConstrainedPt_nanoAOD = (*mu_bsConstrainedPt_nanoAOD)[mu2_index];
        mu1BSC_nanoAOD_vector.SetPtEtaPhiM(mu1_bsConstrainedPt_nanoAOD,
                                           (*mu_eta)[mu1_index], (*mu_phi)[mu1_index],
                                           MUON_MASS);
        mu2BSC_nanoAOD_vector.SetPtEtaPhiM(mu2_bsConstrainedPt_nanoAOD,
                                           (*mu_eta)[mu2_index], (*mu_phi)[mu2_index],
                                           MUON_MASS);
        diMuon_bsConstrainedMass_nanoAOD = (mu1BSC_nanoAOD_vector + mu2BSC_nanoAOD_vector).M();
        mu1_bsConstrainedPt = (*mu_bsConstrainedPt)[mu1_index];
        mu2_bsConstrainedPt = (*mu_bsConstrainedPt)[mu2_index];
        mu1_ptErr = (*mu_ptErr)[mu1_index];
        mu2_ptErr = (*mu_ptErr)[mu2_index];
        mu1_bsConstrainedPtErr = (*mu_bsConstrainedPtErr)[mu1_index];
        mu2_bsConstrainedPtErr = (*mu_bsConstrainedPtErr)[mu2_index];
        mu1_dz = (*mu_dz)[mu1_index];
        mu2_dz = (*mu_dz)[mu2_index];
        mu1_dzErr = (*mu_dzErr)[mu1_index];
        mu2_dzErr = (*mu_dzErr)[mu2_index];
        relative_diMuon_mass_error = std::sqrt(std::pow(mu1_ptErr / mu1_pt, 2) +
                                               std::pow(mu2_ptErr / mu2_pt, 2));
        relative_diMuon_bsConstrainedMass_error = std::sqrt(
            std::pow(mu1_bsConstrainedPtErr / mu1_bsConstrainedPt, 2) +
            std::pow(mu2_bsConstrainedPtErr / mu2_bsConstrainedPt, 2));

        angles_CS = CSAngles(mu1BSC_vector, mu2BSC_vector, (*mu_charge)[mu1_index]);

        mu1_pt_mass_ratio = (*mu_pt)[mu1_index] / diMuon_mass;
        mu2_pt_mass_ratio = (*mu_pt)[mu2_index] / diMuon_mass;
        mu1_bsConstrainedPt_mass_ratio =
            (*mu_bsConstrainedPt)[mu1_index] / diMuon_bsConstrainedMass;
        mu2_bsConstrainedPt_mass_ratio =
            (*mu_bsConstrainedPt)[mu2_index] / diMuon_bsConstrainedMass;
        mu1_eta = (*mu_eta)[mu1_index];
        mu2_eta = (*mu_eta)[mu2_index];
        phi_CS = angles_CS.second;
        cos_theta_CS = angles_CS.first;

        int leading_jet_index = -1;
        int subleading_jet_index = -1;
        n_jet = 0;
        n_bjet = 0;
        n_bjet_Loose = 0;

        float btag_loose_cut = 0.;
        float btag_medium_cut = 0.;
        switch (mc_campaign) {
        case 1:
            btag_loose_cut = 0.047;
            btag_medium_cut = 0.245;
            break;
        case 2:
            btag_loose_cut = 0.0499;
            btag_medium_cut = 0.2605;
            break;
        case 3:
            btag_loose_cut = 0.0358;
            btag_medium_cut = 0.1917;
            break;
        case 4:
            btag_loose_cut = 0.0359;
            btag_medium_cut = 0.1919;
            break;
        case 5:
            btag_loose_cut = 0.0246;
            btag_medium_cut = 0.1272;
            break;
        case 6:
            btag_loose_cut = 0.0246;
            btag_medium_cut = 0.1272;
            break;
        default:
            throw std::runtime_error("Unsupported MC campaign for b-tag cuts");
        }

        const size_t jet_count = jet_pt->size();

        const std::vector<float> *jet_btag_for_selection = nullptr;

        if (mc_campaign == 1 || mc_campaign == 2 ||
            mc_campaign == 3 || mc_campaign == 4) {

            // 2022, 2022EE, 2023, 2023BPix
            jet_btag_for_selection = jet_btagPNetB;

        } else if (mc_campaign == 5 || mc_campaign == 6) {

            // 2024, 2025
            jet_btag_for_selection = jet_btagUParTAK4B;

        } else {
            throw std::runtime_error(
                "Unsupported MC campaign for b-tag discriminator"
            );
        }



        for (size_t jet_index = 0; jet_index < jet_count; ++jet_index) {
            
            if (!passesJetPtSelection(jet_index)) {
                continue;
            }

            ++n_jet;



            const float btag_score =
                jet_btag_for_selection->at(jet_index);

            if (btag_score > btag_loose_cut) {
                ++n_bjet_Loose;
            }

            if (btag_score > btag_medium_cut) {
                ++n_bjet;
            }

            if (leading_jet_index < 0 ||
                jet_pt->at(jet_index) > jet_pt->at(leading_jet_index)) {
                subleading_jet_index = leading_jet_index;
                leading_jet_index = static_cast<int>(jet_index);
            } else if (subleading_jet_index < 0 ||
                       jet_pt->at(jet_index) > jet_pt->at(subleading_jet_index)) {
                subleading_jet_index = static_cast<int>(jet_index);
            }
        }

        if (n_bjet_Loose > 1 || n_bjet > 0) {
            continue;
        }

        h_nBjetRejection->Fill(0.5);

        leading_jet_pt = 0;
        leading_jet_pt_nanoAOD = 0;
        leading_jet_eta = 0;
        leading_jet_mass = -1.;
        leading_jet_area = -1.;

        leading_jet_btagPNetQvG = -1.;
        leading_jet_btagUParTAK4QvG = -1.;
        leading_jet_btagDeepFlavQG = -1.;

        leading_jet_chEmEF = -1.;
        leading_jet_chHEF = -1.;
        leading_jet_neEmEF = -1.;
        leading_jet_neHEF = -1.;

        leading_jet_nConstituents = -1;
        leading_jet_chMultiplicity = -1;
        leading_jet_neMultiplicity = -1;

        subleading_jet_pt = 0;
        subleading_jet_pt_nanoAOD = 0;
        subleading_jet_eta = 0;
        subleading_jet_mass = -1.;
        subleading_jet_area = -1.;

        subleading_jet_btagPNetQvG = -1.;
        subleading_jet_btagUParTAK4QvG = -1.;
        subleading_jet_btagDeepFlavQG = -1.;

        subleading_jet_chEmEF = -1.;
        subleading_jet_chHEF = -1.;
        subleading_jet_neEmEF = -1.;
        subleading_jet_neHEF = -1.;

        subleading_jet_nConstituents = -1;
        subleading_jet_chMultiplicity = -1;
        subleading_jet_neMultiplicity = -1;
    
        diJet_pt = 0;
        diJet_eta = 0;
        diJet_phi = 0;
        diJet_mass = 0;

        delta_eta_diJet = 0;
        delta_phi_diJet = -1;

        z_zeppenfeld = 0;
        pt_balance = -1;
        pt_centrality = -1;

        min_delta_eta_diMuon_jet = 0;
        min_delta_phi_diMuon_jet = 0;
        if (leading_jet_index >= 0) {

            leading_jet_pt = jet_pt->at(leading_jet_index);

            if (jet_syst_name.empty()) {
                leading_jet_pt_nanoAOD = jet_pt_nanoAOD->at(leading_jet_index);
            }

            leading_jet_eta = jet_eta->at(leading_jet_index);
            leading_jet_mass = jet_mass->at(leading_jet_index);
            leading_jet_area = jet_area->at(leading_jet_index);
            leading_jet_btagPNetQvG = jet_btagPNetQvG->at(leading_jet_index);
            leading_jet_btagUParTAK4QvG = jet_btagUParTAK4QvG->at(leading_jet_index);
            leading_jet_btagDeepFlavQG = jet_btagDeepFlavQG->at(leading_jet_index);
            leading_jet_chEmEF = jet_chEmEF->at(leading_jet_index);
            leading_jet_chHEF = jet_chHEF->at(leading_jet_index);
            leading_jet_neEmEF = jet_neEmEF->at(leading_jet_index);
            leading_jet_neHEF = jet_neHEF->at(leading_jet_index);
            leading_jet_nConstituents = jet_nConstituents->at(leading_jet_index);
            leading_jet_chMultiplicity = jet_chMultiplicity->at(leading_jet_index);
            leading_jet_neMultiplicity = jet_neMultiplicity->at(leading_jet_index);

            min_delta_eta_diMuon_jet = DeltaEta(diMuon_eta, jet_eta->at(leading_jet_index));
            min_delta_phi_diMuon_jet = DeltaPhi(diMuon_phi, jet_phi->at(leading_jet_index));
        }

        if (leading_jet_index >= 0 && subleading_jet_index >= 0) {
            subleading_jet_pt = jet_pt->at(subleading_jet_index);
            if (jet_syst_name.empty()) {
                subleading_jet_pt_nanoAOD = jet_pt_nanoAOD->at(subleading_jet_index);
            }
            subleading_jet_eta = jet_eta->at(subleading_jet_index);
            subleading_jet_mass = jet_mass->at(subleading_jet_index);
            subleading_jet_area = jet_area->at(subleading_jet_index);
            subleading_jet_btagPNetQvG = jet_btagPNetQvG->at(subleading_jet_index);
            subleading_jet_btagUParTAK4QvG = jet_btagUParTAK4QvG->at(subleading_jet_index);
            subleading_jet_btagDeepFlavQG = jet_btagDeepFlavQG->at(subleading_jet_index);
            subleading_jet_chEmEF = jet_chEmEF->at(subleading_jet_index);
            subleading_jet_chHEF = jet_chHEF->at(subleading_jet_index);
            subleading_jet_neEmEF = jet_neEmEF->at(subleading_jet_index);
            subleading_jet_neHEF = jet_neHEF->at(subleading_jet_index);
            subleading_jet_nConstituents = jet_nConstituents->at(subleading_jet_index);
            subleading_jet_chMultiplicity = jet_chMultiplicity->at(subleading_jet_index);
            subleading_jet_neMultiplicity = jet_neMultiplicity->at(subleading_jet_index);

            TLorentzVector leading_jet_vector;
            TLorentzVector subleading_jet_vector;
            leading_jet_vector.SetPtEtaPhiM(jet_pt->at(leading_jet_index),
                                            jet_eta->at(leading_jet_index),
                                            jet_phi->at(leading_jet_index),
                                            jet_mass->at(leading_jet_index));
            subleading_jet_vector.SetPtEtaPhiM(jet_pt->at(subleading_jet_index),
                                               jet_eta->at(subleading_jet_index),
                                               jet_phi->at(subleading_jet_index),
                                               jet_mass->at(subleading_jet_index));
            TLorentzVector dijet_vector = leading_jet_vector + subleading_jet_vector;

            diJet_pt = dijet_vector.Pt();
            diJet_eta = dijet_vector.Eta();
            diJet_phi = dijet_vector.Phi();
            diJet_mass = dijet_vector.M();
            delta_eta_diJet = DeltaEta(jet_eta->at(leading_jet_index),
                                       jet_eta->at(subleading_jet_index));
            delta_phi_diJet = DeltaPhi(jet_phi->at(leading_jet_index),
                                       jet_phi->at(subleading_jet_index));

            std::vector<float> ordered_jet_pt = {jet_pt->at(leading_jet_index),
                                                jet_pt->at(subleading_jet_index)};
            std::vector<float> ordered_jet_phi = {jet_phi->at(leading_jet_index),
                                                 jet_phi->at(subleading_jet_index)};
            std::vector<float> ordered_jet_eta = {jet_eta->at(leading_jet_index),
                                                 jet_eta->at(subleading_jet_index)};
            std::vector<float> ordered_jet_mass = {jet_mass->at(leading_jet_index),
                                                  jet_mass->at(subleading_jet_index)};

            z_zeppenfeld = GetZZeppenfeldVariable(diMuon_rapidity,
                                                  &ordered_jet_pt,
                                                  &ordered_jet_phi,
                                                  &ordered_jet_eta,
                                                  &ordered_jet_mass);
            pt_balance = GetPtBalanceVariable(mu1BSC_vector + mu2BSC_vector,
                                              &ordered_jet_pt,
                                              &ordered_jet_phi,
                                              &ordered_jet_eta,
                                              &ordered_jet_mass);
            pt_centrality = GetPtCentralityVariable(diMuon_pt,
                                                    &ordered_jet_pt,
                                                    &ordered_jet_phi,
                                                    &ordered_jet_eta,
                                                    &ordered_jet_mass);

            min_delta_eta_diMuon_jet =
                TMath::Min(DeltaEta(diMuon_eta, jet_eta->at(leading_jet_index)),
                           DeltaEta(diMuon_eta, jet_eta->at(subleading_jet_index)));
            min_delta_phi_diMuon_jet =
                TMath::Min(TMath::Abs(DeltaPhi(diMuon_phi, jet_phi->at(leading_jet_index))),
                           TMath::Abs(DeltaPhi(diMuon_phi, jet_phi->at(subleading_jet_index))));
        }

        // Choose category
        /*if(isJMEJet){
            h_nJMEJets->Fill(0.5);
        }*/
        isggHCategory();
        isVBFCategory();

        tree_output->Fill();
    }

    std::cout << "Output Tuple filled" << std::endl;
}

void CreateTuple::saveTree() {

    gSystem->mkdir(output_directory, true);
    output_file = new TFile(output_directory + output_name, "RECREATE");
    output_file->cd();

    tree_output->Write();
    std::cout << "nEntries at Writing: " << h_nEntries->GetBinContent(1) << std::endl;
    h_nEntries->Write();
    h_nTrigger->Write();
    h_nTwoMuons->Write();
    h_nNoExtraMuon->Write();
    h_nNoExtraElectron->Write();
    h_nTriggerMatch->Write();
    h_nInFinalMassRange->Write();
    h_nBjetRejection->Write();
    h_nJets->Write();
    h_nValidJets->Write();
    h_nValidSeperatedJets->Write();
    h_nValidNotVetoedJets->Write();
    // h_nJMEJets->Write();
    h_n2Jets->Write();
    h_nBothVBFJets->Write();
    h_nVBFEtaSeperated->Write();
    h_nggHEtaSeperated->Write();
    h_nVBFPtPass->Write();
    h_nMjjPass->Write();
    h_nggHCat->Write();
    h_nVBFCat->Write();

    output_file->Close();
    std::cout << "Tuple saved" << std::endl;
}

int CreateTuple::isggHCategory() {

    if ((n_bjet == 0) && (elec_pt->size() == 0)) {
        if (n_jet >= 2) {
            if ((diJet_mass < 400) ||
                (delta_eta_diJet < 2.5) || (leading_jet_pt < 35)) {
                h_nggHEtaSeperated->Fill(0.5);
                h_nggHCat->Fill(0.5);
                is_ggH_category = 1;
                return 1;
            } else {
                is_ggH_category = 0;
                return 2;
            }
        } else {
            h_nggHCat->Fill(0.5);
            is_ggH_category = 1;
            return 3;
        }
    }
    is_ggH_category = 0;
    return 4;
}

int CreateTuple::isVBFCategory() {
    if((n_bjet == 0) && (n_bjet_Loose < 2) && (n_jet >= 2)){
        h_n2Jets->Fill(0.5);
        h_nBothVBFJets->Fill(0.5);
        if(delta_eta_diJet > 2.5){
            h_nVBFEtaSeperated->Fill(0.5);
            if(leading_jet_pt > 35){
                h_nVBFPtPass->Fill(0.5);
                if(diJet_mass >= 400){
                    h_nMjjPass->Fill(0.5);
                }
            }
        }
    }

    if ((n_bjet == 0) && (n_bjet_Loose < 2) &&
        (elec_pt->size() == 0) && (n_jet >= 2) && leading_jet_pt > 35 &&
        (diJet_mass >= 400) && (delta_eta_diJet > 2.5)) {
        h_nVBFCat->Fill(0.5);
        is_VBF_category = 1;
        return 1;
    } else {
        is_VBF_category = 0;
        return 2;
    }
}

bool CreateTuple::passesJetPtSelection(size_t index) const {

    const float pt = jet_pt->at(index);
    const float abs_eta = std::fabs(jet_eta->at(index));

    // Base jet pT cut already used in the old code
    if (pt <= 25.) {
        return false;
    }
    // 2022, 2022EE, 2023, 2023BPix
    if (mc_campaign == 1 || mc_campaign == 2 ||
        mc_campaign == 3 || mc_campaign == 4) {

        if (abs_eta < 2.5) {
            return true;
        } else if (abs_eta < 5.0) {
            return pt > 50.;
        } else {
            return false;
        }
    }

    // 2024
    else if (mc_campaign == 5) {

        if (abs_eta < 2.5) {
            return true;
        } else if (abs_eta < 3.0) {
            return pt > 50.;
        } else {
            return true;
        }
    }

    // 2025
    else if (mc_campaign == 6) {
        return true;
    }

    else {
        std::cerr << "Jet pT era not found. mc_campaign = "
                  << mc_campaign << std::endl;
        return false;
    }
}



/*
bool CreateTuple::isJMEJet() {
    if(mc_campaign == 1 || mc_campaign == 2 || mc_campaign == 3 || mc_campaign == 4){
        if(abs(leading_jet_eta) >= 2.5){
            if(leading_jet_pt < 50 || subleading_jet_pt < 50){
                return false;
            }
            else{
                return true;
            }
        }
    }
    if(mc_campaign == 5){
        if(abs(leading_jet_eta) >= 2.5 && abs(leading_jet_eta) < 3){
            if(leading_jet_pt < 50 || subleading_jet_pt < 50){
                return false;
            }
            else{
                return true;
            }
        }
    }
    return true
}*/
/** MC Campaign variable: 1-22, 2-22EE, 3-23, 4-23BPix, 5-24, 6-25 */

#endif // if LIB_CreateTuple_H
