#ifndef LIB_CreateTuple_H
#define LIB_CreateTuple_H

#include "Constants.h"
#include "Run3Constants.h"
#include "Utils.h"
#include <TChain.h>
#include <TFile.h>
#include "TF1.h"
#include <TH1F.h>
#include <TLorentzVector.h>
#include <TString.h>
#include <TTree.h>
#include <cmath>
#include <iostream>
#include <math.h>
#include <map>

std::map<TString, int> MC_CAMPAIGN_MAP = { {"2022", 1}, {"2022EE", 2}, {"2023", 3}, {"2023BPix", 4}, {"2024", 5}, {"2025", 6}};

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
                bool is_data, bool is_signal_,  bool include_Z, bool include_H);
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

    /** MC Campaign variable: 1-22, 2-22EE, 3-23, 4-23BPix, 5-24, 6-25 */
    int mc_campaign;

    /** Read event variables */
    float gen_weight, pileup_weight, pileup_weight_up, pileup_weight_down;
    int n_SoftJet_pt2, n_SoftJet_pt5, n_SoftJet_pt10;
    float HT, HT_pt2, HT_pt5, HT_pt10;
    /** Read DiMuon variables */
    float diMuon_mass, diMuon_bsConstrainedMass, diMuon_pt, diMuon_bsConstrainedPt, diMuon_phi, diMuon_eta;

    /** Read MET variables **/
    float PuppiMET_phi, PuppiMET_pt, PuppiMET_sumEt;

    /** Read Muon variables */
    int mu1_index, mu2_index;
    std::vector<int> *mu_charge;
    std::vector<float> *mu_pt, *mu_bsConstrainedPt, *mu_phi, *mu_eta, *mu_dz, *mu_dzErr;
    std::vector<float> *mu_ptErr, *mu_bsConstrainedPtErr;

    /** Read electron variables */
    std::vector<float> *elec_pt;

    /** Read Jet variables */
    int n_jet, n_bjet, n_bjet_Loose;
    std::vector<float> *jet_mass, *jet_pt, *jet_phi, *jet_eta, *jet_btagPNetB;

    /** Read Jet variables */
    float diJet_pt, diJet_eta, diJet_phi, diJet_mass, diJet_mass_mo;

    /** New Event variables */
    double scale_factor; // luminosity * cross_section / gen_weight_sum
    Double_t weight;
    double weight_no_lumi;
    float rho;
    int pv;
    // int is_data_int, is_signal_int, pv;
    int is_ggH_category, is_VBF_category;

    /** New DiMuon variables*/
    float diMuon_rapidity;

    /** New Muon variables*/
    float mu1_pt_mass_ratio, mu2_pt_mass_ratio, mu1_bsConstrainedPt_mass_ratio,
          mu2_bsConstrainedPt_mass_ratio, mu1_eta, mu2_eta, phi_CS, cos_theta_CS;
    float mu1_pt, mu2_pt, mu1_bsConstrainedPt, mu2_bsConstrainedPt, mu1_ptErr, mu2_ptErr, mu1_bsConstrainedPtErr, mu2_bsConstrainedPtErr, mu1_dz, mu2_dz, mu1_dzErr, mu2_dzErr;
    /** New Error variables*/
    float relative_diMuon_mass_error, relative_diMuon_bsConstrainedMass_error;

    /** New jets variables*/
    float leading_jet_pt, leading_jet_eta, leading_jet_btagPNetB, subleading_jet_pt, subleading_jet_eta, subleading_jet_btagPNetB;

    /** New DiJets variables*/
    float delta_eta_diJet, delta_phi_diJet, z_zeppenfeld, pt_balance,
        pt_centrality, min_delta_eta_diMuon_jet, min_delta_phi_diMuon_jet;
    
    /** histograms */
    TH1D *h_nEntries, *h_nTrigger, *h_nTwoMuons, *h_nNoExtraMuon, *h_nNoExtraElectron, *h_nTriggerMatch, *h_nBjetRejection;
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

CreateTuple::CreateTuple(TString input, TString weightFile, TString output, TString era,
                         TString channel, bool is_data_, bool is_signal_, bool include_Z_,
                        bool include_H_)
    : luminosity(LUMINOSITY.at(era)), cross_section(CROSS_SECTION.at(channel)) {

    tree_input = new TChain("tree");
    tree_output = new TTree("tree_output", "tree_output");
    input_name = input;
    weight_name = weightFile;
    output_directory = output;
    is_signal = is_signal_;
    include_Z = include_Z_;
    include_H = include_H_;
    analysis_channel = channel;
    is_data = is_data_;

    if(include_Z){
        std::cout << "Z range included" << std::endl;
    }
    if(include_H){
        std::cout << "H range included" << std::endl;
    }

    output_name = channel + "_" + era + "_tuples.root";
    std::cout << "Luminosity: " << luminosity
              << ", cross section: " << cross_section << std::endl;
    if (!is_data) {
        gen_weight_sum = GetGenWeightSum(weight_name);
        if(era == "2024"){
            scale_factor = GetScaleFactor(luminosity + LUMINOSITY.at("2025"), cross_section, gen_weight_sum);
        }
        else{
            scale_factor = GetScaleFactor(luminosity, cross_section, gen_weight_sum);
        }
        // is_data_int = 0;
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
    mu_ptErr = nullptr;
    mu_bsConstrainedPtErr = nullptr;
    mu_phi = nullptr;
    mu_eta = nullptr;
    mu_dz = nullptr;
    mu_dzErr = nullptr;
    elec_pt = nullptr;
    jet_eta = nullptr;
    jet_pt = nullptr;
    jet_phi = nullptr;
    jet_mass = nullptr;
    jet_btagPNetB = nullptr;

    TFile *f_input = TFile::Open(input_name);
    h_nEntries = (TH1D*)f_input->Get("h_nEntries");
    h_nEntries->SetDirectory(0);
    std::cout << "nEntries: " << h_nEntries->GetBinContent(1) << std::endl;
    h_nTrigger = (TH1D*)f_input->Get("h_nTrigger");
    h_nTrigger->SetDirectory(0);
    h_nTwoMuons = (TH1D*)f_input->Get("h_nTwoMuons");
    h_nTwoMuons->SetDirectory(0);
    h_nNoExtraMuon= (TH1D*)f_input->Get("h_nNoExtraMuon");
    h_nNoExtraMuon->SetDirectory(0);
    h_nNoExtraElectron = (TH1D*)f_input->Get("h_nNoExtraElectron");
    h_nNoExtraElectron->SetDirectory(0);
    h_nTriggerMatch = (TH1D*)f_input->Get("h_nTriggerMatch");
    h_nTriggerMatch->SetDirectory(0);
    h_nBjetRejection = (TH1D*)f_input->Get("h_nBjetRejection");
    h_nBjetRejection->SetDirectory(0);
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

    tree_output->Branch("gen_weight", &gen_weight, "gen_weight/f");
    tree_output->Branch("pileup_weight", &pileup_weight, "pileup_weight/f");
    tree_output->Branch("pileup_weight_up", &pileup_weight_up, "pileup_weight_up/f");
    tree_output->Branch("pileup_weight_down", &pileup_weight_down,
                        "pileup_weight_down/f");
    tree_output->Branch("scale_factor", &scale_factor, "scale_factor/d");
    tree_output->Branch("weight", &weight, "weight/D");
    tree_output->Branch("weight_no_lumi", &weight_no_lumi, "weight_no_lumi/d");
    // tree_output->Branch("is_data", &is_data_int, "is_data/i");
    // tree_output->Branch("is_signal", &is_signal_int, "signal/i");
    tree_output->Branch("rho", &rho, "rho/f");
    tree_output->Branch("PV", &pv, "PV/i");
    tree_output->Branch("n_SoftJet_pt2", &n_SoftJet_pt2, "n_SoftJet_pt2/i");
    tree_output->Branch("n_SoftJet_pt5", &n_SoftJet_pt5, "n_SoftJet_pt5/i");
    tree_output->Branch("n_SoftJet_pt10", &n_SoftJet_pt10, "n_SoftJet_pt10/i");
    tree_output->Branch("HT", &HT, "HT/f");
    tree_output->Branch("HT_pt2", &HT_pt2, "HT_pt2/f");
    tree_output->Branch("HT_pt5", &HT_pt5, "HT_pt5/f");
    tree_output->Branch("HT_pt10", &HT_pt10, "HT_pt10/f");

    tree_output->Branch("is_ggH_category", &is_ggH_category,
                        "is_ggH_category/i");
    tree_output->Branch("is_VBF_category", &is_VBF_category,
                        "is_VBF_category/i");

    tree_output->Branch("mc_campaign", &mc_campaign, "mc_campaign/i");
    tree_output->Branch("channel", &analysis_channel);

    // DiMuon variables
    tree_output->Branch("diMuon_mass", &diMuon_mass, "diMuon_mass/f");
    tree_output->Branch("diMuon_bsConstrainedMass", &diMuon_bsConstrainedMass, "diMuon_bsConstrainedMass/f");
    tree_output->Branch("diMuon_pt", &diMuon_pt, "diMuon_pt/f");
    tree_output->Branch("diMuon_bsConstrainedPt", &diMuon_bsConstrainedPt, "diMuon_bsConstrainedPt/f");
    tree_output->Branch("diMuon_phi", &diMuon_phi, "diMuon_phi/f");
    tree_output->Branch("diMuon_eta", &diMuon_eta, "diMuon_eta/f");
    tree_output->Branch("diMuon_rapidity", &diMuon_rapidity,
                        "diMuon_rapidity/f");

    // MET variables
    tree_output->Branch("PuppiMET_phi", &PuppiMET_phi, "PuppiMET_phi/f");
    tree_output->Branch("PuppiMET_pt", &PuppiMET_pt, "PuppiMET_pt/f");
    tree_output->Branch("PuppiMET_sumEt", &PuppiMET_sumEt, "PuppiMET_sumEt/f");

    // Muon variables
    tree_output->Branch("mu1_pt_mass_ratio", &mu1_pt_mass_ratio,
                        "mu1_pt_mass_ratio/f");
    tree_output->Branch("mu2_pt_mass_ratio", &mu2_pt_mass_ratio,
                        "mu2_pt_mass_ratio/f");
    tree_output->Branch("mu1_bsConstrainedPt_mass_ratio", &mu1_bsConstrainedPt_mass_ratio,
                        "mu1_bsConstrainedPt_mass_ratio/f");
    tree_output->Branch("mu2_bsConstrainedPt_mass_ratio", &mu2_bsConstrainedPt_mass_ratio,
                         "mu2_bsConstrainedPt_mass_ratio/f");
    tree_output->Branch("mu1_eta", &mu1_eta, "mu1_eta/f");
    tree_output->Branch("mu2_eta", &mu2_eta, "mu2_eta/f");
    tree_output->Branch("mu1_pt", &mu1_pt, "mu1_pt/f");
    tree_output->Branch("mu2_pt", &mu2_pt, "mu2_pt/f");
    tree_output->Branch("mu1_bsConstrainedPt", &mu1_bsConstrainedPt, "mu1_bsConstrainedPt/f");
    tree_output->Branch("mu2_bsConstrainedPt", &mu2_bsConstrainedPt, "mu2_bsConstrainedPt/f");
    tree_output->Branch("mu1_ptErr", &mu1_ptErr, "mu1_ptErr/f");
    tree_output->Branch("mu2_ptErr", &mu2_ptErr, "mu2_ptErr/f");
    tree_output->Branch("mu1_bsConstrainedPtErr", &mu1_bsConstrainedPtErr, "mu1_bsConstrainedPtErr/f");
    tree_output->Branch("mu2_bsConstrainedPtErr", &mu2_bsConstrainedPtErr, "mu2_bsConstrainedPtErr/f");
    tree_output->Branch("mu1_dz", &mu1_dz, "mu1_dz/f");
    tree_output->Branch("mu2_dz", &mu2_dz, "mu2_dz/f");
    tree_output->Branch("mu1_dzErr", &mu1_dzErr, "mu1_dzErr/f");
    tree_output->Branch("mu2_dzErr", &mu2_dzErr, "mu2_dzErr/f");
    tree_output->Branch("phi_CS", &phi_CS, "phi_CS/f");
    tree_output->Branch("cos_theta_CS", &cos_theta_CS, "cos_theta_CS/f");

    // Error variables
    tree_output->Branch("relative_diMuon_mass_error", &relative_diMuon_mass_error, "relative_diMuon_mass_error/f");
    tree_output->Branch("relative_diMuon_bsConstrainedMass_error", &relative_diMuon_bsConstrainedMass_error, "relative_diMuon_bsConstrainedMass_error/f");

    // Jet variables
    tree_output->Branch("n_jet", &n_jet, "n_jet/i");
    tree_output->Branch("n_bjet", &n_bjet, "n_bjet/i");
    tree_output->Branch("n_bjet_Loose", &n_bjet_Loose, "n_bjet_Loose/i");
    tree_output->Branch("leading_jet_pt", &leading_jet_pt, "leading_jet_pt/f");
    tree_output->Branch("leading_jet_eta", &leading_jet_eta,
                        "leading_jet_eta/f");
    tree_output->Branch("leading_jet_btagPNetB", &leading_jet_btagPNetB,
                        "leading_jet_btagPNetB/f");
    tree_output->Branch("subleading_jet_pt", &subleading_jet_pt,
                        "subleading_jet_pt/f");
    tree_output->Branch("subleading_jet_eta", &subleading_jet_eta,
                        "subleading_jet_eta/f");
    tree_output->Branch("subleading_jet_btagPNetB", &subleading_jet_btagPNetB,
                        "subleading_jet_btagPNetB/f");
    //
    // diJet variables
    tree_output->Branch("diJet_mass", &diJet_mass, "diJet_mass/f");
    tree_output->Branch("delta_eta_diJet", &delta_eta_diJet,
                        "delta_eta_diJet/f");
    tree_output->Branch("delta_phi_diJet", &delta_phi_diJet,
                        "delta_phi_diJet/f");
    tree_output->Branch("z_zeppenfeld", &z_zeppenfeld, "z_zeppenfeld/f");
    tree_output->Branch("pt_balance", &pt_balance, "pt_balance/f");
    tree_output->Branch("pt_centrality", &pt_centrality, "pt_centrality/f");
    tree_output->Branch("min_delta_eta_diMuon_jet", &min_delta_eta_diMuon_jet,
                        "min_delta_eta_diMuon_jet/f");
    tree_output->Branch("min_delta_phi_diMuon_jet", &min_delta_phi_diMuon_jet,
                        "min_delta_phi_diMuon_jet/f");
    // DiJet variables
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
    tree_input->SetBranchAddress("t_diMuon_bsConstrainedMass", &diMuon_bsConstrainedMass);
    tree_input->SetBranchStatus("t_diMuon_bsConstrainedPt", 1);
    tree_input->SetBranchAddress("t_diMuon_bsConstrainedPt", &diMuon_bsConstrainedPt);
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
    tree_input->SetBranchStatus("t_Mu_ptErr", 1);
    tree_input->SetBranchAddress("t_Mu_ptErr", &mu_ptErr);
    tree_input->SetBranchStatus("t_Mu_bsConstrainedPtErr", 1);
    tree_input->SetBranchAddress("t_Mu_bsConstrainedPtErr", &mu_bsConstrainedPtErr);
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
    tree_input->SetBranchStatus("t_nbJet", 1);
    tree_input->SetBranchAddress("t_nbJet", &n_bjet);
    tree_input->SetBranchStatus("t_nbJet_Loose", 1);
    tree_input->SetBranchAddress("t_nbJet_Loose", &n_bjet_Loose);
    tree_input->SetBranchStatus("t_nJet", 1);
    tree_input->SetBranchAddress("t_nJet", &n_jet);
    tree_input->SetBranchStatus("t_Jet_mass", 1);
    tree_input->SetBranchAddress("t_Jet_mass", &jet_mass);
    tree_input->SetBranchStatus("t_Jet_pt", 1);
    tree_input->SetBranchAddress("t_Jet_pt", &jet_pt);
    tree_input->SetBranchStatus("t_Jet_phi", 1);
    tree_input->SetBranchAddress("t_Jet_phi", &jet_phi);
    tree_input->SetBranchStatus("t_Jet_eta", 1);
    tree_input->SetBranchAddress("t_Jet_eta", &jet_eta);
    tree_input->SetBranchAddress("t_Jet_btagPNetB", &jet_btagPNetB);

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
            //in Higgs region
            if(diMuon_bsConstrainedMass < 100 || diMuon_bsConstrainedMass > 180)
                continue;
        }
        // if (diMuon_mass < 110 || diMuon_mass > 150)
        // if (diMuon_mass < 100 || diMuon_mass > 180)
        if (diMuon_bsConstrainedMass < 70 || diMuon_bsConstrainedMass > 180)
            continue;
        
        h_nInFinalMassRange->Fill(0.5);
        
        if(!is_data){
            weight = GetEventWeight(gen_weight, pileup_weight, scale_factor);
            weight_no_lumi = weight / luminosity;
        }

        else{
            weight = 1;
            weight_no_lumi = 1;
        }

        // DiMuon variables
        diMuon_rapidity = (mu1_vector + mu2_vector).Rapidity();

        // Muon variables
        mu1_vector.SetPtEtaPhiM((*mu_pt)[mu1_index], (*mu_eta)[mu1_index],
                                (*mu_phi)[mu1_index], MUON_MASS);
        mu2_vector.SetPtEtaPhiM((*mu_pt)[mu2_index], (*mu_eta)[mu2_index],
                                (*mu_phi)[mu2_index], MUON_MASS);
        mu1BSC_vector.SetPtEtaPhiM((*mu_bsConstrainedPt)[mu1_index], (*mu_eta)[mu1_index],
                                (*mu_phi)[mu1_index], MUON_MASS);
        mu2BSC_vector.SetPtEtaPhiM((*mu_bsConstrainedPt)[mu2_index], (*mu_eta)[mu2_index],
                                (*mu_phi)[mu2_index], MUON_MASS);

        mu1_pt = (*mu_pt)[mu1_index];
        mu2_pt = (*mu_pt)[mu2_index];
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
        relative_diMuon_mass_error = std::sqrt(std::pow(mu1_ptErr/mu1_pt, 2) + std::pow(mu2_ptErr/mu2_pt, 2));
        relative_diMuon_bsConstrainedMass_error = std::sqrt(std::pow(mu1_bsConstrainedPtErr/mu1_bsConstrainedPt, 2) + std::pow(mu2_bsConstrainedPtErr/mu2_bsConstrainedPt, 2));
        
        angles_CS = CSAngles(mu1_vector, mu2_vector, (*mu_charge)[mu1_index]);

        mu1_pt_mass_ratio = (*mu_pt)[mu1_index] / diMuon_mass;
        mu2_pt_mass_ratio = (*mu_pt)[mu2_index] / diMuon_mass;
        mu1_bsConstrainedPt_mass_ratio = (*mu_bsConstrainedPt)[mu1_index] / diMuon_bsConstrainedMass;
        mu2_bsConstrainedPt_mass_ratio = (*mu_bsConstrainedPt)[mu2_index] / diMuon_bsConstrainedMass;
        mu1_eta = (*mu_eta)[mu1_index];
        mu2_eta = (*mu_eta)[mu2_index];
        phi_CS = angles_CS.second;
        cos_theta_CS = angles_CS.first;

        if (n_jet == 0) {
            leading_jet_pt = 0;
            leading_jet_eta = 0;
            leading_jet_btagPNetB = 0;
            diJet_mass = 0;
            subleading_jet_pt = 0;
            subleading_jet_eta = 0;
            delta_eta_diJet = 0;
            delta_phi_diJet = -1;
            z_zeppenfeld = 0;
            pt_balance = -1;
            pt_centrality = -1;
            min_delta_eta_diMuon_jet = 0;
            min_delta_phi_diMuon_jet = 0;
        } else if (n_jet == 1) {
            leading_jet_pt = jet_pt->at(0);
            leading_jet_eta = jet_eta->at(0);
            leading_jet_btagPNetB = jet_btagPNetB->at(0);
            diJet_mass = 0;
            subleading_jet_pt = 0;
            subleading_jet_eta = 0;
            subleading_jet_btagPNetB = 0;
            delta_eta_diJet = 0;
            delta_phi_diJet = -1;
            z_zeppenfeld = 0;
            pt_balance = -1;
            pt_centrality = -1;
            min_delta_eta_diMuon_jet = DeltaEta(diMuon_eta, jet_eta->at(0));
            min_delta_phi_diMuon_jet = DeltaPhi(diMuon_phi, jet_phi->at(0));
        } else {
            leading_jet_pt = jet_pt->at(0);
            leading_jet_eta = jet_eta->at(0);
            leading_jet_btagPNetB = jet_btagPNetB->at(0);
            subleading_jet_pt = jet_pt->at(1);
            subleading_jet_eta = jet_eta->at(1);
            subleading_jet_btagPNetB = jet_btagPNetB->at(1);
            delta_eta_diJet = DeltaEta(jet_eta->at(0), jet_eta->at(1));
            delta_phi_diJet = DeltaPhi(jet_phi->at(0), jet_phi->at(1));
            z_zeppenfeld = GetZZeppenfeldVariable(diMuon_rapidity, jet_pt,
                                                  jet_phi, jet_eta, jet_mass);
            pt_balance = GetPtBalanceVariable(mu1_vector + mu2_vector,
                                              jet_pt, jet_phi, jet_eta,
                                              jet_mass);
            pt_centrality = GetPtCentralityVariable(diMuon_pt, jet_pt, jet_phi,
                                                    jet_eta, jet_mass);
            min_delta_eta_diMuon_jet =
                TMath::Min(DeltaEta(diMuon_eta, jet_eta->at(0)),
                           DeltaEta(diMuon_eta, jet_eta->at(1)));
            min_delta_phi_diMuon_jet =
                TMath::Min(TMath::Abs(DeltaPhi(diMuon_phi, jet_phi->at(0))),
                           TMath::Abs(DeltaPhi(diMuon_phi, jet_phi->at(1))));
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
    //h_nJMEJets->Write();
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

    if ((n_bjet == 0) && (mu_pt->size() < 3) && (elec_pt->size() == 0)) {
        if (n_jet >= 2) {
            if ((diJet_mass < 400) ||
                (DeltaEta(jet_eta->at(0), jet_eta->at(1)) < 2.5) || (leading_jet_pt < 35)) {
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
    if((n_bjet == 0) && (n_bjet_Loose < 2) && n_jet >= 2 && (mu_pt->size() < 3)){
        h_n2Jets->Fill(0.5);
        h_nBothVBFJets->Fill(0.5);
        if(DeltaEta(jet_eta->at(0), jet_eta->at(1)) > 2.5){
            h_nVBFEtaSeperated->Fill(0.5);
            if(leading_jet_pt > 35){
                h_nVBFPtPass->Fill(0.5);
                if(diJet_mass >= 400){
                    h_nMjjPass->Fill(0.5);
                }
            }
        }
    }

    if ((n_bjet == 0) && (n_bjet_Loose < 2) && (mu_pt->size() < 3) &&
        (elec_pt->size() == 0) && (n_jet >= 2) && leading_jet_pt > 35 &&
        (diJet_mass >= 400) && (DeltaEta(jet_eta->at(0), jet_eta->at(1)) > 2.5)) {
        h_nVBFCat->Fill(0.5);
        is_VBF_category = 1;
        return 1;
    } else {
        is_VBF_category = 0;
        return 2;
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
