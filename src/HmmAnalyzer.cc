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

#include "correction.h"
#include "../lib/LeptonEfficiencyCorrector.h"

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

    if (argc != 8) {
        std::cerr << "Please give 7 arguments " << "runList " << " "
                  << "outputFileName" << " " << "dataset"
                  << "data type year include_Z(T/F) and include_H(T/F)" << std::endl;
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

    //read run3 muon efficiency json files
    if (!is_data_input){
        LeptonEfficiencyCorrector corrector;
        corrector.initializeCorrections(year_num.Data());
    }

    HmmAnalyzer Hmm(inputFileList, outFileName, data, is_data_input, year_num, include_Z, include_H);
    std::cout << "Running on: " << std::endl;
    std::cout << "  Dataset: " << data << " year " << year_num << std::endl;
    std::cout << "  Era:  " << year_num << std::endl;
    std::cout << std::boolalpha;
    std::cout << "  Is data? " << is_data_input << std::endl;
    std::cout << "  Year num: " << year_num << std::endl;
    std::cout << "  Include Z? " << include_Z << std::endl;
    std::cout << "  Include H? " << include_H << std::endl;
    Hmm.EventLoop();

    return 0;
}

void HmmAnalyzer::EventLoop() {

    if (fChain == 0)
        return;

    //read run3 muon efficiency json files
    LeptonEfficiencyCorrector corrector;

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
    //nentries = 500;
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
        } else {
            value_h_sumOfgw = value_h_sumOfgw + 1.0;
            value_h_sumOfgpw = value_h_sumOfgpw + 1.0;
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
        vector<float> mu_pt_Roch_corr, mu_ptErr_Roch_corr, mu_Iso_Roch_corr;
        // mu_pt_Roch_corr.clear(), mu_ptErr_Roch_corr.clear(),
        // mu_Iso_Roch_corr.clear();

        float pt_Roch, ptErr_Roch, pt_Roch_sys_up, pt_Roch_sys_down;
        // pt_Roch = 0, ptErr_Roch = 0, pt_Roch_sys_up = 0, pt_Roch_sys_down =
        // 0;
        bool two_valid_muons = false;
        bool trig_match = false;

        for (int i = 0; i < nMuon; i++) {
            // TLorentzVector mu_raw;
            // mu_raw.SetPtEtaPhiM(Muon_pt[i], Muon_eta[i], Muon_phi[i],
            // MUON_MASS); // Muon_mass[i]);
            ROOT::Math::PtEtaPhiMVector mu_raw(Muon_pt[i], Muon_eta[i],
                                               Muon_phi[i], MUON_MASS);
            pt_Roch = 0, ptErr_Roch = 0, pt_Roch_sys_up = 0,
            pt_Roch_sys_down = 0;
            float ptErr_raw = Muon_ptErr[i];

            float gen_pt = FLOAT_NULL_VALUE;
            if (!is_data) {
                for (int j = 0; j < nGenPart; j++) {
                    if (((Muon_charge[i] == -1 && GenPart_pdgId[j] == 13) ||
                         ((Muon_charge[i] == 1 && GenPart_pdgId[j] == -13))) &&
                        DeltaR(Muon_eta[i], Muon_phi[i], GenPart_eta[j],
                               GenPart_phi[j]) < 0.1) {
                        gen_pt = GenPart_pt[j];
                        break;
                    }
                }
            }
            CorrectPtRoch(_Roch_calib, false, mu_raw, ptErr_raw, pt_Roch, ptErr_Roch,
                          pt_Roch_sys_up, pt_Roch_sys_down, Muon_charge[i],
                          Muon_nTrackerLayers[i], gen_pt, is_data);

            if ((pt_Roch > 10 && fabs(Muon_eta[i]) < 2.4 && Muon_isGlobal[i] && Muon_pfRelIso04_all[i] < 0.25 && Muon_looseId[i])){
                mu_pt_Roch_corr.push_back(pt_Roch);
                mu_ptErr_Roch_corr.push_back(ptErr_Roch);
            }
        }

        if(mu_pt_Roch_corr.size() < 2){
            continue;
        }

        for (int muon_index_1 = 0; muon_index_1 < nMuon; muon_index_1++) {
            if (!(Muon_isGlobal[muon_index_1] &&
                  mu_pt_Roch_corr[muon_index_1] > muon_pt_cut.at(yearst) &&
                  Muon_mediumId[muon_index_1] &&
                  fabs(Muon_eta[muon_index_1]) < 2.4 &&
                  Muon_pfRelIso04_all[muon_index_1] < 0.25)) {
                continue;
            }

            for (int muon_index_2 = muon_index_1 + 1; muon_index_2 < nMuon;
                 muon_index_2++) {
                if (Muon_isGlobal[muon_index_2] &&
                    Muon_charge[muon_index_1] * Muon_charge[muon_index_2] ==
                        -1 &&
                    mu_pt_Roch_corr[muon_index_2] > 20. &&
                    Muon_mediumId[muon_index_2] &&
                    fabs(Muon_eta[muon_index_2]) < 2.4 &&
                    Muon_pfRelIso04_all[muon_index_2] < 0.25) {
                    two_valid_muons = true;
                    index_mu1 = muon_index_1;
                    index_mu2 = muon_index_2;
                    break;
                }
            }
            if (two_valid_muons)
                break;
        }

        //std::cout << "Checking 2 valid muons" << std::endl; 
        if(!two_valid_muons){
            //std::cout << "No valid muons" << std::endl; 
            continue;
        }

        h_nTwoMuons->Fill(0.5);

        //Ensure only 3 Muons
        if(mu_pt_Roch_corr.size() > 2){
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


        for (int trigger_index = 0; trigger_index < nTrigObj; trigger_index++) {
            //  float dR_TrigObj = 999.;
            if (TrigObj_id[trigger_index] != 13)
                continue;
            float dR_TrigObj;
            dR_TrigObj =
                DeltaR(Muon_eta[index_mu1], Muon_phi[index_mu1],
                       TrigObj_eta[trigger_index], TrigObj_phi[trigger_index]);
            if (dR_TrigObj < 0.1 && Muon_tightId[index_mu1] &&
                Muon_pfRelIso04_all[index_mu1] < 0.15 &&
                mu_pt_Roch_corr[index_mu1] > muon_pt_cut.at(yearst)) {
                trig_match = true;
                t_index_trigm_mu = 1;
                break;
            }
            dR_TrigObj =
                DeltaR(Muon_eta[index_mu2], Muon_phi[index_mu2],
                       TrigObj_eta[trigger_index], TrigObj_phi[trigger_index]);
            if (mu_pt_Roch_corr[index_mu2] > muon_pt_cut.at(yearst) &&
                Muon_tightId[index_mu2] &&
                Muon_pfRelIso04_all[index_mu2] < 0.15 && dR_TrigObj < 0.1) {
                trig_match = true;
                t_index_trigm_mu = 2;
                break;
            }
        } // end of triger match, end of loop over trigger objects

        //std::cout << "Checking trig match" << std::endl; 
        if (!trig_match) {
            //std::cout << "No trig match" << std::endl; 
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
            if (i == index_mu1)
                t_index_mu1 = t_index;
            if (i == index_mu2)
                t_index_mu2 = t_index;

            t_Mu_charge->push_back(Muon_charge[i]);
            t_Mu_pt->push_back(mu_pt_Roch_corr[i]);
            t_Mu_ptErr->push_back(mu_ptErr_Roch_corr[i]);
            t_Mu_bsConstrainedPt->push_back(Muon_bsConstrainedPt[i]);
            t_Mu_bsConstrainedPtErr->push_back(Muon_bsConstrainedPtErr[i]);
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

            if(year == "2024" || year == "2025"){
                t_Mu_EffSF_TRIG->push_back(1);
                t_Mu_EffSFErr_TRIG->push_back(0);
            }

            else{
                t_Mu_EffSF_TRIG->push_back(corrector.give_eff("Muon_eff_SF_TRIG", Muon_pt[i], Muon_eta[i]));
                t_Mu_EffSFErr_TRIG->push_back(corrector.give_eff("Muon_eff_SFerr_TRIG", Muon_pt[i], Muon_eta[i]));
            }

            t_Mu_EffSF_ID->push_back(corrector.give_eff("Muon_eff_SF_ID", Muon_pt[i], Muon_eta[i]));
            t_Mu_EffSF_ID_stat->push_back(corrector.give_eff("Muon_eff_SF_ID_stat", Muon_pt[i], Muon_eta[i]));
            t_Mu_EffSF_ID_syst->push_back(corrector.give_eff("Muon_eff_SF_ID_syst", Muon_pt[i], Muon_eta[i]));

            t_Mu_EffSF_ISO->push_back(corrector.give_eff("Muon_eff_SF_ISO", Muon_pt[i], Muon_eta[i]));
            t_Mu_EffSF_ISO_stat->push_back(corrector.give_eff("Muon_eff_SF_ISO_stat", Muon_pt[i], Muon_eta[i]));
            t_Mu_EffSF_ISO_syst->push_back(corrector.give_eff("Muon_eff_SF_ISO_syst", Muon_pt[i], Muon_eta[i]));
            //std::cout << "Corrector passed" << std::endl;


            // if (year == "2016") {

            //t_Mu_EffSF_TRIG->push_back(Mu_eff_SF_TRIG.getSFAve(11, Muon_pt[i], Muon_eta[i], 0.5548));
            //t_Mu_EffSFErr_TRIG->push_back(Mu_eff_SF_TRIG.getSFErr(13, Muon_pt[i], Muon_eta[i]));
        
            /*t_Mu_EffSF_ID->push_back(Mu_eff_SF_ID.getSFAve(11, Muon_pt[i], Muon_eta[i], 0.5548));
            t_Mu_EffSF_ID_stat->push_back(Mu_eff_SF_ID_stat.getSFAve(11, Muon_pt[i], Muon_eta[i], 0.5548));
            t_Mu_EffSF_ID_syst->push_back(Mu_eff_SF_ID_syst.getSFAve(11, Muon_pt[i], Muon_eta[i], 0.5548));
            
            t_Mu_EffSF_ISO->push_back(Mu_eff_SF_ISO.getSFAve(11, Muon_pt[i], Muon_eta[i], 0.5548));
            t_Mu_EffSF_ISO_stat->push_back(Mu_eff_SF_ISO_stat.getSFAve(11, Muon_pt[i], Muon_eta[i], 0.5548));
            t_Mu_EffSF_ISO_syst->push_back(Mu_eff_SF_ISO_syst.getSFAve(11, Muon_pt[i], Muon_eta[i], 0.5548));
            */
            //}
        }


        t_mu1 = t_index_mu1;
        t_mu2 = t_index_mu2;
        if (t_index_trigm_mu == 1)
            t_index_trigm_mu = t_mu1;
        else if (t_index_trigm_mu == 2)
            t_index_trigm_mu = t_mu2;

        // TLorentzVector dimu, mu1, mu2;
        ROOT::Math::PtEtaPhiMVector dimu;
        ROOT::Math::PtEtaPhiMVector mu1((mu_pt_Roch_corr)[index_mu1],
                                        (Muon_eta)[index_mu1],
                                        (Muon_phi)[index_mu1], MUON_MASS);
        ROOT::Math::PtEtaPhiMVector mu2((mu_pt_Roch_corr)[index_mu2],
                                        (Muon_eta)[index_mu2],
                                        (Muon_phi)[index_mu2], MUON_MASS);

        ROOT::Math::PtEtaPhiMVector dimuBSC;
        ROOT::Math::PtEtaPhiMVector mu1BSC((Muon_bsConstrainedPt)[index_mu1],
                                        (Muon_eta)[index_mu1],
                                        (Muon_phi)[index_mu1], MUON_MASS);
        ROOT::Math::PtEtaPhiMVector mu2BSC((Muon_bsConstrainedPt)[index_mu2],
                                        (Muon_eta)[index_mu2],
                                        (Muon_phi)[index_mu2], MUON_MASS);
        // mu1.SetPtEtaPhiM((mu_pt_Roch_corr)[index_mu1], (Muon_eta)[index_mu1],
        //(Muon_phi)[index_mu1], MUON_MASS);
        // mu2.SetPtEtaPhiM((mu_pt_Roch_corr)[index_mu2], (Muon_eta)[index_mu2],
        //(Muon_phi)[index_mu2], MUON_MASS);
        dimu = mu1 + mu2;
        dimuBSC = mu1BSC + mu2BSC;
        t_diMuon_pt = dimu.Pt();
        t_diMuon_eta = dimu.Eta();
        t_diMuon_phi = dimu.Phi();
        t_diMuon_mass = dimu.M();

        t_diMuon_bsConstrainedPt = dimuBSC.Pt();
        t_diMuon_bsConstrainedMass = dimuBSC.M();

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

        for (int j = 0; j < nJet; j++) {
            if (!isValidJet(j)) {
                continue;
            }
            // if (!(Jet_pt[j] > 25. && fabs(Jet_eta[j]) < 4.7 &&
            // Jet_jetId[j] >= 2 [> && Jet_puId[j]>=1 <])) {
            // continue;
            //}
            double dR1 = DeltaR(Muon_eta[index_mu1], Muon_phi[index_mu1],
                                Jet_eta[j], Jet_phi[j]);
            double dR2 = DeltaR(Muon_eta[index_mu2], Muon_phi[index_mu2],
                                Jet_eta[j], Jet_phi[j]);
            if (dR1 < 0.4 || dR2 < 0.4) {
                continue;
            }

            t_nJet++;
            t_Jet_area->push_back(Jet_area[j]);
            // t_Jet_btagCMVA->push_back(Jet_btagCMVA[j]);
            // t_Jet_btagCSVV2->push_back(Jet_btagCSVV2[j]);
            t_Jet_btagDeepB->push_back(Jet_btagDeepFlavB[j]);
            t_Jet_btagPNetB->push_back(Jet_btagPNetB[j]);
            t_Jet_chEmEF->push_back(Jet_chEmEF[j]);
            t_Jet_chHEF->push_back(Jet_chHEF[j]);
            t_Jet_eta->push_back(Jet_eta[j]);
            t_Jet_mass->push_back(Jet_mass[j]);
            t_Jet_neEmEF->push_back(Jet_neEmEF[j]);
            t_Jet_neHEF->push_back(Jet_neHEF[j]);
            t_Jet_phi->push_back(Jet_phi[j]);
            t_Jet_pt->push_back(Jet_pt[j]);
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
            t_bJet_mass->push_back(Jet_mass[j]);
            t_bJet_neEmEF->push_back(Jet_neEmEF[j]);
            t_bJet_neHEF->push_back(Jet_neHEF[j]);
            t_bJet_phi->push_back(Jet_phi[j]);
            t_bJet_pt->push_back(Jet_pt[j]);
            // t_bJet_qgl->push_back(Jet_qgl[j]);
            t_bJet_jetId->push_back(Jet_jetId[j]);
            t_bJet_nConstituents->push_back(Jet_nConstituents[j]);
            t_bJet_nElectrons->push_back(Jet_nElectrons[j]);
            t_bJet_nMuons->push_back(Jet_nMuons[j]);
            // t_bJet_puId->push_back(Jet_puId[j]);

            if (!is_data) {
                continue;
            }


            double jet_scalefactor =
                reader.eval_auto_bounds("central", BTagEntry::FLAV_B,
                                        fabs(Jet_eta[j]), // absolute value
                                                          // of eta
                                        Jet_pt[j]);
            double jet_scalefactor_up = reader.eval_auto_bounds(
                "up", BTagEntry::FLAV_B, fabs(Jet_eta[j]), Jet_pt[j]);
            double jet_scalefactor_do = reader.eval_auto_bounds(
                "down", BTagEntry::FLAV_B, fabs(Jet_eta[j]), Jet_pt[j]);
            // std::cout<<jet_scalefactor<<"
            // "<<jet_scalefactor_up<<"
            // "<<jet_scalefactor_do<<std::endl;
            t_bJet_SF->push_back(jet_scalefactor);
            t_bJet_SFup->push_back(jet_scalefactor_up);
            t_bJet_SFdown->push_back(jet_scalefactor_do);
        }

        if(t_nbJet_Loose > 1 || t_nbJet > 0){
            //std::cout << "Too many bJets" << std::endl;
            continue;
        }

        h_nBjetRejection->Fill(0.5);



        // if (t_Jet_pt->size() >= 2) {
        if (t_nJet >= 2) {
            // TLorentzVector j1, j2, jj;
            ROOT::Math::PtEtaPhiMVector j1, j2, jj;
            // j1.SetPtEtaPhiM((*t_Jet_pt)[0], (*t_Jet_eta)[0],
            //(*t_Jet_phi)[0], (*t_Jet_mass)[0]);
            // j2.SetPtEtaPhiM((*t_Jet_pt)[1], (*t_Jet_eta)[1],
            //(*t_Jet_phi)[1], (*t_Jet_mass)[1]);
            j1.SetCoordinates((*t_Jet_pt)[0], (*t_Jet_eta)[0], (*t_Jet_phi)[0],
                              (*t_Jet_mass)[0]);
            j2.SetCoordinates((*t_Jet_pt)[1], (*t_Jet_eta)[1], (*t_Jet_phi)[1],
                              (*t_Jet_mass)[1]);
            jj = j1 + j2;
            t_diJet_pt = jj.Pt();
            t_diJet_eta = jj.Eta();
            t_diJet_phi = jj.Phi();
            t_diJet_mass = jj.M();
            t_diJet_mass_mo = jj.M();
            for (int k = 0; k < t_nJet; k++) {
                for (int m = k + 1; m < t_nJet; m++) {
                    // j1.SetPtEtaPhiM((*t_Jet_pt)[k], (*t_Jet_eta)[k],
                    //(*t_Jet_phi)[k], (*t_Jet_mass)[k]);
                    // j2.SetPtEtaPhiM((*t_Jet_pt)[m], (*t_Jet_eta)[m],
                    //(*t_Jet_phi)[m], (*t_Jet_mass)[m]);
                    j1.SetCoordinates((*t_Jet_pt)[k], (*t_Jet_eta)[k],
                                      (*t_Jet_phi)[k], (*t_Jet_mass)[k]);
                    j2.SetCoordinates((*t_Jet_pt)[m], (*t_Jet_eta)[m],
                                      (*t_Jet_phi)[m], (*t_Jet_mass)[m]);
                    jj = j1 + j2;
                    if (t_diJet_mass_mo < jj.M())
                        t_diJet_mass_mo = jj.M();
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
