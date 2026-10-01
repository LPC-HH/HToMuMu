#define HmmAnalyzer_cxx
#include "../lib/HmmAnalyzer.h"
#include <TCanvas.h>
#include <TH2.h>
#include <TStyle.h>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>
#include <chrono>
#include <algorithm>
#include <cctype>
#include <stdexcept>
#include <Math/Vector4D.h>

#include "../lib/JecApplication.h"
#include "../lib/JecConfigReader.h"
#include "../lib/JetCorrector.h"
#include "../lib/JvmApplication.h"
#include "../lib/JvmConfigReader.h"
#include "../lib/LeptonEfficiencyCorrector.h"
#include "../lib/MuonScaRe.h"
#include "correction.h"

#ifdef MAKECINT
#pragma link C++ class vector < float> + ;
#endif
#ifdef MAKECINT
#pragma link C++ class vector < int> + ;
#endif
#ifdef MAKECINT
#pragma link C++ class vector < bool> + ;
#endif

int main(int argc, char *argv[]) {

    if (argc != 9) {
        std::cerr << "Please give 8 arguments: runList outputFileName dataset "
          << "dataType(T/F) year include_Z(T/F) include_H(T/F) "
          << "muon_pt_syst" << std::endl;
        return -1;
    }
    const char *inputFileList = argv[1];
    const char *outFileName = argv[2];
    const char *data = argv[3];
    // const char *is_data = argv[4];
    const bool is_data_input = *argv[4] == 'T';
    TString year_num = argv[5];
    const bool include_Z = *argv[6] == 'T';
    const bool include_H = *argv[7] == 'T';
    const std::string muon_pt_syst = NormalizeMuonPtSyst(argv[8]);

    //std::cout << year_num.Data() << std::endl;

    HmmAnalyzer Hmm(inputFileList, outFileName, data, is_data_input, year_num,
                    include_Z, include_H);
    Hmm.muon_pt_syst = muon_pt_syst;
    Hmm.apply_muon_pt_syst_to_signal =
        !is_data_input && muon_pt_syst != "nominal";
    std::cout << "Running on: " << std::endl;
    std::cout << "  Dataset: " << data << " year " << year_num << std::endl;
    std::cout << "  Era:  " << year_num << std::endl;
    std::cout << std::boolalpha;
    std::cout << "  Is data? " << is_data_input << std::endl;
    std::cout << "  Year num: " << year_num << std::endl;
    std::cout << "  Include Z? " << include_Z << std::endl;
    std::cout << "  Include H? " << include_H << std::endl;
    std::cout << "  Muon pT systematic: " << muon_pt_syst << std::endl;
    std::cout << "  Apply muon pT systematic? "
              << Hmm.apply_muon_pt_syst_to_signal << std::endl;
    Hmm.EventLoop();

    return 0;
}

void HmmAnalyzer::EventLoop() {

    if (fChain == 0)
        return;

    //read run3 muon efficiency json files
    initializeMuonScaReCorrections(yearst);

    LeptonEfficiencyCorrector corrector;
    if (!is_data){
        corrector.initializeCorrections(yearst);
    }
    //JetCorrector jetCorrector;
    //JetCorrector jetCorrector;
    //jetCorrector.initializeCorrections(yearst);

    JecConfigReader::ConfigPaths jecConfigPaths;
    jecConfigPaths.ak4 = "./data/jetCorrections/JecConfigAK4.json";
    jecConfigPaths.ak8 = "./data/jetCorrections/JecConfigAK8.json";
    JecConfigReader::JecConfig::setDefaultPaths(jecConfigPaths);

    JecConfigReader::JecConfig::setDefaultJerSmearPath(
        "./data/jetCorrections/jer_smear.json.gz");
    JvmConfigReader::JvmConfig::setDefaultConfigPath(
        "./data/jetCorrections/JvmConfig.json");

    JecConfigReader::JecConfig &jec_config =
        JecConfigReader::JecConfig::defaultInstance();
    const std::string jec_year = GetJercYear(yearst);
    const std::string jec_data_era = GetJercEra(jec_year);

    JvmConfigReader::Jvm jvm_config =
        JvmConfigReader::JvmConfig::defaultInstance().getJvmForYear(jec_year);
    JvmApplication::VetoChecker jvm_checker(jvm_config.ref, jvm_config.key);

    std::unique_ptr<JecApplication::Applier> mc_jec_applier;
    std::map<std::string, correction::Correction::Ref> jes_uncertainties;
    std::map<std::string, JecConfigReader::JerBin> jer_uncertainty;
   
   if (!is_data) {
        mc_jec_applier = std::make_unique<JecApplication::Applier>(
            JecApplication::Applier::McAK4(jec_config, jec_year, false));

        JecConfigReader::JesUncSetRefs jes_uncertainty_sets =
            jec_config.getJesUncSetsMcAK4Ref(jec_year);

        const auto &reduced_uncertainty_set = jes_uncertainty_sets.reduced;

        for (const auto &uncertainty_name : jet_jes_syst_names) {
            if (!JecSystAppliesToYear(uncertainty_name, yearst)) {
                continue;
            }

            auto uncertainty = reduced_uncertainty_set.find(uncertainty_name);

            if (uncertainty == reduced_uncertainty_set.end()) {
                throw std::runtime_error(
                    "ERROR: JES uncertainty not found in reduced set: " +
                    uncertainty_name +
                    " for year " + yearst);
            }

            jes_uncertainties.emplace(uncertainty_name, uncertainty->second);
        }

        JecConfigReader::JerUncSets jer_uncertainty_sets =
            jec_config.getJerUncSetsMcAK4(jec_year);

        const auto &jer_full_uncertainty_set = jer_uncertainty_sets.full;

        for (const auto &uncertainty_name : jet_jer_syst_names) {
            if (!JecSystAppliesToYear(uncertainty_name, yearst)) {
                continue;
            }

            auto uncertainty = jer_full_uncertainty_set.find(uncertainty_name);

            if (uncertainty == jer_full_uncertainty_set.end()) {
                throw std::runtime_error(
                    "ERROR: JER uncertainty not found in full set: " +
                    uncertainty_name +
                    " for year " + yearst);
            }

            jer_uncertainty.emplace(uncertainty_name, uncertainty->second);
        }
    }


    // btag SF
    BTagCalibration calib("deepcsv", "./data/btagSF/DeepCSV_94XSF_V3_B_F.csv");
    BTagCalibrationReader reader(BTagEntry::OP_MEDIUM, // operating point
                                 "central",            // central sys type
                                 {"up", "down"});      // other sys types

    reader.load(calib,             // calibration instance
                BTagEntry::FLAV_B, // btag flavour
                "comb");           // measurement type

    std::cout << "Btag calibration loaded" << std::endl;           
    long nentries = fChain->GetEntriesFast();
    //h_nEntries->SetBinContent(1, nentries);
    //nentries = 5000;
    long nbytes = 0;
    long nb = 0;
    
    std::cout << "Number of entries to process: " << nentries << std::endl;
    auto start_time = std::chrono::high_resolution_clock::now();
    for (long jentry = 0; jentry < nentries; jentry++) {
        long ientry = LoadTree(jentry);
        if (ientry < 0)
            break;

        nb = fChain->GetEntry(jentry);
        nbytes += nb;


        if (!is_data && yearst == "2024" && event % 2 == 0) {
            continue;
        }
        if (!is_data && yearst == "2025" && event % 2 != 0) {
            continue;
        }

        h_nEntries->Fill(0.5);
       
        //std::cout << "-------------- Entry " << jentry << " --------------" << std::endl;

        if (jentry % 5000 == 0)
            std::cout << "entry: " << jentry << std::endl;
        clearTreeVectors();

        // sum of genWeight
        float value_h_sumOfgw = h_sumOfgw->GetBinContent(1);
        // sum of genWeight and pileupweight
        float value_h_sumOfgpw = h_sumOfgpw->GetBinContent(1);
        float puWeight, puWeightUp, puWeightDown;


        if (!is_data) {
            value_h_sumOfgw = value_h_sumOfgw + genWeight;
            puWeight = getPileupWeight(Pileup_nTrueInt);
            puWeightUp = getPileupWeightUp(Pileup_nTrueInt);
            puWeightDown = getPileupWeightDown(Pileup_nTrueInt);
            h_pileup->Fill(Pileup_nPU);
            h_pileup_nTrue->Fill(Pileup_nTrueInt);

            value_h_sumOfgpw = value_h_sumOfgpw + genWeight * puWeight;

            for (unsigned int i = 0; i < nLHEPdfWeight; i++) {
                t_LHEPdfWeight->push_back(LHEPdfWeight[i]);
            }

            for (unsigned int i = 0; i < nLHEScaleWeight; i++) {
                t_LHEScaleWeight->push_back(LHEScaleWeight[i]);
            }

            for (unsigned int i = 0; i < nLHEPdfWeight; i++) {
                h_sumOfLHEPdfWeight->AddBinContent(
                    i + 1,
                    genWeight * LHEPdfWeight[i]
                );
            }

            // Sum scale weights over all events
            for (unsigned int i = 0; i < nLHEScaleWeight; i++) {
                h_sumOfLHEScaleWeight->AddBinContent(
                    i + 1,
                    genWeight * LHEScaleWeight[i]
                );
            }

        } else {
            value_h_sumOfgw = value_h_sumOfgw + 1.0;
            value_h_sumOfgpw = value_h_sumOfgpw + 1.0;
            
            t_LHEPdfWeight->assign(N_LHE_PDF_WEIGHTS, 1.0f);
            t_LHEScaleWeight->assign(N_LHE_SCALE_WEIGHTS, 1.0f);

            if (is_data) {

                for (unsigned int i = 0; i < N_LHE_PDF_WEIGHTS; i++) {
                    h_sumOfLHEPdfWeight->SetBinContent(i + 1, 1.0);
                }

                for (unsigned int i = 0; i < N_LHE_SCALE_WEIGHTS; i++) {
                    h_sumOfLHEScaleWeight->SetBinContent(i + 1, 1.0);
                }
            }


        }
        
        h_sumOfgw->SetBinContent(1, value_h_sumOfgw);
        h_sumOfgpw->SetBinContent(1, value_h_sumOfgpw);


        bool trig_decision = (HLT_IsoMu24 == 1);

        bool run_trig_checks = 
            (trig_decision && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter &&
             Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_goodVertices &&
             Flag_globalSuperTightHalo2016Filter && PV_npvsGood > 0);

        if(!run_trig_checks) {
            continue;
        }

        h_nTrigger->Fill(0.5);

        bool run_muChecks =
            (nMuon >= 2 && Flag_BadPFMuonFilter &&
             Flag_BadChargedCandidateFilter);
        
        //std::cout << "Running muon checks" << std::endl; 
        if (!run_muChecks) {
            //std::cout << "Muon checks valid" << std::endl; 
            continue;
        }

        //add in MET variable
        t_PuppiMET_phi = PuppiMET_phi;
        t_PuppiMET_pt = PuppiMET_pt;
        t_PuppiMET_sumEt = PuppiMET_sumEt;

        int index_mu1 = INT_NULL_VALUE;
        int index_mu2 = INT_NULL_VALUE;
        std::vector<float> mu_pt_corr(nMuon, FLOAT_NULL_VALUE);
        std::vector<float> mu_ptErr_corr(nMuon, FLOAT_NULL_VALUE);
        int n_valid_muons = 0;
        bool two_valid_muons = false;
        bool trig_match = false;

        for (int i = 0; i < nMuon; i++) {
            const float pt_raw = Muon_bsConstrainedPt[i];

            // Nominal scale correction
            float pt_scaled = pt_scale(is_data, pt_raw, Muon_eta[i],
                                       Muon_phi[i], Muon_charge[i]);

            float pt_corr = pt_scaled;

            if (!is_data) {
                // Nominal MC smearing
                pt_corr = pt_resol(pt_scaled, Muon_eta[i], Muon_phi[i],
                                   Muon_nTrackerLayers[i],
                                   static_cast<int>(event),
                                   static_cast<int>(luminosityBlock));

                // Scale systematic
                if (apply_muon_pt_syst_to_signal &&
                    IsMuonScaleSyst(muon_pt_syst)) {
                    pt_corr = pt_scale_var(pt_corr, Muon_eta[i], Muon_phi[i],
                                           Muon_charge[i],
                                           MuonSystDirection(muon_pt_syst));
                }
                // Resolution smearring systematic
                if (apply_muon_pt_syst_to_signal &&
                    IsMuonSmearingSyst(muon_pt_syst)) {
                    pt_corr = pt_resol_var(pt_scaled, pt_corr, Muon_eta[i],
                                           MuonSystDirection(muon_pt_syst));
                }

            }

            float ptErr_corr = Muon_bsConstrainedPtErr[i];
            if (pt_raw > 0.0) {
                ptErr_corr *= pt_corr / pt_raw;
            }

            mu_pt_corr[i] = pt_corr;
            mu_ptErr_corr[i] = ptErr_corr;

            if (pt_corr > 10 &&
                fabs(Muon_eta[i]) < 2.4 &&
                Muon_isGlobal[i] &&
                Muon_pfRelIso04_all[i] < 0.25 &&
                Muon_looseId[i]) {
                n_valid_muons++;
            }
        }

        if(n_valid_muons < 2){
            continue;
        }

        float best_pair_pt_sum = -1.0;

        for (int muon_index_1 = 0; muon_index_1 < nMuon; muon_index_1++) {

            if (!(Muon_isGlobal[muon_index_1] &&
                  mu_pt_corr[muon_index_1] > muon_pt_cut.at(yearst) &&
                  Muon_mediumId[muon_index_1] &&
                  fabs(Muon_eta[muon_index_1]) < 2.4 &&
                  Muon_pfRelIso04_all[muon_index_1] < 0.25))
                continue;

            for (int muon_index_2 = muon_index_1 + 1;
                 muon_index_2 < nMuon;
                 muon_index_2++) {

                if (!(Muon_isGlobal[muon_index_2] &&
                      Muon_charge[muon_index_1] * Muon_charge[muon_index_2] == -1 &&
                      mu_pt_corr[muon_index_2] > 20. &&
                      Muon_mediumId[muon_index_2] &&
                      fabs(Muon_eta[muon_index_2]) < 2.4 &&
                      Muon_pfRelIso04_all[muon_index_2] < 0.25))
                    continue;

                float pair_pt_sum =
                    mu_pt_corr[muon_index_1] + mu_pt_corr[muon_index_2];

                if (pair_pt_sum > best_pair_pt_sum) {
                    best_pair_pt_sum = pair_pt_sum;

                    // Store the higher-pT muon as mu1
                    if (mu_pt_corr[muon_index_1] >= mu_pt_corr[muon_index_2]) {
                        index_mu1 = muon_index_1;
                        index_mu2 = muon_index_2;
                    } else {
                        index_mu1 = muon_index_2;
                        index_mu2 = muon_index_1;
                    }

                    two_valid_muons = true;
                }
            }
        }
        //std::cout << "Checking 2 valid muons" << std::endl; 
        if(!two_valid_muons){
            //std::cout << "No valid muons" << std::endl; 
            continue;
        }

        h_nTwoMuons->Fill(0.5);

        //Ensure only 3 Muons
        if(n_valid_muons > 2){
            continue;
        }

        h_nNoExtraMuon->Fill(0.5);


        for (int i = 0; i < nElectron; i++) {
            if ((fabs(Electron_eta[i]) > 2.5 || Electron_pt[i] < 10.0 || fabs(Electron_dz[i]) > 1.0 
                    || fabs(Electron_dxy[i]) > 0.5 || !Electron_mvaIso_WP90[i])) {
                continue;
            }
            // t_El_genPartIdx->push_back(Electron_genPartIdx[i]);
            // t_El_genPartFlav->push_back(Electron_genPartFlav[i]);
            t_El_charge->push_back(Electron_charge[i]);
            t_El_pt->push_back(Electron_pt[i]);
            t_El_phi->push_back(Electron_phi[i]);
            t_El_eta->push_back(Electron_eta[i]);
            t_El_mass->push_back(Electron_mass[i]);
            t_El_cutBased->push_back(Electron_cutBased[i]);
            t_El_tightCharge->push_back(Electron_tightCharge[i]);
            t_El_cutBased_HEEP->push_back(Electron_cutBased_HEEP[i]);
            t_El_isPFcand->push_back(Electron_isPFcand[i]);
            t_El_pfRelIso03_all->push_back(Electron_pfRelIso03_all[i]);
            t_El_pfRelIso03_chg->push_back(Electron_pfRelIso03_chg[i]);
            t_El_miniPFRelIso_all->push_back(Electron_miniPFRelIso_all[i]);
            t_El_miniPFRelIso_chg->push_back(Electron_miniPFRelIso_chg[i]);
            t_El_dxy->push_back(Electron_dxy[i]);
            t_El_dxyErr->push_back(Electron_dxyErr[i]);
            t_El_dz->push_back(Electron_dz[i]);
            t_El_dzErr->push_back(Electron_dzErr[i]);
            t_El_sip3d->push_back(Electron_sip3d[i]);
            t_Electron_mvaFall17Iso->push_back(Electron_mvaIso[i]);
            t_Electron_mvaFall17Iso_WP80->push_back(Electron_mvaIso_WP80[i]);
            t_Electron_mvaFall17Iso_WP90->push_back(Electron_mvaIso_WP90[i]);
            // t_Electron_mvaFall17Iso_WPL->push_back(Electron_mvaFall17V2Iso_WPL[i]);
            t_Electron_mvaFall17noIso->push_back(Electron_mvaNoIso[i]);
            t_Electron_mvaFall17noIso_WP80->push_back(
                Electron_mvaNoIso_WP80[i]);
            t_Electron_mvaFall17noIso_WP90->push_back(
                Electron_mvaNoIso_WP90[i]);
            // t_Electron_mvaFall17noIso_WPL->push_back(Electron_mvaFall17V2noIso_WPL[i]);
        }

        if (t_El_pt->size() > 0){
            continue;
        }

        h_nNoExtraElectron->Fill(0.5);
    
        bool trig_match_mu1 = false;
        bool trig_match_mu2 = false;
        for (int trigger_index = 0; trigger_index < nTrigObj; trigger_index++) {
            //  float dR_TrigObj = 999.;
            if (TrigObj_id[trigger_index] != 13 || !(TrigObj_filterBits[trigger_index] & (1 << 1))) 
                continue;
            float dR_TrigObj;
            if (!trig_match_mu1){
                dR_TrigObj =
                    DeltaR(Muon_eta[index_mu1], Muon_phi[index_mu1],
                           TrigObj_eta[trigger_index], TrigObj_phi[trigger_index]);
                if (dR_TrigObj < 0.1 && Muon_tightId[index_mu1] &&
                    Muon_pfRelIso04_all[index_mu1] < 0.15 &&
                    mu_pt_corr[index_mu1] > muon_pt_cut.at(yearst)) {
                    //trig_match = true;
                    t_index_trigm_mu = 1;
                    trig_match_mu1 = true;
                    //break;
                }
            }
            if (!trig_match_mu2){
                dR_TrigObj =
                    DeltaR(Muon_eta[index_mu2], Muon_phi[index_mu2],
                           TrigObj_eta[trigger_index], TrigObj_phi[trigger_index]);
                if (mu_pt_corr[index_mu2] > muon_pt_cut.at(yearst) &&
                    Muon_tightId[index_mu2] &&
                    Muon_pfRelIso04_all[index_mu2] < 0.15 && dR_TrigObj < 0.1) {
                    //trig_match = true;
                    t_index_trigm_mu = 2;
                    trig_match_mu2 = true;
                    //break;
                }
            }
        } // end of triger match, end of loop over trigger objects
        trig_match= trig_match_mu1 || trig_match_mu2;

        //std::cout << "Checking trig match" << std::endl; 
        if (!trig_match) {
            continue;
        }

        h_nTriggerMatch->Fill(0.5);



        t_run = run;
        t_luminosityBlock = luminosityBlock;
        t_event = event;
        // std::cout<<jentry<<" : "<<t_event<<"-------------------\n";
        int t_index_mu1 = INT_NULL_VALUE;
        int t_index_mu2 = INT_NULL_VALUE;
        int t_index = 0;
        for (int i = 0; i < nMuon; i++) {
            // if(fabs(Muon_eta[i])<2.4 && Muon_mediumId[i] &&
            // Muon_pfRelIso04_all[i] < 0.25){
            if (!(fabs(Muon_eta[i]) < 2.4 && Muon_mediumId[i])) {
                continue;
            }
            
            bool this_muon_trig_matched = false;

            if (i == index_mu1) {
                t_index_mu1 = t_index;
                this_muon_trig_matched = trig_match_mu1;
            }
            else if (i == index_mu2) {
                t_index_mu2 = t_index;
                this_muon_trig_matched = trig_match_mu2;
            }

            t_Mu_charge->push_back(Muon_charge[i]);
            t_Mu_pt->push_back(Muon_pt[i]);
            t_Mu_ptErr->push_back(Muon_ptErr[i]);
            t_Mu_bsConstrainedPt->push_back(mu_pt_corr[i]);
            t_Mu_bsConstrainedPtErr->push_back(mu_ptErr_corr[i]);
            t_Mu_bsConstrainedPt_nanoAOD->push_back(Muon_bsConstrainedPt[i]);
            t_Mu_bsConstrainedPtErr_nanoAOD->push_back(Muon_bsConstrainedPtErr[i]);
            t_Mu_phi->push_back(Muon_phi[i]);
            t_Mu_eta->push_back(Muon_eta[i]);
            t_Mu_mass->push_back(MUON_MASS); // Muon_mass[i]);
            t_Mu_dxy->push_back(Muon_dxy[i]);
            t_Mu_dxyErr->push_back(Muon_dxyErr[i]);
            t_Mu_dz->push_back(Muon_dz[i]);
            t_Mu_dzErr->push_back(Muon_dzErr[i]);
            t_Mu_sip3d->push_back(Muon_sip3d[i]);
            t_Mu_pfRelIso03_all->push_back(Muon_pfRelIso03_all[i]);
            t_Mu_pfRelIso03_chg->push_back(Muon_pfRelIso03_chg[i]);
            t_Mu_pfRelIso04_all->push_back(Muon_pfRelIso04_all[i]);
            t_Mu_miniPFRelIso_all->push_back(Muon_miniPFRelIso_all[i]);
            t_Mu_miniPFRelIso_chg->push_back(Muon_miniPFRelIso_chg[i]);
            t_Mu_tightCharge->push_back(Muon_tightCharge[i]);
            t_Mu_isPFcand->push_back(Muon_isPFcand[i]);
            // t_Mu_isglobal->push_back(Muon_isglobal[i]);
            // t_Mu_istracker->push_back(Muon_istracker[i]);
            t_Mu_looseId->push_back(Muon_looseId[i]);
            t_Mu_mediumId->push_back(Muon_mediumId[i]);
            t_Mu_softId->push_back(Muon_softId[i]);
            t_Mu_tightId->push_back(Muon_tightId[i]);
            t_Mu_nStations->push_back(Muon_nStations[i]);
            t_Mu_nTrackerLayers->push_back(Muon_nTrackerLayers[i]);
            t_index++;

            if (is_data) {
                continue;
            }

            
            t_Mu_EffTRIG_DATA->push_back(corrector.give_eff(
                "Muon_eff_DATAeff_TRIG",
                mu_pt_corr[i], Muon_eta[i]));

            t_Mu_EffTRIG_DATA_up->push_back(corrector.give_eff(
                "Muon_eff_DATAeff_TRIG_up",
                mu_pt_corr[i], Muon_eta[i]));

            t_Mu_EffTRIG_DATA_down->push_back(corrector.give_eff(
                "Muon_eff_DATAeff_TRIG_down",
                mu_pt_corr[i], Muon_eta[i]));


            t_Mu_EffTRIG_MC->push_back(corrector.give_eff(
                "Muon_eff_MCeff_TRIG",
                mu_pt_corr[i], Muon_eta[i]));

            t_Mu_EffTRIG_MC_up->push_back(corrector.give_eff(
                "Muon_eff_MCeff_TRIG_up",
                mu_pt_corr[i], Muon_eta[i]));

            t_Mu_EffTRIG_MC_down->push_back(corrector.give_eff(
                "Muon_eff_MCeff_TRIG_down",
                mu_pt_corr[i], Muon_eta[i]));



            t_Mu_EffSF_ID->push_back(corrector.give_eff("Muon_eff_SF_ID", mu_pt_corr[i], Muon_eta[i]));
            t_Mu_EffSF_ID_up->push_back(corrector.give_eff("Muon_eff_SF_ID_up", mu_pt_corr[i], Muon_eta[i]));
            t_Mu_EffSF_ID_down->push_back(corrector.give_eff("Muon_eff_SF_ID_down", mu_pt_corr[i], Muon_eta[i]));

            
            t_Mu_EffSF_ISO->push_back(corrector.give_eff("Muon_eff_SF_ISO", mu_pt_corr[i], Muon_eta[i]));
            t_Mu_EffSF_ISO_up->push_back(corrector.give_eff("Muon_eff_SF_ISO_up", mu_pt_corr[i], Muon_eta[i]));
            t_Mu_EffSF_ISO_down->push_back(corrector.give_eff("Muon_eff_SF_ISO_down", mu_pt_corr[i], Muon_eta[i]));
        }


        t_mu1 = t_index_mu1;
        t_mu2 = t_index_mu2;
        if (t_index_trigm_mu == 1)
            t_index_trigm_mu = t_mu1;
        else if (t_index_trigm_mu == 2)
            t_index_trigm_mu = t_mu2;

        // TLorentzVector dimu, mu1, mu2;
        ROOT::Math::PtEtaPhiMVector dimu;
        ROOT::Math::PtEtaPhiMVector mu1((Muon_pt)[index_mu1],
                                        (Muon_eta)[index_mu1],
                                        (Muon_phi)[index_mu1], MUON_MASS);
        ROOT::Math::PtEtaPhiMVector mu2((Muon_pt)[index_mu2],
                                        (Muon_eta)[index_mu2],
                                        (Muon_phi)[index_mu2], MUON_MASS);

        ROOT::Math::PtEtaPhiMVector dimuBSC;
        ROOT::Math::PtEtaPhiMVector mu1BSC((mu_pt_corr)[index_mu1],
                                        (Muon_eta)[index_mu1],
                                        (Muon_phi)[index_mu1], MUON_MASS);
        ROOT::Math::PtEtaPhiMVector mu2BSC((mu_pt_corr)[index_mu2],
                                        (Muon_eta)[index_mu2],
                                        (Muon_phi)[index_mu2], MUON_MASS);
        // mu1.SetPtEtaPhiM((mu_pt_corr)[index_mu1], (Muon_eta)[index_mu1],
        //(Muon_phi)[index_mu1], MUON_MASS);
        // mu2.SetPtEtaPhiM((mu_pt_corr)[index_mu2], (Muon_eta)[index_mu2],
        //(Muon_phi)[index_mu2], MUON_MASS);
        dimu = mu1 + mu2;
        dimuBSC = mu1BSC + mu2BSC;
        t_diMuon_pt = dimu.Pt();
        t_diMuon_eta = dimuBSC.Eta();
        t_diMuon_phi = dimuBSC.Phi();
        t_diMuon_mass = dimu.M();

        t_diMuon_bsConstrainedPt = dimuBSC.Pt();
        t_diMuon_bsConstrainedMass = dimuBSC.M();

        //std::cout << "looking at diMuon mass" << std::endl;

        if ((include_Z && include_H) || (!include_Z && !include_H)){
            if (t_diMuon_bsConstrainedMass < 70 || t_diMuon_bsConstrainedMass > 180){
                continue;
            }    
        }
        else if (include_Z){
            if(t_diMuon_bsConstrainedMass < 76 || t_diMuon_bsConstrainedMass > 106){
                continue;
            }
        }
        else{
            //in Higgs region
            if(t_diMuon_bsConstrainedMass < 100 || t_diMuon_bsConstrainedMass > 180){
                continue;
            }
        }

        h_nInMassRegion->Fill(0.5);

        t_nSoftActivityJet = nSoftActivityJet;
        t_SoftActivityJetNjets10 = SoftActivityJetNjets10;
        t_SoftActivityJetNjets2 = SoftActivityJetNjets2;
        t_SoftActivityJetNjets5 = SoftActivityJetNjets5;
        t_SoftActivityJetHT = SoftActivityJetHT;
        t_SoftActivityJetHT10 = SoftActivityJetHT10;
        t_SoftActivityJetHT2 = SoftActivityJetHT2;
        t_SoftActivityJetHT5 = SoftActivityJetHT5;


        /*if(t_diMuon_bsConstrainedMass < 80 || t_diMuon_bsConstrainedMass > 180){
            continue; //not in signal + Z range
        }*/
      


        std::unique_ptr<JecApplication::Applier> data_jec_applier;
        const JecApplication::Applier *jet_applier = mc_jec_applier.get();
        if (is_data) {
            data_jec_applier = std::make_unique<JecApplication::Applier>(
                JecApplication::Applier::DataAK4(jec_config, jec_year, jec_data_era,
                                                 false,
                                                 static_cast<double>(run)));
            jet_applier = data_jec_applier.get();
        }
        
        //std::cout << "There are " << nJet << " jets in event " << jentry << std::endl;
        


        int leadJet_idx = INT_NULL_VALUE;
        int subleadJet_idx = INT_NULL_VALUE;

        float leadJet_pt = FLOAT_NULL_VALUE; 
        float subleadJet_pt = FLOAT_NULL_VALUE;
        
        bool veto_event_jvm = false;
        
        for (int j = 0; j < nJet; j++) {
            h_nJets->Fill(0.5);
            //std::cout << "looking at jet " << j << std::endl;

            JecApplication::JesInputs jesIn{Jet_pt[j],
                                            Jet_eta[j],
                                            Jet_phi[j],
                                            Jet_area[j],
                                            Rho_fixedGridRhoFastjetAll,
                                            Jet_rawFactor[j]};
            float jec_correction = jet_applier->jesFactorNominal(jesIn);
            float corrected_jet_pt_after_jes = Jet_pt[j] * jec_correction;
            float corrected_jet_mass = Jet_mass[j] * jec_correction;
            float corrected_jet_pt = corrected_jet_pt_after_jes;

            std::map<std::string, double> shifted_jes_pts;
            std::map<std::string, double> shifted_jer_pts;
            std::map<std::string, double> shifted_jes_masses;
            std::map<std::string, double> shifted_jer_masses;


            for (const auto &syst_name : jet_jer_syst_names) {
                for (const auto &direction : jer_directions) {
                    const std::string branch_name =
                        JetPtJerSystBranchName(syst_name, direction);

                    shifted_jer_pts[branch_name] = corrected_jet_pt_after_jes;

                    const std::string mass_branch_name =
                        JetMassJerSystBranchName(syst_name, direction);

                    shifted_jer_masses[mass_branch_name] = corrected_jet_mass;
                }
            }

            auto shifted_jet_scale = [&](const std::string &uncertainty_name,
                                       const std::string &direction) {
                if (is_data) {
                    return 1.0;
                }

                if (!JecSystAppliesToYear(uncertainty_name, yearst)) {
                    return 1.0;
                }

                auto uncertainty = jes_uncertainties.find(uncertainty_name);

                if (uncertainty == jes_uncertainties.end()) {
                    throw std::runtime_error(
                        "ERROR: JES uncertainty not found: " + uncertainty_name +
                        ". Check that this name exists in the reduced JES uncertainty set.");
                }

                return JecApplication::Applier::jesComponentSyst(
                    uncertainty->second,
                    direction,
                    Jet_eta[j],
                    corrected_jet_pt_after_jes,
                    false);
            };


            for (const auto &syst_name : jet_jes_syst_names) {
                for (const auto &direction : jes_directions) {
                    const std::string branch_name =
                        JetPtJesSystBranchName(syst_name, direction);

                    const double jes_shift = shifted_jet_scale(syst_name, direction);
                    shifted_jes_pts[branch_name] =
                        corrected_jet_pt_after_jes * jes_shift;

                    const std::string mass_branch_name =
                        JetMassJesSystBranchName(syst_name, direction);
                    shifted_jes_masses[mass_branch_name] =
                        corrected_jet_mass * jes_shift;
                }
            }
        
            if (!is_data) {


                JecApplication::JerInputs jer_inputs{};
                jer_inputs.event = event;
                jer_inputs.rho = Rho_fixedGridRhoFastjetAll;
                jer_inputs.maxDr = 0.2;

                double bestGenJetDR = jer_inputs.maxDr;
                int bestGenJet = -1;

                for (int genJetIndex = 0; genJetIndex < nGenJet; ++genJetIndex) {
                    const double dR =
                        DeltaR(Jet_eta[j], Jet_phi[j],
                               GenJet_eta[genJetIndex],
                               GenJet_phi[genJetIndex]);

                    if (dR < bestGenJetDR) {
                        bestGenJetDR = dR;
                        bestGenJet = genJetIndex;
                    }
                }

                if (bestGenJet >= 0) {
                    jer_inputs.hasGen = true;
                    jer_inputs.genPt = GenJet_pt[bestGenJet];
                    jer_inputs.genEta = GenJet_eta[bestGenJet];
                    jer_inputs.genPhi = GenJet_phi[bestGenJet];
                }

                JecApplication::SystematicOptions systJerNom{};
                systJerNom.jerVar = "nom";

                auto nominal_jer_factor = [&](double pt_after_jes) {
                    JecApplication::JesInputs jet_after_jes{
                        pt_after_jes,
                        Jet_eta[j],
                        Jet_phi[j],
                        Jet_area[j],
                        Rho_fixedGridRhoFastjetAll,
                        0.0
                    };

                    return jet_applier->jerFactor(jet_after_jes,
                                                  jer_inputs,
                                                  systJerNom);
                };

                const double jer_correction =
                    nominal_jer_factor(corrected_jet_pt_after_jes);

                const double nominal_pt_after_jer =
                    corrected_jet_pt_after_jes * jer_correction;


                for (const auto &syst_name : jet_jer_syst_names) {
                    for (const auto &direction : jer_directions) {
                        const std::string branch_name =
                            JetPtJerSystBranchName(syst_name, direction);

                        shifted_jer_pts[branch_name] = nominal_pt_after_jer;

                        const std::string mass_branch_name =
                            JetMassJerSystBranchName(syst_name, direction);
                        shifted_jer_masses[mass_branch_name] =
                            corrected_jet_mass * jer_correction;

                        if (!JecSystAppliesToYear(syst_name, yearst)) {
                            continue;
                        }

                        auto uncertainty = jer_uncertainty.find(syst_name);

                        if (uncertainty == jer_uncertainty.end()) {
                            throw std::runtime_error(
                                "ERROR: JER uncertainty not found: " +
                                syst_name +
                                " for year " + yearst);
                        }

                        const JecConfigReader::JerBin &jer_region = uncertainty->second;

                        JecApplication::SystematicOptions systJer{};
                        systJer.jerVar = ToLower(direction);  // "Up" -> "up", "Down" -> "down"
                        systJer.jerRegion = jer_region;

                        JecApplication::JesInputs jet_after_jes{
                            corrected_jet_pt_after_jes,
                            Jet_eta[j],
                            Jet_phi[j],
                            Jet_area[j],
                            Rho_fixedGridRhoFastjetAll,
                            0.0
                        };

                        const double shifted_jer_factor =
                            jet_applier->jerFactor(jet_after_jes,
                                                    jer_inputs,
                                                    systJer);

                        shifted_jer_pts[branch_name] =
                            corrected_jet_pt_after_jes * shifted_jer_factor;
                        shifted_jer_masses[mass_branch_name] =
                            corrected_jet_mass * shifted_jer_factor;
                    }
                }

                corrected_jet_pt *= jer_correction;
                corrected_jet_mass *= jer_correction;

                for (auto &entry : shifted_jes_pts) {
                    double &shifted_pt = entry.second;
                    const double shifted_jer_factor = nominal_jer_factor(shifted_pt);
                    shifted_pt *= shifted_jer_factor;

                    const std::string mass_branch_name =
                        "t_Jet_mass_" + entry.first.substr(std::string("t_Jet_pt_").size());
                    shifted_jes_masses.at(mass_branch_name) *= shifted_jer_factor;
                }
            }
            
            if (passesJetIdTightLepVeto(j) &&
                jvm_checker.checkJetInVetoRegion(Jet_eta[j], Jet_phi[j], corrected_jet_pt,
                    Jet_jetId[j], Jet_chEmEF[j], Jet_neEmEF[j])) {

                veto_event_jvm = true;
                break;
            }



            if (!isValidJet(j, corrected_jet_pt)) {
                //std::cout << "Jet " << j << " invalid" << std::endl;
                continue;
            }
            h_nValidJets->Fill(0.5);
            //std::cout << "Valid jet" << std::endl;
            // if (!(Jet_pt[j] > 25. && fabs(Jet_eta[j]) < 4.7 &&
            // Jet_jetId[j] >= 2 [> && Jet_puId[j]>=1 <])) {
            // continue;
            //}
            //
            

            double dR1 = DeltaR(Muon_eta[index_mu1], Muon_phi[index_mu1],
                                Jet_eta[j], Jet_phi[j]);
            double dR2 = DeltaR(Muon_eta[index_mu2], Muon_phi[index_mu2],
                                Jet_eta[j], Jet_phi[j]);
            if (dR1 < 0.4 || dR2 < 0.4) {
                //std::cout << "Jet " << j << " not well seperated" << std::endl;
                continue;
            }
            h_nValidSeperatedJets->Fill(0.5);

            /*if((Jet_chEmEF[j] + Jet_neEmEF[j]) > 0.9){
                std::cout << "Vetoing jet with total Em Frac: " << (Jet_chEmEF[j] + Jet_neEmEF[j]) << std::endl;
                continue;
            }*/
            //std::cout << "Jet pass dR and EmEF" << std::endl;
            //if (jvm_checker.checkJetInVetoRegion(
                    //Jet_eta[j], Jet_phi[j], corrected_jet_pt, Jet_jetId[j],
                    //Jet_chEmEF[j], Jet_neEmEF[j])) {
                //// std::cout << "Jet " << j << " vetoed" << std::endl;
                //continue;
            //}



            

            //std::cout << "Jet pass jetVeto" << std::endl;
            int stored_jet_idx = t_nJet;

            if (corrected_jet_pt > leadJet_pt) {
                subleadJet_pt = leadJet_pt;
                subleadJet_idx = leadJet_idx;

                leadJet_pt = corrected_jet_pt;
                leadJet_idx = stored_jet_idx;
            }
            else if (corrected_jet_pt > subleadJet_pt) {
                subleadJet_pt = corrected_jet_pt;
                subleadJet_idx = stored_jet_idx;
            }

            t_nJet++;
            t_Jet_area->push_back(Jet_area[j]);
            // t_Jet_btagCMVA->push_back(Jet_btagCMVA[j]);
            // t_Jet_btagCSVV2->push_back(Jet_btagCSVV2[j]);
            t_Jet_btagDeepB->push_back(Jet_btagDeepFlavB[j]);
            t_Jet_btagDeepFlavQG->push_back(Jet_btagDeepFlavQG[j]);
            t_Jet_btagPNetB->push_back(Jet_btagPNetB[j]);
            t_Jet_btagPNetQvG->push_back(Jet_btagPNetQvG[j]);

            if (NANOAOD_VERSION.at(year) == "v15") {

                t_Jet_chMultiplicity->push_back(Jet_chMultiplicity[j]);
                t_Jet_neMultiplicity->push_back(Jet_neMultiplicity[j]);

                t_Jet_btagUParTAK4QvG->push_back(Jet_btagUParTAK4QvG[j]);
                t_Jet_btagUParTAK4B->push_back(Jet_btagUParTAK4B[j]);

            } else {

                t_Jet_chMultiplicity->push_back(INT_NULL_VALUE);
                t_Jet_neMultiplicity->push_back(INT_NULL_VALUE);

                t_Jet_btagUParTAK4QvG->push_back(FLOAT_NULL_VALUE);
                t_Jet_btagUParTAK4B->push_back(FLOAT_NULL_VALUE);
            }

            t_Jet_chEmEF->push_back(Jet_chEmEF[j]);
            t_Jet_chHEF->push_back(Jet_chHEF[j]);
            t_Jet_eta->push_back(Jet_eta[j]);
            t_Jet_mass->push_back(corrected_jet_mass);
            t_Jet_mass_nanoAOD->push_back(Jet_mass[j]);
            t_Jet_neEmEF->push_back(Jet_neEmEF[j]);
            t_Jet_neHEF->push_back(Jet_neHEF[j]);
            t_Jet_phi->push_back(Jet_phi[j]);
            t_Jet_pt->push_back(corrected_jet_pt);
            for (const auto &entry : shifted_jes_pts) {
                const std::string &branch_name = entry.first;
                const double shifted_pt = entry.second;

                t_Jet_pt_jes_syst.at(branch_name)->push_back(shifted_pt);
            }
            for (const auto &entry : shifted_jer_pts) {
                const std::string &branch_name = entry.first;
                const double shifted_pt = entry.second;

                t_Jet_pt_jer_syst.at(branch_name)->push_back(shifted_pt);
            }
            for (const auto &entry : shifted_jes_masses) {
                const std::string &branch_name = entry.first;
                const double shifted_mass = entry.second;

                t_Jet_mass_jes_syst.at(branch_name)->push_back(shifted_mass);
            }
            for (const auto &entry : shifted_jer_masses) {
                const std::string &branch_name = entry.first;
                const double shifted_mass = entry.second;

                t_Jet_mass_jer_syst.at(branch_name)->push_back(shifted_mass);
            }
            t_Jet_pt_nanoAOD->push_back(Jet_pt[j]);
            // t_Jet_qgl->push_back(Jet_qgl[j]);
            // t_Jet_jetId->push_back(Jet_jetId[j]);

            t_Jet_nConstituents->push_back(Jet_nConstituents[j]);
            
            t_Jet_nElectrons->push_back(Jet_nElectrons[j]);
            t_Jet_nMuons->push_back(Jet_nMuons[j]);
            // t_Jet_puId->push_back(Jet_puId[j]);
            if (Jet_btagPNetB[j] > btagLoose_cut.at(yearst)) {
                t_nbJet_Loose++;
            }

            if (!(Jet_btagPNetB[j] > btagMedium_cut.at(yearst))) {
                continue; // medium WP
            } // end of b-tag
            t_nbJet++;
            t_bJet_area->push_back(Jet_area[j]);
            t_bJet_btagDeepB->push_back(Jet_btagDeepFlavB[j]);
            t_bJet_btagPNetB->push_back(Jet_btagPNetB[j]);
            t_bJet_chEmEF->push_back(Jet_chEmEF[j]);
            t_bJet_chHEF->push_back(Jet_chHEF[j]);
            t_bJet_eta->push_back(Jet_eta[j]);
            t_bJet_mass->push_back(corrected_jet_mass);
            t_bJet_neEmEF->push_back(Jet_neEmEF[j]);
            t_bJet_neHEF->push_back(Jet_neHEF[j]);
            t_bJet_phi->push_back(Jet_phi[j]);
            t_bJet_pt->push_back(corrected_jet_pt);
            // t_bJet_qgl->push_back(Jet_qgl[j]);
            t_bJet_jetId->push_back(Jet_jetId[j]);
            t_bJet_nConstituents->push_back(Jet_nConstituents[j]);
            t_bJet_nElectrons->push_back(Jet_nElectrons[j]);
            t_bJet_nMuons->push_back(Jet_nMuons[j]);
            // t_bJet_puId->push_back(Jet_puId[j]);

            if (is_data) {
                continue;
            }


            double jet_scalefactor =
                reader.eval_auto_bounds("central", BTagEntry::FLAV_B,
                                        fabs(Jet_eta[j]), // absolute value
                                                          // of eta
                                        corrected_jet_pt);
            double jet_scalefactor_up = reader.eval_auto_bounds(
                "up", BTagEntry::FLAV_B, fabs(Jet_eta[j]), corrected_jet_pt);
            double jet_scalefactor_do = reader.eval_auto_bounds(
                "down", BTagEntry::FLAV_B, fabs(Jet_eta[j]), corrected_jet_pt);
            // std::cout<<jet_scalefactor<<"
            // "<<jet_scalefactor_up<<"
            // "<<jet_scalefactor_do<<std::endl;
            t_bJet_SF->push_back(jet_scalefactor);
            t_bJet_SFup->push_back(jet_scalefactor_up);
            t_bJet_SFdown->push_back(jet_scalefactor_do);
        }
        if (veto_event_jvm) {
            continue; 
        }      
        h_nValidNotVetoedJets->Fill(0.5);
        t_leadJet_idx = leadJet_idx;
        t_subleadJet_idx = subleadJet_idx;

        //if(t_nbJet_Loose > 1 || t_nbJet > 0){
            ////std::cout << "Too many bJets" << std::endl;
            //continue;
        //}

        //h_nBjetRejection->Fill(0.5);



        // if (t_Jet_pt->size() >= 2) {
        if (t_nJet >= 2 &&
            leadJet_idx != INT_NULL_VALUE &&
            subleadJet_idx != INT_NULL_VALUE) {

            ROOT::Math::PtEtaPhiMVector j1, j2, jj;

            j1.SetCoordinates((*t_Jet_pt)[leadJet_idx],
                              (*t_Jet_eta)[leadJet_idx],
                              (*t_Jet_phi)[leadJet_idx],
                              (*t_Jet_mass)[leadJet_idx]);

            j2.SetCoordinates((*t_Jet_pt)[subleadJet_idx],
                              (*t_Jet_eta)[subleadJet_idx],
                              (*t_Jet_phi)[subleadJet_idx],
                              (*t_Jet_mass)[subleadJet_idx]);

            jj = j1 + j2;

            t_diJet_pt = jj.Pt();
            t_diJet_eta = jj.Eta();
            t_diJet_phi = jj.Phi();
            t_diJet_mass = jj.M();
            t_diJet_mass_mo = jj.M();

            for (int k = 0; k < t_nJet; k++) {
                for (int m = k + 1; m < t_nJet; m++) {
                    j1.SetCoordinates((*t_Jet_pt)[k], (*t_Jet_eta)[k],
                                      (*t_Jet_phi)[k], (*t_Jet_mass)[k]);
                    j2.SetCoordinates((*t_Jet_pt)[m], (*t_Jet_eta)[m],
                                      (*t_Jet_phi)[m], (*t_Jet_mass)[m]);
                    jj = j1 + j2;

                    if (t_diJet_mass_mo < jj.M()) {
                        t_diJet_mass_mo = jj.M();
                    }
                }
            }
        }

        // if (year != "2017") {
        //t_MET_pt = MET_pt
        //t_MET_phi = MET_phi;
        //t_MET_sumEt = MET_sumEt;
        //}
        for (int i = 0; i < nFatJet; i++) {
            t_FatJet_area->push_back(FatJet_area[i]);
            // t_FatJet_btagCMVA->push_back(FatJet_btagCMVA[i]);
            // t_FatJet_btagCSVV2->push_back(FatJet_btagCSVV2[i]);
            //t_FatJet_btagDeepB->push_back(FatJet_btagDeepB[i]);
            t_FatJet_eta->push_back(FatJet_eta[i]);
            t_FatJet_mass->push_back(FatJet_mass[i]);
            t_FatJet_msoftdrop->push_back(FatJet_msoftdrop[i]);
            t_FatJet_n2b1->push_back(FatJet_n2b1[i]);
            t_FatJet_n3b1->push_back(FatJet_n3b1[i]);
            t_FatJet_phi->push_back(FatJet_phi[i]);
            t_FatJet_pt->push_back(FatJet_pt[i]);
            t_FatJet_tau1->push_back(FatJet_tau1[i]);
            t_FatJet_tau2->push_back(FatJet_tau2[i]);
            t_FatJet_tau3->push_back(FatJet_tau3[i]);
            t_FatJet_tau4->push_back(FatJet_tau4[i]);
            //->push_back(FatJet_jetId[i]);
            t_FatJet_subJetIdx1->push_back(FatJet_subJetIdx1[i]);
            t_FatJet_subJetIdx2->push_back(FatJet_subJetIdx2[i]);
        }
        for (int i = 0; i < nSubJet; i++) {
            // t_SubJet_btagCMVA->push_back(SubJet_btagCMVA[i]);
            // t_SubJet_btagCSVV2->push_back(SubJet_btagCSVV2[i]);
            //t_SubJet_btagDeepB->push_back(SubJet_btagDeepB[i]);
            t_SubJet_eta->push_back(SubJet_eta[i]);
            t_SubJet_mass->push_back(SubJet_mass[i]);
            t_SubJet_n2b1->push_back(SubJet_n2b1[i]);
            t_SubJet_n3b1->push_back(SubJet_n3b1[i]);
            t_SubJet_phi->push_back(SubJet_phi[i]);
            t_SubJet_pt->push_back(SubJet_pt[i]);
            t_SubJet_tau1->push_back(SubJet_tau1[i]);
            t_SubJet_tau2->push_back(SubJet_tau2[i]);
            t_SubJet_tau3->push_back(SubJet_tau3[i]);
            t_SubJet_tau4->push_back(SubJet_tau4[i]);
        }
        t_PV_ndof = PV_ndof;
        t_PV_x = PV_x;
        t_PV_y = PV_y;
        t_PV_z = PV_z;
        t_PV_npvs = PV_npvs;
        t_PV_npvsGood = PV_npvsGood;

        t_Rho = Rho_fixedGridRhoFastjetAll;


        if(t_diMuon_bsConstrainedMass > 76 && t_diMuon_bsConstrainedMass < 106){
            h_nInZPeak->Fill(0.5); //in Z +- 15
        }


        if (!is_data) {
            t_genWeight = genWeight;
            // t_puWeight = 1.0;     // puWeight;
            // t_puWeightUp = 1.0;   // puWeightUp;
            // t_puWeightDown = 1.0; // puWeightDown;
            // t_pileup = Pileup_nPU;
            t_pileup = Pileup_nTrueInt;
            t_puWeight = puWeight;
            t_puWeightUp = puWeightUp;
            t_puWeightDown = puWeightDown;
            //  if (year != "2017") {
            t_PrefireWeight = 1.0;
            t_PrefireWeight_Up = 1.0;
            t_PrefireWeight_Down = 1.0;
            //}
            for (int i = 0; i < nGenPart; i++) {

                if ((abs(GenPart_pdgId[i]) >= 11 &&
                     abs(GenPart_pdgId[i]) <= 16) ||
                    (abs(GenPart_pdgId[i]) >= 23 &&
                     abs(GenPart_pdgId[i]) <= 25) ||
                    (abs(GenPart_genPartIdxMother[i]) >= 23 &&
                     abs(GenPart_genPartIdxMother[i]) <= 25) ||
                    (abs(GenPart_genPartIdxMother[i]) >= 11 &&
                     abs(GenPart_genPartIdxMother[i]) <= 16)) {
                    t_GenPart_eta->push_back(GenPart_eta[i]);
                    t_GenPart_mass->push_back(GenPart_mass[i]);
                    t_GenPart_phi->push_back(GenPart_phi[i]);
                    t_GenPart_pt->push_back(GenPart_pt[i]);
                    t_GenPart_genPartIdxMother->push_back(
                        GenPart_genPartIdxMother[i]);
                    t_GenPart_pdgId->push_back(GenPart_pdgId[i]);
                    t_GenPart_status->push_back(GenPart_status[i]);
                }
            }
            for (int i = 0; i < nGenJet; i++) {
                t_GenJet_eta->push_back(GenJet_eta[i]);
                t_GenJet_mass->push_back(GenJet_mass[i]);
                t_GenJet_phi->push_back(GenJet_phi[i]);
                t_GenJet_pt->push_back(GenJet_pt[i]);
            }
        }
        tree->Fill();
    }
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    std::cout << "Elapsed time: " << duration.count()/60000 << " minutes" << std::endl;
    if(nentries != 0) {
        std::cout << "Time per event: " << duration.count()/nentries << " milliseconds" << std::endl;
    }
}
