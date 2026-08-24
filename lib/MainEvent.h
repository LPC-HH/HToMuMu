#ifndef MainEvent_h
#define MainEvent_h

#include <TROOT.h>
#include <TChain.h>
#include <TLorentzVector.h>
#include <TFile.h>
#include <TSelector.h>
#include <vector>
#ifdef __CINT__

#pragma link C++ class vector<float>+;
#pragma link C++ class vector<int>+;
#pragma link C++ class vector<bool>+;
#endif

using namespace std;
class MainEvent : public TSelector {
public :

   MainEvent(TTree * /*tree*/ =0) : fChain(0) { }
   ~MainEvent();
   void    Init(TTree *tree, TString nanoAODVersion);
   void    InitSimulationVariables(TTree *tree);
   Bool_t  Notify();
   Int_t   GetEntry(Long64_t entry, Int_t getall = 0) { return fChain ? fChain->GetTree()->GetEntry(entry, getall) : 0; }
   double  DeltaPhi(double, double);
   double  DeltaR(double eta1, double phi1, double eta2, double phi2);
   int     FindMom(double dau,double mom,int i);
   double  HT (std::vector<TLorentzVector>);
   TLorentzVector MHT(std::vector<TLorentzVector>);

   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

// Fixed size dimensions of array or collections stored in the TTree if any.

   // Declaration of leaf types
   UInt_t          run;
   UInt_t          luminosityBlock;
   ULong64_t       event;
   UInt_t          bunchCrossing;
   // UChar_t         HTXS_njets25;
   // UChar_t         HTXS_njets30;
   // Int_t           HTXS_stage1_1_cat_pTjet25GeV;
   // Int_t           HTXS_stage1_1_cat_pTjet30GeV;
   // Int_t           HTXS_stage1_1_fine_cat_pTjet25GeV;
   // Int_t           HTXS_stage1_1_fine_cat_pTjet30GeV;
   // Int_t           HTXS_stage1_2_cat_pTjet25GeV;
   // Int_t           HTXS_stage1_2_cat_pTjet30GeV;
   // Int_t           HTXS_stage1_2_fine_cat_pTjet25GeV;
   // Int_t           HTXS_stage1_2_fine_cat_pTjet30GeV;
   // Int_t           HTXS_stage_0;
   // Int_t           HTXS_stage_1_pTjet25;
   // Int_t           HTXS_stage_1_pTjet30;
   // Float_t         HTXS_Higgs_pt;
   // Float_t         HTXS_Higgs_y;
   // Char_t          BeamSpot_type;
   // Float_t         BeamSpot_sigmaZ;
   // Float_t         BeamSpot_sigmaZError;
   // Float_t         BeamSpot_z;
   // Float_t         BeamSpot_zError;
   // Int_t           nboostedTau;
   // UChar_t         boostedTau_idAntiEle2018[4];   //[nboostedTau]
   // UChar_t         boostedTau_idAntiMu[4];   //[nboostedTau]
   // UChar_t         boostedTau_idMVAnewDM2017v2[4];   //[nboostedTau]
   // UChar_t         boostedTau_idMVAoldDM2017v2[4];   //[nboostedTau]
   // Short_t         boostedTau_jetIdx[4];   //[nboostedTau]
   // Short_t         boostedTau_rawAntiEleCat2018[4];   //[nboostedTau]
   // Int_t           boostedTau_charge[4];   //[nboostedTau]
   // Int_t           boostedTau_decayMode[4];   //[nboostedTau]
   // Float_t         boostedTau_chargedIso[4];   //[nboostedTau]
   // Float_t         boostedTau_eta[4];   //[nboostedTau]
   // Float_t         boostedTau_leadTkDeltaEta[4];   //[nboostedTau]
   // Float_t         boostedTau_leadTkDeltaPhi[4];   //[nboostedTau]
   // Float_t         boostedTau_leadTkPtOverTauPt[4];   //[nboostedTau]
   // Float_t         boostedTau_mass[4];   //[nboostedTau]
   // Float_t         boostedTau_neutralIso[4];   //[nboostedTau]
   // Float_t         boostedTau_phi[4];   //[nboostedTau]
   // Float_t         boostedTau_photonsOutsideSignalCone[4];   //[nboostedTau]
   // Float_t         boostedTau_pt[4];   //[nboostedTau]
   // Float_t         boostedTau_puCorr[4];   //[nboostedTau]
   // Float_t         boostedTau_rawAntiEle2018[4];   //[nboostedTau]
   // Float_t         boostedTau_rawIso[4];   //[nboostedTau]
   // Float_t         boostedTau_rawIsodR03[4];   //[nboostedTau]
   // Float_t         boostedTau_rawMVAnewDM2017v2[4];   //[nboostedTau]
   // Float_t         boostedTau_rawMVAoldDM2017v2[4];   //[nboostedTau]
   // Float_t         CaloMET_phi;
   // Float_t         CaloMET_pt;
   // Float_t         CaloMET_sumEt;
   // Float_t         ChsMET_phi;
   // Float_t         ChsMET_pt;
   // Float_t         ChsMET_sumEt;
   // Int_t           nCorrT1METJet;
   // Float_t         CorrT1METJet_area[15];   //[nCorrT1METJet]
   // Float_t         CorrT1METJet_eta[15];   //[nCorrT1METJet]
   // Float_t         CorrT1METJet_muonSubtrFactor[15];   //[nCorrT1METJet]
   // Float_t         CorrT1METJet_phi[15];   //[nCorrT1METJet]
   // Float_t         CorrT1METJet_rawPt[15];   //[nCorrT1METJet]
   // Float_t         DeepMETResolutionTune_phi;
   // Float_t         DeepMETResolutionTune_pt;
   // Float_t         DeepMETResponseTune_phi;
   // Float_t         DeepMETResponseTune_pt;
   Int_t           nElectron;
   Char_t          Electron_seediEtaOriX[4];   //[nElectron]
   Bool_t          Electron_convVeto[4];   //[nElectron]
   UChar_t         Electron_cutBased[4];   //[nElectron]
   Bool_t          Electron_cutBased_HEEP[4];   //[nElectron]
   Bool_t          Electron_isPFcand[4];   //[nElectron]
   UChar_t         Electron_jetNDauCharged[4];   //[nElectron]
   UChar_t         Electron_lostHits[4];   //[nElectron]
   Bool_t          Electron_mvaIso_WP80[4];   //[nElectron]
   Bool_t          Electron_mvaIso_WP90[4];   //[nElectron]
   Bool_t          Electron_mvaNoIso_WP80[4];   //[nElectron]
   Bool_t          Electron_mvaNoIso_WP90[4];   //[nElectron]
   UChar_t         Electron_seedGain[4];   //[nElectron]
   UChar_t         Electron_tightCharge[4];   //[nElectron]
   Short_t         Electron_jetIdx[4];   //[nElectron]
   // Short_t         Electron_photonIdx[4];   //[nElectron]
   Short_t         Electron_svIdx[4];   //[nElectron]
   // Short_t         Electron_fsrPhotonIdx[4];   //[nElectron]
   Int_t           Electron_charge[4];   //[nElectron]
   Int_t           Electron_pdgId[4];   //[nElectron]
   Int_t           Electron_seediPhiOriY[4];   //[nElectron]
   Int_t           Electron_vidNestedWPBitmap[4];   //[nElectron]
   Int_t           Electron_vidNestedWPBitmapHEEP[4];   //[nElectron]
   Float_t         Electron_deltaEtaSC[4];   //[nElectron]
   // Float_t         Electron_dr03EcalRecHitSumEt[4];   //[nElectron]
   // Float_t         Electron_dr03HcalDepth1TowerSumEt[4];   //[nElectron]
   // Float_t         Electron_dr03TkSumPt[4];   //[nElectron]
   // Float_t         Electron_dr03TkSumPtHEEP[4];   //[nElectron]
   Float_t         Electron_dxy[4];   //[nElectron]
   Float_t         Electron_dxyErr[4];   //[nElectron]
   Float_t         Electron_dz[4];   //[nElectron]
   Float_t         Electron_dzErr[4];   //[nElectron]
   Float_t         Electron_eInvMinusPInv[4];   //[nElectron]
   Float_t         Electron_energyErr[4];   //[nElectron]
   Float_t         Electron_eta[4];   //[nElectron]
   Float_t         Electron_hoe[4];   //[nElectron]
   Float_t         Electron_ip3d[4];   //[nElectron]
   Float_t         Electron_jetPtRelv2[4];   //[nElectron]
   Float_t         Electron_jetRelIso[4];   //[nElectron]
   Float_t         Electron_mass[4];   //[nElectron]
   Float_t         Electron_miniPFRelIso_all[4];   //[nElectron]
   Float_t         Electron_miniPFRelIso_chg[4];   //[nElectron]
   Float_t         Electron_mvaHZZIso[4];   //[nElectron]
   Float_t         Electron_mvaIso[4];   //[nElectron]
   Float_t         Electron_mvaNoIso[4];   //[nElectron]
   Float_t         Electron_pfRelIso03_all[4];   //[nElectron]
   Float_t         Electron_pfRelIso03_chg[4];   //[nElectron]
   Float_t         Electron_phi[4];   //[nElectron]
   Float_t         Electron_pt[4];   //[nElectron]
   Float_t         Electron_r9[4];   //[nElectron]
   Float_t         Electron_scEtOverPt[4];   //[nElectron]
   Float_t         Electron_sieie[4];   //[nElectron]
   Float_t         Electron_sip3d[4];   //[nElectron]
   //Float_t         Electron_mvaTTH[4];   //[nElectron]
   Int_t           nFatJet;
   //UChar_t         FatJet_jetId[3];   //[nFatJet]
   UChar_t         FatJet_nConstituents[3];   //[nFatJet]
   Short_t         FatJet_subJetIdx1[3];   //[nFatJet]
   Short_t         FatJet_subJetIdx2[3];   //[nFatJet]
   Short_t         FatJet_electronIdx3SJ[3];   //[nFatJet]
   Short_t         FatJet_muonIdx3SJ[3];   //[nFatJet]
   Float_t         FatJet_area[3];   //[nFatJet]
   //Float_t         FatJet_btagDDBvLV2[3];   //[nFatJet]
   //Float_t         FatJet_btagDDCvBV2[3];   //[nFatJet]
   //Float_t         FatJet_btagDDCvLV2[3];   //[nFatJet]
   //Float_t         FatJet_btagDeepB[3];   //[nFatJet]
   //Float_t         FatJet_btagHbb[3];   //[nFatJet]
   Float_t         FatJet_eta[3];   //[nFatJet]
   Float_t         FatJet_mass[3];   //[nFatJet]
   Float_t         FatJet_msoftdrop[3];   //[nFatJet]
   Float_t         FatJet_n2b1[3];   //[nFatJet]
   Float_t         FatJet_n3b1[3];   //[nFatJet]
   // Float_t         FatJet_particleNetWithMass_H4qvsQCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNetWithMass_HbbvsQCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNetWithMass_HccvsQCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNetWithMass_QCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNetWithMass_TvsQCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNetWithMass_WvsQCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNetWithMass_ZvsQCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNet_QCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNet_QCD0HF[3];   //[nFatJet]
   // Float_t         FatJet_particleNet_QCD1HF[3];   //[nFatJet]
   // Float_t         FatJet_particleNet_QCD2HF[3];   //[nFatJet]
   // Float_t         FatJet_particleNet_XbbVsQCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNet_XccVsQCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNet_XggVsQCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNet_XqqVsQCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNet_XteVsQCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNet_XtmVsQCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNet_XttVsQCD[3];   //[nFatJet]
   // Float_t         FatJet_particleNet_massCorr[3];   //[nFatJet]
   Float_t         FatJet_phi[3];   //[nFatJet]
   Float_t         FatJet_pt[3];   //[nFatJet]
   Float_t         FatJet_rawFactor[3];   //[nFatJet]
   Float_t         FatJet_tau1[3];   //[nFatJet]
   Float_t         FatJet_tau2[3];   //[nFatJet]
   Float_t         FatJet_tau3[3];   //[nFatJet]
   Float_t         FatJet_tau4[3];   //[nFatJet]
   Float_t         FatJet_lsf3[3];   //[nFatJet]
   // Int_t           nFsrPhoton;
   // Short_t         FsrPhoton_electronIdx[2];   //[nFsrPhoton]
   // Short_t         FsrPhoton_muonIdx[2];   //[nFsrPhoton]
   // Float_t         FsrPhoton_dROverEt2[2];   //[nFsrPhoton]
   // Float_t         FsrPhoton_eta[2];   //[nFsrPhoton]
   // Float_t         FsrPhoton_phi[2];   //[nFsrPhoton]
   // Float_t         FsrPhoton_pt[2];   //[nFsrPhoton]
   // Float_t         FsrPhoton_relIso03[2];   //[nFsrPhoton]
   // Int_t           nGenJetAK8;
   // Float_t         GenJetAK8_eta[5];   //[nGenJetAK8]
   // Float_t         GenJetAK8_mass[5];   //[nGenJetAK8]
   // Float_t         GenJetAK8_phi[5];   //[nGenJetAK8]
   // Float_t         GenJetAK8_pt[5];   //[nGenJetAK8]
   Int_t           nGenJet;
   Float_t         GenJet_eta[17];   //[nGenJet]
   Float_t         GenJet_mass[17];   //[nGenJet]
   Float_t         GenJet_phi[17];   //[nGenJet]
   Float_t         GenJet_pt[17];   //[nGenJet]
   Int_t           nGenPart;
   Short_t         GenPart_genPartIdxMother[84];   //[nGenPart]
   UShort_t        GenPart_statusFlags[84];   //[nGenPart]
   Int_t           GenPart_pdgId[84];   //[nGenPart]
   Int_t           GenPart_status[84];   //[nGenPart]
   Float_t         GenPart_eta[84];   //[nGenPart]
   Float_t         GenPart_mass[84];   //[nGenPart]
   Float_t         GenPart_phi[84];   //[nGenPart]
   Float_t         GenPart_pt[84];   //[nGenPart]
   // Int_t           nGenProton;
   // Bool_t          GenProton_isPU[10];   //[nGenProton]
   // Float_t         GenProton_px[10];   //[nGenProton]
   // Float_t         GenProton_py[10];   //[nGenProton]
   // Float_t         GenProton_pz[10];   //[nGenProton]
   // Float_t         GenProton_vz[10];   //[nGenProton]
   // Int_t           nSubGenJetAK8;
   // Float_t         SubGenJetAK8_eta[9];   //[nSubGenJetAK8]
   // Float_t         SubGenJetAK8_mass[9];   //[nSubGenJetAK8]
   // Float_t         SubGenJetAK8_phi[9];   //[nSubGenJetAK8]
   // Float_t         SubGenJetAK8_pt[9];   //[nSubGenJetAK8]
   // Int_t           Generator_id1;
   // Int_t           Generator_id2;
   // Float_t         Generator_binvar;
   // Float_t         Generator_scalePDF;
   // Float_t         Generator_weight;
   // Float_t         Generator_x1;
   // Float_t         Generator_x2;
   // Float_t         Generator_xpdf1;
   // Float_t         Generator_xpdf2;
   // Float_t         GenVtx_x;
   // Float_t         GenVtx_y;
   // Float_t         GenVtx_z;
   // Int_t           nGenVisTau;
   // UChar_t         GenVisTau_status[1];   //[nGenVisTau]
   // Short_t         GenVisTau_charge[1];   //[nGenVisTau]
   // Short_t         GenVisTau_genPartIdxMother[1];   //[nGenVisTau]
   // Float_t         GenVisTau_eta[1];   //[nGenVisTau]
   // Float_t         GenVisTau_mass[1];   //[nGenVisTau]
   // Float_t         GenVisTau_phi[1];   //[nGenVisTau]
   // Float_t         GenVisTau_pt[1];   //[nGenVisTau]
   Float_t         genWeight;
   // Float_t         LHEWeight_originalXWGTUP;
   // Int_t           nLHEPdfWeight;
   // Float_t         LHEPdfWeight[103];   //[nLHEPdfWeight]
   // Int_t           nLHEReweightingWeight;
   // Float_t         LHEReweightingWeight[1];   //[nLHEReweightingWeight]
   // Int_t           nLHEScaleWeight;
   // Float_t         LHEScaleWeight[9];   //[nLHEScaleWeight]
   // Int_t           nPSWeight;
   // Float_t         PSWeight[4];   //[nPSWeight]
   // Int_t           nIsoTrack;
   // Bool_t          IsoTrack_isHighPurityTrack[31];   //[nIsoTrack]
   // Bool_t          IsoTrack_isPFcand[31];   //[nIsoTrack]
   // Bool_t          IsoTrack_isFromLostTrack[31];   //[nIsoTrack]
   // Short_t         IsoTrack_charge[31];   //[nIsoTrack]
   // Short_t         IsoTrack_fromPV[31];   //[nIsoTrack]
   // Int_t           IsoTrack_pdgId[31];   //[nIsoTrack]
   // Float_t         IsoTrack_dxy[31];   //[nIsoTrack]
   // Float_t         IsoTrack_dz[31];   //[nIsoTrack]
   // Float_t         IsoTrack_eta[31];   //[nIsoTrack]
   // Float_t         IsoTrack_pfRelIso03_all[31];   //[nIsoTrack]
   // Float_t         IsoTrack_pfRelIso03_chg[31];   //[nIsoTrack]
   // Float_t         IsoTrack_phi[31];   //[nIsoTrack]
   // Float_t         IsoTrack_pt[31];   //[nIsoTrack]
   // Float_t         IsoTrack_miniPFRelIso_all[31];   //[nIsoTrack]
   // Float_t         IsoTrack_miniPFRelIso_chg[31];   //[nIsoTrack]
   Int_t           nJet;
   UChar_t         Jet_jetId[14];   //[nJet]
   UChar_t         Jet_chMultiplicity[14];   //[nJet]
   UChar_t         Jet_neMultiplicity[14];   //[nJet]
   UChar_t         Jet_nConstituents[14];   //[nJet]
   UChar_t         Jet_nElectrons[14];   //[nJet]
   UChar_t         Jet_nMuons[14];   //[nJet]
   UChar_t         Jet_nSVs[14];   //[nJet]
   Short_t         Jet_electronIdx1[14];   //[nJet]
   Short_t         Jet_electronIdx2[14];   //[nJet]
   Short_t         Jet_muonIdx1[14];   //[nJet]
   Short_t         Jet_muonIdx2[14];   //[nJet]
   Short_t         Jet_svIdx1[14];   //[nJet]
   Short_t         Jet_svIdx2[14];   //[nJet]
   Int_t           Jet_hfadjacentEtaStripsSize[14];   //[nJet]
   Int_t           Jet_hfcentralEtaStripSize[14];   //[nJet]
   Float_t         Jet_PNetRegPtRawCorr[14];   //[nJet]
   Float_t         Jet_PNetRegPtRawCorrNeutrino[14];   //[nJet]
   Float_t         Jet_PNetRegPtRawRes[14];   //[nJet]
   Float_t         Jet_area[14];   //[nJet]
   Float_t         Jet_btagDeepFlavB[14];   //[nJet]
   Float_t         Jet_btagDeepFlavCvB[14];   //[nJet]
   Float_t         Jet_btagDeepFlavCvL[14];   //[nJet]
   Float_t         Jet_btagDeepFlavQG[14];   //[nJet]
   Float_t         Jet_btagPNetB[14];   //[nJet]
   Float_t         Jet_btagPNetCvB[14];   //[nJet]
   Float_t         Jet_btagPNetCvL[14];   //[nJet]
   Float_t         Jet_btagPNetQvG[14];   //[nJet]
   Float_t         Jet_btagPNetTauVJet[14];   //[nJet]
   //Float_t         Jet_btagRobustParTAK4B[14];   //[nJet]
   //Float_t         Jet_btagRobustParTAK4CvB[14];   //[nJet]
   //Float_t         Jet_btagRobustParTAK4CvL[14];   //[nJet]
   //Float_t         Jet_btagRobustParTAK4QG[14];   //[nJet]
   Float_t         Jet_chEmEF[14];   //[nJet]
   Float_t         Jet_chHEF[14];   //[nJet]
   Float_t         Jet_eta[14];   //[nJet]
   Float_t         Jet_hfsigmaEtaEta[14];   //[nJet]
   Float_t         Jet_hfsigmaPhiPhi[14];   //[nJet]
   Float_t         Jet_mass[14];   //[nJet]
   Float_t         Jet_muEF[14];   //[nJet]
   Float_t         Jet_muonSubtrFactor[14];   //[nJet]
   Float_t         Jet_neEmEF[14];   //[nJet]
   Float_t         Jet_neHEF[14];   //[nJet]
   Float_t         Jet_phi[14];   //[nJet]
   Float_t         Jet_pt[14];   //[nJet]
   Float_t         Jet_rawFactor[14];   //[nJet]
   // UChar_t         LHE_Njets;
   // UChar_t         LHE_Nb;
   // UChar_t         LHE_Nc;
   // UChar_t         LHE_Nuds;
   // UChar_t         LHE_Nglu;
   // UChar_t         LHE_NpNLO;
   // UChar_t         LHE_NpLO;
   // Float_t         LHE_HT;
   // Float_t         LHE_HTIncoming;
   // Float_t         LHE_Vpt;
   // Float_t         LHE_AlphaS;
   // Int_t           nLHEPart;
   // Int_t           LHEPart_pdgId[6];   //[nLHEPart]
   // Int_t           LHEPart_status[6];   //[nLHEPart]
   // Int_t           LHEPart_spin[6];   //[nLHEPart]
   // Float_t         LHEPart_pt[6];   //[nLHEPart]
   // Float_t         LHEPart_eta[6];   //[nLHEPart]
   // Float_t         LHEPart_phi[6];   //[nLHEPart]
   // Float_t         LHEPart_mass[6];   //[nLHEPart]
   // Float_t         LHEPart_incomingpz[6];   //[nLHEPart]
   // Int_t           nLowPtElectron;
   // Bool_t          LowPtElectron_convVeto[5];   //[nLowPtElectron]
   // UChar_t         LowPtElectron_convWP[5];   //[nLowPtElectron]
   // UChar_t         LowPtElectron_lostHits[5];   //[nLowPtElectron]
   // Short_t         LowPtElectron_electronIdx[5];   //[nLowPtElectron]
   // Short_t         LowPtElectron_photonIdx[5];   //[nLowPtElectron]
   // Int_t           LowPtElectron_charge[5];   //[nLowPtElectron]
   // Int_t           LowPtElectron_pdgId[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_ID[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_convVtxRadius[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_deltaEtaSC[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_dxy[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_dxyErr[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_dz[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_dzErr[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_eInvMinusPInv[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_energyErr[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_eta[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_hoe[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_mass[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_miniPFRelIso_all[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_miniPFRelIso_chg[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_phi[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_pt[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_ptbiased[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_r9[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_scEtOverPt[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_sieie[5];   //[nLowPtElectron]
   // Float_t         LowPtElectron_unbiased[5];   //[nLowPtElectron]
   Float_t         GenMET_phi;
   Float_t         GenMET_pt;
   //Float_t         MET_MetUnclustEnUpDeltaX;
   //Float_t         MET_MetUnclustEnUpDeltaY;
   //Float_t         MET_covXX;
   //Float_t         MET_covXY;
   //Float_t         MET_covYY;
   //Float_t         MET_phi;
   //Float_t         MET_pt;
   //Float_t         MET_significance;
   //Float_t         MET_sumEt;
   //Float_t         MET_sumPtUnclustered;
   Int_t           nMuon;
   UChar_t         Muon_highPtId[20];   //[nMuon]
   Bool_t          Muon_highPurity[20];   //[nMuon]
   Bool_t          Muon_inTimeMuon[20];   //[nMuon]
   Bool_t          Muon_isGlobal[20];   //[nMuon]
   Bool_t          Muon_isPFcand[20];   //[nMuon]
   Bool_t          Muon_isStandalone[20];   //[nMuon]
   Bool_t          Muon_isTracker[20];   //[nMuon]
   UChar_t         Muon_jetNDauCharged[20];   //[nMuon]
   Bool_t          Muon_looseId[20];   //[nMuon]
   Bool_t          Muon_mediumId[20];   //[nMuon]
   Bool_t          Muon_mediumPromptId[20];   //[nMuon]
   UChar_t         Muon_miniIsoId[20];   //[nMuon]
   UChar_t         Muon_multiIsoId[20];   //[nMuon]
   UChar_t         Muon_mvaMuID_WP[20];   //[nMuon]
   UChar_t         Muon_nStations[20];   //[nMuon]
   UChar_t         Muon_nTrackerLayers[20];   //[nMuon]
   UChar_t         Muon_pfIsoId[20];   //[nMuon]
   UChar_t         Muon_puppiIsoId[20];   //[nMuon]
   Bool_t          Muon_softId[20];   //[nMuon]
   Bool_t          Muon_softMvaId[20];   //[nMuon]
   UChar_t         Muon_tightCharge[20];   //[nMuon]
   Bool_t          Muon_tightId[20];   //[nMuon]
   UChar_t         Muon_tkIsoId[20];   //[nMuon]
   Bool_t          Muon_triggerIdLoose[20];   //[nMuon]
   Short_t         Muon_jetIdx[20];   //[nMuon]
   Short_t         Muon_svIdx[20];   //[nMuon]
   // Short_t         Muon_fsrPhotonIdx[20];   //[nMuon]
   Int_t           Muon_charge[20];   //[nMuon]
   Int_t           Muon_pdgId[20];   //[nMuon]
   Float_t         Muon_dxy[20];   //[nMuon]
   Float_t         Muon_dxyErr[20];   //[nMuon]
   Float_t         Muon_dxybs[20];   //[nMuon]
   Float_t         Muon_dz[20];   //[nMuon]
   Float_t         Muon_dzErr[20];   //[nMuon]
   Float_t         Muon_eta[20];   //[nMuon]
   Float_t         Muon_ip3d[20];   //[nMuon]
   Float_t         Muon_jetPtRelv2[20];   //[nMuon]
   Float_t         Muon_jetRelIso[20];   //[nMuon]
   Float_t         Muon_mass[20];   //[nMuon]
   Float_t         Muon_miniPFRelIso_all[20];   //[nMuon]
   Float_t         Muon_miniPFRelIso_chg[20];   //[nMuon]
   Float_t         Muon_mvaMuID[20];   //[nMuon]
   Float_t         Muon_pfRelIso03_all[20];   //[nMuon]
   Float_t         Muon_pfRelIso03_chg[20];   //[nMuon]
   Float_t         Muon_pfRelIso04_all[20];   //[nMuon]
   Float_t         Muon_phi[20];   //[nMuon]
   Float_t         Muon_pt[20];   //[nMuon]
   Float_t         Muon_ptErr[20];   //[nMuon]
   Float_t         Muon_segmentComp[20];   //[nMuon]
   Float_t         Muon_sip3d[20];   //[nMuon]
   Float_t         Muon_softMva[20];   //[nMuon]
   Float_t         Muon_tkRelIso[20];   //[nMuon]
   Float_t         Muon_tunepRelPt[20];   //[nMuon]
   Float_t         Muon_bsConstrainedChi2[20];   //[nMuon]
   Float_t         Muon_bsConstrainedPt[20];   //[nMuon]
   Float_t         Muon_bsConstrainedPtErr[20];   //[nMuon]
   // Float_t         Muon_mvaLowPt[6];   //[nMuon]
   //Float_t          Muon_mvaTTH[6];   //[nMuon]
   // Int_t           nPhoton;
   // Char_t          Photon_seediEtaOriX[5];   //[nPhoton]
   // UChar_t         Photon_cutBased[5];   //[nPhoton]
   // Bool_t          Photon_electronVeto[5];   //[nPhoton]
   // Bool_t          Photon_hasConversionTracks[5];   //[nPhoton]
   // Bool_t          Photon_isScEtaEB[5];   //[nPhoton]
   // Bool_t          Photon_isScEtaEE[5];   //[nPhoton]
   // Bool_t          Photon_mvaID_WP80[5];   //[nPhoton]
   // Bool_t          Photon_mvaID_WP90[5];   //[nPhoton]
   // Bool_t          Photon_pixelSeed[5];   //[nPhoton]
   // UChar_t         Photon_seedGain[5];   //[nPhoton]
   // Short_t         Photon_electronIdx[5];   //[nPhoton]
   // Short_t         Photon_jetIdx[5];   //[nPhoton]
   // Int_t           Photon_seediPhiOriY[5];   //[nPhoton]
   // Int_t           Photon_vidNestedWPBitmap[5];   //[nPhoton]
   // Float_t         Photon_ecalPFClusterIso[5];   //[nPhoton]
   // Float_t         Photon_energyErr[5];   //[nPhoton]
   // Float_t         Photon_energyRaw[5];   //[nPhoton]
   // Float_t         Photon_esEffSigmaRR[5];   //[nPhoton]
   // Float_t         Photon_esEnergyOverRawE[5];   //[nPhoton]
   // Float_t         Photon_eta[5];   //[nPhoton]
   // Float_t         Photon_etaWidth[5];   //[nPhoton]
   // Float_t         Photon_haloTaggerMVAVal[5];   //[nPhoton]
   // Float_t         Photon_hcalPFClusterIso[5];   //[nPhoton]
   // Float_t         Photon_hoe[5];   //[nPhoton]
   // Float_t         Photon_hoe_PUcorr[5];   //[nPhoton]
   // Float_t         Photon_mvaID[5];   //[nPhoton]
   // Float_t         Photon_pfChargedIso[5];   //[nPhoton]
   // Float_t         Photon_pfChargedIsoPFPV[5];   //[nPhoton]
   // Float_t         Photon_pfChargedIsoWorstVtx[5];   //[nPhoton]
   // Float_t         Photon_pfPhoIso03[5];   //[nPhoton]
   // Float_t         Photon_pfRelIso03_all_quadratic[5];   //[nPhoton]
   // Float_t         Photon_pfRelIso03_chg_quadratic[5];   //[nPhoton]
   // Float_t         Photon_phi[5];   //[nPhoton]
   // Float_t         Photon_phiWidth[5];   //[nPhoton]
   // Float_t         Photon_pt[5];   //[nPhoton]
   // Float_t         Photon_r9[5];   //[nPhoton]
   // Float_t         Photon_s4[5];   //[nPhoton]
   // Float_t         Photon_sieie[5];   //[nPhoton]
   // Float_t         Photon_sieip[5];   //[nPhoton]
   // Float_t         Photon_sipip[5];   //[nPhoton]
   // Float_t         Photon_trkSumPtHollowConeDR03[5];   //[nPhoton]
   // Float_t         Photon_trkSumPtSolidConeDR04[5];   //[nPhoton]
   // Float_t         Photon_x_calo[5];   //[nPhoton]
   // Float_t         Photon_y_calo[5];   //[nPhoton]
   // Float_t         Photon_z_calo[5];   //[nPhoton]
   Int_t           Pileup_nPU;
   Int_t           Pileup_sumEOOT;
   Int_t           Pileup_sumLOOT;
   Float_t         Pileup_nTrueInt;
   Float_t         Pileup_pudensity;
   Float_t         Pileup_gpudensity;
   Float_t         PuppiMET_phi;
   //Float_t         PuppiMET_phiJERDown;
   //Float_t         PuppiMET_phiJERUp;
   //Float_t         PuppiMET_phiJESDown;
   //Float_t         PuppiMET_phiJESUp;
   Float_t         PuppiMET_phiUnclusteredDown;
   Float_t         PuppiMET_phiUnclusteredUp;
   Float_t         PuppiMET_pt;
   //Float_t         PuppiMET_ptJERDown;
   //Float_t         PuppiMET_ptJERUp;
   //Float_t         PuppiMET_ptJESDown;
   //Float_t         PuppiMET_ptJESUp;
   Float_t         PuppiMET_ptUnclusteredDown;
   Float_t         PuppiMET_ptUnclusteredUp;
   Float_t         PuppiMET_sumEt;
   //Float_t         RawMET_phi;
   //Float_t         RawMET_pt;
   //Float_t         RawMET_sumEt;
   Float_t         RawPuppiMET_phi;
   Float_t         RawPuppiMET_pt;
   Float_t         RawPuppiMET_sumEt;
   Float_t         Rho_fixedGridRhoAll;
   Float_t         Rho_fixedGridRhoFastjetAll;
   Float_t         Rho_fixedGridRhoFastjetCentral;
   Float_t         Rho_fixedGridRhoFastjetCentralCalo;
   Float_t         Rho_fixedGridRhoFastjetCentralChargedPileUp;
   Float_t         Rho_fixedGridRhoFastjetCentralNeutral;
   Int_t           nGenDressedLepton;
   Bool_t          GenDressedLepton_hasTauAnc[4];   //[nGenDressedLepton]
   Int_t           GenDressedLepton_pdgId[4];   //[nGenDressedLepton]
   Float_t         GenDressedLepton_eta[4];   //[nGenDressedLepton]
   Float_t         GenDressedLepton_mass[4];   //[nGenDressedLepton]
   Float_t         GenDressedLepton_phi[4];   //[nGenDressedLepton]
   Float_t         GenDressedLepton_pt[4];   //[nGenDressedLepton]
   // Int_t           nGenIsolatedPhoton;
   // Float_t         GenIsolatedPhoton_eta[2];   //[nGenIsolatedPhoton]
   // Float_t         GenIsolatedPhoton_mass[2];   //[nGenIsolatedPhoton]
   // Float_t         GenIsolatedPhoton_phi[2];   //[nGenIsolatedPhoton]
   // Float_t         GenIsolatedPhoton_pt[2];   //[nGenIsolatedPhoton]
   Int_t           nSoftActivityJet;
   Float_t         SoftActivityJet_eta[6];   //[nSoftActivityJet]
   Float_t         SoftActivityJet_phi[6];   //[nSoftActivityJet]
   Float_t         SoftActivityJet_pt[6];   //[nSoftActivityJet]
   Int_t           SoftActivityJetNjets10;
   Int_t           SoftActivityJetNjets2;
   Int_t           SoftActivityJetNjets5;
   Float_t         SoftActivityJetHT;
   Float_t         SoftActivityJetHT10;
   Float_t         SoftActivityJetHT2;
   Float_t         SoftActivityJetHT5;
   Int_t           nSubJet;
   //Float_t         SubJet_btagDeepB[6];   //[nSubJet]
   Float_t         SubJet_eta[6];   //[nSubJet]
   Float_t         SubJet_mass[6];   //[nSubJet]
   Float_t         SubJet_n2b1[6];   //[nSubJet]
   Float_t         SubJet_n3b1[6];   //[nSubJet]
   Float_t         SubJet_phi[6];   //[nSubJet]
   Float_t         SubJet_pt[6];   //[nSubJet]
   Float_t         SubJet_rawFactor[6];   //[nSubJet]
   Float_t         SubJet_tau1[6];   //[nSubJet]
   Float_t         SubJet_tau2[6];   //[nSubJet]
   Float_t         SubJet_tau3[6];   //[nSubJet]
   Float_t         SubJet_tau4[6];   //[nSubJet]
   Int_t           nTau;
   UChar_t         Tau_decayMode[7];   //[nTau]
   Bool_t          Tau_idAntiEleDeadECal[7];   //[nTau]
   UChar_t         Tau_idAntiMu[7];   //[nTau]
   Bool_t          Tau_idDecayModeNewDMs[7];   //[nTau]
   Bool_t          Tau_idDecayModeOldDMs[7];   //[nTau]
   //UChar_t         Tau_idDeepTau2017v2p1VSe[7];   //[nTau]
   //UChar_t         Tau_idDeepTau2017v2p1VSjet[7];   //[nTau]
   //UChar_t         Tau_idDeepTau2017v2p1VSmu[7];   //[nTau]
   //UChar_t         Tau_idDeepTau2018v2p5VSe[7];   //[nTau]
   //UChar_t         Tau_idDeepTau2018v2p5VSjet[7];   //[nTau]
   //UChar_t         Tau_idDeepTau2018v2p5VSmu[7];   //[nTau]
   UChar_t         Tau_nSVs[7];   //[nTau]
   Short_t         Tau_charge[7];   //[nTau]
   Short_t         Tau_decayModePNet[7];   //[nTau]
   Short_t         Tau_eleIdx[7];   //[nTau]
   Short_t         Tau_jetIdx[7];   //[nTau]
   Short_t         Tau_muIdx[7];   //[nTau]
   Short_t         Tau_svIdx1[7];   //[nTau]
   Short_t         Tau_svIdx2[7];   //[nTau]
   Float_t         Tau_chargedIso[7];   //[nTau]
   Float_t         Tau_dxy[7];   //[nTau]
   Float_t         Tau_dz[7];   //[nTau]
   Float_t         Tau_eta[7];   //[nTau]
   Float_t         Tau_leadTkDeltaEta[7];   //[nTau]
   Float_t         Tau_leadTkDeltaPhi[7];   //[nTau]
   Float_t         Tau_leadTkPtOverTauPt[7];   //[nTau]
   Float_t         Tau_mass[7];   //[nTau]
   Float_t         Tau_neutralIso[7];   //[nTau]
   Float_t         Tau_phi[7];   //[nTau]
   // Float_t         Tau_photonsOutsideSignalCone[7];   //[nTau]
   Float_t         Tau_probDM0PNet[7];   //[nTau]
   Float_t         Tau_probDM10PNet[7];   //[nTau]
   Float_t         Tau_probDM11PNet[7];   //[nTau]
   Float_t         Tau_probDM1PNet[7];   //[nTau]
   Float_t         Tau_probDM2PNet[7];   //[nTau]
   Float_t         Tau_pt[7];   //[nTau]
   Float_t         Tau_ptCorrPNet[7];   //[nTau]
   Float_t         Tau_puCorr[7];   //[nTau]
   Float_t         Tau_qConfPNet[7];   //[nTau]
   //Float_t         Tau_rawDeepTau2017v2p1VSe[7];   //[nTau]
   //Float_t         Tau_rawDeepTau2017v2p1VSjet[7];   //[nTau]
   //Float_t         Tau_rawDeepTau2017v2p1VSmu[7];   //[nTau]
   //Float_t         Tau_rawDeepTau2018v2p5VSe[7];   //[nTau]
   //Float_t         Tau_rawDeepTau2018v2p5VSjet[7];   //[nTau]
   //Float_t         Tau_rawDeepTau2018v2p5VSmu[7];   //[nTau]
   Float_t         Tau_rawIso[7];   //[nTau]
   // Float_t         Tau_rawIsodR03[7];   //[nTau]
   Float_t         Tau_rawPNetVSe[7];   //[nTau]
   Float_t         Tau_rawPNetVSjet[7];   //[nTau]
   Float_t         Tau_rawPNetVSmu[7];   //[nTau]
   //Float_t         TkMET_phi;
   //Float_t         TkMET_pt;
   //Float_t         TkMET_sumEt;
   Int_t           nTrigObj;
   Short_t         TrigObj_l1charge[52];   //[nTrigObj]
   UShort_t        TrigObj_id[52];   //[nTrigObj]
   Int_t           TrigObj_l1iso[52];   //[nTrigObj]
   Int_t           TrigObj_filterBits[52];   //[nTrigObj]
   Float_t         TrigObj_pt[52];   //[nTrigObj]
   Float_t         TrigObj_eta[52];   //[nTrigObj]
   Float_t         TrigObj_phi[52];   //[nTrigObj]
   Float_t         TrigObj_l1pt[52];   //[nTrigObj]
   Float_t         TrigObj_l1pt_2[52];   //[nTrigObj]
   Float_t         TrigObj_l2pt[52];   //[nTrigObj]
   Int_t           genTtbarId;
   Int_t           nOtherPV;
   Float_t         OtherPV_z[3];   //[nOtherPV]
   Float_t         OtherPV_score[3];   //[nOtherPV]
   UChar_t         PV_npvs;
   UChar_t         PV_npvsGood;
   Float_t         PV_ndof;
   Float_t         PV_x;
   Float_t         PV_y;
   Float_t         PV_z;
   Float_t         PV_chi2;
   Float_t         PV_score;
   Int_t           nSV;
   Short_t         SV_charge[11];   //[nSV]
   Float_t         SV_dlen[11];   //[nSV]
   Float_t         SV_dlenSig[11];   //[nSV]
   Float_t         SV_dxy[11];   //[nSV]
   Float_t         SV_dxySig[11];   //[nSV]
   Float_t         SV_pAngle[11];   //[nSV]
   // UChar_t         boostedTau_genPartFlav[4];   //[nboostedTau]
   // Short_t         boostedTau_genPartIdx[4];   //[nboostedTau]
   UChar_t         Electron_genPartFlav[4];   //[nElectron]
   Short_t         Electron_genPartIdx[4];   //[nElectron]
   UChar_t         FatJet_hadronFlavour[3];   //[nFatJet]
   //UChar_t         FatJet_nBHadrons[3];   //[nFatJet]
   //UChar_t         FatJet_nCHadrons[3];   //[nFatJet]
   // Short_t         FatJet_genJetAK8Idx[3];   //[nFatJet]
   // UChar_t         GenJetAK8_hadronFlavour[5];   //[nGenJetAK8]
   // Short_t         GenJetAK8_partonFlavour[5];   //[nGenJetAK8]
   UChar_t         GenJet_hadronFlavour[17];   //[nGenJet]
   Short_t         GenJet_partonFlavour[17];   //[nGenJet]
   // Float_t         GenVtx_t0;
   UChar_t         Jet_hadronFlavour[14];   //[nJet]
   Short_t         Jet_genJetIdx[14];   //[nJet]
   Short_t         Jet_partonFlavour[14];   //[nJet]
   // UChar_t         LowPtElectron_genPartFlav[5];   //[nLowPtElectron]
   // Short_t         LowPtElectron_genPartIdx[5];   //[nLowPtElectron]
   UChar_t         Muon_genPartFlav[6];   //[nMuon]
   Short_t         Muon_genPartIdx[6];   //[nMuon]
   // UChar_t         Photon_genPartFlav[5];   //[nPhoton]
   // Short_t         Photon_genPartIdx[5];   //[nPhoton]
   //Float_t         MET_fiducialGenPhi;
   //Float_t         MET_fiducialGenPt;
   UChar_t         SubJet_hadronFlavour[6];   //[nSubJet]
   UChar_t         SubJet_nBHadrons[6];   //[nSubJet]
   UChar_t         SubJet_nCHadrons[6];   //[nSubJet]
   UChar_t         SV_ntracks[11];   //[nSV]
   Float_t         SV_chi2[11];   //[nSV]
   Float_t         SV_eta[11];   //[nSV]
   Float_t         SV_mass[11];   //[nSV]
   Float_t         SV_ndof[11];   //[nSV]
   Float_t         SV_phi[11];   //[nSV]
   Float_t         SV_pt[11];   //[nSV]
   Float_t         SV_x[11];   //[nSV]
   Float_t         SV_y[11];   //[nSV]
   Float_t         SV_z[11];   //[nSV]
   UChar_t         Tau_genPartFlav[7];   //[nTau]
   Short_t         Tau_genPartIdx[7];   //[nTau]
   // Bool_t          L1_AlwaysTrue;
   // Bool_t          L1_BPTX_AND_Ref1_VME;
   // Bool_t          L1_BPTX_AND_Ref3_VME;
   // Bool_t          L1_BPTX_AND_Ref4_VME;
   // Bool_t          L1_BPTX_BeamGas_B1_VME;
   // Bool_t          L1_BPTX_BeamGas_B2_VME;
   // Bool_t          L1_BPTX_BeamGas_Ref1_VME;
   // Bool_t          L1_BPTX_BeamGas_Ref2_VME;
   // Bool_t          L1_BPTX_NotOR_VME;
   // Bool_t          L1_BPTX_OR_Ref3_VME;
   // Bool_t          L1_BPTX_OR_Ref4_VME;
   // Bool_t          L1_BPTX_RefAND_VME;
   // Bool_t          L1_BptxMinus;
   // Bool_t          L1_BptxOR;
   // Bool_t          L1_BptxPlus;
   // Bool_t          L1_BptxXOR;
   // Bool_t          L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142;
   // Bool_t          L1_DoubleEG10_er1p2_dR_Max0p6;
   // Bool_t          L1_DoubleEG10p5_er1p2_dR_Max0p6;
   // Bool_t          L1_DoubleEG11_er1p2_dR_Max0p6;
   // Bool_t          L1_DoubleEG4_er1p2_dR_Max0p9;
   // Bool_t          L1_DoubleEG4p5_er1p2_dR_Max0p9;
   // Bool_t          L1_DoubleEG5_er1p2_dR_Max0p9;
   // Bool_t          L1_DoubleEG5p5_er1p2_dR_Max0p8;
   // Bool_t          L1_DoubleEG6_er1p2_dR_Max0p8;
   // Bool_t          L1_DoubleEG6p5_er1p2_dR_Max0p8;
   // Bool_t          L1_DoubleEG7_er1p2_dR_Max0p8;
   // Bool_t          L1_DoubleEG7p5_er1p2_dR_Max0p7;
   // Bool_t          L1_DoubleEG8_er1p2_dR_Max0p7;
   // Bool_t          L1_DoubleEG8er2p5_HTT260er;
   // Bool_t          L1_DoubleEG8er2p5_HTT280er;
   // Bool_t          L1_DoubleEG8er2p5_HTT300er;
   // Bool_t          L1_DoubleEG8er2p5_HTT320er;
   // Bool_t          L1_DoubleEG8er2p5_HTT340er;
   // Bool_t          L1_DoubleEG8p5_er1p2_dR_Max0p7;
   // Bool_t          L1_DoubleEG9_er1p2_dR_Max0p7;
   // Bool_t          L1_DoubleEG9p5_er1p2_dR_Max0p6;
   // Bool_t          L1_DoubleEG_15_10_er2p5;
   // Bool_t          L1_DoubleEG_20_10_er2p5;
   // Bool_t          L1_DoubleEG_22_10_er2p5;
   // Bool_t          L1_DoubleEG_25_12_er2p5;
   // Bool_t          L1_DoubleEG_25_14_er2p5;
   // Bool_t          L1_DoubleEG_27_14_er2p5;
   // Bool_t          L1_DoubleEG_LooseIso16_LooseIso12_er1p5;
   // Bool_t          L1_DoubleEG_LooseIso18_LooseIso12_er1p5;
   // Bool_t          L1_DoubleEG_LooseIso20_10_er2p5;
   // Bool_t          L1_DoubleEG_LooseIso20_LooseIso12_er1p5;
   // Bool_t          L1_DoubleEG_LooseIso22_10_er2p5;
   // Bool_t          L1_DoubleEG_LooseIso22_12_er2p5;
   // Bool_t          L1_DoubleEG_LooseIso22_LooseIso12_er1p5;
   // Bool_t          L1_DoubleEG_LooseIso25_12_er2p5;
   // Bool_t          L1_DoubleEG_LooseIso25_LooseIso12_er1p5;
   // Bool_t          L1_DoubleIsoTau26er2p1_Jet55_RmOvlp_dR0p5;
   // Bool_t          L1_DoubleIsoTau26er2p1_Jet70_RmOvlp_dR0p5;
   // Bool_t          L1_DoubleIsoTau28er2p1;
   // Bool_t          L1_DoubleIsoTau28er2p1_Mass_Max80;
   // Bool_t          L1_DoubleIsoTau28er2p1_Mass_Max90;
   // Bool_t          L1_DoubleIsoTau30er2p1;
   // Bool_t          L1_DoubleIsoTau30er2p1_Mass_Max80;
   // Bool_t          L1_DoubleIsoTau30er2p1_Mass_Max90;
   // Bool_t          L1_DoubleIsoTau32er2p1;
   // Bool_t          L1_DoubleIsoTau34er2p1;
   // Bool_t          L1_DoubleIsoTau35er2p1;
   // Bool_t          L1_DoubleIsoTau36er2p1;
   // Bool_t          L1_DoubleJet100er2p3_dEta_Max1p6;
   // Bool_t          L1_DoubleJet100er2p5;
   // Bool_t          L1_DoubleJet112er2p3_dEta_Max1p6;
   // Bool_t          L1_DoubleJet120er2p5;
   // Bool_t          L1_DoubleJet150er2p5;
   // Bool_t          L1_DoubleJet30er2p5_Mass_Min150_dEta_Max1p5;
   // Bool_t          L1_DoubleJet30er2p5_Mass_Min200_dEta_Max1p5;
   // Bool_t          L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5;
   // Bool_t          L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5;
   // Bool_t          L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5;
   // Bool_t          L1_DoubleJet30er2p5_Mass_Min360_dEta_Max1p5;
   // Bool_t          L1_DoubleJet35_Mass_Min450_IsoTau45_RmOvlp;
   // Bool_t          L1_DoubleJet35_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5;
   // Bool_t          L1_DoubleJet40er2p5;
   // Bool_t          L1_DoubleJet_100_30_DoubleJet30_Mass_Min620;
   // Bool_t          L1_DoubleJet_110_35_DoubleJet35_Mass_Min620;
   // Bool_t          L1_DoubleJet_115_40_DoubleJet40_Mass_Min620;
   // Bool_t          L1_DoubleJet_115_40_DoubleJet40_Mass_Min620_Jet60TT28;
   // Bool_t          L1_DoubleJet_120_45_DoubleJet45_Mass_Min620;
   // Bool_t          L1_DoubleJet_120_45_DoubleJet45_Mass_Min620_Jet60TT28;
   // Bool_t          L1_DoubleJet_80_30_Mass_Min420_DoubleMu0_SQ;
   // Bool_t          L1_DoubleJet_80_30_Mass_Min420_IsoTau40_RmOvlp;
   // Bool_t          L1_DoubleJet_80_30_Mass_Min420_Mu8;
   // Bool_t          L1_DoubleJet_90_30_DoubleJet30_Mass_Min620;
   // Bool_t          L1_DoubleLLPJet40;
   // Bool_t          L1_DoubleLooseIsoEG22er2p1;
   // Bool_t          L1_DoubleLooseIsoEG24er2p1;
   // Bool_t          L1_DoubleMu0;
   // Bool_t          L1_DoubleMu0_Mass_Min1;
   // Bool_t          L1_DoubleMu0_OQ;
   // Bool_t          L1_DoubleMu0_SQ;
   // Bool_t          L1_DoubleMu0_SQ_OS;
   // Bool_t          L1_DoubleMu0_Upt15_Upt7;
   // Bool_t          L1_DoubleMu0_Upt5_Upt5;
   // Bool_t          L1_DoubleMu0_Upt6_IP_Min1_Upt4;
   // Bool_t          L1_DoubleMu0_dR_Max1p6_Jet90er2p5_dR_Max0p8;
   // Bool_t          L1_DoubleMu0er1p4_OQ_OS_dEta_Max1p6;
   // Bool_t          L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4;
   // Bool_t          L1_DoubleMu0er1p5_SQ;
   // Bool_t          L1_DoubleMu0er1p5_SQ_OS;
   // Bool_t          L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4;
   // Bool_t          L1_DoubleMu0er1p5_SQ_dR_Max1p4;
   // Bool_t          L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p5;
   // Bool_t          L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p6;
   // Bool_t          L1_DoubleMu0er2p0_SQ_OS_dR_Max1p4;
   // Bool_t          L1_DoubleMu0er2p0_SQ_dEta_Max1p5;
   // Bool_t          L1_DoubleMu0er2p0_SQ_dEta_Max1p6;
   // Bool_t          L1_DoubleMu0er2p0_SQ_dR_Max1p4;
   // Bool_t          L1_DoubleMu18er2p1_SQ;
   // Bool_t          L1_DoubleMu3_OS_er2p3_Mass_Max14_DoubleEG7p5_er2p1_Mass_Max20;
   // Bool_t          L1_DoubleMu3_SQ_ETMHF30_HTT60er;
   // Bool_t          L1_DoubleMu3_SQ_ETMHF30_Jet60er2p5_OR_DoubleJet40er2p5;
   // Bool_t          L1_DoubleMu3_SQ_ETMHF40_HTT60er;
   // Bool_t          L1_DoubleMu3_SQ_ETMHF40_Jet60er2p5_OR_DoubleJet40er2p5;
   // Bool_t          L1_DoubleMu3_SQ_ETMHF50_HTT60er;
   // Bool_t          L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5;
   // Bool_t          L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5_OR_DoubleJet40er2p5;
   // Bool_t          L1_DoubleMu3_SQ_ETMHF60_Jet60er2p5;
   // Bool_t          L1_DoubleMu3_SQ_HTT220er;
   // Bool_t          L1_DoubleMu3_SQ_HTT240er;
   // Bool_t          L1_DoubleMu3_SQ_HTT260er;
   // Bool_t          L1_DoubleMu3_dR_Max1p6_Jet90er2p5_dR_Max0p8;
   // Bool_t          L1_DoubleMu3er2p0_SQ_OS_dR_Max1p4;
   // Bool_t          L1_DoubleMu4_SQ_EG9er2p5;
   // Bool_t          L1_DoubleMu4_SQ_OS;
   // Bool_t          L1_DoubleMu4_SQ_OS_dR_Max1p2;
   // Bool_t          L1_DoubleMu4p5_SQ_OS;
   // Bool_t          L1_DoubleMu4p5_SQ_OS_dR_Max1p2;
   // Bool_t          L1_DoubleMu4p5er2p0_SQ_OS;
   // Bool_t          L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18;
   // Bool_t          L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7;
   // Bool_t          L1_DoubleMu5_OS_er2p3_Mass_8to14_DoubleEG3er2p1_Mass_Max20;
   // Bool_t          L1_DoubleMu5_SQ_EG9er2p5;
   // Bool_t          L1_DoubleMu8_SQ;
   // Bool_t          L1_DoubleMu9_SQ;
   // Bool_t          L1_DoubleMu_12_5;
   // Bool_t          L1_DoubleMu_15_5_SQ;
   // Bool_t          L1_DoubleMu_15_7;
   // Bool_t          L1_DoubleMu_15_7_Mass_Min1;
   // Bool_t          L1_DoubleMu_15_7_SQ;
   // Bool_t          L1_DoubleTau70er2p1;
   // Bool_t          L1_ETM120;
   // Bool_t          L1_ETM150;
   // Bool_t          L1_ETMHF100;
   // Bool_t          L1_ETMHF100_HTT60er;
   // Bool_t          L1_ETMHF110;
   // Bool_t          L1_ETMHF110_HTT60er;
   // Bool_t          L1_ETMHF110_HTT60er_NotSecondBunchInTrain;
   // Bool_t          L1_ETMHF120;
   // Bool_t          L1_ETMHF120_HTT60er;
   // Bool_t          L1_ETMHF120_NotSecondBunchInTrain;
   // Bool_t          L1_ETMHF130;
   // Bool_t          L1_ETMHF130_HTT60er;
   // Bool_t          L1_ETMHF140;
   // Bool_t          L1_ETMHF150;
   // Bool_t          L1_ETMHF70;
   // Bool_t          L1_ETMHF70_HTT60er;
   // Bool_t          L1_ETMHF80;
   // Bool_t          L1_ETMHF80_HTT60er;
   // Bool_t          L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p1;
   // Bool_t          L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p6;
   // Bool_t          L1_ETMHF90;
   // Bool_t          L1_ETMHF90_HTT60er;
   // Bool_t          L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p1;
   // Bool_t          L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p6;
   // Bool_t          L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p1;
   // Bool_t          L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p6;
   // Bool_t          L1_ETT1200;
   // Bool_t          L1_ETT1600;
   // Bool_t          L1_ETT2000;
   // Bool_t          L1_FirstBunchAfterTrain;
   // Bool_t          L1_FirstBunchBeforeTrain;
   // Bool_t          L1_FirstBunchInTrain;
   // Bool_t          L1_FirstCollisionInOrbit;
   // Bool_t          L1_FirstCollisionInTrain;
   // Bool_t          L1_HCAL_LaserMon_Trig;
   // Bool_t          L1_HCAL_LaserMon_Veto;
   // Bool_t          L1_HTT120_SingleLLPJet40;
   // Bool_t          L1_HTT120er;
   // Bool_t          L1_HTT160_SingleLLPJet50;
   // Bool_t          L1_HTT160er;
   // Bool_t          L1_HTT200_SingleLLPJet60;
   // Bool_t          L1_HTT200er;
   // Bool_t          L1_HTT240_SingleLLPJet70;
   // Bool_t          L1_HTT255er;
   // Bool_t          L1_HTT280er;
   // Bool_t          L1_HTT280er_QuadJet_70_55_40_35_er2p5;
   // Bool_t          L1_HTT320er;
   // Bool_t          L1_HTT320er_QuadJet_70_55_40_40_er2p5;
   // Bool_t          L1_HTT320er_QuadJet_80_60_er2p1_45_40_er2p3;
   // Bool_t          L1_HTT320er_QuadJet_80_60_er2p1_50_45_er2p3;
   // Bool_t          L1_HTT360er;
   // Bool_t          L1_HTT400er;
   // Bool_t          L1_HTT450er;
   // Bool_t          L1_IsoEG32er2p5_Mt40;
   // Bool_t          L1_IsoTau52er2p1_QuadJet36er2p5;
   // Bool_t          L1_IsolatedBunch;
   // Bool_t          L1_LastBunchInTrain;
   // Bool_t          L1_LastCollisionInTrain;
   // Bool_t          L1_LooseIsoEG22er2p1_IsoTau26er2p1_dR_Min0p3;
   // Bool_t          L1_LooseIsoEG22er2p1_Tau70er2p1_dR_Min0p3;
   // Bool_t          L1_LooseIsoEG24er2p1_HTT100er;
   // Bool_t          L1_LooseIsoEG24er2p1_IsoTau27er2p1_dR_Min0p3;
   // Bool_t          L1_LooseIsoEG26er2p1_HTT100er;
   // Bool_t          L1_LooseIsoEG26er2p1_Jet34er2p5_dR_Min0p3;
   // Bool_t          L1_LooseIsoEG28er2p1_HTT100er;
   // Bool_t          L1_LooseIsoEG28er2p1_Jet34er2p5_dR_Min0p3;
   // Bool_t          L1_LooseIsoEG30er2p1_HTT100er;
   // Bool_t          L1_LooseIsoEG30er2p1_Jet34er2p5_dR_Min0p3;
   // Bool_t          L1_MinimumBiasHF0;
   // Bool_t          L1_MinimumBiasHF0_AND_BptxAND;
   // Bool_t          L1_Mu10er2p3_Jet32er2p3_dR_Max0p4_DoubleJet32er2p3_dEta_Max1p6;
   // Bool_t          L1_Mu12er2p3_Jet40er2p1_dR_Max0p4_DoubleJet40er2p1_dEta_Max1p6;
   // Bool_t          L1_Mu12er2p3_Jet40er2p3_dR_Max0p4_DoubleJet40er2p3_dEta_Max1p6;
   // Bool_t          L1_Mu18er2p1_Tau24er2p1;
   // Bool_t          L1_Mu18er2p1_Tau26er2p1;
   // Bool_t          L1_Mu18er2p1_Tau26er2p1_Jet55;
   // Bool_t          L1_Mu18er2p1_Tau26er2p1_Jet70;
   // Bool_t          L1_Mu20_EG10er2p5;
   // Bool_t          L1_Mu22er2p1_IsoTau28er2p1;
   // Bool_t          L1_Mu22er2p1_IsoTau30er2p1;
   // Bool_t          L1_Mu22er2p1_IsoTau32er2p1;
   // Bool_t          L1_Mu22er2p1_IsoTau34er2p1;
   // Bool_t          L1_Mu22er2p1_IsoTau36er2p1;
   // Bool_t          L1_Mu22er2p1_IsoTau40er2p1;
   // Bool_t          L1_Mu22er2p1_Tau70er2p1;
   // Bool_t          L1_Mu3_Jet120er2p5_dR_Max0p4;
   // Bool_t          L1_Mu3_Jet120er2p5_dR_Max0p8;
   // Bool_t          L1_Mu3_Jet16er2p5_dR_Max0p4;
   // Bool_t          L1_Mu3_Jet30er2p5;
   // Bool_t          L1_Mu3_Jet35er2p5_dR_Max0p4;
   // Bool_t          L1_Mu3_Jet60er2p5_dR_Max0p4;
   // Bool_t          L1_Mu3_Jet80er2p5_dR_Max0p4;
   // Bool_t          L1_Mu3er1p5_Jet100er2p5_ETMHF30;
   // Bool_t          L1_Mu3er1p5_Jet100er2p5_ETMHF40;
   // Bool_t          L1_Mu3er1p5_Jet100er2p5_ETMHF50;
   // Bool_t          L1_Mu5_EG23er2p5;
   // Bool_t          L1_Mu5_LooseIsoEG20er2p5;
   // Bool_t          L1_Mu6_DoubleEG10er2p5;
   // Bool_t          L1_Mu6_DoubleEG12er2p5;
   // Bool_t          L1_Mu6_DoubleEG15er2p5;
   // Bool_t          L1_Mu6_DoubleEG17er2p5;
   // Bool_t          L1_Mu6_HTT240er;
   // Bool_t          L1_Mu6_HTT250er;
   // Bool_t          L1_Mu7_EG20er2p5;
   // Bool_t          L1_Mu7_EG23er2p5;
   // Bool_t          L1_Mu7_LooseIsoEG20er2p5;
   // Bool_t          L1_Mu7_LooseIsoEG23er2p5;
   // Bool_t          L1_NotBptxOR;
   // Bool_t          L1_QuadJet60er2p5;
   // Bool_t          L1_QuadJet_95_75_65_20_DoubleJet_75_65_er2p5_Jet20_FWD3p0;
   // Bool_t          L1_QuadMu0;
   // Bool_t          L1_QuadMu0_OQ;
   // Bool_t          L1_QuadMu0_SQ;
   // Bool_t          L1_SecondBunchInTrain;
   // Bool_t          L1_SecondLastBunchInTrain;
   // Bool_t          L1_SingleEG10er2p5;
   // Bool_t          L1_SingleEG15er2p5;
   // Bool_t          L1_SingleEG26er2p5;
   // Bool_t          L1_SingleEG28_FWD2p5;
   // Bool_t          L1_SingleEG28er1p5;
   // Bool_t          L1_SingleEG28er2p1;
   // Bool_t          L1_SingleEG28er2p5;
   // Bool_t          L1_SingleEG34er2p5;
   // Bool_t          L1_SingleEG36er2p5;
   // Bool_t          L1_SingleEG38er2p5;
   // Bool_t          L1_SingleEG40er2p5;
   // Bool_t          L1_SingleEG42er2p5;
   // Bool_t          L1_SingleEG45er2p5;
   // Bool_t          L1_SingleEG50;
   // Bool_t          L1_SingleEG60;
   // Bool_t          L1_SingleEG8er2p5;
   // Bool_t          L1_SingleIsoEG24er1p5;
   // Bool_t          L1_SingleIsoEG24er2p1;
   // Bool_t          L1_SingleIsoEG26er1p5;
   // Bool_t          L1_SingleIsoEG26er2p1;
   // Bool_t          L1_SingleIsoEG26er2p5;
   // Bool_t          L1_SingleIsoEG28_FWD2p5;
   // Bool_t          L1_SingleIsoEG28er1p5;
   // Bool_t          L1_SingleIsoEG28er2p1;
   // Bool_t          L1_SingleIsoEG28er2p5;
   // Bool_t          L1_SingleIsoEG30er2p1;
   // Bool_t          L1_SingleIsoEG30er2p5;
   // Bool_t          L1_SingleIsoEG32er2p1;
   // Bool_t          L1_SingleIsoEG32er2p5;
   // Bool_t          L1_SingleIsoEG34er2p5;
   // Bool_t          L1_SingleIsoTau32er2p1;
   // Bool_t          L1_SingleJet10erHE;
   // Bool_t          L1_SingleJet120;
   // Bool_t          L1_SingleJet120_FWD3p0;
   // Bool_t          L1_SingleJet120er2p5;
   // Bool_t          L1_SingleJet12erHE;
   // Bool_t          L1_SingleJet140er2p5;
   // Bool_t          L1_SingleJet140er2p5_ETMHF70;
   // Bool_t          L1_SingleJet140er2p5_ETMHF80;
   // Bool_t          L1_SingleJet140er2p5_ETMHF90;
   // Bool_t          L1_SingleJet160er2p5;
   // Bool_t          L1_SingleJet180;
   // Bool_t          L1_SingleJet180er2p5;
   // Bool_t          L1_SingleJet200;
   // Bool_t          L1_SingleJet20er2p5_NotBptxOR;
   // Bool_t          L1_SingleJet20er2p5_NotBptxOR_3BX;
   // Bool_t          L1_SingleJet35;
   // Bool_t          L1_SingleJet35_FWD3p0;
   // Bool_t          L1_SingleJet35er2p5;
   // Bool_t          L1_SingleJet43er2p5_NotBptxOR_3BX;
   // Bool_t          L1_SingleJet46er2p5_NotBptxOR_3BX;
   // Bool_t          L1_SingleJet60;
   // Bool_t          L1_SingleJet60_FWD3p0;
   // Bool_t          L1_SingleJet60er2p5;
   // Bool_t          L1_SingleJet8erHE;
   // Bool_t          L1_SingleJet90;
   // Bool_t          L1_SingleJet90_FWD3p0;
   // Bool_t          L1_SingleJet90er2p5;
   // Bool_t          L1_SingleLooseIsoEG26er1p5;
   // Bool_t          L1_SingleLooseIsoEG26er2p5;
   // Bool_t          L1_SingleLooseIsoEG28_FWD2p5;
   // Bool_t          L1_SingleLooseIsoEG28er1p5;
   // Bool_t          L1_SingleLooseIsoEG28er2p1;
   // Bool_t          L1_SingleLooseIsoEG28er2p5;
   // Bool_t          L1_SingleLooseIsoEG30er1p5;
   // Bool_t          L1_SingleLooseIsoEG30er2p5;
   // Bool_t          L1_SingleMu0_BMTF;
   // Bool_t          L1_SingleMu0_DQ;
   // Bool_t          L1_SingleMu0_EMTF;
   // Bool_t          L1_SingleMu0_OMTF;
   // Bool_t          L1_SingleMu10er1p5;
   // Bool_t          L1_SingleMu12_DQ_BMTF;
   // Bool_t          L1_SingleMu12_DQ_EMTF;
   // Bool_t          L1_SingleMu12_DQ_OMTF;
   // Bool_t          L1_SingleMu12er1p5;
   // Bool_t          L1_SingleMu14er1p5;
   // Bool_t          L1_SingleMu15_DQ;
   // Bool_t          L1_SingleMu16er1p5;
   // Bool_t          L1_SingleMu18;
   // Bool_t          L1_SingleMu18er1p5;
   // Bool_t          L1_SingleMu20;
   // Bool_t          L1_SingleMu22;
   // Bool_t          L1_SingleMu22_BMTF;
   // Bool_t          L1_SingleMu22_DQ;
   // Bool_t          L1_SingleMu22_EMTF;
   // Bool_t          L1_SingleMu22_OMTF;
   // Bool_t          L1_SingleMu22_OQ;
   // Bool_t          L1_SingleMu25;
   // Bool_t          L1_SingleMu3;
   // Bool_t          L1_SingleMu5;
   // Bool_t          L1_SingleMu6er1p5;
   // Bool_t          L1_SingleMu7;
   // Bool_t          L1_SingleMu7_DQ;
   // Bool_t          L1_SingleMu7er1p5;
   // Bool_t          L1_SingleMu8er1p5;
   // Bool_t          L1_SingleMu9er1p5;
   // Bool_t          L1_SingleMuCosmics;
   // Bool_t          L1_SingleMuCosmics_BMTF;
   // Bool_t          L1_SingleMuCosmics_EMTF;
   // Bool_t          L1_SingleMuCosmics_OMTF;
   // Bool_t          L1_SingleMuOpen;
   // Bool_t          L1_SingleMuOpen_NotBptxOR;
   // Bool_t          L1_SingleMuOpen_er1p1_NotBptxOR_3BX;
   // Bool_t          L1_SingleMuOpen_er1p4_NotBptxOR_3BX;
   // Bool_t          L1_SingleMuShower_Nominal;
   // Bool_t          L1_SingleMuShower_Tight;
   // Bool_t          L1_SingleTau120er2p1;
   // Bool_t          L1_SingleTau130er2p1;
   // Bool_t          L1_SingleTau70er2p1;
   // Bool_t          L1_TOTEM_1;
   // Bool_t          L1_TOTEM_2;
   // Bool_t          L1_TOTEM_3;
   // Bool_t          L1_TOTEM_4;
   // Bool_t          L1_TripleEG16er2p5;
   // Bool_t          L1_TripleEG_16_12_8_er2p5;
   // Bool_t          L1_TripleEG_16_15_8_er2p5;
   // Bool_t          L1_TripleEG_18_17_8_er2p5;
   // Bool_t          L1_TripleEG_18_18_12_er2p5;
   // Bool_t          L1_TripleJet_100_80_70_DoubleJet_80_70_er2p5;
   // Bool_t          L1_TripleJet_105_85_75_DoubleJet_85_75_er2p5;
   // Bool_t          L1_TripleJet_95_75_65_DoubleJet_75_65_er2p5;
   // Bool_t          L1_TripleMu0;
   // Bool_t          L1_TripleMu0_OQ;
   // Bool_t          L1_TripleMu0_SQ;
   // Bool_t          L1_TripleMu3;
   // Bool_t          L1_TripleMu3_SQ;
   // Bool_t          L1_TripleMu_2SQ_1p5SQ_0OQ;
   // Bool_t          L1_TripleMu_2SQ_1p5SQ_0OQ_Mass_Max12;
   // Bool_t          L1_TripleMu_3SQ_2p5SQ_0OQ_Mass_Max12;
   // Bool_t          L1_TripleMu_5SQ_3SQ_0OQ;
   // Bool_t          L1_TripleMu_5SQ_3SQ_0OQ_DoubleMu_5_3_SQ_OS_Mass_Max9;
   // Bool_t          L1_TripleMu_5SQ_3SQ_0_DoubleMu_5_3_SQ_OS_Mass_Max9;
   // Bool_t          L1_TripleMu_5_3_3;
   // Bool_t          L1_TripleMu_5_3_3_SQ;
   // Bool_t          L1_TripleMu_5_3p5_2p5;
   // Bool_t          L1_TripleMu_5_3p5_2p5_DoubleMu_5_2p5_OS_Mass_5to17;
   // Bool_t          L1_TripleMu_5_3p5_2p5_OQ_DoubleMu_5_2p5_OQ_OS_Mass_5to17;
   // Bool_t          L1_TripleMu_5_4_2p5_DoubleMu_5_2p5_OS_Mass_5to17;
   // Bool_t          L1_TripleMu_5_5_3;
   // Bool_t          L1_UnpairedBunchBptxMinus;
   // Bool_t          L1_UnpairedBunchBptxPlus;
   // Bool_t          L1_ZeroBias;
   // Bool_t          L1_ZeroBias_copy;
   // Bool_t          L1_UnprefireableEvent;
   Bool_t          Flag_HBHENoiseFilter;
   Bool_t          Flag_HBHENoiseIsoFilter;
   Bool_t          Flag_CSCTightHaloFilter;
   Bool_t          Flag_CSCTightHaloTrkMuUnvetoFilter;
   Bool_t          Flag_CSCTightHalo2015Filter;
   Bool_t          Flag_globalTightHalo2016Filter;
   Bool_t          Flag_globalSuperTightHalo2016Filter;
   Bool_t          Flag_HcalStripHaloFilter;
   Bool_t          Flag_hcalLaserEventFilter;
   Bool_t          Flag_EcalDeadCellTriggerPrimitiveFilter;
   Bool_t          Flag_EcalDeadCellBoundaryEnergyFilter;
   Bool_t          Flag_ecalBadCalibFilter;
   Bool_t          Flag_goodVertices;
   Bool_t          Flag_eeBadScFilter;
   Bool_t          Flag_ecalLaserCorrFilter;
   Bool_t          Flag_trkPOGFilters;
   Bool_t          Flag_chargedHadronTrackResolutionFilter;
   Bool_t          Flag_muonBadTrackFilter;
   Bool_t          Flag_BadChargedCandidateFilter;
   Bool_t          Flag_BadPFMuonFilter;
   Bool_t          Flag_BadPFMuonDzFilter;
   Bool_t          Flag_hfNoisyHitsFilter;
   Bool_t          Flag_BadChargedCandidateSummer16Filter;
   Bool_t          Flag_BadPFMuonSummer16Filter;
   Bool_t          Flag_trkPOG_manystripclus53X;
   Bool_t          Flag_trkPOG_toomanystripclus53X;
   Bool_t          Flag_trkPOG_logErrorTooManyClusters;
   //Bool_t          Flag_METFilters;
   Bool_t          L1Reco_step;
   Bool_t          L1simulation_step;
   Bool_t          HLTriggerFirstPath;
   // Bool_t          HLT_AK8PFJet360_TrimMass30;
   // Bool_t          HLT_AK8PFJet380_TrimMass30;
   // Bool_t          HLT_AK8PFJet400_TrimMass30;
   // Bool_t          HLT_AK8PFJet420_TrimMass30;
   // Bool_t          HLT_AK8PFJet400_MassSD30;
   // Bool_t          HLT_AK8PFJet420_MassSD30;
   // Bool_t          HLT_AK8PFJet450_MassSD30;
   // Bool_t          HLT_AK8DiPFJet250_250_MassSD30;
   // Bool_t          HLT_AK8DiPFJet250_250_MassSD50;
   // Bool_t          HLT_AK8DiPFJet260_260_MassSD30;
   // Bool_t          HLT_AK8DiPFJet270_270_MassSD30;
   // Bool_t          HLT_AK8PFHT750_TrimMass50;
   // Bool_t          HLT_AK8PFHT800_TrimMass50;
   // Bool_t          HLT_AK8PFHT850_TrimMass50;
   // Bool_t          HLT_AK8PFHT900_TrimMass50;
   // Bool_t          HLT_CaloJet500_NoJetID;
   // Bool_t          HLT_CaloJet550_NoJetID;
   // Bool_t          HLT_DoubleMu5_Upsilon_DoubleEle3_CaloIdL_TrackIdL;
   // Bool_t          HLT_DoubleMu3_DoubleEle7p5_CaloIdL_TrackIdL_Upsilon;
   // Bool_t          HLT_Trimuon5_3p5_2_Upsilon_Muon;
   // Bool_t          HLT_TrimuonOpen_5_3p5_2_Upsilon_Muon;
   // Bool_t          HLT_DoubleEle25_CaloIdL_MW;
   // Bool_t          HLT_DoubleEle27_CaloIdL_MW;
   // Bool_t          HLT_DoubleEle33_CaloIdL_MW;
   // Bool_t          HLT_DoubleEle24_eta2p1_WPTight_Gsf;
   // Bool_t          HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_DZ_PFHT350;
   // Bool_t          HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_PFHT350;
   // Bool_t          HLT_Ele27_Ele37_CaloIdL_MW;
   // Bool_t          HLT_Mu27_Ele37_CaloIdL_MW;
   // Bool_t          HLT_Mu37_Ele27_CaloIdL_MW;
   // Bool_t          HLT_Mu37_TkMu27;
   // Bool_t          HLT_DoubleMu4_3_Bs;
   // Bool_t          HLT_DoubleMu4_3_Jpsi;
   // Bool_t          HLT_DoubleMu4_3_LowMass;
   // Bool_t          HLT_DoubleMu4_LowMass_Displaced;
   // Bool_t          HLT_Mu0_L1DoubleMu;
   // Bool_t          HLT_Mu4_L1DoubleMu;
   // Bool_t          HLT_DoubleMu4_3_Photon4_BsToMMG;
   // Bool_t          HLT_DoubleMu4_3_Displaced_Photon4_BsToMMG;
   // Bool_t          HLT_DoubleMu3_Trk_Tau3mu;
   // Bool_t          HLT_DoubleMu3_TkMu_DsTau3Mu;
   // Bool_t          HLT_DoubleMu4_Mass3p8_DZ_PFHT350;
   // Bool_t          HLT_DoubleMu4_MuMuTrk_Displaced;
   // Bool_t          HLT_Mu3_PFJet40;
   // Bool_t          HLT_Mu7p5_L2Mu2_Jpsi;
   // Bool_t          HLT_Mu7p5_L2Mu2_Upsilon;
   // Bool_t          HLT_Mu3_L1SingleMu5orSingleMu7;
   // Bool_t          HLT_DoublePhoton33_CaloIdL;
   // Bool_t          HLT_DoublePhoton70;
   // Bool_t          HLT_DoublePhoton85;
   // Bool_t          HLT_Ele20_WPTight_Gsf;
   // Bool_t          HLT_Ele15_WPLoose_Gsf;
   // Bool_t          HLT_Ele17_WPLoose_Gsf;
   // Bool_t          HLT_Ele20_WPLoose_Gsf;
   // Bool_t          HLT_Ele20_eta2p1_WPLoose_Gsf;
   // Bool_t          HLT_DiEle27_WPTightCaloOnly_L1DoubleEG;
   // Bool_t          HLT_Ele27_WPTight_Gsf;
   // Bool_t          HLT_Ele28_WPTight_Gsf;
   // Bool_t          HLT_Ele30_WPTight_Gsf;
   // Bool_t          HLT_Ele32_WPTight_Gsf;
   // Bool_t          HLT_Ele35_WPTight_Gsf;
   // Bool_t          HLT_Ele35_WPTight_Gsf_L1EGMT;
   // Bool_t          HLT_Ele38_WPTight_Gsf;
   // Bool_t          HLT_Ele40_WPTight_Gsf;
   // Bool_t          HLT_Ele32_WPTight_Gsf_L1DoubleEG;
   // Bool_t          HLT_Ele24_eta2p1_WPTight_Gsf_TightChargedIsoPFTauHPS30_eta2p1_CrossL1;
   // Bool_t          HLT_HT450_Beamspot;
   // Bool_t          HLT_HT300_Beamspot;
   // Bool_t          HLT_ZeroBias_Beamspot;
   // Bool_t          HLT_IsoMu20_eta2p1_TightChargedIsoPFTauHPS27_eta2p1_CrossL1;
   // Bool_t          HLT_IsoMu20_eta2p1_TightChargedIsoPFTauHPS27_eta2p1_TightID_CrossL1;
   // Bool_t          HLT_IsoMu27_LooseChargedIsoPFTau20_Trk1_eta2p1_SingleL1;
   // Bool_t          HLT_IsoMu27_LooseChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1;
   // Bool_t          HLT_IsoMu27_MediumChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1;
   // Bool_t          HLT_IsoMu27_TightChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1;
   // Bool_t          HLT_IsoMu20;
   Bool_t          HLT_IsoMu24;
   // Bool_t          HLT_IsoMu24_eta2p1;
   // Bool_t          HLT_IsoMu27;
   // Bool_t          HLT_IsoMu30;
   // Bool_t          HLT_UncorrectedJetE30_NoBPTX;
   // Bool_t          HLT_UncorrectedJetE30_NoBPTX3BX;
   // Bool_t          HLT_UncorrectedJetE60_NoBPTX3BX;
   // Bool_t          HLT_UncorrectedJetE70_NoBPTX3BX;
   // Bool_t          HLT_L1SingleMu18;
   // Bool_t          HLT_L1SingleMu25;
   // Bool_t          HLT_L1SingleMuCosmics;
   // Bool_t          HLT_L2Mu10;
   // Bool_t          HLT_L2Mu10_NoVertex_NoBPTX3BX;
   // Bool_t          HLT_L2Mu10_NoVertex_NoBPTX;
   // Bool_t          HLT_L2Mu45_NoVertex_3Sta_NoBPTX3BX;
   // Bool_t          HLT_L2Mu40_NoVertex_3Sta_NoBPTX3BX;
   // Bool_t          HLT_L2Mu50;
   // Bool_t          HLT_L2Mu23NoVtx_2Cha;
   // Bool_t          HLT_L2Mu23NoVtx_2Cha_CosmicSeed;
   // Bool_t          HLT_DoubleL2Mu30NoVtx_2Cha_CosmicSeed_Eta2p4;
   // Bool_t          HLT_DoubleL2Mu30NoVtx_2Cha_Eta2p4;
   // Bool_t          HLT_DoubleL2Mu50;
   // Bool_t          HLT_DoubleL2Mu23NoVtx_2Cha_CosmicSeed;
   // Bool_t          HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed;
   // Bool_t          HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed_Eta2p4;
   // Bool_t          HLT_DoubleL2Mu23NoVtx_2Cha;
   // Bool_t          HLT_DoubleL2Mu25NoVtx_2Cha;
   // Bool_t          HLT_DoubleL2Mu25NoVtx_2Cha_Eta2p4;
   // Bool_t          HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL;
   // Bool_t          HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL;
   // Bool_t          HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ;
   // Bool_t          HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ;
   // Bool_t          HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8;
   // Bool_t          HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass8;
   // Bool_t          HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8;
   // Bool_t          HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass3p8;
   // Bool_t          HLT_Mu25_TkMu0_Onia;
   // Bool_t          HLT_Mu30_TkMu0_Psi;
   // Bool_t          HLT_Mu30_TkMu0_Upsilon;
   // Bool_t          HLT_Mu20_TkMu0_Phi;
   // Bool_t          HLT_Mu25_TkMu0_Phi;
   // Bool_t          HLT_Mu12;
   // Bool_t          HLT_Mu15;
   // Bool_t          HLT_Mu20;
   // Bool_t          HLT_Mu27;
   // Bool_t          HLT_Mu50;
   // Bool_t          HLT_Mu55;
   // Bool_t          HLT_CascadeMu100;
   // Bool_t          HLT_HighPtTkMu100;
   // Bool_t          HLT_DiPFJet15_NoCaloMatched;
   // Bool_t          HLT_DiPFJet25_NoCaloMatched;
   // Bool_t          HLT_DiPFJet15_FBEta3_NoCaloMatched;
   // Bool_t          HLT_DiPFJet25_FBEta3_NoCaloMatched;
   // Bool_t          HLT_DiPFJetAve40;
   // Bool_t          HLT_DiPFJetAve60;
   // Bool_t          HLT_DiPFJetAve80;
   // Bool_t          HLT_DiPFJetAve140;
   // Bool_t          HLT_DiPFJetAve200;
   // Bool_t          HLT_DiPFJetAve260;
   // Bool_t          HLT_DiPFJetAve320;
   // Bool_t          HLT_DiPFJetAve400;
   // Bool_t          HLT_DiPFJetAve500;
   // Bool_t          HLT_DiPFJetAve15_HFJEC;
   // Bool_t          HLT_DiPFJetAve25_HFJEC;
   // Bool_t          HLT_DiPFJetAve35_HFJEC;
   // Bool_t          HLT_DiPFJetAve60_HFJEC;
   // Bool_t          HLT_DiPFJetAve80_HFJEC;
   // Bool_t          HLT_DiPFJetAve100_HFJEC;
   // Bool_t          HLT_DiPFJetAve160_HFJEC;
   // Bool_t          HLT_DiPFJetAve220_HFJEC;
   // Bool_t          HLT_DiPFJetAve300_HFJEC;
   // Bool_t          HLT_AK8PFJet15;
   // Bool_t          HLT_AK8PFJet25;
   // Bool_t          HLT_AK8PFJet40;
   // Bool_t          HLT_AK8PFJet60;
   // Bool_t          HLT_AK8PFJet80;
   // Bool_t          HLT_AK8PFJet140;
   // Bool_t          HLT_AK8PFJet200;
   // Bool_t          HLT_AK8PFJet260;
   // Bool_t          HLT_AK8PFJet320;
   // Bool_t          HLT_AK8PFJet400;
   // Bool_t          HLT_AK8PFJet450;
   // Bool_t          HLT_AK8PFJet500;
   // Bool_t          HLT_AK8PFJet550;
   // Bool_t          HLT_PFJet15;
   // Bool_t          HLT_PFJet25;
   // Bool_t          HLT_PFJet40;
   // Bool_t          HLT_PFJet60;
   // Bool_t          HLT_PFJet80;
   // Bool_t          HLT_PFJet140;
   // Bool_t          HLT_PFJet200;
   // Bool_t          HLT_PFJet260;
   // Bool_t          HLT_PFJet320;
   // Bool_t          HLT_PFJet400;
   // Bool_t          HLT_PFJet450;
   // Bool_t          HLT_PFJet500;
   // Bool_t          HLT_PFJet550;
   // Bool_t          HLT_PFJetFwd15;
   // Bool_t          HLT_PFJetFwd25;
   // Bool_t          HLT_PFJetFwd40;
   // Bool_t          HLT_PFJetFwd60;
   // Bool_t          HLT_PFJetFwd80;
   // Bool_t          HLT_PFJetFwd140;
   // Bool_t          HLT_PFJetFwd200;
   // Bool_t          HLT_PFJetFwd260;
   // Bool_t          HLT_PFJetFwd320;
   // Bool_t          HLT_PFJetFwd400;
   // Bool_t          HLT_PFJetFwd450;
   // Bool_t          HLT_PFJetFwd500;
   // Bool_t          HLT_AK8PFJetFwd15;
   // Bool_t          HLT_AK8PFJetFwd25;
   // Bool_t          HLT_AK8PFJetFwd40;
   // Bool_t          HLT_AK8PFJetFwd60;
   // Bool_t          HLT_AK8PFJetFwd80;
   // Bool_t          HLT_AK8PFJetFwd140;
   // Bool_t          HLT_AK8PFJetFwd200;
   // Bool_t          HLT_AK8PFJetFwd260;
   // Bool_t          HLT_AK8PFJetFwd320;
   // Bool_t          HLT_AK8PFJetFwd400;
   // Bool_t          HLT_AK8PFJetFwd450;
   // Bool_t          HLT_AK8PFJetFwd500;
   // Bool_t          HLT_PFHT180;
   // Bool_t          HLT_PFHT250;
   // Bool_t          HLT_PFHT370;
   // Bool_t          HLT_PFHT430;
   // Bool_t          HLT_PFHT510;
   // Bool_t          HLT_PFHT590;
   // Bool_t          HLT_PFHT680;
   // Bool_t          HLT_PFHT780;
   // Bool_t          HLT_PFHT890;
   // Bool_t          HLT_PFHT1050;
   // Bool_t          HLT_PFHT500_PFMET100_PFMHT100_IDTight;
   // Bool_t          HLT_PFHT500_PFMET110_PFMHT110_IDTight;
   // Bool_t          HLT_PFHT700_PFMET85_PFMHT85_IDTight;
   // Bool_t          HLT_PFHT700_PFMET95_PFMHT95_IDTight;
   // Bool_t          HLT_PFHT800_PFMET75_PFMHT75_IDTight;
   // Bool_t          HLT_PFHT800_PFMET85_PFMHT85_IDTight;
   // Bool_t          HLT_PFMET110_PFMHT110_IDTight;
   // Bool_t          HLT_PFMET120_PFMHT120_IDTight;
   // Bool_t          HLT_PFMET130_PFMHT130_IDTight;
   // Bool_t          HLT_PFMET140_PFMHT140_IDTight;
   // Bool_t          HLT_PFMET100_PFMHT100_IDTight_CaloBTagDeepCSV_3p1;
   // Bool_t          HLT_PFMET110_PFMHT110_IDTight_CaloBTagDeepCSV_3p1;
   // Bool_t          HLT_PFMET120_PFMHT120_IDTight_CaloBTagDeepCSV_3p1;
   // Bool_t          HLT_PFMET130_PFMHT130_IDTight_CaloBTagDeepCSV_3p1;
   // Bool_t          HLT_PFMET140_PFMHT140_IDTight_CaloBTagDeepCSV_3p1;
   // Bool_t          HLT_PFMET120_PFMHT120_IDTight_PFHT60;
   // Bool_t          HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60;
   // Bool_t          HLT_PFMETTypeOne120_PFMHT120_IDTight_PFHT60;
   // Bool_t          HLT_PFMETTypeOne110_PFMHT110_IDTight;
   // Bool_t          HLT_PFMETTypeOne120_PFMHT120_IDTight;
   // Bool_t          HLT_PFMETTypeOne130_PFMHT130_IDTight;
   // Bool_t          HLT_PFMETTypeOne140_PFMHT140_IDTight;
   // Bool_t          HLT_PFMETNoMu110_PFMHTNoMu110_IDTight;
   // Bool_t          HLT_PFMETNoMu120_PFMHTNoMu120_IDTight;
   // Bool_t          HLT_PFMETNoMu130_PFMHTNoMu130_IDTight;
   // Bool_t          HLT_PFMETNoMu140_PFMHTNoMu140_IDTight;
   // Bool_t          HLT_PFMETNoMu110_PFMHTNoMu110_IDTight_FilterHF;
   // Bool_t          HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_FilterHF;
   // Bool_t          HLT_PFMETNoMu130_PFMHTNoMu130_IDTight_FilterHF;
   // Bool_t          HLT_PFMETNoMu140_PFMHTNoMu140_IDTight_FilterHF;
   // Bool_t          HLT_MonoCentralPFJet80_PFMETNoMu110_PFMHTNoMu110_IDTight;
   // Bool_t          HLT_MonoCentralPFJet80_PFMETNoMu120_PFMHTNoMu120_IDTight;
   // Bool_t          HLT_MonoCentralPFJet80_PFMETNoMu130_PFMHTNoMu130_IDTight;
   // Bool_t          HLT_MonoCentralPFJet80_PFMETNoMu140_PFMHTNoMu140_IDTight;
   // Bool_t          HLT_L1ETMHadSeeds;
   // Bool_t          HLT_CaloMHT90;
   // Bool_t          HLT_CaloMET80_NotCleaned;
   // Bool_t          HLT_CaloMET90_NotCleaned;
   // Bool_t          HLT_CaloMET100_NotCleaned;
   // Bool_t          HLT_CaloMET110_NotCleaned;
   // Bool_t          HLT_CaloMET250_NotCleaned;
   // Bool_t          HLT_CaloMET300_NotCleaned;
   // Bool_t          HLT_CaloMET350_NotCleaned;
   // Bool_t          HLT_PFMET200_NotCleaned;
   // Bool_t          HLT_PFMET250_NotCleaned;
   // Bool_t          HLT_PFMET300_NotCleaned;
   // Bool_t          HLT_PFMET200_BeamHaloCleaned;
   // Bool_t          HLT_PFMETTypeOne200_BeamHaloCleaned;
   // Bool_t          HLT_MET105_IsoTrk50;
   // Bool_t          HLT_MET120_IsoTrk50;
   // Bool_t          HLT_SingleJet30_Mu12_SinglePFJet40;
   // Bool_t          HLT_Mu12eta2p3;
   // Bool_t          HLT_Mu12eta2p3_PFJet40;
   // Bool_t          HLT_Mu12_DoublePFJets40_PFBTagDeepCSV_p71;
   // Bool_t          HLT_Mu12_DoublePFJets100_PFBTagDeepCSV_p71;
   // Bool_t          HLT_Mu12_DoublePFJets200_PFBTagDeepCSV_p71;
   // Bool_t          HLT_Mu12_DoublePFJets350_PFBTagDeepCSV_p71;
   // Bool_t          HLT_Mu12_DoublePFJets40MaxDeta1p6_DoublePFBTagDeepCSV_p71;
   // Bool_t          HLT_Mu12_DoublePFJets54MaxDeta1p6_DoublePFBTagDeepCSV_p71;
   // Bool_t          HLT_DoublePFJets40_PFBTagDeepCSV_p71;
   // Bool_t          HLT_DoublePFJets100_PFBTagDeepCSV_p71;
   // Bool_t          HLT_DoublePFJets200_PFBTagDeepCSV_p71;
   // Bool_t          HLT_DoublePFJets350_PFBTagDeepCSV_p71;
   // Bool_t          HLT_DoublePFJets116MaxDeta1p6_DoublePFBTagDeepCSV_p71;
   // Bool_t          HLT_DoublePFJets128MaxDeta1p6_DoublePFBTagDeepCSV_p71;
   // Bool_t          HLT_Mu12_DoublePFJets40_PFBTagDeepJet_p71;
   // Bool_t          HLT_Mu12_DoublePFJets100_PFBTagDeepJet_p71;
   // Bool_t          HLT_Mu12_DoublePFJets200_PFBTagDeepJet_p71;
   // Bool_t          HLT_Mu12_DoublePFJets350_PFBTagDeepJet_p71;
   // Bool_t          HLT_Mu12_DoublePFJets40MaxDeta1p6_DoublePFBTagDeepJet_p71;
   // Bool_t          HLT_Mu12_DoublePFJets54MaxDeta1p6_DoublePFBTagDeepJet_p71;
   // Bool_t          HLT_DoublePFJets40_PFBTagDeepJet_p71;
   // Bool_t          HLT_DoublePFJets100_PFBTagDeepJet_p71;
   // Bool_t          HLT_DoublePFJets200_PFBTagDeepJet_p71;
   // Bool_t          HLT_DoublePFJets350_PFBTagDeepJet_p71;
   // Bool_t          HLT_DoublePFJets116MaxDeta1p6_DoublePFBTagDeepJet_p71;
   // Bool_t          HLT_DoublePFJets128MaxDeta1p6_DoublePFBTagDeepJet_p71;
   // Bool_t          HLT_Photon300_NoHE;
   // Bool_t          HLT_Mu8_TrkIsoVVL;
   // Bool_t          HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ;
   // Bool_t          HLT_Mu8_DiEle12_CaloIdL_TrackIdL;
   // Bool_t          HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350_DZ;
   // Bool_t          HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350;
   // Bool_t          HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ;
   // Bool_t          HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30;
   // Bool_t          HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_CaloDiJet30;
   // Bool_t          HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30_PFBtagDeepCSV_1p5;
   // Bool_t          HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_CaloDiJet30_CaloBtagDeepCSV_1p5;
   // Bool_t          HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL;
   // Bool_t          HLT_Mu17_TrkIsoVVL;
   // Bool_t          HLT_Mu19_TrkIsoVVL;
   // Bool_t          HLT_BTagMu_AK4DiJet20_Mu5;
   // Bool_t          HLT_BTagMu_AK4DiJet40_Mu5;
   // Bool_t          HLT_BTagMu_AK4DiJet70_Mu5;
   // Bool_t          HLT_BTagMu_AK4DiJet110_Mu5;
   // Bool_t          HLT_BTagMu_AK4DiJet170_Mu5;
   // Bool_t          HLT_BTagMu_AK4Jet300_Mu5;
   // Bool_t          HLT_BTagMu_AK8DiJet170_Mu5;
   // Bool_t          HLT_BTagMu_AK8Jet170_DoubleMu5;
   // Bool_t          HLT_BTagMu_AK8Jet300_Mu5;
   // Bool_t          HLT_Ele15_Ele8_CaloIdL_TrackIdL_IsoVL;
   // Bool_t          HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ;
   // Bool_t          HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL;
   // Bool_t          HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ;
   // Bool_t          HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL;
   // Bool_t          HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL;
   // Bool_t          HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ;
   // Bool_t          HLT_Mu12_DoublePhoton20;
   // Bool_t          HLT_Photon20;
   // Bool_t          HLT_Photon33;
   // Bool_t          HLT_Photon50;
   // Bool_t          HLT_Photon75;
   // Bool_t          HLT_Photon90;
   // Bool_t          HLT_Photon120;
   // Bool_t          HLT_Photon150;
   // Bool_t          HLT_Photon175;
   // Bool_t          HLT_Photon200;
   // Bool_t          HLT_Photon30EB_TightID_TightIso;
   // Bool_t          HLT_Photon100EB_TightID_TightIso;
   // Bool_t          HLT_Photon110EB_TightID_TightIso;
   // Bool_t          HLT_Photon120EB_TightID_TightIso;
   // Bool_t          HLT_Photon100EBHE10;
   // Bool_t          HLT_Photon100EEHE10;
   // Bool_t          HLT_Photon100EE_TightID_TightIso;
   // Bool_t          HLT_Photon50_R9Id90_HE10_IsoM;
   // Bool_t          HLT_Photon75_R9Id90_HE10_IsoM;
   // Bool_t          HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ300_PFJetsMJJ400DEta3;
   // Bool_t          HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ400_PFJetsMJJ600DEta3;
   // Bool_t          HLT_Photon90_R9Id90_HE10_IsoM;
   // Bool_t          HLT_Photon120_R9Id90_HE10_IsoM;
   // Bool_t          HLT_Photon165_R9Id90_HE10_IsoM;
   // Bool_t          HLT_Photon90_CaloIdL_PFHT700;
   // Bool_t          HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90;
   // Bool_t          HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass95;
   // Bool_t          HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_Mass55;
   // Bool_t          HLT_Photon35_TwoProngs35;
   // Bool_t          HLT_IsoMu24_TwoProngs35;
   // Bool_t          HLT_Dimuon0_Jpsi_L1_NoOS;
   // Bool_t          HLT_Dimuon0_Jpsi_NoVertexing_NoOS;
   // Bool_t          HLT_Dimuon0_Jpsi;
   // Bool_t          HLT_Dimuon0_Jpsi_NoVertexing;
   // Bool_t          HLT_Dimuon0_Jpsi_L1_4R_0er1p5R;
   // Bool_t          HLT_Dimuon0_Jpsi_NoVertexing_L1_4R_0er1p5R;
   // Bool_t          HLT_Dimuon0_Jpsi3p5_Muon2;
   // Bool_t          HLT_Dimuon0_Upsilon_L1_4p5;
   // Bool_t          HLT_Dimuon0_Upsilon_L1_5;
   // Bool_t          HLT_Dimuon0_Upsilon_L1_4p5NoOS;
   // Bool_t          HLT_Dimuon0_Upsilon_L1_4p5er2p0;
   // Bool_t          HLT_Dimuon0_Upsilon_L1_4p5er2p0M;
   // Bool_t          HLT_Dimuon0_Upsilon_NoVertexing;
   // Bool_t          HLT_Dimuon0_Upsilon_L1_5M;
   // Bool_t          HLT_Dimuon0_LowMass_L1_0er1p5R;
   // Bool_t          HLT_Dimuon0_LowMass_L1_0er1p5;
   // Bool_t          HLT_Dimuon0_LowMass;
   // Bool_t          HLT_Dimuon0_LowMass_L1_4;
   // Bool_t          HLT_Dimuon0_LowMass_L1_4R;
   // Bool_t          HLT_Dimuon0_LowMass_L1_TM530;
   // Bool_t          HLT_Dimuon0_Upsilon_Muon_L1_TM0;
   // Bool_t          HLT_Dimuon0_Upsilon_Muon_NoL1Mass;
   // Bool_t          HLT_TripleMu_5_3_3_Mass3p8_DZ;
   // Bool_t          HLT_TripleMu_10_5_5_DZ;
   // Bool_t          HLT_TripleMu_12_10_5;
   // Bool_t          HLT_Tau3Mu_Mu7_Mu1_TkMu1_Tau15;
   // Bool_t          HLT_Tau3Mu_Mu7_Mu1_TkMu1_Tau15_Charge1;
   // Bool_t          HLT_Tau3Mu_Mu7_Mu1_TkMu1_IsoTau15;
   // Bool_t          HLT_Tau3Mu_Mu7_Mu1_TkMu1_IsoTau15_Charge1;
   // Bool_t          HLT_DoubleMu3_DZ_PFMET50_PFMHT60;
   // Bool_t          HLT_DoubleMu3_DZ_PFMET70_PFMHT70;
   // Bool_t          HLT_DoubleMu3_DZ_PFMET90_PFMHT90;
   // Bool_t          HLT_DoubleMu3_Trk_Tau3mu_NoL1Mass;
   // Bool_t          HLT_DoubleMu4_Jpsi_Displaced;
   // Bool_t          HLT_DoubleMu4_Jpsi_NoVertexing;
   // Bool_t          HLT_DoubleMu4_JpsiTrkTrk_Displaced;
   // Bool_t          HLT_DoubleMu4_JpsiTrk_Bc;
   // Bool_t          HLT_DoubleMu43NoFiltersNoVtx;
   // Bool_t          HLT_DoubleMu48NoFiltersNoVtx;
   // Bool_t          HLT_Mu43NoFiltersNoVtx_Photon43_CaloIdL;
   // Bool_t          HLT_Mu48NoFiltersNoVtx_Photon48_CaloIdL;
   // Bool_t          HLT_Mu38NoFiltersNoVtxDisplaced_Photon38_CaloIdL;
   // Bool_t          HLT_Mu43NoFiltersNoVtxDisplaced_Photon43_CaloIdL;
   // Bool_t          HLT_DoubleMu40NoFiltersNoVtxDisplaced;
   // Bool_t          HLT_DoubleMu20_7_Mass0to30_L1_DM4;
   // Bool_t          HLT_DoubleMu20_7_Mass0to30_L1_DM4EG;
   // Bool_t          HLT_HT425;
   // Bool_t          HLT_HT430_DisplacedDijet40_DisplacedTrack;
   // Bool_t          HLT_HT500_DisplacedDijet40_DisplacedTrack;
   // Bool_t          HLT_HT430_DisplacedDijet60_DisplacedTrack;
   // Bool_t          HLT_HT400_DisplacedDijet40_DisplacedTrack;
   // Bool_t          HLT_HT650_DisplacedDijet60_Inclusive;
   // Bool_t          HLT_HT550_DisplacedDijet60_Inclusive;
   // Bool_t          HLT_DiJet110_35_Mjj650_PFMET110;
   // Bool_t          HLT_DiJet110_35_Mjj650_PFMET120;
   // Bool_t          HLT_DiJet110_35_Mjj650_PFMET130;
   // Bool_t          HLT_TripleJet110_35_35_Mjj650_PFMET110;
   // Bool_t          HLT_TripleJet110_35_35_Mjj650_PFMET120;
   // Bool_t          HLT_TripleJet110_35_35_Mjj650_PFMET130;
   // Bool_t          HLT_Ele30_eta2p1_WPTight_Gsf_CentralPFJet35_EleCleaned;
   // Bool_t          HLT_Ele28_eta2p1_WPTight_Gsf_HT150;
   // Bool_t          HLT_Ele28_HighEta_SC20_Mass55;
   // Bool_t          HLT_DoubleMu20_7_Mass0to30_Photon23;
   // Bool_t          HLT_Ele15_IsoVVVL_PFHT450_CaloBTagDeepCSV_4p5;
   // Bool_t          HLT_Ele15_IsoVVVL_PFHT450_PFMET50;
   // Bool_t          HLT_Ele15_IsoVVVL_PFHT450;
   // Bool_t          HLT_Ele50_IsoVVVL_PFHT450;
   // Bool_t          HLT_Ele15_IsoVVVL_PFHT600;
   // Bool_t          HLT_Mu4_TrkIsoVVL_DiPFJet90_40_DEta3p5_MJJ750_HTT300_PFMETNoMu60;
   // Bool_t          HLT_Mu8_TrkIsoVVL_DiPFJet40_DEta3p5_MJJ750_HTT300_PFMETNoMu60;
   // Bool_t          HLT_Mu10_TrkIsoVVL_DiPFJet40_DEta3p5_MJJ750_HTT350_PFMETNoMu60;
   // Bool_t          HLT_Mu15_IsoVVVL_PFHT450_CaloBTagDeepCSV_4p5;
   // Bool_t          HLT_Mu15_IsoVVVL_PFHT450_PFMET50;
   // Bool_t          HLT_Mu15_IsoVVVL_PFHT450;
   // Bool_t          HLT_Mu50_IsoVVVL_PFHT450;
   // Bool_t          HLT_Mu15_IsoVVVL_PFHT600;
   // Bool_t          HLT_Mu3er1p5_PFJet100er2p5_PFMET70_PFMHT70_IDTight;
   // Bool_t          HLT_Mu3er1p5_PFJet100er2p5_PFMET80_PFMHT80_IDTight;
   // Bool_t          HLT_Mu3er1p5_PFJet100er2p5_PFMET90_PFMHT90_IDTight;
   // Bool_t          HLT_Mu3er1p5_PFJet100er2p5_PFMET100_PFMHT100_IDTight;
   // Bool_t          HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu70_PFMHTNoMu70_IDTight;
   // Bool_t          HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu80_PFMHTNoMu80_IDTight;
   // Bool_t          HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu90_PFMHTNoMu90_IDTight;
   // Bool_t          HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu100_PFMHTNoMu100_IDTight;
   // Bool_t          HLT_Dimuon10_PsiPrime_Barrel_Seagulls;
   // Bool_t          HLT_Dimuon20_Jpsi_Barrel_Seagulls;
   // Bool_t          HLT_Dimuon10_Upsilon_y1p4;
   // Bool_t          HLT_Dimuon12_Upsilon_y1p4;
   // Bool_t          HLT_Dimuon14_Phi_Barrel_Seagulls;
   // Bool_t          HLT_Dimuon25_Jpsi;
   // Bool_t          HLT_Dimuon14_PsiPrime;
   // Bool_t          HLT_Dimuon14_PsiPrime_noCorrL1;
   // Bool_t          HLT_Dimuon18_PsiPrime;
   // Bool_t          HLT_Dimuon18_PsiPrime_noCorrL1;
   // Bool_t          HLT_Dimuon24_Upsilon_noCorrL1;
   // Bool_t          HLT_Dimuon24_Phi_noCorrL1;
   // Bool_t          HLT_Dimuon25_Jpsi_noCorrL1;
   // Bool_t          HLT_DiMu4_Ele9_CaloIdL_TrackIdL_DZ_Mass3p8;
   // Bool_t          HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ;
   // Bool_t          HLT_DiMu9_Ele9_CaloIdL_TrackIdL;
   // Bool_t          HLT_DoubleIsoMu20_eta2p1;
   // Bool_t          HLT_TrkMu12_DoubleTrkMu5NoFiltersNoVtx;
   // Bool_t          HLT_TrkMu16_DoubleTrkMu6NoFiltersNoVtx;
   // Bool_t          HLT_TrkMu17_DoubleTrkMu8NoFiltersNoVtx;
   // Bool_t          HLT_Mu8;
   // Bool_t          HLT_Mu17;
   // Bool_t          HLT_Mu19;
   // Bool_t          HLT_Mu17_Photon30_IsoCaloId;
   // Bool_t          HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30;
   // Bool_t          HLT_Ele12_CaloIdL_TrackIdL_IsoVL_PFJet30;
   // Bool_t          HLT_Ele15_CaloIdL_TrackIdL_IsoVL_PFJet30;
   // Bool_t          HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30;
   // Bool_t          HLT_Ele8_CaloIdM_TrackIdM_PFJet30;
   // Bool_t          HLT_Ele17_CaloIdM_TrackIdM_PFJet30;
   // Bool_t          HLT_Ele23_CaloIdM_TrackIdM_PFJet30;
   // Bool_t          HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165;
   // Bool_t          HLT_Ele115_CaloIdVT_GsfTrkIdT;
   // Bool_t          HLT_Ele135_CaloIdVT_GsfTrkIdT;
   // Bool_t          HLT_Ele145_CaloIdVT_GsfTrkIdT;
   // Bool_t          HLT_Ele200_CaloIdVT_GsfTrkIdT;
   // Bool_t          HLT_Ele250_CaloIdVT_GsfTrkIdT;
   // Bool_t          HLT_Ele300_CaloIdVT_GsfTrkIdT;
   // Bool_t          HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepCSV_4p5;
   // Bool_t          HLT_PFHT330PT30_QuadPFJet_75_60_45_40;
   // Bool_t          HLT_PFHT400_SixPFJet32_DoublePFBTagDeepCSV_2p94;
   // Bool_t          HLT_PFHT400_SixPFJet32;
   // Bool_t          HLT_PFHT450_SixPFJet36_PFBTagDeepCSV_1p59;
   // Bool_t          HLT_PFHT450_SixPFJet36;
   // Bool_t          HLT_PFHT400_FivePFJet_100_100_60_30_30;
   // Bool_t          HLT_PFHT400_FivePFJet_100_100_60_30_30_DoublePFBTagDeepCSV_4p5;
   // Bool_t          HLT_PFHT400_FivePFJet_120_120_60_30_30_DoublePFBTagDeepCSV_4p5;
   // Bool_t          HLT_PFHT350;
   // Bool_t          HLT_PFHT350MinPFJet15;
   // Bool_t          HLT_Photon60_R9Id90_CaloIdL_IsoL;
   // Bool_t          HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL;
   // Bool_t          HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL_PFHT350MinPFJet15;
   // Bool_t          HLT_ECALHT800;
   // Bool_t          HLT_DiSC30_18_EIso_AND_HE_Mass70;
   // Bool_t          HLT_Physics;
   // Bool_t          HLT_EphemeralPhysics;
   // Bool_t          HLT_Random;
   // Bool_t          HLT_ZeroBias;
   // Bool_t          HLT_ZeroBias_Alignment;
   // Bool_t          HLT_EphemeralZeroBias;
   // Bool_t          HLT_AK4CaloJet30;
   // Bool_t          HLT_AK4CaloJet40;
   // Bool_t          HLT_AK4CaloJet50;
   // Bool_t          HLT_AK4CaloJet80;
   // Bool_t          HLT_AK4CaloJet100;
   // Bool_t          HLT_AK4CaloJet120;
   // Bool_t          HLT_AK4PFJet30;
   // Bool_t          HLT_AK4PFJet50;
   // Bool_t          HLT_AK4PFJet80;
   // Bool_t          HLT_AK4PFJet100;
   // Bool_t          HLT_AK4PFJet120;
   // Bool_t          HLT_SinglePhoton10_Eta3p1ForPPRef;
   // Bool_t          HLT_SinglePhoton20_Eta3p1ForPPRef;
   // Bool_t          HLT_SinglePhoton30_Eta3p1ForPPRef;
   // Bool_t          HLT_Photon20_HoverELoose;
   // Bool_t          HLT_Photon30_HoverELoose;
   // Bool_t          HLT_EcalCalibration;
   // Bool_t          HLT_HcalCalibration;
   // Bool_t          HLT_L1UnpairedBunchBptxMinus;
   // Bool_t          HLT_L1UnpairedBunchBptxPlus;
   // Bool_t          HLT_L1NotBptxOR;
   // Bool_t          HLT_L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142;
   // Bool_t          HLT_CDC_L2cosmic_10_er1p0;
   // Bool_t          HLT_CDC_L2cosmic_5p5_er1p0;
   // Bool_t          HLT_HcalNZS;
   // Bool_t          HLT_HcalPhiSym;
   // Bool_t          HLT_HcalIsolatedbunch;
   // Bool_t          HLT_IsoTrackHB;
   // Bool_t          HLT_IsoTrackHE;
   // Bool_t          HLT_ZeroBias_FirstCollisionAfterAbortGap;
   // Bool_t          HLT_ZeroBias_IsolatedBunches;
   // Bool_t          HLT_ZeroBias_FirstCollisionInTrain;
   // Bool_t          HLT_ZeroBias_LastCollisionInTrain;
   // Bool_t          HLT_ZeroBias_FirstBXAfterTrain;
   // Bool_t          HLT_MediumChargedIsoPFTau180HighPtRelaxedIso_Trk50_eta2p1;
   // Bool_t          HLT_MediumChargedIsoPFTau200HighPtRelaxedIso_Trk50_eta2p1;
   // Bool_t          HLT_MediumChargedIsoPFTau220HighPtRelaxedIso_Trk50_eta2p1;
   // Bool_t          HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL;
   // Bool_t          HLT_Rsq0p35;
   // Bool_t          HLT_Rsq0p40;
   // Bool_t          HLT_RsqMR300_Rsq0p09_MR200;
   // Bool_t          HLT_RsqMR320_Rsq0p09_MR200;
   // Bool_t          HLT_RsqMR300_Rsq0p09_MR200_4jet;
   // Bool_t          HLT_RsqMR320_Rsq0p09_MR200_4jet;
   // Bool_t          HLT_IsoMu27_MET90;
   // Bool_t          HLT_VBF_DoubleLooseChargedIsoPFTauHPS20_Trk1_eta2p1;
   // Bool_t          HLT_VBF_DoubleMediumChargedIsoPFTauHPS20_Trk1_eta2p1;
   // Bool_t          HLT_VBF_DoubleMediumDeepTauPFTauHPS20_eta2p1;
   // Bool_t          HLT_VBF_DoubleTightChargedIsoPFTauHPS20_Trk1_eta2p1;
   // Bool_t          HLT_Photon50_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3_PFMET50;
   // Bool_t          HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3;
   // Bool_t          HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ600DEta3;
   // Bool_t          HLT_PFMET100_PFMHT100_IDTight_PFHT60;
   // Bool_t          HLT_PFMETNoMu100_PFMHTNoMu100_IDTight_PFHT60;
   // Bool_t          HLT_PFMETTypeOne100_PFMHT100_IDTight_PFHT60;
   // Bool_t          HLT_Mu18_Mu9_SameSign;
   // Bool_t          HLT_Mu18_Mu9_SameSign_DZ;
   // Bool_t          HLT_Mu18_Mu9;
   // Bool_t          HLT_Mu18_Mu9_DZ;
   // Bool_t          HLT_Mu20_Mu10_SameSign;
   // Bool_t          HLT_Mu20_Mu10_SameSign_DZ;
   // Bool_t          HLT_Mu20_Mu10;
   // Bool_t          HLT_Mu20_Mu10_DZ;
   // Bool_t          HLT_Mu23_Mu12_SameSign;
   // Bool_t          HLT_Mu23_Mu12_SameSign_DZ;
   // Bool_t          HLT_Mu23_Mu12;
   // Bool_t          HLT_Mu23_Mu12_DZ;
   // Bool_t          HLT_DoubleMu2_Jpsi_DoubleTrk1_Phi1p05;
   // Bool_t          HLT_DoubleMu2_Jpsi_DoubleTkMu0_Phi;
   // Bool_t          HLT_DoubleMu3_DCA_PFMET50_PFMHT60;
   // Bool_t          HLT_TripleMu_5_3_3_Mass3p8_DCA;
   // Bool_t          HLT_QuadPFJet98_83_71_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1;
   // Bool_t          HLT_QuadPFJet103_88_75_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1;
   // Bool_t          HLT_QuadPFJet111_90_80_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1;
   // Bool_t          HLT_QuadPFJet98_83_71_15_PFBTagDeepCSV_1p3_VBF2;
   // Bool_t          HLT_QuadPFJet103_88_75_15_PFBTagDeepCSV_1p3_VBF2;
   // Bool_t          HLT_QuadPFJet105_88_76_15_PFBTagDeepCSV_1p3_VBF2;
   // Bool_t          HLT_QuadPFJet111_90_80_15_PFBTagDeepCSV_1p3_VBF2;
   // Bool_t          HLT_QuadPFJet98_83_71_15;
   // Bool_t          HLT_QuadPFJet103_88_75_15;
   // Bool_t          HLT_QuadPFJet105_88_76_15;
   // Bool_t          HLT_QuadPFJet111_90_80_15;
   // Bool_t          HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p17;
   // Bool_t          HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p1;
   // Bool_t          HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_p02;
   // Bool_t          HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np2;
   // Bool_t          HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np4;
   // Bool_t          HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_Mass55;
   // Bool_t          HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId;
   // Bool_t          HLT_Mu12_IP6_part0;
   // Bool_t          HLT_Mu12_IP6_part1;
   // Bool_t          HLT_Mu12_IP6_part2;
   // Bool_t          HLT_Mu12_IP6_part3;
   // Bool_t          HLT_Mu12_IP6_part4;
   // Bool_t          HLT_Mu9_IP5_part0;
   // Bool_t          HLT_Mu9_IP5_part1;
   // Bool_t          HLT_Mu9_IP5_part2;
   // Bool_t          HLT_Mu9_IP5_part3;
   // Bool_t          HLT_Mu9_IP5_part4;
   // Bool_t          HLT_Mu7_IP4_part0;
   // Bool_t          HLT_Mu7_IP4_part1;
   // Bool_t          HLT_Mu7_IP4_part2;
   // Bool_t          HLT_Mu7_IP4_part3;
   // Bool_t          HLT_Mu7_IP4_part4;
   // Bool_t          HLT_Mu9_IP4_part0;
   // Bool_t          HLT_Mu9_IP4_part1;
   // Bool_t          HLT_Mu9_IP4_part2;
   // Bool_t          HLT_Mu9_IP4_part3;
   // Bool_t          HLT_Mu9_IP4_part4;
   // Bool_t          HLT_Mu8_IP5_part0;
   // Bool_t          HLT_Mu8_IP5_part1;
   // Bool_t          HLT_Mu8_IP5_part2;
   // Bool_t          HLT_Mu8_IP5_part3;
   // Bool_t          HLT_Mu8_IP5_part4;
   // Bool_t          HLT_Mu8_IP6_part0;
   // Bool_t          HLT_Mu8_IP6_part1;
   // Bool_t          HLT_Mu8_IP6_part2;
   // Bool_t          HLT_Mu8_IP6_part3;
   // Bool_t          HLT_Mu8_IP6_part4;
   // Bool_t          HLT_Mu9_IP6_part0;
   // Bool_t          HLT_Mu9_IP6_part1;
   // Bool_t          HLT_Mu9_IP6_part2;
   // Bool_t          HLT_Mu9_IP6_part3;
   // Bool_t          HLT_Mu9_IP6_part4;
   // Bool_t          HLT_Mu8_IP3_part0;
   // Bool_t          HLT_Mu8_IP3_part1;
   // Bool_t          HLT_Mu8_IP3_part2;
   // Bool_t          HLT_Mu8_IP3_part3;
   // Bool_t          HLT_Mu8_IP3_part4;
   // Bool_t          HLT_Mu9_IP0_part0;
   // Bool_t          HLT_Mu9_IP3_part0;
   // Bool_t          HLT_QuadPFJet105_88_76_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1;
   // Bool_t          HLT_TrkMu6NoFiltersNoVtx;
   // Bool_t          HLT_TrkMu16NoFiltersNoVtx;
   // Bool_t          HLT_DoubleTrkMu_16_6_NoFiltersNoVtx;
   // Bool_t          HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1;
   // Bool_t          HLT_DoubleMediumChargedIsoPFTauHPS40_Trk1_eta2p1;
   // Bool_t          HLT_DoubleTightChargedIsoPFTauHPS35_Trk1_eta2p1;
   // Bool_t          HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1;
   // Bool_t          HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1;
   // Bool_t          HLT_IsoMu24_eta2p1_LooseDeepTauPFTauHPS180_eta2p1;
   // Bool_t          HLT_IsoMu24_eta2p1_LooseDeepTauPFTauHPS30_eta2p1_CrossL1;
   // Bool_t          HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS35_L2NN_eta2p1_CrossL1;
   // Bool_t          HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1;
   // Bool_t          HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepJet_4p5;
   // Bool_t          HLT_PFHT400_FivePFJet_100_100_60_30_30_DoublePFBTagDeepJet_4p5;
   // Bool_t          HLT_PFHT400_FivePFJet_120_120_60_30_30_DoublePFBTagDeepJet_4p5;
   // Bool_t          HLT_PFHT400_SixPFJet32_DoublePFBTagDeepJet_2p94;
   // Bool_t          HLT_PFHT450_SixPFJet36_PFBTagDeepJet_1p59;
   // Bool_t          HLT_QuadPFJet103_88_75_15_DoublePFBTagDeepJet_1p3_7p7_VBF1;
   // Bool_t          HLT_QuadPFJet103_88_75_15_PFBTagDeepJet_1p3_VBF2;
   // Bool_t          HLT_QuadPFJet105_88_76_15_DoublePFBTagDeepJet_1p3_7p7_VBF1;
   // Bool_t          HLT_QuadPFJet105_88_76_15_PFBTagDeepJet_1p3_VBF2;
   // Bool_t          HLT_QuadPFJet111_90_80_15_DoublePFBTagDeepJet_1p3_7p7_VBF1;
   // Bool_t          HLT_QuadPFJet111_90_80_15_PFBTagDeepJet_1p3_VBF2;
   // Bool_t          HLT_QuadPFJet98_83_71_15_DoublePFBTagDeepJet_1p3_7p7_VBF1;
   // Bool_t          HLT_QuadPFJet98_83_71_15_PFBTagDeepJet_1p3_VBF2;
   // Bool_t          HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30_PFBtagDeepJet_1p5;
   // Bool_t          HLT_QuadPFJet70_50_40_30;
   // Bool_t          HLT_QuadPFJet70_50_40_30_PFBTagParticleNet_2BTagSum0p65;
   // Bool_t          HLT_QuadPFJet70_50_40_35_PFBTagParticleNet_2BTagSum0p65;
   // Bool_t          HLT_QuadPFJet70_50_45_35_PFBTagParticleNet_2BTagSum0p65;
   // Bool_t          HLT_AK8PFJet230_SoftDropMass40;
   // Bool_t          HLT_AK8PFJet230_SoftDropMass40_PFAK8ParticleNetBB0p35;
   // Bool_t          HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetBB0p35;
   // Bool_t          HLT_AK8PFJet275_SoftDropMass40_PFAK8ParticleNetBB0p35;
   // Bool_t          HLT_AK8PFJet400_SoftDropMass40;
   // Bool_t          HLT_AK8PFJet425_SoftDropMass40;
   // Bool_t          HLT_AK8PFJet450_SoftDropMass40;
   // Bool_t          HLT_AK8PFJet230_SoftDropMass40_PFAK8ParticleNetTauTau0p30;
   // Bool_t          HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetTauTau0p30;
   // Bool_t          HLT_AK8PFJet275_SoftDropMass40_PFAK8ParticleNetTauTau0p30;
   // Bool_t          HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60;
   // Bool_t          HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75;
   // Bool_t          HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_CrossL1;
   // Bool_t          HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60_CrossL1;
   // Bool_t          HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75_CrossL1;
   // Bool_t          HLT_DoublePFJets40_Mass500_MediumDeepTauPFTauHPS45_L2NN_MediumDeepTauPFTauHPS20_eta2p1;
   // Bool_t          HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS20_eta2p1_SingleL1;
   // Bool_t          HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS45_L2NN_eta2p1_CrossL1;
   // Bool_t          HLT_DoubleL2Mu10NoVtx_2Cha_VetoL3Mu0DxyMax1cm;
   // Bool_t          HLT_DoubleL2Mu12NoVtx_2Cha_VetoL3Mu0DxyMax1cm;
   // Bool_t          HLT_DoubleL2Mu14NoVtx_2Cha_VetoL3Mu0DxyMax1cm;
   // Bool_t          HLT_DoubleL3Mu16_10NoVtx_DxyMin0p01cm;
   // Bool_t          HLT_DoubleL3Mu18_10NoVtx_DxyMin0p01cm;
   // Bool_t          HLT_DoubleL3Mu20_10NoVtx_DxyMin0p01cm;
   // Bool_t          HLT_L2Mu10NoVtx_2Cha;
   // Bool_t          HLT_L2Mu10NoVtx_2Cha_VetoL3Mu0DxyMax1cm;
   // Bool_t          HLT_L3Mu10NoVtx;
   // Bool_t          HLT_L3Mu10NoVtx_DxyMin0p01cm;
   // Bool_t          HLT_Mu20NoFiltersNoVtxDisplaced_Photon20_CaloCustomId;
   // Bool_t          HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1;
   // Bool_t          HLT_HT430_DelayedJet40_DoubleDelay0p5nsTrackless;
   // Bool_t          HLT_HT430_DelayedJet40_DoubleDelay1nsInclusive;
   // Bool_t          HLT_HT430_DelayedJet40_SingleDelay1nsTrackless;
   // Bool_t          HLT_HT430_DelayedJet40_SingleDelay2nsInclusive;
   // Bool_t          HLT_L1Mu6HT240;
   // Bool_t          HLT_Mu6HT240_DisplacedDijet30_Inclusive0PtrkShortSig5;
   // Bool_t          HLT_Mu6HT240_DisplacedDijet30_Inclusive1PtrkShortSig5_DisplacedLoose;
   // Bool_t          HLT_Mu6HT240_DisplacedDijet35_Inclusive0PtrkShortSig5;
   // Bool_t          HLT_Mu6HT240_DisplacedDijet35_Inclusive1PtrkShortSig5_DisplacedLoose;
   // Bool_t          HLT_Mu6HT240_DisplacedDijet40_Inclusive0PtrkShortSig5;
   // Bool_t          HLT_Mu6HT240_DisplacedDijet40_Inclusive1PtrkShortSig5_DisplacedLoose;
   // Bool_t          HLT_HT430_DisplacedDijet30_Inclusive1PtrkShortSig5;
   // Bool_t          HLT_HT430_DisplacedDijet35_Inclusive1PtrkShortSig5;
   // Bool_t          HLT_HT430_DisplacedDijet40_Inclusive1PtrkShortSig5;
   // Bool_t          HLT_CaloMET60_DTCluster50;
   // Bool_t          HLT_CaloMET60_DTClusterNoMB1S50;
   // Bool_t          HLT_L1MET_DTCluster50;
   // Bool_t          HLT_L1MET_DTClusterNoMB1S50;
   // Bool_t          HLT_CscCluster_Loose;
   // Bool_t          HLT_CscCluster_Medium;
   // Bool_t          HLT_CscCluster_Tight;
   // Bool_t          HLT_L1CSCShower_DTCluster50;
   // Bool_t          HLT_L1CSCShower_DTCluster75;
   // Bool_t          HLT_PFMET105_IsoTrk50;
   // Bool_t          HLT_PFMET105_PFJet100_looseRecoiling;
   // Bool_t          HLT_PFMET110_PFJet100;
   // Bool_t          HLT_PFMET110_PFJet100_looseRecoiling;
   // Bool_t          HLT_DoubleL3dTksMu16_10NoVtx_DxyMin0p01cm;
   // Bool_t          HLT_L3dTksMu10_NoVtx_DxyMin0p01cm;
   // Bool_t          HLT_HT170_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack;
   // Bool_t          HLT_HT200_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack;
   // Bool_t          HLT_HT200_L1SingleLLPJet_DisplacedDijet60_DisplacedTrack;
   // Bool_t          HLT_HT270_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack;
   // Bool_t          HLT_HT320_L1SingleLLPJet_DisplacedDijet60_Inclusive;
   // Bool_t          HLT_HT420_L1SingleLLPJet_DisplacedDijet60_Inclusive;
   // Bool_t          HLT_HT200_L1SingleLLPJet_DelayedJet40_SingleDelay1nsTrackless;
   // Bool_t          HLT_HT200_L1SingleLLPJet_DelayedJet40_SingleDelay2nsInclusive;
   // Bool_t          HLT_HT200_L1SingleLLPJet_DelayedJet40_DoubleDelay0p5nsTrackless;
   // Bool_t          HLT_HT200_L1SingleLLPJet_DelayedJet40_DoubleDelay1nsInclusive;
   // Bool_t          HLT_HT200_L1SingleLLPJet_DisplacedDijet30_Inclusive1PtrkShortSig5;
   // Bool_t          HLT_HT200_L1SingleLLPJet_DisplacedDijet35_Inclusive1PtrkShortSig5;
   // Bool_t          HLT_HT200_L1SingleLLPJet_DisplacedDijet40_Inclusive1PtrkShortSig5;
   // Bool_t          HLT_DiPhoton10Time1ns;
   // Bool_t          HLT_DiPhoton10Time1p2ns;
   // Bool_t          HLT_DiPhoton10Time1p4ns;
   // Bool_t          HLT_DiPhoton10Time1p6ns;
   // Bool_t          HLT_DiPhoton10Time1p8ns;
   // Bool_t          HLT_DiPhoton10Time2ns;
   // Bool_t          HLT_DiPhoton10sminlt0p1;
   // Bool_t          HLT_DiPhoton10sminlt0p12;
   // Bool_t          HLT_DiPhoton10sminlt0p14;
   // Bool_t          HLT_DiPhoton10sminlt0p16;
   // Bool_t          HLT_DiPhoton10_CaloIdL;
   // Bool_t          HLT_DoubleEle4_eta1p22_mMax6;
   // Bool_t          HLT_DoubleEle4p5_eta1p22_mMax6;
   // Bool_t          HLT_DoubleEle5_eta1p22_mMax6;
   // Bool_t          HLT_DoubleEle5p5_eta1p22_mMax6;
   // Bool_t          HLT_DoubleEle6_eta1p22_mMax6;
   // Bool_t          HLT_DoubleEle6p5_eta1p22_mMax6;
   // Bool_t          HLT_DoubleEle7_eta1p22_mMax6;
   // Bool_t          HLT_DoubleEle7p5_eta1p22_mMax6;
   // Bool_t          HLT_DoubleEle8_eta1p22_mMax6;
   // Bool_t          HLT_DoubleEle8p5_eta1p22_mMax6;
   // Bool_t          HLT_DoubleEle9_eta1p22_mMax6;
   // Bool_t          HLT_DoubleEle9p5_eta1p22_mMax6;
   // Bool_t          HLT_DoubleEle10_eta1p22_mMax6;
   // Bool_t          HLT_Diphoton20_14_eta1p5_R9IdL_AND_HE_AND_IsoTCaloIdT;
   // Bool_t          HLT_Diphoton20_14_eta1p5_R9IdL_AND_HET_AND_IsoTCaloIdT;
   // Bool_t          HLT_Diphoton22_14_eta1p5_R9IdL_AND_HE_AND_IsoTCaloIdT;
   // Bool_t          HLT_Diphoton22_14_eta1p5_R9IdL_AND_HET_AND_IsoTCaloIdT;
   // Bool_t          HLT_ExpressMuons;
   // Bool_t          HLT_OnlineMonitorGroup;
   // Bool_t          HLT_PPSMaxTracksPerArm1;
   // Bool_t          HLT_PPSMaxTracksPerRP4;
   Bool_t          HLTriggerFinalPath;

   // List of branches
   TBranch        *b_run;   //!
   TBranch        *b_luminosityBlock;   //!
   TBranch        *b_event;   //!
   TBranch        *b_bunchCrossing;   //!
   // TBranch        *b_HTXS_njets25;   //!
   // TBranch        *b_HTXS_njets30;   //!
   // TBranch        *b_HTXS_stage1_1_cat_pTjet25GeV;   //!
   // TBranch        *b_HTXS_stage1_1_cat_pTjet30GeV;   //!
   // TBranch        *b_HTXS_stage1_1_fine_cat_pTjet25GeV;   //!
   // TBranch        *b_HTXS_stage1_1_fine_cat_pTjet30GeV;   //!
   // TBranch        *b_HTXS_stage1_2_cat_pTjet25GeV;   //!
   // TBranch        *b_HTXS_stage1_2_cat_pTjet30GeV;   //!
   // TBranch        *b_HTXS_stage1_2_fine_cat_pTjet25GeV;   //!
   // TBranch        *b_HTXS_stage1_2_fine_cat_pTjet30GeV;   //!
   // TBranch        *b_HTXS_stage_0;   //!
   // TBranch        *b_HTXS_stage_1_pTjet25;   //!
   // TBranch        *b_HTXS_stage_1_pTjet30;   //!
   // TBranch        *b_HTXS_Higgs_pt;   //!
   // TBranch        *b_HTXS_Higgs_y;   //!
   // TBranch        *b_BeamSpot_type;   //!
   // TBranch        *b_BeamSpot_sigmaZ;   //!
   // TBranch        *b_BeamSpot_sigmaZError;   //!
   // TBranch        *b_BeamSpot_z;   //!
   // TBranch        *b_BeamSpot_zError;   //!
   // TBranch        *b_nboostedTau;   //!
   // TBranch        *b_boostedTau_idAntiEle2018;   //!
   // TBranch        *b_boostedTau_idAntiMu;   //!
   // TBranch        *b_boostedTau_idMVAnewDM2017v2;   //!
   // TBranch        *b_boostedTau_idMVAoldDM2017v2;   //!
   // TBranch        *b_boostedTau_jetIdx;   //!
   // TBranch        *b_boostedTau_rawAntiEleCat2018;   //!
   // TBranch        *b_boostedTau_charge;   //!
   // TBranch        *b_boostedTau_decayMode;   //!
   // TBranch        *b_boostedTau_chargedIso;   //!
   // TBranch        *b_boostedTau_eta;   //!
   // TBranch        *b_boostedTau_leadTkDeltaEta;   //!
   // TBranch        *b_boostedTau_leadTkDeltaPhi;   //!
   // TBranch        *b_boostedTau_leadTkPtOverTauPt;   //!
   // TBranch        *b_boostedTau_mass;   //!
   // TBranch        *b_boostedTau_neutralIso;   //!
   // TBranch        *b_boostedTau_phi;   //!
   // TBranch        *b_boostedTau_photonsOutsideSignalCone;   //!
   // TBranch        *b_boostedTau_pt;   //!
   // TBranch        *b_boostedTau_puCorr;   //!
   // TBranch        *b_boostedTau_rawAntiEle2018;   //!
   // TBranch        *b_boostedTau_rawIso;   //!
   // TBranch        *b_boostedTau_rawIsodR03;   //!
   // TBranch        *b_boostedTau_rawMVAnewDM2017v2;   //!
   // TBranch        *b_boostedTau_rawMVAoldDM2017v2;   //!
   // TBranch        *b_CaloMET_phi;   //!
   // TBranch        *b_CaloMET_pt;   //!
   // TBranch        *b_CaloMET_sumEt;   //!
   // TBranch        *b_ChsMET_phi;   //!
   // TBranch        *b_ChsMET_pt;   //!
   // TBranch        *b_ChsMET_sumEt;   //!
   // TBranch        *b_nCorrT1METJet;   //!
   // TBranch        *b_CorrT1METJet_area;   //!
   // TBranch        *b_CorrT1METJet_eta;   //!
   // TBranch        *b_CorrT1METJet_muonSubtrFactor;   //!
   // TBranch        *b_CorrT1METJet_phi;   //!
   // TBranch        *b_CorrT1METJet_rawPt;   //!
   // TBranch        *b_DeepMETResolutionTune_phi;   //!
   // TBranch        *b_DeepMETResolutionTune_pt;   //!
   // TBranch        *b_DeepMETResponseTune_phi;   //!
   // TBranch        *b_DeepMETResponseTune_pt;   //!
   TBranch        *b_nElectron;   //!
   TBranch        *b_Electron_seediEtaOriX;   //!
   TBranch        *b_Electron_convVeto;   //!
   TBranch        *b_Electron_cutBased;   //!
   TBranch        *b_Electron_cutBased_HEEP;   //!
   TBranch        *b_Electron_isPFcand;   //!
   TBranch        *b_Electron_jetNDauCharged;   //!
   TBranch        *b_Electron_lostHits;   //!
   TBranch        *b_Electron_mvaIso_WP80;   //!
   TBranch        *b_Electron_mvaIso_WP90;   //!
   TBranch        *b_Electron_mvaNoIso_WP80;   //!
   TBranch        *b_Electron_mvaNoIso_WP90;   //!
   TBranch        *b_Electron_seedGain;   //!
   TBranch        *b_Electron_tightCharge;   //!
   TBranch        *b_Electron_jetIdx;   //!
   // TBranch        *b_Electron_photonIdx;   //!
   TBranch        *b_Electron_svIdx;   //!
   // TBranch        *b_Electron_fsrPhotonIdx;   //!
   TBranch        *b_Electron_charge;   //!
   TBranch        *b_Electron_pdgId;   //!
   TBranch        *b_Electron_seediPhiOriY;   //!
   TBranch        *b_Electron_vidNestedWPBitmap;   //!
   TBranch        *b_Electron_vidNestedWPBitmapHEEP;   //!
   TBranch        *b_Electron_deltaEtaSC;   //!
   // TBranch        *b_Electron_dr03EcalRecHitSumEt;   //!
   // TBranch        *b_Electron_dr03HcalDepth1TowerSumEt;   //!
   // TBranch        *b_Electron_dr03TkSumPt;   //!
   // TBranch        *b_Electron_dr03TkSumPtHEEP;   //!
   TBranch        *b_Electron_dxy;   //!
   TBranch        *b_Electron_dxyErr;   //!
   TBranch        *b_Electron_dz;   //!
   TBranch        *b_Electron_dzErr;   //!
   TBranch        *b_Electron_eInvMinusPInv;   //!
   TBranch        *b_Electron_energyErr;   //!
   TBranch        *b_Electron_eta;   //!
   TBranch        *b_Electron_hoe;   //!
   TBranch        *b_Electron_ip3d;   //!
   TBranch        *b_Electron_jetPtRelv2;   //!
   TBranch        *b_Electron_jetRelIso;   //!
   TBranch        *b_Electron_mass;   //!
   TBranch        *b_Electron_miniPFRelIso_all;   //!
   TBranch        *b_Electron_miniPFRelIso_chg;   //!
   TBranch        *b_Electron_mvaHZZIso;   //!
   TBranch        *b_Electron_mvaIso;   //!
   TBranch        *b_Electron_mvaNoIso;   //!
   TBranch        *b_Electron_pfRelIso03_all;   //!
   TBranch        *b_Electron_pfRelIso03_chg;   //!
   TBranch        *b_Electron_phi;   //!
   TBranch        *b_Electron_pt;   //!
   TBranch        *b_Electron_r9;   //!
   TBranch        *b_Electron_scEtOverPt;   //!
   TBranch        *b_Electron_sieie;   //!
   TBranch        *b_Electron_sip3d;   //!
   //TBranch        *b_Electron_mvaTTH;   //!
   TBranch        *b_nFatJet;   //!
   //TBranch        *b_FatJet_jetId;   //!
   TBranch        *b_FatJet_nConstituents;   //!
   TBranch        *b_FatJet_subJetIdx1;   //!
   TBranch        *b_FatJet_subJetIdx2;   //!
   TBranch        *b_FatJet_electronIdx3SJ;   //!
   TBranch        *b_FatJet_muonIdx3SJ;   //!
   TBranch        *b_FatJet_area;   //!
   //TBranch        *b_FatJet_btagDDBvLV2;   //!
   //TBranch        *b_FatJet_btagDDCvBV2;   //!
   //TBranch        *b_FatJet_btagDDCvLV2;   //!
   //TBranch        *b_FatJet_btagDeepB;   //!
   //TBranch        *b_FatJet_btagHbb;   //!
   TBranch        *b_FatJet_eta;   //!
   TBranch        *b_FatJet_mass;   //!
   TBranch        *b_FatJet_msoftdrop;   //!
   TBranch        *b_FatJet_n2b1;   //!
   TBranch        *b_FatJet_n3b1;   //!
   // TBranch        *b_FatJet_particleNetWithMass_H4qvsQCD;   //!
   // TBranch        *b_FatJet_particleNetWithMass_HbbvsQCD;   //!
   // TBranch        *b_FatJet_particleNetWithMass_HccvsQCD;   //!
   // TBranch        *b_FatJet_particleNetWithMass_QCD;   //!
   // TBranch        *b_FatJet_particleNetWithMass_TvsQCD;   //!
   // TBranch        *b_FatJet_particleNetWithMass_WvsQCD;   //!
   // TBranch        *b_FatJet_particleNetWithMass_ZvsQCD;   //!
   // TBranch        *b_FatJet_particleNet_QCD;   //!
   // TBranch        *b_FatJet_particleNet_QCD0HF;   //!
   // TBranch        *b_FatJet_particleNet_QCD1HF;   //!
   // TBranch        *b_FatJet_particleNet_QCD2HF;   //!
   // TBranch        *b_FatJet_particleNet_XbbVsQCD;   //!
   // TBranch        *b_FatJet_particleNet_XccVsQCD;   //!
   // TBranch        *b_FatJet_particleNet_XggVsQCD;   //!
   // TBranch        *b_FatJet_particleNet_XqqVsQCD;   //!
   // TBranch        *b_FatJet_particleNet_XteVsQCD;   //!
   // TBranch        *b_FatJet_particleNet_XtmVsQCD;   //!
   // TBranch        *b_FatJet_particleNet_XttVsQCD;   //!
   // TBranch        *b_FatJet_particleNet_massCorr;   //!
   TBranch        *b_FatJet_phi;   //!
   TBranch        *b_FatJet_pt;   //!
   TBranch        *b_FatJet_rawFactor;   //!
   TBranch        *b_FatJet_tau1;   //!
   TBranch        *b_FatJet_tau2;   //!
   TBranch        *b_FatJet_tau3;   //!
   TBranch        *b_FatJet_tau4;   //!
   TBranch        *b_FatJet_lsf3;   //!
   // TBranch        *b_nFsrPhoton;   //!
   // TBranch        *b_FsrPhoton_electronIdx;   //!
   // TBranch        *b_FsrPhoton_muonIdx;   //!
   // TBranch        *b_FsrPhoton_dROverEt2;   //!
   // TBranch        *b_FsrPhoton_eta;   //!
   // TBranch        *b_FsrPhoton_phi;   //!
   // TBranch        *b_FsrPhoton_pt;   //!
   // TBranch        *b_FsrPhoton_relIso03;   //!
   // TBranch        *b_nGenJetAK8;   //!
   // TBranch        *b_GenJetAK8_eta;   //!
   // TBranch        *b_GenJetAK8_mass;   //!
   // TBranch        *b_GenJetAK8_phi;   //!
   // TBranch        *b_GenJetAK8_pt;   //!
   TBranch        *b_nGenJet;   //!
   TBranch        *b_GenJet_eta;   //!
   TBranch        *b_GenJet_mass;   //!
   TBranch        *b_GenJet_phi;   //!
   TBranch        *b_GenJet_pt;   //!
   TBranch        *b_nGenPart;   //!
   TBranch        *b_GenPart_genPartIdxMother;   //!
   TBranch        *b_GenPart_statusFlags;   //!
   TBranch        *b_GenPart_pdgId;   //!
   TBranch        *b_GenPart_status;   //!
   TBranch        *b_GenPart_eta;   //!
   TBranch        *b_GenPart_mass;   //!
   TBranch        *b_GenPart_phi;   //!
   TBranch        *b_GenPart_pt;   //!
   // TBranch        *b_nGenProton;   //!
   // TBranch        *b_GenProton_isPU;   //!
   // TBranch        *b_GenProton_px;   //!
   // TBranch        *b_GenProton_py;   //!
   // TBranch        *b_GenProton_pz;   //!
   // TBranch        *b_GenProton_vz;   //!
   // TBranch        *b_nSubGenJetAK8;   //!
   // TBranch        *b_SubGenJetAK8_eta;   //!
   // TBranch        *b_SubGenJetAK8_mass;   //!
   // TBranch        *b_SubGenJetAK8_phi;   //!
   // TBranch        *b_SubGenJetAK8_pt;   //!
   // TBranch        *b_Generator_id1;   //!
   // TBranch        *b_Generator_id2;   //!
   // TBranch        *b_Generator_binvar;   //!
   // TBranch        *b_Generator_scalePDF;   //!
   // TBranch        *b_Generator_weight;   //!
   // TBranch        *b_Generator_x1;   //!
   // TBranch        *b_Generator_x2;   //!
   // TBranch        *b_Generator_xpdf1;   //!
   // TBranch        *b_Generator_xpdf2;   //!
   // TBranch        *b_GenVtx_x;   //!
   // TBranch        *b_GenVtx_y;   //!
   // TBranch        *b_GenVtx_z;   //!
   // TBranch        *b_nGenVisTau;   //!
   // TBranch        *b_GenVisTau_status;   //!
   // TBranch        *b_GenVisTau_charge;   //!
   // TBranch        *b_GenVisTau_genPartIdxMother;   //!
   // TBranch        *b_GenVisTau_eta;   //!
   // TBranch        *b_GenVisTau_mass;   //!
   // TBranch        *b_GenVisTau_phi;   //!
   // TBranch        *b_GenVisTau_pt;   //!
   TBranch        *b_genWeight;   //!
   // TBranch        *b_LHEWeight_originalXWGTUP;   //!
   // TBranch        *b_nLHEPdfWeight;   //!
   // TBranch        *b_LHEPdfWeight;   //!
   // TBranch        *b_nLHEReweightingWeight;   //!
   // TBranch        *b_LHEReweightingWeight;   //!
   // TBranch        *b_nLHEScaleWeight;   //!
   // TBranch        *b_LHEScaleWeight;   //!
   // TBranch        *b_nPSWeight;   //!
   // TBranch        *b_PSWeight;   //!
   // TBranch        *b_nIsoTrack;   //!
   // TBranch        *b_IsoTrack_isHighPurityTrack;   //!
   // TBranch        *b_IsoTrack_isPFcand;   //!
   // TBranch        *b_IsoTrack_isFromLostTrack;   //!
   // TBranch        *b_IsoTrack_charge;   //!
   // TBranch        *b_IsoTrack_fromPV;   //!
   // TBranch        *b_IsoTrack_pdgId;   //!
   // TBranch        *b_IsoTrack_dxy;   //!
   // TBranch        *b_IsoTrack_dz;   //!
   // TBranch        *b_IsoTrack_eta;   //!
   // TBranch        *b_IsoTrack_pfRelIso03_all;   //!
   // TBranch        *b_IsoTrack_pfRelIso03_chg;   //!
   // TBranch        *b_IsoTrack_phi;   //!
   // TBranch        *b_IsoTrack_pt;   //!
   // TBranch        *b_IsoTrack_miniPFRelIso_all;   //!
   // TBranch        *b_IsoTrack_miniPFRelIso_chg;   //!
   TBranch        *b_nJet;   //!
   TBranch        *b_Jet_jetId;   //!
   TBranch        *b_Jet_chMultiplicity;   //!
   TBranch        *b_Jet_neMultiplicity;   //!
   TBranch        *b_Jet_nConstituents;   //!
   TBranch        *b_Jet_nElectrons;   //!
   TBranch        *b_Jet_nMuons;   //!
   TBranch        *b_Jet_nSVs;   //!
   TBranch        *b_Jet_electronIdx1;   //!
   TBranch        *b_Jet_electronIdx2;   //!
   TBranch        *b_Jet_muonIdx1;   //!
   TBranch        *b_Jet_muonIdx2;   //!
   TBranch        *b_Jet_svIdx1;   //!
   TBranch        *b_Jet_svIdx2;   //!
   TBranch        *b_Jet_hfadjacentEtaStripsSize;   //!
   TBranch        *b_Jet_hfcentralEtaStripSize;   //!
   TBranch        *b_Jet_PNetRegPtRawCorr;   //!
   TBranch        *b_Jet_PNetRegPtRawCorrNeutrino;   //!
   TBranch        *b_Jet_PNetRegPtRawRes;   //!
   TBranch        *b_Jet_area;   //!
   TBranch        *b_Jet_btagDeepFlavB;   //!
   TBranch        *b_Jet_btagDeepFlavCvB;   //!
   TBranch        *b_Jet_btagDeepFlavCvL;   //!
   TBranch        *b_Jet_btagDeepFlavQG;   //!
   TBranch        *b_Jet_btagPNetB;   //!
   TBranch        *b_Jet_btagPNetCvB;   //!
   TBranch        *b_Jet_btagPNetCvL;   //!
   TBranch        *b_Jet_btagPNetQvG;   //!
   TBranch        *b_Jet_btagPNetTauVJet;   //!
   //TBranch        *b_Jet_btagRobustParTAK4B;   //!
   //TBranch        *b_Jet_btagRobustParTAK4CvB;   //!
   //TBranch        *b_Jet_btagRobustParTAK4CvL;   //!
   //TBranch        *b_Jet_btagRobustParTAK4QG;   //!
   TBranch        *b_Jet_chEmEF;   //!
   TBranch        *b_Jet_chHEF;   //!
   TBranch        *b_Jet_eta;   //!
   TBranch        *b_Jet_hfsigmaEtaEta;   //!
   TBranch        *b_Jet_hfsigmaPhiPhi;   //!
   TBranch        *b_Jet_mass;   //!
   TBranch        *b_Jet_muEF;   //!
   TBranch        *b_Jet_muonSubtrFactor;   //!
   TBranch        *b_Jet_neEmEF;   //!
   TBranch        *b_Jet_neHEF;   //!
   TBranch        *b_Jet_phi;   //!
   TBranch        *b_Jet_pt;   //!
   TBranch        *b_Jet_rawFactor;   //!
   // TBranch        *b_LHE_Njets;   //!
   // TBranch        *b_LHE_Nb;   //!
   // TBranch        *b_LHE_Nc;   //!
   // TBranch        *b_LHE_Nuds;   //!
   // TBranch        *b_LHE_Nglu;   //!
   // TBranch        *b_LHE_NpNLO;   //!
   // TBranch        *b_LHE_NpLO;   //!
   // TBranch        *b_LHE_HT;   //!
   // TBranch        *b_LHE_HTIncoming;   //!
   // TBranch        *b_LHE_Vpt;   //!
   // TBranch        *b_LHE_AlphaS;   //!
   // TBranch        *b_nLHEPart;   //!
   // TBranch        *b_LHEPart_pdgId;   //!
   // TBranch        *b_LHEPart_status;   //!
   // TBranch        *b_LHEPart_spin;   //!
   // TBranch        *b_LHEPart_pt;   //!
   // TBranch        *b_LHEPart_eta;   //!
   // TBranch        *b_LHEPart_phi;   //!
   // TBranch        *b_LHEPart_mass;   //!
   // TBranch        *b_LHEPart_incomingpz;   //!
   // TBranch        *b_nLowPtElectron;   //!
   // TBranch        *b_LowPtElectron_convVeto;   //!
   // TBranch        *b_LowPtElectron_convWP;   //!
   // TBranch        *b_LowPtElectron_lostHits;   //!
   // TBranch        *b_LowPtElectron_electronIdx;   //!
   // TBranch        *b_LowPtElectron_photonIdx;   //!
   // TBranch        *b_LowPtElectron_charge;   //!
   // TBranch        *b_LowPtElectron_pdgId;   //!
   // TBranch        *b_LowPtElectron_ID;   //!
   // TBranch        *b_LowPtElectron_convVtxRadius;   //!
   // TBranch        *b_LowPtElectron_deltaEtaSC;   //!
   // TBranch        *b_LowPtElectron_dxy;   //!
   // TBranch        *b_LowPtElectron_dxyErr;   //!
   // TBranch        *b_LowPtElectron_dz;   //!
   // TBranch        *b_LowPtElectron_dzErr;   //!
   // TBranch        *b_LowPtElectron_eInvMinusPInv;   //!
   // TBranch        *b_LowPtElectron_energyErr;   //!
   // TBranch        *b_LowPtElectron_eta;   //!
   // TBranch        *b_LowPtElectron_hoe;   //!
   // TBranch        *b_LowPtElectron_mass;   //!
   // TBranch        *b_LowPtElectron_miniPFRelIso_all;   //!
   // TBranch        *b_LowPtElectron_miniPFRelIso_chg;   //!
   // TBranch        *b_LowPtElectron_phi;   //!
   // TBranch        *b_LowPtElectron_pt;   //!
   // TBranch        *b_LowPtElectron_ptbiased;   //!
   // TBranch        *b_LowPtElectron_r9;   //!
   // TBranch        *b_LowPtElectron_scEtOverPt;   //!
   // TBranch        *b_LowPtElectron_sieie;   //!
   // TBranch        *b_LowPtElectron_unbiased;   //!
   TBranch        *b_GenMET_phi;   //!
   TBranch        *b_GenMET_pt;   //!
   //TBranch        *b_MET_MetUnclustEnUpDeltaX;   //!
   //TBranch        *b_MET_MetUnclustEnUpDeltaY;   //!
   //TBranch        *b_MET_covXX;   //!
   //TBranch        *b_MET_covXY;   //!
   //TBranch        *b_MET_covYY;   //!
   // TBranch        *b_MET_phi;   //!
   // TBranch        *b_MET_pt;   //!
   //TBranch        *b_MET_significance;   //!
   // TBranch        *b_MET_sumEt;   //!
   //TBranch        *b_MET_sumPtUnclustered;   //!
   TBranch        *b_nMuon;   //!
   TBranch        *b_Muon_highPtId;   //!
   TBranch        *b_Muon_highPurity;   //!
   TBranch        *b_Muon_inTimeMuon;   //!
   TBranch        *b_Muon_isGlobal;   //!
   TBranch        *b_Muon_isPFcand;   //!
   TBranch        *b_Muon_isStandalone;   //!
   TBranch        *b_Muon_isTracker;   //!
   TBranch        *b_Muon_jetNDauCharged;   //!
   TBranch        *b_Muon_looseId;   //!
   TBranch        *b_Muon_mediumId;   //!
   TBranch        *b_Muon_mediumPromptId;   //!
   TBranch        *b_Muon_miniIsoId;   //!
   TBranch        *b_Muon_multiIsoId;   //!
   TBranch        *b_Muon_mvaMuID_WP;   //!
   TBranch        *b_Muon_nStations;   //!
   TBranch        *b_Muon_nTrackerLayers;   //!
   TBranch        *b_Muon_pfIsoId;   //!
   TBranch        *b_Muon_puppiIsoId;   //!
   TBranch        *b_Muon_softId;   //!
   TBranch        *b_Muon_softMvaId;   //!
   TBranch        *b_Muon_tightCharge;   //!
   TBranch        *b_Muon_tightId;   //!
   TBranch        *b_Muon_tkIsoId;   //!
   TBranch        *b_Muon_triggerIdLoose;   //!
   TBranch        *b_Muon_jetIdx;   //!
   TBranch        *b_Muon_svIdx;   //!
   // TBranch        *b_Muon_fsrPhotonIdx;   //!
   TBranch        *b_Muon_charge;   //!
   TBranch        *b_Muon_pdgId;   //!
   TBranch        *b_Muon_dxy;   //!
   TBranch        *b_Muon_dxyErr;   //!
   TBranch        *b_Muon_dxybs;   //!
   TBranch        *b_Muon_dz;   //!
   TBranch        *b_Muon_dzErr;   //!
   TBranch        *b_Muon_eta;   //!
   TBranch        *b_Muon_ip3d;   //!
   TBranch        *b_Muon_jetPtRelv2;   //!
   TBranch        *b_Muon_jetRelIso;   //!
   TBranch        *b_Muon_mass;   //!
   TBranch        *b_Muon_miniPFRelIso_all;   //!
   TBranch        *b_Muon_miniPFRelIso_chg;   //!
   TBranch        *b_Muon_mvaMuID;   //!
   TBranch        *b_Muon_pfRelIso03_all;   //!
   TBranch        *b_Muon_pfRelIso03_chg;   //!
   TBranch        *b_Muon_pfRelIso04_all;   //!
   TBranch        *b_Muon_phi;   //!
   TBranch        *b_Muon_pt;   //!
   TBranch        *b_Muon_ptErr;   //!
   TBranch        *b_Muon_segmentComp;   //!
   TBranch        *b_Muon_sip3d;   //!
   TBranch        *b_Muon_softMva;   //!
   TBranch        *b_Muon_tkRelIso;   //!
   TBranch        *b_Muon_tunepRelPt;   //!
   TBranch        *b_Muon_bsConstrainedChi2;   //!
   TBranch        *b_Muon_bsConstrainedPt;   //!
   TBranch        *b_Muon_bsConstrainedPtErr;   //!
   // TBranch        *b_Muon_mvaLowPt;   //!
   //TBranch        *b_Muon_mvaTTH;   //!
   // TBranch        *b_nPhoton;   //!
   // TBranch        *b_Photon_seediEtaOriX;   //!
   // TBranch        *b_Photon_cutBased;   //!
   // TBranch        *b_Photon_electronVeto;   //!
   // TBranch        *b_Photon_hasConversionTracks;   //!
   // TBranch        *b_Photon_isScEtaEB;   //!
   // TBranch        *b_Photon_isScEtaEE;   //!
   // TBranch        *b_Photon_mvaID_WP80;   //!
   // TBranch        *b_Photon_mvaID_WP90;   //!
   // TBranch        *b_Photon_pixelSeed;   //!
   // TBranch        *b_Photon_seedGain;   //!
   // TBranch        *b_Photon_electronIdx;   //!
   // TBranch        *b_Photon_jetIdx;   //!
   // TBranch        *b_Photon_seediPhiOriY;   //!
   // TBranch        *b_Photon_vidNestedWPBitmap;   //!
   // TBranch        *b_Photon_ecalPFClusterIso;   //!
   // TBranch        *b_Photon_energyErr;   //!
   // TBranch        *b_Photon_energyRaw;   //!
   // TBranch        *b_Photon_esEffSigmaRR;   //!
   // TBranch        *b_Photon_esEnergyOverRawE;   //!
   // TBranch        *b_Photon_eta;   //!
   // TBranch        *b_Photon_etaWidth;   //!
   // TBranch        *b_Photon_haloTaggerMVAVal;   //!
   // TBranch        *b_Photon_hcalPFClusterIso;   //!
   // TBranch        *b_Photon_hoe;   //!
   // TBranch        *b_Photon_hoe_PUcorr;   //!
   // TBranch        *b_Photon_mvaID;   //!
   // TBranch        *b_Photon_pfChargedIso;   //!
   // TBranch        *b_Photon_pfChargedIsoPFPV;   //!
   // TBranch        *b_Photon_pfChargedIsoWorstVtx;   //!
   // TBranch        *b_Photon_pfPhoIso03;   //!
   // TBranch        *b_Photon_pfRelIso03_all_quadratic;   //!
   // TBranch        *b_Photon_pfRelIso03_chg_quadratic;   //!
   // TBranch        *b_Photon_phi;   //!
   // TBranch        *b_Photon_phiWidth;   //!
   // TBranch        *b_Photon_pt;   //!
   // TBranch        *b_Photon_r9;   //!
   // TBranch        *b_Photon_s4;   //!
   // TBranch        *b_Photon_sieie;   //!
   // TBranch        *b_Photon_sieip;   //!
   // TBranch        *b_Photon_sipip;   //!
   // TBranch        *b_Photon_trkSumPtHollowConeDR03;   //!
   // TBranch        *b_Photon_trkSumPtSolidConeDR04;   //!
   // TBranch        *b_Photon_x_calo;   //!
   // TBranch        *b_Photon_y_calo;   //!
   // TBranch        *b_Photon_z_calo;   //!
   TBranch        *b_Pileup_nPU;   //!
   TBranch        *b_Pileup_sumEOOT;   //!
   TBranch        *b_Pileup_sumLOOT;   //!
   TBranch        *b_Pileup_nTrueInt;   //!
   TBranch        *b_Pileup_pudensity;   //!
   TBranch        *b_Pileup_gpudensity;   //!
   TBranch        *b_PuppiMET_phi;   //!
   //TBranch        *b_PuppiMET_phiJERDown;   //!
   //TBranch        *b_PuppiMET_phiJERUp;   //!
   //TBranch        *b_PuppiMET_phiJESDown;   //!
   //TBranch        *b_PuppiMET_phiJESUp;   //!
   TBranch        *b_PuppiMET_phiUnclusteredDown;   //!
   TBranch        *b_PuppiMET_phiUnclusteredUp;   //!
   TBranch        *b_PuppiMET_pt;   //!
   //TBranch        *b_PuppiMET_ptJERDown;   //!
   //TBranch        *b_PuppiMET_ptJERUp;   //!
   //TBranch        *b_PuppiMET_ptJESDown;   //!
   //TBranch        *b_PuppiMET_ptJESUp;   //!
   TBranch        *b_PuppiMET_ptUnclusteredDown;   //!
   TBranch        *b_PuppiMET_ptUnclusteredUp;   //!
   TBranch        *b_PuppiMET_sumEt;   //!
   //TBranch        *b_RawMET_phi;   //!
   //TBranch        *b_RawMET_pt;   //!
   //TBranch        *b_RawMET_sumEt;   //!
   TBranch        *b_RawPuppiMET_phi;   //!
   TBranch        *b_RawPuppiMET_pt;   //!
   TBranch        *b_RawPuppiMET_sumEt;   //!
   TBranch        *b_Rho_fixedGridRhoAll;   //!
   TBranch        *b_Rho_fixedGridRhoFastjetAll;   //!
   TBranch        *b_Rho_fixedGridRhoFastjetCentral;   //!
   TBranch        *b_Rho_fixedGridRhoFastjetCentralCalo;   //!
   TBranch        *b_Rho_fixedGridRhoFastjetCentralChargedPileUp;   //!
   TBranch        *b_Rho_fixedGridRhoFastjetCentralNeutral;   //!
   TBranch        *b_nGenDressedLepton;   //!
   TBranch        *b_GenDressedLepton_hasTauAnc;   //!
   TBranch        *b_GenDressedLepton_pdgId;   //!
   TBranch        *b_GenDressedLepton_eta;   //!
   TBranch        *b_GenDressedLepton_mass;   //!
   TBranch        *b_GenDressedLepton_phi;   //!
   TBranch        *b_GenDressedLepton_pt;   //!
   // TBranch        *b_nGenIsolatedPhoton;   //!
   // TBranch        *b_GenIsolatedPhoton_eta;   //!
   // TBranch        *b_GenIsolatedPhoton_mass;   //!
   // TBranch        *b_GenIsolatedPhoton_phi;   //!
   // TBranch        *b_GenIsolatedPhoton_pt;   //!
   TBranch        *b_nSoftActivityJet;   //!
   TBranch        *b_SoftActivityJet_eta;   //!
   TBranch        *b_SoftActivityJet_phi;   //!
   TBranch        *b_SoftActivityJet_pt;   //!
   TBranch        *b_SoftActivityJetNjets10;   //!
   TBranch        *b_SoftActivityJetNjets2;   //!
   TBranch        *b_SoftActivityJetNjets5;   //!
   TBranch        *b_SoftActivityJetHT;   //!
   TBranch        *b_SoftActivityJetHT10;   //!
   TBranch        *b_SoftActivityJetHT2;   //!
   TBranch        *b_SoftActivityJetHT5;   //!
   TBranch        *b_nSubJet;   //!
   //TBranch        *b_SubJet_btagDeepB;   //!
   TBranch        *b_SubJet_eta;   //!
   TBranch        *b_SubJet_mass;   //!
   TBranch        *b_SubJet_n2b1;   //!
   TBranch        *b_SubJet_n3b1;   //!
   TBranch        *b_SubJet_phi;   //!
   TBranch        *b_SubJet_pt;   //!
   TBranch        *b_SubJet_rawFactor;   //!
   TBranch        *b_SubJet_tau1;   //!
   TBranch        *b_SubJet_tau2;   //!
   TBranch        *b_SubJet_tau3;   //!
   TBranch        *b_SubJet_tau4;   //!
   TBranch        *b_nTau;   //!
   TBranch        *b_Tau_decayMode;   //!
   TBranch        *b_Tau_idAntiEleDeadECal;   //!
   TBranch        *b_Tau_idAntiMu;   //!
   TBranch        *b_Tau_idDecayModeNewDMs;   //!
   TBranch        *b_Tau_idDecayModeOldDMs;   //!
   //TBranch        *b_Tau_idDeepTau2017v2p1VSe;   //!
   //TBranch        *b_Tau_idDeepTau2017v2p1VSjet;   //!
   //TBranch        *b_Tau_idDeepTau2017v2p1VSmu;   //!
   //TBranch        *b_Tau_idDeepTau2018v2p5VSe;   //!
   //TBranch        *b_Tau_idDeepTau2018v2p5VSjet;   //!
   //TBranch        *b_Tau_idDeepTau2018v2p5VSmu;   //!
   TBranch        *b_Tau_nSVs;   //!
   TBranch        *b_Tau_charge;   //!
   TBranch        *b_Tau_decayModePNet;   //!
   TBranch        *b_Tau_eleIdx;   //!
   TBranch        *b_Tau_jetIdx;   //!
   TBranch        *b_Tau_muIdx;   //!
   TBranch        *b_Tau_svIdx1;   //!
   TBranch        *b_Tau_svIdx2;   //!
   TBranch        *b_Tau_chargedIso;   //!
   TBranch        *b_Tau_dxy;   //!
   TBranch        *b_Tau_dz;   //!
   TBranch        *b_Tau_eta;   //!
   TBranch        *b_Tau_leadTkDeltaEta;   //!
   TBranch        *b_Tau_leadTkDeltaPhi;   //!
   TBranch        *b_Tau_leadTkPtOverTauPt;   //!
   TBranch        *b_Tau_mass;   //!
   TBranch        *b_Tau_neutralIso;   //!
   TBranch        *b_Tau_phi;   //!
   // TBranch        *b_Tau_photonsOutsideSignalCone;   //!
   TBranch        *b_Tau_probDM0PNet;   //!
   TBranch        *b_Tau_probDM10PNet;   //!
   TBranch        *b_Tau_probDM11PNet;   //!
   TBranch        *b_Tau_probDM1PNet;   //!
   TBranch        *b_Tau_probDM2PNet;   //!
   TBranch        *b_Tau_pt;   //!
   TBranch        *b_Tau_ptCorrPNet;   //!
   TBranch        *b_Tau_puCorr;   //!
   TBranch        *b_Tau_qConfPNet;   //!
   //TBranch        *b_Tau_rawDeepTau2017v2p1VSe;   //!
   //TBranch        *b_Tau_rawDeepTau2017v2p1VSjet;   //!
   //TBranch        *b_Tau_rawDeepTau2017v2p1VSmu;   //!
   //TBranch        *b_Tau_rawDeepTau2018v2p5VSe;   //!
   //TBranch        *b_Tau_rawDeepTau2018v2p5VSjet;   //!
   //TBranch        *b_Tau_rawDeepTau2018v2p5VSmu;   //!
   TBranch        *b_Tau_rawIso;   //!
   // TBranch        *b_Tau_rawIsodR03;   //!
   TBranch        *b_Tau_rawPNetVSe;   //!
   TBranch        *b_Tau_rawPNetVSjet;   //!
   TBranch        *b_Tau_rawPNetVSmu;   //!
   //TBranch        *b_TkMET_phi;   //!
   //TBranch        *b_TkMET_pt;   //!
   //TBranch        *b_TkMET_sumEt;   //!
   TBranch        *b_nTrigObj;   //!
   TBranch        *b_TrigObj_l1charge;   //!
   TBranch        *b_TrigObj_id;   //!
   TBranch        *b_TrigObj_l1iso;   //!
   TBranch        *b_TrigObj_filterBits;   //!
   TBranch        *b_TrigObj_pt;   //!
   TBranch        *b_TrigObj_eta;   //!
   TBranch        *b_TrigObj_phi;   //!
   TBranch        *b_TrigObj_l1pt;   //!
   TBranch        *b_TrigObj_l1pt_2;   //!
   TBranch        *b_TrigObj_l2pt;   //!
   TBranch        *b_genTtbarId;   //!
   TBranch        *b_nOtherPV;   //!
   TBranch        *b_OtherPV_z;   //!
   TBranch        *b_OtherPV_score;   //!
   TBranch        *b_PV_npvs;   //!
   TBranch        *b_PV_npvsGood;   //!
   TBranch        *b_PV_ndof;   //!
   TBranch        *b_PV_x;   //!
   TBranch        *b_PV_y;   //!
   TBranch        *b_PV_z;   //!
   TBranch        *b_PV_chi2;   //!
   TBranch        *b_PV_score;   //!
   TBranch        *b_nSV;   //!
   TBranch        *b_SV_charge;   //!
   TBranch        *b_SV_dlen;   //!
   TBranch        *b_SV_dlenSig;   //!
   TBranch        *b_SV_dxy;   //!
   TBranch        *b_SV_dxySig;   //!
   TBranch        *b_SV_pAngle;   //!
   // TBranch        *b_boostedTau_genPartFlav;   //!
   // TBranch        *b_boostedTau_genPartIdx;   //!
   TBranch        *b_Electron_genPartFlav;   //!
   TBranch        *b_Electron_genPartIdx;   //!
   TBranch        *b_FatJet_hadronFlavour;   //!
   //TBranch        *b_FatJet_nBHadrons;   //!
   //TBranch        *b_FatJet_nCHadrons;   //!
   // TBranch        *b_FatJet_genJetAK8Idx;   //!
   // TBranch        *b_GenJetAK8_hadronFlavour;   //!
   // TBranch        *b_GenJetAK8_partonFlavour;   //!
   TBranch        *b_GenJet_hadronFlavour;   //!
   TBranch        *b_GenJet_partonFlavour;   //!
   // TBranch        *b_GenVtx_t0;   //!
   TBranch        *b_Jet_hadronFlavour;   //!
   TBranch        *b_Jet_genJetIdx;   //!
   TBranch        *b_Jet_partonFlavour;   //!
   // TBranch        *b_LowPtElectron_genPartFlav;   //!
   // TBranch        *b_LowPtElectron_genPartIdx;   //!
   TBranch        *b_Muon_genPartFlav;   //!
   TBranch        *b_Muon_genPartIdx;   //!
   // TBranch        *b_Photon_genPartFlav;   //!
   // TBranch        *b_Photon_genPartIdx;   //!
   //TBranch        *b_MET_fiducialGenPhi;   //!
   //TBranch        *b_MET_fiducialGenPt;   //!
   TBranch        *b_SubJet_hadronFlavour;   //!
   TBranch        *b_SubJet_nBHadrons;   //!
   TBranch        *b_SubJet_nCHadrons;   //!
   TBranch        *b_SV_ntracks;   //!
   TBranch        *b_SV_chi2;   //!
   TBranch        *b_SV_eta;   //!
   TBranch        *b_SV_mass;   //!
   TBranch        *b_SV_ndof;   //!
   TBranch        *b_SV_phi;   //!
   TBranch        *b_SV_pt;   //!
   TBranch        *b_SV_x;   //!
   TBranch        *b_SV_y;   //!
   TBranch        *b_SV_z;   //!
   TBranch        *b_Tau_genPartFlav;   //!
   TBranch        *b_Tau_genPartIdx;   //!
   // TBranch        *b_L1_AlwaysTrue;   //!
   // TBranch        *b_L1_BPTX_AND_Ref1_VME;   //!
   // TBranch        *b_L1_BPTX_AND_Ref3_VME;   //!
   // TBranch        *b_L1_BPTX_AND_Ref4_VME;   //!
   // TBranch        *b_L1_BPTX_BeamGas_B1_VME;   //!
   // TBranch        *b_L1_BPTX_BeamGas_B2_VME;   //!
   // TBranch        *b_L1_BPTX_BeamGas_Ref1_VME;   //!
   // TBranch        *b_L1_BPTX_BeamGas_Ref2_VME;   //!
   // TBranch        *b_L1_BPTX_NotOR_VME;   //!
   // TBranch        *b_L1_BPTX_OR_Ref3_VME;   //!
   // TBranch        *b_L1_BPTX_OR_Ref4_VME;   //!
   // TBranch        *b_L1_BPTX_RefAND_VME;   //!
   // TBranch        *b_L1_BptxMinus;   //!
   // TBranch        *b_L1_BptxOR;   //!
   // TBranch        *b_L1_BptxPlus;   //!
   // TBranch        *b_L1_BptxXOR;   //!
   // TBranch        *b_L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142;   //!
   // TBranch        *b_L1_DoubleEG10_er1p2_dR_Max0p6;   //!
   // TBranch        *b_L1_DoubleEG10p5_er1p2_dR_Max0p6;   //!
   // TBranch        *b_L1_DoubleEG11_er1p2_dR_Max0p6;   //!
   // TBranch        *b_L1_DoubleEG4_er1p2_dR_Max0p9;   //!
   // TBranch        *b_L1_DoubleEG4p5_er1p2_dR_Max0p9;   //!
   // TBranch        *b_L1_DoubleEG5_er1p2_dR_Max0p9;   //!
   // TBranch        *b_L1_DoubleEG5p5_er1p2_dR_Max0p8;   //!
   // TBranch        *b_L1_DoubleEG6_er1p2_dR_Max0p8;   //!
   // TBranch        *b_L1_DoubleEG6p5_er1p2_dR_Max0p8;   //!
   // TBranch        *b_L1_DoubleEG7_er1p2_dR_Max0p8;   //!
   // TBranch        *b_L1_DoubleEG7p5_er1p2_dR_Max0p7;   //!
   // TBranch        *b_L1_DoubleEG8_er1p2_dR_Max0p7;   //!
   // TBranch        *b_L1_DoubleEG8er2p5_HTT260er;   //!
   // TBranch        *b_L1_DoubleEG8er2p5_HTT280er;   //!
   // TBranch        *b_L1_DoubleEG8er2p5_HTT300er;   //!
   // TBranch        *b_L1_DoubleEG8er2p5_HTT320er;   //!
   // TBranch        *b_L1_DoubleEG8er2p5_HTT340er;   //!
   // TBranch        *b_L1_DoubleEG8p5_er1p2_dR_Max0p7;   //!
   // TBranch        *b_L1_DoubleEG9_er1p2_dR_Max0p7;   //!
   // TBranch        *b_L1_DoubleEG9p5_er1p2_dR_Max0p6;   //!
   // TBranch        *b_L1_DoubleEG_15_10_er2p5;   //!
   // TBranch        *b_L1_DoubleEG_20_10_er2p5;   //!
   // TBranch        *b_L1_DoubleEG_22_10_er2p5;   //!
   // TBranch        *b_L1_DoubleEG_25_12_er2p5;   //!
   // TBranch        *b_L1_DoubleEG_25_14_er2p5;   //!
   // TBranch        *b_L1_DoubleEG_27_14_er2p5;   //!
   // TBranch        *b_L1_DoubleEG_LooseIso16_LooseIso12_er1p5;   //!
   // TBranch        *b_L1_DoubleEG_LooseIso18_LooseIso12_er1p5;   //!
   // TBranch        *b_L1_DoubleEG_LooseIso20_10_er2p5;   //!
   // TBranch        *b_L1_DoubleEG_LooseIso20_LooseIso12_er1p5;   //!
   // TBranch        *b_L1_DoubleEG_LooseIso22_10_er2p5;   //!
   // TBranch        *b_L1_DoubleEG_LooseIso22_12_er2p5;   //!
   // TBranch        *b_L1_DoubleEG_LooseIso22_LooseIso12_er1p5;   //!
   // TBranch        *b_L1_DoubleEG_LooseIso25_12_er2p5;   //!
   // TBranch        *b_L1_DoubleEG_LooseIso25_LooseIso12_er1p5;   //!
   // TBranch        *b_L1_DoubleIsoTau26er2p1_Jet55_RmOvlp_dR0p5;   //!
   // TBranch        *b_L1_DoubleIsoTau26er2p1_Jet70_RmOvlp_dR0p5;   //!
   // TBranch        *b_L1_DoubleIsoTau28er2p1;   //!
   // TBranch        *b_L1_DoubleIsoTau28er2p1_Mass_Max80;   //!
   // TBranch        *b_L1_DoubleIsoTau28er2p1_Mass_Max90;   //!
   // TBranch        *b_L1_DoubleIsoTau30er2p1;   //!
   // TBranch        *b_L1_DoubleIsoTau30er2p1_Mass_Max80;   //!
   // TBranch        *b_L1_DoubleIsoTau30er2p1_Mass_Max90;   //!
   // TBranch        *b_L1_DoubleIsoTau32er2p1;   //!
   // TBranch        *b_L1_DoubleIsoTau34er2p1;   //!
   // TBranch        *b_L1_DoubleIsoTau35er2p1;   //!
   // TBranch        *b_L1_DoubleIsoTau36er2p1;   //!
   // TBranch        *b_L1_DoubleJet100er2p3_dEta_Max1p6;   //!
   // TBranch        *b_L1_DoubleJet100er2p5;   //!
   // TBranch        *b_L1_DoubleJet112er2p3_dEta_Max1p6;   //!
   // TBranch        *b_L1_DoubleJet120er2p5;   //!
   // TBranch        *b_L1_DoubleJet150er2p5;   //!
   // TBranch        *b_L1_DoubleJet30er2p5_Mass_Min150_dEta_Max1p5;   //!
   // TBranch        *b_L1_DoubleJet30er2p5_Mass_Min200_dEta_Max1p5;   //!
   // TBranch        *b_L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5;   //!
   // TBranch        *b_L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5;   //!
   // TBranch        *b_L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5;   //!
   // TBranch        *b_L1_DoubleJet30er2p5_Mass_Min360_dEta_Max1p5;   //!
   // TBranch        *b_L1_DoubleJet35_Mass_Min450_IsoTau45_RmOvlp;   //!
   // TBranch        *b_L1_DoubleJet35_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5;   //!
   // TBranch        *b_L1_DoubleJet40er2p5;   //!
   // TBranch        *b_L1_DoubleJet_100_30_DoubleJet30_Mass_Min620;   //!
   // TBranch        *b_L1_DoubleJet_110_35_DoubleJet35_Mass_Min620;   //!
   // TBranch        *b_L1_DoubleJet_115_40_DoubleJet40_Mass_Min620;   //!
   // TBranch        *b_L1_DoubleJet_115_40_DoubleJet40_Mass_Min620_Jet60TT28;   //!
   // TBranch        *b_L1_DoubleJet_120_45_DoubleJet45_Mass_Min620;   //!
   // TBranch        *b_L1_DoubleJet_120_45_DoubleJet45_Mass_Min620_Jet60TT28;   //!
   // TBranch        *b_L1_DoubleJet_80_30_Mass_Min420_DoubleMu0_SQ;   //!
   // TBranch        *b_L1_DoubleJet_80_30_Mass_Min420_IsoTau40_RmOvlp;   //!
   // TBranch        *b_L1_DoubleJet_80_30_Mass_Min420_Mu8;   //!
   // TBranch        *b_L1_DoubleJet_90_30_DoubleJet30_Mass_Min620;   //!
   // TBranch        *b_L1_DoubleLLPJet40;   //!
   // TBranch        *b_L1_DoubleLooseIsoEG22er2p1;   //!
   // TBranch        *b_L1_DoubleLooseIsoEG24er2p1;   //!
   // TBranch        *b_L1_DoubleMu0;   //!
   // TBranch        *b_L1_DoubleMu0_Mass_Min1;   //!
   // TBranch        *b_L1_DoubleMu0_OQ;   //!
   // TBranch        *b_L1_DoubleMu0_SQ;   //!
   // TBranch        *b_L1_DoubleMu0_SQ_OS;   //!
   // TBranch        *b_L1_DoubleMu0_Upt15_Upt7;   //!
   // TBranch        *b_L1_DoubleMu0_Upt5_Upt5;   //!
   // TBranch        *b_L1_DoubleMu0_Upt6_IP_Min1_Upt4;   //!
   // TBranch        *b_L1_DoubleMu0_dR_Max1p6_Jet90er2p5_dR_Max0p8;   //!
   // TBranch        *b_L1_DoubleMu0er1p4_OQ_OS_dEta_Max1p6;   //!
   // TBranch        *b_L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4;   //!
   // TBranch        *b_L1_DoubleMu0er1p5_SQ;   //!
   // TBranch        *b_L1_DoubleMu0er1p5_SQ_OS;   //!
   // TBranch        *b_L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4;   //!
   // TBranch        *b_L1_DoubleMu0er1p5_SQ_dR_Max1p4;   //!
   // TBranch        *b_L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p5;   //!
   // TBranch        *b_L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p6;   //!
   // TBranch        *b_L1_DoubleMu0er2p0_SQ_OS_dR_Max1p4;   //!
   // TBranch        *b_L1_DoubleMu0er2p0_SQ_dEta_Max1p5;   //!
   // TBranch        *b_L1_DoubleMu0er2p0_SQ_dEta_Max1p6;   //!
   // TBranch        *b_L1_DoubleMu0er2p0_SQ_dR_Max1p4;   //!
   // TBranch        *b_L1_DoubleMu18er2p1_SQ;   //!
   // TBranch        *b_L1_DoubleMu3_OS_er2p3_Mass_Max14_DoubleEG7p5_er2p1_Mass_Max20;   //!
   // TBranch        *b_L1_DoubleMu3_SQ_ETMHF30_HTT60er;   //!
   // TBranch        *b_L1_DoubleMu3_SQ_ETMHF30_Jet60er2p5_OR_DoubleJet40er2p5;   //!
   // TBranch        *b_L1_DoubleMu3_SQ_ETMHF40_HTT60er;   //!
   // TBranch        *b_L1_DoubleMu3_SQ_ETMHF40_Jet60er2p5_OR_DoubleJet40er2p5;   //!
   // TBranch        *b_L1_DoubleMu3_SQ_ETMHF50_HTT60er;   //!
   // TBranch        *b_L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5;   //!
   // TBranch        *b_L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5_OR_DoubleJet40er2p5;   //!
   // TBranch        *b_L1_DoubleMu3_SQ_ETMHF60_Jet60er2p5;   //!
   // TBranch        *b_L1_DoubleMu3_SQ_HTT220er;   //!
   // TBranch        *b_L1_DoubleMu3_SQ_HTT240er;   //!
   // TBranch        *b_L1_DoubleMu3_SQ_HTT260er;   //!
   // TBranch        *b_L1_DoubleMu3_dR_Max1p6_Jet90er2p5_dR_Max0p8;   //!
   // TBranch        *b_L1_DoubleMu3er2p0_SQ_OS_dR_Max1p4;   //!
   // TBranch        *b_L1_DoubleMu4_SQ_EG9er2p5;   //!
   // TBranch        *b_L1_DoubleMu4_SQ_OS;   //!
   // TBranch        *b_L1_DoubleMu4_SQ_OS_dR_Max1p2;   //!
   // TBranch        *b_L1_DoubleMu4p5_SQ_OS;   //!
   // TBranch        *b_L1_DoubleMu4p5_SQ_OS_dR_Max1p2;   //!
   // TBranch        *b_L1_DoubleMu4p5er2p0_SQ_OS;   //!
   // TBranch        *b_L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18;   //!
   // TBranch        *b_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7;   //!
   // TBranch        *b_L1_DoubleMu5_OS_er2p3_Mass_8to14_DoubleEG3er2p1_Mass_Max20;   //!
   // TBranch        *b_L1_DoubleMu5_SQ_EG9er2p5;   //!
   // TBranch        *b_L1_DoubleMu8_SQ;   //!
   // TBranch        *b_L1_DoubleMu9_SQ;   //!
   // TBranch        *b_L1_DoubleMu_12_5;   //!
   // TBranch        *b_L1_DoubleMu_15_5_SQ;   //!
   // TBranch        *b_L1_DoubleMu_15_7;   //!
   // TBranch        *b_L1_DoubleMu_15_7_Mass_Min1;   //!
   // TBranch        *b_L1_DoubleMu_15_7_SQ;   //!
   // TBranch        *b_L1_DoubleTau70er2p1;   //!
   // TBranch        *b_L1_ETM120;   //!
   // TBranch        *b_L1_ETM150;   //!
   // TBranch        *b_L1_ETMHF100;   //!
   // TBranch        *b_L1_ETMHF100_HTT60er;   //!
   // TBranch        *b_L1_ETMHF110;   //!
   // TBranch        *b_L1_ETMHF110_HTT60er;   //!
   // TBranch        *b_L1_ETMHF110_HTT60er_NotSecondBunchInTrain;   //!
   // TBranch        *b_L1_ETMHF120;   //!
   // TBranch        *b_L1_ETMHF120_HTT60er;   //!
   // TBranch        *b_L1_ETMHF120_NotSecondBunchInTrain;   //!
   // TBranch        *b_L1_ETMHF130;   //!
   // TBranch        *b_L1_ETMHF130_HTT60er;   //!
   // TBranch        *b_L1_ETMHF140;   //!
   // TBranch        *b_L1_ETMHF150;   //!
   // TBranch        *b_L1_ETMHF70;   //!
   // TBranch        *b_L1_ETMHF70_HTT60er;   //!
   // TBranch        *b_L1_ETMHF80;   //!
   // TBranch        *b_L1_ETMHF80_HTT60er;   //!
   // TBranch        *b_L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p1;   //!
   // TBranch        *b_L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p6;   //!
   // TBranch        *b_L1_ETMHF90;   //!
   // TBranch        *b_L1_ETMHF90_HTT60er;   //!
   // TBranch        *b_L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p1;   //!
   // TBranch        *b_L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p6;   //!
   // TBranch        *b_L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p1;   //!
   // TBranch        *b_L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p6;   //!
   // TBranch        *b_L1_ETT1200;   //!
   // TBranch        *b_L1_ETT1600;   //!
   // TBranch        *b_L1_ETT2000;   //!
   // TBranch        *b_L1_FirstBunchAfterTrain;   //!
   // TBranch        *b_L1_FirstBunchBeforeTrain;   //!
   // TBranch        *b_L1_FirstBunchInTrain;   //!
   // TBranch        *b_L1_FirstCollisionInOrbit;   //!
   // TBranch        *b_L1_FirstCollisionInTrain;   //!
   // TBranch        *b_L1_HCAL_LaserMon_Trig;   //!
   // TBranch        *b_L1_HCAL_LaserMon_Veto;   //!
   // TBranch        *b_L1_HTT120_SingleLLPJet40;   //!
   // TBranch        *b_L1_HTT120er;   //!
   // TBranch        *b_L1_HTT160_SingleLLPJet50;   //!
   // TBranch        *b_L1_HTT160er;   //!
   // TBranch        *b_L1_HTT200_SingleLLPJet60;   //!
   // TBranch        *b_L1_HTT200er;   //!
   // TBranch        *b_L1_HTT240_SingleLLPJet70;   //!
   // TBranch        *b_L1_HTT255er;   //!
   // TBranch        *b_L1_HTT280er;   //!
   // TBranch        *b_L1_HTT280er_QuadJet_70_55_40_35_er2p5;   //!
   // TBranch        *b_L1_HTT320er;   //!
   // TBranch        *b_L1_HTT320er_QuadJet_70_55_40_40_er2p5;   //!
   // TBranch        *b_L1_HTT320er_QuadJet_80_60_er2p1_45_40_er2p3;   //!
   // TBranch        *b_L1_HTT320er_QuadJet_80_60_er2p1_50_45_er2p3;   //!
   // TBranch        *b_L1_HTT360er;   //!
   // TBranch        *b_L1_HTT400er;   //!
   // TBranch        *b_L1_HTT450er;   //!
   // TBranch        *b_L1_IsoEG32er2p5_Mt40;   //!
   // TBranch        *b_L1_IsoTau52er2p1_QuadJet36er2p5;   //!
   // TBranch        *b_L1_IsolatedBunch;   //!
   // TBranch        *b_L1_LastBunchInTrain;   //!
   // TBranch        *b_L1_LastCollisionInTrain;   //!
   // TBranch        *b_L1_LooseIsoEG22er2p1_IsoTau26er2p1_dR_Min0p3;   //!
   // TBranch        *b_L1_LooseIsoEG22er2p1_Tau70er2p1_dR_Min0p3;   //!
   // TBranch        *b_L1_LooseIsoEG24er2p1_HTT100er;   //!
   // TBranch        *b_L1_LooseIsoEG24er2p1_IsoTau27er2p1_dR_Min0p3;   //!
   // TBranch        *b_L1_LooseIsoEG26er2p1_HTT100er;   //!
   // TBranch        *b_L1_LooseIsoEG26er2p1_Jet34er2p5_dR_Min0p3;   //!
   // TBranch        *b_L1_LooseIsoEG28er2p1_HTT100er;   //!
   // TBranch        *b_L1_LooseIsoEG28er2p1_Jet34er2p5_dR_Min0p3;   //!
   // TBranch        *b_L1_LooseIsoEG30er2p1_HTT100er;   //!
   // TBranch        *b_L1_LooseIsoEG30er2p1_Jet34er2p5_dR_Min0p3;   //!
   // TBranch        *b_L1_MinimumBiasHF0;   //!
   // TBranch        *b_L1_MinimumBiasHF0_AND_BptxAND;   //!
   // TBranch        *b_L1_Mu10er2p3_Jet32er2p3_dR_Max0p4_DoubleJet32er2p3_dEta_Max1p6;   //!
   // TBranch        *b_L1_Mu12er2p3_Jet40er2p1_dR_Max0p4_DoubleJet40er2p1_dEta_Max1p6;   //!
   // TBranch        *b_L1_Mu12er2p3_Jet40er2p3_dR_Max0p4_DoubleJet40er2p3_dEta_Max1p6;   //!
   // TBranch        *b_L1_Mu18er2p1_Tau24er2p1;   //!
   // TBranch        *b_L1_Mu18er2p1_Tau26er2p1;   //!
   // TBranch        *b_L1_Mu18er2p1_Tau26er2p1_Jet55;   //!
   // TBranch        *b_L1_Mu18er2p1_Tau26er2p1_Jet70;   //!
   // TBranch        *b_L1_Mu20_EG10er2p5;   //!
   // TBranch        *b_L1_Mu22er2p1_IsoTau28er2p1;   //!
   // TBranch        *b_L1_Mu22er2p1_IsoTau30er2p1;   //!
   // TBranch        *b_L1_Mu22er2p1_IsoTau32er2p1;   //!
   // TBranch        *b_L1_Mu22er2p1_IsoTau34er2p1;   //!
   // TBranch        *b_L1_Mu22er2p1_IsoTau36er2p1;   //!
   // TBranch        *b_L1_Mu22er2p1_IsoTau40er2p1;   //!
   // TBranch        *b_L1_Mu22er2p1_Tau70er2p1;   //!
   // TBranch        *b_L1_Mu3_Jet120er2p5_dR_Max0p4;   //!
   // TBranch        *b_L1_Mu3_Jet120er2p5_dR_Max0p8;   //!
   // TBranch        *b_L1_Mu3_Jet16er2p5_dR_Max0p4;   //!
   // TBranch        *b_L1_Mu3_Jet30er2p5;   //!
   // TBranch        *b_L1_Mu3_Jet35er2p5_dR_Max0p4;   //!
   // TBranch        *b_L1_Mu3_Jet60er2p5_dR_Max0p4;   //!
   // TBranch        *b_L1_Mu3_Jet80er2p5_dR_Max0p4;   //!
   // TBranch        *b_L1_Mu3er1p5_Jet100er2p5_ETMHF30;   //!
   // TBranch        *b_L1_Mu3er1p5_Jet100er2p5_ETMHF40;   //!
   // TBranch        *b_L1_Mu3er1p5_Jet100er2p5_ETMHF50;   //!
   // TBranch        *b_L1_Mu5_EG23er2p5;   //!
   // TBranch        *b_L1_Mu5_LooseIsoEG20er2p5;   //!
   // TBranch        *b_L1_Mu6_DoubleEG10er2p5;   //!
   // TBranch        *b_L1_Mu6_DoubleEG12er2p5;   //!
   // TBranch        *b_L1_Mu6_DoubleEG15er2p5;   //!
   // TBranch        *b_L1_Mu6_DoubleEG17er2p5;   //!
   // TBranch        *b_L1_Mu6_HTT240er;   //!
   // TBranch        *b_L1_Mu6_HTT250er;   //!
   // TBranch        *b_L1_Mu7_EG20er2p5;   //!
   // TBranch        *b_L1_Mu7_EG23er2p5;   //!
   // TBranch        *b_L1_Mu7_LooseIsoEG20er2p5;   //!
   // TBranch        *b_L1_Mu7_LooseIsoEG23er2p5;   //!
   // TBranch        *b_L1_NotBptxOR;   //!
   // TBranch        *b_L1_QuadJet60er2p5;   //!
   // TBranch        *b_L1_QuadJet_95_75_65_20_DoubleJet_75_65_er2p5_Jet20_FWD3p0;   //!
   // TBranch        *b_L1_QuadMu0;   //!
   // TBranch        *b_L1_QuadMu0_OQ;   //!
   // TBranch        *b_L1_QuadMu0_SQ;   //!
   // TBranch        *b_L1_SecondBunchInTrain;   //!
   // TBranch        *b_L1_SecondLastBunchInTrain;   //!
   // TBranch        *b_L1_SingleEG10er2p5;   //!
   // TBranch        *b_L1_SingleEG15er2p5;   //!
   // TBranch        *b_L1_SingleEG26er2p5;   //!
   // TBranch        *b_L1_SingleEG28_FWD2p5;   //!
   // TBranch        *b_L1_SingleEG28er1p5;   //!
   // TBranch        *b_L1_SingleEG28er2p1;   //!
   // TBranch        *b_L1_SingleEG28er2p5;   //!
   // TBranch        *b_L1_SingleEG34er2p5;   //!
   // TBranch        *b_L1_SingleEG36er2p5;   //!
   // TBranch        *b_L1_SingleEG38er2p5;   //!
   // TBranch        *b_L1_SingleEG40er2p5;   //!
   // TBranch        *b_L1_SingleEG42er2p5;   //!
   // TBranch        *b_L1_SingleEG45er2p5;   //!
   // TBranch        *b_L1_SingleEG50;   //!
   // TBranch        *b_L1_SingleEG60;   //!
   // TBranch        *b_L1_SingleEG8er2p5;   //!
   // TBranch        *b_L1_SingleIsoEG24er1p5;   //!
   // TBranch        *b_L1_SingleIsoEG24er2p1;   //!
   // TBranch        *b_L1_SingleIsoEG26er1p5;   //!
   // TBranch        *b_L1_SingleIsoEG26er2p1;   //!
   // TBranch        *b_L1_SingleIsoEG26er2p5;   //!
   // TBranch        *b_L1_SingleIsoEG28_FWD2p5;   //!
   // TBranch        *b_L1_SingleIsoEG28er1p5;   //!
   // TBranch        *b_L1_SingleIsoEG28er2p1;   //!
   // TBranch        *b_L1_SingleIsoEG28er2p5;   //!
   // TBranch        *b_L1_SingleIsoEG30er2p1;   //!
   // TBranch        *b_L1_SingleIsoEG30er2p5;   //!
   // TBranch        *b_L1_SingleIsoEG32er2p1;   //!
   // TBranch        *b_L1_SingleIsoEG32er2p5;   //!
   // TBranch        *b_L1_SingleIsoEG34er2p5;   //!
   // TBranch        *b_L1_SingleIsoTau32er2p1;   //!
   // TBranch        *b_L1_SingleJet10erHE;   //!
   // TBranch        *b_L1_SingleJet120;   //!
   // TBranch        *b_L1_SingleJet120_FWD3p0;   //!
   // TBranch        *b_L1_SingleJet120er2p5;   //!
   // TBranch        *b_L1_SingleJet12erHE;   //!
   // TBranch        *b_L1_SingleJet140er2p5;   //!
   // TBranch        *b_L1_SingleJet140er2p5_ETMHF70;   //!
   // TBranch        *b_L1_SingleJet140er2p5_ETMHF80;   //!
   // TBranch        *b_L1_SingleJet140er2p5_ETMHF90;   //!
   // TBranch        *b_L1_SingleJet160er2p5;   //!
   // TBranch        *b_L1_SingleJet180;   //!
   // TBranch        *b_L1_SingleJet180er2p5;   //!
   // TBranch        *b_L1_SingleJet200;   //!
   // TBranch        *b_L1_SingleJet20er2p5_NotBptxOR;   //!
   // TBranch        *b_L1_SingleJet20er2p5_NotBptxOR_3BX;   //!
   // TBranch        *b_L1_SingleJet35;   //!
   // TBranch        *b_L1_SingleJet35_FWD3p0;   //!
   // TBranch        *b_L1_SingleJet35er2p5;   //!
   // TBranch        *b_L1_SingleJet43er2p5_NotBptxOR_3BX;   //!
   // TBranch        *b_L1_SingleJet46er2p5_NotBptxOR_3BX;   //!
   // TBranch        *b_L1_SingleJet60;   //!
   // TBranch        *b_L1_SingleJet60_FWD3p0;   //!
   // TBranch        *b_L1_SingleJet60er2p5;   //!
   // TBranch        *b_L1_SingleJet8erHE;   //!
   // TBranch        *b_L1_SingleJet90;   //!
   // TBranch        *b_L1_SingleJet90_FWD3p0;   //!
   // TBranch        *b_L1_SingleJet90er2p5;   //!
   // TBranch        *b_L1_SingleLooseIsoEG26er1p5;   //!
   // TBranch        *b_L1_SingleLooseIsoEG26er2p5;   //!
   // TBranch        *b_L1_SingleLooseIsoEG28_FWD2p5;   //!
   // TBranch        *b_L1_SingleLooseIsoEG28er1p5;   //!
   // TBranch        *b_L1_SingleLooseIsoEG28er2p1;   //!
   // TBranch        *b_L1_SingleLooseIsoEG28er2p5;   //!
   // TBranch        *b_L1_SingleLooseIsoEG30er1p5;   //!
   // TBranch        *b_L1_SingleLooseIsoEG30er2p5;   //!
   // TBranch        *b_L1_SingleMu0_BMTF;   //!
   // TBranch        *b_L1_SingleMu0_DQ;   //!
   // TBranch        *b_L1_SingleMu0_EMTF;   //!
   // TBranch        *b_L1_SingleMu0_OMTF;   //!
   // TBranch        *b_L1_SingleMu10er1p5;   //!
   // TBranch        *b_L1_SingleMu12_DQ_BMTF;   //!
   // TBranch        *b_L1_SingleMu12_DQ_EMTF;   //!
   // TBranch        *b_L1_SingleMu12_DQ_OMTF;   //!
   // TBranch        *b_L1_SingleMu12er1p5;   //!
   // TBranch        *b_L1_SingleMu14er1p5;   //!
   // TBranch        *b_L1_SingleMu15_DQ;   //!
   // TBranch        *b_L1_SingleMu16er1p5;   //!
   // TBranch        *b_L1_SingleMu18;   //!
   // TBranch        *b_L1_SingleMu18er1p5;   //!
   // TBranch        *b_L1_SingleMu20;   //!
   // TBranch        *b_L1_SingleMu22;   //!
   // TBranch        *b_L1_SingleMu22_BMTF;   //!
   // TBranch        *b_L1_SingleMu22_DQ;   //!
   // TBranch        *b_L1_SingleMu22_EMTF;   //!
   // TBranch        *b_L1_SingleMu22_OMTF;   //!
   // TBranch        *b_L1_SingleMu22_OQ;   //!
   // TBranch        *b_L1_SingleMu25;   //!
   // TBranch        *b_L1_SingleMu3;   //!
   // TBranch        *b_L1_SingleMu5;   //!
   // TBranch        *b_L1_SingleMu6er1p5;   //!
   // TBranch        *b_L1_SingleMu7;   //!
   // TBranch        *b_L1_SingleMu7_DQ;   //!
   // TBranch        *b_L1_SingleMu7er1p5;   //!
   // TBranch        *b_L1_SingleMu8er1p5;   //!
   // TBranch        *b_L1_SingleMu9er1p5;   //!
   // TBranch        *b_L1_SingleMuCosmics;   //!
   // TBranch        *b_L1_SingleMuCosmics_BMTF;   //!
   // TBranch        *b_L1_SingleMuCosmics_EMTF;   //!
   // TBranch        *b_L1_SingleMuCosmics_OMTF;   //!
   // TBranch        *b_L1_SingleMuOpen;   //!
   // TBranch        *b_L1_SingleMuOpen_NotBptxOR;   //!
   // TBranch        *b_L1_SingleMuOpen_er1p1_NotBptxOR_3BX;   //!
   // TBranch        *b_L1_SingleMuOpen_er1p4_NotBptxOR_3BX;   //!
   // TBranch        *b_L1_SingleMuShower_Nominal;   //!
   // TBranch        *b_L1_SingleMuShower_Tight;   //!
   // TBranch        *b_L1_SingleTau120er2p1;   //!
   // TBranch        *b_L1_SingleTau130er2p1;   //!
   // TBranch        *b_L1_SingleTau70er2p1;   //!
   // TBranch        *b_L1_TOTEM_1;   //!
   // TBranch        *b_L1_TOTEM_2;   //!
   // TBranch        *b_L1_TOTEM_3;   //!
   // TBranch        *b_L1_TOTEM_4;   //!
   // TBranch        *b_L1_TripleEG16er2p5;   //!
   // TBranch        *b_L1_TripleEG_16_12_8_er2p5;   //!
   // TBranch        *b_L1_TripleEG_16_15_8_er2p5;   //!
   // TBranch        *b_L1_TripleEG_18_17_8_er2p5;   //!
   // TBranch        *b_L1_TripleEG_18_18_12_er2p5;   //!
   // TBranch        *b_L1_TripleJet_100_80_70_DoubleJet_80_70_er2p5;   //!
   // TBranch        *b_L1_TripleJet_105_85_75_DoubleJet_85_75_er2p5;   //!
   // TBranch        *b_L1_TripleJet_95_75_65_DoubleJet_75_65_er2p5;   //!
   // TBranch        *b_L1_TripleMu0;   //!
   // TBranch        *b_L1_TripleMu0_OQ;   //!
   // TBranch        *b_L1_TripleMu0_SQ;   //!
   // TBranch        *b_L1_TripleMu3;   //!
   // TBranch        *b_L1_TripleMu3_SQ;   //!
   // TBranch        *b_L1_TripleMu_2SQ_1p5SQ_0OQ;   //!
   // TBranch        *b_L1_TripleMu_2SQ_1p5SQ_0OQ_Mass_Max12;   //!
   // TBranch        *b_L1_TripleMu_3SQ_2p5SQ_0OQ_Mass_Max12;   //!
   // TBranch        *b_L1_TripleMu_5SQ_3SQ_0OQ;   //!
   // TBranch        *b_L1_TripleMu_5SQ_3SQ_0OQ_DoubleMu_5_3_SQ_OS_Mass_Max9;   //!
   // TBranch        *b_L1_TripleMu_5SQ_3SQ_0_DoubleMu_5_3_SQ_OS_Mass_Max9;   //!
   // TBranch        *b_L1_TripleMu_5_3_3;   //!
   // TBranch        *b_L1_TripleMu_5_3_3_SQ;   //!
   // TBranch        *b_L1_TripleMu_5_3p5_2p5;   //!
   // TBranch        *b_L1_TripleMu_5_3p5_2p5_DoubleMu_5_2p5_OS_Mass_5to17;   //!
   // TBranch        *b_L1_TripleMu_5_3p5_2p5_OQ_DoubleMu_5_2p5_OQ_OS_Mass_5to17;   //!
   // TBranch        *b_L1_TripleMu_5_4_2p5_DoubleMu_5_2p5_OS_Mass_5to17;   //!
   // TBranch        *b_L1_TripleMu_5_5_3;   //!
   // TBranch        *b_L1_UnpairedBunchBptxMinus;   //!
   // TBranch        *b_L1_UnpairedBunchBptxPlus;   //!
   // TBranch        *b_L1_ZeroBias;   //!
   // TBranch        *b_L1_ZeroBias_copy;   //!
   // TBranch        *b_L1_UnprefireableEvent;   //!
   TBranch        *b_Flag_HBHENoiseFilter;   //!
   TBranch        *b_Flag_HBHENoiseIsoFilter;   //!
   TBranch        *b_Flag_CSCTightHaloFilter;   //!
   TBranch        *b_Flag_CSCTightHaloTrkMuUnvetoFilter;   //!
   TBranch        *b_Flag_CSCTightHalo2015Filter;   //!
   TBranch        *b_Flag_globalTightHalo2016Filter;   //!
   TBranch        *b_Flag_globalSuperTightHalo2016Filter;   //!
   TBranch        *b_Flag_HcalStripHaloFilter;   //!
   TBranch        *b_Flag_hcalLaserEventFilter;   //!
   TBranch        *b_Flag_EcalDeadCellTriggerPrimitiveFilter;   //!
   TBranch        *b_Flag_EcalDeadCellBoundaryEnergyFilter;   //!
   TBranch        *b_Flag_ecalBadCalibFilter;   //!
   TBranch        *b_Flag_goodVertices;   //!
   TBranch        *b_Flag_eeBadScFilter;   //!
   TBranch        *b_Flag_ecalLaserCorrFilter;   //!
   TBranch        *b_Flag_trkPOGFilters;   //!
   TBranch        *b_Flag_chargedHadronTrackResolutionFilter;   //!
   TBranch        *b_Flag_muonBadTrackFilter;   //!
   TBranch        *b_Flag_BadChargedCandidateFilter;   //!
   TBranch        *b_Flag_BadPFMuonFilter;   //!
   TBranch        *b_Flag_BadPFMuonDzFilter;   //!
   TBranch        *b_Flag_hfNoisyHitsFilter;   //!
   TBranch        *b_Flag_BadChargedCandidateSummer16Filter;   //!
   TBranch        *b_Flag_BadPFMuonSummer16Filter;   //!
   TBranch        *b_Flag_trkPOG_manystripclus53X;   //!
   TBranch        *b_Flag_trkPOG_toomanystripclus53X;   //!
   TBranch        *b_Flag_trkPOG_logErrorTooManyClusters;   //!
   //TBranch        *b_Flag_METFilters;   //!
   TBranch        *b_L1Reco_step;   //!
   TBranch        *b_L1simulation_step;   //!
   TBranch        *b_HLTriggerFirstPath;   //!
   // TBranch        *b_HLT_AK8PFJet360_TrimMass30;   //!
   // TBranch        *b_HLT_AK8PFJet380_TrimMass30;   //!
   // TBranch        *b_HLT_AK8PFJet400_TrimMass30;   //!
   // TBranch        *b_HLT_AK8PFJet420_TrimMass30;   //!
   // TBranch        *b_HLT_AK8PFJet400_MassSD30;   //!
   // TBranch        *b_HLT_AK8PFJet420_MassSD30;   //!
   // TBranch        *b_HLT_AK8PFJet450_MassSD30;   //!
   // TBranch        *b_HLT_AK8DiPFJet250_250_MassSD30;   //!
   // TBranch        *b_HLT_AK8DiPFJet250_250_MassSD50;   //!
   // TBranch        *b_HLT_AK8DiPFJet260_260_MassSD30;   //!
   // TBranch        *b_HLT_AK8DiPFJet270_270_MassSD30;   //!
   // TBranch        *b_HLT_AK8PFHT750_TrimMass50;   //!
   // TBranch        *b_HLT_AK8PFHT800_TrimMass50;   //!
   // TBranch        *b_HLT_AK8PFHT850_TrimMass50;   //!
   // TBranch        *b_HLT_AK8PFHT900_TrimMass50;   //!
   // TBranch        *b_HLT_CaloJet500_NoJetID;   //!
   // TBranch        *b_HLT_CaloJet550_NoJetID;   //!
   // TBranch        *b_HLT_DoubleMu5_Upsilon_DoubleEle3_CaloIdL_TrackIdL;   //!
   // TBranch        *b_HLT_DoubleMu3_DoubleEle7p5_CaloIdL_TrackIdL_Upsilon;   //!
   // TBranch        *b_HLT_Trimuon5_3p5_2_Upsilon_Muon;   //!
   // TBranch        *b_HLT_TrimuonOpen_5_3p5_2_Upsilon_Muon;   //!
   // TBranch        *b_HLT_DoubleEle25_CaloIdL_MW;   //!
   // TBranch        *b_HLT_DoubleEle27_CaloIdL_MW;   //!
   // TBranch        *b_HLT_DoubleEle33_CaloIdL_MW;   //!
   // TBranch        *b_HLT_DoubleEle24_eta2p1_WPTight_Gsf;   //!
   // TBranch        *b_HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_DZ_PFHT350;   //!
   // TBranch        *b_HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_PFHT350;   //!
   // TBranch        *b_HLT_Ele27_Ele37_CaloIdL_MW;   //!
   // TBranch        *b_HLT_Mu27_Ele37_CaloIdL_MW;   //!
   // TBranch        *b_HLT_Mu37_Ele27_CaloIdL_MW;   //!
   // TBranch        *b_HLT_Mu37_TkMu27;   //!
   // TBranch        *b_HLT_DoubleMu4_3_Bs;   //!
   // TBranch        *b_HLT_DoubleMu4_3_Jpsi;   //!
   // TBranch        *b_HLT_DoubleMu4_3_LowMass;   //!
   // TBranch        *b_HLT_DoubleMu4_LowMass_Displaced;   //!
   // TBranch        *b_HLT_Mu0_L1DoubleMu;   //!
   // TBranch        *b_HLT_Mu4_L1DoubleMu;   //!
   // TBranch        *b_HLT_DoubleMu4_3_Photon4_BsToMMG;   //!
   // TBranch        *b_HLT_DoubleMu4_3_Displaced_Photon4_BsToMMG;   //!
   // TBranch        *b_HLT_DoubleMu3_Trk_Tau3mu;   //!
   // TBranch        *b_HLT_DoubleMu3_TkMu_DsTau3Mu;   //!
   // TBranch        *b_HLT_DoubleMu4_Mass3p8_DZ_PFHT350;   //!
   // TBranch        *b_HLT_DoubleMu4_MuMuTrk_Displaced;   //!
   // TBranch        *b_HLT_Mu3_PFJet40;   //!
   // TBranch        *b_HLT_Mu7p5_L2Mu2_Jpsi;   //!
   // TBranch        *b_HLT_Mu7p5_L2Mu2_Upsilon;   //!
   // TBranch        *b_HLT_Mu3_L1SingleMu5orSingleMu7;   //!
   // TBranch        *b_HLT_DoublePhoton33_CaloIdL;   //!
   // TBranch        *b_HLT_DoublePhoton70;   //!
   // TBranch        *b_HLT_DoublePhoton85;   //!
   // TBranch        *b_HLT_Ele20_WPTight_Gsf;   //!
   // TBranch        *b_HLT_Ele15_WPLoose_Gsf;   //!
   // TBranch        *b_HLT_Ele17_WPLoose_Gsf;   //!
   // TBranch        *b_HLT_Ele20_WPLoose_Gsf;   //!
   // TBranch        *b_HLT_Ele20_eta2p1_WPLoose_Gsf;   //!
   // TBranch        *b_HLT_DiEle27_WPTightCaloOnly_L1DoubleEG;   //!
   // TBranch        *b_HLT_Ele27_WPTight_Gsf;   //!
   // TBranch        *b_HLT_Ele28_WPTight_Gsf;   //!
   // TBranch        *b_HLT_Ele30_WPTight_Gsf;   //!
   // TBranch        *b_HLT_Ele32_WPTight_Gsf;   //!
   // TBranch        *b_HLT_Ele35_WPTight_Gsf;   //!
   // TBranch        *b_HLT_Ele35_WPTight_Gsf_L1EGMT;   //!
   // TBranch        *b_HLT_Ele38_WPTight_Gsf;   //!
   // TBranch        *b_HLT_Ele40_WPTight_Gsf;   //!
   // TBranch        *b_HLT_Ele32_WPTight_Gsf_L1DoubleEG;   //!
   // TBranch        *b_HLT_Ele24_eta2p1_WPTight_Gsf_TightChargedIsoPFTauHPS30_eta2p1_CrossL1;   //!
   // TBranch        *b_HLT_HT450_Beamspot;   //!
   // TBranch        *b_HLT_HT300_Beamspot;   //!
   // TBranch        *b_HLT_ZeroBias_Beamspot;   //!
   // TBranch        *b_HLT_IsoMu20_eta2p1_TightChargedIsoPFTauHPS27_eta2p1_CrossL1;   //!
   // TBranch        *b_HLT_IsoMu20_eta2p1_TightChargedIsoPFTauHPS27_eta2p1_TightID_CrossL1;   //!
   // TBranch        *b_HLT_IsoMu27_LooseChargedIsoPFTau20_Trk1_eta2p1_SingleL1;   //!
   // TBranch        *b_HLT_IsoMu27_LooseChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1;   //!
   // TBranch        *b_HLT_IsoMu27_MediumChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1;   //!
   // TBranch        *b_HLT_IsoMu27_TightChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1;   //!
   // TBranch        *b_HLT_IsoMu20;   //!
   TBranch        *b_HLT_IsoMu24;   //!
   // TBranch        *b_HLT_IsoMu24_eta2p1;   //!
   // TBranch        *b_HLT_IsoMu27;   //!
   // TBranch        *b_HLT_IsoMu30;   //!
   // TBranch        *b_HLT_UncorrectedJetE30_NoBPTX;   //!
   // TBranch        *b_HLT_UncorrectedJetE30_NoBPTX3BX;   //!
   // TBranch        *b_HLT_UncorrectedJetE60_NoBPTX3BX;   //!
   // TBranch        *b_HLT_UncorrectedJetE70_NoBPTX3BX;   //!
   // TBranch        *b_HLT_L1SingleMu18;   //!
   // TBranch        *b_HLT_L1SingleMu25;   //!
   // TBranch        *b_HLT_L1SingleMuCosmics;   //!
   // TBranch        *b_HLT_L2Mu10;   //!
   // TBranch        *b_HLT_L2Mu10_NoVertex_NoBPTX3BX;   //!
   // TBranch        *b_HLT_L2Mu10_NoVertex_NoBPTX;   //!
   // TBranch        *b_HLT_L2Mu45_NoVertex_3Sta_NoBPTX3BX;   //!
   // TBranch        *b_HLT_L2Mu40_NoVertex_3Sta_NoBPTX3BX;   //!
   // TBranch        *b_HLT_L2Mu50;   //!
   // TBranch        *b_HLT_L2Mu23NoVtx_2Cha;   //!
   // TBranch        *b_HLT_L2Mu23NoVtx_2Cha_CosmicSeed;   //!
   // TBranch        *b_HLT_DoubleL2Mu30NoVtx_2Cha_CosmicSeed_Eta2p4;   //!
   // TBranch        *b_HLT_DoubleL2Mu30NoVtx_2Cha_Eta2p4;   //!
   // TBranch        *b_HLT_DoubleL2Mu50;   //!
   // TBranch        *b_HLT_DoubleL2Mu23NoVtx_2Cha_CosmicSeed;   //!
   // TBranch        *b_HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed;   //!
   // TBranch        *b_HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed_Eta2p4;   //!
   // TBranch        *b_HLT_DoubleL2Mu23NoVtx_2Cha;   //!
   // TBranch        *b_HLT_DoubleL2Mu25NoVtx_2Cha;   //!
   // TBranch        *b_HLT_DoubleL2Mu25NoVtx_2Cha_Eta2p4;   //!
   // TBranch        *b_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL;   //!
   // TBranch        *b_HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL;   //!
   // TBranch        *b_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ;   //!
   // TBranch        *b_HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ;   //!
   // TBranch        *b_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8;   //!
   // TBranch        *b_HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass8;   //!
   // TBranch        *b_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8;   //!
   // TBranch        *b_HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass3p8;   //!
   // TBranch        *b_HLT_Mu25_TkMu0_Onia;   //!
   // TBranch        *b_HLT_Mu30_TkMu0_Psi;   //!
   // TBranch        *b_HLT_Mu30_TkMu0_Upsilon;   //!
   // TBranch        *b_HLT_Mu20_TkMu0_Phi;   //!
   // TBranch        *b_HLT_Mu25_TkMu0_Phi;   //!
   // TBranch        *b_HLT_Mu12;   //!
   // TBranch        *b_HLT_Mu15;   //!
   // TBranch        *b_HLT_Mu20;   //!
   // TBranch        *b_HLT_Mu27;   //!
   // TBranch        *b_HLT_Mu50;   //!
   // TBranch        *b_HLT_Mu55;   //!
   // TBranch        *b_HLT_CascadeMu100;   //!
   // TBranch        *b_HLT_HighPtTkMu100;   //!
   // TBranch        *b_HLT_DiPFJet15_NoCaloMatched;   //!
   // TBranch        *b_HLT_DiPFJet25_NoCaloMatched;   //!
   // TBranch        *b_HLT_DiPFJet15_FBEta3_NoCaloMatched;   //!
   // TBranch        *b_HLT_DiPFJet25_FBEta3_NoCaloMatched;   //!
   // TBranch        *b_HLT_DiPFJetAve40;   //!
   // TBranch        *b_HLT_DiPFJetAve60;   //!
   // TBranch        *b_HLT_DiPFJetAve80;   //!
   // TBranch        *b_HLT_DiPFJetAve140;   //!
   // TBranch        *b_HLT_DiPFJetAve200;   //!
   // TBranch        *b_HLT_DiPFJetAve260;   //!
   // TBranch        *b_HLT_DiPFJetAve320;   //!
   // TBranch        *b_HLT_DiPFJetAve400;   //!
   // TBranch        *b_HLT_DiPFJetAve500;   //!
   // TBranch        *b_HLT_DiPFJetAve15_HFJEC;   //!
   // TBranch        *b_HLT_DiPFJetAve25_HFJEC;   //!
   // TBranch        *b_HLT_DiPFJetAve35_HFJEC;   //!
   // TBranch        *b_HLT_DiPFJetAve60_HFJEC;   //!
   // TBranch        *b_HLT_DiPFJetAve80_HFJEC;   //!
   // TBranch        *b_HLT_DiPFJetAve100_HFJEC;   //!
   // TBranch        *b_HLT_DiPFJetAve160_HFJEC;   //!
   // TBranch        *b_HLT_DiPFJetAve220_HFJEC;   //!
   // TBranch        *b_HLT_DiPFJetAve300_HFJEC;   //!
   // TBranch        *b_HLT_AK8PFJet15;   //!
   // TBranch        *b_HLT_AK8PFJet25;   //!
   // TBranch        *b_HLT_AK8PFJet40;   //!
   // TBranch        *b_HLT_AK8PFJet60;   //!
   // TBranch        *b_HLT_AK8PFJet80;   //!
   // TBranch        *b_HLT_AK8PFJet140;   //!
   // TBranch        *b_HLT_AK8PFJet200;   //!
   // TBranch        *b_HLT_AK8PFJet260;   //!
   // TBranch        *b_HLT_AK8PFJet320;   //!
   // TBranch        *b_HLT_AK8PFJet400;   //!
   // TBranch        *b_HLT_AK8PFJet450;   //!
   // TBranch        *b_HLT_AK8PFJet500;   //!
   // TBranch        *b_HLT_AK8PFJet550;   //!
   // TBranch        *b_HLT_PFJet15;   //!
   // TBranch        *b_HLT_PFJet25;   //!
   // TBranch        *b_HLT_PFJet40;   //!
   // TBranch        *b_HLT_PFJet60;   //!
   // TBranch        *b_HLT_PFJet80;   //!
   // TBranch        *b_HLT_PFJet140;   //!
   // TBranch        *b_HLT_PFJet200;   //!
   // TBranch        *b_HLT_PFJet260;   //!
   // TBranch        *b_HLT_PFJet320;   //!
   // TBranch        *b_HLT_PFJet400;   //!
   // TBranch        *b_HLT_PFJet450;   //!
   // TBranch        *b_HLT_PFJet500;   //!
   // TBranch        *b_HLT_PFJet550;   //!
   // TBranch        *b_HLT_PFJetFwd15;   //!
   // TBranch        *b_HLT_PFJetFwd25;   //!
   // TBranch        *b_HLT_PFJetFwd40;   //!
   // TBranch        *b_HLT_PFJetFwd60;   //!
   // TBranch        *b_HLT_PFJetFwd80;   //!
   // TBranch        *b_HLT_PFJetFwd140;   //!
   // TBranch        *b_HLT_PFJetFwd200;   //!
   // TBranch        *b_HLT_PFJetFwd260;   //!
   // TBranch        *b_HLT_PFJetFwd320;   //!
   // TBranch        *b_HLT_PFJetFwd400;   //!
   // TBranch        *b_HLT_PFJetFwd450;   //!
   // TBranch        *b_HLT_PFJetFwd500;   //!
   // TBranch        *b_HLT_AK8PFJetFwd15;   //!
   // TBranch        *b_HLT_AK8PFJetFwd25;   //!
   // TBranch        *b_HLT_AK8PFJetFwd40;   //!
   // TBranch        *b_HLT_AK8PFJetFwd60;   //!
   // TBranch        *b_HLT_AK8PFJetFwd80;   //!
   // TBranch        *b_HLT_AK8PFJetFwd140;   //!
   // TBranch        *b_HLT_AK8PFJetFwd200;   //!
   // TBranch        *b_HLT_AK8PFJetFwd260;   //!
   // TBranch        *b_HLT_AK8PFJetFwd320;   //!
   // TBranch        *b_HLT_AK8PFJetFwd400;   //!
   // TBranch        *b_HLT_AK8PFJetFwd450;   //!
   // TBranch        *b_HLT_AK8PFJetFwd500;   //!
   // TBranch        *b_HLT_PFHT180;   //!
   // TBranch        *b_HLT_PFHT250;   //!
   // TBranch        *b_HLT_PFHT370;   //!
   // TBranch        *b_HLT_PFHT430;   //!
   // TBranch        *b_HLT_PFHT510;   //!
   // TBranch        *b_HLT_PFHT590;   //!
   // TBranch        *b_HLT_PFHT680;   //!
   // TBranch        *b_HLT_PFHT780;   //!
   // TBranch        *b_HLT_PFHT890;   //!
   // TBranch        *b_HLT_PFHT1050;   //!
   // TBranch        *b_HLT_PFHT500_PFMET100_PFMHT100_IDTight;   //!
   // TBranch        *b_HLT_PFHT500_PFMET110_PFMHT110_IDTight;   //!
   // TBranch        *b_HLT_PFHT700_PFMET85_PFMHT85_IDTight;   //!
   // TBranch        *b_HLT_PFHT700_PFMET95_PFMHT95_IDTight;   //!
   // TBranch        *b_HLT_PFHT800_PFMET75_PFMHT75_IDTight;   //!
   // TBranch        *b_HLT_PFHT800_PFMET85_PFMHT85_IDTight;   //!
   // TBranch        *b_HLT_PFMET110_PFMHT110_IDTight;   //!
   // TBranch        *b_HLT_PFMET120_PFMHT120_IDTight;   //!
   // TBranch        *b_HLT_PFMET130_PFMHT130_IDTight;   //!
   // TBranch        *b_HLT_PFMET140_PFMHT140_IDTight;   //!
   // TBranch        *b_HLT_PFMET100_PFMHT100_IDTight_CaloBTagDeepCSV_3p1;   //!
   // TBranch        *b_HLT_PFMET110_PFMHT110_IDTight_CaloBTagDeepCSV_3p1;   //!
   // TBranch        *b_HLT_PFMET120_PFMHT120_IDTight_CaloBTagDeepCSV_3p1;   //!
   // TBranch        *b_HLT_PFMET130_PFMHT130_IDTight_CaloBTagDeepCSV_3p1;   //!
   // TBranch        *b_HLT_PFMET140_PFMHT140_IDTight_CaloBTagDeepCSV_3p1;   //!
   // TBranch        *b_HLT_PFMET120_PFMHT120_IDTight_PFHT60;   //!
   // TBranch        *b_HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60;   //!
   // TBranch        *b_HLT_PFMETTypeOne120_PFMHT120_IDTight_PFHT60;   //!
   // TBranch        *b_HLT_PFMETTypeOne110_PFMHT110_IDTight;   //!
   // TBranch        *b_HLT_PFMETTypeOne120_PFMHT120_IDTight;   //!
   // TBranch        *b_HLT_PFMETTypeOne130_PFMHT130_IDTight;   //!
   // TBranch        *b_HLT_PFMETTypeOne140_PFMHT140_IDTight;   //!
   // TBranch        *b_HLT_PFMETNoMu110_PFMHTNoMu110_IDTight;   //!
   // TBranch        *b_HLT_PFMETNoMu120_PFMHTNoMu120_IDTight;   //!
   // TBranch        *b_HLT_PFMETNoMu130_PFMHTNoMu130_IDTight;   //!
   // TBranch        *b_HLT_PFMETNoMu140_PFMHTNoMu140_IDTight;   //!
   // TBranch        *b_HLT_PFMETNoMu110_PFMHTNoMu110_IDTight_FilterHF;   //!
   // TBranch        *b_HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_FilterHF;   //!
   // TBranch        *b_HLT_PFMETNoMu130_PFMHTNoMu130_IDTight_FilterHF;   //!
   // TBranch        *b_HLT_PFMETNoMu140_PFMHTNoMu140_IDTight_FilterHF;   //!
   // TBranch        *b_HLT_MonoCentralPFJet80_PFMETNoMu110_PFMHTNoMu110_IDTight;   //!
   // TBranch        *b_HLT_MonoCentralPFJet80_PFMETNoMu120_PFMHTNoMu120_IDTight;   //!
   // TBranch        *b_HLT_MonoCentralPFJet80_PFMETNoMu130_PFMHTNoMu130_IDTight;   //!
   // TBranch        *b_HLT_MonoCentralPFJet80_PFMETNoMu140_PFMHTNoMu140_IDTight;   //!
   // TBranch        *b_HLT_L1ETMHadSeeds;   //!
   // TBranch        *b_HLT_CaloMHT90;   //!
   // TBranch        *b_HLT_CaloMET80_NotCleaned;   //!
   // TBranch        *b_HLT_CaloMET90_NotCleaned;   //!
   // TBranch        *b_HLT_CaloMET100_NotCleaned;   //!
   // TBranch        *b_HLT_CaloMET110_NotCleaned;   //!
   // TBranch        *b_HLT_CaloMET250_NotCleaned;   //!
   // TBranch        *b_HLT_CaloMET300_NotCleaned;   //!
   // TBranch        *b_HLT_CaloMET350_NotCleaned;   //!
   // TBranch        *b_HLT_PFMET200_NotCleaned;   //!
   // TBranch        *b_HLT_PFMET250_NotCleaned;   //!
   // TBranch        *b_HLT_PFMET300_NotCleaned;   //!
   // TBranch        *b_HLT_PFMET200_BeamHaloCleaned;   //!
   // TBranch        *b_HLT_PFMETTypeOne200_BeamHaloCleaned;   //!
   // TBranch        *b_HLT_MET105_IsoTrk50;   //!
   // TBranch        *b_HLT_MET120_IsoTrk50;   //!
   // TBranch        *b_HLT_SingleJet30_Mu12_SinglePFJet40;   //!
   // TBranch        *b_HLT_Mu12eta2p3;   //!
   // TBranch        *b_HLT_Mu12eta2p3_PFJet40;   //!
   // TBranch        *b_HLT_Mu12_DoublePFJets40_PFBTagDeepCSV_p71;   //!
   // TBranch        *b_HLT_Mu12_DoublePFJets100_PFBTagDeepCSV_p71;   //!
   // TBranch        *b_HLT_Mu12_DoublePFJets200_PFBTagDeepCSV_p71;   //!
   // TBranch        *b_HLT_Mu12_DoublePFJets350_PFBTagDeepCSV_p71;   //!
   // TBranch        *b_HLT_Mu12_DoublePFJets40MaxDeta1p6_DoublePFBTagDeepCSV_p71;   //!
   // TBranch        *b_HLT_Mu12_DoublePFJets54MaxDeta1p6_DoublePFBTagDeepCSV_p71;   //!
   // TBranch        *b_HLT_DoublePFJets40_PFBTagDeepCSV_p71;   //!
   // TBranch        *b_HLT_DoublePFJets100_PFBTagDeepCSV_p71;   //!
   // TBranch        *b_HLT_DoublePFJets200_PFBTagDeepCSV_p71;   //!
   // TBranch        *b_HLT_DoublePFJets350_PFBTagDeepCSV_p71;   //!
   // TBranch        *b_HLT_DoublePFJets116MaxDeta1p6_DoublePFBTagDeepCSV_p71;   //!
   // TBranch        *b_HLT_DoublePFJets128MaxDeta1p6_DoublePFBTagDeepCSV_p71;   //!
   // TBranch        *b_HLT_Mu12_DoublePFJets40_PFBTagDeepJet_p71;   //!
   // TBranch        *b_HLT_Mu12_DoublePFJets100_PFBTagDeepJet_p71;   //!
   // TBranch        *b_HLT_Mu12_DoublePFJets200_PFBTagDeepJet_p71;   //!
   // TBranch        *b_HLT_Mu12_DoublePFJets350_PFBTagDeepJet_p71;   //!
   // TBranch        *b_HLT_Mu12_DoublePFJets40MaxDeta1p6_DoublePFBTagDeepJet_p71;   //!
   // TBranch        *b_HLT_Mu12_DoublePFJets54MaxDeta1p6_DoublePFBTagDeepJet_p71;   //!
   // TBranch        *b_HLT_DoublePFJets40_PFBTagDeepJet_p71;   //!
   // TBranch        *b_HLT_DoublePFJets100_PFBTagDeepJet_p71;   //!
   // TBranch        *b_HLT_DoublePFJets200_PFBTagDeepJet_p71;   //!
   // TBranch        *b_HLT_DoublePFJets350_PFBTagDeepJet_p71;   //!
   // TBranch        *b_HLT_DoublePFJets116MaxDeta1p6_DoublePFBTagDeepJet_p71;   //!
   // TBranch        *b_HLT_DoublePFJets128MaxDeta1p6_DoublePFBTagDeepJet_p71;   //!
   // TBranch        *b_HLT_Photon300_NoHE;   //!
   // TBranch        *b_HLT_Mu8_TrkIsoVVL;   //!
   // TBranch        *b_HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ;   //!
   // TBranch        *b_HLT_Mu8_DiEle12_CaloIdL_TrackIdL;   //!
   // TBranch        *b_HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350_DZ;   //!
   // TBranch        *b_HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350;   //!
   // TBranch        *b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ;   //!
   // TBranch        *b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30;   //!
   // TBranch        *b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_CaloDiJet30;   //!
   // TBranch        *b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30_PFBtagDeepCSV_1p5;   //!
   // TBranch        *b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_CaloDiJet30_CaloBtagDeepCSV_1p5;   //!
   // TBranch        *b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL;   //!
   // TBranch        *b_HLT_Mu17_TrkIsoVVL;   //!
   // TBranch        *b_HLT_Mu19_TrkIsoVVL;   //!
   // TBranch        *b_HLT_BTagMu_AK4DiJet20_Mu5;   //!
   // TBranch        *b_HLT_BTagMu_AK4DiJet40_Mu5;   //!
   // TBranch        *b_HLT_BTagMu_AK4DiJet70_Mu5;   //!
   // TBranch        *b_HLT_BTagMu_AK4DiJet110_Mu5;   //!
   // TBranch        *b_HLT_BTagMu_AK4DiJet170_Mu5;   //!
   // TBranch        *b_HLT_BTagMu_AK4Jet300_Mu5;   //!
   // TBranch        *b_HLT_BTagMu_AK8DiJet170_Mu5;   //!
   // TBranch        *b_HLT_BTagMu_AK8Jet170_DoubleMu5;   //!
   // TBranch        *b_HLT_BTagMu_AK8Jet300_Mu5;   //!
   // TBranch        *b_HLT_Ele15_Ele8_CaloIdL_TrackIdL_IsoVL;   //!
   // TBranch        *b_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ;   //!
   // TBranch        *b_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL;   //!
   // TBranch        *b_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ;   //!
   // TBranch        *b_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL;   //!
   // TBranch        *b_HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL;   //!
   // TBranch        *b_HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ;   //!
   // TBranch        *b_HLT_Mu12_DoublePhoton20;   //!
   // TBranch        *b_HLT_Photon20;   //!
   // TBranch        *b_HLT_Photon33;   //!
   // TBranch        *b_HLT_Photon50;   //!
   // TBranch        *b_HLT_Photon75;   //!
   // TBranch        *b_HLT_Photon90;   //!
   // TBranch        *b_HLT_Photon120;   //!
   // TBranch        *b_HLT_Photon150;   //!
   // TBranch        *b_HLT_Photon175;   //!
   // TBranch        *b_HLT_Photon200;   //!
   // TBranch        *b_HLT_Photon30EB_TightID_TightIso;   //!
   // TBranch        *b_HLT_Photon100EB_TightID_TightIso;   //!
   // TBranch        *b_HLT_Photon110EB_TightID_TightIso;   //!
   // TBranch        *b_HLT_Photon120EB_TightID_TightIso;   //!
   // TBranch        *b_HLT_Photon100EBHE10;   //!
   // TBranch        *b_HLT_Photon100EEHE10;   //!
   // TBranch        *b_HLT_Photon100EE_TightID_TightIso;   //!
   // TBranch        *b_HLT_Photon50_R9Id90_HE10_IsoM;   //!
   // TBranch        *b_HLT_Photon75_R9Id90_HE10_IsoM;   //!
   // TBranch        *b_HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ300_PFJetsMJJ400DEta3;   //!
   // TBranch        *b_HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ400_PFJetsMJJ600DEta3;   //!
   // TBranch        *b_HLT_Photon90_R9Id90_HE10_IsoM;   //!
   // TBranch        *b_HLT_Photon120_R9Id90_HE10_IsoM;   //!
   // TBranch        *b_HLT_Photon165_R9Id90_HE10_IsoM;   //!
   // TBranch        *b_HLT_Photon90_CaloIdL_PFHT700;   //!
   // TBranch        *b_HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90;   //!
   // TBranch        *b_HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass95;   //!
   // TBranch        *b_HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_Mass55;   //!
   // TBranch        *b_HLT_Photon35_TwoProngs35;   //!
   // TBranch        *b_HLT_IsoMu24_TwoProngs35;   //!
   // TBranch        *b_HLT_Dimuon0_Jpsi_L1_NoOS;   //!
   // TBranch        *b_HLT_Dimuon0_Jpsi_NoVertexing_NoOS;   //!
   // TBranch        *b_HLT_Dimuon0_Jpsi;   //!
   // TBranch        *b_HLT_Dimuon0_Jpsi_NoVertexing;   //!
   // TBranch        *b_HLT_Dimuon0_Jpsi_L1_4R_0er1p5R;   //!
   // TBranch        *b_HLT_Dimuon0_Jpsi_NoVertexing_L1_4R_0er1p5R;   //!
   // TBranch        *b_HLT_Dimuon0_Jpsi3p5_Muon2;   //!
   // TBranch        *b_HLT_Dimuon0_Upsilon_L1_4p5;   //!
   // TBranch        *b_HLT_Dimuon0_Upsilon_L1_5;   //!
   // TBranch        *b_HLT_Dimuon0_Upsilon_L1_4p5NoOS;   //!
   // TBranch        *b_HLT_Dimuon0_Upsilon_L1_4p5er2p0;   //!
   // TBranch        *b_HLT_Dimuon0_Upsilon_L1_4p5er2p0M;   //!
   // TBranch        *b_HLT_Dimuon0_Upsilon_NoVertexing;   //!
   // TBranch        *b_HLT_Dimuon0_Upsilon_L1_5M;   //!
   // TBranch        *b_HLT_Dimuon0_LowMass_L1_0er1p5R;   //!
   // TBranch        *b_HLT_Dimuon0_LowMass_L1_0er1p5;   //!
   // TBranch        *b_HLT_Dimuon0_LowMass;   //!
   // TBranch        *b_HLT_Dimuon0_LowMass_L1_4;   //!
   // TBranch        *b_HLT_Dimuon0_LowMass_L1_4R;   //!
   // TBranch        *b_HLT_Dimuon0_LowMass_L1_TM530;   //!
   // TBranch        *b_HLT_Dimuon0_Upsilon_Muon_L1_TM0;   //!
   // TBranch        *b_HLT_Dimuon0_Upsilon_Muon_NoL1Mass;   //!
   // TBranch        *b_HLT_TripleMu_5_3_3_Mass3p8_DZ;   //!
   // TBranch        *b_HLT_TripleMu_10_5_5_DZ;   //!
   // TBranch        *b_HLT_TripleMu_12_10_5;   //!
   // TBranch        *b_HLT_Tau3Mu_Mu7_Mu1_TkMu1_Tau15;   //!
   // TBranch        *b_HLT_Tau3Mu_Mu7_Mu1_TkMu1_Tau15_Charge1;   //!
   // TBranch        *b_HLT_Tau3Mu_Mu7_Mu1_TkMu1_IsoTau15;   //!
   // TBranch        *b_HLT_Tau3Mu_Mu7_Mu1_TkMu1_IsoTau15_Charge1;   //!
   // TBranch        *b_HLT_DoubleMu3_DZ_PFMET50_PFMHT60;   //!
   // TBranch        *b_HLT_DoubleMu3_DZ_PFMET70_PFMHT70;   //!
   // TBranch        *b_HLT_DoubleMu3_DZ_PFMET90_PFMHT90;   //!
   // TBranch        *b_HLT_DoubleMu3_Trk_Tau3mu_NoL1Mass;   //!
   // TBranch        *b_HLT_DoubleMu4_Jpsi_Displaced;   //!
   // TBranch        *b_HLT_DoubleMu4_Jpsi_NoVertexing;   //!
   // TBranch        *b_HLT_DoubleMu4_JpsiTrkTrk_Displaced;   //!
   // TBranch        *b_HLT_DoubleMu4_JpsiTrk_Bc;   //!
   // TBranch        *b_HLT_DoubleMu43NoFiltersNoVtx;   //!
   // TBranch        *b_HLT_DoubleMu48NoFiltersNoVtx;   //!
   // TBranch        *b_HLT_Mu43NoFiltersNoVtx_Photon43_CaloIdL;   //!
   // TBranch        *b_HLT_Mu48NoFiltersNoVtx_Photon48_CaloIdL;   //!
   // TBranch        *b_HLT_Mu38NoFiltersNoVtxDisplaced_Photon38_CaloIdL;   //!
   // TBranch        *b_HLT_Mu43NoFiltersNoVtxDisplaced_Photon43_CaloIdL;   //!
   // TBranch        *b_HLT_DoubleMu40NoFiltersNoVtxDisplaced;   //!
   // TBranch        *b_HLT_DoubleMu20_7_Mass0to30_L1_DM4;   //!
   // TBranch        *b_HLT_DoubleMu20_7_Mass0to30_L1_DM4EG;   //!
   // TBranch        *b_HLT_HT425;   //!
   // TBranch        *b_HLT_HT430_DisplacedDijet40_DisplacedTrack;   //!
   // TBranch        *b_HLT_HT500_DisplacedDijet40_DisplacedTrack;   //!
   // TBranch        *b_HLT_HT430_DisplacedDijet60_DisplacedTrack;   //!
   // TBranch        *b_HLT_HT400_DisplacedDijet40_DisplacedTrack;   //!
   // TBranch        *b_HLT_HT650_DisplacedDijet60_Inclusive;   //!
   // TBranch        *b_HLT_HT550_DisplacedDijet60_Inclusive;   //!
   // TBranch        *b_HLT_DiJet110_35_Mjj650_PFMET110;   //!
   // TBranch        *b_HLT_DiJet110_35_Mjj650_PFMET120;   //!
   // TBranch        *b_HLT_DiJet110_35_Mjj650_PFMET130;   //!
   // TBranch        *b_HLT_TripleJet110_35_35_Mjj650_PFMET110;   //!
   // TBranch        *b_HLT_TripleJet110_35_35_Mjj650_PFMET120;   //!
   // TBranch        *b_HLT_TripleJet110_35_35_Mjj650_PFMET130;   //!
   // TBranch        *b_HLT_Ele30_eta2p1_WPTight_Gsf_CentralPFJet35_EleCleaned;   //!
   // TBranch        *b_HLT_Ele28_eta2p1_WPTight_Gsf_HT150;   //!
   // TBranch        *b_HLT_Ele28_HighEta_SC20_Mass55;   //!
   // TBranch        *b_HLT_DoubleMu20_7_Mass0to30_Photon23;   //!
   // TBranch        *b_HLT_Ele15_IsoVVVL_PFHT450_CaloBTagDeepCSV_4p5;   //!
   // TBranch        *b_HLT_Ele15_IsoVVVL_PFHT450_PFMET50;   //!
   // TBranch        *b_HLT_Ele15_IsoVVVL_PFHT450;   //!
   // TBranch        *b_HLT_Ele50_IsoVVVL_PFHT450;   //!
   // TBranch        *b_HLT_Ele15_IsoVVVL_PFHT600;   //!
   // TBranch        *b_HLT_Mu4_TrkIsoVVL_DiPFJet90_40_DEta3p5_MJJ750_HTT300_PFMETNoMu60;   //!
   // TBranch        *b_HLT_Mu8_TrkIsoVVL_DiPFJet40_DEta3p5_MJJ750_HTT300_PFMETNoMu60;   //!
   // TBranch        *b_HLT_Mu10_TrkIsoVVL_DiPFJet40_DEta3p5_MJJ750_HTT350_PFMETNoMu60;   //!
   // TBranch        *b_HLT_Mu15_IsoVVVL_PFHT450_CaloBTagDeepCSV_4p5;   //!
   // TBranch        *b_HLT_Mu15_IsoVVVL_PFHT450_PFMET50;   //!
   // TBranch        *b_HLT_Mu15_IsoVVVL_PFHT450;   //!
   // TBranch        *b_HLT_Mu50_IsoVVVL_PFHT450;   //!
   // TBranch        *b_HLT_Mu15_IsoVVVL_PFHT600;   //!
   // TBranch        *b_HLT_Mu3er1p5_PFJet100er2p5_PFMET70_PFMHT70_IDTight;   //!
   // TBranch        *b_HLT_Mu3er1p5_PFJet100er2p5_PFMET80_PFMHT80_IDTight;   //!
   // TBranch        *b_HLT_Mu3er1p5_PFJet100er2p5_PFMET90_PFMHT90_IDTight;   //!
   // TBranch        *b_HLT_Mu3er1p5_PFJet100er2p5_PFMET100_PFMHT100_IDTight;   //!
   // TBranch        *b_HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu70_PFMHTNoMu70_IDTight;   //!
   // TBranch        *b_HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu80_PFMHTNoMu80_IDTight;   //!
   // TBranch        *b_HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu90_PFMHTNoMu90_IDTight;   //!
   // TBranch        *b_HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu100_PFMHTNoMu100_IDTight;   //!
   // TBranch        *b_HLT_Dimuon10_PsiPrime_Barrel_Seagulls;   //!
   // TBranch        *b_HLT_Dimuon20_Jpsi_Barrel_Seagulls;   //!
   // TBranch        *b_HLT_Dimuon10_Upsilon_y1p4;   //!
   // TBranch        *b_HLT_Dimuon12_Upsilon_y1p4;   //!
   // TBranch        *b_HLT_Dimuon14_Phi_Barrel_Seagulls;   //!
   // TBranch        *b_HLT_Dimuon25_Jpsi;   //!
   // TBranch        *b_HLT_Dimuon14_PsiPrime;   //!
   // TBranch        *b_HLT_Dimuon14_PsiPrime_noCorrL1;   //!
   // TBranch        *b_HLT_Dimuon18_PsiPrime;   //!
   // TBranch        *b_HLT_Dimuon18_PsiPrime_noCorrL1;   //!
   // TBranch        *b_HLT_Dimuon24_Upsilon_noCorrL1;   //!
   // TBranch        *b_HLT_Dimuon24_Phi_noCorrL1;   //!
   // TBranch        *b_HLT_Dimuon25_Jpsi_noCorrL1;   //!
   // TBranch        *b_HLT_DiMu4_Ele9_CaloIdL_TrackIdL_DZ_Mass3p8;   //!
   // TBranch        *b_HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ;   //!
   // TBranch        *b_HLT_DiMu9_Ele9_CaloIdL_TrackIdL;   //!
   // TBranch        *b_HLT_DoubleIsoMu20_eta2p1;   //!
   // TBranch        *b_HLT_TrkMu12_DoubleTrkMu5NoFiltersNoVtx;   //!
   // TBranch        *b_HLT_TrkMu16_DoubleTrkMu6NoFiltersNoVtx;   //!
   // TBranch        *b_HLT_TrkMu17_DoubleTrkMu8NoFiltersNoVtx;   //!
   // TBranch        *b_HLT_Mu8;   //!
   // TBranch        *b_HLT_Mu17;   //!
   // TBranch        *b_HLT_Mu19;   //!
   // TBranch        *b_HLT_Mu17_Photon30_IsoCaloId;   //!
   // TBranch        *b_HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30;   //!
   // TBranch        *b_HLT_Ele12_CaloIdL_TrackIdL_IsoVL_PFJet30;   //!
   // TBranch        *b_HLT_Ele15_CaloIdL_TrackIdL_IsoVL_PFJet30;   //!
   // TBranch        *b_HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30;   //!
   // TBranch        *b_HLT_Ele8_CaloIdM_TrackIdM_PFJet30;   //!
   // TBranch        *b_HLT_Ele17_CaloIdM_TrackIdM_PFJet30;   //!
   // TBranch        *b_HLT_Ele23_CaloIdM_TrackIdM_PFJet30;   //!
   // TBranch        *b_HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165;   //!
   // TBranch        *b_HLT_Ele115_CaloIdVT_GsfTrkIdT;   //!
   // TBranch        *b_HLT_Ele135_CaloIdVT_GsfTrkIdT;   //!
   // TBranch        *b_HLT_Ele145_CaloIdVT_GsfTrkIdT;   //!
   // TBranch        *b_HLT_Ele200_CaloIdVT_GsfTrkIdT;   //!
   // TBranch        *b_HLT_Ele250_CaloIdVT_GsfTrkIdT;   //!
   // TBranch        *b_HLT_Ele300_CaloIdVT_GsfTrkIdT;   //!
   // TBranch        *b_HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepCSV_4p5;   //!
   // TBranch        *b_HLT_PFHT330PT30_QuadPFJet_75_60_45_40;   //!
   // TBranch        *b_HLT_PFHT400_SixPFJet32_DoublePFBTagDeepCSV_2p94;   //!
   // TBranch        *b_HLT_PFHT400_SixPFJet32;   //!
   // TBranch        *b_HLT_PFHT450_SixPFJet36_PFBTagDeepCSV_1p59;   //!
   // TBranch        *b_HLT_PFHT450_SixPFJet36;   //!
   // TBranch        *b_HLT_PFHT400_FivePFJet_100_100_60_30_30;   //!
   // TBranch        *b_HLT_PFHT400_FivePFJet_100_100_60_30_30_DoublePFBTagDeepCSV_4p5;   //!
   // TBranch        *b_HLT_PFHT400_FivePFJet_120_120_60_30_30_DoublePFBTagDeepCSV_4p5;   //!
   // TBranch        *b_HLT_PFHT350;   //!
   // TBranch        *b_HLT_PFHT350MinPFJet15;   //!
   // TBranch        *b_HLT_Photon60_R9Id90_CaloIdL_IsoL;   //!
   // TBranch        *b_HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL;   //!
   // TBranch        *b_HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL_PFHT350MinPFJet15;   //!
   // TBranch        *b_HLT_ECALHT800;   //!
   // TBranch        *b_HLT_DiSC30_18_EIso_AND_HE_Mass70;   //!
   // TBranch        *b_HLT_Physics;   //!
   // TBranch        *b_HLT_EphemeralPhysics;   //!
   // TBranch        *b_HLT_Random;   //!
   // TBranch        *b_HLT_ZeroBias;   //!
   // TBranch        *b_HLT_ZeroBias_Alignment;   //!
   // TBranch        *b_HLT_EphemeralZeroBias;   //!
   // TBranch        *b_HLT_AK4CaloJet30;   //!
   // TBranch        *b_HLT_AK4CaloJet40;   //!
   // TBranch        *b_HLT_AK4CaloJet50;   //!
   // TBranch        *b_HLT_AK4CaloJet80;   //!
   // TBranch        *b_HLT_AK4CaloJet100;   //!
   // TBranch        *b_HLT_AK4CaloJet120;   //!
   // TBranch        *b_HLT_AK4PFJet30;   //!
   // TBranch        *b_HLT_AK4PFJet50;   //!
   // TBranch        *b_HLT_AK4PFJet80;   //!
   // TBranch        *b_HLT_AK4PFJet100;   //!
   // TBranch        *b_HLT_AK4PFJet120;   //!
   // TBranch        *b_HLT_SinglePhoton10_Eta3p1ForPPRef;   //!
   // TBranch        *b_HLT_SinglePhoton20_Eta3p1ForPPRef;   //!
   // TBranch        *b_HLT_SinglePhoton30_Eta3p1ForPPRef;   //!
   // TBranch        *b_HLT_Photon20_HoverELoose;   //!
   // TBranch        *b_HLT_Photon30_HoverELoose;   //!
   // TBranch        *b_HLT_EcalCalibration;   //!
   // TBranch        *b_HLT_HcalCalibration;   //!
   // TBranch        *b_HLT_L1UnpairedBunchBptxMinus;   //!
   // TBranch        *b_HLT_L1UnpairedBunchBptxPlus;   //!
   // TBranch        *b_HLT_L1NotBptxOR;   //!
   // TBranch        *b_HLT_L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142;   //!
   // TBranch        *b_HLT_CDC_L2cosmic_10_er1p0;   //!
   // TBranch        *b_HLT_CDC_L2cosmic_5p5_er1p0;   //!
   // TBranch        *b_HLT_HcalNZS;   //!
   // TBranch        *b_HLT_HcalPhiSym;   //!
   // TBranch        *b_HLT_HcalIsolatedbunch;   //!
   // TBranch        *b_HLT_IsoTrackHB;   //!
   // TBranch        *b_HLT_IsoTrackHE;   //!
   // TBranch        *b_HLT_ZeroBias_FirstCollisionAfterAbortGap;   //!
   // TBranch        *b_HLT_ZeroBias_IsolatedBunches;   //!
   // TBranch        *b_HLT_ZeroBias_FirstCollisionInTrain;   //!
   // TBranch        *b_HLT_ZeroBias_LastCollisionInTrain;   //!
   // TBranch        *b_HLT_ZeroBias_FirstBXAfterTrain;   //!
   // TBranch        *b_HLT_MediumChargedIsoPFTau180HighPtRelaxedIso_Trk50_eta2p1;   //!
   // TBranch        *b_HLT_MediumChargedIsoPFTau200HighPtRelaxedIso_Trk50_eta2p1;   //!
   // TBranch        *b_HLT_MediumChargedIsoPFTau220HighPtRelaxedIso_Trk50_eta2p1;   //!
   // TBranch        *b_HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL;   //!
   // TBranch        *b_HLT_Rsq0p35;   //!
   // TBranch        *b_HLT_Rsq0p40;   //!
   // TBranch        *b_HLT_RsqMR300_Rsq0p09_MR200;   //!
   // TBranch        *b_HLT_RsqMR320_Rsq0p09_MR200;   //!
   // TBranch        *b_HLT_RsqMR300_Rsq0p09_MR200_4jet;   //!
   // TBranch        *b_HLT_RsqMR320_Rsq0p09_MR200_4jet;   //!
   // TBranch        *b_HLT_IsoMu27_MET90;   //!
   // TBranch        *b_HLT_VBF_DoubleLooseChargedIsoPFTauHPS20_Trk1_eta2p1;   //!
   // TBranch        *b_HLT_VBF_DoubleMediumChargedIsoPFTauHPS20_Trk1_eta2p1;   //!
   // TBranch        *b_HLT_VBF_DoubleMediumDeepTauPFTauHPS20_eta2p1;   //!
   // TBranch        *b_HLT_VBF_DoubleTightChargedIsoPFTauHPS20_Trk1_eta2p1;   //!
   // TBranch        *b_HLT_Photon50_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3_PFMET50;   //!
   // TBranch        *b_HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3;   //!
   // TBranch        *b_HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ600DEta3;   //!
   // TBranch        *b_HLT_PFMET100_PFMHT100_IDTight_PFHT60;   //!
   // TBranch        *b_HLT_PFMETNoMu100_PFMHTNoMu100_IDTight_PFHT60;   //!
   // TBranch        *b_HLT_PFMETTypeOne100_PFMHT100_IDTight_PFHT60;   //!
   // TBranch        *b_HLT_Mu18_Mu9_SameSign;   //!
   // TBranch        *b_HLT_Mu18_Mu9_SameSign_DZ;   //!
   // TBranch        *b_HLT_Mu18_Mu9;   //!
   // TBranch        *b_HLT_Mu18_Mu9_DZ;   //!
   // TBranch        *b_HLT_Mu20_Mu10_SameSign;   //!
   // TBranch        *b_HLT_Mu20_Mu10_SameSign_DZ;   //!
   // TBranch        *b_HLT_Mu20_Mu10;   //!
   // TBranch        *b_HLT_Mu20_Mu10_DZ;   //!
   // TBranch        *b_HLT_Mu23_Mu12_SameSign;   //!
   // TBranch        *b_HLT_Mu23_Mu12_SameSign_DZ;   //!
   // TBranch        *b_HLT_Mu23_Mu12;   //!
   // TBranch        *b_HLT_Mu23_Mu12_DZ;   //!
   // TBranch        *b_HLT_DoubleMu2_Jpsi_DoubleTrk1_Phi1p05;   //!
   // TBranch        *b_HLT_DoubleMu2_Jpsi_DoubleTkMu0_Phi;   //!
   // TBranch        *b_HLT_DoubleMu3_DCA_PFMET50_PFMHT60;   //!
   // TBranch        *b_HLT_TripleMu_5_3_3_Mass3p8_DCA;   //!
   // TBranch        *b_HLT_QuadPFJet98_83_71_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1;   //!
   // TBranch        *b_HLT_QuadPFJet103_88_75_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1;   //!
   // TBranch        *b_HLT_QuadPFJet111_90_80_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1;   //!
   // TBranch        *b_HLT_QuadPFJet98_83_71_15_PFBTagDeepCSV_1p3_VBF2;   //!
   // TBranch        *b_HLT_QuadPFJet103_88_75_15_PFBTagDeepCSV_1p3_VBF2;   //!
   // TBranch        *b_HLT_QuadPFJet105_88_76_15_PFBTagDeepCSV_1p3_VBF2;   //!
   // TBranch        *b_HLT_QuadPFJet111_90_80_15_PFBTagDeepCSV_1p3_VBF2;   //!
   // TBranch        *b_HLT_QuadPFJet98_83_71_15;   //!
   // TBranch        *b_HLT_QuadPFJet103_88_75_15;   //!
   // TBranch        *b_HLT_QuadPFJet105_88_76_15;   //!
   // TBranch        *b_HLT_QuadPFJet111_90_80_15;   //!
   // TBranch        *b_HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p17;   //!
   // TBranch        *b_HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p1;   //!
   // TBranch        *b_HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_p02;   //!
   // TBranch        *b_HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np2;   //!
   // TBranch        *b_HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np4;   //!
   // TBranch        *b_HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_Mass55;   //!
   // TBranch        *b_HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId;   //!
   // TBranch        *b_HLT_Mu12_IP6_part0;   //!
   // TBranch        *b_HLT_Mu12_IP6_part1;   //!
   // TBranch        *b_HLT_Mu12_IP6_part2;   //!
   // TBranch        *b_HLT_Mu12_IP6_part3;   //!
   // TBranch        *b_HLT_Mu12_IP6_part4;   //!
   // TBranch        *b_HLT_Mu9_IP5_part0;   //!
   // TBranch        *b_HLT_Mu9_IP5_part1;   //!
   // TBranch        *b_HLT_Mu9_IP5_part2;   //!
   // TBranch        *b_HLT_Mu9_IP5_part3;   //!
   // TBranch        *b_HLT_Mu9_IP5_part4;   //!
   // TBranch        *b_HLT_Mu7_IP4_part0;   //!
   // TBranch        *b_HLT_Mu7_IP4_part1;   //!
   // TBranch        *b_HLT_Mu7_IP4_part2;   //!
   // TBranch        *b_HLT_Mu7_IP4_part3;   //!
   // TBranch        *b_HLT_Mu7_IP4_part4;   //!
   // TBranch        *b_HLT_Mu9_IP4_part0;   //!
   // TBranch        *b_HLT_Mu9_IP4_part1;   //!
   // TBranch        *b_HLT_Mu9_IP4_part2;   //!
   // TBranch        *b_HLT_Mu9_IP4_part3;   //!
   // TBranch        *b_HLT_Mu9_IP4_part4;   //!
   // TBranch        *b_HLT_Mu8_IP5_part0;   //!
   // TBranch        *b_HLT_Mu8_IP5_part1;   //!
   // TBranch        *b_HLT_Mu8_IP5_part2;   //!
   // TBranch        *b_HLT_Mu8_IP5_part3;   //!
   // TBranch        *b_HLT_Mu8_IP5_part4;   //!
   // TBranch        *b_HLT_Mu8_IP6_part0;   //!
   // TBranch        *b_HLT_Mu8_IP6_part1;   //!
   // TBranch        *b_HLT_Mu8_IP6_part2;   //!
   // TBranch        *b_HLT_Mu8_IP6_part3;   //!
   // TBranch        *b_HLT_Mu8_IP6_part4;   //!
   // TBranch        *b_HLT_Mu9_IP6_part0;   //!
   // TBranch        *b_HLT_Mu9_IP6_part1;   //!
   // TBranch        *b_HLT_Mu9_IP6_part2;   //!
   // TBranch        *b_HLT_Mu9_IP6_part3;   //!
   // TBranch        *b_HLT_Mu9_IP6_part4;   //!
   // TBranch        *b_HLT_Mu8_IP3_part0;   //!
   // TBranch        *b_HLT_Mu8_IP3_part1;   //!
   // TBranch        *b_HLT_Mu8_IP3_part2;   //!
   // TBranch        *b_HLT_Mu8_IP3_part3;   //!
   // TBranch        *b_HLT_Mu8_IP3_part4;   //!
   // TBranch        *b_HLT_Mu9_IP0_part0;   //!
   // TBranch        *b_HLT_Mu9_IP3_part0;   //!
   // TBranch        *b_HLT_QuadPFJet105_88_76_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1;   //!
   // TBranch        *b_HLT_TrkMu6NoFiltersNoVtx;   //!
   // TBranch        *b_HLT_TrkMu16NoFiltersNoVtx;   //!
   // TBranch        *b_HLT_DoubleTrkMu_16_6_NoFiltersNoVtx;   //!
   // TBranch        *b_HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1;   //!
   // TBranch        *b_HLT_DoubleMediumChargedIsoPFTauHPS40_Trk1_eta2p1;   //!
   // TBranch        *b_HLT_DoubleTightChargedIsoPFTauHPS35_Trk1_eta2p1;   //!
   // TBranch        *b_HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1;   //!
   // TBranch        *b_HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1;   //!
   // TBranch        *b_HLT_IsoMu24_eta2p1_LooseDeepTauPFTauHPS180_eta2p1;   //!
   // TBranch        *b_HLT_IsoMu24_eta2p1_LooseDeepTauPFTauHPS30_eta2p1_CrossL1;   //!
   // TBranch        *b_HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS35_L2NN_eta2p1_CrossL1;   //!
   // TBranch        *b_HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1;   //!
   // TBranch        *b_HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepJet_4p5;   //!
   // TBranch        *b_HLT_PFHT400_FivePFJet_100_100_60_30_30_DoublePFBTagDeepJet_4p5;   //!
   // TBranch        *b_HLT_PFHT400_FivePFJet_120_120_60_30_30_DoublePFBTagDeepJet_4p5;   //!
   // TBranch        *b_HLT_PFHT400_SixPFJet32_DoublePFBTagDeepJet_2p94;   //!
   // TBranch        *b_HLT_PFHT450_SixPFJet36_PFBTagDeepJet_1p59;   //!
   // TBranch        *b_HLT_QuadPFJet103_88_75_15_DoublePFBTagDeepJet_1p3_7p7_VBF1;   //!
   // TBranch        *b_HLT_QuadPFJet103_88_75_15_PFBTagDeepJet_1p3_VBF2;   //!
   // TBranch        *b_HLT_QuadPFJet105_88_76_15_DoublePFBTagDeepJet_1p3_7p7_VBF1;   //!
   // TBranch        *b_HLT_QuadPFJet105_88_76_15_PFBTagDeepJet_1p3_VBF2;   //!
   // TBranch        *b_HLT_QuadPFJet111_90_80_15_DoublePFBTagDeepJet_1p3_7p7_VBF1;   //!
   // TBranch        *b_HLT_QuadPFJet111_90_80_15_PFBTagDeepJet_1p3_VBF2;   //!
   // TBranch        *b_HLT_QuadPFJet98_83_71_15_DoublePFBTagDeepJet_1p3_7p7_VBF1;   //!
   // TBranch        *b_HLT_QuadPFJet98_83_71_15_PFBTagDeepJet_1p3_VBF2;   //!
   // TBranch        *b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30_PFBtagDeepJet_1p5;   //!
   // TBranch        *b_HLT_QuadPFJet70_50_40_30;   //!
   // TBranch        *b_HLT_QuadPFJet70_50_40_30_PFBTagParticleNet_2BTagSum0p65;   //!
   // TBranch        *b_HLT_QuadPFJet70_50_40_35_PFBTagParticleNet_2BTagSum0p65;   //!
   // TBranch        *b_HLT_QuadPFJet70_50_45_35_PFBTagParticleNet_2BTagSum0p65;   //!
   // TBranch        *b_HLT_AK8PFJet230_SoftDropMass40;   //!
   // TBranch        *b_HLT_AK8PFJet230_SoftDropMass40_PFAK8ParticleNetBB0p35;   //!
   // TBranch        *b_HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetBB0p35;   //!
   // TBranch        *b_HLT_AK8PFJet275_SoftDropMass40_PFAK8ParticleNetBB0p35;   //!
   // TBranch        *b_HLT_AK8PFJet400_SoftDropMass40;   //!
   // TBranch        *b_HLT_AK8PFJet425_SoftDropMass40;   //!
   // TBranch        *b_HLT_AK8PFJet450_SoftDropMass40;   //!
   // TBranch        *b_HLT_AK8PFJet230_SoftDropMass40_PFAK8ParticleNetTauTau0p30;   //!
   // TBranch        *b_HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetTauTau0p30;   //!
   // TBranch        *b_HLT_AK8PFJet275_SoftDropMass40_PFAK8ParticleNetTauTau0p30;   //!
   // TBranch        *b_HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60;   //!
   // TBranch        *b_HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75;   //!
   // TBranch        *b_HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_CrossL1;   //!
   // TBranch        *b_HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60_CrossL1;   //!
   // TBranch        *b_HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75_CrossL1;   //!
   // TBranch        *b_HLT_DoublePFJets40_Mass500_MediumDeepTauPFTauHPS45_L2NN_MediumDeepTauPFTauHPS20_eta2p1;   //!
   // TBranch        *b_HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS20_eta2p1_SingleL1;   //!
   // TBranch        *b_HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS45_L2NN_eta2p1_CrossL1;   //!
   // TBranch        *b_HLT_DoubleL2Mu10NoVtx_2Cha_VetoL3Mu0DxyMax1cm;   //!
   // TBranch        *b_HLT_DoubleL2Mu12NoVtx_2Cha_VetoL3Mu0DxyMax1cm;   //!
   // TBranch        *b_HLT_DoubleL2Mu14NoVtx_2Cha_VetoL3Mu0DxyMax1cm;   //!
   // TBranch        *b_HLT_DoubleL3Mu16_10NoVtx_DxyMin0p01cm;   //!
   // TBranch        *b_HLT_DoubleL3Mu18_10NoVtx_DxyMin0p01cm;   //!
   // TBranch        *b_HLT_DoubleL3Mu20_10NoVtx_DxyMin0p01cm;   //!
   // TBranch        *b_HLT_L2Mu10NoVtx_2Cha;   //!
   // TBranch        *b_HLT_L2Mu10NoVtx_2Cha_VetoL3Mu0DxyMax1cm;   //!
   // TBranch        *b_HLT_L3Mu10NoVtx;   //!
   // TBranch        *b_HLT_L3Mu10NoVtx_DxyMin0p01cm;   //!
   // TBranch        *b_HLT_Mu20NoFiltersNoVtxDisplaced_Photon20_CaloCustomId;   //!
   // TBranch        *b_HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1;   //!
   // TBranch        *b_HLT_HT430_DelayedJet40_DoubleDelay0p5nsTrackless;   //!
   // TBranch        *b_HLT_HT430_DelayedJet40_DoubleDelay1nsInclusive;   //!
   // TBranch        *b_HLT_HT430_DelayedJet40_SingleDelay1nsTrackless;   //!
   // TBranch        *b_HLT_HT430_DelayedJet40_SingleDelay2nsInclusive;   //!
   // TBranch        *b_HLT_L1Mu6HT240;   //!
   // TBranch        *b_HLT_Mu6HT240_DisplacedDijet30_Inclusive0PtrkShortSig5;   //!
   // TBranch        *b_HLT_Mu6HT240_DisplacedDijet30_Inclusive1PtrkShortSig5_DisplacedLoose;   //!
   // TBranch        *b_HLT_Mu6HT240_DisplacedDijet35_Inclusive0PtrkShortSig5;   //!
   // TBranch        *b_HLT_Mu6HT240_DisplacedDijet35_Inclusive1PtrkShortSig5_DisplacedLoose;   //!
   // TBranch        *b_HLT_Mu6HT240_DisplacedDijet40_Inclusive0PtrkShortSig5;   //!
   // TBranch        *b_HLT_Mu6HT240_DisplacedDijet40_Inclusive1PtrkShortSig5_DisplacedLoose;   //!
   // TBranch        *b_HLT_HT430_DisplacedDijet30_Inclusive1PtrkShortSig5;   //!
   // TBranch        *b_HLT_HT430_DisplacedDijet35_Inclusive1PtrkShortSig5;   //!
   // TBranch        *b_HLT_HT430_DisplacedDijet40_Inclusive1PtrkShortSig5;   //!
   // TBranch        *b_HLT_CaloMET60_DTCluster50;   //!
   // TBranch        *b_HLT_CaloMET60_DTClusterNoMB1S50;   //!
   // TBranch        *b_HLT_L1MET_DTCluster50;   //!
   // TBranch        *b_HLT_L1MET_DTClusterNoMB1S50;   //!
   // TBranch        *b_HLT_CscCluster_Loose;   //!
   // TBranch        *b_HLT_CscCluster_Medium;   //!
   // TBranch        *b_HLT_CscCluster_Tight;   //!
   // TBranch        *b_HLT_L1CSCShower_DTCluster50;   //!
   // TBranch        *b_HLT_L1CSCShower_DTCluster75;   //!
   // TBranch        *b_HLT_PFMET105_IsoTrk50;   //!
   // TBranch        *b_HLT_PFMET105_PFJet100_looseRecoiling;   //!
   // TBranch        *b_HLT_PFMET110_PFJet100;   //!
   // TBranch        *b_HLT_PFMET110_PFJet100_looseRecoiling;   //!
   // TBranch        *b_HLT_DoubleL3dTksMu16_10NoVtx_DxyMin0p01cm;   //!
   // TBranch        *b_HLT_L3dTksMu10_NoVtx_DxyMin0p01cm;   //!
   // TBranch        *b_HLT_HT170_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack;   //!
   // TBranch        *b_HLT_HT200_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack;   //!
   // TBranch        *b_HLT_HT200_L1SingleLLPJet_DisplacedDijet60_DisplacedTrack;   //!
   // TBranch        *b_HLT_HT270_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack;   //!
   // TBranch        *b_HLT_HT320_L1SingleLLPJet_DisplacedDijet60_Inclusive;   //!
   // TBranch        *b_HLT_HT420_L1SingleLLPJet_DisplacedDijet60_Inclusive;   //!
   // TBranch        *b_HLT_HT200_L1SingleLLPJet_DelayedJet40_SingleDelay1nsTrackless;   //!
   // TBranch        *b_HLT_HT200_L1SingleLLPJet_DelayedJet40_SingleDelay2nsInclusive;   //!
   // TBranch        *b_HLT_HT200_L1SingleLLPJet_DelayedJet40_DoubleDelay0p5nsTrackless;   //!
   // TBranch        *b_HLT_HT200_L1SingleLLPJet_DelayedJet40_DoubleDelay1nsInclusive;   //!
   // TBranch        *b_HLT_HT200_L1SingleLLPJet_DisplacedDijet30_Inclusive1PtrkShortSig5;   //!
   // TBranch        *b_HLT_HT200_L1SingleLLPJet_DisplacedDijet35_Inclusive1PtrkShortSig5;   //!
   // TBranch        *b_HLT_HT200_L1SingleLLPJet_DisplacedDijet40_Inclusive1PtrkShortSig5;   //!
   // TBranch        *b_HLT_DiPhoton10Time1ns;   //!
   // TBranch        *b_HLT_DiPhoton10Time1p2ns;   //!
   // TBranch        *b_HLT_DiPhoton10Time1p4ns;   //!
   // TBranch        *b_HLT_DiPhoton10Time1p6ns;   //!
   // TBranch        *b_HLT_DiPhoton10Time1p8ns;   //!
   // TBranch        *b_HLT_DiPhoton10Time2ns;   //!
   // TBranch        *b_HLT_DiPhoton10sminlt0p1;   //!
   // TBranch        *b_HLT_DiPhoton10sminlt0p12;   //!
   // TBranch        *b_HLT_DiPhoton10sminlt0p14;   //!
   // TBranch        *b_HLT_DiPhoton10sminlt0p16;   //!
   // TBranch        *b_HLT_DiPhoton10_CaloIdL;   //!
   // TBranch        *b_HLT_DoubleEle4_eta1p22_mMax6;   //!
   // TBranch        *b_HLT_DoubleEle4p5_eta1p22_mMax6;   //!
   // TBranch        *b_HLT_DoubleEle5_eta1p22_mMax6;   //!
   // TBranch        *b_HLT_DoubleEle5p5_eta1p22_mMax6;   //!
   // TBranch        *b_HLT_DoubleEle6_eta1p22_mMax6;   //!
   // TBranch        *b_HLT_DoubleEle6p5_eta1p22_mMax6;   //!
   // TBranch        *b_HLT_DoubleEle7_eta1p22_mMax6;   //!
   // TBranch        *b_HLT_DoubleEle7p5_eta1p22_mMax6;   //!
   // TBranch        *b_HLT_DoubleEle8_eta1p22_mMax6;   //!
   // TBranch        *b_HLT_DoubleEle8p5_eta1p22_mMax6;   //!
   // TBranch        *b_HLT_DoubleEle9_eta1p22_mMax6;   //!
   // TBranch        *b_HLT_DoubleEle9p5_eta1p22_mMax6;   //!
   // TBranch        *b_HLT_DoubleEle10_eta1p22_mMax6;   //!
   // TBranch        *b_HLT_Diphoton20_14_eta1p5_R9IdL_AND_HE_AND_IsoTCaloIdT;   //!
   // TBranch        *b_HLT_Diphoton20_14_eta1p5_R9IdL_AND_HET_AND_IsoTCaloIdT;   //!
   // TBranch        *b_HLT_Diphoton22_14_eta1p5_R9IdL_AND_HE_AND_IsoTCaloIdT;   //!
   // TBranch        *b_HLT_Diphoton22_14_eta1p5_R9IdL_AND_HET_AND_IsoTCaloIdT;   //!
   // TBranch        *b_HLT_ExpressMuons;   //!
   // TBranch        *b_HLT_OnlineMonitorGroup;   //!
   // TBranch        *b_HLT_PPSMaxTracksPerArm1;   //!
   // TBranch        *b_HLT_PPSMaxTracksPerRP4;   //!
   TBranch        *b_HLTriggerFinalPath;   //!

};

#endif

#ifdef MainEvent_cxx

MainEvent::~MainEvent()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

void MainEvent::Init(TTree *tree, TString nanoAODVersion)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);
 
   fChain->SetCacheSize(50 * 1024 * 1024);
   fChain->SetBranchStatus("*", 0);

   fChain->SetBranchStatus("run", 1);
   fChain->SetBranchAddress("run", &run, &b_run);
   fChain->SetBranchStatus("luminosityBlock", 1);
   fChain->SetBranchAddress("luminosityBlock", &luminosityBlock, &b_luminosityBlock);
   fChain->SetBranchStatus("event", 1);
   fChain->SetBranchAddress("event", &event, &b_event);
   fChain->SetBranchStatus("bunchCrossing", 1);
   fChain->SetBranchAddress("bunchCrossing", &bunchCrossing, &b_bunchCrossing);
   // fChain->SetBranchStatus("BeamSpot_type", 1);
   // fChain->SetBranchAddress("BeamSpot_type", &BeamSpot_type, &b_BeamSpot_type);
   // fChain->SetBranchStatus("BeamSpot_sigmaZ", 1);
   // fChain->SetBranchAddress("BeamSpot_sigmaZ", &BeamSpot_sigmaZ, &b_BeamSpot_sigmaZ);
   // fChain->SetBranchStatus("BeamSpot_sigmaZError", 1);
   // fChain->SetBranchAddress("BeamSpot_sigmaZError", &BeamSpot_sigmaZError, &b_BeamSpot_sigmaZError);
   // fChain->SetBranchStatus("BeamSpot_z", 1);
   // fChain->SetBranchAddress("BeamSpot_z", &BeamSpot_z, &b_BeamSpot_z);
   // fChain->SetBranchStatus("BeamSpot_zError", 1);
   // fChain->SetBranchAddress("BeamSpot_zError", &BeamSpot_zError, &b_BeamSpot_zError);
   // fChain->SetBranchStatus("nboostedTau", 1);
   // fChain->SetBranchAddress("nboostedTau", &nboostedTau, &b_nboostedTau);
   // fChain->SetBranchStatus("boostedTau_idAntiEle2018", 1);
   // fChain->SetBranchAddress("boostedTau_idAntiEle2018", boostedTau_idAntiEle2018, &b_boostedTau_idAntiEle2018);
   // fChain->SetBranchStatus("boostedTau_idAntiMu", 1);
   // fChain->SetBranchAddress("boostedTau_idAntiMu", boostedTau_idAntiMu, &b_boostedTau_idAntiMu);
   // fChain->SetBranchStatus("boostedTau_idMVAnewDM2017v2", 1);
   // fChain->SetBranchAddress("boostedTau_idMVAnewDM2017v2", boostedTau_idMVAnewDM2017v2, &b_boostedTau_idMVAnewDM2017v2);
   // fChain->SetBranchStatus("boostedTau_idMVAoldDM2017v2", 1);
   // fChain->SetBranchAddress("boostedTau_idMVAoldDM2017v2", boostedTau_idMVAoldDM2017v2, &b_boostedTau_idMVAoldDM2017v2);
   // fChain->SetBranchStatus("boostedTau_jetIdx", 1);
   // fChain->SetBranchAddress("boostedTau_jetIdx", boostedTau_jetIdx, &b_boostedTau_jetIdx);
   // fChain->SetBranchStatus("boostedTau_rawAntiEleCat2018", 1);
   // fChain->SetBranchAddress("boostedTau_rawAntiEleCat2018", boostedTau_rawAntiEleCat2018, &b_boostedTau_rawAntiEleCat2018);
   // fChain->SetBranchStatus("boostedTau_charge", 1);
   // fChain->SetBranchAddress("boostedTau_charge", boostedTau_charge, &b_boostedTau_charge);
   // fChain->SetBranchStatus("boostedTau_decayMode", 1);
   // fChain->SetBranchAddress("boostedTau_decayMode", boostedTau_decayMode, &b_boostedTau_decayMode);
   // fChain->SetBranchStatus("boostedTau_chargedIso", 1);
   // fChain->SetBranchAddress("boostedTau_chargedIso", boostedTau_chargedIso, &b_boostedTau_chargedIso);
   // fChain->SetBranchStatus("boostedTau_eta", 1);
   // fChain->SetBranchAddress("boostedTau_eta", boostedTau_eta, &b_boostedTau_eta);
   // fChain->SetBranchStatus("boostedTau_leadTkDeltaEta", 1);
   // fChain->SetBranchAddress("boostedTau_leadTkDeltaEta", boostedTau_leadTkDeltaEta, &b_boostedTau_leadTkDeltaEta);
   // fChain->SetBranchStatus("boostedTau_leadTkDeltaPhi", 1);
   // fChain->SetBranchAddress("boostedTau_leadTkDeltaPhi", boostedTau_leadTkDeltaPhi, &b_boostedTau_leadTkDeltaPhi);
   // fChain->SetBranchStatus("boostedTau_leadTkPtOverTauPt", 1);
   // fChain->SetBranchAddress("boostedTau_leadTkPtOverTauPt", boostedTau_leadTkPtOverTauPt, &b_boostedTau_leadTkPtOverTauPt);
   // fChain->SetBranchStatus("boostedTau_mass", 1);
   // fChain->SetBranchAddress("boostedTau_mass", boostedTau_mass, &b_boostedTau_mass);
   // fChain->SetBranchStatus("boostedTau_neutralIso", 1);
   // fChain->SetBranchAddress("boostedTau_neutralIso", boostedTau_neutralIso, &b_boostedTau_neutralIso);
   // fChain->SetBranchStatus("boostedTau_phi", 1);
   // fChain->SetBranchAddress("boostedTau_phi", boostedTau_phi, &b_boostedTau_phi);
   // fChain->SetBranchStatus("boostedTau_photonsOutsideSignalCone", 1);
   // fChain->SetBranchAddress("boostedTau_photonsOutsideSignalCone", boostedTau_photonsOutsideSignalCone, &b_boostedTau_photonsOutsideSignalCone);
   // fChain->SetBranchStatus("boostedTau_pt", 1);
   // fChain->SetBranchAddress("boostedTau_pt", boostedTau_pt, &b_boostedTau_pt);
   // fChain->SetBranchStatus("boostedTau_puCorr", 1);
   // fChain->SetBranchAddress("boostedTau_puCorr", boostedTau_puCorr, &b_boostedTau_puCorr);
   // fChain->SetBranchStatus("boostedTau_rawAntiEle2018", 1);
   // fChain->SetBranchAddress("boostedTau_rawAntiEle2018", boostedTau_rawAntiEle2018, &b_boostedTau_rawAntiEle2018);
   // fChain->SetBranchStatus("boostedTau_rawIso", 1);
   // fChain->SetBranchAddress("boostedTau_rawIso", boostedTau_rawIso, &b_boostedTau_rawIso);
   // fChain->SetBranchStatus("boostedTau_rawIsodR03", 1);
   // fChain->SetBranchAddress("boostedTau_rawIsodR03", boostedTau_rawIsodR03, &b_boostedTau_rawIsodR03);
   // fChain->SetBranchStatus("boostedTau_rawMVAnewDM2017v2", 1);
   // fChain->SetBranchAddress("boostedTau_rawMVAnewDM2017v2", boostedTau_rawMVAnewDM2017v2, &b_boostedTau_rawMVAnewDM2017v2);
   // fChain->SetBranchStatus("boostedTau_rawMVAoldDM2017v2", 1);
   // fChain->SetBranchAddress("boostedTau_rawMVAoldDM2017v2", boostedTau_rawMVAoldDM2017v2, &b_boostedTau_rawMVAoldDM2017v2);
   // fChain->SetBranchStatus("CaloMET_phi", 1);
   // fChain->SetBranchAddress("CaloMET_phi", &CaloMET_phi, &b_CaloMET_phi);
   // fChain->SetBranchStatus("CaloMET_pt", 1);
   // fChain->SetBranchAddress("CaloMET_pt", &CaloMET_pt, &b_CaloMET_pt);
   // fChain->SetBranchStatus("CaloMET_sumEt", 1);
   // fChain->SetBranchAddress("CaloMET_sumEt", &CaloMET_sumEt, &b_CaloMET_sumEt);
   // fChain->SetBranchStatus("ChsMET_phi", 1);
   // fChain->SetBranchAddress("ChsMET_phi", &ChsMET_phi, &b_ChsMET_phi);
   // fChain->SetBranchStatus("ChsMET_pt", 1);
   // fChain->SetBranchAddress("ChsMET_pt", &ChsMET_pt, &b_ChsMET_pt);
   // fChain->SetBranchStatus("ChsMET_sumEt", 1);
   // fChain->SetBranchAddress("ChsMET_sumEt", &ChsMET_sumEt, &b_ChsMET_sumEt);
   // fChain->SetBranchStatus("nCorrT1METJet", 1);
   // fChain->SetBranchAddress("nCorrT1METJet", &nCorrT1METJet, &b_nCorrT1METJet);
   // fChain->SetBranchStatus("CorrT1METJet_area", 1);
   // fChain->SetBranchAddress("CorrT1METJet_area", CorrT1METJet_area, &b_CorrT1METJet_area);
   // fChain->SetBranchStatus("CorrT1METJet_eta", 1);
   // fChain->SetBranchAddress("CorrT1METJet_eta", CorrT1METJet_eta, &b_CorrT1METJet_eta);
   // fChain->SetBranchStatus("CorrT1METJet_muonSubtrFactor", 1);
   // fChain->SetBranchAddress("CorrT1METJet_muonSubtrFactor", CorrT1METJet_muonSubtrFactor, &b_CorrT1METJet_muonSubtrFactor);
   // fChain->SetBranchStatus("CorrT1METJet_phi", 1);
   // fChain->SetBranchAddress("CorrT1METJet_phi", CorrT1METJet_phi, &b_CorrT1METJet_phi);
   // fChain->SetBranchStatus("CorrT1METJet_rawPt", 1);
   // fChain->SetBranchAddress("CorrT1METJet_rawPt", CorrT1METJet_rawPt, &b_CorrT1METJet_rawPt);
   // fChain->SetBranchStatus("DeepMETResolutionTune_phi", 1);
   // fChain->SetBranchAddress("DeepMETResolutionTune_phi", &DeepMETResolutionTune_phi, &b_DeepMETResolutionTune_phi);
   // fChain->SetBranchStatus("DeepMETResolutionTune_pt", 1);
   // fChain->SetBranchAddress("DeepMETResolutionTune_pt", &DeepMETResolutionTune_pt, &b_DeepMETResolutionTune_pt);
   // fChain->SetBranchStatus("DeepMETResponseTune_phi", 1);
   // fChain->SetBranchAddress("DeepMETResponseTune_phi", &DeepMETResponseTune_phi, &b_DeepMETResponseTune_phi);
   // fChain->SetBranchStatus("DeepMETResponseTune_pt", 1);
   // fChain->SetBranchAddress("DeepMETResponseTune_pt", &DeepMETResponseTune_pt, &b_DeepMETResponseTune_pt);
   fChain->SetBranchStatus("nElectron", 1);
   fChain->SetBranchAddress("nElectron", &nElectron, &b_nElectron);
   fChain->SetBranchStatus("Electron_seediEtaOriX", 1);
   fChain->SetBranchAddress("Electron_seediEtaOriX", Electron_seediEtaOriX, &b_Electron_seediEtaOriX);
   fChain->SetBranchStatus("Electron_convVeto", 1);
   fChain->SetBranchAddress("Electron_convVeto", Electron_convVeto, &b_Electron_convVeto);
   fChain->SetBranchStatus("Electron_cutBased", 1);
   fChain->SetBranchAddress("Electron_cutBased", Electron_cutBased, &b_Electron_cutBased);
   fChain->SetBranchStatus("Electron_cutBased_HEEP", 1);
   fChain->SetBranchAddress("Electron_cutBased_HEEP", Electron_cutBased_HEEP, &b_Electron_cutBased_HEEP);
   fChain->SetBranchStatus("Electron_isPFcand", 1);
   fChain->SetBranchAddress("Electron_isPFcand", Electron_isPFcand, &b_Electron_isPFcand);
   fChain->SetBranchStatus("Electron_jetNDauCharged", 1);
   fChain->SetBranchAddress("Electron_jetNDauCharged", Electron_jetNDauCharged, &b_Electron_jetNDauCharged);
   fChain->SetBranchStatus("Electron_lostHits", 1);
   fChain->SetBranchAddress("Electron_lostHits", Electron_lostHits, &b_Electron_lostHits);
   fChain->SetBranchStatus("Electron_mvaIso_WP80", 1);
   fChain->SetBranchAddress("Electron_mvaIso_WP80", Electron_mvaIso_WP80, &b_Electron_mvaIso_WP80);
   fChain->SetBranchStatus("Electron_mvaIso_WP90", 1);
   fChain->SetBranchAddress("Electron_mvaIso_WP90", Electron_mvaIso_WP90, &b_Electron_mvaIso_WP90);
   fChain->SetBranchStatus("Electron_mvaNoIso_WP80", 1);
   fChain->SetBranchAddress("Electron_mvaNoIso_WP80", Electron_mvaNoIso_WP80, &b_Electron_mvaNoIso_WP80);
   fChain->SetBranchStatus("Electron_mvaNoIso_WP90", 1);
   fChain->SetBranchAddress("Electron_mvaNoIso_WP90", Electron_mvaNoIso_WP90, &b_Electron_mvaNoIso_WP90);
   fChain->SetBranchStatus("Electron_seedGain", 1);
   fChain->SetBranchAddress("Electron_seedGain", Electron_seedGain, &b_Electron_seedGain);
   fChain->SetBranchStatus("Electron_tightCharge", 1);
   fChain->SetBranchAddress("Electron_tightCharge", Electron_tightCharge, &b_Electron_tightCharge);
   fChain->SetBranchStatus("Electron_jetIdx", 1);
   fChain->SetBranchAddress("Electron_jetIdx", Electron_jetIdx, &b_Electron_jetIdx);
   // fChain->SetBranchStatus("Electron_photonIdx", 1);
   // fChain->SetBranchAddress("Electron_photonIdx", Electron_photonIdx, &b_Electron_photonIdx);
   fChain->SetBranchStatus("Electron_svIdx", 1);
   fChain->SetBranchAddress("Electron_svIdx", Electron_svIdx, &b_Electron_svIdx);
   // fChain->SetBranchStatus("Electron_fsrPhotonIdx", 1);
   // fChain->SetBranchAddress("Electron_fsrPhotonIdx", Electron_fsrPhotonIdx, &b_Electron_fsrPhotonIdx);
   fChain->SetBranchStatus("Electron_charge", 1);
   fChain->SetBranchAddress("Electron_charge", Electron_charge, &b_Electron_charge);
   fChain->SetBranchStatus("Electron_pdgId", 1);
   fChain->SetBranchAddress("Electron_pdgId", Electron_pdgId, &b_Electron_pdgId);
   fChain->SetBranchStatus("Electron_seediPhiOriY", 1);
   fChain->SetBranchAddress("Electron_seediPhiOriY", Electron_seediPhiOriY, &b_Electron_seediPhiOriY);
   fChain->SetBranchStatus("Electron_vidNestedWPBitmap", 1);
   fChain->SetBranchAddress("Electron_vidNestedWPBitmap", Electron_vidNestedWPBitmap, &b_Electron_vidNestedWPBitmap);
   fChain->SetBranchStatus("Electron_vidNestedWPBitmapHEEP", 1);
   fChain->SetBranchAddress("Electron_vidNestedWPBitmapHEEP", Electron_vidNestedWPBitmapHEEP, &b_Electron_vidNestedWPBitmapHEEP);
   fChain->SetBranchStatus("Electron_deltaEtaSC", 1);
   fChain->SetBranchAddress("Electron_deltaEtaSC", Electron_deltaEtaSC, &b_Electron_deltaEtaSC);
   // fChain->SetBranchStatus("Electron_dr03EcalRecHitSumEt", 1);
   // fChain->SetBranchAddress("Electron_dr03EcalRecHitSumEt", Electron_dr03EcalRecHitSumEt, &b_Electron_dr03EcalRecHitSumEt);
   // fChain->SetBranchStatus("Electron_dr03HcalDepth1TowerSumEt", 1);
   // fChain->SetBranchAddress("Electron_dr03HcalDepth1TowerSumEt", Electron_dr03HcalDepth1TowerSumEt, &b_Electron_dr03HcalDepth1TowerSumEt);
   // fChain->SetBranchStatus("Electron_dr03TkSumPt", 1);
   // fChain->SetBranchAddress("Electron_dr03TkSumPt", Electron_dr03TkSumPt, &b_Electron_dr03TkSumPt);
   // fChain->SetBranchStatus("Electron_dr03TkSumPtHEEP", 1);
   // fChain->SetBranchAddress("Electron_dr03TkSumPtHEEP", Electron_dr03TkSumPtHEEP, &b_Electron_dr03TkSumPtHEEP);
   fChain->SetBranchStatus("Electron_dxy", 1);
   fChain->SetBranchAddress("Electron_dxy", Electron_dxy, &b_Electron_dxy);
   fChain->SetBranchStatus("Electron_dxyErr", 1);
   fChain->SetBranchAddress("Electron_dxyErr", Electron_dxyErr, &b_Electron_dxyErr);
   fChain->SetBranchStatus("Electron_dz", 1);
   fChain->SetBranchAddress("Electron_dz", Electron_dz, &b_Electron_dz);
   fChain->SetBranchStatus("Electron_dzErr", 1);
   fChain->SetBranchAddress("Electron_dzErr", Electron_dzErr, &b_Electron_dzErr);
   fChain->SetBranchStatus("Electron_eInvMinusPInv", 1);
   fChain->SetBranchAddress("Electron_eInvMinusPInv", Electron_eInvMinusPInv, &b_Electron_eInvMinusPInv);
   fChain->SetBranchStatus("Electron_energyErr", 1);
   fChain->SetBranchAddress("Electron_energyErr", Electron_energyErr, &b_Electron_energyErr);
   fChain->SetBranchStatus("Electron_eta", 1);
   fChain->SetBranchAddress("Electron_eta", Electron_eta, &b_Electron_eta);
   fChain->SetBranchStatus("Electron_hoe", 1);
   fChain->SetBranchAddress("Electron_hoe", Electron_hoe, &b_Electron_hoe);
   fChain->SetBranchStatus("Electron_ip3d", 1);
   fChain->SetBranchAddress("Electron_ip3d", Electron_ip3d, &b_Electron_ip3d);
   fChain->SetBranchStatus("Electron_jetPtRelv2", 1);
   fChain->SetBranchAddress("Electron_jetPtRelv2", Electron_jetPtRelv2, &b_Electron_jetPtRelv2);
   fChain->SetBranchStatus("Electron_jetRelIso", 1);
   fChain->SetBranchAddress("Electron_jetRelIso", Electron_jetRelIso, &b_Electron_jetRelIso);
   fChain->SetBranchStatus("Electron_mass", 1);
   fChain->SetBranchAddress("Electron_mass", Electron_mass, &b_Electron_mass);
   fChain->SetBranchStatus("Electron_miniPFRelIso_all", 1);
   fChain->SetBranchAddress("Electron_miniPFRelIso_all", Electron_miniPFRelIso_all, &b_Electron_miniPFRelIso_all);
   fChain->SetBranchStatus("Electron_miniPFRelIso_chg", 1);
   fChain->SetBranchAddress("Electron_miniPFRelIso_chg", Electron_miniPFRelIso_chg, &b_Electron_miniPFRelIso_chg);
   fChain->SetBranchStatus("Electron_mvaHZZIso", 1);
   fChain->SetBranchAddress("Electron_mvaHZZIso", Electron_mvaHZZIso, &b_Electron_mvaHZZIso);
   fChain->SetBranchStatus("Electron_mvaIso", 1);
   fChain->SetBranchAddress("Electron_mvaIso", Electron_mvaIso, &b_Electron_mvaIso);
   fChain->SetBranchStatus("Electron_mvaNoIso", 1);
   fChain->SetBranchAddress("Electron_mvaNoIso", Electron_mvaNoIso, &b_Electron_mvaNoIso);
   fChain->SetBranchStatus("Electron_pfRelIso03_all", 1);
   fChain->SetBranchAddress("Electron_pfRelIso03_all", Electron_pfRelIso03_all, &b_Electron_pfRelIso03_all);
   fChain->SetBranchStatus("Electron_pfRelIso03_chg", 1);
   fChain->SetBranchAddress("Electron_pfRelIso03_chg", Electron_pfRelIso03_chg, &b_Electron_pfRelIso03_chg);
   fChain->SetBranchStatus("Electron_phi", 1);
   fChain->SetBranchAddress("Electron_phi", Electron_phi, &b_Electron_phi);
   fChain->SetBranchStatus("Electron_pt", 1);
   fChain->SetBranchAddress("Electron_pt", Electron_pt, &b_Electron_pt);
   fChain->SetBranchStatus("Electron_r9", 1);
   fChain->SetBranchAddress("Electron_r9", Electron_r9, &b_Electron_r9);
   fChain->SetBranchStatus("Electron_scEtOverPt", 1);
   fChain->SetBranchAddress("Electron_scEtOverPt", Electron_scEtOverPt, &b_Electron_scEtOverPt);
   fChain->SetBranchStatus("Electron_sieie", 1);
   fChain->SetBranchAddress("Electron_sieie", Electron_sieie, &b_Electron_sieie);
   fChain->SetBranchStatus("Electron_sip3d", 1);
   fChain->SetBranchAddress("Electron_sip3d", Electron_sip3d, &b_Electron_sip3d);
   //fChain->SetBranchStatus("Electron_mvaTTH", 1);
   //fChain->SetBranchAddress("Electron_mvaTTH", Electron_mvaTTH, &b_Electron_mvaTTH);
   fChain->SetBranchStatus("nFatJet", 1);
   fChain->SetBranchAddress("nFatJet", &nFatJet, &b_nFatJet);
   //fChain->SetBranchStatus("FatJet_jetId", 1);
   //fChain->SetBranchAddress("FatJet_jetId", FatJet_jetId, &b_FatJet_jetId);
   fChain->SetBranchStatus("FatJet_nConstituents", 1);
   fChain->SetBranchAddress("FatJet_nConstituents", FatJet_nConstituents, &b_FatJet_nConstituents);
   fChain->SetBranchStatus("FatJet_subJetIdx1", 1);
   fChain->SetBranchAddress("FatJet_subJetIdx1", FatJet_subJetIdx1, &b_FatJet_subJetIdx1);
   fChain->SetBranchStatus("FatJet_subJetIdx2", 1);
   fChain->SetBranchAddress("FatJet_subJetIdx2", FatJet_subJetIdx2, &b_FatJet_subJetIdx2);
   fChain->SetBranchStatus("FatJet_electronIdx3SJ", 1);
   fChain->SetBranchAddress("FatJet_electronIdx3SJ", FatJet_electronIdx3SJ, &b_FatJet_electronIdx3SJ);
   fChain->SetBranchStatus("FatJet_muonIdx3SJ", 1);
   fChain->SetBranchAddress("FatJet_muonIdx3SJ", FatJet_muonIdx3SJ, &b_FatJet_muonIdx3SJ);
   fChain->SetBranchStatus("FatJet_area", 1);
   fChain->SetBranchAddress("FatJet_area", FatJet_area, &b_FatJet_area);
   //fChain->SetBranchStatus("FatJet_btagDDBvLV2", 1);
   //fChain->SetBranchAddress("FatJet_btagDDBvLV2", FatJet_btagDDBvLV2, &b_FatJet_btagDDBvLV2);
   //fChain->SetBranchStatus("FatJet_btagDDCvBV2", 1);
   //fChain->SetBranchAddress("FatJet_btagDDCvBV2", FatJet_btagDDCvBV2, &b_FatJet_btagDDCvBV2);
   //fChain->SetBranchStatus("FatJet_btagDDCvLV2", 1);
   //fChain->SetBranchAddress("FatJet_btagDDCvLV2", FatJet_btagDDCvLV2, &b_FatJet_btagDDCvLV2);
   //fChain->SetBranchStatus("FatJet_btagDeepB", 1);
   //fChain->SetBranchAddress("FatJet_btagDeepB", FatJet_btagDeepB, &b_FatJet_btagDeepB);
   //fChain->SetBranchStatus("FatJet_btagHbb", 1);
   //fChain->SetBranchAddress("FatJet_btagHbb", FatJet_btagHbb, &b_FatJet_btagHbb);
   fChain->SetBranchStatus("FatJet_eta", 1);
   fChain->SetBranchAddress("FatJet_eta", FatJet_eta, &b_FatJet_eta);
   fChain->SetBranchStatus("FatJet_mass", 1);
   fChain->SetBranchAddress("FatJet_mass", FatJet_mass, &b_FatJet_mass);
   fChain->SetBranchStatus("FatJet_msoftdrop", 1);
   fChain->SetBranchAddress("FatJet_msoftdrop", FatJet_msoftdrop, &b_FatJet_msoftdrop);
   fChain->SetBranchStatus("FatJet_n2b1", 1);
   fChain->SetBranchAddress("FatJet_n2b1", FatJet_n2b1, &b_FatJet_n2b1);
   fChain->SetBranchStatus("FatJet_n3b1", 1);
   fChain->SetBranchAddress("FatJet_n3b1", FatJet_n3b1, &b_FatJet_n3b1);
   // fChain->SetBranchStatus("FatJet_particleNetWithMass_H4qvsQCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNetWithMass_H4qvsQCD", FatJet_particleNetWithMass_H4qvsQCD, &b_FatJet_particleNetWithMass_H4qvsQCD);
   // fChain->SetBranchStatus("FatJet_particleNetWithMass_HbbvsQCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNetWithMass_HbbvsQCD", FatJet_particleNetWithMass_HbbvsQCD, &b_FatJet_particleNetWithMass_HbbvsQCD);
   // fChain->SetBranchStatus("FatJet_particleNetWithMass_HccvsQCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNetWithMass_HccvsQCD", FatJet_particleNetWithMass_HccvsQCD, &b_FatJet_particleNetWithMass_HccvsQCD);
   // fChain->SetBranchStatus("FatJet_particleNetWithMass_QCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNetWithMass_QCD", FatJet_particleNetWithMass_QCD, &b_FatJet_particleNetWithMass_QCD);
   // fChain->SetBranchStatus("FatJet_particleNetWithMass_TvsQCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNetWithMass_TvsQCD", FatJet_particleNetWithMass_TvsQCD, &b_FatJet_particleNetWithMass_TvsQCD);
   // fChain->SetBranchStatus("FatJet_particleNetWithMass_WvsQCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNetWithMass_WvsQCD", FatJet_particleNetWithMass_WvsQCD, &b_FatJet_particleNetWithMass_WvsQCD);
   // fChain->SetBranchStatus("FatJet_particleNetWithMass_ZvsQCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNetWithMass_ZvsQCD", FatJet_particleNetWithMass_ZvsQCD, &b_FatJet_particleNetWithMass_ZvsQCD);
   // fChain->SetBranchStatus("FatJet_particleNet_QCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNet_QCD", FatJet_particleNet_QCD, &b_FatJet_particleNet_QCD);
   // fChain->SetBranchStatus("FatJet_particleNet_QCD0HF", 1);
   // fChain->SetBranchAddress("FatJet_particleNet_QCD0HF", FatJet_particleNet_QCD0HF, &b_FatJet_particleNet_QCD0HF);
   // fChain->SetBranchStatus("FatJet_particleNet_QCD1HF", 1);
   // fChain->SetBranchAddress("FatJet_particleNet_QCD1HF", FatJet_particleNet_QCD1HF, &b_FatJet_particleNet_QCD1HF);
   // fChain->SetBranchStatus("FatJet_particleNet_QCD2HF", 1);
   // fChain->SetBranchAddress("FatJet_particleNet_QCD2HF", FatJet_particleNet_QCD2HF, &b_FatJet_particleNet_QCD2HF);
   // fChain->SetBranchStatus("FatJet_particleNet_XbbVsQCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNet_XbbVsQCD", FatJet_particleNet_XbbVsQCD, &b_FatJet_particleNet_XbbVsQCD);
   // fChain->SetBranchStatus("FatJet_particleNet_XccVsQCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNet_XccVsQCD", FatJet_particleNet_XccVsQCD, &b_FatJet_particleNet_XccVsQCD);
   // fChain->SetBranchStatus("FatJet_particleNet_XggVsQCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNet_XggVsQCD", FatJet_particleNet_XggVsQCD, &b_FatJet_particleNet_XggVsQCD);
   // fChain->SetBranchStatus("FatJet_particleNet_XqqVsQCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNet_XqqVsQCD", FatJet_particleNet_XqqVsQCD, &b_FatJet_particleNet_XqqVsQCD);
   // fChain->SetBranchStatus("FatJet_particleNet_XteVsQCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNet_XteVsQCD", FatJet_particleNet_XteVsQCD, &b_FatJet_particleNet_XteVsQCD);
   // fChain->SetBranchStatus("FatJet_particleNet_XtmVsQCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNet_XtmVsQCD", FatJet_particleNet_XtmVsQCD, &b_FatJet_particleNet_XtmVsQCD);
   // fChain->SetBranchStatus("FatJet_particleNet_XttVsQCD", 1);
   // fChain->SetBranchAddress("FatJet_particleNet_XttVsQCD", FatJet_particleNet_XttVsQCD, &b_FatJet_particleNet_XttVsQCD);
   // fChain->SetBranchStatus("FatJet_particleNet_massCorr", 1);
   // fChain->SetBranchAddress("FatJet_particleNet_massCorr", FatJet_particleNet_massCorr, &b_FatJet_particleNet_massCorr);
   fChain->SetBranchStatus("FatJet_phi", 1);
   fChain->SetBranchAddress("FatJet_phi", FatJet_phi, &b_FatJet_phi);
   fChain->SetBranchStatus("FatJet_pt", 1);
   fChain->SetBranchAddress("FatJet_pt", FatJet_pt, &b_FatJet_pt);
   fChain->SetBranchStatus("FatJet_rawFactor", 1);
   fChain->SetBranchAddress("FatJet_rawFactor", FatJet_rawFactor, &b_FatJet_rawFactor);
   fChain->SetBranchStatus("FatJet_tau1", 1);
   fChain->SetBranchAddress("FatJet_tau1", FatJet_tau1, &b_FatJet_tau1);
   fChain->SetBranchStatus("FatJet_tau2", 1);
   fChain->SetBranchAddress("FatJet_tau2", FatJet_tau2, &b_FatJet_tau2);
   fChain->SetBranchStatus("FatJet_tau3", 1);
   fChain->SetBranchAddress("FatJet_tau3", FatJet_tau3, &b_FatJet_tau3);
   fChain->SetBranchStatus("FatJet_tau4", 1);
   fChain->SetBranchAddress("FatJet_tau4", FatJet_tau4, &b_FatJet_tau4);
   fChain->SetBranchStatus("FatJet_lsf3", 1);
   fChain->SetBranchAddress("FatJet_lsf3", FatJet_lsf3, &b_FatJet_lsf3);
   // fChain->SetBranchStatus("nFsrPhoton", 1);
   // fChain->SetBranchAddress("nFsrPhoton", &nFsrPhoton, &b_nFsrPhoton);
   // fChain->SetBranchStatus("FsrPhoton_electronIdx", 1);
   // fChain->SetBranchAddress("FsrPhoton_electronIdx", FsrPhoton_electronIdx, &b_FsrPhoton_electronIdx);
   // fChain->SetBranchStatus("FsrPhoton_muonIdx", 1);
   // fChain->SetBranchAddress("FsrPhoton_muonIdx", FsrPhoton_muonIdx, &b_FsrPhoton_muonIdx);
   // fChain->SetBranchStatus("FsrPhoton_dROverEt2", 1);
   // fChain->SetBranchAddress("FsrPhoton_dROverEt2", FsrPhoton_dROverEt2, &b_FsrPhoton_dROverEt2);
   // fChain->SetBranchStatus("FsrPhoton_eta", 1);
   // fChain->SetBranchAddress("FsrPhoton_eta", FsrPhoton_eta, &b_FsrPhoton_eta);
   // fChain->SetBranchStatus("FsrPhoton_phi", 1);
   // fChain->SetBranchAddress("FsrPhoton_phi", FsrPhoton_phi, &b_FsrPhoton_phi);
   // fChain->SetBranchStatus("FsrPhoton_pt", 1);
   // fChain->SetBranchAddress("FsrPhoton_pt", FsrPhoton_pt, &b_FsrPhoton_pt);
   // fChain->SetBranchStatus("FsrPhoton_relIso03", 1);
   // fChain->SetBranchAddress("FsrPhoton_relIso03", FsrPhoton_relIso03, &b_FsrPhoton_relIso03);
   // fChain->SetBranchStatus("nIsoTrack", 1);
   // fChain->SetBranchAddress("nIsoTrack", &nIsoTrack, &b_nIsoTrack);
   // fChain->SetBranchStatus("IsoTrack_isHighPurityTrack", 1);
   // fChain->SetBranchAddress("IsoTrack_isHighPurityTrack", IsoTrack_isHighPurityTrack, &b_IsoTrack_isHighPurityTrack);
   // fChain->SetBranchStatus("IsoTrack_isPFcand", 1);
   // fChain->SetBranchAddress("IsoTrack_isPFcand", IsoTrack_isPFcand, &b_IsoTrack_isPFcand);
   // fChain->SetBranchStatus("IsoTrack_isFromLostTrack", 1);
   // fChain->SetBranchAddress("IsoTrack_isFromLostTrack", IsoTrack_isFromLostTrack, &b_IsoTrack_isFromLostTrack);
   // fChain->SetBranchStatus("IsoTrack_charge", 1);
   // fChain->SetBranchAddress("IsoTrack_charge", IsoTrack_charge, &b_IsoTrack_charge);
   // fChain->SetBranchStatus("IsoTrack_fromPV", 1);
   // fChain->SetBranchAddress("IsoTrack_fromPV", IsoTrack_fromPV, &b_IsoTrack_fromPV);
   // fChain->SetBranchStatus("IsoTrack_pdgId", 1);
   // fChain->SetBranchAddress("IsoTrack_pdgId", IsoTrack_pdgId, &b_IsoTrack_pdgId);
   // fChain->SetBranchStatus("IsoTrack_dxy", 1);
   // fChain->SetBranchAddress("IsoTrack_dxy", IsoTrack_dxy, &b_IsoTrack_dxy);
   // fChain->SetBranchStatus("IsoTrack_dz", 1);
   // fChain->SetBranchAddress("IsoTrack_dz", IsoTrack_dz, &b_IsoTrack_dz);
   // fChain->SetBranchStatus("IsoTrack_eta", 1);
   // fChain->SetBranchAddress("IsoTrack_eta", IsoTrack_eta, &b_IsoTrack_eta);
   // fChain->SetBranchStatus("IsoTrack_pfRelIso03_all", 1);
   // fChain->SetBranchAddress("IsoTrack_pfRelIso03_all", IsoTrack_pfRelIso03_all, &b_IsoTrack_pfRelIso03_all);
   // fChain->SetBranchStatus("IsoTrack_pfRelIso03_chg", 1);
   // fChain->SetBranchAddress("IsoTrack_pfRelIso03_chg", IsoTrack_pfRelIso03_chg, &b_IsoTrack_pfRelIso03_chg);
   // fChain->SetBranchStatus("IsoTrack_phi", 1);
   // fChain->SetBranchAddress("IsoTrack_phi", IsoTrack_phi, &b_IsoTrack_phi);
   // fChain->SetBranchStatus("IsoTrack_pt", 1);
   // fChain->SetBranchAddress("IsoTrack_pt", IsoTrack_pt, &b_IsoTrack_pt);
   // fChain->SetBranchStatus("IsoTrack_miniPFRelIso_all", 1);
   // fChain->SetBranchAddress("IsoTrack_miniPFRelIso_all", IsoTrack_miniPFRelIso_all, &b_IsoTrack_miniPFRelIso_all);
   // fChain->SetBranchStatus("IsoTrack_miniPFRelIso_chg", 1);
   // fChain->SetBranchAddress("IsoTrack_miniPFRelIso_chg", IsoTrack_miniPFRelIso_chg, &b_IsoTrack_miniPFRelIso_chg);
   fChain->SetBranchStatus("nJet", 1);
   fChain->SetBranchAddress("nJet", &nJet, &b_nJet);

   if(nanoAODVersion == "v12"){
      std::cout << "USING NANOAOD v12 BRANCHES" << std::endl;
      fChain->SetBranchStatus("Jet_jetId", 1);
      fChain->SetBranchAddress("Jet_jetId", Jet_jetId, &b_Jet_jetId);
   }
   else if (nanoAODVersion == "v15"){
      std::cout << "USING NANOAOD v15 BRANCHES" << std::endl;
      fChain->SetBranchStatus("Jet_chMultiplicity", 1);
      fChain->SetBranchAddress("Jet_chMultiplicity", Jet_chMultiplicity, &b_Jet_chMultiplicity);
      fChain->SetBranchStatus("Jet_neMultiplicity", 1);
      fChain->SetBranchAddress("Jet_neMultiplicity", Jet_neMultiplicity, &b_Jet_neMultiplicity);
   }

   fChain->SetBranchStatus("Jet_nConstituents", 1);
   fChain->SetBranchAddress("Jet_nConstituents", Jet_nConstituents, &b_Jet_nConstituents);
   fChain->SetBranchStatus("Jet_nElectrons", 1);
   fChain->SetBranchAddress("Jet_nElectrons", Jet_nElectrons, &b_Jet_nElectrons);
   fChain->SetBranchStatus("Jet_nMuons", 1);
   fChain->SetBranchAddress("Jet_nMuons", Jet_nMuons, &b_Jet_nMuons);
   fChain->SetBranchStatus("Jet_nSVs", 1);
   fChain->SetBranchAddress("Jet_nSVs", Jet_nSVs, &b_Jet_nSVs);
   fChain->SetBranchStatus("Jet_electronIdx1", 1);
   fChain->SetBranchAddress("Jet_electronIdx1", Jet_electronIdx1, &b_Jet_electronIdx1);
   fChain->SetBranchStatus("Jet_electronIdx2", 1);
   fChain->SetBranchAddress("Jet_electronIdx2", Jet_electronIdx2, &b_Jet_electronIdx2);
   fChain->SetBranchStatus("Jet_muonIdx1", 1);
   fChain->SetBranchAddress("Jet_muonIdx1", Jet_muonIdx1, &b_Jet_muonIdx1);
   fChain->SetBranchStatus("Jet_muonIdx2", 1);
   fChain->SetBranchAddress("Jet_muonIdx2", Jet_muonIdx2, &b_Jet_muonIdx2);
   fChain->SetBranchStatus("Jet_svIdx1", 1);
   fChain->SetBranchAddress("Jet_svIdx1", Jet_svIdx1, &b_Jet_svIdx1);
   fChain->SetBranchStatus("Jet_svIdx2", 1);
   fChain->SetBranchAddress("Jet_svIdx2", Jet_svIdx2, &b_Jet_svIdx2);
   fChain->SetBranchStatus("Jet_hfadjacentEtaStripsSize", 1);
   fChain->SetBranchAddress("Jet_hfadjacentEtaStripsSize", Jet_hfadjacentEtaStripsSize, &b_Jet_hfadjacentEtaStripsSize);
   fChain->SetBranchStatus("Jet_hfcentralEtaStripSize", 1);
   fChain->SetBranchAddress("Jet_hfcentralEtaStripSize", Jet_hfcentralEtaStripSize, &b_Jet_hfcentralEtaStripSize);
   fChain->SetBranchStatus("Jet_PNetRegPtRawCorr", 1);
   fChain->SetBranchAddress("Jet_PNetRegPtRawCorr", Jet_PNetRegPtRawCorr, &b_Jet_PNetRegPtRawCorr);
   fChain->SetBranchStatus("Jet_PNetRegPtRawCorrNeutrino", 1);
   fChain->SetBranchAddress("Jet_PNetRegPtRawCorrNeutrino", Jet_PNetRegPtRawCorrNeutrino, &b_Jet_PNetRegPtRawCorrNeutrino);
   fChain->SetBranchStatus("Jet_PNetRegPtRawRes", 1);
   fChain->SetBranchAddress("Jet_PNetRegPtRawRes", Jet_PNetRegPtRawRes, &b_Jet_PNetRegPtRawRes);
   fChain->SetBranchStatus("Jet_area", 1);
   fChain->SetBranchAddress("Jet_area", Jet_area, &b_Jet_area);
   fChain->SetBranchStatus("Jet_btagDeepFlavB", 1);
   fChain->SetBranchAddress("Jet_btagDeepFlavB", Jet_btagDeepFlavB, &b_Jet_btagDeepFlavB);
   fChain->SetBranchStatus("Jet_btagDeepFlavCvB", 1);
   fChain->SetBranchAddress("Jet_btagDeepFlavCvB", Jet_btagDeepFlavCvB, &b_Jet_btagDeepFlavCvB);
   fChain->SetBranchStatus("Jet_btagDeepFlavCvL", 1);
   fChain->SetBranchAddress("Jet_btagDeepFlavCvL", Jet_btagDeepFlavCvL, &b_Jet_btagDeepFlavCvL);
   fChain->SetBranchStatus("Jet_btagDeepFlavQG", 1);
   fChain->SetBranchAddress("Jet_btagDeepFlavQG", Jet_btagDeepFlavQG, &b_Jet_btagDeepFlavQG);
   fChain->SetBranchStatus("Jet_btagPNetB", 1);
   fChain->SetBranchAddress("Jet_btagPNetB", Jet_btagPNetB, &b_Jet_btagPNetB);
   fChain->SetBranchStatus("Jet_btagPNetCvB", 1);
   fChain->SetBranchAddress("Jet_btagPNetCvB", Jet_btagPNetCvB, &b_Jet_btagPNetCvB);
   fChain->SetBranchStatus("Jet_btagPNetCvL", 1);
   fChain->SetBranchAddress("Jet_btagPNetCvL", Jet_btagPNetCvL, &b_Jet_btagPNetCvL);
   fChain->SetBranchStatus("Jet_btagPNetQvG", 1);
   fChain->SetBranchAddress("Jet_btagPNetQvG", Jet_btagPNetQvG, &b_Jet_btagPNetQvG);
   fChain->SetBranchStatus("Jet_btagPNetTauVJet", 1);
   fChain->SetBranchAddress("Jet_btagPNetTauVJet", Jet_btagPNetTauVJet, &b_Jet_btagPNetTauVJet);
   //fChain->SetBranchStatus("Jet_btagRobustParTAK4B", 1);
   //fChain->SetBranchAddress("Jet_btagRobustParTAK4B", Jet_btagRobustParTAK4B, &b_Jet_btagRobustParTAK4B);
   //fChain->SetBranchStatus("Jet_btagRobustParTAK4CvB", 1);
   //fChain->SetBranchAddress("Jet_btagRobustParTAK4CvB", Jet_btagRobustParTAK4CvB, &b_Jet_btagRobustParTAK4CvB);
   //fChain->SetBranchStatus("Jet_btagRobustParTAK4CvL", 1);
   //fChain->SetBranchAddress("Jet_btagRobustParTAK4CvL", Jet_btagRobustParTAK4CvL, &b_Jet_btagRobustParTAK4CvL);
   //fChain->SetBranchStatus("Jet_btagRobustParTAK4QG", 1);
   //fChain->SetBranchAddress("Jet_btagRobustParTAK4QG", Jet_btagRobustParTAK4QG, &b_Jet_btagRobustParTAK4QG);
   fChain->SetBranchStatus("Jet_chEmEF", 1);
   fChain->SetBranchAddress("Jet_chEmEF", Jet_chEmEF, &b_Jet_chEmEF);
   fChain->SetBranchStatus("Jet_chHEF", 1);
   fChain->SetBranchAddress("Jet_chHEF", Jet_chHEF, &b_Jet_chHEF);
   fChain->SetBranchStatus("Jet_eta", 1);
   fChain->SetBranchAddress("Jet_eta", Jet_eta, &b_Jet_eta);
   //cout << "Jet eta: " << Jet_eta;
   //cout << "Jet eta: " << Jet_eta;
   fChain->SetBranchStatus("Jet_hfsigmaEtaEta", 1);
   fChain->SetBranchAddress("Jet_hfsigmaEtaEta", Jet_hfsigmaEtaEta, &b_Jet_hfsigmaEtaEta);
   fChain->SetBranchStatus("Jet_hfsigmaPhiPhi", 1);
   fChain->SetBranchAddress("Jet_hfsigmaPhiPhi", Jet_hfsigmaPhiPhi, &b_Jet_hfsigmaPhiPhi);
   fChain->SetBranchStatus("Jet_mass", 1);
   fChain->SetBranchAddress("Jet_mass", Jet_mass, &b_Jet_mass);
   fChain->SetBranchStatus("Jet_muEF", 1);
   fChain->SetBranchAddress("Jet_muEF", Jet_muEF, &b_Jet_muEF);
   fChain->SetBranchStatus("Jet_muonSubtrFactor", 1);
   fChain->SetBranchAddress("Jet_muonSubtrFactor", Jet_muonSubtrFactor, &b_Jet_muonSubtrFactor);
   fChain->SetBranchStatus("Jet_neEmEF", 1);
   fChain->SetBranchAddress("Jet_neEmEF", Jet_neEmEF, &b_Jet_neEmEF);
   fChain->SetBranchStatus("Jet_neHEF", 1);
   fChain->SetBranchAddress("Jet_neHEF", Jet_neHEF, &b_Jet_neHEF);
   fChain->SetBranchStatus("Jet_phi", 1);
   fChain->SetBranchAddress("Jet_phi", Jet_phi, &b_Jet_phi);
   fChain->SetBranchStatus("Jet_pt", 1);
   fChain->SetBranchAddress("Jet_pt", Jet_pt, &b_Jet_pt);
   fChain->SetBranchStatus("Jet_rawFactor", 1);
   fChain->SetBranchAddress("Jet_rawFactor", Jet_rawFactor, &b_Jet_rawFactor);
   // fChain->SetBranchStatus("nLowPtElectron", 1);
   // fChain->SetBranchAddress("nLowPtElectron", &nLowPtElectron, &b_nLowPtElectron);
   // fChain->SetBranchStatus("LowPtElectron_convVeto", 1);
   // fChain->SetBranchAddress("LowPtElectron_convVeto", LowPtElectron_convVeto, &b_LowPtElectron_convVeto);
   // fChain->SetBranchStatus("LowPtElectron_convWP", 1);
   // fChain->SetBranchAddress("LowPtElectron_convWP", LowPtElectron_convWP, &b_LowPtElectron_convWP);
   // fChain->SetBranchStatus("LowPtElectron_lostHits", 1);
   // fChain->SetBranchAddress("LowPtElectron_lostHits", LowPtElectron_lostHits, &b_LowPtElectron_lostHits);
   // fChain->SetBranchStatus("LowPtElectron_electronIdx", 1);
   // fChain->SetBranchAddress("LowPtElectron_electronIdx", LowPtElectron_electronIdx, &b_LowPtElectron_electronIdx);
   // fChain->SetBranchStatus("LowPtElectron_photonIdx", 1);
   // fChain->SetBranchAddress("LowPtElectron_photonIdx", LowPtElectron_photonIdx, &b_LowPtElectron_photonIdx);
   // fChain->SetBranchStatus("LowPtElectron_charge", 1);
   // fChain->SetBranchAddress("LowPtElectron_charge", LowPtElectron_charge, &b_LowPtElectron_charge);
   // fChain->SetBranchStatus("LowPtElectron_pdgId", 1);
   // fChain->SetBranchAddress("LowPtElectron_pdgId", LowPtElectron_pdgId, &b_LowPtElectron_pdgId);
   // fChain->SetBranchStatus("LowPtElectron_ID", 1);
   // fChain->SetBranchAddress("LowPtElectron_ID", LowPtElectron_ID, &b_LowPtElectron_ID);
   // fChain->SetBranchStatus("LowPtElectron_convVtxRadius", 1);
   // fChain->SetBranchAddress("LowPtElectron_convVtxRadius", LowPtElectron_convVtxRadius, &b_LowPtElectron_convVtxRadius);
   // fChain->SetBranchStatus("LowPtElectron_deltaEtaSC", 1);
   // fChain->SetBranchAddress("LowPtElectron_deltaEtaSC", LowPtElectron_deltaEtaSC, &b_LowPtElectron_deltaEtaSC);
   // fChain->SetBranchStatus("LowPtElectron_dxy", 1);
   // fChain->SetBranchAddress("LowPtElectron_dxy", LowPtElectron_dxy, &b_LowPtElectron_dxy);
   // fChain->SetBranchStatus("LowPtElectron_dxyErr", 1);
   // fChain->SetBranchAddress("LowPtElectron_dxyErr", LowPtElectron_dxyErr, &b_LowPtElectron_dxyErr);
   // fChain->SetBranchStatus("LowPtElectron_dz", 1);
   // fChain->SetBranchAddress("LowPtElectron_dz", LowPtElectron_dz, &b_LowPtElectron_dz);
   // fChain->SetBranchStatus("LowPtElectron_dzErr", 1);
   // fChain->SetBranchAddress("LowPtElectron_dzErr", LowPtElectron_dzErr, &b_LowPtElectron_dzErr);
   // fChain->SetBranchStatus("LowPtElectron_eInvMinusPInv", 1);
   // fChain->SetBranchAddress("LowPtElectron_eInvMinusPInv", LowPtElectron_eInvMinusPInv, &b_LowPtElectron_eInvMinusPInv);
   // fChain->SetBranchStatus("LowPtElectron_energyErr", 1);
   // fChain->SetBranchAddress("LowPtElectron_energyErr", LowPtElectron_energyErr, &b_LowPtElectron_energyErr);
   // fChain->SetBranchStatus("LowPtElectron_eta", 1);
   // fChain->SetBranchAddress("LowPtElectron_eta", LowPtElectron_eta, &b_LowPtElectron_eta);
   // fChain->SetBranchStatus("LowPtElectron_hoe", 1);
   // fChain->SetBranchAddress("LowPtElectron_hoe", LowPtElectron_hoe, &b_LowPtElectron_hoe);
   // fChain->SetBranchStatus("LowPtElectron_mass", 1);
   // fChain->SetBranchAddress("LowPtElectron_mass", LowPtElectron_mass, &b_LowPtElectron_mass);
   // fChain->SetBranchStatus("LowPtElectron_miniPFRelIso_all", 1);
   // fChain->SetBranchAddress("LowPtElectron_miniPFRelIso_all", LowPtElectron_miniPFRelIso_all, &b_LowPtElectron_miniPFRelIso_all);
   // fChain->SetBranchStatus("LowPtElectron_miniPFRelIso_chg", 1);
   // fChain->SetBranchAddress("LowPtElectron_miniPFRelIso_chg", LowPtElectron_miniPFRelIso_chg, &b_LowPtElectron_miniPFRelIso_chg);
   // fChain->SetBranchStatus("LowPtElectron_phi", 1);
   // fChain->SetBranchAddress("LowPtElectron_phi", LowPtElectron_phi, &b_LowPtElectron_phi);
   // fChain->SetBranchStatus("LowPtElectron_pt", 1);
   // fChain->SetBranchAddress("LowPtElectron_pt", LowPtElectron_pt, &b_LowPtElectron_pt);
   // fChain->SetBranchStatus("LowPtElectron_ptbiased", 1);
   // fChain->SetBranchAddress("LowPtElectron_ptbiased", LowPtElectron_ptbiased, &b_LowPtElectron_ptbiased);
   // fChain->SetBranchStatus("LowPtElectron_r9", 1);
   // fChain->SetBranchAddress("LowPtElectron_r9", LowPtElectron_r9, &b_LowPtElectron_r9);
   // fChain->SetBranchStatus("LowPtElectron_scEtOverPt", 1);
   // fChain->SetBranchAddress("LowPtElectron_scEtOverPt", LowPtElectron_scEtOverPt, &b_LowPtElectron_scEtOverPt);
   // fChain->SetBranchStatus("LowPtElectron_sieie", 1);
   // fChain->SetBranchAddress("LowPtElectron_sieie", LowPtElectron_sieie, &b_LowPtElectron_sieie);
   // fChain->SetBranchStatus("LowPtElectron_unbiased", 1);
   // fChain->SetBranchAddress("LowPtElectron_unbiased", LowPtElectron_unbiased, &b_LowPtElectron_unbiased);
   //fChain->SetBranchStatus("MET_MetUnclustEnUpDeltaX", 1);
   //fChain->SetBranchAddress("MET_MetUnclustEnUpDeltaX", &MET_MetUnclustEnUpDeltaX, &b_MET_MetUnclustEnUpDeltaX);
   //fChain->SetBranchStatus("MET_MetUnclustEnUpDeltaY", 1);
   //fChain->SetBranchAddress("MET_MetUnclustEnUpDeltaY", &MET_MetUnclustEnUpDeltaY, &b_MET_MetUnclustEnUpDeltaY);
   //fChain->SetBranchStatus("MET_covXX", 1);
   //fChain->SetBranchAddress("MET_covXX", &MET_covXX, &b_MET_covXX);
   //fChain->SetBranchStatus("MET_covXY", 1);
   //fChain->SetBranchAddress("MET_covXY", &MET_covXY, &b_MET_covXY);
   //fChain->SetBranchStatus("MET_covYY", 1);
   //fChain->SetBranchAddress("MET_covYY", &MET_covYY, &b_MET_covYY);
   // fChain->SetBranchStatus("MET_phi", 1);
   // fChain->SetBranchAddress("MET_phi", &MET_phi, &b_MET_phi);
   // fChain->SetBranchStatus("MET_pt", 1);
   // fChain->SetBranchAddress("MET_pt", &MET_pt, &b_MET_pt);
   //fChain->SetBranchStatus("MET_significance", 1);
   //fChain->SetBranchAddress("MET_significance", &MET_significance, &b_MET_significance);
   // fChain->SetBranchStatus("MET_sumEt", 1);
   // fChain->SetBranchAddress("MET_sumEt", &MET_sumEt, &b_MET_sumEt);
   //fChain->SetBranchStatus("MET_sumPtUnclustered", 1);
   //fChain->SetBranchAddress("MET_sumPtUnclustered", &MET_sumPtUnclustered, &b_MET_sumPtUnclustered);
   fChain->SetBranchStatus("nMuon", 1);
   fChain->SetBranchAddress("nMuon", &nMuon, &b_nMuon);
   fChain->SetBranchStatus("Muon_highPtId", 1);
   fChain->SetBranchAddress("Muon_highPtId", Muon_highPtId, &b_Muon_highPtId);
   fChain->SetBranchStatus("Muon_highPurity", 1);
   fChain->SetBranchAddress("Muon_highPurity", Muon_highPurity, &b_Muon_highPurity);
   fChain->SetBranchStatus("Muon_inTimeMuon", 1);
   fChain->SetBranchAddress("Muon_inTimeMuon", Muon_inTimeMuon, &b_Muon_inTimeMuon);
   fChain->SetBranchStatus("Muon_isGlobal", 1);
   fChain->SetBranchAddress("Muon_isGlobal", Muon_isGlobal, &b_Muon_isGlobal);
   fChain->SetBranchStatus("Muon_isPFcand", 1);
   fChain->SetBranchAddress("Muon_isPFcand", Muon_isPFcand, &b_Muon_isPFcand);
   fChain->SetBranchStatus("Muon_isStandalone", 1);
   fChain->SetBranchAddress("Muon_isStandalone", Muon_isStandalone, &b_Muon_isStandalone);
   fChain->SetBranchStatus("Muon_isTracker", 1);
   fChain->SetBranchAddress("Muon_isTracker", Muon_isTracker, &b_Muon_isTracker);
   fChain->SetBranchStatus("Muon_jetNDauCharged", 1);
   fChain->SetBranchAddress("Muon_jetNDauCharged", Muon_jetNDauCharged, &b_Muon_jetNDauCharged);
   fChain->SetBranchStatus("Muon_looseId", 1);
   fChain->SetBranchAddress("Muon_looseId", Muon_looseId, &b_Muon_looseId);
   fChain->SetBranchStatus("Muon_mediumId", 1);
   fChain->SetBranchAddress("Muon_mediumId", Muon_mediumId, &b_Muon_mediumId);
   fChain->SetBranchStatus("Muon_mediumPromptId", 1);
   fChain->SetBranchAddress("Muon_mediumPromptId", Muon_mediumPromptId, &b_Muon_mediumPromptId);
   fChain->SetBranchStatus("Muon_miniIsoId", 1);
   fChain->SetBranchAddress("Muon_miniIsoId", Muon_miniIsoId, &b_Muon_miniIsoId);
   fChain->SetBranchStatus("Muon_multiIsoId", 1);
   fChain->SetBranchAddress("Muon_multiIsoId", Muon_multiIsoId, &b_Muon_multiIsoId);
   fChain->SetBranchStatus("Muon_mvaMuID_WP", 1);
   fChain->SetBranchAddress("Muon_mvaMuID_WP", Muon_mvaMuID_WP, &b_Muon_mvaMuID_WP);
   fChain->SetBranchStatus("Muon_nStations", 1);
   fChain->SetBranchAddress("Muon_nStations", Muon_nStations, &b_Muon_nStations);
   fChain->SetBranchStatus("Muon_nTrackerLayers", 1);
   fChain->SetBranchAddress("Muon_nTrackerLayers", Muon_nTrackerLayers, &b_Muon_nTrackerLayers);
   fChain->SetBranchStatus("Muon_pfIsoId", 1);
   fChain->SetBranchAddress("Muon_pfIsoId", Muon_pfIsoId, &b_Muon_pfIsoId);
   fChain->SetBranchStatus("Muon_puppiIsoId", 1);
   fChain->SetBranchAddress("Muon_puppiIsoId", Muon_puppiIsoId, &b_Muon_puppiIsoId);
   fChain->SetBranchStatus("Muon_softId", 1);
   fChain->SetBranchAddress("Muon_softId", Muon_softId, &b_Muon_softId);
   fChain->SetBranchStatus("Muon_softMvaId", 1);
   fChain->SetBranchAddress("Muon_softMvaId", Muon_softMvaId, &b_Muon_softMvaId);
   fChain->SetBranchStatus("Muon_tightCharge", 1);
   fChain->SetBranchAddress("Muon_tightCharge", Muon_tightCharge, &b_Muon_tightCharge);
   fChain->SetBranchStatus("Muon_tightId", 1);
   fChain->SetBranchAddress("Muon_tightId", Muon_tightId, &b_Muon_tightId);
   fChain->SetBranchStatus("Muon_tkIsoId", 1);
   fChain->SetBranchAddress("Muon_tkIsoId", Muon_tkIsoId, &b_Muon_tkIsoId);
   fChain->SetBranchStatus("Muon_triggerIdLoose", 1);
   fChain->SetBranchAddress("Muon_triggerIdLoose", Muon_triggerIdLoose, &b_Muon_triggerIdLoose);
   fChain->SetBranchStatus("Muon_jetIdx", 1);
   fChain->SetBranchAddress("Muon_jetIdx", Muon_jetIdx, &b_Muon_jetIdx);
   fChain->SetBranchStatus("Muon_svIdx", 1);
   fChain->SetBranchAddress("Muon_svIdx", Muon_svIdx, &b_Muon_svIdx);
   // fChain->SetBranchStatus("Muon_fsrPhotonIdx", 1);
   // fChain->SetBranchAddress("Muon_fsrPhotonIdx", Muon_fsrPhotonIdx, &b_Muon_fsrPhotonIdx);
   fChain->SetBranchStatus("Muon_charge", 1);
   fChain->SetBranchAddress("Muon_charge", Muon_charge, &b_Muon_charge);
   fChain->SetBranchStatus("Muon_pdgId", 1);
   fChain->SetBranchAddress("Muon_pdgId", Muon_pdgId, &b_Muon_pdgId);
   fChain->SetBranchStatus("Muon_dxy", 1);
   fChain->SetBranchAddress("Muon_dxy", Muon_dxy, &b_Muon_dxy);
   fChain->SetBranchStatus("Muon_dxyErr", 1);
   fChain->SetBranchAddress("Muon_dxyErr", Muon_dxyErr, &b_Muon_dxyErr);
   fChain->SetBranchStatus("Muon_dxybs", 1);
   fChain->SetBranchAddress("Muon_dxybs", Muon_dxybs, &b_Muon_dxybs);
   fChain->SetBranchStatus("Muon_dz", 1);
   fChain->SetBranchAddress("Muon_dz", Muon_dz, &b_Muon_dz);
   fChain->SetBranchStatus("Muon_dzErr", 1);
   fChain->SetBranchAddress("Muon_dzErr", Muon_dzErr, &b_Muon_dzErr);
   fChain->SetBranchStatus("Muon_eta", 1);
   fChain->SetBranchAddress("Muon_eta", Muon_eta, &b_Muon_eta);
   fChain->SetBranchStatus("Muon_ip3d", 1);
   fChain->SetBranchAddress("Muon_ip3d", Muon_ip3d, &b_Muon_ip3d);
   fChain->SetBranchStatus("Muon_jetPtRelv2", 1);
   fChain->SetBranchAddress("Muon_jetPtRelv2", Muon_jetPtRelv2, &b_Muon_jetPtRelv2);
   fChain->SetBranchStatus("Muon_jetRelIso", 1);
   fChain->SetBranchAddress("Muon_jetRelIso", Muon_jetRelIso, &b_Muon_jetRelIso);
   fChain->SetBranchStatus("Muon_mass", 1);
   fChain->SetBranchAddress("Muon_mass", Muon_mass, &b_Muon_mass);
   fChain->SetBranchStatus("Muon_miniPFRelIso_all", 1);
   fChain->SetBranchAddress("Muon_miniPFRelIso_all", Muon_miniPFRelIso_all, &b_Muon_miniPFRelIso_all);
   fChain->SetBranchStatus("Muon_miniPFRelIso_chg", 1);
   fChain->SetBranchAddress("Muon_miniPFRelIso_chg", Muon_miniPFRelIso_chg, &b_Muon_miniPFRelIso_chg);
   fChain->SetBranchStatus("Muon_mvaMuID", 1);
   fChain->SetBranchAddress("Muon_mvaMuID", Muon_mvaMuID, &b_Muon_mvaMuID);
   fChain->SetBranchStatus("Muon_pfRelIso03_all", 1);
   fChain->SetBranchAddress("Muon_pfRelIso03_all", Muon_pfRelIso03_all, &b_Muon_pfRelIso03_all);
   fChain->SetBranchStatus("Muon_pfRelIso03_chg", 1);
   fChain->SetBranchAddress("Muon_pfRelIso03_chg", Muon_pfRelIso03_chg, &b_Muon_pfRelIso03_chg);
   fChain->SetBranchStatus("Muon_pfRelIso04_all", 1);
   fChain->SetBranchAddress("Muon_pfRelIso04_all", Muon_pfRelIso04_all, &b_Muon_pfRelIso04_all);
   fChain->SetBranchStatus("Muon_phi", 1);
   fChain->SetBranchAddress("Muon_phi", Muon_phi, &b_Muon_phi);
   fChain->SetBranchStatus("Muon_pt", 1);
   fChain->SetBranchAddress("Muon_pt", Muon_pt, &b_Muon_pt);
   fChain->SetBranchStatus("Muon_ptErr", 1);
   fChain->SetBranchAddress("Muon_ptErr", Muon_ptErr, &b_Muon_ptErr);
   fChain->SetBranchStatus("Muon_segmentComp", 1);
   fChain->SetBranchAddress("Muon_segmentComp", Muon_segmentComp, &b_Muon_segmentComp);
   fChain->SetBranchStatus("Muon_sip3d", 1);
   fChain->SetBranchAddress("Muon_sip3d", Muon_sip3d, &b_Muon_sip3d);
   fChain->SetBranchStatus("Muon_softMva", 1);
   fChain->SetBranchAddress("Muon_softMva", Muon_softMva, &b_Muon_softMva);
   fChain->SetBranchStatus("Muon_tkRelIso", 1);
   fChain->SetBranchAddress("Muon_tkRelIso", Muon_tkRelIso, &b_Muon_tkRelIso);
   fChain->SetBranchStatus("Muon_tunepRelPt", 1);
   fChain->SetBranchAddress("Muon_tunepRelPt", Muon_tunepRelPt, &b_Muon_tunepRelPt);
   fChain->SetBranchStatus("Muon_bsConstrainedChi2", 1);
   fChain->SetBranchAddress("Muon_bsConstrainedChi2", Muon_bsConstrainedChi2, &b_Muon_bsConstrainedChi2);
   fChain->SetBranchStatus("Muon_bsConstrainedPt", 1);
   fChain->SetBranchAddress("Muon_bsConstrainedPt", Muon_bsConstrainedPt, &b_Muon_bsConstrainedPt);
   fChain->SetBranchStatus("Muon_bsConstrainedPtErr", 1);
   fChain->SetBranchAddress("Muon_bsConstrainedPtErr", Muon_bsConstrainedPtErr, &b_Muon_bsConstrainedPtErr);
   // fChain->SetBranchStatus("Muon_mvaLowPt", 1);
   // fChain->SetBranchAddress("Muon_mvaLowPt", Muon_mvaLowPt, &b_Muon_mvaLowPt);
   //fChain->SetBranchStatus("Muon_mvaTTH", 1);
   //fChain->SetBranchAddress("Muon_mvaTTH", Muon_mvaTTH, &b_Muon_mvaTTH);
   // fChain->SetBranchStatus("nPhoton", 1);
   // fChain->SetBranchAddress("nPhoton", &nPhoton, &b_nPhoton);
   // fChain->SetBranchStatus("Photon_seediEtaOriX", 1);
   // fChain->SetBranchAddress("Photon_seediEtaOriX", Photon_seediEtaOriX, &b_Photon_seediEtaOriX);
   // fChain->SetBranchStatus("Photon_cutBased", 1);
   // fChain->SetBranchAddress("Photon_cutBased", Photon_cutBased, &b_Photon_cutBased);
   // fChain->SetBranchStatus("Photon_electronVeto", 1);
   // fChain->SetBranchAddress("Photon_electronVeto", Photon_electronVeto, &b_Photon_electronVeto);
   // fChain->SetBranchStatus("Photon_hasConversionTracks", 1);
   // fChain->SetBranchAddress("Photon_hasConversionTracks", Photon_hasConversionTracks, &b_Photon_hasConversionTracks);
   // fChain->SetBranchStatus("Photon_isScEtaEB", 1);
   // fChain->SetBranchAddress("Photon_isScEtaEB", Photon_isScEtaEB, &b_Photon_isScEtaEB);
   // fChain->SetBranchStatus("Photon_isScEtaEE", 1);
   // fChain->SetBranchAddress("Photon_isScEtaEE", Photon_isScEtaEE, &b_Photon_isScEtaEE);
   // fChain->SetBranchStatus("Photon_mvaID_WP80", 1);
   // fChain->SetBranchAddress("Photon_mvaID_WP80", Photon_mvaID_WP80, &b_Photon_mvaID_WP80);
   // fChain->SetBranchStatus("Photon_mvaID_WP90", 1);
   // fChain->SetBranchAddress("Photon_mvaID_WP90", Photon_mvaID_WP90, &b_Photon_mvaID_WP90);
   // fChain->SetBranchStatus("Photon_pixelSeed", 1);
   // fChain->SetBranchAddress("Photon_pixelSeed", Photon_pixelSeed, &b_Photon_pixelSeed);
   // fChain->SetBranchStatus("Photon_seedGain", 1);
   // fChain->SetBranchAddress("Photon_seedGain", Photon_seedGain, &b_Photon_seedGain);
   // fChain->SetBranchStatus("Photon_electronIdx", 1);
   // fChain->SetBranchAddress("Photon_electronIdx", Photon_electronIdx, &b_Photon_electronIdx);
   // fChain->SetBranchStatus("Photon_jetIdx", 1);
   // fChain->SetBranchAddress("Photon_jetIdx", Photon_jetIdx, &b_Photon_jetIdx);
   // fChain->SetBranchStatus("Photon_seediPhiOriY", 1);
   // fChain->SetBranchAddress("Photon_seediPhiOriY", Photon_seediPhiOriY, &b_Photon_seediPhiOriY);
   // fChain->SetBranchStatus("Photon_vidNestedWPBitmap", 1);
   // fChain->SetBranchAddress("Photon_vidNestedWPBitmap", Photon_vidNestedWPBitmap, &b_Photon_vidNestedWPBitmap);
   // fChain->SetBranchStatus("Photon_ecalPFClusterIso", 1);
   // fChain->SetBranchAddress("Photon_ecalPFClusterIso", Photon_ecalPFClusterIso, &b_Photon_ecalPFClusterIso);
   // fChain->SetBranchStatus("Photon_energyErr", 1);
   // fChain->SetBranchAddress("Photon_energyErr", Photon_energyErr, &b_Photon_energyErr);
   // fChain->SetBranchStatus("Photon_energyRaw", 1);
   // fChain->SetBranchAddress("Photon_energyRaw", Photon_energyRaw, &b_Photon_energyRaw);
   // fChain->SetBranchStatus("Photon_esEffSigmaRR", 1);
   // fChain->SetBranchAddress("Photon_esEffSigmaRR", Photon_esEffSigmaRR, &b_Photon_esEffSigmaRR);
   // fChain->SetBranchStatus("Photon_esEnergyOverRawE", 1);
   // fChain->SetBranchAddress("Photon_esEnergyOverRawE", Photon_esEnergyOverRawE, &b_Photon_esEnergyOverRawE);
   // fChain->SetBranchStatus("Photon_eta", 1);
   // fChain->SetBranchAddress("Photon_eta", Photon_eta, &b_Photon_eta);
   // fChain->SetBranchStatus("Photon_etaWidth", 1);
   // fChain->SetBranchAddress("Photon_etaWidth", Photon_etaWidth, &b_Photon_etaWidth);
   // fChain->SetBranchStatus("Photon_haloTaggerMVAVal", 1);
   // fChain->SetBranchAddress("Photon_haloTaggerMVAVal", Photon_haloTaggerMVAVal, &b_Photon_haloTaggerMVAVal);
   // fChain->SetBranchStatus("Photon_hcalPFClusterIso", 1);
   // fChain->SetBranchAddress("Photon_hcalPFClusterIso", Photon_hcalPFClusterIso, &b_Photon_hcalPFClusterIso);
   // fChain->SetBranchStatus("Photon_hoe", 1);
   // fChain->SetBranchAddress("Photon_hoe", Photon_hoe, &b_Photon_hoe);
   // fChain->SetBranchStatus("Photon_hoe_PUcorr", 1);
   // fChain->SetBranchAddress("Photon_hoe_PUcorr", Photon_hoe_PUcorr, &b_Photon_hoe_PUcorr);
   // fChain->SetBranchStatus("Photon_mvaID", 1);
   // fChain->SetBranchAddress("Photon_mvaID", Photon_mvaID, &b_Photon_mvaID);
   // fChain->SetBranchStatus("Photon_pfChargedIso", 1);
   // fChain->SetBranchAddress("Photon_pfChargedIso", Photon_pfChargedIso, &b_Photon_pfChargedIso);
   // fChain->SetBranchStatus("Photon_pfChargedIsoPFPV", 1);
   // fChain->SetBranchAddress("Photon_pfChargedIsoPFPV", Photon_pfChargedIsoPFPV, &b_Photon_pfChargedIsoPFPV);
   // fChain->SetBranchStatus("Photon_pfChargedIsoWorstVtx", 1);
   // fChain->SetBranchAddress("Photon_pfChargedIsoWorstVtx", Photon_pfChargedIsoWorstVtx, &b_Photon_pfChargedIsoWorstVtx);
   // fChain->SetBranchStatus("Photon_pfPhoIso03", 1);
   // fChain->SetBranchAddress("Photon_pfPhoIso03", Photon_pfPhoIso03, &b_Photon_pfPhoIso03);
   // fChain->SetBranchStatus("Photon_pfRelIso03_all_quadratic", 1);
   // fChain->SetBranchAddress("Photon_pfRelIso03_all_quadratic", Photon_pfRelIso03_all_quadratic, &b_Photon_pfRelIso03_all_quadratic);
   // fChain->SetBranchStatus("Photon_pfRelIso03_chg_quadratic", 1);
   // fChain->SetBranchAddress("Photon_pfRelIso03_chg_quadratic", Photon_pfRelIso03_chg_quadratic, &b_Photon_pfRelIso03_chg_quadratic);
   // fChain->SetBranchStatus("Photon_phi", 1);
   // fChain->SetBranchAddress("Photon_phi", Photon_phi, &b_Photon_phi);
   // fChain->SetBranchStatus("Photon_phiWidth", 1);
   // fChain->SetBranchAddress("Photon_phiWidth", Photon_phiWidth, &b_Photon_phiWidth);
   // fChain->SetBranchStatus("Photon_pt", 1);
   // fChain->SetBranchAddress("Photon_pt", Photon_pt, &b_Photon_pt);
   // fChain->SetBranchStatus("Photon_r9", 1);
   // fChain->SetBranchAddress("Photon_r9", Photon_r9, &b_Photon_r9);
   // fChain->SetBranchStatus("Photon_s4", 1);
   // fChain->SetBranchAddress("Photon_s4", Photon_s4, &b_Photon_s4);
   // fChain->SetBranchStatus("Photon_sieie", 1);
   // fChain->SetBranchAddress("Photon_sieie", Photon_sieie, &b_Photon_sieie);
   // fChain->SetBranchStatus("Photon_sieip", 1);
   // fChain->SetBranchAddress("Photon_sieip", Photon_sieip, &b_Photon_sieip);
   // fChain->SetBranchStatus("Photon_sipip", 1);
   // fChain->SetBranchAddress("Photon_sipip", Photon_sipip, &b_Photon_sipip);
   // fChain->SetBranchStatus("Photon_trkSumPtHollowConeDR03", 1);
   // fChain->SetBranchAddress("Photon_trkSumPtHollowConeDR03", Photon_trkSumPtHollowConeDR03, &b_Photon_trkSumPtHollowConeDR03);
   // fChain->SetBranchStatus("Photon_trkSumPtSolidConeDR04", 1);
   // fChain->SetBranchAddress("Photon_trkSumPtSolidConeDR04", Photon_trkSumPtSolidConeDR04, &b_Photon_trkSumPtSolidConeDR04);
   // fChain->SetBranchStatus("Photon_x_calo", 1);
   // fChain->SetBranchAddress("Photon_x_calo", Photon_x_calo, &b_Photon_x_calo);
   // fChain->SetBranchStatus("Photon_y_calo", 1);
   // fChain->SetBranchAddress("Photon_y_calo", Photon_y_calo, &b_Photon_y_calo);
   // fChain->SetBranchStatus("Photon_z_calo", 1);
   // fChain->SetBranchAddress("Photon_z_calo", Photon_z_calo, &b_Photon_z_calo);
   fChain->SetBranchStatus("PuppiMET_phi", 1);
   fChain->SetBranchAddress("PuppiMET_phi", &PuppiMET_phi, &b_PuppiMET_phi);
   //fChain->SetBranchStatus("PuppiMET_phiJERDown", 1);
   //fChain->SetBranchAddress("PuppiMET_phiJERDown", &PuppiMET_phiJERDown, &b_PuppiMET_phiJERDown);
   //fChain->SetBranchStatus("PuppiMET_phiJERUp", 1);
   //fChain->SetBranchAddress("PuppiMET_phiJERUp", &PuppiMET_phiJERUp, &b_PuppiMET_phiJERUp);
   //fChain->SetBranchStatus("PuppiMET_phiJESDown", 1);
   //fChain->SetBranchAddress("PuppiMET_phiJESDown", &PuppiMET_phiJESDown, &b_PuppiMET_phiJESDown);
   //fChain->SetBranchStatus("PuppiMET_phiJESUp", 1);
   //fChain->SetBranchAddress("PuppiMET_phiJESUp", &PuppiMET_phiJESUp, &b_PuppiMET_phiJESUp);
   fChain->SetBranchStatus("PuppiMET_phiUnclusteredDown", 1);
   fChain->SetBranchAddress("PuppiMET_phiUnclusteredDown", &PuppiMET_phiUnclusteredDown, &b_PuppiMET_phiUnclusteredDown);
   fChain->SetBranchStatus("PuppiMET_phiUnclusteredUp", 1);
   fChain->SetBranchAddress("PuppiMET_phiUnclusteredUp", &PuppiMET_phiUnclusteredUp, &b_PuppiMET_phiUnclusteredUp);
   fChain->SetBranchStatus("PuppiMET_pt", 1);
   fChain->SetBranchAddress("PuppiMET_pt", &PuppiMET_pt, &b_PuppiMET_pt);
   //fChain->SetBranchStatus("PuppiMET_ptJERDown", 1);
   //fChain->SetBranchAddress("PuppiMET_ptJERDown", &PuppiMET_ptJERDown, &b_PuppiMET_ptJERDown);
   //fChain->SetBranchStatus("PuppiMET_ptJERUp", 1);
   //fChain->SetBranchAddress("PuppiMET_ptJERUp", &PuppiMET_ptJERUp, &b_PuppiMET_ptJERUp);
   //fChain->SetBranchStatus("PuppiMET_ptJESDown", 1);
   //fChain->SetBranchAddress("PuppiMET_ptJESDown", &PuppiMET_ptJESDown, &b_PuppiMET_ptJESDown);
   //fChain->SetBranchStatus("PuppiMET_ptJESUp", 1);
   //fChain->SetBranchAddress("PuppiMET_ptJESUp", &PuppiMET_ptJESUp, &b_PuppiMET_ptJESUp);
   fChain->SetBranchStatus("PuppiMET_ptUnclusteredDown", 1);
   fChain->SetBranchAddress("PuppiMET_ptUnclusteredDown", &PuppiMET_ptUnclusteredDown, &b_PuppiMET_ptUnclusteredDown);
   fChain->SetBranchStatus("PuppiMET_ptUnclusteredUp", 1);
   fChain->SetBranchAddress("PuppiMET_ptUnclusteredUp", &PuppiMET_ptUnclusteredUp, &b_PuppiMET_ptUnclusteredUp);
   fChain->SetBranchStatus("PuppiMET_sumEt", 1);
   fChain->SetBranchAddress("PuppiMET_sumEt", &PuppiMET_sumEt, &b_PuppiMET_sumEt);
   //fChain->SetBranchStatus("RawMET_phi", 1);
   //fChain->SetBranchAddress("RawMET_phi", &RawMET_phi, &b_RawMET_phi);
   //fChain->SetBranchStatus("RawMET_pt", 1);
   //fChain->SetBranchAddress("RawMET_pt", &RawMET_pt, &b_RawMET_pt);
   //fChain->SetBranchStatus("RawMET_sumEt", 1);
   //fChain->SetBranchAddress("RawMET_sumEt", &RawMET_sumEt, &b_RawMET_sumEt);
   fChain->SetBranchStatus("RawPuppiMET_phi", 1);
   fChain->SetBranchAddress("RawPuppiMET_phi", &RawPuppiMET_phi, &b_RawPuppiMET_phi);
   fChain->SetBranchStatus("RawPuppiMET_pt", 1);
   fChain->SetBranchAddress("RawPuppiMET_pt", &RawPuppiMET_pt, &b_RawPuppiMET_pt);
   fChain->SetBranchStatus("RawPuppiMET_sumEt", 1);
   fChain->SetBranchAddress("RawPuppiMET_sumEt", &RawPuppiMET_sumEt, &b_RawPuppiMET_sumEt);
   fChain->SetBranchStatus("Rho_fixedGridRhoAll", 1);
   fChain->SetBranchAddress("Rho_fixedGridRhoAll", &Rho_fixedGridRhoAll, &b_Rho_fixedGridRhoAll);
   fChain->SetBranchStatus("Rho_fixedGridRhoFastjetAll", 1);
   fChain->SetBranchAddress("Rho_fixedGridRhoFastjetAll", &Rho_fixedGridRhoFastjetAll, &b_Rho_fixedGridRhoFastjetAll);
   fChain->SetBranchStatus("Rho_fixedGridRhoFastjetCentral", 1);
   fChain->SetBranchAddress("Rho_fixedGridRhoFastjetCentral", &Rho_fixedGridRhoFastjetCentral, &b_Rho_fixedGridRhoFastjetCentral);
   fChain->SetBranchStatus("Rho_fixedGridRhoFastjetCentralCalo", 1);
   fChain->SetBranchAddress("Rho_fixedGridRhoFastjetCentralCalo", &Rho_fixedGridRhoFastjetCentralCalo, &b_Rho_fixedGridRhoFastjetCentralCalo);
   fChain->SetBranchStatus("Rho_fixedGridRhoFastjetCentralChargedPileUp", 1);
   fChain->SetBranchAddress("Rho_fixedGridRhoFastjetCentralChargedPileUp", &Rho_fixedGridRhoFastjetCentralChargedPileUp, &b_Rho_fixedGridRhoFastjetCentralChargedPileUp);
   fChain->SetBranchStatus("Rho_fixedGridRhoFastjetCentralNeutral", 1);
   fChain->SetBranchAddress("Rho_fixedGridRhoFastjetCentralNeutral", &Rho_fixedGridRhoFastjetCentralNeutral, &b_Rho_fixedGridRhoFastjetCentralNeutral);
   fChain->SetBranchStatus("nSoftActivityJet", 1);
   fChain->SetBranchAddress("nSoftActivityJet", &nSoftActivityJet, &b_nSoftActivityJet);
   fChain->SetBranchStatus("SoftActivityJet_eta", 1);
   fChain->SetBranchAddress("SoftActivityJet_eta", SoftActivityJet_eta, &b_SoftActivityJet_eta);
   fChain->SetBranchStatus("SoftActivityJet_phi", 1);
   fChain->SetBranchAddress("SoftActivityJet_phi", SoftActivityJet_phi, &b_SoftActivityJet_phi);
   fChain->SetBranchStatus("SoftActivityJet_pt", 1);
   fChain->SetBranchAddress("SoftActivityJet_pt", SoftActivityJet_pt, &b_SoftActivityJet_pt);
   fChain->SetBranchStatus("SoftActivityJetNjets10", 1);
   fChain->SetBranchAddress("SoftActivityJetNjets10", &SoftActivityJetNjets10, &b_SoftActivityJetNjets10);
   fChain->SetBranchStatus("SoftActivityJetNjets2", 1);
   fChain->SetBranchAddress("SoftActivityJetNjets2", &SoftActivityJetNjets2, &b_SoftActivityJetNjets2);
   fChain->SetBranchStatus("SoftActivityJetNjets5", 1);
   fChain->SetBranchAddress("SoftActivityJetNjets5", &SoftActivityJetNjets5, &b_SoftActivityJetNjets5);
   fChain->SetBranchStatus("SoftActivityJetHT", 1);
   fChain->SetBranchAddress("SoftActivityJetHT", &SoftActivityJetHT, &b_SoftActivityJetHT);
   fChain->SetBranchStatus("SoftActivityJetHT10", 1);
   fChain->SetBranchAddress("SoftActivityJetHT10", &SoftActivityJetHT10, &b_SoftActivityJetHT10);
   fChain->SetBranchStatus("SoftActivityJetHT2", 1);
   fChain->SetBranchAddress("SoftActivityJetHT2", &SoftActivityJetHT2, &b_SoftActivityJetHT2);
   fChain->SetBranchStatus("SoftActivityJetHT5", 1);
   fChain->SetBranchAddress("SoftActivityJetHT5", &SoftActivityJetHT5, &b_SoftActivityJetHT5);
   fChain->SetBranchStatus("nSubJet", 1);
   fChain->SetBranchAddress("nSubJet", &nSubJet, &b_nSubJet);
   //fChain->SetBranchStatus("SubJet_btagDeepB", 1);
   //fChain->SetBranchAddress("SubJet_btagDeepB", SubJet_btagDeepB, &b_SubJet_btagDeepB);
   fChain->SetBranchStatus("SubJet_eta", 1);
   fChain->SetBranchAddress("SubJet_eta", SubJet_eta, &b_SubJet_eta);
   fChain->SetBranchStatus("SubJet_mass", 1);
   fChain->SetBranchAddress("SubJet_mass", SubJet_mass, &b_SubJet_mass);
   fChain->SetBranchStatus("SubJet_n2b1", 1);
   fChain->SetBranchAddress("SubJet_n2b1", SubJet_n2b1, &b_SubJet_n2b1);
   fChain->SetBranchStatus("SubJet_n3b1", 1);
   fChain->SetBranchAddress("SubJet_n3b1", SubJet_n3b1, &b_SubJet_n3b1);
   fChain->SetBranchStatus("SubJet_phi", 1);
   fChain->SetBranchAddress("SubJet_phi", SubJet_phi, &b_SubJet_phi);
   fChain->SetBranchStatus("SubJet_pt", 1);
   fChain->SetBranchAddress("SubJet_pt", SubJet_pt, &b_SubJet_pt);
   fChain->SetBranchStatus("SubJet_rawFactor", 1);
   fChain->SetBranchAddress("SubJet_rawFactor", SubJet_rawFactor, &b_SubJet_rawFactor);
   fChain->SetBranchStatus("SubJet_tau1", 1);
   fChain->SetBranchAddress("SubJet_tau1", SubJet_tau1, &b_SubJet_tau1);
   fChain->SetBranchStatus("SubJet_tau2", 1);
   fChain->SetBranchAddress("SubJet_tau2", SubJet_tau2, &b_SubJet_tau2);
   fChain->SetBranchStatus("SubJet_tau3", 1);
   fChain->SetBranchAddress("SubJet_tau3", SubJet_tau3, &b_SubJet_tau3);
   fChain->SetBranchStatus("SubJet_tau4", 1);
   fChain->SetBranchAddress("SubJet_tau4", SubJet_tau4, &b_SubJet_tau4);
   fChain->SetBranchStatus("nTau", 1);
   fChain->SetBranchAddress("nTau", &nTau, &b_nTau);
   fChain->SetBranchStatus("Tau_decayMode", 1);
   fChain->SetBranchAddress("Tau_decayMode", Tau_decayMode, &b_Tau_decayMode);
   fChain->SetBranchStatus("Tau_idAntiEleDeadECal", 1);
   fChain->SetBranchAddress("Tau_idAntiEleDeadECal", Tau_idAntiEleDeadECal, &b_Tau_idAntiEleDeadECal);
   fChain->SetBranchStatus("Tau_idAntiMu", 1);
   fChain->SetBranchAddress("Tau_idAntiMu", Tau_idAntiMu, &b_Tau_idAntiMu);
   fChain->SetBranchStatus("Tau_idDecayModeNewDMs", 1);
   fChain->SetBranchAddress("Tau_idDecayModeNewDMs", Tau_idDecayModeNewDMs, &b_Tau_idDecayModeNewDMs);
   fChain->SetBranchStatus("Tau_idDecayModeOldDMs", 1);
   fChain->SetBranchAddress("Tau_idDecayModeOldDMs", Tau_idDecayModeOldDMs, &b_Tau_idDecayModeOldDMs);
   //fChain->SetBranchStatus("Tau_idDeepTau2017v2p1VSe", 1);
   //fChain->SetBranchAddress("Tau_idDeepTau2017v2p1VSe", Tau_idDeepTau2017v2p1VSe, &b_Tau_idDeepTau2017v2p1VSe);
   //fChain->SetBranchStatus("Tau_idDeepTau2017v2p1VSjet", 1);
   //fChain->SetBranchAddress("Tau_idDeepTau2017v2p1VSjet", Tau_idDeepTau2017v2p1VSjet, &b_Tau_idDeepTau2017v2p1VSjet);
   //fChain->SetBranchStatus("Tau_idDeepTau2017v2p1VSmu", 1);
   //fChain->SetBranchAddress("Tau_idDeepTau2017v2p1VSmu", Tau_idDeepTau2017v2p1VSmu, &b_Tau_idDeepTau2017v2p1VSmu);
   //fChain->SetBranchStatus("Tau_idDeepTau2018v2p5VSe", 1);
   //fChain->SetBranchAddress("Tau_idDeepTau2018v2p5VSe", Tau_idDeepTau2018v2p5VSe, &b_Tau_idDeepTau2018v2p5VSe);
   //fChain->SetBranchStatus("Tau_idDeepTau2018v2p5VSjet", 1);
   //fChain->SetBranchAddress("Tau_idDeepTau2018v2p5VSjet", Tau_idDeepTau2018v2p5VSjet, &b_Tau_idDeepTau2018v2p5VSjet);
   //fChain->SetBranchStatus("Tau_idDeepTau2018v2p5VSmu", 1);
   //fChain->SetBranchAddress("Tau_idDeepTau2018v2p5VSmu", Tau_idDeepTau2018v2p5VSmu, &b_Tau_idDeepTau2018v2p5VSmu);
   fChain->SetBranchStatus("Tau_nSVs", 1);
   fChain->SetBranchAddress("Tau_nSVs", Tau_nSVs, &b_Tau_nSVs);
   fChain->SetBranchStatus("Tau_charge", 1);
   fChain->SetBranchAddress("Tau_charge", Tau_charge, &b_Tau_charge);
   fChain->SetBranchStatus("Tau_decayModePNet", 1);
   fChain->SetBranchAddress("Tau_decayModePNet", Tau_decayModePNet, &b_Tau_decayModePNet);
   fChain->SetBranchStatus("Tau_eleIdx", 1);
   fChain->SetBranchAddress("Tau_eleIdx", Tau_eleIdx, &b_Tau_eleIdx);
   fChain->SetBranchStatus("Tau_jetIdx", 1);
   fChain->SetBranchAddress("Tau_jetIdx", Tau_jetIdx, &b_Tau_jetIdx);
   fChain->SetBranchStatus("Tau_muIdx", 1);
   fChain->SetBranchAddress("Tau_muIdx", Tau_muIdx, &b_Tau_muIdx);
   fChain->SetBranchStatus("Tau_svIdx1", 1);
   fChain->SetBranchAddress("Tau_svIdx1", Tau_svIdx1, &b_Tau_svIdx1);
   fChain->SetBranchStatus("Tau_svIdx2", 1);
   fChain->SetBranchAddress("Tau_svIdx2", Tau_svIdx2, &b_Tau_svIdx2);
   fChain->SetBranchStatus("Tau_chargedIso", 1);
   fChain->SetBranchAddress("Tau_chargedIso", Tau_chargedIso, &b_Tau_chargedIso);
   fChain->SetBranchStatus("Tau_dxy", 1);
   fChain->SetBranchAddress("Tau_dxy", Tau_dxy, &b_Tau_dxy);
   fChain->SetBranchStatus("Tau_dz", 1);
   fChain->SetBranchAddress("Tau_dz", Tau_dz, &b_Tau_dz);
   fChain->SetBranchStatus("Tau_eta", 1);
   fChain->SetBranchAddress("Tau_eta", Tau_eta, &b_Tau_eta);
   fChain->SetBranchStatus("Tau_leadTkDeltaEta", 1);
   fChain->SetBranchAddress("Tau_leadTkDeltaEta", Tau_leadTkDeltaEta, &b_Tau_leadTkDeltaEta);
   fChain->SetBranchStatus("Tau_leadTkDeltaPhi", 1);
   fChain->SetBranchAddress("Tau_leadTkDeltaPhi", Tau_leadTkDeltaPhi, &b_Tau_leadTkDeltaPhi);
   fChain->SetBranchStatus("Tau_leadTkPtOverTauPt", 1);
   fChain->SetBranchAddress("Tau_leadTkPtOverTauPt", Tau_leadTkPtOverTauPt, &b_Tau_leadTkPtOverTauPt);
   fChain->SetBranchStatus("Tau_mass", 1);
   fChain->SetBranchAddress("Tau_mass", Tau_mass, &b_Tau_mass);
   fChain->SetBranchStatus("Tau_neutralIso", 1);
   fChain->SetBranchAddress("Tau_neutralIso", Tau_neutralIso, &b_Tau_neutralIso);
   fChain->SetBranchStatus("Tau_phi", 1);
   fChain->SetBranchAddress("Tau_phi", Tau_phi, &b_Tau_phi);
   // fChain->SetBranchStatus("Tau_photonsOutsideSignalCone", 1);
   // fChain->SetBranchAddress("Tau_photonsOutsideSignalCone", Tau_photonsOutsideSignalCone, &b_Tau_photonsOutsideSignalCone);
   fChain->SetBranchStatus("Tau_probDM0PNet", 1);
   fChain->SetBranchAddress("Tau_probDM0PNet", Tau_probDM0PNet, &b_Tau_probDM0PNet);
   fChain->SetBranchStatus("Tau_probDM10PNet", 1);
   fChain->SetBranchAddress("Tau_probDM10PNet", Tau_probDM10PNet, &b_Tau_probDM10PNet);
   fChain->SetBranchStatus("Tau_probDM11PNet", 1);
   fChain->SetBranchAddress("Tau_probDM11PNet", Tau_probDM11PNet, &b_Tau_probDM11PNet);
   fChain->SetBranchStatus("Tau_probDM1PNet", 1);
   fChain->SetBranchAddress("Tau_probDM1PNet", Tau_probDM1PNet, &b_Tau_probDM1PNet);
   fChain->SetBranchStatus("Tau_probDM2PNet", 1);
   fChain->SetBranchAddress("Tau_probDM2PNet", Tau_probDM2PNet, &b_Tau_probDM2PNet);
   fChain->SetBranchStatus("Tau_pt", 1);
   fChain->SetBranchAddress("Tau_pt", Tau_pt, &b_Tau_pt);
   fChain->SetBranchStatus("Tau_ptCorrPNet", 1);
   fChain->SetBranchAddress("Tau_ptCorrPNet", Tau_ptCorrPNet, &b_Tau_ptCorrPNet);
   fChain->SetBranchStatus("Tau_puCorr", 1);
   fChain->SetBranchAddress("Tau_puCorr", Tau_puCorr, &b_Tau_puCorr);
   fChain->SetBranchStatus("Tau_qConfPNet", 1);
   fChain->SetBranchAddress("Tau_qConfPNet", Tau_qConfPNet, &b_Tau_qConfPNet);
   //fChain->SetBranchStatus("Tau_rawDeepTau2017v2p1VSe", 1);
   //fChain->SetBranchAddress("Tau_rawDeepTau2017v2p1VSe", Tau_rawDeepTau2017v2p1VSe, &b_Tau_rawDeepTau2017v2p1VSe);
   //fChain->SetBranchStatus("Tau_rawDeepTau2017v2p1VSjet", 1);
   //fChain->SetBranchAddress("Tau_rawDeepTau2017v2p1VSjet", Tau_rawDeepTau2017v2p1VSjet, &b_Tau_rawDeepTau2017v2p1VSjet);
   //fChain->SetBranchStatus("Tau_rawDeepTau2017v2p1VSmu", 1);
   //fChain->SetBranchAddress("Tau_rawDeepTau2017v2p1VSmu", Tau_rawDeepTau2017v2p1VSmu, &b_Tau_rawDeepTau2017v2p1VSmu);
   //fChain->SetBranchStatus("Tau_rawDeepTau2018v2p5VSe", 1);
   //fChain->SetBranchAddress("Tau_rawDeepTau2018v2p5VSe", Tau_rawDeepTau2018v2p5VSe, &b_Tau_rawDeepTau2018v2p5VSe);
   //fChain->SetBranchStatus("Tau_rawDeepTau2018v2p5VSjet", 1);
   //fChain->SetBranchAddress("Tau_rawDeepTau2018v2p5VSjet", Tau_rawDeepTau2018v2p5VSjet, &b_Tau_rawDeepTau2018v2p5VSjet);
   //fChain->SetBranchStatus("Tau_rawDeepTau2018v2p5VSmu", 1);
   //fChain->SetBranchAddress("Tau_rawDeepTau2018v2p5VSmu", Tau_rawDeepTau2018v2p5VSmu, &b_Tau_rawDeepTau2018v2p5VSmu);
   fChain->SetBranchStatus("Tau_rawIso", 1);
   fChain->SetBranchAddress("Tau_rawIso", Tau_rawIso, &b_Tau_rawIso);
   // fChain->SetBranchStatus("Tau_rawIsodR03", 1);
   // fChain->SetBranchAddress("Tau_rawIsodR03", Tau_rawIsodR03, &b_Tau_rawIsodR03);
   fChain->SetBranchStatus("Tau_rawPNetVSe", 1);
   fChain->SetBranchAddress("Tau_rawPNetVSe", Tau_rawPNetVSe, &b_Tau_rawPNetVSe);
   fChain->SetBranchStatus("Tau_rawPNetVSjet", 1);
   fChain->SetBranchAddress("Tau_rawPNetVSjet", Tau_rawPNetVSjet, &b_Tau_rawPNetVSjet);
   fChain->SetBranchStatus("Tau_rawPNetVSmu", 1);
   fChain->SetBranchAddress("Tau_rawPNetVSmu", Tau_rawPNetVSmu, &b_Tau_rawPNetVSmu);
   //fChain->SetBranchStatus("TkMET_phi", 1);
   //fChain->SetBranchAddress("TkMET_phi", &TkMET_phi, &b_TkMET_phi);
   //fChain->SetBranchStatus("TkMET_pt", 1);
   //fChain->SetBranchAddress("TkMET_pt", &TkMET_pt, &b_TkMET_pt);
   //fChain->SetBranchStatus("TkMET_sumEt", 1);
   //fChain->SetBranchAddress("TkMET_sumEt", &TkMET_sumEt, &b_TkMET_sumEt);
   fChain->SetBranchStatus("nTrigObj", 1);
   fChain->SetBranchAddress("nTrigObj", &nTrigObj, &b_nTrigObj);
   fChain->SetBranchStatus("TrigObj_l1charge", 1);
   fChain->SetBranchAddress("TrigObj_l1charge", TrigObj_l1charge, &b_TrigObj_l1charge);
   fChain->SetBranchStatus("TrigObj_id", 1);
   fChain->SetBranchAddress("TrigObj_id", TrigObj_id, &b_TrigObj_id);
   fChain->SetBranchStatus("TrigObj_l1iso", 1);
   fChain->SetBranchAddress("TrigObj_l1iso", TrigObj_l1iso, &b_TrigObj_l1iso);
   fChain->SetBranchStatus("TrigObj_filterBits", 1);
   fChain->SetBranchAddress("TrigObj_filterBits", TrigObj_filterBits, &b_TrigObj_filterBits);
   fChain->SetBranchStatus("TrigObj_pt", 1);
   fChain->SetBranchAddress("TrigObj_pt", TrigObj_pt, &b_TrigObj_pt);
   fChain->SetBranchStatus("TrigObj_eta", 1);
   fChain->SetBranchAddress("TrigObj_eta", TrigObj_eta, &b_TrigObj_eta);
   fChain->SetBranchStatus("TrigObj_phi", 1);
   fChain->SetBranchAddress("TrigObj_phi", TrigObj_phi, &b_TrigObj_phi);
   fChain->SetBranchStatus("TrigObj_l1pt", 1);
   fChain->SetBranchAddress("TrigObj_l1pt", TrigObj_l1pt, &b_TrigObj_l1pt);
   fChain->SetBranchStatus("TrigObj_l1pt_2", 1);
   fChain->SetBranchAddress("TrigObj_l1pt_2", TrigObj_l1pt_2, &b_TrigObj_l1pt_2);
   fChain->SetBranchStatus("TrigObj_l2pt", 1);
   fChain->SetBranchAddress("TrigObj_l2pt", TrigObj_l2pt, &b_TrigObj_l2pt);
   fChain->SetBranchStatus("nOtherPV", 1);
   fChain->SetBranchAddress("nOtherPV", &nOtherPV, &b_nOtherPV);
   fChain->SetBranchStatus("OtherPV_z", 1);
   fChain->SetBranchAddress("OtherPV_z", OtherPV_z, &b_OtherPV_z);
   fChain->SetBranchStatus("OtherPV_score", 1);
   fChain->SetBranchAddress("OtherPV_score", OtherPV_score, &b_OtherPV_score);
   fChain->SetBranchStatus("PV_npvs", 1);
   fChain->SetBranchAddress("PV_npvs", &PV_npvs, &b_PV_npvs);
   fChain->SetBranchStatus("PV_npvsGood", 1);
   fChain->SetBranchAddress("PV_npvsGood", &PV_npvsGood, &b_PV_npvsGood);
   fChain->SetBranchStatus("PV_ndof", 1);
   fChain->SetBranchAddress("PV_ndof", &PV_ndof, &b_PV_ndof);
   fChain->SetBranchStatus("PV_x", 1);
   fChain->SetBranchAddress("PV_x", &PV_x, &b_PV_x);
   fChain->SetBranchStatus("PV_y", 1);
   fChain->SetBranchAddress("PV_y", &PV_y, &b_PV_y);
   fChain->SetBranchStatus("PV_z", 1);
   fChain->SetBranchAddress("PV_z", &PV_z, &b_PV_z);
   fChain->SetBranchStatus("PV_chi2", 1);
   fChain->SetBranchAddress("PV_chi2", &PV_chi2, &b_PV_chi2);
   fChain->SetBranchStatus("PV_score", 1);
   fChain->SetBranchAddress("PV_score", &PV_score, &b_PV_score);
   fChain->SetBranchStatus("nSV", 1);
   fChain->SetBranchAddress("nSV", &nSV, &b_nSV);
   fChain->SetBranchStatus("SV_charge", 1);
   fChain->SetBranchAddress("SV_charge", SV_charge, &b_SV_charge);
   fChain->SetBranchStatus("SV_dlen", 1);
   fChain->SetBranchAddress("SV_dlen", SV_dlen, &b_SV_dlen);
   fChain->SetBranchStatus("SV_dlenSig", 1);
   fChain->SetBranchAddress("SV_dlenSig", SV_dlenSig, &b_SV_dlenSig);
   fChain->SetBranchStatus("SV_dxy", 1);
   fChain->SetBranchAddress("SV_dxy", SV_dxy, &b_SV_dxy);
   fChain->SetBranchStatus("SV_dxySig", 1);
   fChain->SetBranchAddress("SV_dxySig", SV_dxySig, &b_SV_dxySig);
   fChain->SetBranchStatus("SV_pAngle", 1);
   fChain->SetBranchAddress("SV_pAngle", SV_pAngle, &b_SV_pAngle);
   fChain->SetBranchStatus("SV_ntracks", 1);
   fChain->SetBranchAddress("SV_ntracks", SV_ntracks, &b_SV_ntracks);
   fChain->SetBranchStatus("SV_chi2", 1);
   fChain->SetBranchAddress("SV_chi2", SV_chi2, &b_SV_chi2);
   fChain->SetBranchStatus("SV_eta", 1);
   fChain->SetBranchAddress("SV_eta", SV_eta, &b_SV_eta);
   fChain->SetBranchStatus("SV_mass", 1);
   fChain->SetBranchAddress("SV_mass", SV_mass, &b_SV_mass);
   fChain->SetBranchStatus("SV_ndof", 1);
   fChain->SetBranchAddress("SV_ndof", SV_ndof, &b_SV_ndof);
   fChain->SetBranchStatus("SV_phi", 1);
   fChain->SetBranchAddress("SV_phi", SV_phi, &b_SV_phi);
   fChain->SetBranchStatus("SV_pt", 1);
   fChain->SetBranchAddress("SV_pt", SV_pt, &b_SV_pt);
   fChain->SetBranchStatus("SV_x", 1);
   fChain->SetBranchAddress("SV_x", SV_x, &b_SV_x);
   fChain->SetBranchStatus("SV_y", 1);
   fChain->SetBranchAddress("SV_y", SV_y, &b_SV_y);
   fChain->SetBranchStatus("SV_z", 1);
   fChain->SetBranchAddress("SV_z", SV_z, &b_SV_z);
   // fChain->SetBranchStatus("L1_AlwaysTrue", 1);
   // fChain->SetBranchAddress("L1_AlwaysTrue", &L1_AlwaysTrue, &b_L1_AlwaysTrue);
   // fChain->SetBranchStatus("L1_BPTX_AND_Ref1_VME", 1);
   // fChain->SetBranchAddress("L1_BPTX_AND_Ref1_VME", &L1_BPTX_AND_Ref1_VME, &b_L1_BPTX_AND_Ref1_VME);
   // fChain->SetBranchStatus("L1_BPTX_AND_Ref3_VME", 1);
   // fChain->SetBranchAddress("L1_BPTX_AND_Ref3_VME", &L1_BPTX_AND_Ref3_VME, &b_L1_BPTX_AND_Ref3_VME);
   // fChain->SetBranchStatus("L1_BPTX_AND_Ref4_VME", 1);
   // fChain->SetBranchAddress("L1_BPTX_AND_Ref4_VME", &L1_BPTX_AND_Ref4_VME, &b_L1_BPTX_AND_Ref4_VME);
   // fChain->SetBranchStatus("L1_BPTX_BeamGas_B1_VME", 1);
   // fChain->SetBranchAddress("L1_BPTX_BeamGas_B1_VME", &L1_BPTX_BeamGas_B1_VME, &b_L1_BPTX_BeamGas_B1_VME);
   // fChain->SetBranchStatus("L1_BPTX_BeamGas_B2_VME", 1);
   // fChain->SetBranchAddress("L1_BPTX_BeamGas_B2_VME", &L1_BPTX_BeamGas_B2_VME, &b_L1_BPTX_BeamGas_B2_VME);
   // fChain->SetBranchStatus("L1_BPTX_BeamGas_Ref1_VME", 1);
   // fChain->SetBranchAddress("L1_BPTX_BeamGas_Ref1_VME", &L1_BPTX_BeamGas_Ref1_VME, &b_L1_BPTX_BeamGas_Ref1_VME);
   // fChain->SetBranchStatus("L1_BPTX_BeamGas_Ref2_VME", 1);
   // fChain->SetBranchAddress("L1_BPTX_BeamGas_Ref2_VME", &L1_BPTX_BeamGas_Ref2_VME, &b_L1_BPTX_BeamGas_Ref2_VME);
   // fChain->SetBranchStatus("L1_BPTX_NotOR_VME", 1);
   // fChain->SetBranchAddress("L1_BPTX_NotOR_VME", &L1_BPTX_NotOR_VME, &b_L1_BPTX_NotOR_VME);
   // fChain->SetBranchStatus("L1_BPTX_OR_Ref3_VME", 1);
   // fChain->SetBranchAddress("L1_BPTX_OR_Ref3_VME", &L1_BPTX_OR_Ref3_VME, &b_L1_BPTX_OR_Ref3_VME);
   // fChain->SetBranchStatus("L1_BPTX_OR_Ref4_VME", 1);
   // fChain->SetBranchAddress("L1_BPTX_OR_Ref4_VME", &L1_BPTX_OR_Ref4_VME, &b_L1_BPTX_OR_Ref4_VME);
   // fChain->SetBranchStatus("L1_BPTX_RefAND_VME", 1);
   // fChain->SetBranchAddress("L1_BPTX_RefAND_VME", &L1_BPTX_RefAND_VME, &b_L1_BPTX_RefAND_VME);
   // fChain->SetBranchStatus("L1_BptxMinus", 1);
   // fChain->SetBranchAddress("L1_BptxMinus", &L1_BptxMinus, &b_L1_BptxMinus);
   // fChain->SetBranchStatus("L1_BptxOR", 1);
   // fChain->SetBranchAddress("L1_BptxOR", &L1_BptxOR, &b_L1_BptxOR);
   // fChain->SetBranchStatus("L1_BptxPlus", 1);
   // fChain->SetBranchAddress("L1_BptxPlus", &L1_BptxPlus, &b_L1_BptxPlus);
   // fChain->SetBranchStatus("L1_BptxXOR", 1);
   // fChain->SetBranchAddress("L1_BptxXOR", &L1_BptxXOR, &b_L1_BptxXOR);
   // fChain->SetBranchStatus("L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142", 1);
   // fChain->SetBranchAddress("L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142", &L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142, &b_L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142);
   // fChain->SetBranchStatus("L1_DoubleEG10_er1p2_dR_Max0p6", 1);
   // fChain->SetBranchAddress("L1_DoubleEG10_er1p2_dR_Max0p6", &L1_DoubleEG10_er1p2_dR_Max0p6, &b_L1_DoubleEG10_er1p2_dR_Max0p6);
   // fChain->SetBranchStatus("L1_DoubleEG10p5_er1p2_dR_Max0p6", 1);
   // fChain->SetBranchAddress("L1_DoubleEG10p5_er1p2_dR_Max0p6", &L1_DoubleEG10p5_er1p2_dR_Max0p6, &b_L1_DoubleEG10p5_er1p2_dR_Max0p6);
   // fChain->SetBranchStatus("L1_DoubleEG11_er1p2_dR_Max0p6", 1);
   // fChain->SetBranchAddress("L1_DoubleEG11_er1p2_dR_Max0p6", &L1_DoubleEG11_er1p2_dR_Max0p6, &b_L1_DoubleEG11_er1p2_dR_Max0p6);
   // fChain->SetBranchStatus("L1_DoubleEG4_er1p2_dR_Max0p9", 1);
   // fChain->SetBranchAddress("L1_DoubleEG4_er1p2_dR_Max0p9", &L1_DoubleEG4_er1p2_dR_Max0p9, &b_L1_DoubleEG4_er1p2_dR_Max0p9);
   // fChain->SetBranchStatus("L1_DoubleEG4p5_er1p2_dR_Max0p9", 1);
   // fChain->SetBranchAddress("L1_DoubleEG4p5_er1p2_dR_Max0p9", &L1_DoubleEG4p5_er1p2_dR_Max0p9, &b_L1_DoubleEG4p5_er1p2_dR_Max0p9);
   // fChain->SetBranchStatus("L1_DoubleEG5_er1p2_dR_Max0p9", 1);
   // fChain->SetBranchAddress("L1_DoubleEG5_er1p2_dR_Max0p9", &L1_DoubleEG5_er1p2_dR_Max0p9, &b_L1_DoubleEG5_er1p2_dR_Max0p9);
   // fChain->SetBranchStatus("L1_DoubleEG5p5_er1p2_dR_Max0p8", 1);
   // fChain->SetBranchAddress("L1_DoubleEG5p5_er1p2_dR_Max0p8", &L1_DoubleEG5p5_er1p2_dR_Max0p8, &b_L1_DoubleEG5p5_er1p2_dR_Max0p8);
   // fChain->SetBranchStatus("L1_DoubleEG6_er1p2_dR_Max0p8", 1);
   // fChain->SetBranchAddress("L1_DoubleEG6_er1p2_dR_Max0p8", &L1_DoubleEG6_er1p2_dR_Max0p8, &b_L1_DoubleEG6_er1p2_dR_Max0p8);
   // fChain->SetBranchStatus("L1_DoubleEG6p5_er1p2_dR_Max0p8", 1);
   // fChain->SetBranchAddress("L1_DoubleEG6p5_er1p2_dR_Max0p8", &L1_DoubleEG6p5_er1p2_dR_Max0p8, &b_L1_DoubleEG6p5_er1p2_dR_Max0p8);
   // fChain->SetBranchStatus("L1_DoubleEG7_er1p2_dR_Max0p8", 1);
   // fChain->SetBranchAddress("L1_DoubleEG7_er1p2_dR_Max0p8", &L1_DoubleEG7_er1p2_dR_Max0p8, &b_L1_DoubleEG7_er1p2_dR_Max0p8);
   // fChain->SetBranchStatus("L1_DoubleEG7p5_er1p2_dR_Max0p7", 1);
   // fChain->SetBranchAddress("L1_DoubleEG7p5_er1p2_dR_Max0p7", &L1_DoubleEG7p5_er1p2_dR_Max0p7, &b_L1_DoubleEG7p5_er1p2_dR_Max0p7);
   // fChain->SetBranchStatus("L1_DoubleEG8_er1p2_dR_Max0p7", 1);
   // fChain->SetBranchAddress("L1_DoubleEG8_er1p2_dR_Max0p7", &L1_DoubleEG8_er1p2_dR_Max0p7, &b_L1_DoubleEG8_er1p2_dR_Max0p7);
   // fChain->SetBranchStatus("L1_DoubleEG8er2p5_HTT260er", 1);
   // fChain->SetBranchAddress("L1_DoubleEG8er2p5_HTT260er", &L1_DoubleEG8er2p5_HTT260er, &b_L1_DoubleEG8er2p5_HTT260er);
   // fChain->SetBranchStatus("L1_DoubleEG8er2p5_HTT280er", 1);
   // fChain->SetBranchAddress("L1_DoubleEG8er2p5_HTT280er", &L1_DoubleEG8er2p5_HTT280er, &b_L1_DoubleEG8er2p5_HTT280er);
   // fChain->SetBranchStatus("L1_DoubleEG8er2p5_HTT300er", 1);
   // fChain->SetBranchAddress("L1_DoubleEG8er2p5_HTT300er", &L1_DoubleEG8er2p5_HTT300er, &b_L1_DoubleEG8er2p5_HTT300er);
   // fChain->SetBranchStatus("L1_DoubleEG8er2p5_HTT320er", 1);
   // fChain->SetBranchAddress("L1_DoubleEG8er2p5_HTT320er", &L1_DoubleEG8er2p5_HTT320er, &b_L1_DoubleEG8er2p5_HTT320er);
   // fChain->SetBranchStatus("L1_DoubleEG8er2p5_HTT340er", 1);
   // fChain->SetBranchAddress("L1_DoubleEG8er2p5_HTT340er", &L1_DoubleEG8er2p5_HTT340er, &b_L1_DoubleEG8er2p5_HTT340er);
   // fChain->SetBranchStatus("L1_DoubleEG8p5_er1p2_dR_Max0p7", 1);
   // fChain->SetBranchAddress("L1_DoubleEG8p5_er1p2_dR_Max0p7", &L1_DoubleEG8p5_er1p2_dR_Max0p7, &b_L1_DoubleEG8p5_er1p2_dR_Max0p7);
   // fChain->SetBranchStatus("L1_DoubleEG9_er1p2_dR_Max0p7", 1);
   // fChain->SetBranchAddress("L1_DoubleEG9_er1p2_dR_Max0p7", &L1_DoubleEG9_er1p2_dR_Max0p7, &b_L1_DoubleEG9_er1p2_dR_Max0p7);
   // fChain->SetBranchStatus("L1_DoubleEG9p5_er1p2_dR_Max0p6", 1);
   // fChain->SetBranchAddress("L1_DoubleEG9p5_er1p2_dR_Max0p6", &L1_DoubleEG9p5_er1p2_dR_Max0p6, &b_L1_DoubleEG9p5_er1p2_dR_Max0p6);
   // fChain->SetBranchStatus("L1_DoubleEG_15_10_er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_15_10_er2p5", &L1_DoubleEG_15_10_er2p5, &b_L1_DoubleEG_15_10_er2p5);
   // fChain->SetBranchStatus("L1_DoubleEG_20_10_er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_20_10_er2p5", &L1_DoubleEG_20_10_er2p5, &b_L1_DoubleEG_20_10_er2p5);
   // fChain->SetBranchStatus("L1_DoubleEG_22_10_er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_22_10_er2p5", &L1_DoubleEG_22_10_er2p5, &b_L1_DoubleEG_22_10_er2p5);
   // fChain->SetBranchStatus("L1_DoubleEG_25_12_er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_25_12_er2p5", &L1_DoubleEG_25_12_er2p5, &b_L1_DoubleEG_25_12_er2p5);
   // fChain->SetBranchStatus("L1_DoubleEG_25_14_er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_25_14_er2p5", &L1_DoubleEG_25_14_er2p5, &b_L1_DoubleEG_25_14_er2p5);
   // fChain->SetBranchStatus("L1_DoubleEG_27_14_er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_27_14_er2p5", &L1_DoubleEG_27_14_er2p5, &b_L1_DoubleEG_27_14_er2p5);
   // fChain->SetBranchStatus("L1_DoubleEG_LooseIso16_LooseIso12_er1p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_LooseIso16_LooseIso12_er1p5", &L1_DoubleEG_LooseIso16_LooseIso12_er1p5, &b_L1_DoubleEG_LooseIso16_LooseIso12_er1p5);
   // fChain->SetBranchStatus("L1_DoubleEG_LooseIso18_LooseIso12_er1p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_LooseIso18_LooseIso12_er1p5", &L1_DoubleEG_LooseIso18_LooseIso12_er1p5, &b_L1_DoubleEG_LooseIso18_LooseIso12_er1p5);
   // fChain->SetBranchStatus("L1_DoubleEG_LooseIso20_10_er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_LooseIso20_10_er2p5", &L1_DoubleEG_LooseIso20_10_er2p5, &b_L1_DoubleEG_LooseIso20_10_er2p5);
   // fChain->SetBranchStatus("L1_DoubleEG_LooseIso20_LooseIso12_er1p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_LooseIso20_LooseIso12_er1p5", &L1_DoubleEG_LooseIso20_LooseIso12_er1p5, &b_L1_DoubleEG_LooseIso20_LooseIso12_er1p5);
   // fChain->SetBranchStatus("L1_DoubleEG_LooseIso22_10_er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_LooseIso22_10_er2p5", &L1_DoubleEG_LooseIso22_10_er2p5, &b_L1_DoubleEG_LooseIso22_10_er2p5);
   // fChain->SetBranchStatus("L1_DoubleEG_LooseIso22_12_er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_LooseIso22_12_er2p5", &L1_DoubleEG_LooseIso22_12_er2p5, &b_L1_DoubleEG_LooseIso22_12_er2p5);
   // fChain->SetBranchStatus("L1_DoubleEG_LooseIso22_LooseIso12_er1p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_LooseIso22_LooseIso12_er1p5", &L1_DoubleEG_LooseIso22_LooseIso12_er1p5, &b_L1_DoubleEG_LooseIso22_LooseIso12_er1p5);
   // fChain->SetBranchStatus("L1_DoubleEG_LooseIso25_12_er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_LooseIso25_12_er2p5", &L1_DoubleEG_LooseIso25_12_er2p5, &b_L1_DoubleEG_LooseIso25_12_er2p5);
   // fChain->SetBranchStatus("L1_DoubleEG_LooseIso25_LooseIso12_er1p5", 1);
   // fChain->SetBranchAddress("L1_DoubleEG_LooseIso25_LooseIso12_er1p5", &L1_DoubleEG_LooseIso25_LooseIso12_er1p5, &b_L1_DoubleEG_LooseIso25_LooseIso12_er1p5);
   // fChain->SetBranchStatus("L1_DoubleIsoTau26er2p1_Jet55_RmOvlp_dR0p5", 1);
   // fChain->SetBranchAddress("L1_DoubleIsoTau26er2p1_Jet55_RmOvlp_dR0p5", &L1_DoubleIsoTau26er2p1_Jet55_RmOvlp_dR0p5, &b_L1_DoubleIsoTau26er2p1_Jet55_RmOvlp_dR0p5);
   // fChain->SetBranchStatus("L1_DoubleIsoTau26er2p1_Jet70_RmOvlp_dR0p5", 1);
   // fChain->SetBranchAddress("L1_DoubleIsoTau26er2p1_Jet70_RmOvlp_dR0p5", &L1_DoubleIsoTau26er2p1_Jet70_RmOvlp_dR0p5, &b_L1_DoubleIsoTau26er2p1_Jet70_RmOvlp_dR0p5);
   // fChain->SetBranchStatus("L1_DoubleIsoTau28er2p1", 1);
   // fChain->SetBranchAddress("L1_DoubleIsoTau28er2p1", &L1_DoubleIsoTau28er2p1, &b_L1_DoubleIsoTau28er2p1);
   // fChain->SetBranchStatus("L1_DoubleIsoTau28er2p1_Mass_Max80", 1);
   // fChain->SetBranchAddress("L1_DoubleIsoTau28er2p1_Mass_Max80", &L1_DoubleIsoTau28er2p1_Mass_Max80, &b_L1_DoubleIsoTau28er2p1_Mass_Max80);
   // fChain->SetBranchStatus("L1_DoubleIsoTau28er2p1_Mass_Max90", 1);
   // fChain->SetBranchAddress("L1_DoubleIsoTau28er2p1_Mass_Max90", &L1_DoubleIsoTau28er2p1_Mass_Max90, &b_L1_DoubleIsoTau28er2p1_Mass_Max90);
   // fChain->SetBranchStatus("L1_DoubleIsoTau30er2p1", 1);
   // fChain->SetBranchAddress("L1_DoubleIsoTau30er2p1", &L1_DoubleIsoTau30er2p1, &b_L1_DoubleIsoTau30er2p1);
   // fChain->SetBranchStatus("L1_DoubleIsoTau30er2p1_Mass_Max80", 1);
   // fChain->SetBranchAddress("L1_DoubleIsoTau30er2p1_Mass_Max80", &L1_DoubleIsoTau30er2p1_Mass_Max80, &b_L1_DoubleIsoTau30er2p1_Mass_Max80);
   // fChain->SetBranchStatus("L1_DoubleIsoTau30er2p1_Mass_Max90", 1);
   // fChain->SetBranchAddress("L1_DoubleIsoTau30er2p1_Mass_Max90", &L1_DoubleIsoTau30er2p1_Mass_Max90, &b_L1_DoubleIsoTau30er2p1_Mass_Max90);
   // fChain->SetBranchStatus("L1_DoubleIsoTau32er2p1", 1);
   // fChain->SetBranchAddress("L1_DoubleIsoTau32er2p1", &L1_DoubleIsoTau32er2p1, &b_L1_DoubleIsoTau32er2p1);
   // fChain->SetBranchStatus("L1_DoubleIsoTau34er2p1", 1);
   // fChain->SetBranchAddress("L1_DoubleIsoTau34er2p1", &L1_DoubleIsoTau34er2p1, &b_L1_DoubleIsoTau34er2p1);
   // fChain->SetBranchStatus("L1_DoubleIsoTau35er2p1", 1);
   // fChain->SetBranchAddress("L1_DoubleIsoTau35er2p1", &L1_DoubleIsoTau35er2p1, &b_L1_DoubleIsoTau35er2p1);
   // fChain->SetBranchStatus("L1_DoubleIsoTau36er2p1", 1);
   // fChain->SetBranchAddress("L1_DoubleIsoTau36er2p1", &L1_DoubleIsoTau36er2p1, &b_L1_DoubleIsoTau36er2p1);
   // fChain->SetBranchStatus("L1_DoubleJet100er2p3_dEta_Max1p6", 1);
   // fChain->SetBranchAddress("L1_DoubleJet100er2p3_dEta_Max1p6", &L1_DoubleJet100er2p3_dEta_Max1p6, &b_L1_DoubleJet100er2p3_dEta_Max1p6);
   // fChain->SetBranchStatus("L1_DoubleJet100er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleJet100er2p5", &L1_DoubleJet100er2p5, &b_L1_DoubleJet100er2p5);
   // fChain->SetBranchStatus("L1_DoubleJet112er2p3_dEta_Max1p6", 1);
   // fChain->SetBranchAddress("L1_DoubleJet112er2p3_dEta_Max1p6", &L1_DoubleJet112er2p3_dEta_Max1p6, &b_L1_DoubleJet112er2p3_dEta_Max1p6);
   // fChain->SetBranchStatus("L1_DoubleJet120er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleJet120er2p5", &L1_DoubleJet120er2p5, &b_L1_DoubleJet120er2p5);
   // fChain->SetBranchStatus("L1_DoubleJet150er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleJet150er2p5", &L1_DoubleJet150er2p5, &b_L1_DoubleJet150er2p5);
   // fChain->SetBranchStatus("L1_DoubleJet30er2p5_Mass_Min150_dEta_Max1p5", 1);
   // fChain->SetBranchAddress("L1_DoubleJet30er2p5_Mass_Min150_dEta_Max1p5", &L1_DoubleJet30er2p5_Mass_Min150_dEta_Max1p5, &b_L1_DoubleJet30er2p5_Mass_Min150_dEta_Max1p5);
   // fChain->SetBranchStatus("L1_DoubleJet30er2p5_Mass_Min200_dEta_Max1p5", 1);
   // fChain->SetBranchAddress("L1_DoubleJet30er2p5_Mass_Min200_dEta_Max1p5", &L1_DoubleJet30er2p5_Mass_Min200_dEta_Max1p5, &b_L1_DoubleJet30er2p5_Mass_Min200_dEta_Max1p5);
   // fChain->SetBranchStatus("L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5", 1);
   // fChain->SetBranchAddress("L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5", &L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5, &b_L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5);
   // fChain->SetBranchStatus("L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5", 1);
   // fChain->SetBranchAddress("L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5", &L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5, &b_L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5);
   // fChain->SetBranchStatus("L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5", 1);
   // fChain->SetBranchAddress("L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5", &L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5, &b_L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5);
   // fChain->SetBranchStatus("L1_DoubleJet30er2p5_Mass_Min360_dEta_Max1p5", 1);
   // fChain->SetBranchAddress("L1_DoubleJet30er2p5_Mass_Min360_dEta_Max1p5", &L1_DoubleJet30er2p5_Mass_Min360_dEta_Max1p5, &b_L1_DoubleJet30er2p5_Mass_Min360_dEta_Max1p5);
   // fChain->SetBranchStatus("L1_DoubleJet35_Mass_Min450_IsoTau45_RmOvlp", 1);
   // fChain->SetBranchAddress("L1_DoubleJet35_Mass_Min450_IsoTau45_RmOvlp", &L1_DoubleJet35_Mass_Min450_IsoTau45_RmOvlp, &b_L1_DoubleJet35_Mass_Min450_IsoTau45_RmOvlp);
   // fChain->SetBranchStatus("L1_DoubleJet35_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5", 1);
   // fChain->SetBranchAddress("L1_DoubleJet35_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5", &L1_DoubleJet35_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5, &b_L1_DoubleJet35_Mass_Min450_IsoTau45er2p1_RmOvlp_dR0p5);
   // fChain->SetBranchStatus("L1_DoubleJet40er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleJet40er2p5", &L1_DoubleJet40er2p5, &b_L1_DoubleJet40er2p5);
   // fChain->SetBranchStatus("L1_DoubleJet_100_30_DoubleJet30_Mass_Min620", 1);
   // fChain->SetBranchAddress("L1_DoubleJet_100_30_DoubleJet30_Mass_Min620", &L1_DoubleJet_100_30_DoubleJet30_Mass_Min620, &b_L1_DoubleJet_100_30_DoubleJet30_Mass_Min620);
   // fChain->SetBranchStatus("L1_DoubleJet_110_35_DoubleJet35_Mass_Min620", 1);
   // fChain->SetBranchAddress("L1_DoubleJet_110_35_DoubleJet35_Mass_Min620", &L1_DoubleJet_110_35_DoubleJet35_Mass_Min620, &b_L1_DoubleJet_110_35_DoubleJet35_Mass_Min620);
   // fChain->SetBranchStatus("L1_DoubleJet_115_40_DoubleJet40_Mass_Min620", 1);
   // fChain->SetBranchAddress("L1_DoubleJet_115_40_DoubleJet40_Mass_Min620", &L1_DoubleJet_115_40_DoubleJet40_Mass_Min620, &b_L1_DoubleJet_115_40_DoubleJet40_Mass_Min620);
   // fChain->SetBranchStatus("L1_DoubleJet_115_40_DoubleJet40_Mass_Min620_Jet60TT28", 1);
   // fChain->SetBranchAddress("L1_DoubleJet_115_40_DoubleJet40_Mass_Min620_Jet60TT28", &L1_DoubleJet_115_40_DoubleJet40_Mass_Min620_Jet60TT28, &b_L1_DoubleJet_115_40_DoubleJet40_Mass_Min620_Jet60TT28);
   // fChain->SetBranchStatus("L1_DoubleJet_120_45_DoubleJet45_Mass_Min620", 1);
   // fChain->SetBranchAddress("L1_DoubleJet_120_45_DoubleJet45_Mass_Min620", &L1_DoubleJet_120_45_DoubleJet45_Mass_Min620, &b_L1_DoubleJet_120_45_DoubleJet45_Mass_Min620);
   // fChain->SetBranchStatus("L1_DoubleJet_120_45_DoubleJet45_Mass_Min620_Jet60TT28", 1);
   // fChain->SetBranchAddress("L1_DoubleJet_120_45_DoubleJet45_Mass_Min620_Jet60TT28", &L1_DoubleJet_120_45_DoubleJet45_Mass_Min620_Jet60TT28, &b_L1_DoubleJet_120_45_DoubleJet45_Mass_Min620_Jet60TT28);
   // fChain->SetBranchStatus("L1_DoubleJet_80_30_Mass_Min420_DoubleMu0_SQ", 1);
   // fChain->SetBranchAddress("L1_DoubleJet_80_30_Mass_Min420_DoubleMu0_SQ", &L1_DoubleJet_80_30_Mass_Min420_DoubleMu0_SQ, &b_L1_DoubleJet_80_30_Mass_Min420_DoubleMu0_SQ);
   // fChain->SetBranchStatus("L1_DoubleJet_80_30_Mass_Min420_IsoTau40_RmOvlp", 1);
   // fChain->SetBranchAddress("L1_DoubleJet_80_30_Mass_Min420_IsoTau40_RmOvlp", &L1_DoubleJet_80_30_Mass_Min420_IsoTau40_RmOvlp, &b_L1_DoubleJet_80_30_Mass_Min420_IsoTau40_RmOvlp);
   // fChain->SetBranchStatus("L1_DoubleJet_80_30_Mass_Min420_Mu8", 1);
   // fChain->SetBranchAddress("L1_DoubleJet_80_30_Mass_Min420_Mu8", &L1_DoubleJet_80_30_Mass_Min420_Mu8, &b_L1_DoubleJet_80_30_Mass_Min420_Mu8);
   // fChain->SetBranchStatus("L1_DoubleJet_90_30_DoubleJet30_Mass_Min620", 1);
   // fChain->SetBranchAddress("L1_DoubleJet_90_30_DoubleJet30_Mass_Min620", &L1_DoubleJet_90_30_DoubleJet30_Mass_Min620, &b_L1_DoubleJet_90_30_DoubleJet30_Mass_Min620);
   // fChain->SetBranchStatus("L1_DoubleLLPJet40", 1);
   // fChain->SetBranchAddress("L1_DoubleLLPJet40", &L1_DoubleLLPJet40, &b_L1_DoubleLLPJet40);
   // fChain->SetBranchStatus("L1_DoubleLooseIsoEG22er2p1", 1);
   // fChain->SetBranchAddress("L1_DoubleLooseIsoEG22er2p1", &L1_DoubleLooseIsoEG22er2p1, &b_L1_DoubleLooseIsoEG22er2p1);
   // fChain->SetBranchStatus("L1_DoubleLooseIsoEG24er2p1", 1);
   // fChain->SetBranchAddress("L1_DoubleLooseIsoEG24er2p1", &L1_DoubleLooseIsoEG24er2p1, &b_L1_DoubleLooseIsoEG24er2p1);
   // fChain->SetBranchStatus("L1_DoubleMu0", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0", &L1_DoubleMu0, &b_L1_DoubleMu0);
   // fChain->SetBranchStatus("L1_DoubleMu0_Mass_Min1", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0_Mass_Min1", &L1_DoubleMu0_Mass_Min1, &b_L1_DoubleMu0_Mass_Min1);
   // fChain->SetBranchStatus("L1_DoubleMu0_OQ", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0_OQ", &L1_DoubleMu0_OQ, &b_L1_DoubleMu0_OQ);
   // fChain->SetBranchStatus("L1_DoubleMu0_SQ", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0_SQ", &L1_DoubleMu0_SQ, &b_L1_DoubleMu0_SQ);
   // fChain->SetBranchStatus("L1_DoubleMu0_SQ_OS", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0_SQ_OS", &L1_DoubleMu0_SQ_OS, &b_L1_DoubleMu0_SQ_OS);
   // fChain->SetBranchStatus("L1_DoubleMu0_Upt15_Upt7", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0_Upt15_Upt7", &L1_DoubleMu0_Upt15_Upt7, &b_L1_DoubleMu0_Upt15_Upt7);
   // fChain->SetBranchStatus("L1_DoubleMu0_Upt5_Upt5", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0_Upt5_Upt5", &L1_DoubleMu0_Upt5_Upt5, &b_L1_DoubleMu0_Upt5_Upt5);
   // fChain->SetBranchStatus("L1_DoubleMu0_Upt6_IP_Min1_Upt4", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0_Upt6_IP_Min1_Upt4", &L1_DoubleMu0_Upt6_IP_Min1_Upt4, &b_L1_DoubleMu0_Upt6_IP_Min1_Upt4);
   // fChain->SetBranchStatus("L1_DoubleMu0_dR_Max1p6_Jet90er2p5_dR_Max0p8", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0_dR_Max1p6_Jet90er2p5_dR_Max0p8", &L1_DoubleMu0_dR_Max1p6_Jet90er2p5_dR_Max0p8, &b_L1_DoubleMu0_dR_Max1p6_Jet90er2p5_dR_Max0p8);
   // fChain->SetBranchStatus("L1_DoubleMu0er1p4_OQ_OS_dEta_Max1p6", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0er1p4_OQ_OS_dEta_Max1p6", &L1_DoubleMu0er1p4_OQ_OS_dEta_Max1p6, &b_L1_DoubleMu0er1p4_OQ_OS_dEta_Max1p6);
   // fChain->SetBranchStatus("L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4", &L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4, &b_L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4);
   // fChain->SetBranchStatus("L1_DoubleMu0er1p5_SQ", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0er1p5_SQ", &L1_DoubleMu0er1p5_SQ, &b_L1_DoubleMu0er1p5_SQ);
   // fChain->SetBranchStatus("L1_DoubleMu0er1p5_SQ_OS", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0er1p5_SQ_OS", &L1_DoubleMu0er1p5_SQ_OS, &b_L1_DoubleMu0er1p5_SQ_OS);
   // fChain->SetBranchStatus("L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4", &L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4, &b_L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4);
   // fChain->SetBranchStatus("L1_DoubleMu0er1p5_SQ_dR_Max1p4", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0er1p5_SQ_dR_Max1p4", &L1_DoubleMu0er1p5_SQ_dR_Max1p4, &b_L1_DoubleMu0er1p5_SQ_dR_Max1p4);
   // fChain->SetBranchStatus("L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p5", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p5", &L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p5, &b_L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p5);
   // fChain->SetBranchStatus("L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p6", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p6", &L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p6, &b_L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p6);
   // fChain->SetBranchStatus("L1_DoubleMu0er2p0_SQ_OS_dR_Max1p4", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0er2p0_SQ_OS_dR_Max1p4", &L1_DoubleMu0er2p0_SQ_OS_dR_Max1p4, &b_L1_DoubleMu0er2p0_SQ_OS_dR_Max1p4);
   // fChain->SetBranchStatus("L1_DoubleMu0er2p0_SQ_dEta_Max1p5", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0er2p0_SQ_dEta_Max1p5", &L1_DoubleMu0er2p0_SQ_dEta_Max1p5, &b_L1_DoubleMu0er2p0_SQ_dEta_Max1p5);
   // fChain->SetBranchStatus("L1_DoubleMu0er2p0_SQ_dEta_Max1p6", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0er2p0_SQ_dEta_Max1p6", &L1_DoubleMu0er2p0_SQ_dEta_Max1p6, &b_L1_DoubleMu0er2p0_SQ_dEta_Max1p6);
   // fChain->SetBranchStatus("L1_DoubleMu0er2p0_SQ_dR_Max1p4", 1);
   // fChain->SetBranchAddress("L1_DoubleMu0er2p0_SQ_dR_Max1p4", &L1_DoubleMu0er2p0_SQ_dR_Max1p4, &b_L1_DoubleMu0er2p0_SQ_dR_Max1p4);
   // fChain->SetBranchStatus("L1_DoubleMu18er2p1_SQ", 1);
   // fChain->SetBranchAddress("L1_DoubleMu18er2p1_SQ", &L1_DoubleMu18er2p1_SQ, &b_L1_DoubleMu18er2p1_SQ);
   // fChain->SetBranchStatus("L1_DoubleMu3_OS_er2p3_Mass_Max14_DoubleEG7p5_er2p1_Mass_Max20", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3_OS_er2p3_Mass_Max14_DoubleEG7p5_er2p1_Mass_Max20", &L1_DoubleMu3_OS_er2p3_Mass_Max14_DoubleEG7p5_er2p1_Mass_Max20, &b_L1_DoubleMu3_OS_er2p3_Mass_Max14_DoubleEG7p5_er2p1_Mass_Max20);
   // fChain->SetBranchStatus("L1_DoubleMu3_SQ_ETMHF50_HTT60er", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3_SQ_ETMHF50_HTT60er", &L1_DoubleMu3_SQ_ETMHF50_HTT60er, &b_L1_DoubleMu3_SQ_ETMHF50_HTT60er);
   // fChain->SetBranchStatus("L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5", &L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5, &b_L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5);
   // fChain->SetBranchStatus("L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5_OR_DoubleJet40er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5_OR_DoubleJet40er2p5", &L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5_OR_DoubleJet40er2p5, &b_L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5_OR_DoubleJet40er2p5);
   // fChain->SetBranchStatus("L1_DoubleMu3_SQ_ETMHF60_Jet60er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3_SQ_ETMHF60_Jet60er2p5", &L1_DoubleMu3_SQ_ETMHF60_Jet60er2p5, &b_L1_DoubleMu3_SQ_ETMHF60_Jet60er2p5);
   // fChain->SetBranchStatus("L1_DoubleMu3_SQ_HTT220er", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3_SQ_HTT220er", &L1_DoubleMu3_SQ_HTT220er, &b_L1_DoubleMu3_SQ_HTT220er);
   // fChain->SetBranchStatus("L1_DoubleMu3_SQ_HTT240er", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3_SQ_HTT240er", &L1_DoubleMu3_SQ_HTT240er, &b_L1_DoubleMu3_SQ_HTT240er);
   // fChain->SetBranchStatus("L1_DoubleMu3_SQ_HTT260er", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3_SQ_HTT260er", &L1_DoubleMu3_SQ_HTT260er, &b_L1_DoubleMu3_SQ_HTT260er);
   // fChain->SetBranchStatus("L1_DoubleMu3_dR_Max1p6_Jet90er2p5_dR_Max0p8", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3_dR_Max1p6_Jet90er2p5_dR_Max0p8", &L1_DoubleMu3_dR_Max1p6_Jet90er2p5_dR_Max0p8, &b_L1_DoubleMu3_dR_Max1p6_Jet90er2p5_dR_Max0p8);
   // fChain->SetBranchStatus("L1_DoubleMu3er2p0_SQ_OS_dR_Max1p4", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3er2p0_SQ_OS_dR_Max1p4", &L1_DoubleMu3er2p0_SQ_OS_dR_Max1p4, &b_L1_DoubleMu3er2p0_SQ_OS_dR_Max1p4);
   // fChain->SetBranchStatus("L1_DoubleMu4_SQ_EG9er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleMu4_SQ_EG9er2p5", &L1_DoubleMu4_SQ_EG9er2p5, &b_L1_DoubleMu4_SQ_EG9er2p5);
   // fChain->SetBranchStatus("L1_DoubleMu4_SQ_OS", 1);
   // fChain->SetBranchAddress("L1_DoubleMu4_SQ_OS", &L1_DoubleMu4_SQ_OS, &b_L1_DoubleMu4_SQ_OS);
   // fChain->SetBranchStatus("L1_DoubleMu4_SQ_OS_dR_Max1p2", 1);
   // fChain->SetBranchAddress("L1_DoubleMu4_SQ_OS_dR_Max1p2", &L1_DoubleMu4_SQ_OS_dR_Max1p2, &b_L1_DoubleMu4_SQ_OS_dR_Max1p2);
   // fChain->SetBranchStatus("L1_DoubleMu4p5_SQ_OS", 1);
   // fChain->SetBranchAddress("L1_DoubleMu4p5_SQ_OS", &L1_DoubleMu4p5_SQ_OS, &b_L1_DoubleMu4p5_SQ_OS);
   // fChain->SetBranchStatus("L1_DoubleMu4p5_SQ_OS_dR_Max1p2", 1);
   // fChain->SetBranchAddress("L1_DoubleMu4p5_SQ_OS_dR_Max1p2", &L1_DoubleMu4p5_SQ_OS_dR_Max1p2, &b_L1_DoubleMu4p5_SQ_OS_dR_Max1p2);
   // fChain->SetBranchStatus("L1_DoubleMu4p5er2p0_SQ_OS", 1);
   // fChain->SetBranchAddress("L1_DoubleMu4p5er2p0_SQ_OS", &L1_DoubleMu4p5er2p0_SQ_OS, &b_L1_DoubleMu4p5er2p0_SQ_OS);
   // fChain->SetBranchStatus("L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18", 1);
   // fChain->SetBranchAddress("L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18", &L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18, &b_L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18);
   // fChain->SetBranchStatus("L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7", 1);
   // fChain->SetBranchAddress("L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7", &L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7, &b_L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7);
   // fChain->SetBranchStatus("L1_DoubleMu5_OS_er2p3_Mass_8to14_DoubleEG3er2p1_Mass_Max20", 1);
   // fChain->SetBranchAddress("L1_DoubleMu5_OS_er2p3_Mass_8to14_DoubleEG3er2p1_Mass_Max20", &L1_DoubleMu5_OS_er2p3_Mass_8to14_DoubleEG3er2p1_Mass_Max20, &b_L1_DoubleMu5_OS_er2p3_Mass_8to14_DoubleEG3er2p1_Mass_Max20);
   // fChain->SetBranchStatus("L1_DoubleMu5_SQ_EG9er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleMu5_SQ_EG9er2p5", &L1_DoubleMu5_SQ_EG9er2p5, &b_L1_DoubleMu5_SQ_EG9er2p5);
   // fChain->SetBranchStatus("L1_DoubleMu8_SQ", 1);
   // fChain->SetBranchAddress("L1_DoubleMu8_SQ", &L1_DoubleMu8_SQ, &b_L1_DoubleMu8_SQ);
   // fChain->SetBranchStatus("L1_DoubleMu9_SQ", 1);
   // fChain->SetBranchAddress("L1_DoubleMu9_SQ", &L1_DoubleMu9_SQ, &b_L1_DoubleMu9_SQ);
   // fChain->SetBranchStatus("L1_DoubleMu_12_5", 1);
   // fChain->SetBranchAddress("L1_DoubleMu_12_5", &L1_DoubleMu_12_5, &b_L1_DoubleMu_12_5);
   // fChain->SetBranchStatus("L1_DoubleMu_15_5_SQ", 1);
   // fChain->SetBranchAddress("L1_DoubleMu_15_5_SQ", &L1_DoubleMu_15_5_SQ, &b_L1_DoubleMu_15_5_SQ);
   // fChain->SetBranchStatus("L1_DoubleMu_15_7", 1);
   // fChain->SetBranchAddress("L1_DoubleMu_15_7", &L1_DoubleMu_15_7, &b_L1_DoubleMu_15_7);
   // fChain->SetBranchStatus("L1_DoubleMu_15_7_Mass_Min1", 1);
   // fChain->SetBranchAddress("L1_DoubleMu_15_7_Mass_Min1", &L1_DoubleMu_15_7_Mass_Min1, &b_L1_DoubleMu_15_7_Mass_Min1);
   // fChain->SetBranchStatus("L1_DoubleMu_15_7_SQ", 1);
   // fChain->SetBranchAddress("L1_DoubleMu_15_7_SQ", &L1_DoubleMu_15_7_SQ, &b_L1_DoubleMu_15_7_SQ);
   // fChain->SetBranchStatus("L1_DoubleTau70er2p1", 1);
   // fChain->SetBranchAddress("L1_DoubleTau70er2p1", &L1_DoubleTau70er2p1, &b_L1_DoubleTau70er2p1);
   // fChain->SetBranchStatus("L1_ETM120", 1);
   // fChain->SetBranchAddress("L1_ETM120", &L1_ETM120, &b_L1_ETM120);
   // fChain->SetBranchStatus("L1_ETM150", 1);
   // fChain->SetBranchAddress("L1_ETM150", &L1_ETM150, &b_L1_ETM150);
   // fChain->SetBranchStatus("L1_ETMHF100", 1);
   // fChain->SetBranchAddress("L1_ETMHF100", &L1_ETMHF100, &b_L1_ETMHF100);
   // fChain->SetBranchStatus("L1_ETMHF100_HTT60er", 1);
   // fChain->SetBranchAddress("L1_ETMHF100_HTT60er", &L1_ETMHF100_HTT60er, &b_L1_ETMHF100_HTT60er);
   // fChain->SetBranchStatus("L1_ETMHF110", 1);
   // fChain->SetBranchAddress("L1_ETMHF110", &L1_ETMHF110, &b_L1_ETMHF110);
   // fChain->SetBranchStatus("L1_ETMHF110_HTT60er", 1);
   // fChain->SetBranchAddress("L1_ETMHF110_HTT60er", &L1_ETMHF110_HTT60er, &b_L1_ETMHF110_HTT60er);
   // fChain->SetBranchStatus("L1_ETMHF110_HTT60er_NotSecondBunchInTrain", 1);
   // fChain->SetBranchAddress("L1_ETMHF110_HTT60er_NotSecondBunchInTrain", &L1_ETMHF110_HTT60er_NotSecondBunchInTrain, &b_L1_ETMHF110_HTT60er_NotSecondBunchInTrain);
   // fChain->SetBranchStatus("L1_ETMHF120", 1);
   // fChain->SetBranchAddress("L1_ETMHF120", &L1_ETMHF120, &b_L1_ETMHF120);
   // fChain->SetBranchStatus("L1_ETMHF120_HTT60er", 1);
   // fChain->SetBranchAddress("L1_ETMHF120_HTT60er", &L1_ETMHF120_HTT60er, &b_L1_ETMHF120_HTT60er);
   // fChain->SetBranchStatus("L1_ETMHF120_NotSecondBunchInTrain", 1);
   // fChain->SetBranchAddress("L1_ETMHF120_NotSecondBunchInTrain", &L1_ETMHF120_NotSecondBunchInTrain, &b_L1_ETMHF120_NotSecondBunchInTrain);
   // fChain->SetBranchStatus("L1_ETMHF130", 1);
   // fChain->SetBranchAddress("L1_ETMHF130", &L1_ETMHF130, &b_L1_ETMHF130);
   // fChain->SetBranchStatus("L1_ETMHF130_HTT60er", 1);
   // fChain->SetBranchAddress("L1_ETMHF130_HTT60er", &L1_ETMHF130_HTT60er, &b_L1_ETMHF130_HTT60er);
   // fChain->SetBranchStatus("L1_ETMHF140", 1);
   // fChain->SetBranchAddress("L1_ETMHF140", &L1_ETMHF140, &b_L1_ETMHF140);
   // fChain->SetBranchStatus("L1_ETMHF150", 1);
   // fChain->SetBranchAddress("L1_ETMHF150", &L1_ETMHF150, &b_L1_ETMHF150);
   // fChain->SetBranchStatus("L1_ETMHF90_HTT60er", 1);
   // fChain->SetBranchAddress("L1_ETMHF90_HTT60er", &L1_ETMHF90_HTT60er, &b_L1_ETMHF90_HTT60er);
   // fChain->SetBranchStatus("L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p1", 1);
   // fChain->SetBranchAddress("L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p1", &L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p1, &b_L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p1);
   // fChain->SetBranchStatus("L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p6", 1);
   // fChain->SetBranchAddress("L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p6", &L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p6, &b_L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p6);
   // fChain->SetBranchStatus("L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p1", 1);
   // fChain->SetBranchAddress("L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p1", &L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p1, &b_L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p1);
   // fChain->SetBranchStatus("L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p6", 1);
   // fChain->SetBranchAddress("L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p6", &L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p6, &b_L1_ETMHF90_SingleJet80er2p5_dPhi_Min2p6);
   // fChain->SetBranchStatus("L1_ETT1200", 1);
   // fChain->SetBranchAddress("L1_ETT1200", &L1_ETT1200, &b_L1_ETT1200);
   // fChain->SetBranchStatus("L1_ETT1600", 1);
   // fChain->SetBranchAddress("L1_ETT1600", &L1_ETT1600, &b_L1_ETT1600);
   // fChain->SetBranchStatus("L1_ETT2000", 1);
   // fChain->SetBranchAddress("L1_ETT2000", &L1_ETT2000, &b_L1_ETT2000);
   // fChain->SetBranchStatus("L1_FirstBunchAfterTrain", 1);
   // fChain->SetBranchAddress("L1_FirstBunchAfterTrain", &L1_FirstBunchAfterTrain, &b_L1_FirstBunchAfterTrain);
   // fChain->SetBranchStatus("L1_FirstBunchBeforeTrain", 1);
   // fChain->SetBranchAddress("L1_FirstBunchBeforeTrain", &L1_FirstBunchBeforeTrain, &b_L1_FirstBunchBeforeTrain);
   // fChain->SetBranchStatus("L1_FirstBunchInTrain", 1);
   // fChain->SetBranchAddress("L1_FirstBunchInTrain", &L1_FirstBunchInTrain, &b_L1_FirstBunchInTrain);
   // fChain->SetBranchStatus("L1_FirstCollisionInOrbit", 1);
   // fChain->SetBranchAddress("L1_FirstCollisionInOrbit", &L1_FirstCollisionInOrbit, &b_L1_FirstCollisionInOrbit);
   // fChain->SetBranchStatus("L1_FirstCollisionInTrain", 1);
   // fChain->SetBranchAddress("L1_FirstCollisionInTrain", &L1_FirstCollisionInTrain, &b_L1_FirstCollisionInTrain);
   // fChain->SetBranchStatus("L1_HCAL_LaserMon_Trig", 1);
   // fChain->SetBranchAddress("L1_HCAL_LaserMon_Trig", &L1_HCAL_LaserMon_Trig, &b_L1_HCAL_LaserMon_Trig);
   // fChain->SetBranchStatus("L1_HCAL_LaserMon_Veto", 1);
   // fChain->SetBranchAddress("L1_HCAL_LaserMon_Veto", &L1_HCAL_LaserMon_Veto, &b_L1_HCAL_LaserMon_Veto);
   // fChain->SetBranchStatus("L1_HTT120_SingleLLPJet40", 1);
   // fChain->SetBranchAddress("L1_HTT120_SingleLLPJet40", &L1_HTT120_SingleLLPJet40, &b_L1_HTT120_SingleLLPJet40);
   // fChain->SetBranchStatus("L1_HTT120er", 1);
   // fChain->SetBranchAddress("L1_HTT120er", &L1_HTT120er, &b_L1_HTT120er);
   // fChain->SetBranchStatus("L1_HTT160_SingleLLPJet50", 1);
   // fChain->SetBranchAddress("L1_HTT160_SingleLLPJet50", &L1_HTT160_SingleLLPJet50, &b_L1_HTT160_SingleLLPJet50);
   // fChain->SetBranchStatus("L1_HTT160er", 1);
   // fChain->SetBranchAddress("L1_HTT160er", &L1_HTT160er, &b_L1_HTT160er);
   // fChain->SetBranchStatus("L1_HTT200_SingleLLPJet60", 1);
   // fChain->SetBranchAddress("L1_HTT200_SingleLLPJet60", &L1_HTT200_SingleLLPJet60, &b_L1_HTT200_SingleLLPJet60);
   // fChain->SetBranchStatus("L1_HTT200er", 1);
   // fChain->SetBranchAddress("L1_HTT200er", &L1_HTT200er, &b_L1_HTT200er);
   // fChain->SetBranchStatus("L1_HTT240_SingleLLPJet70", 1);
   // fChain->SetBranchAddress("L1_HTT240_SingleLLPJet70", &L1_HTT240_SingleLLPJet70, &b_L1_HTT240_SingleLLPJet70);
   // fChain->SetBranchStatus("L1_HTT255er", 1);
   // fChain->SetBranchAddress("L1_HTT255er", &L1_HTT255er, &b_L1_HTT255er);
   // fChain->SetBranchStatus("L1_HTT280er", 1);
   // fChain->SetBranchAddress("L1_HTT280er", &L1_HTT280er, &b_L1_HTT280er);
   // fChain->SetBranchStatus("L1_HTT280er_QuadJet_70_55_40_35_er2p5", 1);
   // fChain->SetBranchAddress("L1_HTT280er_QuadJet_70_55_40_35_er2p5", &L1_HTT280er_QuadJet_70_55_40_35_er2p5, &b_L1_HTT280er_QuadJet_70_55_40_35_er2p5);
   // fChain->SetBranchStatus("L1_HTT320er", 1);
   // fChain->SetBranchAddress("L1_HTT320er", &L1_HTT320er, &b_L1_HTT320er);
   // fChain->SetBranchStatus("L1_HTT320er_QuadJet_70_55_40_40_er2p5", 1);
   // fChain->SetBranchAddress("L1_HTT320er_QuadJet_70_55_40_40_er2p5", &L1_HTT320er_QuadJet_70_55_40_40_er2p5, &b_L1_HTT320er_QuadJet_70_55_40_40_er2p5);
   // fChain->SetBranchStatus("L1_HTT320er_QuadJet_80_60_er2p1_45_40_er2p3", 1);
   // fChain->SetBranchAddress("L1_HTT320er_QuadJet_80_60_er2p1_45_40_er2p3", &L1_HTT320er_QuadJet_80_60_er2p1_45_40_er2p3, &b_L1_HTT320er_QuadJet_80_60_er2p1_45_40_er2p3);
   // fChain->SetBranchStatus("L1_HTT320er_QuadJet_80_60_er2p1_50_45_er2p3", 1);
   // fChain->SetBranchAddress("L1_HTT320er_QuadJet_80_60_er2p1_50_45_er2p3", &L1_HTT320er_QuadJet_80_60_er2p1_50_45_er2p3, &b_L1_HTT320er_QuadJet_80_60_er2p1_50_45_er2p3);
   // fChain->SetBranchStatus("L1_HTT360er", 1);
   // fChain->SetBranchAddress("L1_HTT360er", &L1_HTT360er, &b_L1_HTT360er);
   // fChain->SetBranchStatus("L1_HTT400er", 1);
   // fChain->SetBranchAddress("L1_HTT400er", &L1_HTT400er, &b_L1_HTT400er);
   // fChain->SetBranchStatus("L1_HTT450er", 1);
   // fChain->SetBranchAddress("L1_HTT450er", &L1_HTT450er, &b_L1_HTT450er);
   // fChain->SetBranchStatus("L1_IsoEG32er2p5_Mt40", 1);
   // fChain->SetBranchAddress("L1_IsoEG32er2p5_Mt40", &L1_IsoEG32er2p5_Mt40, &b_L1_IsoEG32er2p5_Mt40);
   // fChain->SetBranchStatus("L1_IsoTau52er2p1_QuadJet36er2p5", 1);
   // fChain->SetBranchAddress("L1_IsoTau52er2p1_QuadJet36er2p5", &L1_IsoTau52er2p1_QuadJet36er2p5, &b_L1_IsoTau52er2p1_QuadJet36er2p5);
   // fChain->SetBranchStatus("L1_IsolatedBunch", 1);
   // fChain->SetBranchAddress("L1_IsolatedBunch", &L1_IsolatedBunch, &b_L1_IsolatedBunch);
   // fChain->SetBranchStatus("L1_LastBunchInTrain", 1);
   // fChain->SetBranchAddress("L1_LastBunchInTrain", &L1_LastBunchInTrain, &b_L1_LastBunchInTrain);
   // fChain->SetBranchStatus("L1_LastCollisionInTrain", 1);
   // fChain->SetBranchAddress("L1_LastCollisionInTrain", &L1_LastCollisionInTrain, &b_L1_LastCollisionInTrain);
   // fChain->SetBranchStatus("L1_LooseIsoEG22er2p1_IsoTau26er2p1_dR_Min0p3", 1);
   // fChain->SetBranchAddress("L1_LooseIsoEG22er2p1_IsoTau26er2p1_dR_Min0p3", &L1_LooseIsoEG22er2p1_IsoTau26er2p1_dR_Min0p3, &b_L1_LooseIsoEG22er2p1_IsoTau26er2p1_dR_Min0p3);
   // fChain->SetBranchStatus("L1_LooseIsoEG22er2p1_Tau70er2p1_dR_Min0p3", 1);
   // fChain->SetBranchAddress("L1_LooseIsoEG22er2p1_Tau70er2p1_dR_Min0p3", &L1_LooseIsoEG22er2p1_Tau70er2p1_dR_Min0p3, &b_L1_LooseIsoEG22er2p1_Tau70er2p1_dR_Min0p3);
   // fChain->SetBranchStatus("L1_LooseIsoEG24er2p1_HTT100er", 1);
   // fChain->SetBranchAddress("L1_LooseIsoEG24er2p1_HTT100er", &L1_LooseIsoEG24er2p1_HTT100er, &b_L1_LooseIsoEG24er2p1_HTT100er);
   // fChain->SetBranchStatus("L1_LooseIsoEG24er2p1_IsoTau27er2p1_dR_Min0p3", 1);
   // fChain->SetBranchAddress("L1_LooseIsoEG24er2p1_IsoTau27er2p1_dR_Min0p3", &L1_LooseIsoEG24er2p1_IsoTau27er2p1_dR_Min0p3, &b_L1_LooseIsoEG24er2p1_IsoTau27er2p1_dR_Min0p3);
   // fChain->SetBranchStatus("L1_LooseIsoEG26er2p1_HTT100er", 1);
   // fChain->SetBranchAddress("L1_LooseIsoEG26er2p1_HTT100er", &L1_LooseIsoEG26er2p1_HTT100er, &b_L1_LooseIsoEG26er2p1_HTT100er);
   // fChain->SetBranchStatus("L1_LooseIsoEG26er2p1_Jet34er2p5_dR_Min0p3", 1);
   // fChain->SetBranchAddress("L1_LooseIsoEG26er2p1_Jet34er2p5_dR_Min0p3", &L1_LooseIsoEG26er2p1_Jet34er2p5_dR_Min0p3, &b_L1_LooseIsoEG26er2p1_Jet34er2p5_dR_Min0p3);
   // fChain->SetBranchStatus("L1_LooseIsoEG28er2p1_HTT100er", 1);
   // fChain->SetBranchAddress("L1_LooseIsoEG28er2p1_HTT100er", &L1_LooseIsoEG28er2p1_HTT100er, &b_L1_LooseIsoEG28er2p1_HTT100er);
   // fChain->SetBranchStatus("L1_LooseIsoEG28er2p1_Jet34er2p5_dR_Min0p3", 1);
   // fChain->SetBranchAddress("L1_LooseIsoEG28er2p1_Jet34er2p5_dR_Min0p3", &L1_LooseIsoEG28er2p1_Jet34er2p5_dR_Min0p3, &b_L1_LooseIsoEG28er2p1_Jet34er2p5_dR_Min0p3);
   // fChain->SetBranchStatus("L1_LooseIsoEG30er2p1_HTT100er", 1);
   // fChain->SetBranchAddress("L1_LooseIsoEG30er2p1_HTT100er", &L1_LooseIsoEG30er2p1_HTT100er, &b_L1_LooseIsoEG30er2p1_HTT100er);
   // fChain->SetBranchStatus("L1_LooseIsoEG30er2p1_Jet34er2p5_dR_Min0p3", 1);
   // fChain->SetBranchAddress("L1_LooseIsoEG30er2p1_Jet34er2p5_dR_Min0p3", &L1_LooseIsoEG30er2p1_Jet34er2p5_dR_Min0p3, &b_L1_LooseIsoEG30er2p1_Jet34er2p5_dR_Min0p3);
   // fChain->SetBranchStatus("L1_MinimumBiasHF0", 1);
   // fChain->SetBranchAddress("L1_MinimumBiasHF0", &L1_MinimumBiasHF0, &b_L1_MinimumBiasHF0);
   // fChain->SetBranchStatus("L1_MinimumBiasHF0_AND_BptxAND", 1);
   // fChain->SetBranchAddress("L1_MinimumBiasHF0_AND_BptxAND", &L1_MinimumBiasHF0_AND_BptxAND, &b_L1_MinimumBiasHF0_AND_BptxAND);
   // fChain->SetBranchStatus("L1_Mu10er2p3_Jet32er2p3_dR_Max0p4_DoubleJet32er2p3_dEta_Max1p6", 1);
   // fChain->SetBranchAddress("L1_Mu10er2p3_Jet32er2p3_dR_Max0p4_DoubleJet32er2p3_dEta_Max1p6", &L1_Mu10er2p3_Jet32er2p3_dR_Max0p4_DoubleJet32er2p3_dEta_Max1p6, &b_L1_Mu10er2p3_Jet32er2p3_dR_Max0p4_DoubleJet32er2p3_dEta_Max1p6);
   // fChain->SetBranchStatus("L1_Mu12er2p3_Jet40er2p1_dR_Max0p4_DoubleJet40er2p1_dEta_Max1p6", 1);
   // fChain->SetBranchAddress("L1_Mu12er2p3_Jet40er2p1_dR_Max0p4_DoubleJet40er2p1_dEta_Max1p6", &L1_Mu12er2p3_Jet40er2p1_dR_Max0p4_DoubleJet40er2p1_dEta_Max1p6, &b_L1_Mu12er2p3_Jet40er2p1_dR_Max0p4_DoubleJet40er2p1_dEta_Max1p6);
   // fChain->SetBranchStatus("L1_Mu12er2p3_Jet40er2p3_dR_Max0p4_DoubleJet40er2p3_dEta_Max1p6", 1);
   // fChain->SetBranchAddress("L1_Mu12er2p3_Jet40er2p3_dR_Max0p4_DoubleJet40er2p3_dEta_Max1p6", &L1_Mu12er2p3_Jet40er2p3_dR_Max0p4_DoubleJet40er2p3_dEta_Max1p6, &b_L1_Mu12er2p3_Jet40er2p3_dR_Max0p4_DoubleJet40er2p3_dEta_Max1p6);
   // fChain->SetBranchStatus("L1_Mu18er2p1_Tau24er2p1", 1);
   // fChain->SetBranchAddress("L1_Mu18er2p1_Tau24er2p1", &L1_Mu18er2p1_Tau24er2p1, &b_L1_Mu18er2p1_Tau24er2p1);
   // fChain->SetBranchStatus("L1_Mu18er2p1_Tau26er2p1", 1);
   // fChain->SetBranchAddress("L1_Mu18er2p1_Tau26er2p1", &L1_Mu18er2p1_Tau26er2p1, &b_L1_Mu18er2p1_Tau26er2p1);
   // fChain->SetBranchStatus("L1_Mu18er2p1_Tau26er2p1_Jet55", 1);
   // fChain->SetBranchAddress("L1_Mu18er2p1_Tau26er2p1_Jet55", &L1_Mu18er2p1_Tau26er2p1_Jet55, &b_L1_Mu18er2p1_Tau26er2p1_Jet55);
   // fChain->SetBranchStatus("L1_Mu18er2p1_Tau26er2p1_Jet70", 1);
   // fChain->SetBranchAddress("L1_Mu18er2p1_Tau26er2p1_Jet70", &L1_Mu18er2p1_Tau26er2p1_Jet70, &b_L1_Mu18er2p1_Tau26er2p1_Jet70);
   // fChain->SetBranchStatus("L1_Mu20_EG10er2p5", 1);
   // fChain->SetBranchAddress("L1_Mu20_EG10er2p5", &L1_Mu20_EG10er2p5, &b_L1_Mu20_EG10er2p5);
   // fChain->SetBranchStatus("L1_Mu22er2p1_IsoTau28er2p1", 1);
   // fChain->SetBranchAddress("L1_Mu22er2p1_IsoTau28er2p1", &L1_Mu22er2p1_IsoTau28er2p1, &b_L1_Mu22er2p1_IsoTau28er2p1);
   // fChain->SetBranchStatus("L1_Mu22er2p1_IsoTau30er2p1", 1);
   // fChain->SetBranchAddress("L1_Mu22er2p1_IsoTau30er2p1", &L1_Mu22er2p1_IsoTau30er2p1, &b_L1_Mu22er2p1_IsoTau30er2p1);
   // fChain->SetBranchStatus("L1_Mu22er2p1_IsoTau32er2p1", 1);
   // fChain->SetBranchAddress("L1_Mu22er2p1_IsoTau32er2p1", &L1_Mu22er2p1_IsoTau32er2p1, &b_L1_Mu22er2p1_IsoTau32er2p1);
   // fChain->SetBranchStatus("L1_Mu22er2p1_IsoTau34er2p1", 1);
   // fChain->SetBranchAddress("L1_Mu22er2p1_IsoTau34er2p1", &L1_Mu22er2p1_IsoTau34er2p1, &b_L1_Mu22er2p1_IsoTau34er2p1);
   // fChain->SetBranchStatus("L1_Mu22er2p1_IsoTau36er2p1", 1);
   // fChain->SetBranchAddress("L1_Mu22er2p1_IsoTau36er2p1", &L1_Mu22er2p1_IsoTau36er2p1, &b_L1_Mu22er2p1_IsoTau36er2p1);
   // fChain->SetBranchStatus("L1_Mu22er2p1_IsoTau40er2p1", 1);
   // fChain->SetBranchAddress("L1_Mu22er2p1_IsoTau40er2p1", &L1_Mu22er2p1_IsoTau40er2p1, &b_L1_Mu22er2p1_IsoTau40er2p1);
   // fChain->SetBranchStatus("L1_Mu22er2p1_Tau70er2p1", 1);
   // fChain->SetBranchAddress("L1_Mu22er2p1_Tau70er2p1", &L1_Mu22er2p1_Tau70er2p1, &b_L1_Mu22er2p1_Tau70er2p1);
   // fChain->SetBranchStatus("L1_Mu3_Jet120er2p5_dR_Max0p4", 1);
   // fChain->SetBranchAddress("L1_Mu3_Jet120er2p5_dR_Max0p4", &L1_Mu3_Jet120er2p5_dR_Max0p4, &b_L1_Mu3_Jet120er2p5_dR_Max0p4);
   // fChain->SetBranchStatus("L1_Mu3_Jet120er2p5_dR_Max0p8", 1);
   // fChain->SetBranchAddress("L1_Mu3_Jet120er2p5_dR_Max0p8", &L1_Mu3_Jet120er2p5_dR_Max0p8, &b_L1_Mu3_Jet120er2p5_dR_Max0p8);
   // fChain->SetBranchStatus("L1_Mu3_Jet16er2p5_dR_Max0p4", 1);
   // fChain->SetBranchAddress("L1_Mu3_Jet16er2p5_dR_Max0p4", &L1_Mu3_Jet16er2p5_dR_Max0p4, &b_L1_Mu3_Jet16er2p5_dR_Max0p4);
   // fChain->SetBranchStatus("L1_Mu3_Jet30er2p5", 1);
   // fChain->SetBranchAddress("L1_Mu3_Jet30er2p5", &L1_Mu3_Jet30er2p5, &b_L1_Mu3_Jet30er2p5);
   // fChain->SetBranchStatus("L1_Mu3_Jet35er2p5_dR_Max0p4", 1);
   // fChain->SetBranchAddress("L1_Mu3_Jet35er2p5_dR_Max0p4", &L1_Mu3_Jet35er2p5_dR_Max0p4, &b_L1_Mu3_Jet35er2p5_dR_Max0p4);
   // fChain->SetBranchStatus("L1_Mu3_Jet60er2p5_dR_Max0p4", 1);
   // fChain->SetBranchAddress("L1_Mu3_Jet60er2p5_dR_Max0p4", &L1_Mu3_Jet60er2p5_dR_Max0p4, &b_L1_Mu3_Jet60er2p5_dR_Max0p4);
   // fChain->SetBranchStatus("L1_Mu3_Jet80er2p5_dR_Max0p4", 1);
   // fChain->SetBranchAddress("L1_Mu3_Jet80er2p5_dR_Max0p4", &L1_Mu3_Jet80er2p5_dR_Max0p4, &b_L1_Mu3_Jet80er2p5_dR_Max0p4);
   // fChain->SetBranchStatus("L1_Mu3er1p5_Jet100er2p5_ETMHF40", 1);
   // fChain->SetBranchAddress("L1_Mu3er1p5_Jet100er2p5_ETMHF40", &L1_Mu3er1p5_Jet100er2p5_ETMHF40, &b_L1_Mu3er1p5_Jet100er2p5_ETMHF40);
   // fChain->SetBranchStatus("L1_Mu3er1p5_Jet100er2p5_ETMHF50", 1);
   // fChain->SetBranchAddress("L1_Mu3er1p5_Jet100er2p5_ETMHF50", &L1_Mu3er1p5_Jet100er2p5_ETMHF50, &b_L1_Mu3er1p5_Jet100er2p5_ETMHF50);
   // fChain->SetBranchStatus("L1_Mu5_EG23er2p5", 1);
   // fChain->SetBranchAddress("L1_Mu5_EG23er2p5", &L1_Mu5_EG23er2p5, &b_L1_Mu5_EG23er2p5);
   // fChain->SetBranchStatus("L1_Mu5_LooseIsoEG20er2p5", 1);
   // fChain->SetBranchAddress("L1_Mu5_LooseIsoEG20er2p5", &L1_Mu5_LooseIsoEG20er2p5, &b_L1_Mu5_LooseIsoEG20er2p5);
   // fChain->SetBranchStatus("L1_Mu6_DoubleEG10er2p5", 1);
   // fChain->SetBranchAddress("L1_Mu6_DoubleEG10er2p5", &L1_Mu6_DoubleEG10er2p5, &b_L1_Mu6_DoubleEG10er2p5);
   // fChain->SetBranchStatus("L1_Mu6_DoubleEG12er2p5", 1);
   // fChain->SetBranchAddress("L1_Mu6_DoubleEG12er2p5", &L1_Mu6_DoubleEG12er2p5, &b_L1_Mu6_DoubleEG12er2p5);
   // fChain->SetBranchStatus("L1_Mu6_DoubleEG15er2p5", 1);
   // fChain->SetBranchAddress("L1_Mu6_DoubleEG15er2p5", &L1_Mu6_DoubleEG15er2p5, &b_L1_Mu6_DoubleEG15er2p5);
   // fChain->SetBranchStatus("L1_Mu6_DoubleEG17er2p5", 1);
   // fChain->SetBranchAddress("L1_Mu6_DoubleEG17er2p5", &L1_Mu6_DoubleEG17er2p5, &b_L1_Mu6_DoubleEG17er2p5);
   // fChain->SetBranchStatus("L1_Mu6_HTT240er", 1);
   // fChain->SetBranchAddress("L1_Mu6_HTT240er", &L1_Mu6_HTT240er, &b_L1_Mu6_HTT240er);
   // fChain->SetBranchStatus("L1_Mu6_HTT250er", 1);
   // fChain->SetBranchAddress("L1_Mu6_HTT250er", &L1_Mu6_HTT250er, &b_L1_Mu6_HTT250er);
   // fChain->SetBranchStatus("L1_Mu7_EG20er2p5", 1);
   // fChain->SetBranchAddress("L1_Mu7_EG20er2p5", &L1_Mu7_EG20er2p5, &b_L1_Mu7_EG20er2p5);
   // fChain->SetBranchStatus("L1_Mu7_EG23er2p5", 1);
   // fChain->SetBranchAddress("L1_Mu7_EG23er2p5", &L1_Mu7_EG23er2p5, &b_L1_Mu7_EG23er2p5);
   // fChain->SetBranchStatus("L1_Mu7_LooseIsoEG20er2p5", 1);
   // fChain->SetBranchAddress("L1_Mu7_LooseIsoEG20er2p5", &L1_Mu7_LooseIsoEG20er2p5, &b_L1_Mu7_LooseIsoEG20er2p5);
   // fChain->SetBranchStatus("L1_Mu7_LooseIsoEG23er2p5", 1);
   // fChain->SetBranchAddress("L1_Mu7_LooseIsoEG23er2p5", &L1_Mu7_LooseIsoEG23er2p5, &b_L1_Mu7_LooseIsoEG23er2p5);
   // fChain->SetBranchStatus("L1_NotBptxOR", 1);
   // fChain->SetBranchAddress("L1_NotBptxOR", &L1_NotBptxOR, &b_L1_NotBptxOR);
   // fChain->SetBranchStatus("L1_QuadJet60er2p5", 1);
   // fChain->SetBranchAddress("L1_QuadJet60er2p5", &L1_QuadJet60er2p5, &b_L1_QuadJet60er2p5);
   // fChain->SetBranchStatus("L1_QuadJet_95_75_65_20_DoubleJet_75_65_er2p5_Jet20_FWD3p0", 1);
   // fChain->SetBranchAddress("L1_QuadJet_95_75_65_20_DoubleJet_75_65_er2p5_Jet20_FWD3p0", &L1_QuadJet_95_75_65_20_DoubleJet_75_65_er2p5_Jet20_FWD3p0, &b_L1_QuadJet_95_75_65_20_DoubleJet_75_65_er2p5_Jet20_FWD3p0);
   // fChain->SetBranchStatus("L1_QuadMu0", 1);
   // fChain->SetBranchAddress("L1_QuadMu0", &L1_QuadMu0, &b_L1_QuadMu0);
   // fChain->SetBranchStatus("L1_QuadMu0_OQ", 1);
   // fChain->SetBranchAddress("L1_QuadMu0_OQ", &L1_QuadMu0_OQ, &b_L1_QuadMu0_OQ);
   // fChain->SetBranchStatus("L1_QuadMu0_SQ", 1);
   // fChain->SetBranchAddress("L1_QuadMu0_SQ", &L1_QuadMu0_SQ, &b_L1_QuadMu0_SQ);
   // fChain->SetBranchStatus("L1_SecondBunchInTrain", 1);
   // fChain->SetBranchAddress("L1_SecondBunchInTrain", &L1_SecondBunchInTrain, &b_L1_SecondBunchInTrain);
   // fChain->SetBranchStatus("L1_SecondLastBunchInTrain", 1);
   // fChain->SetBranchAddress("L1_SecondLastBunchInTrain", &L1_SecondLastBunchInTrain, &b_L1_SecondLastBunchInTrain);
   // fChain->SetBranchStatus("L1_SingleEG10er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleEG10er2p5", &L1_SingleEG10er2p5, &b_L1_SingleEG10er2p5);
   // fChain->SetBranchStatus("L1_SingleEG15er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleEG15er2p5", &L1_SingleEG15er2p5, &b_L1_SingleEG15er2p5);
   // fChain->SetBranchStatus("L1_SingleEG26er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleEG26er2p5", &L1_SingleEG26er2p5, &b_L1_SingleEG26er2p5);
   // fChain->SetBranchStatus("L1_SingleEG28_FWD2p5", 1);
   // fChain->SetBranchAddress("L1_SingleEG28_FWD2p5", &L1_SingleEG28_FWD2p5, &b_L1_SingleEG28_FWD2p5);
   // fChain->SetBranchStatus("L1_SingleEG28er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleEG28er1p5", &L1_SingleEG28er1p5, &b_L1_SingleEG28er1p5);
   // fChain->SetBranchStatus("L1_SingleEG28er2p1", 1);
   // fChain->SetBranchAddress("L1_SingleEG28er2p1", &L1_SingleEG28er2p1, &b_L1_SingleEG28er2p1);
   // fChain->SetBranchStatus("L1_SingleEG28er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleEG28er2p5", &L1_SingleEG28er2p5, &b_L1_SingleEG28er2p5);
   // fChain->SetBranchStatus("L1_SingleEG34er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleEG34er2p5", &L1_SingleEG34er2p5, &b_L1_SingleEG34er2p5);
   // fChain->SetBranchStatus("L1_SingleEG36er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleEG36er2p5", &L1_SingleEG36er2p5, &b_L1_SingleEG36er2p5);
   // fChain->SetBranchStatus("L1_SingleEG38er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleEG38er2p5", &L1_SingleEG38er2p5, &b_L1_SingleEG38er2p5);
   // fChain->SetBranchStatus("L1_SingleEG40er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleEG40er2p5", &L1_SingleEG40er2p5, &b_L1_SingleEG40er2p5);
   // fChain->SetBranchStatus("L1_SingleEG42er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleEG42er2p5", &L1_SingleEG42er2p5, &b_L1_SingleEG42er2p5);
   // fChain->SetBranchStatus("L1_SingleEG45er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleEG45er2p5", &L1_SingleEG45er2p5, &b_L1_SingleEG45er2p5);
   // fChain->SetBranchStatus("L1_SingleEG50", 1);
   // fChain->SetBranchAddress("L1_SingleEG50", &L1_SingleEG50, &b_L1_SingleEG50);
   // fChain->SetBranchStatus("L1_SingleEG60", 1);
   // fChain->SetBranchAddress("L1_SingleEG60", &L1_SingleEG60, &b_L1_SingleEG60);
   // fChain->SetBranchStatus("L1_SingleEG8er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleEG8er2p5", &L1_SingleEG8er2p5, &b_L1_SingleEG8er2p5);
   // fChain->SetBranchStatus("L1_SingleIsoEG24er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG24er1p5", &L1_SingleIsoEG24er1p5, &b_L1_SingleIsoEG24er1p5);
   // fChain->SetBranchStatus("L1_SingleIsoEG24er2p1", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG24er2p1", &L1_SingleIsoEG24er2p1, &b_L1_SingleIsoEG24er2p1);
   // fChain->SetBranchStatus("L1_SingleIsoEG26er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG26er1p5", &L1_SingleIsoEG26er1p5, &b_L1_SingleIsoEG26er1p5);
   // fChain->SetBranchStatus("L1_SingleIsoEG26er2p1", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG26er2p1", &L1_SingleIsoEG26er2p1, &b_L1_SingleIsoEG26er2p1);
   // fChain->SetBranchStatus("L1_SingleIsoEG26er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG26er2p5", &L1_SingleIsoEG26er2p5, &b_L1_SingleIsoEG26er2p5);
   // fChain->SetBranchStatus("L1_SingleIsoEG28_FWD2p5", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG28_FWD2p5", &L1_SingleIsoEG28_FWD2p5, &b_L1_SingleIsoEG28_FWD2p5);
   // fChain->SetBranchStatus("L1_SingleIsoEG28er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG28er1p5", &L1_SingleIsoEG28er1p5, &b_L1_SingleIsoEG28er1p5);
   // fChain->SetBranchStatus("L1_SingleIsoEG28er2p1", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG28er2p1", &L1_SingleIsoEG28er2p1, &b_L1_SingleIsoEG28er2p1);
   // fChain->SetBranchStatus("L1_SingleIsoEG28er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG28er2p5", &L1_SingleIsoEG28er2p5, &b_L1_SingleIsoEG28er2p5);
   // fChain->SetBranchStatus("L1_SingleIsoEG30er2p1", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG30er2p1", &L1_SingleIsoEG30er2p1, &b_L1_SingleIsoEG30er2p1);
   // fChain->SetBranchStatus("L1_SingleIsoEG30er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG30er2p5", &L1_SingleIsoEG30er2p5, &b_L1_SingleIsoEG30er2p5);
   // fChain->SetBranchStatus("L1_SingleIsoEG32er2p1", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG32er2p1", &L1_SingleIsoEG32er2p1, &b_L1_SingleIsoEG32er2p1);
   // fChain->SetBranchStatus("L1_SingleIsoEG32er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG32er2p5", &L1_SingleIsoEG32er2p5, &b_L1_SingleIsoEG32er2p5);
   // fChain->SetBranchStatus("L1_SingleIsoEG34er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleIsoEG34er2p5", &L1_SingleIsoEG34er2p5, &b_L1_SingleIsoEG34er2p5);
   // fChain->SetBranchStatus("L1_SingleIsoTau32er2p1", 1);
   // fChain->SetBranchAddress("L1_SingleIsoTau32er2p1", &L1_SingleIsoTau32er2p1, &b_L1_SingleIsoTau32er2p1);
   // fChain->SetBranchStatus("L1_SingleJet10erHE", 1);
   // fChain->SetBranchAddress("L1_SingleJet10erHE", &L1_SingleJet10erHE, &b_L1_SingleJet10erHE);
   // fChain->SetBranchStatus("L1_SingleJet120", 1);
   // fChain->SetBranchAddress("L1_SingleJet120", &L1_SingleJet120, &b_L1_SingleJet120);
   // fChain->SetBranchStatus("L1_SingleJet120_FWD3p0", 1);
   // fChain->SetBranchAddress("L1_SingleJet120_FWD3p0", &L1_SingleJet120_FWD3p0, &b_L1_SingleJet120_FWD3p0);
   // fChain->SetBranchStatus("L1_SingleJet120er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleJet120er2p5", &L1_SingleJet120er2p5, &b_L1_SingleJet120er2p5);
   // fChain->SetBranchStatus("L1_SingleJet12erHE", 1);
   // fChain->SetBranchAddress("L1_SingleJet12erHE", &L1_SingleJet12erHE, &b_L1_SingleJet12erHE);
   // fChain->SetBranchStatus("L1_SingleJet140er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleJet140er2p5", &L1_SingleJet140er2p5, &b_L1_SingleJet140er2p5);
   // fChain->SetBranchStatus("L1_SingleJet140er2p5_ETMHF70", 1);
   // fChain->SetBranchAddress("L1_SingleJet140er2p5_ETMHF70", &L1_SingleJet140er2p5_ETMHF70, &b_L1_SingleJet140er2p5_ETMHF70);
   // fChain->SetBranchStatus("L1_SingleJet140er2p5_ETMHF80", 1);
   // fChain->SetBranchAddress("L1_SingleJet140er2p5_ETMHF80", &L1_SingleJet140er2p5_ETMHF80, &b_L1_SingleJet140er2p5_ETMHF80);
   // fChain->SetBranchStatus("L1_SingleJet140er2p5_ETMHF90", 1);
   // fChain->SetBranchAddress("L1_SingleJet140er2p5_ETMHF90", &L1_SingleJet140er2p5_ETMHF90, &b_L1_SingleJet140er2p5_ETMHF90);
   // fChain->SetBranchStatus("L1_SingleJet160er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleJet160er2p5", &L1_SingleJet160er2p5, &b_L1_SingleJet160er2p5);
   // fChain->SetBranchStatus("L1_SingleJet180", 1);
   // fChain->SetBranchAddress("L1_SingleJet180", &L1_SingleJet180, &b_L1_SingleJet180);
   // fChain->SetBranchStatus("L1_SingleJet180er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleJet180er2p5", &L1_SingleJet180er2p5, &b_L1_SingleJet180er2p5);
   // fChain->SetBranchStatus("L1_SingleJet200", 1);
   // fChain->SetBranchAddress("L1_SingleJet200", &L1_SingleJet200, &b_L1_SingleJet200);
   // fChain->SetBranchStatus("L1_SingleJet20er2p5_NotBptxOR", 1);
   // fChain->SetBranchAddress("L1_SingleJet20er2p5_NotBptxOR", &L1_SingleJet20er2p5_NotBptxOR, &b_L1_SingleJet20er2p5_NotBptxOR);
   // fChain->SetBranchStatus("L1_SingleJet20er2p5_NotBptxOR_3BX", 1);
   // fChain->SetBranchAddress("L1_SingleJet20er2p5_NotBptxOR_3BX", &L1_SingleJet20er2p5_NotBptxOR_3BX, &b_L1_SingleJet20er2p5_NotBptxOR_3BX);
   // fChain->SetBranchStatus("L1_SingleJet35", 1);
   // fChain->SetBranchAddress("L1_SingleJet35", &L1_SingleJet35, &b_L1_SingleJet35);
   // fChain->SetBranchStatus("L1_SingleJet35_FWD3p0", 1);
   // fChain->SetBranchAddress("L1_SingleJet35_FWD3p0", &L1_SingleJet35_FWD3p0, &b_L1_SingleJet35_FWD3p0);
   // fChain->SetBranchStatus("L1_SingleJet35er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleJet35er2p5", &L1_SingleJet35er2p5, &b_L1_SingleJet35er2p5);
   // fChain->SetBranchStatus("L1_SingleJet43er2p5_NotBptxOR_3BX", 1);
   // fChain->SetBranchAddress("L1_SingleJet43er2p5_NotBptxOR_3BX", &L1_SingleJet43er2p5_NotBptxOR_3BX, &b_L1_SingleJet43er2p5_NotBptxOR_3BX);
   // fChain->SetBranchStatus("L1_SingleJet46er2p5_NotBptxOR_3BX", 1);
   // fChain->SetBranchAddress("L1_SingleJet46er2p5_NotBptxOR_3BX", &L1_SingleJet46er2p5_NotBptxOR_3BX, &b_L1_SingleJet46er2p5_NotBptxOR_3BX);
   // fChain->SetBranchStatus("L1_SingleJet60", 1);
   // fChain->SetBranchAddress("L1_SingleJet60", &L1_SingleJet60, &b_L1_SingleJet60);
   // fChain->SetBranchStatus("L1_SingleJet60_FWD3p0", 1);
   // fChain->SetBranchAddress("L1_SingleJet60_FWD3p0", &L1_SingleJet60_FWD3p0, &b_L1_SingleJet60_FWD3p0);
   // fChain->SetBranchStatus("L1_SingleJet60er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleJet60er2p5", &L1_SingleJet60er2p5, &b_L1_SingleJet60er2p5);
   // fChain->SetBranchStatus("L1_SingleJet8erHE", 1);
   // fChain->SetBranchAddress("L1_SingleJet8erHE", &L1_SingleJet8erHE, &b_L1_SingleJet8erHE);
   // fChain->SetBranchStatus("L1_SingleJet90", 1);
   // fChain->SetBranchAddress("L1_SingleJet90", &L1_SingleJet90, &b_L1_SingleJet90);
   // fChain->SetBranchStatus("L1_SingleJet90_FWD3p0", 1);
   // fChain->SetBranchAddress("L1_SingleJet90_FWD3p0", &L1_SingleJet90_FWD3p0, &b_L1_SingleJet90_FWD3p0);
   // fChain->SetBranchStatus("L1_SingleJet90er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleJet90er2p5", &L1_SingleJet90er2p5, &b_L1_SingleJet90er2p5);
   // fChain->SetBranchStatus("L1_SingleLooseIsoEG26er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleLooseIsoEG26er1p5", &L1_SingleLooseIsoEG26er1p5, &b_L1_SingleLooseIsoEG26er1p5);
   // fChain->SetBranchStatus("L1_SingleLooseIsoEG26er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleLooseIsoEG26er2p5", &L1_SingleLooseIsoEG26er2p5, &b_L1_SingleLooseIsoEG26er2p5);
   // fChain->SetBranchStatus("L1_SingleLooseIsoEG28_FWD2p5", 1);
   // fChain->SetBranchAddress("L1_SingleLooseIsoEG28_FWD2p5", &L1_SingleLooseIsoEG28_FWD2p5, &b_L1_SingleLooseIsoEG28_FWD2p5);
   // fChain->SetBranchStatus("L1_SingleLooseIsoEG28er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleLooseIsoEG28er1p5", &L1_SingleLooseIsoEG28er1p5, &b_L1_SingleLooseIsoEG28er1p5);
   // fChain->SetBranchStatus("L1_SingleLooseIsoEG28er2p1", 1);
   // fChain->SetBranchAddress("L1_SingleLooseIsoEG28er2p1", &L1_SingleLooseIsoEG28er2p1, &b_L1_SingleLooseIsoEG28er2p1);
   // fChain->SetBranchStatus("L1_SingleLooseIsoEG28er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleLooseIsoEG28er2p5", &L1_SingleLooseIsoEG28er2p5, &b_L1_SingleLooseIsoEG28er2p5);
   // fChain->SetBranchStatus("L1_SingleLooseIsoEG30er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleLooseIsoEG30er1p5", &L1_SingleLooseIsoEG30er1p5, &b_L1_SingleLooseIsoEG30er1p5);
   // fChain->SetBranchStatus("L1_SingleLooseIsoEG30er2p5", 1);
   // fChain->SetBranchAddress("L1_SingleLooseIsoEG30er2p5", &L1_SingleLooseIsoEG30er2p5, &b_L1_SingleLooseIsoEG30er2p5);
   // fChain->SetBranchStatus("L1_SingleMu0_BMTF", 1);
   // fChain->SetBranchAddress("L1_SingleMu0_BMTF", &L1_SingleMu0_BMTF, &b_L1_SingleMu0_BMTF);
   // fChain->SetBranchStatus("L1_SingleMu0_DQ", 1);
   // fChain->SetBranchAddress("L1_SingleMu0_DQ", &L1_SingleMu0_DQ, &b_L1_SingleMu0_DQ);
   // fChain->SetBranchStatus("L1_SingleMu0_EMTF", 1);
   // fChain->SetBranchAddress("L1_SingleMu0_EMTF", &L1_SingleMu0_EMTF, &b_L1_SingleMu0_EMTF);
   // fChain->SetBranchStatus("L1_SingleMu0_OMTF", 1);
   // fChain->SetBranchAddress("L1_SingleMu0_OMTF", &L1_SingleMu0_OMTF, &b_L1_SingleMu0_OMTF);
   // fChain->SetBranchStatus("L1_SingleMu10er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleMu10er1p5", &L1_SingleMu10er1p5, &b_L1_SingleMu10er1p5);
   // fChain->SetBranchStatus("L1_SingleMu12_DQ_BMTF", 1);
   // fChain->SetBranchAddress("L1_SingleMu12_DQ_BMTF", &L1_SingleMu12_DQ_BMTF, &b_L1_SingleMu12_DQ_BMTF);
   // fChain->SetBranchStatus("L1_SingleMu12_DQ_EMTF", 1);
   // fChain->SetBranchAddress("L1_SingleMu12_DQ_EMTF", &L1_SingleMu12_DQ_EMTF, &b_L1_SingleMu12_DQ_EMTF);
   // fChain->SetBranchStatus("L1_SingleMu12_DQ_OMTF", 1);
   // fChain->SetBranchAddress("L1_SingleMu12_DQ_OMTF", &L1_SingleMu12_DQ_OMTF, &b_L1_SingleMu12_DQ_OMTF);
   // fChain->SetBranchStatus("L1_SingleMu12er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleMu12er1p5", &L1_SingleMu12er1p5, &b_L1_SingleMu12er1p5);
   // fChain->SetBranchStatus("L1_SingleMu14er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleMu14er1p5", &L1_SingleMu14er1p5, &b_L1_SingleMu14er1p5);
   // fChain->SetBranchStatus("L1_SingleMu15_DQ", 1);
   // fChain->SetBranchAddress("L1_SingleMu15_DQ", &L1_SingleMu15_DQ, &b_L1_SingleMu15_DQ);
   // fChain->SetBranchStatus("L1_SingleMu16er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleMu16er1p5", &L1_SingleMu16er1p5, &b_L1_SingleMu16er1p5);
   // fChain->SetBranchStatus("L1_SingleMu18", 1);
   // fChain->SetBranchAddress("L1_SingleMu18", &L1_SingleMu18, &b_L1_SingleMu18);
   // fChain->SetBranchStatus("L1_SingleMu18er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleMu18er1p5", &L1_SingleMu18er1p5, &b_L1_SingleMu18er1p5);
   // fChain->SetBranchStatus("L1_SingleMu20", 1);
   // fChain->SetBranchAddress("L1_SingleMu20", &L1_SingleMu20, &b_L1_SingleMu20);
   // fChain->SetBranchStatus("L1_SingleMu22", 1);
   // fChain->SetBranchAddress("L1_SingleMu22", &L1_SingleMu22, &b_L1_SingleMu22);
   // fChain->SetBranchStatus("L1_SingleMu22_BMTF", 1);
   // fChain->SetBranchAddress("L1_SingleMu22_BMTF", &L1_SingleMu22_BMTF, &b_L1_SingleMu22_BMTF);
   // fChain->SetBranchStatus("L1_SingleMu22_DQ", 1);
   // fChain->SetBranchAddress("L1_SingleMu22_DQ", &L1_SingleMu22_DQ, &b_L1_SingleMu22_DQ);
   // fChain->SetBranchStatus("L1_SingleMu22_EMTF", 1);
   // fChain->SetBranchAddress("L1_SingleMu22_EMTF", &L1_SingleMu22_EMTF, &b_L1_SingleMu22_EMTF);
   // fChain->SetBranchStatus("L1_SingleMu22_OMTF", 1);
   // fChain->SetBranchAddress("L1_SingleMu22_OMTF", &L1_SingleMu22_OMTF, &b_L1_SingleMu22_OMTF);
   // fChain->SetBranchStatus("L1_SingleMu22_OQ", 1);
   // fChain->SetBranchAddress("L1_SingleMu22_OQ", &L1_SingleMu22_OQ, &b_L1_SingleMu22_OQ);
   // fChain->SetBranchStatus("L1_SingleMu25", 1);
   // fChain->SetBranchAddress("L1_SingleMu25", &L1_SingleMu25, &b_L1_SingleMu25);
   // fChain->SetBranchStatus("L1_SingleMu3", 1);
   // fChain->SetBranchAddress("L1_SingleMu3", &L1_SingleMu3, &b_L1_SingleMu3);
   // fChain->SetBranchStatus("L1_SingleMu5", 1);
   // fChain->SetBranchAddress("L1_SingleMu5", &L1_SingleMu5, &b_L1_SingleMu5);
   // fChain->SetBranchStatus("L1_SingleMu6er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleMu6er1p5", &L1_SingleMu6er1p5, &b_L1_SingleMu6er1p5);
   // fChain->SetBranchStatus("L1_SingleMu7", 1);
   // fChain->SetBranchAddress("L1_SingleMu7", &L1_SingleMu7, &b_L1_SingleMu7);
   // fChain->SetBranchStatus("L1_SingleMu7_DQ", 1);
   // fChain->SetBranchAddress("L1_SingleMu7_DQ", &L1_SingleMu7_DQ, &b_L1_SingleMu7_DQ);
   // fChain->SetBranchStatus("L1_SingleMu7er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleMu7er1p5", &L1_SingleMu7er1p5, &b_L1_SingleMu7er1p5);
   // fChain->SetBranchStatus("L1_SingleMu8er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleMu8er1p5", &L1_SingleMu8er1p5, &b_L1_SingleMu8er1p5);
   // fChain->SetBranchStatus("L1_SingleMu9er1p5", 1);
   // fChain->SetBranchAddress("L1_SingleMu9er1p5", &L1_SingleMu9er1p5, &b_L1_SingleMu9er1p5);
   // fChain->SetBranchStatus("L1_SingleMuCosmics", 1);
   // fChain->SetBranchAddress("L1_SingleMuCosmics", &L1_SingleMuCosmics, &b_L1_SingleMuCosmics);
   // fChain->SetBranchStatus("L1_SingleMuCosmics_BMTF", 1);
   // fChain->SetBranchAddress("L1_SingleMuCosmics_BMTF", &L1_SingleMuCosmics_BMTF, &b_L1_SingleMuCosmics_BMTF);
   // fChain->SetBranchStatus("L1_SingleMuCosmics_EMTF", 1);
   // fChain->SetBranchAddress("L1_SingleMuCosmics_EMTF", &L1_SingleMuCosmics_EMTF, &b_L1_SingleMuCosmics_EMTF);
   // fChain->SetBranchStatus("L1_SingleMuCosmics_OMTF", 1);
   // fChain->SetBranchAddress("L1_SingleMuCosmics_OMTF", &L1_SingleMuCosmics_OMTF, &b_L1_SingleMuCosmics_OMTF);
   // fChain->SetBranchStatus("L1_SingleMuOpen", 1);
   // fChain->SetBranchAddress("L1_SingleMuOpen", &L1_SingleMuOpen, &b_L1_SingleMuOpen);
   // fChain->SetBranchStatus("L1_SingleMuOpen_NotBptxOR", 1);
   // fChain->SetBranchAddress("L1_SingleMuOpen_NotBptxOR", &L1_SingleMuOpen_NotBptxOR, &b_L1_SingleMuOpen_NotBptxOR);
   // fChain->SetBranchStatus("L1_SingleMuOpen_er1p1_NotBptxOR_3BX", 1);
   // fChain->SetBranchAddress("L1_SingleMuOpen_er1p1_NotBptxOR_3BX", &L1_SingleMuOpen_er1p1_NotBptxOR_3BX, &b_L1_SingleMuOpen_er1p1_NotBptxOR_3BX);
   // fChain->SetBranchStatus("L1_SingleMuOpen_er1p4_NotBptxOR_3BX", 1);
   // fChain->SetBranchAddress("L1_SingleMuOpen_er1p4_NotBptxOR_3BX", &L1_SingleMuOpen_er1p4_NotBptxOR_3BX, &b_L1_SingleMuOpen_er1p4_NotBptxOR_3BX);
   // fChain->SetBranchStatus("L1_SingleMuShower_Nominal", 1);
   // fChain->SetBranchAddress("L1_SingleMuShower_Nominal", &L1_SingleMuShower_Nominal, &b_L1_SingleMuShower_Nominal);
   // fChain->SetBranchStatus("L1_SingleMuShower_Tight", 1);
   // fChain->SetBranchAddress("L1_SingleMuShower_Tight", &L1_SingleMuShower_Tight, &b_L1_SingleMuShower_Tight);
   // fChain->SetBranchStatus("L1_SingleTau120er2p1", 1);
   // fChain->SetBranchAddress("L1_SingleTau120er2p1", &L1_SingleTau120er2p1, &b_L1_SingleTau120er2p1);
   // fChain->SetBranchStatus("L1_SingleTau130er2p1", 1);
   // fChain->SetBranchAddress("L1_SingleTau130er2p1", &L1_SingleTau130er2p1, &b_L1_SingleTau130er2p1);
   // fChain->SetBranchStatus("L1_SingleTau70er2p1", 1);
   // fChain->SetBranchAddress("L1_SingleTau70er2p1", &L1_SingleTau70er2p1, &b_L1_SingleTau70er2p1);
   // fChain->SetBranchStatus("L1_TOTEM_1", 1);
   // fChain->SetBranchAddress("L1_TOTEM_1", &L1_TOTEM_1, &b_L1_TOTEM_1);
   // fChain->SetBranchStatus("L1_TOTEM_2", 1);
   // fChain->SetBranchAddress("L1_TOTEM_2", &L1_TOTEM_2, &b_L1_TOTEM_2);
   // fChain->SetBranchStatus("L1_TOTEM_3", 1);
   // fChain->SetBranchAddress("L1_TOTEM_3", &L1_TOTEM_3, &b_L1_TOTEM_3);
   // fChain->SetBranchStatus("L1_TOTEM_4", 1);
   // fChain->SetBranchAddress("L1_TOTEM_4", &L1_TOTEM_4, &b_L1_TOTEM_4);
   // fChain->SetBranchStatus("L1_TripleEG16er2p5", 1);
   // fChain->SetBranchAddress("L1_TripleEG16er2p5", &L1_TripleEG16er2p5, &b_L1_TripleEG16er2p5);
   // fChain->SetBranchStatus("L1_TripleEG_16_12_8_er2p5", 1);
   // fChain->SetBranchAddress("L1_TripleEG_16_12_8_er2p5", &L1_TripleEG_16_12_8_er2p5, &b_L1_TripleEG_16_12_8_er2p5);
   // fChain->SetBranchStatus("L1_TripleEG_16_15_8_er2p5", 1);
   // fChain->SetBranchAddress("L1_TripleEG_16_15_8_er2p5", &L1_TripleEG_16_15_8_er2p5, &b_L1_TripleEG_16_15_8_er2p5);
   // fChain->SetBranchStatus("L1_TripleEG_18_17_8_er2p5", 1);
   // fChain->SetBranchAddress("L1_TripleEG_18_17_8_er2p5", &L1_TripleEG_18_17_8_er2p5, &b_L1_TripleEG_18_17_8_er2p5);
   // fChain->SetBranchStatus("L1_TripleEG_18_18_12_er2p5", 1);
   // fChain->SetBranchAddress("L1_TripleEG_18_18_12_er2p5", &L1_TripleEG_18_18_12_er2p5, &b_L1_TripleEG_18_18_12_er2p5);
   // fChain->SetBranchStatus("L1_TripleJet_100_80_70_DoubleJet_80_70_er2p5", 1);
   // fChain->SetBranchAddress("L1_TripleJet_100_80_70_DoubleJet_80_70_er2p5", &L1_TripleJet_100_80_70_DoubleJet_80_70_er2p5, &b_L1_TripleJet_100_80_70_DoubleJet_80_70_er2p5);
   // fChain->SetBranchStatus("L1_TripleJet_105_85_75_DoubleJet_85_75_er2p5", 1);
   // fChain->SetBranchAddress("L1_TripleJet_105_85_75_DoubleJet_85_75_er2p5", &L1_TripleJet_105_85_75_DoubleJet_85_75_er2p5, &b_L1_TripleJet_105_85_75_DoubleJet_85_75_er2p5);
   // fChain->SetBranchStatus("L1_TripleJet_95_75_65_DoubleJet_75_65_er2p5", 1);
   // fChain->SetBranchAddress("L1_TripleJet_95_75_65_DoubleJet_75_65_er2p5", &L1_TripleJet_95_75_65_DoubleJet_75_65_er2p5, &b_L1_TripleJet_95_75_65_DoubleJet_75_65_er2p5);
   // fChain->SetBranchStatus("L1_TripleMu0", 1);
   // fChain->SetBranchAddress("L1_TripleMu0", &L1_TripleMu0, &b_L1_TripleMu0);
   // fChain->SetBranchStatus("L1_TripleMu0_OQ", 1);
   // fChain->SetBranchAddress("L1_TripleMu0_OQ", &L1_TripleMu0_OQ, &b_L1_TripleMu0_OQ);
   // fChain->SetBranchStatus("L1_TripleMu0_SQ", 1);
   // fChain->SetBranchAddress("L1_TripleMu0_SQ", &L1_TripleMu0_SQ, &b_L1_TripleMu0_SQ);
   // fChain->SetBranchStatus("L1_TripleMu3", 1);
   // fChain->SetBranchAddress("L1_TripleMu3", &L1_TripleMu3, &b_L1_TripleMu3);
   // fChain->SetBranchStatus("L1_TripleMu3_SQ", 1);
   // fChain->SetBranchAddress("L1_TripleMu3_SQ", &L1_TripleMu3_SQ, &b_L1_TripleMu3_SQ);
   // fChain->SetBranchStatus("L1_TripleMu_2SQ_1p5SQ_0OQ", 1);
   // fChain->SetBranchAddress("L1_TripleMu_2SQ_1p5SQ_0OQ", &L1_TripleMu_2SQ_1p5SQ_0OQ, &b_L1_TripleMu_2SQ_1p5SQ_0OQ);
   // fChain->SetBranchStatus("L1_TripleMu_2SQ_1p5SQ_0OQ_Mass_Max12", 1);
   // fChain->SetBranchAddress("L1_TripleMu_2SQ_1p5SQ_0OQ_Mass_Max12", &L1_TripleMu_2SQ_1p5SQ_0OQ_Mass_Max12, &b_L1_TripleMu_2SQ_1p5SQ_0OQ_Mass_Max12);
   // fChain->SetBranchStatus("L1_TripleMu_3SQ_2p5SQ_0OQ_Mass_Max12", 1);
   // fChain->SetBranchAddress("L1_TripleMu_3SQ_2p5SQ_0OQ_Mass_Max12", &L1_TripleMu_3SQ_2p5SQ_0OQ_Mass_Max12, &b_L1_TripleMu_3SQ_2p5SQ_0OQ_Mass_Max12);
   // fChain->SetBranchStatus("L1_TripleMu_5SQ_3SQ_0OQ", 1);
   // fChain->SetBranchAddress("L1_TripleMu_5SQ_3SQ_0OQ", &L1_TripleMu_5SQ_3SQ_0OQ, &b_L1_TripleMu_5SQ_3SQ_0OQ);
   // fChain->SetBranchStatus("L1_TripleMu_5SQ_3SQ_0OQ_DoubleMu_5_3_SQ_OS_Mass_Max9", 1);
   // fChain->SetBranchAddress("L1_TripleMu_5SQ_3SQ_0OQ_DoubleMu_5_3_SQ_OS_Mass_Max9", &L1_TripleMu_5SQ_3SQ_0OQ_DoubleMu_5_3_SQ_OS_Mass_Max9, &b_L1_TripleMu_5SQ_3SQ_0OQ_DoubleMu_5_3_SQ_OS_Mass_Max9);
   // fChain->SetBranchStatus("L1_TripleMu_5SQ_3SQ_0_DoubleMu_5_3_SQ_OS_Mass_Max9", 1);
   // fChain->SetBranchAddress("L1_TripleMu_5SQ_3SQ_0_DoubleMu_5_3_SQ_OS_Mass_Max9", &L1_TripleMu_5SQ_3SQ_0_DoubleMu_5_3_SQ_OS_Mass_Max9, &b_L1_TripleMu_5SQ_3SQ_0_DoubleMu_5_3_SQ_OS_Mass_Max9);
   // fChain->SetBranchStatus("L1_TripleMu_5_3_3", 1);
   // fChain->SetBranchAddress("L1_TripleMu_5_3_3", &L1_TripleMu_5_3_3, &b_L1_TripleMu_5_3_3);
   // fChain->SetBranchStatus("L1_TripleMu_5_3_3_SQ", 1);
   // fChain->SetBranchAddress("L1_TripleMu_5_3_3_SQ", &L1_TripleMu_5_3_3_SQ, &b_L1_TripleMu_5_3_3_SQ);
   // fChain->SetBranchStatus("L1_TripleMu_5_3p5_2p5", 1);
   // fChain->SetBranchAddress("L1_TripleMu_5_3p5_2p5", &L1_TripleMu_5_3p5_2p5, &b_L1_TripleMu_5_3p5_2p5);
   // fChain->SetBranchStatus("L1_TripleMu_5_3p5_2p5_DoubleMu_5_2p5_OS_Mass_5to17", 1);
   // fChain->SetBranchAddress("L1_TripleMu_5_3p5_2p5_DoubleMu_5_2p5_OS_Mass_5to17", &L1_TripleMu_5_3p5_2p5_DoubleMu_5_2p5_OS_Mass_5to17, &b_L1_TripleMu_5_3p5_2p5_DoubleMu_5_2p5_OS_Mass_5to17);
   // fChain->SetBranchStatus("L1_TripleMu_5_3p5_2p5_OQ_DoubleMu_5_2p5_OQ_OS_Mass_5to17", 1);
   // fChain->SetBranchAddress("L1_TripleMu_5_3p5_2p5_OQ_DoubleMu_5_2p5_OQ_OS_Mass_5to17", &L1_TripleMu_5_3p5_2p5_OQ_DoubleMu_5_2p5_OQ_OS_Mass_5to17, &b_L1_TripleMu_5_3p5_2p5_OQ_DoubleMu_5_2p5_OQ_OS_Mass_5to17);
   // fChain->SetBranchStatus("L1_TripleMu_5_4_2p5_DoubleMu_5_2p5_OS_Mass_5to17", 1);
   // fChain->SetBranchAddress("L1_TripleMu_5_4_2p5_DoubleMu_5_2p5_OS_Mass_5to17", &L1_TripleMu_5_4_2p5_DoubleMu_5_2p5_OS_Mass_5to17, &b_L1_TripleMu_5_4_2p5_DoubleMu_5_2p5_OS_Mass_5to17);
   // fChain->SetBranchStatus("L1_TripleMu_5_5_3", 1);
   // fChain->SetBranchAddress("L1_TripleMu_5_5_3", &L1_TripleMu_5_5_3, &b_L1_TripleMu_5_5_3);
   // fChain->SetBranchStatus("L1_UnpairedBunchBptxMinus", 1);
   // fChain->SetBranchAddress("L1_UnpairedBunchBptxMinus", &L1_UnpairedBunchBptxMinus, &b_L1_UnpairedBunchBptxMinus);
   // fChain->SetBranchStatus("L1_UnpairedBunchBptxPlus", 1);
   // fChain->SetBranchAddress("L1_UnpairedBunchBptxPlus", &L1_UnpairedBunchBptxPlus, &b_L1_UnpairedBunchBptxPlus);
   // fChain->SetBranchStatus("L1_ZeroBias", 1);
   // fChain->SetBranchAddress("L1_ZeroBias", &L1_ZeroBias, &b_L1_ZeroBias);
   // fChain->SetBranchStatus("L1_ZeroBias_copy", 1);
   // fChain->SetBranchAddress("L1_ZeroBias_copy", &L1_ZeroBias_copy, &b_L1_ZeroBias_copy);
   // fChain->SetBranchStatus("L1_UnprefireableEvent", 1);
   // fChain->SetBranchAddress("L1_UnprefireableEvent", &L1_UnprefireableEvent, &b_L1_UnprefireableEvent);
   fChain->SetBranchStatus("Flag_HBHENoiseFilter", 1);
   fChain->SetBranchAddress("Flag_HBHENoiseFilter", &Flag_HBHENoiseFilter, &b_Flag_HBHENoiseFilter);
   fChain->SetBranchStatus("Flag_HBHENoiseIsoFilter", 1);
   fChain->SetBranchAddress("Flag_HBHENoiseIsoFilter", &Flag_HBHENoiseIsoFilter, &b_Flag_HBHENoiseIsoFilter);
   fChain->SetBranchStatus("Flag_CSCTightHaloFilter", 1);
   fChain->SetBranchAddress("Flag_CSCTightHaloFilter", &Flag_CSCTightHaloFilter, &b_Flag_CSCTightHaloFilter);
   fChain->SetBranchStatus("Flag_CSCTightHaloTrkMuUnvetoFilter", 1);
   fChain->SetBranchAddress("Flag_CSCTightHaloTrkMuUnvetoFilter", &Flag_CSCTightHaloTrkMuUnvetoFilter, &b_Flag_CSCTightHaloTrkMuUnvetoFilter);
   fChain->SetBranchStatus("Flag_CSCTightHalo2015Filter", 1);
   fChain->SetBranchAddress("Flag_CSCTightHalo2015Filter", &Flag_CSCTightHalo2015Filter, &b_Flag_CSCTightHalo2015Filter);
   fChain->SetBranchStatus("Flag_globalTightHalo2016Filter", 1);
   fChain->SetBranchAddress("Flag_globalTightHalo2016Filter", &Flag_globalTightHalo2016Filter, &b_Flag_globalTightHalo2016Filter);
   fChain->SetBranchStatus("Flag_globalSuperTightHalo2016Filter", 1);
   fChain->SetBranchAddress("Flag_globalSuperTightHalo2016Filter", &Flag_globalSuperTightHalo2016Filter, &b_Flag_globalSuperTightHalo2016Filter);
   fChain->SetBranchStatus("Flag_HcalStripHaloFilter", 1);
   fChain->SetBranchAddress("Flag_HcalStripHaloFilter", &Flag_HcalStripHaloFilter, &b_Flag_HcalStripHaloFilter);
   fChain->SetBranchStatus("Flag_hcalLaserEventFilter", 1);
   fChain->SetBranchAddress("Flag_hcalLaserEventFilter", &Flag_hcalLaserEventFilter, &b_Flag_hcalLaserEventFilter);
   fChain->SetBranchStatus("Flag_EcalDeadCellTriggerPrimitiveFilter", 1);
   fChain->SetBranchAddress("Flag_EcalDeadCellTriggerPrimitiveFilter", &Flag_EcalDeadCellTriggerPrimitiveFilter, &b_Flag_EcalDeadCellTriggerPrimitiveFilter);
   fChain->SetBranchStatus("Flag_EcalDeadCellBoundaryEnergyFilter", 1);
   fChain->SetBranchAddress("Flag_EcalDeadCellBoundaryEnergyFilter", &Flag_EcalDeadCellBoundaryEnergyFilter, &b_Flag_EcalDeadCellBoundaryEnergyFilter);
   fChain->SetBranchStatus("Flag_ecalBadCalibFilter", 1);
   fChain->SetBranchAddress("Flag_ecalBadCalibFilter", &Flag_ecalBadCalibFilter, &b_Flag_ecalBadCalibFilter);
   fChain->SetBranchStatus("Flag_goodVertices", 1);
   fChain->SetBranchAddress("Flag_goodVertices", &Flag_goodVertices, &b_Flag_goodVertices);
   fChain->SetBranchStatus("Flag_eeBadScFilter", 1);
   fChain->SetBranchAddress("Flag_eeBadScFilter", &Flag_eeBadScFilter, &b_Flag_eeBadScFilter);
   fChain->SetBranchStatus("Flag_ecalLaserCorrFilter", 1);
   fChain->SetBranchAddress("Flag_ecalLaserCorrFilter", &Flag_ecalLaserCorrFilter, &b_Flag_ecalLaserCorrFilter);
   fChain->SetBranchStatus("Flag_trkPOGFilters", 1);
   fChain->SetBranchAddress("Flag_trkPOGFilters", &Flag_trkPOGFilters, &b_Flag_trkPOGFilters);
   fChain->SetBranchStatus("Flag_chargedHadronTrackResolutionFilter", 1);
   fChain->SetBranchAddress("Flag_chargedHadronTrackResolutionFilter", &Flag_chargedHadronTrackResolutionFilter, &b_Flag_chargedHadronTrackResolutionFilter);
   fChain->SetBranchStatus("Flag_muonBadTrackFilter", 1);
   fChain->SetBranchAddress("Flag_muonBadTrackFilter", &Flag_muonBadTrackFilter, &b_Flag_muonBadTrackFilter);
   fChain->SetBranchStatus("Flag_BadChargedCandidateFilter", 1);
   fChain->SetBranchAddress("Flag_BadChargedCandidateFilter", &Flag_BadChargedCandidateFilter, &b_Flag_BadChargedCandidateFilter);
   fChain->SetBranchStatus("Flag_BadPFMuonFilter", 1);
   fChain->SetBranchAddress("Flag_BadPFMuonFilter", &Flag_BadPFMuonFilter, &b_Flag_BadPFMuonFilter);
   fChain->SetBranchStatus("Flag_BadPFMuonDzFilter", 1);
   fChain->SetBranchAddress("Flag_BadPFMuonDzFilter", &Flag_BadPFMuonDzFilter, &b_Flag_BadPFMuonDzFilter);
   fChain->SetBranchStatus("Flag_hfNoisyHitsFilter", 1);
   fChain->SetBranchAddress("Flag_hfNoisyHitsFilter", &Flag_hfNoisyHitsFilter, &b_Flag_hfNoisyHitsFilter);
   fChain->SetBranchStatus("Flag_BadChargedCandidateSummer16Filter", 1);
   fChain->SetBranchAddress("Flag_BadChargedCandidateSummer16Filter", &Flag_BadChargedCandidateSummer16Filter, &b_Flag_BadChargedCandidateSummer16Filter);
   fChain->SetBranchStatus("Flag_BadPFMuonSummer16Filter", 1);
   fChain->SetBranchAddress("Flag_BadPFMuonSummer16Filter", &Flag_BadPFMuonSummer16Filter, &b_Flag_BadPFMuonSummer16Filter);
   fChain->SetBranchStatus("Flag_trkPOG_manystripclus53X", 1);
   fChain->SetBranchAddress("Flag_trkPOG_manystripclus53X", &Flag_trkPOG_manystripclus53X, &b_Flag_trkPOG_manystripclus53X);
   fChain->SetBranchStatus("Flag_trkPOG_toomanystripclus53X", 1);
   fChain->SetBranchAddress("Flag_trkPOG_toomanystripclus53X", &Flag_trkPOG_toomanystripclus53X, &b_Flag_trkPOG_toomanystripclus53X);
   fChain->SetBranchStatus("Flag_trkPOG_logErrorTooManyClusters", 1);
   fChain->SetBranchAddress("Flag_trkPOG_logErrorTooManyClusters", &Flag_trkPOG_logErrorTooManyClusters, &b_Flag_trkPOG_logErrorTooManyClusters);
   //fChain->SetBranchStatus("Flag_METFilters", 1);
   //fChain->SetBranchAddress("Flag_METFilters", &Flag_METFilters, &b_Flag_METFilters);
   fChain->SetBranchStatus("L1Reco_step", 1);
   fChain->SetBranchAddress("L1Reco_step", &L1Reco_step, &b_L1Reco_step);
   fChain->SetBranchStatus("HLTriggerFirstPath", 1);
   fChain->SetBranchAddress("HLTriggerFirstPath", &HLTriggerFirstPath, &b_HLTriggerFirstPath);
   // fChain->SetBranchStatus("HLT_AK8PFJet360_TrimMass30", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet360_TrimMass30", &HLT_AK8PFJet360_TrimMass30, &b_HLT_AK8PFJet360_TrimMass30);
   // fChain->SetBranchStatus("HLT_AK8PFJet380_TrimMass30", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet380_TrimMass30", &HLT_AK8PFJet380_TrimMass30, &b_HLT_AK8PFJet380_TrimMass30);
   // fChain->SetBranchStatus("HLT_AK8PFJet400_TrimMass30", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet400_TrimMass30", &HLT_AK8PFJet400_TrimMass30, &b_HLT_AK8PFJet400_TrimMass30);
   // fChain->SetBranchStatus("HLT_AK8PFJet420_TrimMass30", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet420_TrimMass30", &HLT_AK8PFJet420_TrimMass30, &b_HLT_AK8PFJet420_TrimMass30);
   // fChain->SetBranchStatus("HLT_AK8PFHT750_TrimMass50", 1);
   // fChain->SetBranchAddress("HLT_AK8PFHT750_TrimMass50", &HLT_AK8PFHT750_TrimMass50, &b_HLT_AK8PFHT750_TrimMass50);
   // fChain->SetBranchStatus("HLT_AK8PFHT800_TrimMass50", 1);
   // fChain->SetBranchAddress("HLT_AK8PFHT800_TrimMass50", &HLT_AK8PFHT800_TrimMass50, &b_HLT_AK8PFHT800_TrimMass50);
   // fChain->SetBranchStatus("HLT_AK8PFHT850_TrimMass50", 1);
   // fChain->SetBranchAddress("HLT_AK8PFHT850_TrimMass50", &HLT_AK8PFHT850_TrimMass50, &b_HLT_AK8PFHT850_TrimMass50);
   // fChain->SetBranchStatus("HLT_AK8PFHT900_TrimMass50", 1);
   // fChain->SetBranchAddress("HLT_AK8PFHT900_TrimMass50", &HLT_AK8PFHT900_TrimMass50, &b_HLT_AK8PFHT900_TrimMass50);
   // fChain->SetBranchStatus("HLT_CaloJet500_NoJetID", 1);
   // fChain->SetBranchAddress("HLT_CaloJet500_NoJetID", &HLT_CaloJet500_NoJetID, &b_HLT_CaloJet500_NoJetID);
   // fChain->SetBranchStatus("HLT_CaloJet550_NoJetID", 1);
   // fChain->SetBranchAddress("HLT_CaloJet550_NoJetID", &HLT_CaloJet550_NoJetID, &b_HLT_CaloJet550_NoJetID);
   // fChain->SetBranchStatus("HLT_DoubleMu5_Upsilon_DoubleEle3_CaloIdL_TrackIdL", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu5_Upsilon_DoubleEle3_CaloIdL_TrackIdL", &HLT_DoubleMu5_Upsilon_DoubleEle3_CaloIdL_TrackIdL, &b_HLT_DoubleMu5_Upsilon_DoubleEle3_CaloIdL_TrackIdL);
   // fChain->SetBranchStatus("HLT_DoubleMu3_DoubleEle7p5_CaloIdL_TrackIdL_Upsilon", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu3_DoubleEle7p5_CaloIdL_TrackIdL_Upsilon", &HLT_DoubleMu3_DoubleEle7p5_CaloIdL_TrackIdL_Upsilon, &b_HLT_DoubleMu3_DoubleEle7p5_CaloIdL_TrackIdL_Upsilon);
   // fChain->SetBranchStatus("HLT_Trimuon5_3p5_2_Upsilon_Muon", 1);
   // fChain->SetBranchAddress("HLT_Trimuon5_3p5_2_Upsilon_Muon", &HLT_Trimuon5_3p5_2_Upsilon_Muon, &b_HLT_Trimuon5_3p5_2_Upsilon_Muon);
   // fChain->SetBranchStatus("HLT_TrimuonOpen_5_3p5_2_Upsilon_Muon", 1);
   // fChain->SetBranchAddress("HLT_TrimuonOpen_5_3p5_2_Upsilon_Muon", &HLT_TrimuonOpen_5_3p5_2_Upsilon_Muon, &b_HLT_TrimuonOpen_5_3p5_2_Upsilon_Muon);
   // fChain->SetBranchStatus("HLT_DoubleEle25_CaloIdL_MW", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle25_CaloIdL_MW", &HLT_DoubleEle25_CaloIdL_MW, &b_HLT_DoubleEle25_CaloIdL_MW);
   // fChain->SetBranchStatus("HLT_DoubleEle27_CaloIdL_MW", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle27_CaloIdL_MW", &HLT_DoubleEle27_CaloIdL_MW, &b_HLT_DoubleEle27_CaloIdL_MW);
   // fChain->SetBranchStatus("HLT_DoubleEle33_CaloIdL_MW", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle33_CaloIdL_MW", &HLT_DoubleEle33_CaloIdL_MW, &b_HLT_DoubleEle33_CaloIdL_MW);
   // fChain->SetBranchStatus("HLT_DoubleEle24_eta2p1_WPTight_Gsf", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle24_eta2p1_WPTight_Gsf", &HLT_DoubleEle24_eta2p1_WPTight_Gsf, &b_HLT_DoubleEle24_eta2p1_WPTight_Gsf);
   // fChain->SetBranchStatus("HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_DZ_PFHT350", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_DZ_PFHT350", &HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_DZ_PFHT350, &b_HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_DZ_PFHT350);
   // fChain->SetBranchStatus("HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_PFHT350", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_PFHT350", &HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_PFHT350, &b_HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_PFHT350);
   // fChain->SetBranchStatus("HLT_Ele27_Ele37_CaloIdL_MW", 1);
   // fChain->SetBranchAddress("HLT_Ele27_Ele37_CaloIdL_MW", &HLT_Ele27_Ele37_CaloIdL_MW, &b_HLT_Ele27_Ele37_CaloIdL_MW);
   // fChain->SetBranchStatus("HLT_Mu27_Ele37_CaloIdL_MW", 1);
   // fChain->SetBranchAddress("HLT_Mu27_Ele37_CaloIdL_MW", &HLT_Mu27_Ele37_CaloIdL_MW, &b_HLT_Mu27_Ele37_CaloIdL_MW);
   // fChain->SetBranchStatus("HLT_Mu37_Ele27_CaloIdL_MW", 1);
   // fChain->SetBranchAddress("HLT_Mu37_Ele27_CaloIdL_MW", &HLT_Mu37_Ele27_CaloIdL_MW, &b_HLT_Mu37_Ele27_CaloIdL_MW);
   // fChain->SetBranchStatus("HLT_Mu37_TkMu27", 1);
   // fChain->SetBranchAddress("HLT_Mu37_TkMu27", &HLT_Mu37_TkMu27, &b_HLT_Mu37_TkMu27);
   // fChain->SetBranchStatus("HLT_DoubleMu4_3_Bs", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu4_3_Bs", &HLT_DoubleMu4_3_Bs, &b_HLT_DoubleMu4_3_Bs);
   // fChain->SetBranchStatus("HLT_DoubleMu4_3_Jpsi", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu4_3_Jpsi", &HLT_DoubleMu4_3_Jpsi, &b_HLT_DoubleMu4_3_Jpsi);
   // fChain->SetBranchStatus("HLT_DoubleMu4_3_LowMass", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu4_3_LowMass", &HLT_DoubleMu4_3_LowMass, &b_HLT_DoubleMu4_3_LowMass);
   // fChain->SetBranchStatus("HLT_DoubleMu4_LowMass_Displaced", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu4_LowMass_Displaced", &HLT_DoubleMu4_LowMass_Displaced, &b_HLT_DoubleMu4_LowMass_Displaced);
   // fChain->SetBranchStatus("HLT_Mu0_L1DoubleMu", 1);
   // fChain->SetBranchAddress("HLT_Mu0_L1DoubleMu", &HLT_Mu0_L1DoubleMu, &b_HLT_Mu0_L1DoubleMu);
   // fChain->SetBranchStatus("HLT_Mu4_L1DoubleMu", 1);
   // fChain->SetBranchAddress("HLT_Mu4_L1DoubleMu", &HLT_Mu4_L1DoubleMu, &b_HLT_Mu4_L1DoubleMu);
   // fChain->SetBranchStatus("HLT_DoubleMu3_Trk_Tau3mu", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu3_Trk_Tau3mu", &HLT_DoubleMu3_Trk_Tau3mu, &b_HLT_DoubleMu3_Trk_Tau3mu);
   // fChain->SetBranchStatus("HLT_DoubleMu3_TkMu_DsTau3Mu", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu3_TkMu_DsTau3Mu", &HLT_DoubleMu3_TkMu_DsTau3Mu, &b_HLT_DoubleMu3_TkMu_DsTau3Mu);
   // fChain->SetBranchStatus("HLT_DoubleMu4_Mass3p8_DZ_PFHT350", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu4_Mass3p8_DZ_PFHT350", &HLT_DoubleMu4_Mass3p8_DZ_PFHT350, &b_HLT_DoubleMu4_Mass3p8_DZ_PFHT350);
   // fChain->SetBranchStatus("HLT_DoubleMu4_MuMuTrk_Displaced", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu4_MuMuTrk_Displaced", &HLT_DoubleMu4_MuMuTrk_Displaced, &b_HLT_DoubleMu4_MuMuTrk_Displaced);
   // fChain->SetBranchStatus("HLT_Mu3_PFJet40", 1);
   // fChain->SetBranchAddress("HLT_Mu3_PFJet40", &HLT_Mu3_PFJet40, &b_HLT_Mu3_PFJet40);
   // fChain->SetBranchStatus("HLT_Mu7p5_L2Mu2_Jpsi", 1);
   // fChain->SetBranchAddress("HLT_Mu7p5_L2Mu2_Jpsi", &HLT_Mu7p5_L2Mu2_Jpsi, &b_HLT_Mu7p5_L2Mu2_Jpsi);
   // fChain->SetBranchStatus("HLT_Mu7p5_L2Mu2_Upsilon", 1);
   // fChain->SetBranchAddress("HLT_Mu7p5_L2Mu2_Upsilon", &HLT_Mu7p5_L2Mu2_Upsilon, &b_HLT_Mu7p5_L2Mu2_Upsilon);
   // fChain->SetBranchStatus("HLT_Mu3_L1SingleMu5orSingleMu7", 1);
   // fChain->SetBranchAddress("HLT_Mu3_L1SingleMu5orSingleMu7", &HLT_Mu3_L1SingleMu5orSingleMu7, &b_HLT_Mu3_L1SingleMu5orSingleMu7);
   // fChain->SetBranchStatus("HLT_DoublePhoton33_CaloIdL", 1);
   // fChain->SetBranchAddress("HLT_DoublePhoton33_CaloIdL", &HLT_DoublePhoton33_CaloIdL, &b_HLT_DoublePhoton33_CaloIdL);
   // fChain->SetBranchStatus("HLT_DoublePhoton70", 1);
   // fChain->SetBranchAddress("HLT_DoublePhoton70", &HLT_DoublePhoton70, &b_HLT_DoublePhoton70);
   // fChain->SetBranchStatus("HLT_DoublePhoton85", 1);
   // fChain->SetBranchAddress("HLT_DoublePhoton85", &HLT_DoublePhoton85, &b_HLT_DoublePhoton85);
   // fChain->SetBranchStatus("HLT_Ele20_WPTight_Gsf", 1);
   // fChain->SetBranchAddress("HLT_Ele20_WPTight_Gsf", &HLT_Ele20_WPTight_Gsf, &b_HLT_Ele20_WPTight_Gsf);
   // fChain->SetBranchStatus("HLT_Ele15_WPLoose_Gsf", 1);
   // fChain->SetBranchAddress("HLT_Ele15_WPLoose_Gsf", &HLT_Ele15_WPLoose_Gsf, &b_HLT_Ele15_WPLoose_Gsf);
   // fChain->SetBranchStatus("HLT_Ele17_WPLoose_Gsf", 1);
   // fChain->SetBranchAddress("HLT_Ele17_WPLoose_Gsf", &HLT_Ele17_WPLoose_Gsf, &b_HLT_Ele17_WPLoose_Gsf);
   // fChain->SetBranchStatus("HLT_Ele20_WPLoose_Gsf", 1);
   // fChain->SetBranchAddress("HLT_Ele20_WPLoose_Gsf", &HLT_Ele20_WPLoose_Gsf, &b_HLT_Ele20_WPLoose_Gsf);
   // fChain->SetBranchStatus("HLT_Ele20_eta2p1_WPLoose_Gsf", 1);
   // fChain->SetBranchAddress("HLT_Ele20_eta2p1_WPLoose_Gsf", &HLT_Ele20_eta2p1_WPLoose_Gsf, &b_HLT_Ele20_eta2p1_WPLoose_Gsf);
   // fChain->SetBranchStatus("HLT_DiEle27_WPTightCaloOnly_L1DoubleEG", 1);
   // fChain->SetBranchAddress("HLT_DiEle27_WPTightCaloOnly_L1DoubleEG", &HLT_DiEle27_WPTightCaloOnly_L1DoubleEG, &b_HLT_DiEle27_WPTightCaloOnly_L1DoubleEG);
   // fChain->SetBranchStatus("HLT_Ele27_WPTight_Gsf", 1);
   // fChain->SetBranchAddress("HLT_Ele27_WPTight_Gsf", &HLT_Ele27_WPTight_Gsf, &b_HLT_Ele27_WPTight_Gsf);
   // fChain->SetBranchStatus("HLT_Ele28_WPTight_Gsf", 1);
   // fChain->SetBranchAddress("HLT_Ele28_WPTight_Gsf", &HLT_Ele28_WPTight_Gsf, &b_HLT_Ele28_WPTight_Gsf);
   // fChain->SetBranchStatus("HLT_Ele30_WPTight_Gsf", 1);
   // fChain->SetBranchAddress("HLT_Ele30_WPTight_Gsf", &HLT_Ele30_WPTight_Gsf, &b_HLT_Ele30_WPTight_Gsf);
   // fChain->SetBranchStatus("HLT_Ele32_WPTight_Gsf", 1);
   // fChain->SetBranchAddress("HLT_Ele32_WPTight_Gsf", &HLT_Ele32_WPTight_Gsf, &b_HLT_Ele32_WPTight_Gsf);
   // fChain->SetBranchStatus("HLT_Ele35_WPTight_Gsf", 1);
   // fChain->SetBranchAddress("HLT_Ele35_WPTight_Gsf", &HLT_Ele35_WPTight_Gsf, &b_HLT_Ele35_WPTight_Gsf);
   // fChain->SetBranchStatus("HLT_Ele35_WPTight_Gsf_L1EGMT", 1);
   // fChain->SetBranchAddress("HLT_Ele35_WPTight_Gsf_L1EGMT", &HLT_Ele35_WPTight_Gsf_L1EGMT, &b_HLT_Ele35_WPTight_Gsf_L1EGMT);
   // fChain->SetBranchStatus("HLT_Ele38_WPTight_Gsf", 1);
   // fChain->SetBranchAddress("HLT_Ele38_WPTight_Gsf", &HLT_Ele38_WPTight_Gsf, &b_HLT_Ele38_WPTight_Gsf);
   // fChain->SetBranchStatus("HLT_Ele40_WPTight_Gsf", 1);
   // fChain->SetBranchAddress("HLT_Ele40_WPTight_Gsf", &HLT_Ele40_WPTight_Gsf, &b_HLT_Ele40_WPTight_Gsf);
   // fChain->SetBranchStatus("HLT_Ele32_WPTight_Gsf_L1DoubleEG", 1);
   // fChain->SetBranchAddress("HLT_Ele32_WPTight_Gsf_L1DoubleEG", &HLT_Ele32_WPTight_Gsf_L1DoubleEG, &b_HLT_Ele32_WPTight_Gsf_L1DoubleEG);
   // fChain->SetBranchStatus("HLT_Ele24_eta2p1_WPTight_Gsf_TightChargedIsoPFTauHPS30_eta2p1_CrossL1", 1);
   // fChain->SetBranchAddress("HLT_Ele24_eta2p1_WPTight_Gsf_TightChargedIsoPFTauHPS30_eta2p1_CrossL1", &HLT_Ele24_eta2p1_WPTight_Gsf_TightChargedIsoPFTauHPS30_eta2p1_CrossL1, &b_HLT_Ele24_eta2p1_WPTight_Gsf_TightChargedIsoPFTauHPS30_eta2p1_CrossL1);
   // fChain->SetBranchStatus("HLT_HT450_Beamspot", 1);
   // fChain->SetBranchAddress("HLT_HT450_Beamspot", &HLT_HT450_Beamspot, &b_HLT_HT450_Beamspot);
   // fChain->SetBranchStatus("HLT_HT300_Beamspot", 1);
   // fChain->SetBranchAddress("HLT_HT300_Beamspot", &HLT_HT300_Beamspot, &b_HLT_HT300_Beamspot);
   // fChain->SetBranchStatus("HLT_ZeroBias_Beamspot", 1);
   // fChain->SetBranchAddress("HLT_ZeroBias_Beamspot", &HLT_ZeroBias_Beamspot, &b_HLT_ZeroBias_Beamspot);
   // fChain->SetBranchStatus("HLT_IsoMu20_eta2p1_TightChargedIsoPFTauHPS27_eta2p1_CrossL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu20_eta2p1_TightChargedIsoPFTauHPS27_eta2p1_CrossL1", &HLT_IsoMu20_eta2p1_TightChargedIsoPFTauHPS27_eta2p1_CrossL1, &b_HLT_IsoMu20_eta2p1_TightChargedIsoPFTauHPS27_eta2p1_CrossL1);
   // fChain->SetBranchStatus("HLT_IsoMu20_eta2p1_TightChargedIsoPFTauHPS27_eta2p1_TightID_CrossL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu20_eta2p1_TightChargedIsoPFTauHPS27_eta2p1_TightID_CrossL1", &HLT_IsoMu20_eta2p1_TightChargedIsoPFTauHPS27_eta2p1_TightID_CrossL1, &b_HLT_IsoMu20_eta2p1_TightChargedIsoPFTauHPS27_eta2p1_TightID_CrossL1);
   // fChain->SetBranchStatus("HLT_IsoMu27_LooseChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu27_LooseChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1", &HLT_IsoMu27_LooseChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1, &b_HLT_IsoMu27_LooseChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1);
   // fChain->SetBranchStatus("HLT_IsoMu27_MediumChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu27_MediumChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1", &HLT_IsoMu27_MediumChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1, &b_HLT_IsoMu27_MediumChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1);
   // fChain->SetBranchStatus("HLT_IsoMu27_TightChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu27_TightChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1", &HLT_IsoMu27_TightChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1, &b_HLT_IsoMu27_TightChargedIsoPFTauHPS20_Trk1_eta2p1_SingleL1);
   // fChain->SetBranchStatus("HLT_IsoMu20", 1);
   // fChain->SetBranchAddress("HLT_IsoMu20", &HLT_IsoMu20, &b_HLT_IsoMu20);
   fChain->SetBranchStatus("HLT_IsoMu24", 1);
   fChain->SetBranchAddress("HLT_IsoMu24", &HLT_IsoMu24, &b_HLT_IsoMu24);
   // fChain->SetBranchStatus("HLT_IsoMu24_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu24_eta2p1", &HLT_IsoMu24_eta2p1, &b_HLT_IsoMu24_eta2p1);
   // fChain->SetBranchStatus("HLT_IsoMu27", 1);
   // fChain->SetBranchAddress("HLT_IsoMu27", &HLT_IsoMu27, &b_HLT_IsoMu27);
   // fChain->SetBranchStatus("HLT_IsoMu30", 1);
   // fChain->SetBranchAddress("HLT_IsoMu30", &HLT_IsoMu30, &b_HLT_IsoMu30);
   // fChain->SetBranchStatus("HLT_UncorrectedJetE30_NoBPTX", 1);
   // fChain->SetBranchAddress("HLT_UncorrectedJetE30_NoBPTX", &HLT_UncorrectedJetE30_NoBPTX, &b_HLT_UncorrectedJetE30_NoBPTX);
   // fChain->SetBranchStatus("HLT_UncorrectedJetE30_NoBPTX3BX", 1);
   // fChain->SetBranchAddress("HLT_UncorrectedJetE30_NoBPTX3BX", &HLT_UncorrectedJetE30_NoBPTX3BX, &b_HLT_UncorrectedJetE30_NoBPTX3BX);
   // fChain->SetBranchStatus("HLT_UncorrectedJetE60_NoBPTX3BX", 1);
   // fChain->SetBranchAddress("HLT_UncorrectedJetE60_NoBPTX3BX", &HLT_UncorrectedJetE60_NoBPTX3BX, &b_HLT_UncorrectedJetE60_NoBPTX3BX);
   // fChain->SetBranchStatus("HLT_UncorrectedJetE70_NoBPTX3BX", 1);
   // fChain->SetBranchAddress("HLT_UncorrectedJetE70_NoBPTX3BX", &HLT_UncorrectedJetE70_NoBPTX3BX, &b_HLT_UncorrectedJetE70_NoBPTX3BX);
   // fChain->SetBranchStatus("HLT_L1SingleMu18", 1);
   // fChain->SetBranchAddress("HLT_L1SingleMu18", &HLT_L1SingleMu18, &b_HLT_L1SingleMu18);
   // fChain->SetBranchStatus("HLT_L1SingleMu25", 1);
   // fChain->SetBranchAddress("HLT_L1SingleMu25", &HLT_L1SingleMu25, &b_HLT_L1SingleMu25);
   // fChain->SetBranchStatus("HLT_L1SingleMuCosmics", 1);
   // fChain->SetBranchAddress("HLT_L1SingleMuCosmics", &HLT_L1SingleMuCosmics, &b_HLT_L1SingleMuCosmics);
   // fChain->SetBranchStatus("HLT_L2Mu10", 1);
   // fChain->SetBranchAddress("HLT_L2Mu10", &HLT_L2Mu10, &b_HLT_L2Mu10);
   // fChain->SetBranchStatus("HLT_L2Mu10_NoVertex_NoBPTX3BX", 1);
   // fChain->SetBranchAddress("HLT_L2Mu10_NoVertex_NoBPTX3BX", &HLT_L2Mu10_NoVertex_NoBPTX3BX, &b_HLT_L2Mu10_NoVertex_NoBPTX3BX);
   // fChain->SetBranchStatus("HLT_L2Mu10_NoVertex_NoBPTX", 1);
   // fChain->SetBranchAddress("HLT_L2Mu10_NoVertex_NoBPTX", &HLT_L2Mu10_NoVertex_NoBPTX, &b_HLT_L2Mu10_NoVertex_NoBPTX);
   // fChain->SetBranchStatus("HLT_L2Mu45_NoVertex_3Sta_NoBPTX3BX", 1);
   // fChain->SetBranchAddress("HLT_L2Mu45_NoVertex_3Sta_NoBPTX3BX", &HLT_L2Mu45_NoVertex_3Sta_NoBPTX3BX, &b_HLT_L2Mu45_NoVertex_3Sta_NoBPTX3BX);
   // fChain->SetBranchStatus("HLT_L2Mu40_NoVertex_3Sta_NoBPTX3BX", 1);
   // fChain->SetBranchAddress("HLT_L2Mu40_NoVertex_3Sta_NoBPTX3BX", &HLT_L2Mu40_NoVertex_3Sta_NoBPTX3BX, &b_HLT_L2Mu40_NoVertex_3Sta_NoBPTX3BX);
   // fChain->SetBranchStatus("HLT_L2Mu50", 1);
   // fChain->SetBranchAddress("HLT_L2Mu50", &HLT_L2Mu50, &b_HLT_L2Mu50);
   // fChain->SetBranchStatus("HLT_L2Mu23NoVtx_2Cha", 1);
   // fChain->SetBranchAddress("HLT_L2Mu23NoVtx_2Cha", &HLT_L2Mu23NoVtx_2Cha, &b_HLT_L2Mu23NoVtx_2Cha);
   // fChain->SetBranchStatus("HLT_L2Mu23NoVtx_2Cha_CosmicSeed", 1);
   // fChain->SetBranchAddress("HLT_L2Mu23NoVtx_2Cha_CosmicSeed", &HLT_L2Mu23NoVtx_2Cha_CosmicSeed, &b_HLT_L2Mu23NoVtx_2Cha_CosmicSeed);
   // fChain->SetBranchStatus("HLT_DoubleL2Mu30NoVtx_2Cha_CosmicSeed_Eta2p4", 1);
   // fChain->SetBranchAddress("HLT_DoubleL2Mu30NoVtx_2Cha_CosmicSeed_Eta2p4", &HLT_DoubleL2Mu30NoVtx_2Cha_CosmicSeed_Eta2p4, &b_HLT_DoubleL2Mu30NoVtx_2Cha_CosmicSeed_Eta2p4);
   // fChain->SetBranchStatus("HLT_DoubleL2Mu30NoVtx_2Cha_Eta2p4", 1);
   // fChain->SetBranchAddress("HLT_DoubleL2Mu30NoVtx_2Cha_Eta2p4", &HLT_DoubleL2Mu30NoVtx_2Cha_Eta2p4, &b_HLT_DoubleL2Mu30NoVtx_2Cha_Eta2p4);
   // fChain->SetBranchStatus("HLT_DoubleL2Mu50", 1);
   // fChain->SetBranchAddress("HLT_DoubleL2Mu50", &HLT_DoubleL2Mu50, &b_HLT_DoubleL2Mu50);
   // fChain->SetBranchStatus("HLT_DoubleL2Mu23NoVtx_2Cha_CosmicSeed", 1);
   // fChain->SetBranchAddress("HLT_DoubleL2Mu23NoVtx_2Cha_CosmicSeed", &HLT_DoubleL2Mu23NoVtx_2Cha_CosmicSeed, &b_HLT_DoubleL2Mu23NoVtx_2Cha_CosmicSeed);
   // fChain->SetBranchStatus("HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed", 1);
   // fChain->SetBranchAddress("HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed", &HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed, &b_HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed);
   // fChain->SetBranchStatus("HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed_Eta2p4", 1);
   // fChain->SetBranchAddress("HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed_Eta2p4", &HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed_Eta2p4, &b_HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed_Eta2p4);
   // fChain->SetBranchStatus("HLT_DoubleL2Mu23NoVtx_2Cha", 1);
   // fChain->SetBranchAddress("HLT_DoubleL2Mu23NoVtx_2Cha", &HLT_DoubleL2Mu23NoVtx_2Cha, &b_HLT_DoubleL2Mu23NoVtx_2Cha);
   // fChain->SetBranchStatus("HLT_DoubleL2Mu25NoVtx_2Cha", 1);
   // fChain->SetBranchAddress("HLT_DoubleL2Mu25NoVtx_2Cha", &HLT_DoubleL2Mu25NoVtx_2Cha, &b_HLT_DoubleL2Mu25NoVtx_2Cha);
   // fChain->SetBranchStatus("HLT_DoubleL2Mu25NoVtx_2Cha_Eta2p4", 1);
   // fChain->SetBranchAddress("HLT_DoubleL2Mu25NoVtx_2Cha_Eta2p4", &HLT_DoubleL2Mu25NoVtx_2Cha_Eta2p4, &b_HLT_DoubleL2Mu25NoVtx_2Cha_Eta2p4);
   // fChain->SetBranchStatus("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL", 1);
   // fChain->SetBranchAddress("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL", &HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL, &b_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL);
   // fChain->SetBranchStatus("HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL", 1);
   // fChain->SetBranchAddress("HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL", &HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL, &b_HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL);
   // fChain->SetBranchStatus("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ", 1);
   // fChain->SetBranchAddress("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ", &HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ, &b_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ);
   // fChain->SetBranchStatus("HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ", 1);
   // fChain->SetBranchAddress("HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ", &HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ, &b_HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ);
   // fChain->SetBranchStatus("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8", 1);
   // fChain->SetBranchAddress("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8", &HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8, &b_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8);
   // fChain->SetBranchStatus("HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass8", 1);
   // fChain->SetBranchAddress("HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass8", &HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass8, &b_HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass8);
   // fChain->SetBranchStatus("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8", 1);
   // fChain->SetBranchAddress("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8", &HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8, &b_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8);
   // fChain->SetBranchStatus("HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass3p8", 1);
   // fChain->SetBranchAddress("HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass3p8", &HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass3p8, &b_HLT_Mu19_TrkIsoVVL_Mu9_TrkIsoVVL_DZ_Mass3p8);
   // fChain->SetBranchStatus("HLT_Mu25_TkMu0_Onia", 1);
   // fChain->SetBranchAddress("HLT_Mu25_TkMu0_Onia", &HLT_Mu25_TkMu0_Onia, &b_HLT_Mu25_TkMu0_Onia);
   // fChain->SetBranchStatus("HLT_Mu30_TkMu0_Psi", 1);
   // fChain->SetBranchAddress("HLT_Mu30_TkMu0_Psi", &HLT_Mu30_TkMu0_Psi, &b_HLT_Mu30_TkMu0_Psi);
   // fChain->SetBranchStatus("HLT_Mu30_TkMu0_Upsilon", 1);
   // fChain->SetBranchAddress("HLT_Mu30_TkMu0_Upsilon", &HLT_Mu30_TkMu0_Upsilon, &b_HLT_Mu30_TkMu0_Upsilon);
   // fChain->SetBranchStatus("HLT_Mu20_TkMu0_Phi", 1);
   // fChain->SetBranchAddress("HLT_Mu20_TkMu0_Phi", &HLT_Mu20_TkMu0_Phi, &b_HLT_Mu20_TkMu0_Phi);
   // fChain->SetBranchStatus("HLT_Mu25_TkMu0_Phi", 1);
   // fChain->SetBranchAddress("HLT_Mu25_TkMu0_Phi", &HLT_Mu25_TkMu0_Phi, &b_HLT_Mu25_TkMu0_Phi);
   // fChain->SetBranchStatus("HLT_Mu12", 1);
   // fChain->SetBranchAddress("HLT_Mu12", &HLT_Mu12, &b_HLT_Mu12);
   // fChain->SetBranchStatus("HLT_Mu15", 1);
   // fChain->SetBranchAddress("HLT_Mu15", &HLT_Mu15, &b_HLT_Mu15);
   // fChain->SetBranchStatus("HLT_Mu20", 1);
   // fChain->SetBranchAddress("HLT_Mu20", &HLT_Mu20, &b_HLT_Mu20);
   // fChain->SetBranchStatus("HLT_Mu27", 1);
   // fChain->SetBranchAddress("HLT_Mu27", &HLT_Mu27, &b_HLT_Mu27);
   // fChain->SetBranchStatus("HLT_Mu50", 1);
   // fChain->SetBranchAddress("HLT_Mu50", &HLT_Mu50, &b_HLT_Mu50);
   // fChain->SetBranchStatus("HLT_Mu55", 1);
   // fChain->SetBranchAddress("HLT_Mu55", &HLT_Mu55, &b_HLT_Mu55);
   // fChain->SetBranchStatus("HLT_CascadeMu100", 1);
   // fChain->SetBranchAddress("HLT_CascadeMu100", &HLT_CascadeMu100, &b_HLT_CascadeMu100);
   // fChain->SetBranchStatus("HLT_HighPtTkMu100", 1);
   // fChain->SetBranchAddress("HLT_HighPtTkMu100", &HLT_HighPtTkMu100, &b_HLT_HighPtTkMu100);
   // fChain->SetBranchStatus("HLT_DiPFJetAve40", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve40", &HLT_DiPFJetAve40, &b_HLT_DiPFJetAve40);
   // fChain->SetBranchStatus("HLT_DiPFJetAve60", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve60", &HLT_DiPFJetAve60, &b_HLT_DiPFJetAve60);
   // fChain->SetBranchStatus("HLT_DiPFJetAve80", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve80", &HLT_DiPFJetAve80, &b_HLT_DiPFJetAve80);
   // fChain->SetBranchStatus("HLT_DiPFJetAve140", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve140", &HLT_DiPFJetAve140, &b_HLT_DiPFJetAve140);
   // fChain->SetBranchStatus("HLT_DiPFJetAve200", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve200", &HLT_DiPFJetAve200, &b_HLT_DiPFJetAve200);
   // fChain->SetBranchStatus("HLT_DiPFJetAve260", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve260", &HLT_DiPFJetAve260, &b_HLT_DiPFJetAve260);
   // fChain->SetBranchStatus("HLT_DiPFJetAve320", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve320", &HLT_DiPFJetAve320, &b_HLT_DiPFJetAve320);
   // fChain->SetBranchStatus("HLT_DiPFJetAve400", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve400", &HLT_DiPFJetAve400, &b_HLT_DiPFJetAve400);
   // fChain->SetBranchStatus("HLT_DiPFJetAve500", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve500", &HLT_DiPFJetAve500, &b_HLT_DiPFJetAve500);
   // fChain->SetBranchStatus("HLT_DiPFJetAve60_HFJEC", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve60_HFJEC", &HLT_DiPFJetAve60_HFJEC, &b_HLT_DiPFJetAve60_HFJEC);
   // fChain->SetBranchStatus("HLT_DiPFJetAve80_HFJEC", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve80_HFJEC", &HLT_DiPFJetAve80_HFJEC, &b_HLT_DiPFJetAve80_HFJEC);
   // fChain->SetBranchStatus("HLT_DiPFJetAve100_HFJEC", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve100_HFJEC", &HLT_DiPFJetAve100_HFJEC, &b_HLT_DiPFJetAve100_HFJEC);
   // fChain->SetBranchStatus("HLT_DiPFJetAve160_HFJEC", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve160_HFJEC", &HLT_DiPFJetAve160_HFJEC, &b_HLT_DiPFJetAve160_HFJEC);
   // fChain->SetBranchStatus("HLT_DiPFJetAve220_HFJEC", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve220_HFJEC", &HLT_DiPFJetAve220_HFJEC, &b_HLT_DiPFJetAve220_HFJEC);
   // fChain->SetBranchStatus("HLT_DiPFJetAve300_HFJEC", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve300_HFJEC", &HLT_DiPFJetAve300_HFJEC, &b_HLT_DiPFJetAve300_HFJEC);
   // fChain->SetBranchStatus("HLT_AK8PFJet15", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet15", &HLT_AK8PFJet15, &b_HLT_AK8PFJet15);
   // fChain->SetBranchStatus("HLT_AK8PFJet25", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet25", &HLT_AK8PFJet25, &b_HLT_AK8PFJet25);
   // fChain->SetBranchStatus("HLT_AK8PFJet40", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet40", &HLT_AK8PFJet40, &b_HLT_AK8PFJet40);
   // fChain->SetBranchStatus("HLT_AK8PFJet60", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet60", &HLT_AK8PFJet60, &b_HLT_AK8PFJet60);
   // fChain->SetBranchStatus("HLT_AK8PFJet80", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet80", &HLT_AK8PFJet80, &b_HLT_AK8PFJet80);
   // fChain->SetBranchStatus("HLT_AK8PFJet140", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet140", &HLT_AK8PFJet140, &b_HLT_AK8PFJet140);
   // fChain->SetBranchStatus("HLT_AK8PFJet200", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet200", &HLT_AK8PFJet200, &b_HLT_AK8PFJet200);
   // fChain->SetBranchStatus("HLT_AK8PFJet260", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet260", &HLT_AK8PFJet260, &b_HLT_AK8PFJet260);
   // fChain->SetBranchStatus("HLT_AK8PFJet320", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet320", &HLT_AK8PFJet320, &b_HLT_AK8PFJet320);
   // fChain->SetBranchStatus("HLT_AK8PFJet400", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet400", &HLT_AK8PFJet400, &b_HLT_AK8PFJet400);
   // fChain->SetBranchStatus("HLT_AK8PFJet450", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet450", &HLT_AK8PFJet450, &b_HLT_AK8PFJet450);
   // fChain->SetBranchStatus("HLT_AK8PFJet500", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet500", &HLT_AK8PFJet500, &b_HLT_AK8PFJet500);
   // fChain->SetBranchStatus("HLT_AK8PFJet550", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet550", &HLT_AK8PFJet550, &b_HLT_AK8PFJet550);
   // fChain->SetBranchStatus("HLT_PFJet15", 1);
   // fChain->SetBranchAddress("HLT_PFJet15", &HLT_PFJet15, &b_HLT_PFJet15);
   // fChain->SetBranchStatus("HLT_PFJet25", 1);
   // fChain->SetBranchAddress("HLT_PFJet25", &HLT_PFJet25, &b_HLT_PFJet25);
   // fChain->SetBranchStatus("HLT_PFJet40", 1);
   // fChain->SetBranchAddress("HLT_PFJet40", &HLT_PFJet40, &b_HLT_PFJet40);
   // fChain->SetBranchStatus("HLT_PFJet60", 1);
   // fChain->SetBranchAddress("HLT_PFJet60", &HLT_PFJet60, &b_HLT_PFJet60);
   // fChain->SetBranchStatus("HLT_PFJet80", 1);
   // fChain->SetBranchAddress("HLT_PFJet80", &HLT_PFJet80, &b_HLT_PFJet80);
   // fChain->SetBranchStatus("HLT_PFJet140", 1);
   // fChain->SetBranchAddress("HLT_PFJet140", &HLT_PFJet140, &b_HLT_PFJet140);
   // fChain->SetBranchStatus("HLT_PFJet200", 1);
   // fChain->SetBranchAddress("HLT_PFJet200", &HLT_PFJet200, &b_HLT_PFJet200);
   // fChain->SetBranchStatus("HLT_PFJet260", 1);
   // fChain->SetBranchAddress("HLT_PFJet260", &HLT_PFJet260, &b_HLT_PFJet260);
   // fChain->SetBranchStatus("HLT_PFJet320", 1);
   // fChain->SetBranchAddress("HLT_PFJet320", &HLT_PFJet320, &b_HLT_PFJet320);
   // fChain->SetBranchStatus("HLT_PFJet400", 1);
   // fChain->SetBranchAddress("HLT_PFJet400", &HLT_PFJet400, &b_HLT_PFJet400);
   // fChain->SetBranchStatus("HLT_PFJet450", 1);
   // fChain->SetBranchAddress("HLT_PFJet450", &HLT_PFJet450, &b_HLT_PFJet450);
   // fChain->SetBranchStatus("HLT_PFJet500", 1);
   // fChain->SetBranchAddress("HLT_PFJet500", &HLT_PFJet500, &b_HLT_PFJet500);
   // fChain->SetBranchStatus("HLT_PFJet550", 1);
   // fChain->SetBranchAddress("HLT_PFJet550", &HLT_PFJet550, &b_HLT_PFJet550);
   // fChain->SetBranchStatus("HLT_PFJetFwd15", 1);
   // fChain->SetBranchAddress("HLT_PFJetFwd15", &HLT_PFJetFwd15, &b_HLT_PFJetFwd15);
   // fChain->SetBranchStatus("HLT_PFJetFwd25", 1);
   // fChain->SetBranchAddress("HLT_PFJetFwd25", &HLT_PFJetFwd25, &b_HLT_PFJetFwd25);
   // fChain->SetBranchStatus("HLT_PFJetFwd40", 1);
   // fChain->SetBranchAddress("HLT_PFJetFwd40", &HLT_PFJetFwd40, &b_HLT_PFJetFwd40);
   // fChain->SetBranchStatus("HLT_PFJetFwd60", 1);
   // fChain->SetBranchAddress("HLT_PFJetFwd60", &HLT_PFJetFwd60, &b_HLT_PFJetFwd60);
   // fChain->SetBranchStatus("HLT_PFJetFwd80", 1);
   // fChain->SetBranchAddress("HLT_PFJetFwd80", &HLT_PFJetFwd80, &b_HLT_PFJetFwd80);
   // fChain->SetBranchStatus("HLT_PFJetFwd140", 1);
   // fChain->SetBranchAddress("HLT_PFJetFwd140", &HLT_PFJetFwd140, &b_HLT_PFJetFwd140);
   // fChain->SetBranchStatus("HLT_PFJetFwd200", 1);
   // fChain->SetBranchAddress("HLT_PFJetFwd200", &HLT_PFJetFwd200, &b_HLT_PFJetFwd200);
   // fChain->SetBranchStatus("HLT_PFJetFwd260", 1);
   // fChain->SetBranchAddress("HLT_PFJetFwd260", &HLT_PFJetFwd260, &b_HLT_PFJetFwd260);
   // fChain->SetBranchStatus("HLT_PFJetFwd320", 1);
   // fChain->SetBranchAddress("HLT_PFJetFwd320", &HLT_PFJetFwd320, &b_HLT_PFJetFwd320);
   // fChain->SetBranchStatus("HLT_PFJetFwd400", 1);
   // fChain->SetBranchAddress("HLT_PFJetFwd400", &HLT_PFJetFwd400, &b_HLT_PFJetFwd400);
   // fChain->SetBranchStatus("HLT_PFJetFwd450", 1);
   // fChain->SetBranchAddress("HLT_PFJetFwd450", &HLT_PFJetFwd450, &b_HLT_PFJetFwd450);
   // fChain->SetBranchStatus("HLT_PFJetFwd500", 1);
   // fChain->SetBranchAddress("HLT_PFJetFwd500", &HLT_PFJetFwd500, &b_HLT_PFJetFwd500);
   // fChain->SetBranchStatus("HLT_AK8PFJetFwd15", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJetFwd15", &HLT_AK8PFJetFwd15, &b_HLT_AK8PFJetFwd15);
   // fChain->SetBranchStatus("HLT_AK8PFJetFwd25", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJetFwd25", &HLT_AK8PFJetFwd25, &b_HLT_AK8PFJetFwd25);
   // fChain->SetBranchStatus("HLT_AK8PFJetFwd40", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJetFwd40", &HLT_AK8PFJetFwd40, &b_HLT_AK8PFJetFwd40);
   // fChain->SetBranchStatus("HLT_AK8PFJetFwd60", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJetFwd60", &HLT_AK8PFJetFwd60, &b_HLT_AK8PFJetFwd60);
   // fChain->SetBranchStatus("HLT_AK8PFJetFwd80", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJetFwd80", &HLT_AK8PFJetFwd80, &b_HLT_AK8PFJetFwd80);
   // fChain->SetBranchStatus("HLT_AK8PFJetFwd140", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJetFwd140", &HLT_AK8PFJetFwd140, &b_HLT_AK8PFJetFwd140);
   // fChain->SetBranchStatus("HLT_AK8PFJetFwd200", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJetFwd200", &HLT_AK8PFJetFwd200, &b_HLT_AK8PFJetFwd200);
   // fChain->SetBranchStatus("HLT_AK8PFJetFwd260", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJetFwd260", &HLT_AK8PFJetFwd260, &b_HLT_AK8PFJetFwd260);
   // fChain->SetBranchStatus("HLT_AK8PFJetFwd320", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJetFwd320", &HLT_AK8PFJetFwd320, &b_HLT_AK8PFJetFwd320);
   // fChain->SetBranchStatus("HLT_AK8PFJetFwd400", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJetFwd400", &HLT_AK8PFJetFwd400, &b_HLT_AK8PFJetFwd400);
   // fChain->SetBranchStatus("HLT_AK8PFJetFwd450", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJetFwd450", &HLT_AK8PFJetFwd450, &b_HLT_AK8PFJetFwd450);
   // fChain->SetBranchStatus("HLT_AK8PFJetFwd500", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJetFwd500", &HLT_AK8PFJetFwd500, &b_HLT_AK8PFJetFwd500);
   // fChain->SetBranchStatus("HLT_PFHT180", 1);
   // fChain->SetBranchAddress("HLT_PFHT180", &HLT_PFHT180, &b_HLT_PFHT180);
   // fChain->SetBranchStatus("HLT_PFHT250", 1);
   // fChain->SetBranchAddress("HLT_PFHT250", &HLT_PFHT250, &b_HLT_PFHT250);
   // fChain->SetBranchStatus("HLT_PFHT370", 1);
   // fChain->SetBranchAddress("HLT_PFHT370", &HLT_PFHT370, &b_HLT_PFHT370);
   // fChain->SetBranchStatus("HLT_PFHT430", 1);
   // fChain->SetBranchAddress("HLT_PFHT430", &HLT_PFHT430, &b_HLT_PFHT430);
   // fChain->SetBranchStatus("HLT_PFHT510", 1);
   // fChain->SetBranchAddress("HLT_PFHT510", &HLT_PFHT510, &b_HLT_PFHT510);
   // fChain->SetBranchStatus("HLT_PFHT590", 1);
   // fChain->SetBranchAddress("HLT_PFHT590", &HLT_PFHT590, &b_HLT_PFHT590);
   // fChain->SetBranchStatus("HLT_PFHT680", 1);
   // fChain->SetBranchAddress("HLT_PFHT680", &HLT_PFHT680, &b_HLT_PFHT680);
   // fChain->SetBranchStatus("HLT_PFHT780", 1);
   // fChain->SetBranchAddress("HLT_PFHT780", &HLT_PFHT780, &b_HLT_PFHT780);
   // fChain->SetBranchStatus("HLT_PFHT890", 1);
   // fChain->SetBranchAddress("HLT_PFHT890", &HLT_PFHT890, &b_HLT_PFHT890);
   // fChain->SetBranchStatus("HLT_PFHT1050", 1);
   // fChain->SetBranchAddress("HLT_PFHT1050", &HLT_PFHT1050, &b_HLT_PFHT1050);
   // fChain->SetBranchStatus("HLT_PFHT500_PFMET100_PFMHT100_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFHT500_PFMET100_PFMHT100_IDTight", &HLT_PFHT500_PFMET100_PFMHT100_IDTight, &b_HLT_PFHT500_PFMET100_PFMHT100_IDTight);
   // fChain->SetBranchStatus("HLT_PFHT500_PFMET110_PFMHT110_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFHT500_PFMET110_PFMHT110_IDTight", &HLT_PFHT500_PFMET110_PFMHT110_IDTight, &b_HLT_PFHT500_PFMET110_PFMHT110_IDTight);
   // fChain->SetBranchStatus("HLT_PFHT700_PFMET85_PFMHT85_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFHT700_PFMET85_PFMHT85_IDTight", &HLT_PFHT700_PFMET85_PFMHT85_IDTight, &b_HLT_PFHT700_PFMET85_PFMHT85_IDTight);
   // fChain->SetBranchStatus("HLT_PFHT700_PFMET95_PFMHT95_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFHT700_PFMET95_PFMHT95_IDTight", &HLT_PFHT700_PFMET95_PFMHT95_IDTight, &b_HLT_PFHT700_PFMET95_PFMHT95_IDTight);
   // fChain->SetBranchStatus("HLT_PFHT800_PFMET75_PFMHT75_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFHT800_PFMET75_PFMHT75_IDTight", &HLT_PFHT800_PFMET75_PFMHT75_IDTight, &b_HLT_PFHT800_PFMET75_PFMHT75_IDTight);
   // fChain->SetBranchStatus("HLT_PFHT800_PFMET85_PFMHT85_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFHT800_PFMET85_PFMHT85_IDTight", &HLT_PFHT800_PFMET85_PFMHT85_IDTight, &b_HLT_PFHT800_PFMET85_PFMHT85_IDTight);
   // fChain->SetBranchStatus("HLT_PFMET110_PFMHT110_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFMET110_PFMHT110_IDTight", &HLT_PFMET110_PFMHT110_IDTight, &b_HLT_PFMET110_PFMHT110_IDTight);
   // fChain->SetBranchStatus("HLT_PFMET120_PFMHT120_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFMET120_PFMHT120_IDTight", &HLT_PFMET120_PFMHT120_IDTight, &b_HLT_PFMET120_PFMHT120_IDTight);
   // fChain->SetBranchStatus("HLT_PFMET130_PFMHT130_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFMET130_PFMHT130_IDTight", &HLT_PFMET130_PFMHT130_IDTight, &b_HLT_PFMET130_PFMHT130_IDTight);
   // fChain->SetBranchStatus("HLT_PFMET140_PFMHT140_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFMET140_PFMHT140_IDTight", &HLT_PFMET140_PFMHT140_IDTight, &b_HLT_PFMET140_PFMHT140_IDTight);
   // fChain->SetBranchStatus("HLT_PFMET100_PFMHT100_IDTight_CaloBTagDeepCSV_3p1", 1);
   // fChain->SetBranchAddress("HLT_PFMET100_PFMHT100_IDTight_CaloBTagDeepCSV_3p1", &HLT_PFMET100_PFMHT100_IDTight_CaloBTagDeepCSV_3p1, &b_HLT_PFMET100_PFMHT100_IDTight_CaloBTagDeepCSV_3p1);
   // fChain->SetBranchStatus("HLT_PFMET110_PFMHT110_IDTight_CaloBTagDeepCSV_3p1", 1);
   // fChain->SetBranchAddress("HLT_PFMET110_PFMHT110_IDTight_CaloBTagDeepCSV_3p1", &HLT_PFMET110_PFMHT110_IDTight_CaloBTagDeepCSV_3p1, &b_HLT_PFMET110_PFMHT110_IDTight_CaloBTagDeepCSV_3p1);
   // fChain->SetBranchStatus("HLT_PFMET120_PFMHT120_IDTight_CaloBTagDeepCSV_3p1", 1);
   // fChain->SetBranchAddress("HLT_PFMET120_PFMHT120_IDTight_CaloBTagDeepCSV_3p1", &HLT_PFMET120_PFMHT120_IDTight_CaloBTagDeepCSV_3p1, &b_HLT_PFMET120_PFMHT120_IDTight_CaloBTagDeepCSV_3p1);
   // fChain->SetBranchStatus("HLT_PFMET130_PFMHT130_IDTight_CaloBTagDeepCSV_3p1", 1);
   // fChain->SetBranchAddress("HLT_PFMET130_PFMHT130_IDTight_CaloBTagDeepCSV_3p1", &HLT_PFMET130_PFMHT130_IDTight_CaloBTagDeepCSV_3p1, &b_HLT_PFMET130_PFMHT130_IDTight_CaloBTagDeepCSV_3p1);
   // fChain->SetBranchStatus("HLT_PFMET140_PFMHT140_IDTight_CaloBTagDeepCSV_3p1", 1);
   // fChain->SetBranchAddress("HLT_PFMET140_PFMHT140_IDTight_CaloBTagDeepCSV_3p1", &HLT_PFMET140_PFMHT140_IDTight_CaloBTagDeepCSV_3p1, &b_HLT_PFMET140_PFMHT140_IDTight_CaloBTagDeepCSV_3p1);
   // fChain->SetBranchStatus("HLT_PFMET120_PFMHT120_IDTight_PFHT60", 1);
   // fChain->SetBranchAddress("HLT_PFMET120_PFMHT120_IDTight_PFHT60", &HLT_PFMET120_PFMHT120_IDTight_PFHT60, &b_HLT_PFMET120_PFMHT120_IDTight_PFHT60);
   // fChain->SetBranchStatus("HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60", 1);
   // fChain->SetBranchAddress("HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60", &HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60, &b_HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60);
   // fChain->SetBranchStatus("HLT_PFMETTypeOne120_PFMHT120_IDTight_PFHT60", 1);
   // fChain->SetBranchAddress("HLT_PFMETTypeOne120_PFMHT120_IDTight_PFHT60", &HLT_PFMETTypeOne120_PFMHT120_IDTight_PFHT60, &b_HLT_PFMETTypeOne120_PFMHT120_IDTight_PFHT60);
   // fChain->SetBranchStatus("HLT_PFMETTypeOne110_PFMHT110_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFMETTypeOne110_PFMHT110_IDTight", &HLT_PFMETTypeOne110_PFMHT110_IDTight, &b_HLT_PFMETTypeOne110_PFMHT110_IDTight);
   // fChain->SetBranchStatus("HLT_PFMETTypeOne120_PFMHT120_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFMETTypeOne120_PFMHT120_IDTight", &HLT_PFMETTypeOne120_PFMHT120_IDTight, &b_HLT_PFMETTypeOne120_PFMHT120_IDTight);
   // fChain->SetBranchStatus("HLT_PFMETTypeOne130_PFMHT130_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFMETTypeOne130_PFMHT130_IDTight", &HLT_PFMETTypeOne130_PFMHT130_IDTight, &b_HLT_PFMETTypeOne130_PFMHT130_IDTight);
   // fChain->SetBranchStatus("HLT_PFMETTypeOne140_PFMHT140_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFMETTypeOne140_PFMHT140_IDTight", &HLT_PFMETTypeOne140_PFMHT140_IDTight, &b_HLT_PFMETTypeOne140_PFMHT140_IDTight);
   // fChain->SetBranchStatus("HLT_PFMETNoMu110_PFMHTNoMu110_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFMETNoMu110_PFMHTNoMu110_IDTight", &HLT_PFMETNoMu110_PFMHTNoMu110_IDTight, &b_HLT_PFMETNoMu110_PFMHTNoMu110_IDTight);
   // fChain->SetBranchStatus("HLT_PFMETNoMu120_PFMHTNoMu120_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFMETNoMu120_PFMHTNoMu120_IDTight", &HLT_PFMETNoMu120_PFMHTNoMu120_IDTight, &b_HLT_PFMETNoMu120_PFMHTNoMu120_IDTight);
   // fChain->SetBranchStatus("HLT_PFMETNoMu130_PFMHTNoMu130_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFMETNoMu130_PFMHTNoMu130_IDTight", &HLT_PFMETNoMu130_PFMHTNoMu130_IDTight, &b_HLT_PFMETNoMu130_PFMHTNoMu130_IDTight);
   // fChain->SetBranchStatus("HLT_PFMETNoMu140_PFMHTNoMu140_IDTight", 1);
   // fChain->SetBranchAddress("HLT_PFMETNoMu140_PFMHTNoMu140_IDTight", &HLT_PFMETNoMu140_PFMHTNoMu140_IDTight, &b_HLT_PFMETNoMu140_PFMHTNoMu140_IDTight);
   // fChain->SetBranchStatus("HLT_MonoCentralPFJet80_PFMETNoMu110_PFMHTNoMu110_IDTight", 1);
   // fChain->SetBranchAddress("HLT_MonoCentralPFJet80_PFMETNoMu110_PFMHTNoMu110_IDTight", &HLT_MonoCentralPFJet80_PFMETNoMu110_PFMHTNoMu110_IDTight, &b_HLT_MonoCentralPFJet80_PFMETNoMu110_PFMHTNoMu110_IDTight);
   // fChain->SetBranchStatus("HLT_MonoCentralPFJet80_PFMETNoMu120_PFMHTNoMu120_IDTight", 1);
   // fChain->SetBranchAddress("HLT_MonoCentralPFJet80_PFMETNoMu120_PFMHTNoMu120_IDTight", &HLT_MonoCentralPFJet80_PFMETNoMu120_PFMHTNoMu120_IDTight, &b_HLT_MonoCentralPFJet80_PFMETNoMu120_PFMHTNoMu120_IDTight);
   // fChain->SetBranchStatus("HLT_MonoCentralPFJet80_PFMETNoMu130_PFMHTNoMu130_IDTight", 1);
   // fChain->SetBranchAddress("HLT_MonoCentralPFJet80_PFMETNoMu130_PFMHTNoMu130_IDTight", &HLT_MonoCentralPFJet80_PFMETNoMu130_PFMHTNoMu130_IDTight, &b_HLT_MonoCentralPFJet80_PFMETNoMu130_PFMHTNoMu130_IDTight);
   // fChain->SetBranchStatus("HLT_MonoCentralPFJet80_PFMETNoMu140_PFMHTNoMu140_IDTight", 1);
   // fChain->SetBranchAddress("HLT_MonoCentralPFJet80_PFMETNoMu140_PFMHTNoMu140_IDTight", &HLT_MonoCentralPFJet80_PFMETNoMu140_PFMHTNoMu140_IDTight, &b_HLT_MonoCentralPFJet80_PFMETNoMu140_PFMHTNoMu140_IDTight);
   // fChain->SetBranchStatus("HLT_L1ETMHadSeeds", 1);
   // fChain->SetBranchAddress("HLT_L1ETMHadSeeds", &HLT_L1ETMHadSeeds, &b_HLT_L1ETMHadSeeds);
   // fChain->SetBranchStatus("HLT_CaloMHT90", 1);
   // fChain->SetBranchAddress("HLT_CaloMHT90", &HLT_CaloMHT90, &b_HLT_CaloMHT90);
   // fChain->SetBranchStatus("HLT_CaloMET80_NotCleaned", 1);
   // fChain->SetBranchAddress("HLT_CaloMET80_NotCleaned", &HLT_CaloMET80_NotCleaned, &b_HLT_CaloMET80_NotCleaned);
   // fChain->SetBranchStatus("HLT_CaloMET90_NotCleaned", 1);
   // fChain->SetBranchAddress("HLT_CaloMET90_NotCleaned", &HLT_CaloMET90_NotCleaned, &b_HLT_CaloMET90_NotCleaned);
   // fChain->SetBranchStatus("HLT_CaloMET100_NotCleaned", 1);
   // fChain->SetBranchAddress("HLT_CaloMET100_NotCleaned", &HLT_CaloMET100_NotCleaned, &b_HLT_CaloMET100_NotCleaned);
   // fChain->SetBranchStatus("HLT_CaloMET110_NotCleaned", 1);
   // fChain->SetBranchAddress("HLT_CaloMET110_NotCleaned", &HLT_CaloMET110_NotCleaned, &b_HLT_CaloMET110_NotCleaned);
   // fChain->SetBranchStatus("HLT_CaloMET250_NotCleaned", 1);
   // fChain->SetBranchAddress("HLT_CaloMET250_NotCleaned", &HLT_CaloMET250_NotCleaned, &b_HLT_CaloMET250_NotCleaned);
   // fChain->SetBranchStatus("HLT_CaloMET300_NotCleaned", 1);
   // fChain->SetBranchAddress("HLT_CaloMET300_NotCleaned", &HLT_CaloMET300_NotCleaned, &b_HLT_CaloMET300_NotCleaned);
   // fChain->SetBranchStatus("HLT_CaloMET350_NotCleaned", 1);
   // fChain->SetBranchAddress("HLT_CaloMET350_NotCleaned", &HLT_CaloMET350_NotCleaned, &b_HLT_CaloMET350_NotCleaned);
   // fChain->SetBranchStatus("HLT_PFMET200_NotCleaned", 1);
   // fChain->SetBranchAddress("HLT_PFMET200_NotCleaned", &HLT_PFMET200_NotCleaned, &b_HLT_PFMET200_NotCleaned);
   // fChain->SetBranchStatus("HLT_PFMET250_NotCleaned", 1);
   // fChain->SetBranchAddress("HLT_PFMET250_NotCleaned", &HLT_PFMET250_NotCleaned, &b_HLT_PFMET250_NotCleaned);
   // fChain->SetBranchStatus("HLT_PFMET300_NotCleaned", 1);
   // fChain->SetBranchAddress("HLT_PFMET300_NotCleaned", &HLT_PFMET300_NotCleaned, &b_HLT_PFMET300_NotCleaned);
   // fChain->SetBranchStatus("HLT_PFMET200_BeamHaloCleaned", 1);
   // fChain->SetBranchAddress("HLT_PFMET200_BeamHaloCleaned", &HLT_PFMET200_BeamHaloCleaned, &b_HLT_PFMET200_BeamHaloCleaned);
   // fChain->SetBranchStatus("HLT_PFMETTypeOne200_BeamHaloCleaned", 1);
   // fChain->SetBranchAddress("HLT_PFMETTypeOne200_BeamHaloCleaned", &HLT_PFMETTypeOne200_BeamHaloCleaned, &b_HLT_PFMETTypeOne200_BeamHaloCleaned);
   // fChain->SetBranchStatus("HLT_MET105_IsoTrk50", 1);
   // fChain->SetBranchAddress("HLT_MET105_IsoTrk50", &HLT_MET105_IsoTrk50, &b_HLT_MET105_IsoTrk50);
   // fChain->SetBranchStatus("HLT_MET120_IsoTrk50", 1);
   // fChain->SetBranchAddress("HLT_MET120_IsoTrk50", &HLT_MET120_IsoTrk50, &b_HLT_MET120_IsoTrk50);
   // fChain->SetBranchStatus("HLT_SingleJet30_Mu12_SinglePFJet40", 1);
   // fChain->SetBranchAddress("HLT_SingleJet30_Mu12_SinglePFJet40", &HLT_SingleJet30_Mu12_SinglePFJet40, &b_HLT_SingleJet30_Mu12_SinglePFJet40);
   // fChain->SetBranchStatus("HLT_Mu12eta2p3", 1);
   // fChain->SetBranchAddress("HLT_Mu12eta2p3", &HLT_Mu12eta2p3, &b_HLT_Mu12eta2p3);
   // fChain->SetBranchStatus("HLT_Mu12eta2p3_PFJet40", 1);
   // fChain->SetBranchAddress("HLT_Mu12eta2p3_PFJet40", &HLT_Mu12eta2p3_PFJet40, &b_HLT_Mu12eta2p3_PFJet40);
   // fChain->SetBranchStatus("HLT_Mu12_DoublePFJets40_PFBTagDeepCSV_p71", 1);
   // fChain->SetBranchAddress("HLT_Mu12_DoublePFJets40_PFBTagDeepCSV_p71", &HLT_Mu12_DoublePFJets40_PFBTagDeepCSV_p71, &b_HLT_Mu12_DoublePFJets40_PFBTagDeepCSV_p71);
   // fChain->SetBranchStatus("HLT_Mu12_DoublePFJets100_PFBTagDeepCSV_p71", 1);
   // fChain->SetBranchAddress("HLT_Mu12_DoublePFJets100_PFBTagDeepCSV_p71", &HLT_Mu12_DoublePFJets100_PFBTagDeepCSV_p71, &b_HLT_Mu12_DoublePFJets100_PFBTagDeepCSV_p71);
   // fChain->SetBranchStatus("HLT_Mu12_DoublePFJets200_PFBTagDeepCSV_p71", 1);
   // fChain->SetBranchAddress("HLT_Mu12_DoublePFJets200_PFBTagDeepCSV_p71", &HLT_Mu12_DoublePFJets200_PFBTagDeepCSV_p71, &b_HLT_Mu12_DoublePFJets200_PFBTagDeepCSV_p71);
   // fChain->SetBranchStatus("HLT_Mu12_DoublePFJets350_PFBTagDeepCSV_p71", 1);
   // fChain->SetBranchAddress("HLT_Mu12_DoublePFJets350_PFBTagDeepCSV_p71", &HLT_Mu12_DoublePFJets350_PFBTagDeepCSV_p71, &b_HLT_Mu12_DoublePFJets350_PFBTagDeepCSV_p71);
   // fChain->SetBranchStatus("HLT_Mu12_DoublePFJets40MaxDeta1p6_DoublePFBTagDeepCSV_p71", 1);
   // fChain->SetBranchAddress("HLT_Mu12_DoublePFJets40MaxDeta1p6_DoublePFBTagDeepCSV_p71", &HLT_Mu12_DoublePFJets40MaxDeta1p6_DoublePFBTagDeepCSV_p71, &b_HLT_Mu12_DoublePFJets40MaxDeta1p6_DoublePFBTagDeepCSV_p71);
   // fChain->SetBranchStatus("HLT_Mu12_DoublePFJets54MaxDeta1p6_DoublePFBTagDeepCSV_p71", 1);
   // fChain->SetBranchAddress("HLT_Mu12_DoublePFJets54MaxDeta1p6_DoublePFBTagDeepCSV_p71", &HLT_Mu12_DoublePFJets54MaxDeta1p6_DoublePFBTagDeepCSV_p71, &b_HLT_Mu12_DoublePFJets54MaxDeta1p6_DoublePFBTagDeepCSV_p71);
   // fChain->SetBranchStatus("HLT_DoublePFJets40_PFBTagDeepCSV_p71", 1);
   // fChain->SetBranchAddress("HLT_DoublePFJets40_PFBTagDeepCSV_p71", &HLT_DoublePFJets40_PFBTagDeepCSV_p71, &b_HLT_DoublePFJets40_PFBTagDeepCSV_p71);
   // fChain->SetBranchStatus("HLT_DoublePFJets100_PFBTagDeepCSV_p71", 1);
   // fChain->SetBranchAddress("HLT_DoublePFJets100_PFBTagDeepCSV_p71", &HLT_DoublePFJets100_PFBTagDeepCSV_p71, &b_HLT_DoublePFJets100_PFBTagDeepCSV_p71);
   // fChain->SetBranchStatus("HLT_DoublePFJets200_PFBTagDeepCSV_p71", 1);
   // fChain->SetBranchAddress("HLT_DoublePFJets200_PFBTagDeepCSV_p71", &HLT_DoublePFJets200_PFBTagDeepCSV_p71, &b_HLT_DoublePFJets200_PFBTagDeepCSV_p71);
   // fChain->SetBranchStatus("HLT_DoublePFJets350_PFBTagDeepCSV_p71", 1);
   // fChain->SetBranchAddress("HLT_DoublePFJets350_PFBTagDeepCSV_p71", &HLT_DoublePFJets350_PFBTagDeepCSV_p71, &b_HLT_DoublePFJets350_PFBTagDeepCSV_p71);
   // fChain->SetBranchStatus("HLT_DoublePFJets116MaxDeta1p6_DoublePFBTagDeepCSV_p71", 1);
   // fChain->SetBranchAddress("HLT_DoublePFJets116MaxDeta1p6_DoublePFBTagDeepCSV_p71", &HLT_DoublePFJets116MaxDeta1p6_DoublePFBTagDeepCSV_p71, &b_HLT_DoublePFJets116MaxDeta1p6_DoublePFBTagDeepCSV_p71);
   // fChain->SetBranchStatus("HLT_DoublePFJets128MaxDeta1p6_DoublePFBTagDeepCSV_p71", 1);
   // fChain->SetBranchAddress("HLT_DoublePFJets128MaxDeta1p6_DoublePFBTagDeepCSV_p71", &HLT_DoublePFJets128MaxDeta1p6_DoublePFBTagDeepCSV_p71, &b_HLT_DoublePFJets128MaxDeta1p6_DoublePFBTagDeepCSV_p71);
   // fChain->SetBranchStatus("HLT_Mu12_DoublePFJets40_PFBTagDeepJet_p71", 1);
   // fChain->SetBranchAddress("HLT_Mu12_DoublePFJets40_PFBTagDeepJet_p71", &HLT_Mu12_DoublePFJets40_PFBTagDeepJet_p71, &b_HLT_Mu12_DoublePFJets40_PFBTagDeepJet_p71);
   // fChain->SetBranchStatus("HLT_Mu12_DoublePFJets100_PFBTagDeepJet_p71", 1);
   // fChain->SetBranchAddress("HLT_Mu12_DoublePFJets100_PFBTagDeepJet_p71", &HLT_Mu12_DoublePFJets100_PFBTagDeepJet_p71, &b_HLT_Mu12_DoublePFJets100_PFBTagDeepJet_p71);
   // fChain->SetBranchStatus("HLT_Mu12_DoublePFJets200_PFBTagDeepJet_p71", 1);
   // fChain->SetBranchAddress("HLT_Mu12_DoublePFJets200_PFBTagDeepJet_p71", &HLT_Mu12_DoublePFJets200_PFBTagDeepJet_p71, &b_HLT_Mu12_DoublePFJets200_PFBTagDeepJet_p71);
   // fChain->SetBranchStatus("HLT_Mu12_DoublePFJets350_PFBTagDeepJet_p71", 1);
   // fChain->SetBranchAddress("HLT_Mu12_DoublePFJets350_PFBTagDeepJet_p71", &HLT_Mu12_DoublePFJets350_PFBTagDeepJet_p71, &b_HLT_Mu12_DoublePFJets350_PFBTagDeepJet_p71);
   // fChain->SetBranchStatus("HLT_Mu12_DoublePFJets40MaxDeta1p6_DoublePFBTagDeepJet_p71", 1);
   // fChain->SetBranchAddress("HLT_Mu12_DoublePFJets40MaxDeta1p6_DoublePFBTagDeepJet_p71", &HLT_Mu12_DoublePFJets40MaxDeta1p6_DoublePFBTagDeepJet_p71, &b_HLT_Mu12_DoublePFJets40MaxDeta1p6_DoublePFBTagDeepJet_p71);
   // fChain->SetBranchStatus("HLT_Mu12_DoublePFJets54MaxDeta1p6_DoublePFBTagDeepJet_p71", 1);
   // fChain->SetBranchAddress("HLT_Mu12_DoublePFJets54MaxDeta1p6_DoublePFBTagDeepJet_p71", &HLT_Mu12_DoublePFJets54MaxDeta1p6_DoublePFBTagDeepJet_p71, &b_HLT_Mu12_DoublePFJets54MaxDeta1p6_DoublePFBTagDeepJet_p71);
   // fChain->SetBranchStatus("HLT_DoublePFJets40_PFBTagDeepJet_p71", 1);
   // fChain->SetBranchAddress("HLT_DoublePFJets40_PFBTagDeepJet_p71", &HLT_DoublePFJets40_PFBTagDeepJet_p71, &b_HLT_DoublePFJets40_PFBTagDeepJet_p71);
   // fChain->SetBranchStatus("HLT_DoublePFJets100_PFBTagDeepJet_p71", 1);
   // fChain->SetBranchAddress("HLT_DoublePFJets100_PFBTagDeepJet_p71", &HLT_DoublePFJets100_PFBTagDeepJet_p71, &b_HLT_DoublePFJets100_PFBTagDeepJet_p71);
   // fChain->SetBranchStatus("HLT_DoublePFJets200_PFBTagDeepJet_p71", 1);
   // fChain->SetBranchAddress("HLT_DoublePFJets200_PFBTagDeepJet_p71", &HLT_DoublePFJets200_PFBTagDeepJet_p71, &b_HLT_DoublePFJets200_PFBTagDeepJet_p71);
   // fChain->SetBranchStatus("HLT_DoublePFJets350_PFBTagDeepJet_p71", 1);
   // fChain->SetBranchAddress("HLT_DoublePFJets350_PFBTagDeepJet_p71", &HLT_DoublePFJets350_PFBTagDeepJet_p71, &b_HLT_DoublePFJets350_PFBTagDeepJet_p71);
   // fChain->SetBranchStatus("HLT_DoublePFJets116MaxDeta1p6_DoublePFBTagDeepJet_p71", 1);
   // fChain->SetBranchAddress("HLT_DoublePFJets116MaxDeta1p6_DoublePFBTagDeepJet_p71", &HLT_DoublePFJets116MaxDeta1p6_DoublePFBTagDeepJet_p71, &b_HLT_DoublePFJets116MaxDeta1p6_DoublePFBTagDeepJet_p71);
   // fChain->SetBranchStatus("HLT_DoublePFJets128MaxDeta1p6_DoublePFBTagDeepJet_p71", 1);
   // fChain->SetBranchAddress("HLT_DoublePFJets128MaxDeta1p6_DoublePFBTagDeepJet_p71", &HLT_DoublePFJets128MaxDeta1p6_DoublePFBTagDeepJet_p71, &b_HLT_DoublePFJets128MaxDeta1p6_DoublePFBTagDeepJet_p71);
   // fChain->SetBranchStatus("HLT_Photon300_NoHE", 1);
   // fChain->SetBranchAddress("HLT_Photon300_NoHE", &HLT_Photon300_NoHE, &b_HLT_Photon300_NoHE);
   // fChain->SetBranchStatus("HLT_Mu8_TrkIsoVVL", 1);
   // fChain->SetBranchAddress("HLT_Mu8_TrkIsoVVL", &HLT_Mu8_TrkIsoVVL, &b_HLT_Mu8_TrkIsoVVL);
   // fChain->SetBranchStatus("HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ", 1);
   // fChain->SetBranchAddress("HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ", &HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ, &b_HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ);
   // fChain->SetBranchStatus("HLT_Mu8_DiEle12_CaloIdL_TrackIdL", 1);
   // fChain->SetBranchAddress("HLT_Mu8_DiEle12_CaloIdL_TrackIdL", &HLT_Mu8_DiEle12_CaloIdL_TrackIdL, &b_HLT_Mu8_DiEle12_CaloIdL_TrackIdL);
   // fChain->SetBranchStatus("HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350_DZ", 1);
   // fChain->SetBranchAddress("HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350_DZ", &HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350_DZ, &b_HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350_DZ);
   // fChain->SetBranchStatus("HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350", 1);
   // fChain->SetBranchAddress("HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350", &HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350, &b_HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350);
   // fChain->SetBranchStatus("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", 1);
   // fChain->SetBranchAddress("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", &HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ, &b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ);
   // fChain->SetBranchStatus("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30", 1);
   // fChain->SetBranchAddress("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30", &HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30, &b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30);
   // fChain->SetBranchStatus("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_CaloDiJet30", 1);
   // fChain->SetBranchAddress("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_CaloDiJet30", &HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_CaloDiJet30, &b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_CaloDiJet30);
   // fChain->SetBranchStatus("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30_PFBtagDeepCSV_1p5", 1);
   // fChain->SetBranchAddress("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30_PFBtagDeepCSV_1p5", &HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30_PFBtagDeepCSV_1p5, &b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30_PFBtagDeepCSV_1p5);
   // fChain->SetBranchStatus("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_CaloDiJet30_CaloBtagDeepCSV_1p5", 1);
   // fChain->SetBranchAddress("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_CaloDiJet30_CaloBtagDeepCSV_1p5", &HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_CaloDiJet30_CaloBtagDeepCSV_1p5, &b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_CaloDiJet30_CaloBtagDeepCSV_1p5);
   // fChain->SetBranchStatus("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL", 1);
   // fChain->SetBranchAddress("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL", &HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL, &b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL);
   // fChain->SetBranchStatus("HLT_Mu17_TrkIsoVVL", 1);
   // fChain->SetBranchAddress("HLT_Mu17_TrkIsoVVL", &HLT_Mu17_TrkIsoVVL, &b_HLT_Mu17_TrkIsoVVL);
   // fChain->SetBranchStatus("HLT_Mu19_TrkIsoVVL", 1);
   // fChain->SetBranchAddress("HLT_Mu19_TrkIsoVVL", &HLT_Mu19_TrkIsoVVL, &b_HLT_Mu19_TrkIsoVVL);
   // fChain->SetBranchStatus("HLT_BTagMu_AK4DiJet20_Mu5", 1);
   // fChain->SetBranchAddress("HLT_BTagMu_AK4DiJet20_Mu5", &HLT_BTagMu_AK4DiJet20_Mu5, &b_HLT_BTagMu_AK4DiJet20_Mu5);
   // fChain->SetBranchStatus("HLT_BTagMu_AK4DiJet40_Mu5", 1);
   // fChain->SetBranchAddress("HLT_BTagMu_AK4DiJet40_Mu5", &HLT_BTagMu_AK4DiJet40_Mu5, &b_HLT_BTagMu_AK4DiJet40_Mu5);
   // fChain->SetBranchStatus("HLT_BTagMu_AK4DiJet70_Mu5", 1);
   // fChain->SetBranchAddress("HLT_BTagMu_AK4DiJet70_Mu5", &HLT_BTagMu_AK4DiJet70_Mu5, &b_HLT_BTagMu_AK4DiJet70_Mu5);
   // fChain->SetBranchStatus("HLT_BTagMu_AK4DiJet110_Mu5", 1);
   // fChain->SetBranchAddress("HLT_BTagMu_AK4DiJet110_Mu5", &HLT_BTagMu_AK4DiJet110_Mu5, &b_HLT_BTagMu_AK4DiJet110_Mu5);
   // fChain->SetBranchStatus("HLT_BTagMu_AK4DiJet170_Mu5", 1);
   // fChain->SetBranchAddress("HLT_BTagMu_AK4DiJet170_Mu5", &HLT_BTagMu_AK4DiJet170_Mu5, &b_HLT_BTagMu_AK4DiJet170_Mu5);
   // fChain->SetBranchStatus("HLT_BTagMu_AK4Jet300_Mu5", 1);
   // fChain->SetBranchAddress("HLT_BTagMu_AK4Jet300_Mu5", &HLT_BTagMu_AK4Jet300_Mu5, &b_HLT_BTagMu_AK4Jet300_Mu5);
   // fChain->SetBranchStatus("HLT_BTagMu_AK8DiJet170_Mu5", 1);
   // fChain->SetBranchAddress("HLT_BTagMu_AK8DiJet170_Mu5", &HLT_BTagMu_AK8DiJet170_Mu5, &b_HLT_BTagMu_AK8DiJet170_Mu5);
   // fChain->SetBranchStatus("HLT_BTagMu_AK8Jet170_DoubleMu5", 1);
   // fChain->SetBranchAddress("HLT_BTagMu_AK8Jet170_DoubleMu5", &HLT_BTagMu_AK8Jet170_DoubleMu5, &b_HLT_BTagMu_AK8Jet170_DoubleMu5);
   // fChain->SetBranchStatus("HLT_BTagMu_AK8Jet300_Mu5", 1);
   // fChain->SetBranchAddress("HLT_BTagMu_AK8Jet300_Mu5", &HLT_BTagMu_AK8Jet300_Mu5, &b_HLT_BTagMu_AK8Jet300_Mu5);
   // fChain->SetBranchStatus("HLT_Ele15_Ele8_CaloIdL_TrackIdL_IsoVL", 1);
   // fChain->SetBranchAddress("HLT_Ele15_Ele8_CaloIdL_TrackIdL_IsoVL", &HLT_Ele15_Ele8_CaloIdL_TrackIdL_IsoVL, &b_HLT_Ele15_Ele8_CaloIdL_TrackIdL_IsoVL);
   // fChain->SetBranchStatus("HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", 1);
   // fChain->SetBranchAddress("HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", &HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, &b_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ);
   // fChain->SetBranchStatus("HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", 1);
   // fChain->SetBranchAddress("HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", &HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL, &b_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL);
   // fChain->SetBranchStatus("HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", 1);
   // fChain->SetBranchAddress("HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", &HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, &b_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ);
   // fChain->SetBranchStatus("HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL", 1);
   // fChain->SetBranchAddress("HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL", &HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL, &b_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL);
   // fChain->SetBranchStatus("HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL", 1);
   // fChain->SetBranchAddress("HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL", &HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL, &b_HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL);
   // fChain->SetBranchStatus("HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", 1);
   // fChain->SetBranchAddress("HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", &HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ, &b_HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ);
   // fChain->SetBranchStatus("HLT_Mu12_DoublePhoton20", 1);
   // fChain->SetBranchAddress("HLT_Mu12_DoublePhoton20", &HLT_Mu12_DoublePhoton20, &b_HLT_Mu12_DoublePhoton20);
   // fChain->SetBranchStatus("HLT_Photon20", 1);
   // fChain->SetBranchAddress("HLT_Photon20", &HLT_Photon20, &b_HLT_Photon20);
   // fChain->SetBranchStatus("HLT_Photon33", 1);
   // fChain->SetBranchAddress("HLT_Photon33", &HLT_Photon33, &b_HLT_Photon33);
   // fChain->SetBranchStatus("HLT_Photon50", 1);
   // fChain->SetBranchAddress("HLT_Photon50", &HLT_Photon50, &b_HLT_Photon50);
   // fChain->SetBranchStatus("HLT_Photon75", 1);
   // fChain->SetBranchAddress("HLT_Photon75", &HLT_Photon75, &b_HLT_Photon75);
   // fChain->SetBranchStatus("HLT_Photon90", 1);
   // fChain->SetBranchAddress("HLT_Photon90", &HLT_Photon90, &b_HLT_Photon90);
   // fChain->SetBranchStatus("HLT_Photon120", 1);
   // fChain->SetBranchAddress("HLT_Photon120", &HLT_Photon120, &b_HLT_Photon120);
   // fChain->SetBranchStatus("HLT_Photon150", 1);
   // fChain->SetBranchAddress("HLT_Photon150", &HLT_Photon150, &b_HLT_Photon150);
   // fChain->SetBranchStatus("HLT_Photon175", 1);
   // fChain->SetBranchAddress("HLT_Photon175", &HLT_Photon175, &b_HLT_Photon175);
   // fChain->SetBranchStatus("HLT_Photon200", 1);
   // fChain->SetBranchAddress("HLT_Photon200", &HLT_Photon200, &b_HLT_Photon200);
   // fChain->SetBranchStatus("HLT_Photon100EB_TightID_TightIso", 1);
   // fChain->SetBranchAddress("HLT_Photon100EB_TightID_TightIso", &HLT_Photon100EB_TightID_TightIso, &b_HLT_Photon100EB_TightID_TightIso);
   // fChain->SetBranchStatus("HLT_Photon110EB_TightID_TightIso", 1);
   // fChain->SetBranchAddress("HLT_Photon110EB_TightID_TightIso", &HLT_Photon110EB_TightID_TightIso, &b_HLT_Photon110EB_TightID_TightIso);
   // fChain->SetBranchStatus("HLT_Photon120EB_TightID_TightIso", 1);
   // fChain->SetBranchAddress("HLT_Photon120EB_TightID_TightIso", &HLT_Photon120EB_TightID_TightIso, &b_HLT_Photon120EB_TightID_TightIso);
   // fChain->SetBranchStatus("HLT_Photon100EBHE10", 1);
   // fChain->SetBranchAddress("HLT_Photon100EBHE10", &HLT_Photon100EBHE10, &b_HLT_Photon100EBHE10);
   // fChain->SetBranchStatus("HLT_Photon100EEHE10", 1);
   // fChain->SetBranchAddress("HLT_Photon100EEHE10", &HLT_Photon100EEHE10, &b_HLT_Photon100EEHE10);
   // fChain->SetBranchStatus("HLT_Photon100EE_TightID_TightIso", 1);
   // fChain->SetBranchAddress("HLT_Photon100EE_TightID_TightIso", &HLT_Photon100EE_TightID_TightIso, &b_HLT_Photon100EE_TightID_TightIso);
   // fChain->SetBranchStatus("HLT_Photon50_R9Id90_HE10_IsoM", 1);
   // fChain->SetBranchAddress("HLT_Photon50_R9Id90_HE10_IsoM", &HLT_Photon50_R9Id90_HE10_IsoM, &b_HLT_Photon50_R9Id90_HE10_IsoM);
   // fChain->SetBranchStatus("HLT_Photon75_R9Id90_HE10_IsoM", 1);
   // fChain->SetBranchAddress("HLT_Photon75_R9Id90_HE10_IsoM", &HLT_Photon75_R9Id90_HE10_IsoM, &b_HLT_Photon75_R9Id90_HE10_IsoM);
   // fChain->SetBranchStatus("HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ300_PFJetsMJJ400DEta3", 1);
   // fChain->SetBranchAddress("HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ300_PFJetsMJJ400DEta3", &HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ300_PFJetsMJJ400DEta3, &b_HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ300_PFJetsMJJ400DEta3);
   // fChain->SetBranchStatus("HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ400_PFJetsMJJ600DEta3", 1);
   // fChain->SetBranchAddress("HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ400_PFJetsMJJ600DEta3", &HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ400_PFJetsMJJ600DEta3, &b_HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ400_PFJetsMJJ600DEta3);
   // fChain->SetBranchStatus("HLT_Photon90_R9Id90_HE10_IsoM", 1);
   // fChain->SetBranchAddress("HLT_Photon90_R9Id90_HE10_IsoM", &HLT_Photon90_R9Id90_HE10_IsoM, &b_HLT_Photon90_R9Id90_HE10_IsoM);
   // fChain->SetBranchStatus("HLT_Photon120_R9Id90_HE10_IsoM", 1);
   // fChain->SetBranchAddress("HLT_Photon120_R9Id90_HE10_IsoM", &HLT_Photon120_R9Id90_HE10_IsoM, &b_HLT_Photon120_R9Id90_HE10_IsoM);
   // fChain->SetBranchStatus("HLT_Photon165_R9Id90_HE10_IsoM", 1);
   // fChain->SetBranchAddress("HLT_Photon165_R9Id90_HE10_IsoM", &HLT_Photon165_R9Id90_HE10_IsoM, &b_HLT_Photon165_R9Id90_HE10_IsoM);
   // fChain->SetBranchStatus("HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90", 1);
   // fChain->SetBranchAddress("HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90", &HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90, &b_HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90);
   // fChain->SetBranchStatus("HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass95", 1);
   // fChain->SetBranchAddress("HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass95", &HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass95, &b_HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass95);
   // fChain->SetBranchStatus("HLT_Photon35_TwoProngs35", 1);
   // fChain->SetBranchAddress("HLT_Photon35_TwoProngs35", &HLT_Photon35_TwoProngs35, &b_HLT_Photon35_TwoProngs35);
   // fChain->SetBranchStatus("HLT_IsoMu24_TwoProngs35", 1);
   // fChain->SetBranchAddress("HLT_IsoMu24_TwoProngs35", &HLT_IsoMu24_TwoProngs35, &b_HLT_IsoMu24_TwoProngs35);
   // fChain->SetBranchStatus("HLT_Dimuon0_Jpsi_L1_NoOS", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Jpsi_L1_NoOS", &HLT_Dimuon0_Jpsi_L1_NoOS, &b_HLT_Dimuon0_Jpsi_L1_NoOS);
   // fChain->SetBranchStatus("HLT_Dimuon0_Jpsi_NoVertexing_NoOS", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Jpsi_NoVertexing_NoOS", &HLT_Dimuon0_Jpsi_NoVertexing_NoOS, &b_HLT_Dimuon0_Jpsi_NoVertexing_NoOS);
   // fChain->SetBranchStatus("HLT_Dimuon0_Jpsi", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Jpsi", &HLT_Dimuon0_Jpsi, &b_HLT_Dimuon0_Jpsi);
   // fChain->SetBranchStatus("HLT_Dimuon0_Jpsi_NoVertexing", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Jpsi_NoVertexing", &HLT_Dimuon0_Jpsi_NoVertexing, &b_HLT_Dimuon0_Jpsi_NoVertexing);
   // fChain->SetBranchStatus("HLT_Dimuon0_Jpsi_L1_4R_0er1p5R", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Jpsi_L1_4R_0er1p5R", &HLT_Dimuon0_Jpsi_L1_4R_0er1p5R, &b_HLT_Dimuon0_Jpsi_L1_4R_0er1p5R);
   // fChain->SetBranchStatus("HLT_Dimuon0_Jpsi_NoVertexing_L1_4R_0er1p5R", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Jpsi_NoVertexing_L1_4R_0er1p5R", &HLT_Dimuon0_Jpsi_NoVertexing_L1_4R_0er1p5R, &b_HLT_Dimuon0_Jpsi_NoVertexing_L1_4R_0er1p5R);
   // fChain->SetBranchStatus("HLT_Dimuon0_Jpsi3p5_Muon2", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Jpsi3p5_Muon2", &HLT_Dimuon0_Jpsi3p5_Muon2, &b_HLT_Dimuon0_Jpsi3p5_Muon2);
   // fChain->SetBranchStatus("HLT_Dimuon0_Upsilon_L1_4p5", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Upsilon_L1_4p5", &HLT_Dimuon0_Upsilon_L1_4p5, &b_HLT_Dimuon0_Upsilon_L1_4p5);
   // fChain->SetBranchStatus("HLT_Dimuon0_Upsilon_L1_5", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Upsilon_L1_5", &HLT_Dimuon0_Upsilon_L1_5, &b_HLT_Dimuon0_Upsilon_L1_5);
   // fChain->SetBranchStatus("HLT_Dimuon0_Upsilon_L1_4p5NoOS", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Upsilon_L1_4p5NoOS", &HLT_Dimuon0_Upsilon_L1_4p5NoOS, &b_HLT_Dimuon0_Upsilon_L1_4p5NoOS);
   // fChain->SetBranchStatus("HLT_Dimuon0_Upsilon_L1_4p5er2p0", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Upsilon_L1_4p5er2p0", &HLT_Dimuon0_Upsilon_L1_4p5er2p0, &b_HLT_Dimuon0_Upsilon_L1_4p5er2p0);
   // fChain->SetBranchStatus("HLT_Dimuon0_Upsilon_L1_4p5er2p0M", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Upsilon_L1_4p5er2p0M", &HLT_Dimuon0_Upsilon_L1_4p5er2p0M, &b_HLT_Dimuon0_Upsilon_L1_4p5er2p0M);
   // fChain->SetBranchStatus("HLT_Dimuon0_Upsilon_NoVertexing", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Upsilon_NoVertexing", &HLT_Dimuon0_Upsilon_NoVertexing, &b_HLT_Dimuon0_Upsilon_NoVertexing);
   // fChain->SetBranchStatus("HLT_Dimuon0_Upsilon_L1_5M", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Upsilon_L1_5M", &HLT_Dimuon0_Upsilon_L1_5M, &b_HLT_Dimuon0_Upsilon_L1_5M);
   // fChain->SetBranchStatus("HLT_Dimuon0_LowMass_L1_0er1p5R", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_LowMass_L1_0er1p5R", &HLT_Dimuon0_LowMass_L1_0er1p5R, &b_HLT_Dimuon0_LowMass_L1_0er1p5R);
   // fChain->SetBranchStatus("HLT_Dimuon0_LowMass_L1_0er1p5", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_LowMass_L1_0er1p5", &HLT_Dimuon0_LowMass_L1_0er1p5, &b_HLT_Dimuon0_LowMass_L1_0er1p5);
   // fChain->SetBranchStatus("HLT_Dimuon0_LowMass", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_LowMass", &HLT_Dimuon0_LowMass, &b_HLT_Dimuon0_LowMass);
   // fChain->SetBranchStatus("HLT_Dimuon0_LowMass_L1_4", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_LowMass_L1_4", &HLT_Dimuon0_LowMass_L1_4, &b_HLT_Dimuon0_LowMass_L1_4);
   // fChain->SetBranchStatus("HLT_Dimuon0_LowMass_L1_4R", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_LowMass_L1_4R", &HLT_Dimuon0_LowMass_L1_4R, &b_HLT_Dimuon0_LowMass_L1_4R);
   // fChain->SetBranchStatus("HLT_Dimuon0_LowMass_L1_TM530", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_LowMass_L1_TM530", &HLT_Dimuon0_LowMass_L1_TM530, &b_HLT_Dimuon0_LowMass_L1_TM530);
   // fChain->SetBranchStatus("HLT_Dimuon0_Upsilon_Muon_L1_TM0", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Upsilon_Muon_L1_TM0", &HLT_Dimuon0_Upsilon_Muon_L1_TM0, &b_HLT_Dimuon0_Upsilon_Muon_L1_TM0);
   // fChain->SetBranchStatus("HLT_Dimuon0_Upsilon_Muon_NoL1Mass", 1);
   // fChain->SetBranchAddress("HLT_Dimuon0_Upsilon_Muon_NoL1Mass", &HLT_Dimuon0_Upsilon_Muon_NoL1Mass, &b_HLT_Dimuon0_Upsilon_Muon_NoL1Mass);
   // fChain->SetBranchStatus("HLT_TripleMu_5_3_3_Mass3p8_DZ", 1);
   // fChain->SetBranchAddress("HLT_TripleMu_5_3_3_Mass3p8_DZ", &HLT_TripleMu_5_3_3_Mass3p8_DZ, &b_HLT_TripleMu_5_3_3_Mass3p8_DZ);
   // fChain->SetBranchStatus("HLT_TripleMu_10_5_5_DZ", 1);
   // fChain->SetBranchAddress("HLT_TripleMu_10_5_5_DZ", &HLT_TripleMu_10_5_5_DZ, &b_HLT_TripleMu_10_5_5_DZ);
   // fChain->SetBranchStatus("HLT_TripleMu_12_10_5", 1);
   // fChain->SetBranchAddress("HLT_TripleMu_12_10_5", &HLT_TripleMu_12_10_5, &b_HLT_TripleMu_12_10_5);
   // fChain->SetBranchStatus("HLT_Tau3Mu_Mu7_Mu1_TkMu1_Tau15", 1);
   // fChain->SetBranchAddress("HLT_Tau3Mu_Mu7_Mu1_TkMu1_Tau15", &HLT_Tau3Mu_Mu7_Mu1_TkMu1_Tau15, &b_HLT_Tau3Mu_Mu7_Mu1_TkMu1_Tau15);
   // fChain->SetBranchStatus("HLT_Tau3Mu_Mu7_Mu1_TkMu1_Tau15_Charge1", 1);
   // fChain->SetBranchAddress("HLT_Tau3Mu_Mu7_Mu1_TkMu1_Tau15_Charge1", &HLT_Tau3Mu_Mu7_Mu1_TkMu1_Tau15_Charge1, &b_HLT_Tau3Mu_Mu7_Mu1_TkMu1_Tau15_Charge1);
   // fChain->SetBranchStatus("HLT_Tau3Mu_Mu7_Mu1_TkMu1_IsoTau15", 1);
   // fChain->SetBranchAddress("HLT_Tau3Mu_Mu7_Mu1_TkMu1_IsoTau15", &HLT_Tau3Mu_Mu7_Mu1_TkMu1_IsoTau15, &b_HLT_Tau3Mu_Mu7_Mu1_TkMu1_IsoTau15);
   // fChain->SetBranchStatus("HLT_Tau3Mu_Mu7_Mu1_TkMu1_IsoTau15_Charge1", 1);
   // fChain->SetBranchAddress("HLT_Tau3Mu_Mu7_Mu1_TkMu1_IsoTau15_Charge1", &HLT_Tau3Mu_Mu7_Mu1_TkMu1_IsoTau15_Charge1, &b_HLT_Tau3Mu_Mu7_Mu1_TkMu1_IsoTau15_Charge1);
   // fChain->SetBranchStatus("HLT_DoubleMu3_DZ_PFMET50_PFMHT60", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu3_DZ_PFMET50_PFMHT60", &HLT_DoubleMu3_DZ_PFMET50_PFMHT60, &b_HLT_DoubleMu3_DZ_PFMET50_PFMHT60);
   // fChain->SetBranchStatus("HLT_DoubleMu3_DZ_PFMET70_PFMHT70", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu3_DZ_PFMET70_PFMHT70", &HLT_DoubleMu3_DZ_PFMET70_PFMHT70, &b_HLT_DoubleMu3_DZ_PFMET70_PFMHT70);
   // fChain->SetBranchStatus("HLT_DoubleMu3_DZ_PFMET90_PFMHT90", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu3_DZ_PFMET90_PFMHT90", &HLT_DoubleMu3_DZ_PFMET90_PFMHT90, &b_HLT_DoubleMu3_DZ_PFMET90_PFMHT90);
   // fChain->SetBranchStatus("HLT_DoubleMu3_Trk_Tau3mu_NoL1Mass", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu3_Trk_Tau3mu_NoL1Mass", &HLT_DoubleMu3_Trk_Tau3mu_NoL1Mass, &b_HLT_DoubleMu3_Trk_Tau3mu_NoL1Mass);
   // fChain->SetBranchStatus("HLT_DoubleMu4_Jpsi_Displaced", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu4_Jpsi_Displaced", &HLT_DoubleMu4_Jpsi_Displaced, &b_HLT_DoubleMu4_Jpsi_Displaced);
   // fChain->SetBranchStatus("HLT_DoubleMu4_Jpsi_NoVertexing", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu4_Jpsi_NoVertexing", &HLT_DoubleMu4_Jpsi_NoVertexing, &b_HLT_DoubleMu4_Jpsi_NoVertexing);
   // fChain->SetBranchStatus("HLT_DoubleMu4_JpsiTrkTrk_Displaced", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu4_JpsiTrkTrk_Displaced", &HLT_DoubleMu4_JpsiTrkTrk_Displaced, &b_HLT_DoubleMu4_JpsiTrkTrk_Displaced);
   // fChain->SetBranchStatus("HLT_DoubleMu43NoFiltersNoVtx", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu43NoFiltersNoVtx", &HLT_DoubleMu43NoFiltersNoVtx, &b_HLT_DoubleMu43NoFiltersNoVtx);
   // fChain->SetBranchStatus("HLT_DoubleMu48NoFiltersNoVtx", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu48NoFiltersNoVtx", &HLT_DoubleMu48NoFiltersNoVtx, &b_HLT_DoubleMu48NoFiltersNoVtx);
   // fChain->SetBranchStatus("HLT_Mu43NoFiltersNoVtx_Photon43_CaloIdL", 1);
   // fChain->SetBranchAddress("HLT_Mu43NoFiltersNoVtx_Photon43_CaloIdL", &HLT_Mu43NoFiltersNoVtx_Photon43_CaloIdL, &b_HLT_Mu43NoFiltersNoVtx_Photon43_CaloIdL);
   // fChain->SetBranchStatus("HLT_Mu48NoFiltersNoVtx_Photon48_CaloIdL", 1);
   // fChain->SetBranchAddress("HLT_Mu48NoFiltersNoVtx_Photon48_CaloIdL", &HLT_Mu48NoFiltersNoVtx_Photon48_CaloIdL, &b_HLT_Mu48NoFiltersNoVtx_Photon48_CaloIdL);
   // fChain->SetBranchStatus("HLT_Mu38NoFiltersNoVtxDisplaced_Photon38_CaloIdL", 1);
   // fChain->SetBranchAddress("HLT_Mu38NoFiltersNoVtxDisplaced_Photon38_CaloIdL", &HLT_Mu38NoFiltersNoVtxDisplaced_Photon38_CaloIdL, &b_HLT_Mu38NoFiltersNoVtxDisplaced_Photon38_CaloIdL);
   // fChain->SetBranchStatus("HLT_Mu43NoFiltersNoVtxDisplaced_Photon43_CaloIdL", 1);
   // fChain->SetBranchAddress("HLT_Mu43NoFiltersNoVtxDisplaced_Photon43_CaloIdL", &HLT_Mu43NoFiltersNoVtxDisplaced_Photon43_CaloIdL, &b_HLT_Mu43NoFiltersNoVtxDisplaced_Photon43_CaloIdL);
   // fChain->SetBranchStatus("HLT_DoubleMu40NoFiltersNoVtxDisplaced", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu40NoFiltersNoVtxDisplaced", &HLT_DoubleMu40NoFiltersNoVtxDisplaced, &b_HLT_DoubleMu40NoFiltersNoVtxDisplaced);
   // fChain->SetBranchStatus("HLT_DoubleMu20_7_Mass0to30_L1_DM4", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu20_7_Mass0to30_L1_DM4", &HLT_DoubleMu20_7_Mass0to30_L1_DM4, &b_HLT_DoubleMu20_7_Mass0to30_L1_DM4);
   // fChain->SetBranchStatus("HLT_DoubleMu20_7_Mass0to30_L1_DM4EG", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu20_7_Mass0to30_L1_DM4EG", &HLT_DoubleMu20_7_Mass0to30_L1_DM4EG, &b_HLT_DoubleMu20_7_Mass0to30_L1_DM4EG);
   // fChain->SetBranchStatus("HLT_HT425", 1);
   // fChain->SetBranchAddress("HLT_HT425", &HLT_HT425, &b_HLT_HT425);
   // fChain->SetBranchStatus("HLT_HT430_DisplacedDijet40_DisplacedTrack", 1);
   // fChain->SetBranchAddress("HLT_HT430_DisplacedDijet40_DisplacedTrack", &HLT_HT430_DisplacedDijet40_DisplacedTrack, &b_HLT_HT430_DisplacedDijet40_DisplacedTrack);
   // fChain->SetBranchStatus("HLT_HT500_DisplacedDijet40_DisplacedTrack", 1);
   // fChain->SetBranchAddress("HLT_HT500_DisplacedDijet40_DisplacedTrack", &HLT_HT500_DisplacedDijet40_DisplacedTrack, &b_HLT_HT500_DisplacedDijet40_DisplacedTrack);
   // fChain->SetBranchStatus("HLT_HT430_DisplacedDijet60_DisplacedTrack", 1);
   // fChain->SetBranchAddress("HLT_HT430_DisplacedDijet60_DisplacedTrack", &HLT_HT430_DisplacedDijet60_DisplacedTrack, &b_HLT_HT430_DisplacedDijet60_DisplacedTrack);
   // fChain->SetBranchStatus("HLT_HT400_DisplacedDijet40_DisplacedTrack", 1);
   // fChain->SetBranchAddress("HLT_HT400_DisplacedDijet40_DisplacedTrack", &HLT_HT400_DisplacedDijet40_DisplacedTrack, &b_HLT_HT400_DisplacedDijet40_DisplacedTrack);
   // fChain->SetBranchStatus("HLT_HT650_DisplacedDijet60_Inclusive", 1);
   // fChain->SetBranchAddress("HLT_HT650_DisplacedDijet60_Inclusive", &HLT_HT650_DisplacedDijet60_Inclusive, &b_HLT_HT650_DisplacedDijet60_Inclusive);
   // fChain->SetBranchStatus("HLT_HT550_DisplacedDijet60_Inclusive", 1);
   // fChain->SetBranchAddress("HLT_HT550_DisplacedDijet60_Inclusive", &HLT_HT550_DisplacedDijet60_Inclusive, &b_HLT_HT550_DisplacedDijet60_Inclusive);
   // fChain->SetBranchStatus("HLT_DiJet110_35_Mjj650_PFMET110", 1);
   // fChain->SetBranchAddress("HLT_DiJet110_35_Mjj650_PFMET110", &HLT_DiJet110_35_Mjj650_PFMET110, &b_HLT_DiJet110_35_Mjj650_PFMET110);
   // fChain->SetBranchStatus("HLT_DiJet110_35_Mjj650_PFMET120", 1);
   // fChain->SetBranchAddress("HLT_DiJet110_35_Mjj650_PFMET120", &HLT_DiJet110_35_Mjj650_PFMET120, &b_HLT_DiJet110_35_Mjj650_PFMET120);
   // fChain->SetBranchStatus("HLT_DiJet110_35_Mjj650_PFMET130", 1);
   // fChain->SetBranchAddress("HLT_DiJet110_35_Mjj650_PFMET130", &HLT_DiJet110_35_Mjj650_PFMET130, &b_HLT_DiJet110_35_Mjj650_PFMET130);
   // fChain->SetBranchStatus("HLT_TripleJet110_35_35_Mjj650_PFMET110", 1);
   // fChain->SetBranchAddress("HLT_TripleJet110_35_35_Mjj650_PFMET110", &HLT_TripleJet110_35_35_Mjj650_PFMET110, &b_HLT_TripleJet110_35_35_Mjj650_PFMET110);
   // fChain->SetBranchStatus("HLT_TripleJet110_35_35_Mjj650_PFMET120", 1);
   // fChain->SetBranchAddress("HLT_TripleJet110_35_35_Mjj650_PFMET120", &HLT_TripleJet110_35_35_Mjj650_PFMET120, &b_HLT_TripleJet110_35_35_Mjj650_PFMET120);
   // fChain->SetBranchStatus("HLT_TripleJet110_35_35_Mjj650_PFMET130", 1);
   // fChain->SetBranchAddress("HLT_TripleJet110_35_35_Mjj650_PFMET130", &HLT_TripleJet110_35_35_Mjj650_PFMET130, &b_HLT_TripleJet110_35_35_Mjj650_PFMET130);
   // fChain->SetBranchStatus("HLT_Ele30_eta2p1_WPTight_Gsf_CentralPFJet35_EleCleaned", 1);
   // fChain->SetBranchAddress("HLT_Ele30_eta2p1_WPTight_Gsf_CentralPFJet35_EleCleaned", &HLT_Ele30_eta2p1_WPTight_Gsf_CentralPFJet35_EleCleaned, &b_HLT_Ele30_eta2p1_WPTight_Gsf_CentralPFJet35_EleCleaned);
   // fChain->SetBranchStatus("HLT_Ele28_eta2p1_WPTight_Gsf_HT150", 1);
   // fChain->SetBranchAddress("HLT_Ele28_eta2p1_WPTight_Gsf_HT150", &HLT_Ele28_eta2p1_WPTight_Gsf_HT150, &b_HLT_Ele28_eta2p1_WPTight_Gsf_HT150);
   // fChain->SetBranchStatus("HLT_Ele28_HighEta_SC20_Mass55", 1);
   // fChain->SetBranchAddress("HLT_Ele28_HighEta_SC20_Mass55", &HLT_Ele28_HighEta_SC20_Mass55, &b_HLT_Ele28_HighEta_SC20_Mass55);
   // fChain->SetBranchStatus("HLT_DoubleMu20_7_Mass0to30_Photon23", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu20_7_Mass0to30_Photon23", &HLT_DoubleMu20_7_Mass0to30_Photon23, &b_HLT_DoubleMu20_7_Mass0to30_Photon23);
   // fChain->SetBranchStatus("HLT_Ele15_IsoVVVL_PFHT450_CaloBTagDeepCSV_4p5", 1);
   // fChain->SetBranchAddress("HLT_Ele15_IsoVVVL_PFHT450_CaloBTagDeepCSV_4p5", &HLT_Ele15_IsoVVVL_PFHT450_CaloBTagDeepCSV_4p5, &b_HLT_Ele15_IsoVVVL_PFHT450_CaloBTagDeepCSV_4p5);
   // fChain->SetBranchStatus("HLT_Ele15_IsoVVVL_PFHT450_PFMET50", 1);
   // fChain->SetBranchAddress("HLT_Ele15_IsoVVVL_PFHT450_PFMET50", &HLT_Ele15_IsoVVVL_PFHT450_PFMET50, &b_HLT_Ele15_IsoVVVL_PFHT450_PFMET50);
   // fChain->SetBranchStatus("HLT_Ele15_IsoVVVL_PFHT450", 1);
   // fChain->SetBranchAddress("HLT_Ele15_IsoVVVL_PFHT450", &HLT_Ele15_IsoVVVL_PFHT450, &b_HLT_Ele15_IsoVVVL_PFHT450);
   // fChain->SetBranchStatus("HLT_Ele50_IsoVVVL_PFHT450", 1);
   // fChain->SetBranchAddress("HLT_Ele50_IsoVVVL_PFHT450", &HLT_Ele50_IsoVVVL_PFHT450, &b_HLT_Ele50_IsoVVVL_PFHT450);
   // fChain->SetBranchStatus("HLT_Ele15_IsoVVVL_PFHT600", 1);
   // fChain->SetBranchAddress("HLT_Ele15_IsoVVVL_PFHT600", &HLT_Ele15_IsoVVVL_PFHT600, &b_HLT_Ele15_IsoVVVL_PFHT600);
   // fChain->SetBranchStatus("HLT_Mu4_TrkIsoVVL_DiPFJet90_40_DEta3p5_MJJ750_HTT300_PFMETNoMu60", 1);
   // fChain->SetBranchAddress("HLT_Mu4_TrkIsoVVL_DiPFJet90_40_DEta3p5_MJJ750_HTT300_PFMETNoMu60", &HLT_Mu4_TrkIsoVVL_DiPFJet90_40_DEta3p5_MJJ750_HTT300_PFMETNoMu60, &b_HLT_Mu4_TrkIsoVVL_DiPFJet90_40_DEta3p5_MJJ750_HTT300_PFMETNoMu60);
   // fChain->SetBranchStatus("HLT_Mu8_TrkIsoVVL_DiPFJet40_DEta3p5_MJJ750_HTT300_PFMETNoMu60", 1);
   // fChain->SetBranchAddress("HLT_Mu8_TrkIsoVVL_DiPFJet40_DEta3p5_MJJ750_HTT300_PFMETNoMu60", &HLT_Mu8_TrkIsoVVL_DiPFJet40_DEta3p5_MJJ750_HTT300_PFMETNoMu60, &b_HLT_Mu8_TrkIsoVVL_DiPFJet40_DEta3p5_MJJ750_HTT300_PFMETNoMu60);
   // fChain->SetBranchStatus("HLT_Mu10_TrkIsoVVL_DiPFJet40_DEta3p5_MJJ750_HTT350_PFMETNoMu60", 1);
   // fChain->SetBranchAddress("HLT_Mu10_TrkIsoVVL_DiPFJet40_DEta3p5_MJJ750_HTT350_PFMETNoMu60", &HLT_Mu10_TrkIsoVVL_DiPFJet40_DEta3p5_MJJ750_HTT350_PFMETNoMu60, &b_HLT_Mu10_TrkIsoVVL_DiPFJet40_DEta3p5_MJJ750_HTT350_PFMETNoMu60);
   // fChain->SetBranchStatus("HLT_Mu15_IsoVVVL_PFHT450_CaloBTagDeepCSV_4p5", 1);
   // fChain->SetBranchAddress("HLT_Mu15_IsoVVVL_PFHT450_CaloBTagDeepCSV_4p5", &HLT_Mu15_IsoVVVL_PFHT450_CaloBTagDeepCSV_4p5, &b_HLT_Mu15_IsoVVVL_PFHT450_CaloBTagDeepCSV_4p5);
   // fChain->SetBranchStatus("HLT_Mu15_IsoVVVL_PFHT450_PFMET50", 1);
   // fChain->SetBranchAddress("HLT_Mu15_IsoVVVL_PFHT450_PFMET50", &HLT_Mu15_IsoVVVL_PFHT450_PFMET50, &b_HLT_Mu15_IsoVVVL_PFHT450_PFMET50);
   // fChain->SetBranchStatus("HLT_Mu15_IsoVVVL_PFHT450", 1);
   // fChain->SetBranchAddress("HLT_Mu15_IsoVVVL_PFHT450", &HLT_Mu15_IsoVVVL_PFHT450, &b_HLT_Mu15_IsoVVVL_PFHT450);
   // fChain->SetBranchStatus("HLT_Mu50_IsoVVVL_PFHT450", 1);
   // fChain->SetBranchAddress("HLT_Mu50_IsoVVVL_PFHT450", &HLT_Mu50_IsoVVVL_PFHT450, &b_HLT_Mu50_IsoVVVL_PFHT450);
   // fChain->SetBranchStatus("HLT_Mu15_IsoVVVL_PFHT600", 1);
   // fChain->SetBranchAddress("HLT_Mu15_IsoVVVL_PFHT600", &HLT_Mu15_IsoVVVL_PFHT600, &b_HLT_Mu15_IsoVVVL_PFHT600);
   // fChain->SetBranchStatus("HLT_Mu3er1p5_PFJet100er2p5_PFMET70_PFMHT70_IDTight", 1);
   // fChain->SetBranchAddress("HLT_Mu3er1p5_PFJet100er2p5_PFMET70_PFMHT70_IDTight", &HLT_Mu3er1p5_PFJet100er2p5_PFMET70_PFMHT70_IDTight, &b_HLT_Mu3er1p5_PFJet100er2p5_PFMET70_PFMHT70_IDTight);
   // fChain->SetBranchStatus("HLT_Mu3er1p5_PFJet100er2p5_PFMET80_PFMHT80_IDTight", 1);
   // fChain->SetBranchAddress("HLT_Mu3er1p5_PFJet100er2p5_PFMET80_PFMHT80_IDTight", &HLT_Mu3er1p5_PFJet100er2p5_PFMET80_PFMHT80_IDTight, &b_HLT_Mu3er1p5_PFJet100er2p5_PFMET80_PFMHT80_IDTight);
   // fChain->SetBranchStatus("HLT_Mu3er1p5_PFJet100er2p5_PFMET90_PFMHT90_IDTight", 1);
   // fChain->SetBranchAddress("HLT_Mu3er1p5_PFJet100er2p5_PFMET90_PFMHT90_IDTight", &HLT_Mu3er1p5_PFJet100er2p5_PFMET90_PFMHT90_IDTight, &b_HLT_Mu3er1p5_PFJet100er2p5_PFMET90_PFMHT90_IDTight);
   // fChain->SetBranchStatus("HLT_Mu3er1p5_PFJet100er2p5_PFMET100_PFMHT100_IDTight", 1);
   // fChain->SetBranchAddress("HLT_Mu3er1p5_PFJet100er2p5_PFMET100_PFMHT100_IDTight", &HLT_Mu3er1p5_PFJet100er2p5_PFMET100_PFMHT100_IDTight, &b_HLT_Mu3er1p5_PFJet100er2p5_PFMET100_PFMHT100_IDTight);
   // fChain->SetBranchStatus("HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu70_PFMHTNoMu70_IDTight", 1);
   // fChain->SetBranchAddress("HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu70_PFMHTNoMu70_IDTight", &HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu70_PFMHTNoMu70_IDTight, &b_HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu70_PFMHTNoMu70_IDTight);
   // fChain->SetBranchStatus("HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu80_PFMHTNoMu80_IDTight", 1);
   // fChain->SetBranchAddress("HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu80_PFMHTNoMu80_IDTight", &HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu80_PFMHTNoMu80_IDTight, &b_HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu80_PFMHTNoMu80_IDTight);
   // fChain->SetBranchStatus("HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu90_PFMHTNoMu90_IDTight", 1);
   // fChain->SetBranchAddress("HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu90_PFMHTNoMu90_IDTight", &HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu90_PFMHTNoMu90_IDTight, &b_HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu90_PFMHTNoMu90_IDTight);
   // fChain->SetBranchStatus("HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu100_PFMHTNoMu100_IDTight", 1);
   // fChain->SetBranchAddress("HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu100_PFMHTNoMu100_IDTight", &HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu100_PFMHTNoMu100_IDTight, &b_HLT_Mu3er1p5_PFJet100er2p5_PFMETNoMu100_PFMHTNoMu100_IDTight);
   // fChain->SetBranchStatus("HLT_Dimuon10_PsiPrime_Barrel_Seagulls", 1);
   // fChain->SetBranchAddress("HLT_Dimuon10_PsiPrime_Barrel_Seagulls", &HLT_Dimuon10_PsiPrime_Barrel_Seagulls, &b_HLT_Dimuon10_PsiPrime_Barrel_Seagulls);
   // fChain->SetBranchStatus("HLT_Dimuon20_Jpsi_Barrel_Seagulls", 1);
   // fChain->SetBranchAddress("HLT_Dimuon20_Jpsi_Barrel_Seagulls", &HLT_Dimuon20_Jpsi_Barrel_Seagulls, &b_HLT_Dimuon20_Jpsi_Barrel_Seagulls);
   // fChain->SetBranchStatus("HLT_Dimuon12_Upsilon_y1p4", 1);
   // fChain->SetBranchAddress("HLT_Dimuon12_Upsilon_y1p4", &HLT_Dimuon12_Upsilon_y1p4, &b_HLT_Dimuon12_Upsilon_y1p4);
   // fChain->SetBranchStatus("HLT_Dimuon14_Phi_Barrel_Seagulls", 1);
   // fChain->SetBranchAddress("HLT_Dimuon14_Phi_Barrel_Seagulls", &HLT_Dimuon14_Phi_Barrel_Seagulls, &b_HLT_Dimuon14_Phi_Barrel_Seagulls);
   // fChain->SetBranchStatus("HLT_Dimuon25_Jpsi", 1);
   // fChain->SetBranchAddress("HLT_Dimuon25_Jpsi", &HLT_Dimuon25_Jpsi, &b_HLT_Dimuon25_Jpsi);
   // fChain->SetBranchStatus("HLT_Dimuon18_PsiPrime", 1);
   // fChain->SetBranchAddress("HLT_Dimuon18_PsiPrime", &HLT_Dimuon18_PsiPrime, &b_HLT_Dimuon18_PsiPrime);
   // fChain->SetBranchStatus("HLT_Dimuon18_PsiPrime_noCorrL1", 1);
   // fChain->SetBranchAddress("HLT_Dimuon18_PsiPrime_noCorrL1", &HLT_Dimuon18_PsiPrime_noCorrL1, &b_HLT_Dimuon18_PsiPrime_noCorrL1);
   // fChain->SetBranchStatus("HLT_Dimuon24_Upsilon_noCorrL1", 1);
   // fChain->SetBranchAddress("HLT_Dimuon24_Upsilon_noCorrL1", &HLT_Dimuon24_Upsilon_noCorrL1, &b_HLT_Dimuon24_Upsilon_noCorrL1);
   // fChain->SetBranchStatus("HLT_Dimuon24_Phi_noCorrL1", 1);
   // fChain->SetBranchAddress("HLT_Dimuon24_Phi_noCorrL1", &HLT_Dimuon24_Phi_noCorrL1, &b_HLT_Dimuon24_Phi_noCorrL1);
   // fChain->SetBranchStatus("HLT_Dimuon25_Jpsi_noCorrL1", 1);
   // fChain->SetBranchAddress("HLT_Dimuon25_Jpsi_noCorrL1", &HLT_Dimuon25_Jpsi_noCorrL1, &b_HLT_Dimuon25_Jpsi_noCorrL1);
   // fChain->SetBranchStatus("HLT_DiMu4_Ele9_CaloIdL_TrackIdL_DZ_Mass3p8", 1);
   // fChain->SetBranchAddress("HLT_DiMu4_Ele9_CaloIdL_TrackIdL_DZ_Mass3p8", &HLT_DiMu4_Ele9_CaloIdL_TrackIdL_DZ_Mass3p8, &b_HLT_DiMu4_Ele9_CaloIdL_TrackIdL_DZ_Mass3p8);
   // fChain->SetBranchStatus("HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ", 1);
   // fChain->SetBranchAddress("HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ", &HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ, &b_HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ);
   // fChain->SetBranchStatus("HLT_DiMu9_Ele9_CaloIdL_TrackIdL", 1);
   // fChain->SetBranchAddress("HLT_DiMu9_Ele9_CaloIdL_TrackIdL", &HLT_DiMu9_Ele9_CaloIdL_TrackIdL, &b_HLT_DiMu9_Ele9_CaloIdL_TrackIdL);
   // fChain->SetBranchStatus("HLT_DoubleIsoMu20_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_DoubleIsoMu20_eta2p1", &HLT_DoubleIsoMu20_eta2p1, &b_HLT_DoubleIsoMu20_eta2p1);
   // fChain->SetBranchStatus("HLT_TrkMu12_DoubleTrkMu5NoFiltersNoVtx", 1);
   // fChain->SetBranchAddress("HLT_TrkMu12_DoubleTrkMu5NoFiltersNoVtx", &HLT_TrkMu12_DoubleTrkMu5NoFiltersNoVtx, &b_HLT_TrkMu12_DoubleTrkMu5NoFiltersNoVtx);
   // fChain->SetBranchStatus("HLT_TrkMu16_DoubleTrkMu6NoFiltersNoVtx", 1);
   // fChain->SetBranchAddress("HLT_TrkMu16_DoubleTrkMu6NoFiltersNoVtx", &HLT_TrkMu16_DoubleTrkMu6NoFiltersNoVtx, &b_HLT_TrkMu16_DoubleTrkMu6NoFiltersNoVtx);
   // fChain->SetBranchStatus("HLT_TrkMu17_DoubleTrkMu8NoFiltersNoVtx", 1);
   // fChain->SetBranchAddress("HLT_TrkMu17_DoubleTrkMu8NoFiltersNoVtx", &HLT_TrkMu17_DoubleTrkMu8NoFiltersNoVtx, &b_HLT_TrkMu17_DoubleTrkMu8NoFiltersNoVtx);
   // fChain->SetBranchStatus("HLT_Mu8", 1);
   // fChain->SetBranchAddress("HLT_Mu8", &HLT_Mu8, &b_HLT_Mu8);
   // fChain->SetBranchStatus("HLT_Mu17", 1);
   // fChain->SetBranchAddress("HLT_Mu17", &HLT_Mu17, &b_HLT_Mu17);
   // fChain->SetBranchStatus("HLT_Mu19", 1);
   // fChain->SetBranchAddress("HLT_Mu19", &HLT_Mu19, &b_HLT_Mu19);
   // fChain->SetBranchStatus("HLT_Mu17_Photon30_IsoCaloId", 1);
   // fChain->SetBranchAddress("HLT_Mu17_Photon30_IsoCaloId", &HLT_Mu17_Photon30_IsoCaloId, &b_HLT_Mu17_Photon30_IsoCaloId);
   // fChain->SetBranchStatus("HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30", 1);
   // fChain->SetBranchAddress("HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30", &HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30, &b_HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30);
   // fChain->SetBranchStatus("HLT_Ele12_CaloIdL_TrackIdL_IsoVL_PFJet30", 1);
   // fChain->SetBranchAddress("HLT_Ele12_CaloIdL_TrackIdL_IsoVL_PFJet30", &HLT_Ele12_CaloIdL_TrackIdL_IsoVL_PFJet30, &b_HLT_Ele12_CaloIdL_TrackIdL_IsoVL_PFJet30);
   // fChain->SetBranchStatus("HLT_Ele15_CaloIdL_TrackIdL_IsoVL_PFJet30", 1);
   // fChain->SetBranchAddress("HLT_Ele15_CaloIdL_TrackIdL_IsoVL_PFJet30", &HLT_Ele15_CaloIdL_TrackIdL_IsoVL_PFJet30, &b_HLT_Ele15_CaloIdL_TrackIdL_IsoVL_PFJet30);
   // fChain->SetBranchStatus("HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30", 1);
   // fChain->SetBranchAddress("HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30", &HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30, &b_HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30);
   // fChain->SetBranchStatus("HLT_Ele8_CaloIdM_TrackIdM_PFJet30", 1);
   // fChain->SetBranchAddress("HLT_Ele8_CaloIdM_TrackIdM_PFJet30", &HLT_Ele8_CaloIdM_TrackIdM_PFJet30, &b_HLT_Ele8_CaloIdM_TrackIdM_PFJet30);
   // fChain->SetBranchStatus("HLT_Ele17_CaloIdM_TrackIdM_PFJet30", 1);
   // fChain->SetBranchAddress("HLT_Ele17_CaloIdM_TrackIdM_PFJet30", &HLT_Ele17_CaloIdM_TrackIdM_PFJet30, &b_HLT_Ele17_CaloIdM_TrackIdM_PFJet30);
   // fChain->SetBranchStatus("HLT_Ele23_CaloIdM_TrackIdM_PFJet30", 1);
   // fChain->SetBranchAddress("HLT_Ele23_CaloIdM_TrackIdM_PFJet30", &HLT_Ele23_CaloIdM_TrackIdM_PFJet30, &b_HLT_Ele23_CaloIdM_TrackIdM_PFJet30);
   // fChain->SetBranchStatus("HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165", 1);
   // fChain->SetBranchAddress("HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165", &HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165, &b_HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165);
   // fChain->SetBranchStatus("HLT_Ele115_CaloIdVT_GsfTrkIdT", 1);
   // fChain->SetBranchAddress("HLT_Ele115_CaloIdVT_GsfTrkIdT", &HLT_Ele115_CaloIdVT_GsfTrkIdT, &b_HLT_Ele115_CaloIdVT_GsfTrkIdT);
   // fChain->SetBranchStatus("HLT_Ele135_CaloIdVT_GsfTrkIdT", 1);
   // fChain->SetBranchAddress("HLT_Ele135_CaloIdVT_GsfTrkIdT", &HLT_Ele135_CaloIdVT_GsfTrkIdT, &b_HLT_Ele135_CaloIdVT_GsfTrkIdT);
   // fChain->SetBranchStatus("HLT_Ele145_CaloIdVT_GsfTrkIdT", 1);
   // fChain->SetBranchAddress("HLT_Ele145_CaloIdVT_GsfTrkIdT", &HLT_Ele145_CaloIdVT_GsfTrkIdT, &b_HLT_Ele145_CaloIdVT_GsfTrkIdT);
   // fChain->SetBranchStatus("HLT_Ele200_CaloIdVT_GsfTrkIdT", 1);
   // fChain->SetBranchAddress("HLT_Ele200_CaloIdVT_GsfTrkIdT", &HLT_Ele200_CaloIdVT_GsfTrkIdT, &b_HLT_Ele200_CaloIdVT_GsfTrkIdT);
   // fChain->SetBranchStatus("HLT_Ele250_CaloIdVT_GsfTrkIdT", 1);
   // fChain->SetBranchAddress("HLT_Ele250_CaloIdVT_GsfTrkIdT", &HLT_Ele250_CaloIdVT_GsfTrkIdT, &b_HLT_Ele250_CaloIdVT_GsfTrkIdT);
   // fChain->SetBranchStatus("HLT_Ele300_CaloIdVT_GsfTrkIdT", 1);
   // fChain->SetBranchAddress("HLT_Ele300_CaloIdVT_GsfTrkIdT", &HLT_Ele300_CaloIdVT_GsfTrkIdT, &b_HLT_Ele300_CaloIdVT_GsfTrkIdT);
   // fChain->SetBranchStatus("HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepCSV_4p5", 1);
   // fChain->SetBranchAddress("HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepCSV_4p5", &HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepCSV_4p5, &b_HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepCSV_4p5);
   // fChain->SetBranchStatus("HLT_PFHT330PT30_QuadPFJet_75_60_45_40", 1);
   // fChain->SetBranchAddress("HLT_PFHT330PT30_QuadPFJet_75_60_45_40", &HLT_PFHT330PT30_QuadPFJet_75_60_45_40, &b_HLT_PFHT330PT30_QuadPFJet_75_60_45_40);
   // fChain->SetBranchStatus("HLT_PFHT400_SixPFJet32_DoublePFBTagDeepCSV_2p94", 1);
   // fChain->SetBranchAddress("HLT_PFHT400_SixPFJet32_DoublePFBTagDeepCSV_2p94", &HLT_PFHT400_SixPFJet32_DoublePFBTagDeepCSV_2p94, &b_HLT_PFHT400_SixPFJet32_DoublePFBTagDeepCSV_2p94);
   // fChain->SetBranchStatus("HLT_PFHT400_SixPFJet32", 1);
   // fChain->SetBranchAddress("HLT_PFHT400_SixPFJet32", &HLT_PFHT400_SixPFJet32, &b_HLT_PFHT400_SixPFJet32);
   // fChain->SetBranchStatus("HLT_PFHT450_SixPFJet36_PFBTagDeepCSV_1p59", 1);
   // fChain->SetBranchAddress("HLT_PFHT450_SixPFJet36_PFBTagDeepCSV_1p59", &HLT_PFHT450_SixPFJet36_PFBTagDeepCSV_1p59, &b_HLT_PFHT450_SixPFJet36_PFBTagDeepCSV_1p59);
   // fChain->SetBranchStatus("HLT_PFHT450_SixPFJet36", 1);
   // fChain->SetBranchAddress("HLT_PFHT450_SixPFJet36", &HLT_PFHT450_SixPFJet36, &b_HLT_PFHT450_SixPFJet36);
   // fChain->SetBranchStatus("HLT_PFHT400_FivePFJet_100_100_60_30_30", 1);
   // fChain->SetBranchAddress("HLT_PFHT400_FivePFJet_100_100_60_30_30", &HLT_PFHT400_FivePFJet_100_100_60_30_30, &b_HLT_PFHT400_FivePFJet_100_100_60_30_30);
   // fChain->SetBranchStatus("HLT_PFHT400_FivePFJet_100_100_60_30_30_DoublePFBTagDeepCSV_4p5", 1);
   // fChain->SetBranchAddress("HLT_PFHT400_FivePFJet_100_100_60_30_30_DoublePFBTagDeepCSV_4p5", &HLT_PFHT400_FivePFJet_100_100_60_30_30_DoublePFBTagDeepCSV_4p5, &b_HLT_PFHT400_FivePFJet_100_100_60_30_30_DoublePFBTagDeepCSV_4p5);
   // fChain->SetBranchStatus("HLT_PFHT400_FivePFJet_120_120_60_30_30_DoublePFBTagDeepCSV_4p5", 1);
   // fChain->SetBranchAddress("HLT_PFHT400_FivePFJet_120_120_60_30_30_DoublePFBTagDeepCSV_4p5", &HLT_PFHT400_FivePFJet_120_120_60_30_30_DoublePFBTagDeepCSV_4p5, &b_HLT_PFHT400_FivePFJet_120_120_60_30_30_DoublePFBTagDeepCSV_4p5);
   // fChain->SetBranchStatus("HLT_PFHT350", 1);
   // fChain->SetBranchAddress("HLT_PFHT350", &HLT_PFHT350, &b_HLT_PFHT350);
   // fChain->SetBranchStatus("HLT_PFHT350MinPFJet15", 1);
   // fChain->SetBranchAddress("HLT_PFHT350MinPFJet15", &HLT_PFHT350MinPFJet15, &b_HLT_PFHT350MinPFJet15);
   // fChain->SetBranchStatus("HLT_Photon60_R9Id90_CaloIdL_IsoL", 1);
   // fChain->SetBranchAddress("HLT_Photon60_R9Id90_CaloIdL_IsoL", &HLT_Photon60_R9Id90_CaloIdL_IsoL, &b_HLT_Photon60_R9Id90_CaloIdL_IsoL);
   // fChain->SetBranchStatus("HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL", 1);
   // fChain->SetBranchAddress("HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL", &HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL, &b_HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL);
   // fChain->SetBranchStatus("HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL_PFHT350MinPFJet15", 1);
   // fChain->SetBranchAddress("HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL_PFHT350MinPFJet15", &HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL_PFHT350MinPFJet15, &b_HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL_PFHT350MinPFJet15);
   // fChain->SetBranchStatus("HLT_ECALHT800", 1);
   // fChain->SetBranchAddress("HLT_ECALHT800", &HLT_ECALHT800, &b_HLT_ECALHT800);
   // fChain->SetBranchStatus("HLT_DiSC30_18_EIso_AND_HE_Mass70", 1);
   // fChain->SetBranchAddress("HLT_DiSC30_18_EIso_AND_HE_Mass70", &HLT_DiSC30_18_EIso_AND_HE_Mass70, &b_HLT_DiSC30_18_EIso_AND_HE_Mass70);
   // fChain->SetBranchStatus("HLT_Physics", 1);
   // fChain->SetBranchAddress("HLT_Physics", &HLT_Physics, &b_HLT_Physics);
   // fChain->SetBranchStatus("HLT_EphemeralPhysics", 1);
   // fChain->SetBranchAddress("HLT_EphemeralPhysics", &HLT_EphemeralPhysics, &b_HLT_EphemeralPhysics);
   // fChain->SetBranchStatus("HLT_Random", 1);
   // fChain->SetBranchAddress("HLT_Random", &HLT_Random, &b_HLT_Random);
   // fChain->SetBranchStatus("HLT_ZeroBias", 1);
   // fChain->SetBranchAddress("HLT_ZeroBias", &HLT_ZeroBias, &b_HLT_ZeroBias);
   // fChain->SetBranchStatus("HLT_ZeroBias_Alignment", 1);
   // fChain->SetBranchAddress("HLT_ZeroBias_Alignment", &HLT_ZeroBias_Alignment, &b_HLT_ZeroBias_Alignment);
   // fChain->SetBranchStatus("HLT_EphemeralZeroBias", 1);
   // fChain->SetBranchAddress("HLT_EphemeralZeroBias", &HLT_EphemeralZeroBias, &b_HLT_EphemeralZeroBias);
   // fChain->SetBranchStatus("HLT_AK4CaloJet30", 1);
   // fChain->SetBranchAddress("HLT_AK4CaloJet30", &HLT_AK4CaloJet30, &b_HLT_AK4CaloJet30);
   // fChain->SetBranchStatus("HLT_AK4CaloJet40", 1);
   // fChain->SetBranchAddress("HLT_AK4CaloJet40", &HLT_AK4CaloJet40, &b_HLT_AK4CaloJet40);
   // fChain->SetBranchStatus("HLT_AK4CaloJet50", 1);
   // fChain->SetBranchAddress("HLT_AK4CaloJet50", &HLT_AK4CaloJet50, &b_HLT_AK4CaloJet50);
   // fChain->SetBranchStatus("HLT_AK4CaloJet80", 1);
   // fChain->SetBranchAddress("HLT_AK4CaloJet80", &HLT_AK4CaloJet80, &b_HLT_AK4CaloJet80);
   // fChain->SetBranchStatus("HLT_AK4CaloJet100", 1);
   // fChain->SetBranchAddress("HLT_AK4CaloJet100", &HLT_AK4CaloJet100, &b_HLT_AK4CaloJet100);
   // fChain->SetBranchStatus("HLT_AK4CaloJet120", 1);
   // fChain->SetBranchAddress("HLT_AK4CaloJet120", &HLT_AK4CaloJet120, &b_HLT_AK4CaloJet120);
   // fChain->SetBranchStatus("HLT_AK4PFJet30", 1);
   // fChain->SetBranchAddress("HLT_AK4PFJet30", &HLT_AK4PFJet30, &b_HLT_AK4PFJet30);
   // fChain->SetBranchStatus("HLT_AK4PFJet50", 1);
   // fChain->SetBranchAddress("HLT_AK4PFJet50", &HLT_AK4PFJet50, &b_HLT_AK4PFJet50);
   // fChain->SetBranchStatus("HLT_AK4PFJet80", 1);
   // fChain->SetBranchAddress("HLT_AK4PFJet80", &HLT_AK4PFJet80, &b_HLT_AK4PFJet80);
   // fChain->SetBranchStatus("HLT_AK4PFJet100", 1);
   // fChain->SetBranchAddress("HLT_AK4PFJet100", &HLT_AK4PFJet100, &b_HLT_AK4PFJet100);
   // fChain->SetBranchStatus("HLT_AK4PFJet120", 1);
   // fChain->SetBranchAddress("HLT_AK4PFJet120", &HLT_AK4PFJet120, &b_HLT_AK4PFJet120);
   // fChain->SetBranchStatus("HLT_SinglePhoton10_Eta3p1ForPPRef", 1);
   // fChain->SetBranchAddress("HLT_SinglePhoton10_Eta3p1ForPPRef", &HLT_SinglePhoton10_Eta3p1ForPPRef, &b_HLT_SinglePhoton10_Eta3p1ForPPRef);
   // fChain->SetBranchStatus("HLT_SinglePhoton20_Eta3p1ForPPRef", 1);
   // fChain->SetBranchAddress("HLT_SinglePhoton20_Eta3p1ForPPRef", &HLT_SinglePhoton20_Eta3p1ForPPRef, &b_HLT_SinglePhoton20_Eta3p1ForPPRef);
   // fChain->SetBranchStatus("HLT_SinglePhoton30_Eta3p1ForPPRef", 1);
   // fChain->SetBranchAddress("HLT_SinglePhoton30_Eta3p1ForPPRef", &HLT_SinglePhoton30_Eta3p1ForPPRef, &b_HLT_SinglePhoton30_Eta3p1ForPPRef);
   // fChain->SetBranchStatus("HLT_Photon20_HoverELoose", 1);
   // fChain->SetBranchAddress("HLT_Photon20_HoverELoose", &HLT_Photon20_HoverELoose, &b_HLT_Photon20_HoverELoose);
   // fChain->SetBranchStatus("HLT_Photon30_HoverELoose", 1);
   // fChain->SetBranchAddress("HLT_Photon30_HoverELoose", &HLT_Photon30_HoverELoose, &b_HLT_Photon30_HoverELoose);
   // fChain->SetBranchStatus("HLT_EcalCalibration", 1);
   // fChain->SetBranchAddress("HLT_EcalCalibration", &HLT_EcalCalibration, &b_HLT_EcalCalibration);
   // fChain->SetBranchStatus("HLT_HcalCalibration", 1);
   // fChain->SetBranchAddress("HLT_HcalCalibration", &HLT_HcalCalibration, &b_HLT_HcalCalibration);
   // fChain->SetBranchStatus("HLT_L1UnpairedBunchBptxMinus", 1);
   // fChain->SetBranchAddress("HLT_L1UnpairedBunchBptxMinus", &HLT_L1UnpairedBunchBptxMinus, &b_HLT_L1UnpairedBunchBptxMinus);
   // fChain->SetBranchStatus("HLT_L1UnpairedBunchBptxPlus", 1);
   // fChain->SetBranchAddress("HLT_L1UnpairedBunchBptxPlus", &HLT_L1UnpairedBunchBptxPlus, &b_HLT_L1UnpairedBunchBptxPlus);
   // fChain->SetBranchStatus("HLT_L1NotBptxOR", 1);
   // fChain->SetBranchAddress("HLT_L1NotBptxOR", &HLT_L1NotBptxOR, &b_HLT_L1NotBptxOR);
   // fChain->SetBranchStatus("HLT_L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142", 1);
   // fChain->SetBranchAddress("HLT_L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142", &HLT_L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142, &b_HLT_L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142);
   // fChain->SetBranchStatus("HLT_CDC_L2cosmic_10_er1p0", 1);
   // fChain->SetBranchAddress("HLT_CDC_L2cosmic_10_er1p0", &HLT_CDC_L2cosmic_10_er1p0, &b_HLT_CDC_L2cosmic_10_er1p0);
   // fChain->SetBranchStatus("HLT_CDC_L2cosmic_5p5_er1p0", 1);
   // fChain->SetBranchAddress("HLT_CDC_L2cosmic_5p5_er1p0", &HLT_CDC_L2cosmic_5p5_er1p0, &b_HLT_CDC_L2cosmic_5p5_er1p0);
   // fChain->SetBranchStatus("HLT_HcalNZS", 1);
   // fChain->SetBranchAddress("HLT_HcalNZS", &HLT_HcalNZS, &b_HLT_HcalNZS);
   // fChain->SetBranchStatus("HLT_HcalPhiSym", 1);
   // fChain->SetBranchAddress("HLT_HcalPhiSym", &HLT_HcalPhiSym, &b_HLT_HcalPhiSym);
   // fChain->SetBranchStatus("HLT_HcalIsolatedbunch", 1);
   // fChain->SetBranchAddress("HLT_HcalIsolatedbunch", &HLT_HcalIsolatedbunch, &b_HLT_HcalIsolatedbunch);
   // fChain->SetBranchStatus("HLT_IsoTrackHB", 1);
   // fChain->SetBranchAddress("HLT_IsoTrackHB", &HLT_IsoTrackHB, &b_HLT_IsoTrackHB);
   // fChain->SetBranchStatus("HLT_IsoTrackHE", 1);
   // fChain->SetBranchAddress("HLT_IsoTrackHE", &HLT_IsoTrackHE, &b_HLT_IsoTrackHE);
   // fChain->SetBranchStatus("HLT_ZeroBias_FirstCollisionAfterAbortGap", 1);
   // fChain->SetBranchAddress("HLT_ZeroBias_FirstCollisionAfterAbortGap", &HLT_ZeroBias_FirstCollisionAfterAbortGap, &b_HLT_ZeroBias_FirstCollisionAfterAbortGap);
   // fChain->SetBranchStatus("HLT_ZeroBias_IsolatedBunches", 1);
   // fChain->SetBranchAddress("HLT_ZeroBias_IsolatedBunches", &HLT_ZeroBias_IsolatedBunches, &b_HLT_ZeroBias_IsolatedBunches);
   // fChain->SetBranchStatus("HLT_ZeroBias_FirstCollisionInTrain", 1);
   // fChain->SetBranchAddress("HLT_ZeroBias_FirstCollisionInTrain", &HLT_ZeroBias_FirstCollisionInTrain, &b_HLT_ZeroBias_FirstCollisionInTrain);
   // fChain->SetBranchStatus("HLT_ZeroBias_LastCollisionInTrain", 1);
   // fChain->SetBranchAddress("HLT_ZeroBias_LastCollisionInTrain", &HLT_ZeroBias_LastCollisionInTrain, &b_HLT_ZeroBias_LastCollisionInTrain);
   // fChain->SetBranchStatus("HLT_ZeroBias_FirstBXAfterTrain", 1);
   // fChain->SetBranchAddress("HLT_ZeroBias_FirstBXAfterTrain", &HLT_ZeroBias_FirstBXAfterTrain, &b_HLT_ZeroBias_FirstBXAfterTrain);
   // fChain->SetBranchStatus("HLT_MediumChargedIsoPFTau180HighPtRelaxedIso_Trk50_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_MediumChargedIsoPFTau180HighPtRelaxedIso_Trk50_eta2p1", &HLT_MediumChargedIsoPFTau180HighPtRelaxedIso_Trk50_eta2p1, &b_HLT_MediumChargedIsoPFTau180HighPtRelaxedIso_Trk50_eta2p1);
   // fChain->SetBranchStatus("HLT_MediumChargedIsoPFTau200HighPtRelaxedIso_Trk50_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_MediumChargedIsoPFTau200HighPtRelaxedIso_Trk50_eta2p1", &HLT_MediumChargedIsoPFTau200HighPtRelaxedIso_Trk50_eta2p1, &b_HLT_MediumChargedIsoPFTau200HighPtRelaxedIso_Trk50_eta2p1);
   // fChain->SetBranchStatus("HLT_MediumChargedIsoPFTau220HighPtRelaxedIso_Trk50_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_MediumChargedIsoPFTau220HighPtRelaxedIso_Trk50_eta2p1", &HLT_MediumChargedIsoPFTau220HighPtRelaxedIso_Trk50_eta2p1, &b_HLT_MediumChargedIsoPFTau220HighPtRelaxedIso_Trk50_eta2p1);
   // fChain->SetBranchStatus("HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL", 1);
   // fChain->SetBranchAddress("HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL", &HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL, &b_HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL);
   // fChain->SetBranchStatus("HLT_Rsq0p35", 1);
   // fChain->SetBranchAddress("HLT_Rsq0p35", &HLT_Rsq0p35, &b_HLT_Rsq0p35);
   // fChain->SetBranchStatus("HLT_Rsq0p40", 1);
   // fChain->SetBranchAddress("HLT_Rsq0p40", &HLT_Rsq0p40, &b_HLT_Rsq0p40);
   // fChain->SetBranchStatus("HLT_RsqMR300_Rsq0p09_MR200", 1);
   // fChain->SetBranchAddress("HLT_RsqMR300_Rsq0p09_MR200", &HLT_RsqMR300_Rsq0p09_MR200, &b_HLT_RsqMR300_Rsq0p09_MR200);
   // fChain->SetBranchStatus("HLT_RsqMR320_Rsq0p09_MR200", 1);
   // fChain->SetBranchAddress("HLT_RsqMR320_Rsq0p09_MR200", &HLT_RsqMR320_Rsq0p09_MR200, &b_HLT_RsqMR320_Rsq0p09_MR200);
   // fChain->SetBranchStatus("HLT_RsqMR300_Rsq0p09_MR200_4jet", 1);
   // fChain->SetBranchAddress("HLT_RsqMR300_Rsq0p09_MR200_4jet", &HLT_RsqMR300_Rsq0p09_MR200_4jet, &b_HLT_RsqMR300_Rsq0p09_MR200_4jet);
   // fChain->SetBranchStatus("HLT_RsqMR320_Rsq0p09_MR200_4jet", 1);
   // fChain->SetBranchAddress("HLT_RsqMR320_Rsq0p09_MR200_4jet", &HLT_RsqMR320_Rsq0p09_MR200_4jet, &b_HLT_RsqMR320_Rsq0p09_MR200_4jet);
   // fChain->SetBranchStatus("HLT_IsoMu27_MET90", 1);
   // fChain->SetBranchAddress("HLT_IsoMu27_MET90", &HLT_IsoMu27_MET90, &b_HLT_IsoMu27_MET90);
   // fChain->SetBranchStatus("HLT_VBF_DoubleLooseChargedIsoPFTauHPS20_Trk1_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_VBF_DoubleLooseChargedIsoPFTauHPS20_Trk1_eta2p1", &HLT_VBF_DoubleLooseChargedIsoPFTauHPS20_Trk1_eta2p1, &b_HLT_VBF_DoubleLooseChargedIsoPFTauHPS20_Trk1_eta2p1);
   // fChain->SetBranchStatus("HLT_VBF_DoubleMediumChargedIsoPFTauHPS20_Trk1_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_VBF_DoubleMediumChargedIsoPFTauHPS20_Trk1_eta2p1", &HLT_VBF_DoubleMediumChargedIsoPFTauHPS20_Trk1_eta2p1, &b_HLT_VBF_DoubleMediumChargedIsoPFTauHPS20_Trk1_eta2p1);
   // fChain->SetBranchStatus("HLT_VBF_DoubleTightChargedIsoPFTauHPS20_Trk1_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_VBF_DoubleTightChargedIsoPFTauHPS20_Trk1_eta2p1", &HLT_VBF_DoubleTightChargedIsoPFTauHPS20_Trk1_eta2p1, &b_HLT_VBF_DoubleTightChargedIsoPFTauHPS20_Trk1_eta2p1);
   // fChain->SetBranchStatus("HLT_Photon50_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3_PFMET50", 1);
   // fChain->SetBranchAddress("HLT_Photon50_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3_PFMET50", &HLT_Photon50_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3_PFMET50, &b_HLT_Photon50_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3_PFMET50);
   // fChain->SetBranchStatus("HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3", 1);
   // fChain->SetBranchAddress("HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3", &HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3, &b_HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3);
   // fChain->SetBranchStatus("HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ600DEta3", 1);
   // fChain->SetBranchAddress("HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ600DEta3", &HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ600DEta3, &b_HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ600DEta3);
   // fChain->SetBranchStatus("HLT_PFMET100_PFMHT100_IDTight_PFHT60", 1);
   // fChain->SetBranchAddress("HLT_PFMET100_PFMHT100_IDTight_PFHT60", &HLT_PFMET100_PFMHT100_IDTight_PFHT60, &b_HLT_PFMET100_PFMHT100_IDTight_PFHT60);
   // fChain->SetBranchStatus("HLT_PFMETNoMu100_PFMHTNoMu100_IDTight_PFHT60", 1);
   // fChain->SetBranchAddress("HLT_PFMETNoMu100_PFMHTNoMu100_IDTight_PFHT60", &HLT_PFMETNoMu100_PFMHTNoMu100_IDTight_PFHT60, &b_HLT_PFMETNoMu100_PFMHTNoMu100_IDTight_PFHT60);
   // fChain->SetBranchStatus("HLT_PFMETTypeOne100_PFMHT100_IDTight_PFHT60", 1);
   // fChain->SetBranchAddress("HLT_PFMETTypeOne100_PFMHT100_IDTight_PFHT60", &HLT_PFMETTypeOne100_PFMHT100_IDTight_PFHT60, &b_HLT_PFMETTypeOne100_PFMHT100_IDTight_PFHT60);
   // fChain->SetBranchStatus("HLT_Mu18_Mu9_SameSign", 1);
   // fChain->SetBranchAddress("HLT_Mu18_Mu9_SameSign", &HLT_Mu18_Mu9_SameSign, &b_HLT_Mu18_Mu9_SameSign);
   // fChain->SetBranchStatus("HLT_Mu18_Mu9_SameSign_DZ", 1);
   // fChain->SetBranchAddress("HLT_Mu18_Mu9_SameSign_DZ", &HLT_Mu18_Mu9_SameSign_DZ, &b_HLT_Mu18_Mu9_SameSign_DZ);
   // fChain->SetBranchStatus("HLT_Mu18_Mu9", 1);
   // fChain->SetBranchAddress("HLT_Mu18_Mu9", &HLT_Mu18_Mu9, &b_HLT_Mu18_Mu9);
   // fChain->SetBranchStatus("HLT_Mu18_Mu9_DZ", 1);
   // fChain->SetBranchAddress("HLT_Mu18_Mu9_DZ", &HLT_Mu18_Mu9_DZ, &b_HLT_Mu18_Mu9_DZ);
   // fChain->SetBranchStatus("HLT_Mu20_Mu10_SameSign", 1);
   // fChain->SetBranchAddress("HLT_Mu20_Mu10_SameSign", &HLT_Mu20_Mu10_SameSign, &b_HLT_Mu20_Mu10_SameSign);
   // fChain->SetBranchStatus("HLT_Mu20_Mu10_SameSign_DZ", 1);
   // fChain->SetBranchAddress("HLT_Mu20_Mu10_SameSign_DZ", &HLT_Mu20_Mu10_SameSign_DZ, &b_HLT_Mu20_Mu10_SameSign_DZ);
   // fChain->SetBranchStatus("HLT_Mu20_Mu10", 1);
   // fChain->SetBranchAddress("HLT_Mu20_Mu10", &HLT_Mu20_Mu10, &b_HLT_Mu20_Mu10);
   // fChain->SetBranchStatus("HLT_Mu20_Mu10_DZ", 1);
   // fChain->SetBranchAddress("HLT_Mu20_Mu10_DZ", &HLT_Mu20_Mu10_DZ, &b_HLT_Mu20_Mu10_DZ);
   // fChain->SetBranchStatus("HLT_Mu23_Mu12_SameSign", 1);
   // fChain->SetBranchAddress("HLT_Mu23_Mu12_SameSign", &HLT_Mu23_Mu12_SameSign, &b_HLT_Mu23_Mu12_SameSign);
   // fChain->SetBranchStatus("HLT_Mu23_Mu12_SameSign_DZ", 1);
   // fChain->SetBranchAddress("HLT_Mu23_Mu12_SameSign_DZ", &HLT_Mu23_Mu12_SameSign_DZ, &b_HLT_Mu23_Mu12_SameSign_DZ);
   // fChain->SetBranchStatus("HLT_Mu23_Mu12", 1);
   // fChain->SetBranchAddress("HLT_Mu23_Mu12", &HLT_Mu23_Mu12, &b_HLT_Mu23_Mu12);
   // fChain->SetBranchStatus("HLT_Mu23_Mu12_DZ", 1);
   // fChain->SetBranchAddress("HLT_Mu23_Mu12_DZ", &HLT_Mu23_Mu12_DZ, &b_HLT_Mu23_Mu12_DZ);
   // fChain->SetBranchStatus("HLT_DoubleMu2_Jpsi_DoubleTrk1_Phi1p05", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu2_Jpsi_DoubleTrk1_Phi1p05", &HLT_DoubleMu2_Jpsi_DoubleTrk1_Phi1p05, &b_HLT_DoubleMu2_Jpsi_DoubleTrk1_Phi1p05);
   // fChain->SetBranchStatus("HLT_DoubleMu2_Jpsi_DoubleTkMu0_Phi", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu2_Jpsi_DoubleTkMu0_Phi", &HLT_DoubleMu2_Jpsi_DoubleTkMu0_Phi, &b_HLT_DoubleMu2_Jpsi_DoubleTkMu0_Phi);
   // fChain->SetBranchStatus("HLT_DoubleMu3_DCA_PFMET50_PFMHT60", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu3_DCA_PFMET50_PFMHT60", &HLT_DoubleMu3_DCA_PFMET50_PFMHT60, &b_HLT_DoubleMu3_DCA_PFMET50_PFMHT60);
   // fChain->SetBranchStatus("HLT_TripleMu_5_3_3_Mass3p8_DCA", 1);
   // fChain->SetBranchAddress("HLT_TripleMu_5_3_3_Mass3p8_DCA", &HLT_TripleMu_5_3_3_Mass3p8_DCA, &b_HLT_TripleMu_5_3_3_Mass3p8_DCA);
   // fChain->SetBranchStatus("HLT_QuadPFJet98_83_71_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet98_83_71_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1", &HLT_QuadPFJet98_83_71_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1, &b_HLT_QuadPFJet98_83_71_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1);
   // fChain->SetBranchStatus("HLT_QuadPFJet103_88_75_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet103_88_75_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1", &HLT_QuadPFJet103_88_75_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1, &b_HLT_QuadPFJet103_88_75_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1);
   // fChain->SetBranchStatus("HLT_QuadPFJet111_90_80_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet111_90_80_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1", &HLT_QuadPFJet111_90_80_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1, &b_HLT_QuadPFJet111_90_80_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1);
   // fChain->SetBranchStatus("HLT_QuadPFJet98_83_71_15_PFBTagDeepCSV_1p3_VBF2", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet98_83_71_15_PFBTagDeepCSV_1p3_VBF2", &HLT_QuadPFJet98_83_71_15_PFBTagDeepCSV_1p3_VBF2, &b_HLT_QuadPFJet98_83_71_15_PFBTagDeepCSV_1p3_VBF2);
   // fChain->SetBranchStatus("HLT_QuadPFJet103_88_75_15_PFBTagDeepCSV_1p3_VBF2", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet103_88_75_15_PFBTagDeepCSV_1p3_VBF2", &HLT_QuadPFJet103_88_75_15_PFBTagDeepCSV_1p3_VBF2, &b_HLT_QuadPFJet103_88_75_15_PFBTagDeepCSV_1p3_VBF2);
   // fChain->SetBranchStatus("HLT_QuadPFJet105_88_76_15_PFBTagDeepCSV_1p3_VBF2", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet105_88_76_15_PFBTagDeepCSV_1p3_VBF2", &HLT_QuadPFJet105_88_76_15_PFBTagDeepCSV_1p3_VBF2, &b_HLT_QuadPFJet105_88_76_15_PFBTagDeepCSV_1p3_VBF2);
   // fChain->SetBranchStatus("HLT_QuadPFJet111_90_80_15_PFBTagDeepCSV_1p3_VBF2", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet111_90_80_15_PFBTagDeepCSV_1p3_VBF2", &HLT_QuadPFJet111_90_80_15_PFBTagDeepCSV_1p3_VBF2, &b_HLT_QuadPFJet111_90_80_15_PFBTagDeepCSV_1p3_VBF2);
   // fChain->SetBranchStatus("HLT_QuadPFJet98_83_71_15", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet98_83_71_15", &HLT_QuadPFJet98_83_71_15, &b_HLT_QuadPFJet98_83_71_15);
   // fChain->SetBranchStatus("HLT_QuadPFJet103_88_75_15", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet103_88_75_15", &HLT_QuadPFJet103_88_75_15, &b_HLT_QuadPFJet103_88_75_15);
   // fChain->SetBranchStatus("HLT_QuadPFJet105_88_76_15", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet105_88_76_15", &HLT_QuadPFJet105_88_76_15, &b_HLT_QuadPFJet105_88_76_15);
   // fChain->SetBranchStatus("HLT_QuadPFJet111_90_80_15", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet111_90_80_15", &HLT_QuadPFJet111_90_80_15, &b_HLT_QuadPFJet111_90_80_15);
   // fChain->SetBranchStatus("HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p17", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p17", &HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p17, &b_HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p17);
   // fChain->SetBranchStatus("HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p1", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p1", &HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p1, &b_HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p1);
   // fChain->SetBranchStatus("HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_p02", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_p02", &HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_p02, &b_HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_p02);
   // fChain->SetBranchStatus("HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np2", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np2", &HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np2, &b_HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np2);
   // fChain->SetBranchStatus("HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np4", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np4", &HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np4, &b_HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np4);
   // fChain->SetBranchStatus("HLT_Mu12_IP6_part0", 1);
   // fChain->SetBranchAddress("HLT_Mu12_IP6_part0", &HLT_Mu12_IP6_part0, &b_HLT_Mu12_IP6_part0);
   // fChain->SetBranchStatus("HLT_Mu12_IP6_part1", 1);
   // fChain->SetBranchAddress("HLT_Mu12_IP6_part1", &HLT_Mu12_IP6_part1, &b_HLT_Mu12_IP6_part1);
   // fChain->SetBranchStatus("HLT_Mu12_IP6_part2", 1);
   // fChain->SetBranchAddress("HLT_Mu12_IP6_part2", &HLT_Mu12_IP6_part2, &b_HLT_Mu12_IP6_part2);
   // fChain->SetBranchStatus("HLT_Mu12_IP6_part3", 1);
   // fChain->SetBranchAddress("HLT_Mu12_IP6_part3", &HLT_Mu12_IP6_part3, &b_HLT_Mu12_IP6_part3);
   // fChain->SetBranchStatus("HLT_Mu12_IP6_part4", 1);
   // fChain->SetBranchAddress("HLT_Mu12_IP6_part4", &HLT_Mu12_IP6_part4, &b_HLT_Mu12_IP6_part4);
   // fChain->SetBranchStatus("HLT_Mu9_IP5_part0", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP5_part0", &HLT_Mu9_IP5_part0, &b_HLT_Mu9_IP5_part0);
   // fChain->SetBranchStatus("HLT_Mu9_IP5_part1", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP5_part1", &HLT_Mu9_IP5_part1, &b_HLT_Mu9_IP5_part1);
   // fChain->SetBranchStatus("HLT_Mu9_IP5_part2", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP5_part2", &HLT_Mu9_IP5_part2, &b_HLT_Mu9_IP5_part2);
   // fChain->SetBranchStatus("HLT_Mu9_IP5_part3", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP5_part3", &HLT_Mu9_IP5_part3, &b_HLT_Mu9_IP5_part3);
   // fChain->SetBranchStatus("HLT_Mu9_IP5_part4", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP5_part4", &HLT_Mu9_IP5_part4, &b_HLT_Mu9_IP5_part4);
   // fChain->SetBranchStatus("HLT_Mu7_IP4_part0", 1);
   // fChain->SetBranchAddress("HLT_Mu7_IP4_part0", &HLT_Mu7_IP4_part0, &b_HLT_Mu7_IP4_part0);
   // fChain->SetBranchStatus("HLT_Mu7_IP4_part1", 1);
   // fChain->SetBranchAddress("HLT_Mu7_IP4_part1", &HLT_Mu7_IP4_part1, &b_HLT_Mu7_IP4_part1);
   // fChain->SetBranchStatus("HLT_Mu7_IP4_part2", 1);
   // fChain->SetBranchAddress("HLT_Mu7_IP4_part2", &HLT_Mu7_IP4_part2, &b_HLT_Mu7_IP4_part2);
   // fChain->SetBranchStatus("HLT_Mu7_IP4_part3", 1);
   // fChain->SetBranchAddress("HLT_Mu7_IP4_part3", &HLT_Mu7_IP4_part3, &b_HLT_Mu7_IP4_part3);
   // fChain->SetBranchStatus("HLT_Mu7_IP4_part4", 1);
   // fChain->SetBranchAddress("HLT_Mu7_IP4_part4", &HLT_Mu7_IP4_part4, &b_HLT_Mu7_IP4_part4);
   // fChain->SetBranchStatus("HLT_Mu9_IP4_part0", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP4_part0", &HLT_Mu9_IP4_part0, &b_HLT_Mu9_IP4_part0);
   // fChain->SetBranchStatus("HLT_Mu9_IP4_part1", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP4_part1", &HLT_Mu9_IP4_part1, &b_HLT_Mu9_IP4_part1);
   // fChain->SetBranchStatus("HLT_Mu9_IP4_part2", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP4_part2", &HLT_Mu9_IP4_part2, &b_HLT_Mu9_IP4_part2);
   // fChain->SetBranchStatus("HLT_Mu9_IP4_part3", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP4_part3", &HLT_Mu9_IP4_part3, &b_HLT_Mu9_IP4_part3);
   // fChain->SetBranchStatus("HLT_Mu9_IP4_part4", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP4_part4", &HLT_Mu9_IP4_part4, &b_HLT_Mu9_IP4_part4);
   // fChain->SetBranchStatus("HLT_Mu8_IP5_part0", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP5_part0", &HLT_Mu8_IP5_part0, &b_HLT_Mu8_IP5_part0);
   // fChain->SetBranchStatus("HLT_Mu8_IP5_part1", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP5_part1", &HLT_Mu8_IP5_part1, &b_HLT_Mu8_IP5_part1);
   // fChain->SetBranchStatus("HLT_Mu8_IP5_part2", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP5_part2", &HLT_Mu8_IP5_part2, &b_HLT_Mu8_IP5_part2);
   // fChain->SetBranchStatus("HLT_Mu8_IP5_part3", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP5_part3", &HLT_Mu8_IP5_part3, &b_HLT_Mu8_IP5_part3);
   // fChain->SetBranchStatus("HLT_Mu8_IP5_part4", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP5_part4", &HLT_Mu8_IP5_part4, &b_HLT_Mu8_IP5_part4);
   // fChain->SetBranchStatus("HLT_Mu8_IP6_part0", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP6_part0", &HLT_Mu8_IP6_part0, &b_HLT_Mu8_IP6_part0);
   // fChain->SetBranchStatus("HLT_Mu8_IP6_part1", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP6_part1", &HLT_Mu8_IP6_part1, &b_HLT_Mu8_IP6_part1);
   // fChain->SetBranchStatus("HLT_Mu8_IP6_part2", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP6_part2", &HLT_Mu8_IP6_part2, &b_HLT_Mu8_IP6_part2);
   // fChain->SetBranchStatus("HLT_Mu8_IP6_part3", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP6_part3", &HLT_Mu8_IP6_part3, &b_HLT_Mu8_IP6_part3);
   // fChain->SetBranchStatus("HLT_Mu8_IP6_part4", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP6_part4", &HLT_Mu8_IP6_part4, &b_HLT_Mu8_IP6_part4);
   // fChain->SetBranchStatus("HLT_Mu9_IP6_part0", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP6_part0", &HLT_Mu9_IP6_part0, &b_HLT_Mu9_IP6_part0);
   // fChain->SetBranchStatus("HLT_Mu9_IP6_part1", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP6_part1", &HLT_Mu9_IP6_part1, &b_HLT_Mu9_IP6_part1);
   // fChain->SetBranchStatus("HLT_Mu9_IP6_part2", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP6_part2", &HLT_Mu9_IP6_part2, &b_HLT_Mu9_IP6_part2);
   // fChain->SetBranchStatus("HLT_Mu9_IP6_part3", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP6_part3", &HLT_Mu9_IP6_part3, &b_HLT_Mu9_IP6_part3);
   // fChain->SetBranchStatus("HLT_Mu9_IP6_part4", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP6_part4", &HLT_Mu9_IP6_part4, &b_HLT_Mu9_IP6_part4);
   // fChain->SetBranchStatus("HLT_Mu8_IP3_part0", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP3_part0", &HLT_Mu8_IP3_part0, &b_HLT_Mu8_IP3_part0);
   // fChain->SetBranchStatus("HLT_Mu8_IP3_part1", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP3_part1", &HLT_Mu8_IP3_part1, &b_HLT_Mu8_IP3_part1);
   // fChain->SetBranchStatus("HLT_Mu8_IP3_part2", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP3_part2", &HLT_Mu8_IP3_part2, &b_HLT_Mu8_IP3_part2);
   // fChain->SetBranchStatus("HLT_Mu8_IP3_part3", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP3_part3", &HLT_Mu8_IP3_part3, &b_HLT_Mu8_IP3_part3);
   // fChain->SetBranchStatus("HLT_Mu8_IP3_part4", 1);
   // fChain->SetBranchAddress("HLT_Mu8_IP3_part4", &HLT_Mu8_IP3_part4, &b_HLT_Mu8_IP3_part4);
   // fChain->SetBranchStatus("HLT_Mu9_IP0_part0", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP0_part0", &HLT_Mu9_IP0_part0, &b_HLT_Mu9_IP0_part0);
   // fChain->SetBranchStatus("HLT_Mu9_IP3_part0", 1);
   // fChain->SetBranchAddress("HLT_Mu9_IP3_part0", &HLT_Mu9_IP3_part0, &b_HLT_Mu9_IP3_part0);
   // fChain->SetBranchStatus("HLT_QuadPFJet105_88_76_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet105_88_76_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1", &HLT_QuadPFJet105_88_76_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1, &b_HLT_QuadPFJet105_88_76_15_DoublePFBTagDeepCSV_1p3_7p7_VBF1);
   // fChain->SetBranchStatus("HLT_TrkMu6NoFiltersNoVtx", 1);
   // fChain->SetBranchAddress("HLT_TrkMu6NoFiltersNoVtx", &HLT_TrkMu6NoFiltersNoVtx, &b_HLT_TrkMu6NoFiltersNoVtx);
   // fChain->SetBranchStatus("HLT_TrkMu16NoFiltersNoVtx", 1);
   // fChain->SetBranchAddress("HLT_TrkMu16NoFiltersNoVtx", &HLT_TrkMu16NoFiltersNoVtx, &b_HLT_TrkMu16NoFiltersNoVtx);
   // fChain->SetBranchStatus("HLT_DoubleTrkMu_16_6_NoFiltersNoVtx", 1);
   // fChain->SetBranchAddress("HLT_DoubleTrkMu_16_6_NoFiltersNoVtx", &HLT_DoubleTrkMu_16_6_NoFiltersNoVtx, &b_HLT_DoubleTrkMu_16_6_NoFiltersNoVtx);
   // fChain->SetBranchStatus("HLT_DoubleMediumChargedIsoPFTauHPS40_Trk1_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_DoubleMediumChargedIsoPFTauHPS40_Trk1_eta2p1", &HLT_DoubleMediumChargedIsoPFTauHPS40_Trk1_eta2p1, &b_HLT_DoubleMediumChargedIsoPFTauHPS40_Trk1_eta2p1);
   // fChain->SetBranchStatus("HLT_DoubleTightChargedIsoPFTauHPS35_Trk1_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_DoubleTightChargedIsoPFTauHPS35_Trk1_eta2p1", &HLT_DoubleTightChargedIsoPFTauHPS35_Trk1_eta2p1, &b_HLT_DoubleTightChargedIsoPFTauHPS35_Trk1_eta2p1);
   // fChain->SetBranchStatus("HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1", 1);
   // fChain->SetBranchAddress("HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1", &HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1, &b_HLT_Ele24_eta2p1_WPTight_Gsf_LooseDeepTauPFTauHPS30_eta2p1_CrossL1);
   // fChain->SetBranchStatus("HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1", &HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1, &b_HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1);
   // fChain->SetBranchStatus("HLT_IsoMu24_eta2p1_LooseDeepTauPFTauHPS180_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu24_eta2p1_LooseDeepTauPFTauHPS180_eta2p1", &HLT_IsoMu24_eta2p1_LooseDeepTauPFTauHPS180_eta2p1, &b_HLT_IsoMu24_eta2p1_LooseDeepTauPFTauHPS180_eta2p1);
   // fChain->SetBranchStatus("HLT_IsoMu24_eta2p1_LooseDeepTauPFTauHPS30_eta2p1_CrossL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu24_eta2p1_LooseDeepTauPFTauHPS30_eta2p1_CrossL1", &HLT_IsoMu24_eta2p1_LooseDeepTauPFTauHPS30_eta2p1_CrossL1, &b_HLT_IsoMu24_eta2p1_LooseDeepTauPFTauHPS30_eta2p1_CrossL1);
   // fChain->SetBranchStatus("HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS35_L2NN_eta2p1_CrossL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS35_L2NN_eta2p1_CrossL1", &HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS35_L2NN_eta2p1_CrossL1, &b_HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS35_L2NN_eta2p1_CrossL1);
   // fChain->SetBranchStatus("HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1", &HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1, &b_HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1);
   // fChain->SetBranchStatus("HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepJet_4p5", 1);
   // fChain->SetBranchAddress("HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepJet_4p5", &HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepJet_4p5, &b_HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepJet_4p5);
   // fChain->SetBranchStatus("HLT_PFHT400_FivePFJet_100_100_60_30_30_DoublePFBTagDeepJet_4p5", 1);
   // fChain->SetBranchAddress("HLT_PFHT400_FivePFJet_100_100_60_30_30_DoublePFBTagDeepJet_4p5", &HLT_PFHT400_FivePFJet_100_100_60_30_30_DoublePFBTagDeepJet_4p5, &b_HLT_PFHT400_FivePFJet_100_100_60_30_30_DoublePFBTagDeepJet_4p5);
   // fChain->SetBranchStatus("HLT_PFHT400_FivePFJet_120_120_60_30_30_DoublePFBTagDeepJet_4p5", 1);
   // fChain->SetBranchAddress("HLT_PFHT400_FivePFJet_120_120_60_30_30_DoublePFBTagDeepJet_4p5", &HLT_PFHT400_FivePFJet_120_120_60_30_30_DoublePFBTagDeepJet_4p5, &b_HLT_PFHT400_FivePFJet_120_120_60_30_30_DoublePFBTagDeepJet_4p5);
   // fChain->SetBranchStatus("HLT_PFHT400_SixPFJet32_DoublePFBTagDeepJet_2p94", 1);
   // fChain->SetBranchAddress("HLT_PFHT400_SixPFJet32_DoublePFBTagDeepJet_2p94", &HLT_PFHT400_SixPFJet32_DoublePFBTagDeepJet_2p94, &b_HLT_PFHT400_SixPFJet32_DoublePFBTagDeepJet_2p94);
   // fChain->SetBranchStatus("HLT_PFHT450_SixPFJet36_PFBTagDeepJet_1p59", 1);
   // fChain->SetBranchAddress("HLT_PFHT450_SixPFJet36_PFBTagDeepJet_1p59", &HLT_PFHT450_SixPFJet36_PFBTagDeepJet_1p59, &b_HLT_PFHT450_SixPFJet36_PFBTagDeepJet_1p59);
   // fChain->SetBranchStatus("HLT_QuadPFJet103_88_75_15_DoublePFBTagDeepJet_1p3_7p7_VBF1", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet103_88_75_15_DoublePFBTagDeepJet_1p3_7p7_VBF1", &HLT_QuadPFJet103_88_75_15_DoublePFBTagDeepJet_1p3_7p7_VBF1, &b_HLT_QuadPFJet103_88_75_15_DoublePFBTagDeepJet_1p3_7p7_VBF1);
   // fChain->SetBranchStatus("HLT_QuadPFJet103_88_75_15_PFBTagDeepJet_1p3_VBF2", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet103_88_75_15_PFBTagDeepJet_1p3_VBF2", &HLT_QuadPFJet103_88_75_15_PFBTagDeepJet_1p3_VBF2, &b_HLT_QuadPFJet103_88_75_15_PFBTagDeepJet_1p3_VBF2);
   // fChain->SetBranchStatus("HLT_QuadPFJet105_88_76_15_DoublePFBTagDeepJet_1p3_7p7_VBF1", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet105_88_76_15_DoublePFBTagDeepJet_1p3_7p7_VBF1", &HLT_QuadPFJet105_88_76_15_DoublePFBTagDeepJet_1p3_7p7_VBF1, &b_HLT_QuadPFJet105_88_76_15_DoublePFBTagDeepJet_1p3_7p7_VBF1);
   // fChain->SetBranchStatus("HLT_QuadPFJet105_88_76_15_PFBTagDeepJet_1p3_VBF2", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet105_88_76_15_PFBTagDeepJet_1p3_VBF2", &HLT_QuadPFJet105_88_76_15_PFBTagDeepJet_1p3_VBF2, &b_HLT_QuadPFJet105_88_76_15_PFBTagDeepJet_1p3_VBF2);
   // fChain->SetBranchStatus("HLT_QuadPFJet111_90_80_15_DoublePFBTagDeepJet_1p3_7p7_VBF1", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet111_90_80_15_DoublePFBTagDeepJet_1p3_7p7_VBF1", &HLT_QuadPFJet111_90_80_15_DoublePFBTagDeepJet_1p3_7p7_VBF1, &b_HLT_QuadPFJet111_90_80_15_DoublePFBTagDeepJet_1p3_7p7_VBF1);
   // fChain->SetBranchStatus("HLT_QuadPFJet111_90_80_15_PFBTagDeepJet_1p3_VBF2", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet111_90_80_15_PFBTagDeepJet_1p3_VBF2", &HLT_QuadPFJet111_90_80_15_PFBTagDeepJet_1p3_VBF2, &b_HLT_QuadPFJet111_90_80_15_PFBTagDeepJet_1p3_VBF2);
   // fChain->SetBranchStatus("HLT_QuadPFJet98_83_71_15_DoublePFBTagDeepJet_1p3_7p7_VBF1", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet98_83_71_15_DoublePFBTagDeepJet_1p3_7p7_VBF1", &HLT_QuadPFJet98_83_71_15_DoublePFBTagDeepJet_1p3_7p7_VBF1, &b_HLT_QuadPFJet98_83_71_15_DoublePFBTagDeepJet_1p3_7p7_VBF1);
   // fChain->SetBranchStatus("HLT_QuadPFJet98_83_71_15_PFBTagDeepJet_1p3_VBF2", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet98_83_71_15_PFBTagDeepJet_1p3_VBF2", &HLT_QuadPFJet98_83_71_15_PFBTagDeepJet_1p3_VBF2, &b_HLT_QuadPFJet98_83_71_15_PFBTagDeepJet_1p3_VBF2);
   // fChain->SetBranchStatus("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30_PFBtagDeepJet_1p5", 1);
   // fChain->SetBranchAddress("HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30_PFBtagDeepJet_1p5", &HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30_PFBtagDeepJet_1p5, &b_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_PFDiJet30_PFBtagDeepJet_1p5);
   // fChain->SetBranchStatus("HLT_QuadPFJet70_50_40_30", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet70_50_40_30", &HLT_QuadPFJet70_50_40_30, &b_HLT_QuadPFJet70_50_40_30);
   // fChain->SetBranchStatus("HLT_QuadPFJet70_50_40_30_PFBTagParticleNet_2BTagSum0p65", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet70_50_40_30_PFBTagParticleNet_2BTagSum0p65", &HLT_QuadPFJet70_50_40_30_PFBTagParticleNet_2BTagSum0p65, &b_HLT_QuadPFJet70_50_40_30_PFBTagParticleNet_2BTagSum0p65);
   // fChain->SetBranchStatus("HLT_QuadPFJet70_50_40_35_PFBTagParticleNet_2BTagSum0p65", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet70_50_40_35_PFBTagParticleNet_2BTagSum0p65", &HLT_QuadPFJet70_50_40_35_PFBTagParticleNet_2BTagSum0p65, &b_HLT_QuadPFJet70_50_40_35_PFBTagParticleNet_2BTagSum0p65);
   // fChain->SetBranchStatus("HLT_QuadPFJet70_50_45_35_PFBTagParticleNet_2BTagSum0p65", 1);
   // fChain->SetBranchAddress("HLT_QuadPFJet70_50_45_35_PFBTagParticleNet_2BTagSum0p65", &HLT_QuadPFJet70_50_45_35_PFBTagParticleNet_2BTagSum0p65, &b_HLT_QuadPFJet70_50_45_35_PFBTagParticleNet_2BTagSum0p65);
   // fChain->SetBranchStatus("HLT_AK8PFJet230_SoftDropMass40", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet230_SoftDropMass40", &HLT_AK8PFJet230_SoftDropMass40, &b_HLT_AK8PFJet230_SoftDropMass40);
   // fChain->SetBranchStatus("HLT_AK8PFJet230_SoftDropMass40_PFAK8ParticleNetBB0p35", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet230_SoftDropMass40_PFAK8ParticleNetBB0p35", &HLT_AK8PFJet230_SoftDropMass40_PFAK8ParticleNetBB0p35, &b_HLT_AK8PFJet230_SoftDropMass40_PFAK8ParticleNetBB0p35);
   // fChain->SetBranchStatus("HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetBB0p35", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetBB0p35", &HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetBB0p35, &b_HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetBB0p35);
   // fChain->SetBranchStatus("HLT_AK8PFJet275_SoftDropMass40_PFAK8ParticleNetBB0p35", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet275_SoftDropMass40_PFAK8ParticleNetBB0p35", &HLT_AK8PFJet275_SoftDropMass40_PFAK8ParticleNetBB0p35, &b_HLT_AK8PFJet275_SoftDropMass40_PFAK8ParticleNetBB0p35);
   // fChain->SetBranchStatus("HLT_AK8PFJet400_SoftDropMass40", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet400_SoftDropMass40", &HLT_AK8PFJet400_SoftDropMass40, &b_HLT_AK8PFJet400_SoftDropMass40);
   // fChain->SetBranchStatus("HLT_AK8PFJet425_SoftDropMass40", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet425_SoftDropMass40", &HLT_AK8PFJet425_SoftDropMass40, &b_HLT_AK8PFJet425_SoftDropMass40);
   // fChain->SetBranchStatus("HLT_AK8PFJet450_SoftDropMass40", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet450_SoftDropMass40", &HLT_AK8PFJet450_SoftDropMass40, &b_HLT_AK8PFJet450_SoftDropMass40);
   // fChain->SetBranchStatus("HLT_AK8PFJet230_SoftDropMass40_PFAK8ParticleNetTauTau0p30", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet230_SoftDropMass40_PFAK8ParticleNetTauTau0p30", &HLT_AK8PFJet230_SoftDropMass40_PFAK8ParticleNetTauTau0p30, &b_HLT_AK8PFJet230_SoftDropMass40_PFAK8ParticleNetTauTau0p30);
   // fChain->SetBranchStatus("HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetTauTau0p30", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetTauTau0p30", &HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetTauTau0p30, &b_HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetTauTau0p30);
   // fChain->SetBranchStatus("HLT_AK8PFJet275_SoftDropMass40_PFAK8ParticleNetTauTau0p30", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet275_SoftDropMass40_PFAK8ParticleNetTauTau0p30", &HLT_AK8PFJet275_SoftDropMass40_PFAK8ParticleNetTauTau0p30, &b_HLT_AK8PFJet275_SoftDropMass40_PFAK8ParticleNetTauTau0p30);
   // fChain->SetBranchStatus("HLT_DoubleL2Mu10NoVtx_2Cha_VetoL3Mu0DxyMax1cm", 1);
   // fChain->SetBranchAddress("HLT_DoubleL2Mu10NoVtx_2Cha_VetoL3Mu0DxyMax1cm", &HLT_DoubleL2Mu10NoVtx_2Cha_VetoL3Mu0DxyMax1cm, &b_HLT_DoubleL2Mu10NoVtx_2Cha_VetoL3Mu0DxyMax1cm);
   // fChain->SetBranchStatus("HLT_DoubleL3Mu16_10NoVtx_DxyMin0p01cm", 1);
   // fChain->SetBranchAddress("HLT_DoubleL3Mu16_10NoVtx_DxyMin0p01cm", &HLT_DoubleL3Mu16_10NoVtx_DxyMin0p01cm, &b_HLT_DoubleL3Mu16_10NoVtx_DxyMin0p01cm);
   // fChain->SetBranchStatus("HLT_Mu20NoFiltersNoVtxDisplaced_Photon20_CaloCustomId", 1);
   // fChain->SetBranchAddress("HLT_Mu20NoFiltersNoVtxDisplaced_Photon20_CaloCustomId", &HLT_Mu20NoFiltersNoVtxDisplaced_Photon20_CaloCustomId, &b_HLT_Mu20NoFiltersNoVtxDisplaced_Photon20_CaloCustomId);
   // fChain->SetBranchStatus("HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1", &HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1, &b_HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1);
   // fChain->SetBranchStatus("HLT_HT430_DelayedJet40_DoubleDelay0p5nsTrackless", 1);
   // fChain->SetBranchAddress("HLT_HT430_DelayedJet40_DoubleDelay0p5nsTrackless", &HLT_HT430_DelayedJet40_DoubleDelay0p5nsTrackless, &b_HLT_HT430_DelayedJet40_DoubleDelay0p5nsTrackless);
   // fChain->SetBranchStatus("HLT_HT430_DelayedJet40_DoubleDelay1nsInclusive", 1);
   // fChain->SetBranchAddress("HLT_HT430_DelayedJet40_DoubleDelay1nsInclusive", &HLT_HT430_DelayedJet40_DoubleDelay1nsInclusive, &b_HLT_HT430_DelayedJet40_DoubleDelay1nsInclusive);
   // fChain->SetBranchStatus("HLT_HT430_DelayedJet40_SingleDelay1nsTrackless", 1);
   // fChain->SetBranchAddress("HLT_HT430_DelayedJet40_SingleDelay1nsTrackless", &HLT_HT430_DelayedJet40_SingleDelay1nsTrackless, &b_HLT_HT430_DelayedJet40_SingleDelay1nsTrackless);
   // fChain->SetBranchStatus("HLT_HT430_DelayedJet40_SingleDelay2nsInclusive", 1);
   // fChain->SetBranchAddress("HLT_HT430_DelayedJet40_SingleDelay2nsInclusive", &HLT_HT430_DelayedJet40_SingleDelay2nsInclusive, &b_HLT_HT430_DelayedJet40_SingleDelay2nsInclusive);
   // fChain->SetBranchStatus("HLT_L1Mu6HT240", 1);
   // fChain->SetBranchAddress("HLT_L1Mu6HT240", &HLT_L1Mu6HT240, &b_HLT_L1Mu6HT240);
   // fChain->SetBranchStatus("HLT_Mu6HT240_DisplacedDijet30_Inclusive0PtrkShortSig5", 1);
   // fChain->SetBranchAddress("HLT_Mu6HT240_DisplacedDijet30_Inclusive0PtrkShortSig5", &HLT_Mu6HT240_DisplacedDijet30_Inclusive0PtrkShortSig5, &b_HLT_Mu6HT240_DisplacedDijet30_Inclusive0PtrkShortSig5);
   // fChain->SetBranchStatus("HLT_Mu6HT240_DisplacedDijet30_Inclusive1PtrkShortSig5_DisplacedLoose", 1);
   // fChain->SetBranchAddress("HLT_Mu6HT240_DisplacedDijet30_Inclusive1PtrkShortSig5_DisplacedLoose", &HLT_Mu6HT240_DisplacedDijet30_Inclusive1PtrkShortSig5_DisplacedLoose, &b_HLT_Mu6HT240_DisplacedDijet30_Inclusive1PtrkShortSig5_DisplacedLoose);
   // fChain->SetBranchStatus("HLT_Mu6HT240_DisplacedDijet35_Inclusive0PtrkShortSig5", 1);
   // fChain->SetBranchAddress("HLT_Mu6HT240_DisplacedDijet35_Inclusive0PtrkShortSig5", &HLT_Mu6HT240_DisplacedDijet35_Inclusive0PtrkShortSig5, &b_HLT_Mu6HT240_DisplacedDijet35_Inclusive0PtrkShortSig5);
   // fChain->SetBranchStatus("HLT_Mu6HT240_DisplacedDijet35_Inclusive1PtrkShortSig5_DisplacedLoose", 1);
   // fChain->SetBranchAddress("HLT_Mu6HT240_DisplacedDijet35_Inclusive1PtrkShortSig5_DisplacedLoose", &HLT_Mu6HT240_DisplacedDijet35_Inclusive1PtrkShortSig5_DisplacedLoose, &b_HLT_Mu6HT240_DisplacedDijet35_Inclusive1PtrkShortSig5_DisplacedLoose);
   // fChain->SetBranchStatus("HLT_Mu6HT240_DisplacedDijet40_Inclusive0PtrkShortSig5", 1);
   // fChain->SetBranchAddress("HLT_Mu6HT240_DisplacedDijet40_Inclusive0PtrkShortSig5", &HLT_Mu6HT240_DisplacedDijet40_Inclusive0PtrkShortSig5, &b_HLT_Mu6HT240_DisplacedDijet40_Inclusive0PtrkShortSig5);
   // fChain->SetBranchStatus("HLT_Mu6HT240_DisplacedDijet40_Inclusive1PtrkShortSig5_DisplacedLoose", 1);
   // fChain->SetBranchAddress("HLT_Mu6HT240_DisplacedDijet40_Inclusive1PtrkShortSig5_DisplacedLoose", &HLT_Mu6HT240_DisplacedDijet40_Inclusive1PtrkShortSig5_DisplacedLoose, &b_HLT_Mu6HT240_DisplacedDijet40_Inclusive1PtrkShortSig5_DisplacedLoose);
   // fChain->SetBranchStatus("HLT_HT430_DisplacedDijet30_Inclusive1PtrkShortSig5", 1);
   // fChain->SetBranchAddress("HLT_HT430_DisplacedDijet30_Inclusive1PtrkShortSig5", &HLT_HT430_DisplacedDijet30_Inclusive1PtrkShortSig5, &b_HLT_HT430_DisplacedDijet30_Inclusive1PtrkShortSig5);
   // fChain->SetBranchStatus("HLT_HT430_DisplacedDijet35_Inclusive1PtrkShortSig5", 1);
   // fChain->SetBranchAddress("HLT_HT430_DisplacedDijet35_Inclusive1PtrkShortSig5", &HLT_HT430_DisplacedDijet35_Inclusive1PtrkShortSig5, &b_HLT_HT430_DisplacedDijet35_Inclusive1PtrkShortSig5);
   // fChain->SetBranchStatus("HLT_HT430_DisplacedDijet40_Inclusive1PtrkShortSig5", 1);
   // fChain->SetBranchAddress("HLT_HT430_DisplacedDijet40_Inclusive1PtrkShortSig5", &HLT_HT430_DisplacedDijet40_Inclusive1PtrkShortSig5, &b_HLT_HT430_DisplacedDijet40_Inclusive1PtrkShortSig5);
   // fChain->SetBranchStatus("HLT_CaloMET60_DTCluster50", 1);
   // fChain->SetBranchAddress("HLT_CaloMET60_DTCluster50", &HLT_CaloMET60_DTCluster50, &b_HLT_CaloMET60_DTCluster50);
   // fChain->SetBranchStatus("HLT_CaloMET60_DTClusterNoMB1S50", 1);
   // fChain->SetBranchAddress("HLT_CaloMET60_DTClusterNoMB1S50", &HLT_CaloMET60_DTClusterNoMB1S50, &b_HLT_CaloMET60_DTClusterNoMB1S50);
   // fChain->SetBranchStatus("HLT_L1MET_DTCluster50", 1);
   // fChain->SetBranchAddress("HLT_L1MET_DTCluster50", &HLT_L1MET_DTCluster50, &b_HLT_L1MET_DTCluster50);
   // fChain->SetBranchStatus("HLT_L1MET_DTClusterNoMB1S50", 1);
   // fChain->SetBranchAddress("HLT_L1MET_DTClusterNoMB1S50", &HLT_L1MET_DTClusterNoMB1S50, &b_HLT_L1MET_DTClusterNoMB1S50);
   // fChain->SetBranchStatus("HLT_CscCluster_Loose", 1);
   // fChain->SetBranchAddress("HLT_CscCluster_Loose", &HLT_CscCluster_Loose, &b_HLT_CscCluster_Loose);
   // fChain->SetBranchStatus("HLT_CscCluster_Medium", 1);
   // fChain->SetBranchAddress("HLT_CscCluster_Medium", &HLT_CscCluster_Medium, &b_HLT_CscCluster_Medium);
   // fChain->SetBranchStatus("HLT_CscCluster_Tight", 1);
   // fChain->SetBranchAddress("HLT_CscCluster_Tight", &HLT_CscCluster_Tight, &b_HLT_CscCluster_Tight);
   // fChain->SetBranchStatus("HLT_L1CSCShower_DTCluster50", 1);
   // fChain->SetBranchAddress("HLT_L1CSCShower_DTCluster50", &HLT_L1CSCShower_DTCluster50, &b_HLT_L1CSCShower_DTCluster50);
   // fChain->SetBranchStatus("HLT_L1CSCShower_DTCluster75", 1);
   // fChain->SetBranchAddress("HLT_L1CSCShower_DTCluster75", &HLT_L1CSCShower_DTCluster75, &b_HLT_L1CSCShower_DTCluster75);
   // fChain->SetBranchStatus("HLT_PFMET105_IsoTrk50", 1);
   // fChain->SetBranchAddress("HLT_PFMET105_IsoTrk50", &HLT_PFMET105_IsoTrk50, &b_HLT_PFMET105_IsoTrk50);
   // fChain->SetBranchStatus("HLT_PFMET105_PFJet100_looseRecoiling", 1);
   // fChain->SetBranchAddress("HLT_PFMET105_PFJet100_looseRecoiling", &HLT_PFMET105_PFJet100_looseRecoiling, &b_HLT_PFMET105_PFJet100_looseRecoiling);
   // fChain->SetBranchStatus("HLT_PFMET110_PFJet100", 1);
   // fChain->SetBranchAddress("HLT_PFMET110_PFJet100", &HLT_PFMET110_PFJet100, &b_HLT_PFMET110_PFJet100);
   // fChain->SetBranchStatus("HLT_PFMET110_PFJet100_looseRecoiling", 1);
   // fChain->SetBranchAddress("HLT_PFMET110_PFJet100_looseRecoiling", &HLT_PFMET110_PFJet100_looseRecoiling, &b_HLT_PFMET110_PFJet100_looseRecoiling);
   // fChain->SetBranchStatus("HLT_ExpressMuons", 1);
   // fChain->SetBranchAddress("HLT_ExpressMuons", &HLT_ExpressMuons, &b_HLT_ExpressMuons);
   // fChain->SetBranchStatus("HLT_OnlineMonitorGroup", 1);
   // fChain->SetBranchAddress("HLT_OnlineMonitorGroup", &HLT_OnlineMonitorGroup, &b_HLT_OnlineMonitorGroup);
   // fChain->SetBranchStatus("HLT_PPSMaxTracksPerArm1", 1);
   // fChain->SetBranchAddress("HLT_PPSMaxTracksPerArm1", &HLT_PPSMaxTracksPerArm1, &b_HLT_PPSMaxTracksPerArm1);
   // fChain->SetBranchStatus("HLT_PPSMaxTracksPerRP4", 1);
   // fChain->SetBranchAddress("HLT_PPSMaxTracksPerRP4", &HLT_PPSMaxTracksPerRP4, &b_HLT_PPSMaxTracksPerRP4);
   fChain->SetBranchStatus("HLTriggerFinalPath", 1);
   fChain->SetBranchAddress("HLTriggerFinalPath", &HLTriggerFinalPath, &b_HLTriggerFinalPath);
   
   Notify();

}

void MainEvent::InitSimulationVariables(TTree *tree){

   if (!tree) return;
   // fChain->SetBranchStatus("HTXS_njets25", 1);
   // fChain->SetBranchAddress("HTXS_njets25", &HTXS_njets25, &b_HTXS_njets25);
   // fChain->SetBranchStatus("HTXS_njets30", 1);
   // fChain->SetBranchAddress("HTXS_njets30", &HTXS_njets30, &b_HTXS_njets30);
   // fChain->SetBranchStatus("HTXS_stage1_1_cat_pTjet25GeV", 1);
   // fChain->SetBranchAddress("HTXS_stage1_1_cat_pTjet25GeV", &HTXS_stage1_1_cat_pTjet25GeV, &b_HTXS_stage1_1_cat_pTjet25GeV);
   // fChain->SetBranchStatus("HTXS_stage1_1_cat_pTjet30GeV", 1);
   // fChain->SetBranchAddress("HTXS_stage1_1_cat_pTjet30GeV", &HTXS_stage1_1_cat_pTjet30GeV, &b_HTXS_stage1_1_cat_pTjet30GeV);
   // fChain->SetBranchStatus("HTXS_stage1_1_fine_cat_pTjet25GeV", 1);
   // fChain->SetBranchAddress("HTXS_stage1_1_fine_cat_pTjet25GeV", &HTXS_stage1_1_fine_cat_pTjet25GeV, &b_HTXS_stage1_1_fine_cat_pTjet25GeV);
   // fChain->SetBranchStatus("HTXS_stage1_1_fine_cat_pTjet30GeV", 1);
   // fChain->SetBranchAddress("HTXS_stage1_1_fine_cat_pTjet30GeV", &HTXS_stage1_1_fine_cat_pTjet30GeV, &b_HTXS_stage1_1_fine_cat_pTjet30GeV);
   // fChain->SetBranchStatus("HTXS_stage1_2_cat_pTjet25GeV", 1);
   // fChain->SetBranchAddress("HTXS_stage1_2_cat_pTjet25GeV", &HTXS_stage1_2_cat_pTjet25GeV, &b_HTXS_stage1_2_cat_pTjet25GeV);
   // fChain->SetBranchStatus("HTXS_stage1_2_cat_pTjet30GeV", 1);
   // fChain->SetBranchAddress("HTXS_stage1_2_cat_pTjet30GeV", &HTXS_stage1_2_cat_pTjet30GeV, &b_HTXS_stage1_2_cat_pTjet30GeV);
   // fChain->SetBranchStatus("HTXS_stage1_2_fine_cat_pTjet25GeV", 1);
   // fChain->SetBranchAddress("HTXS_stage1_2_fine_cat_pTjet25GeV", &HTXS_stage1_2_fine_cat_pTjet25GeV, &b_HTXS_stage1_2_fine_cat_pTjet25GeV);
   // fChain->SetBranchStatus("HTXS_stage1_2_fine_cat_pTjet30GeV", 1);
   // fChain->SetBranchAddress("HTXS_stage1_2_fine_cat_pTjet30GeV", &HTXS_stage1_2_fine_cat_pTjet30GeV, &b_HTXS_stage1_2_fine_cat_pTjet30GeV);
   // fChain->SetBranchStatus("HTXS_stage_0", 1);
   // fChain->SetBranchAddress("HTXS_stage_0", &HTXS_stage_0, &b_HTXS_stage_0);
   // fChain->SetBranchStatus("HTXS_stage_1_pTjet25", 1);
   // fChain->SetBranchAddress("HTXS_stage_1_pTjet25", &HTXS_stage_1_pTjet25, &b_HTXS_stage_1_pTjet25);
   // fChain->SetBranchStatus("HTXS_stage_1_pTjet30", 1);
   // fChain->SetBranchAddress("HTXS_stage_1_pTjet30", &HTXS_stage_1_pTjet30, &b_HTXS_stage_1_pTjet30);
   // fChain->SetBranchStatus("HTXS_Higgs_pt", 1);
   // fChain->SetBranchAddress("HTXS_Higgs_pt", &HTXS_Higgs_pt, &b_HTXS_Higgs_pt);
   // fChain->SetBranchStatus("HTXS_Higgs_y", 1);
   // fChain->SetBranchAddress("HTXS_Higgs_y", &HTXS_Higgs_y, &b_HTXS_Higgs_y);
   // fChain->SetBranchStatus("nGenJetAK8", 1);
   // fChain->SetBranchAddress("nGenJetAK8", &nGenJetAK8, &b_nGenJetAK8);
   // fChain->SetBranchStatus("GenJetAK8_eta", 1);
   // fChain->SetBranchAddress("GenJetAK8_eta", GenJetAK8_eta, &b_GenJetAK8_eta);
   // fChain->SetBranchStatus("GenJetAK8_mass", 1);
   // fChain->SetBranchAddress("GenJetAK8_mass", GenJetAK8_mass, &b_GenJetAK8_mass);
   // fChain->SetBranchStatus("GenJetAK8_phi", 1);
   // fChain->SetBranchAddress("GenJetAK8_phi", GenJetAK8_phi, &b_GenJetAK8_phi);
   // fChain->SetBranchStatus("GenJetAK8_pt", 1);
   // fChain->SetBranchAddress("GenJetAK8_pt", GenJetAK8_pt, &b_GenJetAK8_pt);
   fChain->SetBranchStatus("nGenJet", 1);
   fChain->SetBranchAddress("nGenJet", &nGenJet, &b_nGenJet);
   fChain->SetBranchStatus("GenJet_eta", 1);
   fChain->SetBranchAddress("GenJet_eta", GenJet_eta, &b_GenJet_eta);
   fChain->SetBranchStatus("GenJet_mass", 1);
   fChain->SetBranchAddress("GenJet_mass", GenJet_mass, &b_GenJet_mass);
   fChain->SetBranchStatus("GenJet_phi", 1);
   fChain->SetBranchAddress("GenJet_phi", GenJet_phi, &b_GenJet_phi);
   fChain->SetBranchStatus("GenJet_pt", 1);
   fChain->SetBranchAddress("GenJet_pt", GenJet_pt, &b_GenJet_pt);
   fChain->SetBranchStatus("nGenPart", 1);
   fChain->SetBranchAddress("nGenPart", &nGenPart, &b_nGenPart);
   fChain->SetBranchStatus("GenPart_genPartIdxMother", 1);
   fChain->SetBranchAddress("GenPart_genPartIdxMother", GenPart_genPartIdxMother, &b_GenPart_genPartIdxMother);
   fChain->SetBranchStatus("GenPart_statusFlags", 1);
   fChain->SetBranchAddress("GenPart_statusFlags", GenPart_statusFlags, &b_GenPart_statusFlags);
   fChain->SetBranchStatus("GenPart_pdgId", 1);
   fChain->SetBranchAddress("GenPart_pdgId", GenPart_pdgId, &b_GenPart_pdgId);
   fChain->SetBranchStatus("GenPart_status", 1);
   fChain->SetBranchAddress("GenPart_status", GenPart_status, &b_GenPart_status);
   fChain->SetBranchStatus("GenPart_eta", 1);
   fChain->SetBranchAddress("GenPart_eta", GenPart_eta, &b_GenPart_eta);
   fChain->SetBranchStatus("GenPart_mass", 1);
   fChain->SetBranchAddress("GenPart_mass", GenPart_mass, &b_GenPart_mass);
   fChain->SetBranchStatus("GenPart_phi", 1);
   fChain->SetBranchAddress("GenPart_phi", GenPart_phi, &b_GenPart_phi);
   fChain->SetBranchStatus("GenPart_pt", 1);
   fChain->SetBranchAddress("GenPart_pt", GenPart_pt, &b_GenPart_pt);
   // fChain->SetBranchStatus("nGenProton", 1);
   // fChain->SetBranchAddress("nGenProton", &nGenProton, &b_nGenProton);
   // fChain->SetBranchStatus("GenProton_isPU", 1);
   // fChain->SetBranchAddress("GenProton_isPU", GenProton_isPU, &b_GenProton_isPU);
   // fChain->SetBranchStatus("GenProton_px", 1);
   // fChain->SetBranchAddress("GenProton_px", GenProton_px, &b_GenProton_px);
   // fChain->SetBranchStatus("GenProton_py", 1);
   // fChain->SetBranchAddress("GenProton_py", GenProton_py, &b_GenProton_py);
   // fChain->SetBranchStatus("GenProton_pz", 1);
   // fChain->SetBranchAddress("GenProton_pz", GenProton_pz, &b_GenProton_pz);
   // fChain->SetBranchStatus("GenProton_vz", 1);
   // fChain->SetBranchAddress("GenProton_vz", GenProton_vz, &b_GenProton_vz);
   // fChain->SetBranchStatus("nSubGenJetAK8", 1);
   // fChain->SetBranchAddress("nSubGenJetAK8", &nSubGenJetAK8, &b_nSubGenJetAK8);
   // fChain->SetBranchStatus("SubGenJetAK8_eta", 1);
   // fChain->SetBranchAddress("SubGenJetAK8_eta", SubGenJetAK8_eta, &b_SubGenJetAK8_eta);
   // fChain->SetBranchStatus("SubGenJetAK8_mass", 1);
   // fChain->SetBranchAddress("SubGenJetAK8_mass", SubGenJetAK8_mass, &b_SubGenJetAK8_mass);
   // fChain->SetBranchStatus("SubGenJetAK8_phi", 1);
   // fChain->SetBranchAddress("SubGenJetAK8_phi", SubGenJetAK8_phi, &b_SubGenJetAK8_phi);
   // fChain->SetBranchStatus("SubGenJetAK8_pt", 1);
   // fChain->SetBranchAddress("SubGenJetAK8_pt", SubGenJetAK8_pt, &b_SubGenJetAK8_pt);
   // fChain->SetBranchStatus("Generator_id1", 1);
   // fChain->SetBranchAddress("Generator_id1", &Generator_id1, &b_Generator_id1);
   // fChain->SetBranchStatus("Generator_id2", 1);
   // fChain->SetBranchAddress("Generator_id2", &Generator_id2, &b_Generator_id2);
   // fChain->SetBranchStatus("Generator_binvar", 1);
   // fChain->SetBranchAddress("Generator_binvar", &Generator_binvar, &b_Generator_binvar);
   // fChain->SetBranchStatus("Generator_scalePDF", 1);
   // fChain->SetBranchAddress("Generator_scalePDF", &Generator_scalePDF, &b_Generator_scalePDF);
   // fChain->SetBranchStatus("Generator_weight", 1);
   // fChain->SetBranchAddress("Generator_weight", &Generator_weight, &b_Generator_weight);
   // fChain->SetBranchStatus("Generator_x1", 1);
   // fChain->SetBranchAddress("Generator_x1", &Generator_x1, &b_Generator_x1);
   // fChain->SetBranchStatus("Generator_x2", 1);
   // fChain->SetBranchAddress("Generator_x2", &Generator_x2, &b_Generator_x2);
   // fChain->SetBranchStatus("Generator_xpdf1", 1);
   // fChain->SetBranchAddress("Generator_xpdf1", &Generator_xpdf1, &b_Generator_xpdf1);
   // fChain->SetBranchStatus("Generator_xpdf2", 1);
   // fChain->SetBranchAddress("Generator_xpdf2", &Generator_xpdf2, &b_Generator_xpdf2);
   // fChain->SetBranchStatus("GenVtx_x", 1);
   // fChain->SetBranchAddress("GenVtx_x", &GenVtx_x, &b_GenVtx_x);
   // fChain->SetBranchStatus("GenVtx_y", 1);
   // fChain->SetBranchAddress("GenVtx_y", &GenVtx_y, &b_GenVtx_y);
   // fChain->SetBranchStatus("GenVtx_z", 1);
   // fChain->SetBranchAddress("GenVtx_z", &GenVtx_z, &b_GenVtx_z);
   // fChain->SetBranchStatus("nGenVisTau", 1);
   // fChain->SetBranchAddress("nGenVisTau", &nGenVisTau, &b_nGenVisTau);
   // fChain->SetBranchStatus("GenVisTau_status", 1);
   // fChain->SetBranchAddress("GenVisTau_status", GenVisTau_status, &b_GenVisTau_status);
   // fChain->SetBranchStatus("GenVisTau_charge", 1);
   // fChain->SetBranchAddress("GenVisTau_charge", GenVisTau_charge, &b_GenVisTau_charge);
   // fChain->SetBranchStatus("GenVisTau_genPartIdxMother", 1);
   // fChain->SetBranchAddress("GenVisTau_genPartIdxMother", GenVisTau_genPartIdxMother, &b_GenVisTau_genPartIdxMother);
   // fChain->SetBranchStatus("GenVisTau_eta", 1);
   // fChain->SetBranchAddress("GenVisTau_eta", GenVisTau_eta, &b_GenVisTau_eta);
   // fChain->SetBranchStatus("GenVisTau_mass", 1);
   // fChain->SetBranchAddress("GenVisTau_mass", GenVisTau_mass, &b_GenVisTau_mass);
   // fChain->SetBranchStatus("GenVisTau_phi", 1);
   // fChain->SetBranchAddress("GenVisTau_phi", GenVisTau_phi, &b_GenVisTau_phi);
   // fChain->SetBranchStatus("GenVisTau_pt", 1);
   // fChain->SetBranchAddress("GenVisTau_pt", GenVisTau_pt, &b_GenVisTau_pt);
   fChain->SetBranchStatus("genWeight", 1);
   fChain->SetBranchAddress("genWeight", &genWeight, &b_genWeight);
   // fChain->SetBranchStatus("LHEWeight_originalXWGTUP", 1);
   // fChain->SetBranchAddress("LHEWeight_originalXWGTUP", &LHEWeight_originalXWGTUP, &b_LHEWeight_originalXWGTUP);
   // fChain->SetBranchStatus("nLHEPdfWeight", 1);
   // fChain->SetBranchAddress("nLHEPdfWeight", &nLHEPdfWeight, &b_nLHEPdfWeight);
   // fChain->SetBranchStatus("LHEPdfWeight", 1);
   // fChain->SetBranchAddress("LHEPdfWeight", LHEPdfWeight, &b_LHEPdfWeight);
   // fChain->SetBranchStatus("nLHEReweightingWeight", 1);
   // fChain->SetBranchAddress("nLHEReweightingWeight", &nLHEReweightingWeight, &b_nLHEReweightingWeight);
   // fChain->SetBranchStatus("LHEReweightingWeight", 1);
   // fChain->SetBranchAddress("LHEReweightingWeight", &LHEReweightingWeight, &b_LHEReweightingWeight);
   // fChain->SetBranchStatus("nLHEScaleWeight", 1);
   // fChain->SetBranchAddress("nLHEScaleWeight", &nLHEScaleWeight, &b_nLHEScaleWeight);
   // fChain->SetBranchStatus("LHEScaleWeight", 1);
   // fChain->SetBranchAddress("LHEScaleWeight", LHEScaleWeight, &b_LHEScaleWeight);
   // fChain->SetBranchStatus("nPSWeight", 1);
   // fChain->SetBranchAddress("nPSWeight", &nPSWeight, &b_nPSWeight);
   // fChain->SetBranchStatus("PSWeight", 1);
   // fChain->SetBranchAddress("PSWeight", PSWeight, &b_PSWeight);
   // fChain->SetBranchStatus("LHE_Njets", 1);
   // fChain->SetBranchAddress("LHE_Njets", &LHE_Njets, &b_LHE_Njets);
   // fChain->SetBranchStatus("LHE_Nb", 1);
   // fChain->SetBranchAddress("LHE_Nb", &LHE_Nb, &b_LHE_Nb);
   // fChain->SetBranchStatus("LHE_Nc", 1);
   // fChain->SetBranchAddress("LHE_Nc", &LHE_Nc, &b_LHE_Nc);
   // fChain->SetBranchStatus("LHE_Nuds", 1);
   // fChain->SetBranchAddress("LHE_Nuds", &LHE_Nuds, &b_LHE_Nuds);
   // fChain->SetBranchStatus("LHE_Nglu", 1);
   // fChain->SetBranchAddress("LHE_Nglu", &LHE_Nglu, &b_LHE_Nglu);
   // fChain->SetBranchStatus("LHE_NpNLO", 1);
   // fChain->SetBranchAddress("LHE_NpNLO", &LHE_NpNLO, &b_LHE_NpNLO);
   // fChain->SetBranchStatus("LHE_NpLO", 1);
   // fChain->SetBranchAddress("LHE_NpLO", &LHE_NpLO, &b_LHE_NpLO);
   // fChain->SetBranchStatus("LHE_HT", 1);
   // fChain->SetBranchAddress("LHE_HT", &LHE_HT, &b_LHE_HT);
   // fChain->SetBranchStatus("LHE_HTIncoming", 1);
   // fChain->SetBranchAddress("LHE_HTIncoming", &LHE_HTIncoming, &b_LHE_HTIncoming);
   // fChain->SetBranchStatus("LHE_Vpt", 1);
   // fChain->SetBranchAddress("LHE_Vpt", &LHE_Vpt, &b_LHE_Vpt);
   // fChain->SetBranchStatus("LHE_AlphaS", 1);
   // fChain->SetBranchAddress("LHE_AlphaS", &LHE_AlphaS, &b_LHE_AlphaS);
   // fChain->SetBranchStatus("nLHEPart", 1);
   // fChain->SetBranchAddress("nLHEPart", &nLHEPart, &b_nLHEPart);
   // fChain->SetBranchStatus("LHEPart_pdgId", 1);
   // fChain->SetBranchAddress("LHEPart_pdgId", LHEPart_pdgId, &b_LHEPart_pdgId);
   // fChain->SetBranchStatus("LHEPart_status", 1);
   // fChain->SetBranchAddress("LHEPart_status", LHEPart_status, &b_LHEPart_status);
   // fChain->SetBranchStatus("LHEPart_spin", 1);
   // fChain->SetBranchAddress("LHEPart_spin", LHEPart_spin, &b_LHEPart_spin);
   // fChain->SetBranchStatus("LHEPart_pt", 1);
   // fChain->SetBranchAddress("LHEPart_pt", LHEPart_pt, &b_LHEPart_pt);
   // fChain->SetBranchStatus("LHEPart_eta", 1);
   // fChain->SetBranchAddress("LHEPart_eta", LHEPart_eta, &b_LHEPart_eta);
   // fChain->SetBranchStatus("LHEPart_phi", 1);
   // fChain->SetBranchAddress("LHEPart_phi", LHEPart_phi, &b_LHEPart_phi);
   // fChain->SetBranchStatus("LHEPart_mass", 1);
   // fChain->SetBranchAddress("LHEPart_mass", LHEPart_mass, &b_LHEPart_mass);
   // fChain->SetBranchStatus("LHEPart_incomingpz", 1);
   // fChain->SetBranchAddress("LHEPart_incomingpz", LHEPart_incomingpz, &b_LHEPart_incomingpz);
   fChain->SetBranchStatus("GenMET_phi", 1);
   fChain->SetBranchAddress("GenMET_phi", &GenMET_phi, &b_GenMET_phi);
   fChain->SetBranchStatus("GenMET_pt", 1);
   fChain->SetBranchAddress("GenMET_pt", &GenMET_pt, &b_GenMET_pt);
   fChain->SetBranchStatus("Pileup_nPU", 1);
   fChain->SetBranchAddress("Pileup_nPU", &Pileup_nPU, &b_Pileup_nPU);
   fChain->SetBranchStatus("Pileup_sumEOOT", 1);
   fChain->SetBranchAddress("Pileup_sumEOOT", &Pileup_sumEOOT, &b_Pileup_sumEOOT);
   fChain->SetBranchStatus("Pileup_sumLOOT", 1);
   fChain->SetBranchAddress("Pileup_sumLOOT", &Pileup_sumLOOT, &b_Pileup_sumLOOT);
   fChain->SetBranchStatus("Pileup_nTrueInt", 1);
   fChain->SetBranchAddress("Pileup_nTrueInt", &Pileup_nTrueInt, &b_Pileup_nTrueInt);
   fChain->SetBranchStatus("Pileup_pudensity", 1);
   fChain->SetBranchAddress("Pileup_pudensity", &Pileup_pudensity, &b_Pileup_pudensity);
   fChain->SetBranchStatus("Pileup_gpudensity", 1);
   fChain->SetBranchAddress("Pileup_gpudensity", &Pileup_gpudensity, &b_Pileup_gpudensity);
   fChain->SetBranchStatus("nGenDressedLepton", 1);
   fChain->SetBranchAddress("nGenDressedLepton", &nGenDressedLepton, &b_nGenDressedLepton);
   fChain->SetBranchStatus("GenDressedLepton_hasTauAnc", 1);
   fChain->SetBranchAddress("GenDressedLepton_hasTauAnc", GenDressedLepton_hasTauAnc, &b_GenDressedLepton_hasTauAnc);
   fChain->SetBranchStatus("GenDressedLepton_pdgId", 1);
   fChain->SetBranchAddress("GenDressedLepton_pdgId", GenDressedLepton_pdgId, &b_GenDressedLepton_pdgId);
   fChain->SetBranchStatus("GenDressedLepton_eta", 1);
   fChain->SetBranchAddress("GenDressedLepton_eta", GenDressedLepton_eta, &b_GenDressedLepton_eta);
   fChain->SetBranchStatus("GenDressedLepton_mass", 1);
   fChain->SetBranchAddress("GenDressedLepton_mass", GenDressedLepton_mass, &b_GenDressedLepton_mass);
   fChain->SetBranchStatus("GenDressedLepton_phi", 1);
   fChain->SetBranchAddress("GenDressedLepton_phi", GenDressedLepton_phi, &b_GenDressedLepton_phi);
   fChain->SetBranchStatus("GenDressedLepton_pt", 1);
   fChain->SetBranchAddress("GenDressedLepton_pt", GenDressedLepton_pt, &b_GenDressedLepton_pt);
   // fChain->SetBranchStatus("nGenIsolatedPhoton", 1);
   // fChain->SetBranchAddress("nGenIsolatedPhoton", &nGenIsolatedPhoton, &b_nGenIsolatedPhoton);
   // fChain->SetBranchStatus("GenIsolatedPhoton_eta", 1);
   // fChain->SetBranchAddress("GenIsolatedPhoton_eta", GenIsolatedPhoton_eta, &b_GenIsolatedPhoton_eta);
   // fChain->SetBranchStatus("GenIsolatedPhoton_mass", 1);
   // fChain->SetBranchAddress("GenIsolatedPhoton_mass", GenIsolatedPhoton_mass, &b_GenIsolatedPhoton_mass);
   // fChain->SetBranchStatus("GenIsolatedPhoton_phi", 1);
   // fChain->SetBranchAddress("GenIsolatedPhoton_phi", GenIsolatedPhoton_phi, &b_GenIsolatedPhoton_phi);
   // fChain->SetBranchStatus("GenIsolatedPhoton_pt", 1);
   // fChain->SetBranchAddress("GenIsolatedPhoton_pt", GenIsolatedPhoton_pt, &b_GenIsolatedPhoton_pt);
   fChain->SetBranchStatus("genTtbarId", 1);
   fChain->SetBranchAddress("genTtbarId", &genTtbarId, &b_genTtbarId);
   // fChain->SetBranchStatus("boostedTau_genPartFlav", 1);
   // fChain->SetBranchAddress("boostedTau_genPartFlav", boostedTau_genPartFlav, &b_boostedTau_genPartFlav);
   // fChain->SetBranchStatus("boostedTau_genPartIdx", 1);
   // fChain->SetBranchAddress("boostedTau_genPartIdx", boostedTau_genPartIdx, &b_boostedTau_genPartIdx);
   fChain->SetBranchStatus("Electron_genPartFlav", 1);
   fChain->SetBranchAddress("Electron_genPartFlav", Electron_genPartFlav, &b_Electron_genPartFlav);
   fChain->SetBranchStatus("Electron_genPartIdx", 1);
   fChain->SetBranchAddress("Electron_genPartIdx", Electron_genPartIdx, &b_Electron_genPartIdx);
   fChain->SetBranchStatus("FatJet_hadronFlavour", 1);
   fChain->SetBranchAddress("FatJet_hadronFlavour", FatJet_hadronFlavour, &b_FatJet_hadronFlavour);
   //fChain->SetBranchStatus("FatJet_nBHadrons", 1);
   //fChain->SetBranchAddress("FatJet_nBHadrons", FatJet_nBHadrons, &b_FatJet_nBHadrons);
   //fChain->SetBranchStatus("FatJet_nCHadrons", 1);
   //fChain->SetBranchAddress("FatJet_nCHadrons", FatJet_nCHadrons, &b_FatJet_nCHadrons);
   // fChain->SetBranchStatus("FatJet_genJetAK8Idx", 1);
   // fChain->SetBranchAddress("FatJet_genJetAK8Idx", FatJet_genJetAK8Idx, &b_FatJet_genJetAK8Idx);
   // fChain->SetBranchStatus("GenJetAK8_hadronFlavour", 1);
   // fChain->SetBranchAddress("GenJetAK8_hadronFlavour", GenJetAK8_hadronFlavour, &b_GenJetAK8_hadronFlavour);
   // fChain->SetBranchStatus("GenJetAK8_partonFlavour", 1);
   // fChain->SetBranchAddress("GenJetAK8_partonFlavour", GenJetAK8_partonFlavour, &b_GenJetAK8_partonFlavour);
   fChain->SetBranchStatus("GenJet_hadronFlavour", 1);
   fChain->SetBranchAddress("GenJet_hadronFlavour", GenJet_hadronFlavour, &b_GenJet_hadronFlavour);
   fChain->SetBranchStatus("GenJet_partonFlavour", 1);
   fChain->SetBranchAddress("GenJet_partonFlavour", GenJet_partonFlavour, &b_GenJet_partonFlavour);
   // fChain->SetBranchStatus("GenVtx_t0", 1);
   // fChain->SetBranchAddress("GenVtx_t0", &GenVtx_t0, &b_GenVtx_t0);
   fChain->SetBranchStatus("Jet_hadronFlavour", 1);
   fChain->SetBranchAddress("Jet_hadronFlavour", Jet_hadronFlavour, &b_Jet_hadronFlavour);
   fChain->SetBranchStatus("Jet_genJetIdx", 1);
   fChain->SetBranchAddress("Jet_genJetIdx", Jet_genJetIdx, &b_Jet_genJetIdx);
   fChain->SetBranchStatus("Jet_partonFlavour", 1);
   fChain->SetBranchAddress("Jet_partonFlavour", Jet_partonFlavour, &b_Jet_partonFlavour);
   // fChain->SetBranchStatus("LowPtElectron_genPartFlav", 1);
   // fChain->SetBranchAddress("LowPtElectron_genPartFlav", LowPtElectron_genPartFlav, &b_LowPtElectron_genPartFlav);
   // fChain->SetBranchStatus("LowPtElectron_genPartIdx", 1);
   // fChain->SetBranchAddress("LowPtElectron_genPartIdx", LowPtElectron_genPartIdx, &b_LowPtElectron_genPartIdx);
   fChain->SetBranchStatus("Muon_genPartFlav", 1);
   fChain->SetBranchAddress("Muon_genPartFlav", Muon_genPartFlav, &b_Muon_genPartFlav);
   fChain->SetBranchStatus("Muon_genPartIdx", 1);
   fChain->SetBranchAddress("Muon_genPartIdx", Muon_genPartIdx, &b_Muon_genPartIdx);
   // fChain->SetBranchStatus("Photon_genPartFlav", 1);
   // fChain->SetBranchAddress("Photon_genPartFlav", Photon_genPartFlav, &b_Photon_genPartFlav);
   // fChain->SetBranchStatus("Photon_genPartIdx", 1);
   // fChain->SetBranchAddress("Photon_genPartIdx", Photon_genPartIdx, &b_Photon_genPartIdx);
   //fChain->SetBranchStatus("MET_fiducialGenPhi", 1);
   //fChain->SetBranchAddress("MET_fiducialGenPhi", &MET_fiducialGenPhi, &b_MET_fiducialGenPhi);
   //fChain->SetBranchStatus("MET_fiducialGenPt", 1);
   //fChain->SetBranchAddress("MET_fiducialGenPt", &MET_fiducialGenPt, &b_MET_fiducialGenPt);
   fChain->SetBranchStatus("SubJet_hadronFlavour", 1);
   fChain->SetBranchAddress("SubJet_hadronFlavour", SubJet_hadronFlavour, &b_SubJet_hadronFlavour);
   fChain->SetBranchStatus("SubJet_nBHadrons", 1);
   fChain->SetBranchAddress("SubJet_nBHadrons", SubJet_nBHadrons, &b_SubJet_nBHadrons);
   fChain->SetBranchStatus("SubJet_nCHadrons", 1);
   fChain->SetBranchAddress("SubJet_nCHadrons", SubJet_nCHadrons, &b_SubJet_nCHadrons);
   fChain->SetBranchStatus("Tau_genPartFlav", 1);
   fChain->SetBranchAddress("Tau_genPartFlav", Tau_genPartFlav, &b_Tau_genPartFlav);
   fChain->SetBranchStatus("Tau_genPartIdx", 1);
   fChain->SetBranchAddress("Tau_genPartIdx", Tau_genPartIdx, &b_Tau_genPartIdx);
   // fChain->SetBranchStatus("L1_DoubleMu3_SQ_ETMHF30_HTT60er", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3_SQ_ETMHF30_HTT60er", &L1_DoubleMu3_SQ_ETMHF30_HTT60er, &b_L1_DoubleMu3_SQ_ETMHF30_HTT60er);
   // fChain->SetBranchStatus("L1_DoubleMu3_SQ_ETMHF30_Jet60er2p5_OR_DoubleJet40er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3_SQ_ETMHF30_Jet60er2p5_OR_DoubleJet40er2p5", &L1_DoubleMu3_SQ_ETMHF30_Jet60er2p5_OR_DoubleJet40er2p5, &b_L1_DoubleMu3_SQ_ETMHF30_Jet60er2p5_OR_DoubleJet40er2p5);
   // fChain->SetBranchStatus("L1_DoubleMu3_SQ_ETMHF40_HTT60er", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3_SQ_ETMHF40_HTT60er", &L1_DoubleMu3_SQ_ETMHF40_HTT60er, &b_L1_DoubleMu3_SQ_ETMHF40_HTT60er);
   // fChain->SetBranchStatus("L1_DoubleMu3_SQ_ETMHF40_Jet60er2p5_OR_DoubleJet40er2p5", 1);
   // fChain->SetBranchAddress("L1_DoubleMu3_SQ_ETMHF40_Jet60er2p5_OR_DoubleJet40er2p5", &L1_DoubleMu3_SQ_ETMHF40_Jet60er2p5_OR_DoubleJet40er2p5, &b_L1_DoubleMu3_SQ_ETMHF40_Jet60er2p5_OR_DoubleJet40er2p5);
   // fChain->SetBranchStatus("L1_ETMHF70", 1);
   // fChain->SetBranchAddress("L1_ETMHF70", &L1_ETMHF70, &b_L1_ETMHF70);
   // fChain->SetBranchStatus("L1_ETMHF70_HTT60er", 1);
   // fChain->SetBranchAddress("L1_ETMHF70_HTT60er", &L1_ETMHF70_HTT60er, &b_L1_ETMHF70_HTT60er);
   // fChain->SetBranchStatus("L1_ETMHF80", 1);
   // fChain->SetBranchAddress("L1_ETMHF80", &L1_ETMHF80, &b_L1_ETMHF80);
   // fChain->SetBranchStatus("L1_ETMHF80_HTT60er", 1);
   // fChain->SetBranchAddress("L1_ETMHF80_HTT60er", &L1_ETMHF80_HTT60er, &b_L1_ETMHF80_HTT60er);
   // fChain->SetBranchStatus("L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p1", 1);
   // fChain->SetBranchAddress("L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p1", &L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p1, &b_L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p1);
   // fChain->SetBranchStatus("L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p6", 1);
   // fChain->SetBranchAddress("L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p6", &L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p6, &b_L1_ETMHF80_SingleJet55er2p5_dPhi_Min2p6);
   // fChain->SetBranchStatus("L1_ETMHF90", 1);
   // fChain->SetBranchAddress("L1_ETMHF90", &L1_ETMHF90, &b_L1_ETMHF90);
   // fChain->SetBranchStatus("L1_Mu3er1p5_Jet100er2p5_ETMHF30", 1);
   // fChain->SetBranchAddress("L1_Mu3er1p5_Jet100er2p5_ETMHF30", &L1_Mu3er1p5_Jet100er2p5_ETMHF30, &b_L1_Mu3er1p5_Jet100er2p5_ETMHF30);
   fChain->SetBranchStatus("L1simulation_step", 1);
   fChain->SetBranchAddress("L1simulation_step", &L1simulation_step, &b_L1simulation_step);
   // fChain->SetBranchStatus("HLT_AK8PFJet400_MassSD30", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet400_MassSD30", &HLT_AK8PFJet400_MassSD30, &b_HLT_AK8PFJet400_MassSD30);
   // fChain->SetBranchStatus("HLT_AK8PFJet420_MassSD30", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet420_MassSD30", &HLT_AK8PFJet420_MassSD30, &b_HLT_AK8PFJet420_MassSD30);
   // fChain->SetBranchStatus("HLT_AK8PFJet450_MassSD30", 1);
   // fChain->SetBranchAddress("HLT_AK8PFJet450_MassSD30", &HLT_AK8PFJet450_MassSD30, &b_HLT_AK8PFJet450_MassSD30);
   // fChain->SetBranchStatus("HLT_AK8DiPFJet250_250_MassSD30", 1);
   // fChain->SetBranchAddress("HLT_AK8DiPFJet250_250_MassSD30", &HLT_AK8DiPFJet250_250_MassSD30, &b_HLT_AK8DiPFJet250_250_MassSD30);
   // fChain->SetBranchStatus("HLT_AK8DiPFJet250_250_MassSD50", 1);
   // fChain->SetBranchAddress("HLT_AK8DiPFJet250_250_MassSD50", &HLT_AK8DiPFJet250_250_MassSD50, &b_HLT_AK8DiPFJet250_250_MassSD50);
   // fChain->SetBranchStatus("HLT_AK8DiPFJet260_260_MassSD30", 1);
   // fChain->SetBranchAddress("HLT_AK8DiPFJet260_260_MassSD30", &HLT_AK8DiPFJet260_260_MassSD30, &b_HLT_AK8DiPFJet260_260_MassSD30);
   // fChain->SetBranchStatus("HLT_AK8DiPFJet270_270_MassSD30", 1);
   // fChain->SetBranchAddress("HLT_AK8DiPFJet270_270_MassSD30", &HLT_AK8DiPFJet270_270_MassSD30, &b_HLT_AK8DiPFJet270_270_MassSD30);
   // fChain->SetBranchStatus("HLT_DoubleMu4_3_Photon4_BsToMMG", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu4_3_Photon4_BsToMMG", &HLT_DoubleMu4_3_Photon4_BsToMMG, &b_HLT_DoubleMu4_3_Photon4_BsToMMG);
   // fChain->SetBranchStatus("HLT_DoubleMu4_3_Displaced_Photon4_BsToMMG", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu4_3_Displaced_Photon4_BsToMMG", &HLT_DoubleMu4_3_Displaced_Photon4_BsToMMG, &b_HLT_DoubleMu4_3_Displaced_Photon4_BsToMMG);
   // fChain->SetBranchStatus("HLT_IsoMu27_LooseChargedIsoPFTau20_Trk1_eta2p1_SingleL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu27_LooseChargedIsoPFTau20_Trk1_eta2p1_SingleL1", &HLT_IsoMu27_LooseChargedIsoPFTau20_Trk1_eta2p1_SingleL1, &b_HLT_IsoMu27_LooseChargedIsoPFTau20_Trk1_eta2p1_SingleL1);
   // fChain->SetBranchStatus("HLT_DiPFJet15_NoCaloMatched", 1);
   // fChain->SetBranchAddress("HLT_DiPFJet15_NoCaloMatched", &HLT_DiPFJet15_NoCaloMatched, &b_HLT_DiPFJet15_NoCaloMatched);
   // fChain->SetBranchStatus("HLT_DiPFJet25_NoCaloMatched", 1);
   // fChain->SetBranchAddress("HLT_DiPFJet25_NoCaloMatched", &HLT_DiPFJet25_NoCaloMatched, &b_HLT_DiPFJet25_NoCaloMatched);
   // fChain->SetBranchStatus("HLT_DiPFJet15_FBEta3_NoCaloMatched", 1);
   // fChain->SetBranchAddress("HLT_DiPFJet15_FBEta3_NoCaloMatched", &HLT_DiPFJet15_FBEta3_NoCaloMatched, &b_HLT_DiPFJet15_FBEta3_NoCaloMatched);
   // fChain->SetBranchStatus("HLT_DiPFJet25_FBEta3_NoCaloMatched", 1);
   // fChain->SetBranchAddress("HLT_DiPFJet25_FBEta3_NoCaloMatched", &HLT_DiPFJet25_FBEta3_NoCaloMatched, &b_HLT_DiPFJet25_FBEta3_NoCaloMatched);
   // fChain->SetBranchStatus("HLT_DiPFJetAve15_HFJEC", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve15_HFJEC", &HLT_DiPFJetAve15_HFJEC, &b_HLT_DiPFJetAve15_HFJEC);
   // fChain->SetBranchStatus("HLT_DiPFJetAve25_HFJEC", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve25_HFJEC", &HLT_DiPFJetAve25_HFJEC, &b_HLT_DiPFJetAve25_HFJEC);
   // fChain->SetBranchStatus("HLT_DiPFJetAve35_HFJEC", 1);
   // fChain->SetBranchAddress("HLT_DiPFJetAve35_HFJEC", &HLT_DiPFJetAve35_HFJEC, &b_HLT_DiPFJetAve35_HFJEC);
   // fChain->SetBranchStatus("HLT_PFMETNoMu110_PFMHTNoMu110_IDTight_FilterHF", 1);
   // fChain->SetBranchAddress("HLT_PFMETNoMu110_PFMHTNoMu110_IDTight_FilterHF", &HLT_PFMETNoMu110_PFMHTNoMu110_IDTight_FilterHF, &b_HLT_PFMETNoMu110_PFMHTNoMu110_IDTight_FilterHF);
   // fChain->SetBranchStatus("HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_FilterHF", 1);
   // fChain->SetBranchAddress("HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_FilterHF", &HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_FilterHF, &b_HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_FilterHF);
   // fChain->SetBranchStatus("HLT_PFMETNoMu130_PFMHTNoMu130_IDTight_FilterHF", 1);
   // fChain->SetBranchAddress("HLT_PFMETNoMu130_PFMHTNoMu130_IDTight_FilterHF", &HLT_PFMETNoMu130_PFMHTNoMu130_IDTight_FilterHF, &b_HLT_PFMETNoMu130_PFMHTNoMu130_IDTight_FilterHF);
   // fChain->SetBranchStatus("HLT_PFMETNoMu140_PFMHTNoMu140_IDTight_FilterHF", 1);
   // fChain->SetBranchAddress("HLT_PFMETNoMu140_PFMHTNoMu140_IDTight_FilterHF", &HLT_PFMETNoMu140_PFMHTNoMu140_IDTight_FilterHF, &b_HLT_PFMETNoMu140_PFMHTNoMu140_IDTight_FilterHF);
   // fChain->SetBranchStatus("HLT_Photon30EB_TightID_TightIso", 1);
   // fChain->SetBranchAddress("HLT_Photon30EB_TightID_TightIso", &HLT_Photon30EB_TightID_TightIso, &b_HLT_Photon30EB_TightID_TightIso);
   // fChain->SetBranchStatus("HLT_Photon90_CaloIdL_PFHT700", 1);
   // fChain->SetBranchAddress("HLT_Photon90_CaloIdL_PFHT700", &HLT_Photon90_CaloIdL_PFHT700, &b_HLT_Photon90_CaloIdL_PFHT700);
   // fChain->SetBranchStatus("HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_Mass55", 1);
   // fChain->SetBranchAddress("HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_Mass55", &HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_Mass55, &b_HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_Mass55);
   // fChain->SetBranchStatus("HLT_DoubleMu4_JpsiTrk_Bc", 1);
   // fChain->SetBranchAddress("HLT_DoubleMu4_JpsiTrk_Bc", &HLT_DoubleMu4_JpsiTrk_Bc, &b_HLT_DoubleMu4_JpsiTrk_Bc);
   // fChain->SetBranchStatus("HLT_Dimuon10_Upsilon_y1p4", 1);
   // fChain->SetBranchAddress("HLT_Dimuon10_Upsilon_y1p4", &HLT_Dimuon10_Upsilon_y1p4, &b_HLT_Dimuon10_Upsilon_y1p4);
   // fChain->SetBranchStatus("HLT_Dimuon14_PsiPrime", 1);
   // fChain->SetBranchAddress("HLT_Dimuon14_PsiPrime", &HLT_Dimuon14_PsiPrime, &b_HLT_Dimuon14_PsiPrime);
   // fChain->SetBranchStatus("HLT_Dimuon14_PsiPrime_noCorrL1", 1);
   // fChain->SetBranchAddress("HLT_Dimuon14_PsiPrime_noCorrL1", &HLT_Dimuon14_PsiPrime_noCorrL1, &b_HLT_Dimuon14_PsiPrime_noCorrL1);
   // fChain->SetBranchStatus("HLT_VBF_DoubleMediumDeepTauPFTauHPS20_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_VBF_DoubleMediumDeepTauPFTauHPS20_eta2p1", &HLT_VBF_DoubleMediumDeepTauPFTauHPS20_eta2p1, &b_HLT_VBF_DoubleMediumDeepTauPFTauHPS20_eta2p1);
   // fChain->SetBranchStatus("HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_Mass55", 1);
   // fChain->SetBranchAddress("HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_Mass55", &HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_Mass55, &b_HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_Mass55);
   // fChain->SetBranchStatus("HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId", 1);
   // fChain->SetBranchAddress("HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId", &HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId, &b_HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId);
   // fChain->SetBranchStatus("HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1", &HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1, &b_HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1);
   // fChain->SetBranchStatus("HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60", 1);
   // fChain->SetBranchAddress("HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60", &HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60, &b_HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60);
   // fChain->SetBranchStatus("HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75", 1);
   // fChain->SetBranchAddress("HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75", &HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75, &b_HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75);
   // fChain->SetBranchStatus("HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_CrossL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_CrossL1", &HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_CrossL1, &b_HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_CrossL1);
   // fChain->SetBranchStatus("HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60_CrossL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60_CrossL1", &HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60_CrossL1, &b_HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60_CrossL1);
   // fChain->SetBranchStatus("HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75_CrossL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75_CrossL1", &HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75_CrossL1, &b_HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75_CrossL1);
   // fChain->SetBranchStatus("HLT_DoublePFJets40_Mass500_MediumDeepTauPFTauHPS45_L2NN_MediumDeepTauPFTauHPS20_eta2p1", 1);
   // fChain->SetBranchAddress("HLT_DoublePFJets40_Mass500_MediumDeepTauPFTauHPS45_L2NN_MediumDeepTauPFTauHPS20_eta2p1", &HLT_DoublePFJets40_Mass500_MediumDeepTauPFTauHPS45_L2NN_MediumDeepTauPFTauHPS20_eta2p1, &b_HLT_DoublePFJets40_Mass500_MediumDeepTauPFTauHPS45_L2NN_MediumDeepTauPFTauHPS20_eta2p1);
   // fChain->SetBranchStatus("HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS20_eta2p1_SingleL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS20_eta2p1_SingleL1", &HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS20_eta2p1_SingleL1, &b_HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS20_eta2p1_SingleL1);
   // fChain->SetBranchStatus("HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS45_L2NN_eta2p1_CrossL1", 1);
   // fChain->SetBranchAddress("HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS45_L2NN_eta2p1_CrossL1", &HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS45_L2NN_eta2p1_CrossL1, &b_HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS45_L2NN_eta2p1_CrossL1);
   // fChain->SetBranchStatus("HLT_DoubleL2Mu12NoVtx_2Cha_VetoL3Mu0DxyMax1cm", 1);
   // fChain->SetBranchAddress("HLT_DoubleL2Mu12NoVtx_2Cha_VetoL3Mu0DxyMax1cm", &HLT_DoubleL2Mu12NoVtx_2Cha_VetoL3Mu0DxyMax1cm, &b_HLT_DoubleL2Mu12NoVtx_2Cha_VetoL3Mu0DxyMax1cm);
   // fChain->SetBranchStatus("HLT_DoubleL2Mu14NoVtx_2Cha_VetoL3Mu0DxyMax1cm", 1);
   // fChain->SetBranchAddress("HLT_DoubleL2Mu14NoVtx_2Cha_VetoL3Mu0DxyMax1cm", &HLT_DoubleL2Mu14NoVtx_2Cha_VetoL3Mu0DxyMax1cm, &b_HLT_DoubleL2Mu14NoVtx_2Cha_VetoL3Mu0DxyMax1cm);
   // fChain->SetBranchStatus("HLT_DoubleL3Mu18_10NoVtx_DxyMin0p01cm", 1);
   // fChain->SetBranchAddress("HLT_DoubleL3Mu18_10NoVtx_DxyMin0p01cm", &HLT_DoubleL3Mu18_10NoVtx_DxyMin0p01cm, &b_HLT_DoubleL3Mu18_10NoVtx_DxyMin0p01cm);
   // fChain->SetBranchStatus("HLT_DoubleL3Mu20_10NoVtx_DxyMin0p01cm", 1);
   // fChain->SetBranchAddress("HLT_DoubleL3Mu20_10NoVtx_DxyMin0p01cm", &HLT_DoubleL3Mu20_10NoVtx_DxyMin0p01cm, &b_HLT_DoubleL3Mu20_10NoVtx_DxyMin0p01cm);
   // fChain->SetBranchStatus("HLT_L2Mu10NoVtx_2Cha", 1);
   // fChain->SetBranchAddress("HLT_L2Mu10NoVtx_2Cha", &HLT_L2Mu10NoVtx_2Cha, &b_HLT_L2Mu10NoVtx_2Cha);
   // fChain->SetBranchStatus("HLT_L2Mu10NoVtx_2Cha_VetoL3Mu0DxyMax1cm", 1);
   // fChain->SetBranchAddress("HLT_L2Mu10NoVtx_2Cha_VetoL3Mu0DxyMax1cm", &HLT_L2Mu10NoVtx_2Cha_VetoL3Mu0DxyMax1cm, &b_HLT_L2Mu10NoVtx_2Cha_VetoL3Mu0DxyMax1cm);
   // fChain->SetBranchStatus("HLT_L3Mu10NoVtx", 1);
   // fChain->SetBranchAddress("HLT_L3Mu10NoVtx", &HLT_L3Mu10NoVtx, &b_HLT_L3Mu10NoVtx);
   // fChain->SetBranchStatus("HLT_L3Mu10NoVtx_DxyMin0p01cm", 1);
   // fChain->SetBranchAddress("HLT_L3Mu10NoVtx_DxyMin0p01cm", &HLT_L3Mu10NoVtx_DxyMin0p01cm, &b_HLT_L3Mu10NoVtx_DxyMin0p01cm);
   // fChain->SetBranchStatus("HLT_DoubleL3dTksMu16_10NoVtx_DxyMin0p01cm", 1);
   // fChain->SetBranchAddress("HLT_DoubleL3dTksMu16_10NoVtx_DxyMin0p01cm", &HLT_DoubleL3dTksMu16_10NoVtx_DxyMin0p01cm, &b_HLT_DoubleL3dTksMu16_10NoVtx_DxyMin0p01cm);
   // fChain->SetBranchStatus("HLT_L3dTksMu10_NoVtx_DxyMin0p01cm", 1);
   // fChain->SetBranchAddress("HLT_L3dTksMu10_NoVtx_DxyMin0p01cm", &HLT_L3dTksMu10_NoVtx_DxyMin0p01cm, &b_HLT_L3dTksMu10_NoVtx_DxyMin0p01cm);
   // fChain->SetBranchStatus("HLT_HT170_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack", 1);
   // fChain->SetBranchAddress("HLT_HT170_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack", &HLT_HT170_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack, &b_HLT_HT170_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack);
   // fChain->SetBranchStatus("HLT_HT200_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack", 1);
   // fChain->SetBranchAddress("HLT_HT200_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack", &HLT_HT200_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack, &b_HLT_HT200_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack);
   // fChain->SetBranchStatus("HLT_HT200_L1SingleLLPJet_DisplacedDijet60_DisplacedTrack", 1);
   // fChain->SetBranchAddress("HLT_HT200_L1SingleLLPJet_DisplacedDijet60_DisplacedTrack", &HLT_HT200_L1SingleLLPJet_DisplacedDijet60_DisplacedTrack, &b_HLT_HT200_L1SingleLLPJet_DisplacedDijet60_DisplacedTrack);
   // fChain->SetBranchStatus("HLT_HT270_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack", 1);
   // fChain->SetBranchAddress("HLT_HT270_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack", &HLT_HT270_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack, &b_HLT_HT270_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack);
   // fChain->SetBranchStatus("HLT_HT320_L1SingleLLPJet_DisplacedDijet60_Inclusive", 1);
   // fChain->SetBranchAddress("HLT_HT320_L1SingleLLPJet_DisplacedDijet60_Inclusive", &HLT_HT320_L1SingleLLPJet_DisplacedDijet60_Inclusive, &b_HLT_HT320_L1SingleLLPJet_DisplacedDijet60_Inclusive);
   // fChain->SetBranchStatus("HLT_HT420_L1SingleLLPJet_DisplacedDijet60_Inclusive", 1);
   // fChain->SetBranchAddress("HLT_HT420_L1SingleLLPJet_DisplacedDijet60_Inclusive", &HLT_HT420_L1SingleLLPJet_DisplacedDijet60_Inclusive, &b_HLT_HT420_L1SingleLLPJet_DisplacedDijet60_Inclusive);
   // fChain->SetBranchStatus("HLT_HT200_L1SingleLLPJet_DelayedJet40_SingleDelay1nsTrackless", 1);
   // fChain->SetBranchAddress("HLT_HT200_L1SingleLLPJet_DelayedJet40_SingleDelay1nsTrackless", &HLT_HT200_L1SingleLLPJet_DelayedJet40_SingleDelay1nsTrackless, &b_HLT_HT200_L1SingleLLPJet_DelayedJet40_SingleDelay1nsTrackless);
   // fChain->SetBranchStatus("HLT_HT200_L1SingleLLPJet_DelayedJet40_SingleDelay2nsInclusive", 1);
   // fChain->SetBranchAddress("HLT_HT200_L1SingleLLPJet_DelayedJet40_SingleDelay2nsInclusive", &HLT_HT200_L1SingleLLPJet_DelayedJet40_SingleDelay2nsInclusive, &b_HLT_HT200_L1SingleLLPJet_DelayedJet40_SingleDelay2nsInclusive);
   // fChain->SetBranchStatus("HLT_HT200_L1SingleLLPJet_DelayedJet40_DoubleDelay0p5nsTrackless", 1);
   // fChain->SetBranchAddress("HLT_HT200_L1SingleLLPJet_DelayedJet40_DoubleDelay0p5nsTrackless", &HLT_HT200_L1SingleLLPJet_DelayedJet40_DoubleDelay0p5nsTrackless, &b_HLT_HT200_L1SingleLLPJet_DelayedJet40_DoubleDelay0p5nsTrackless);
   // fChain->SetBranchStatus("HLT_HT200_L1SingleLLPJet_DelayedJet40_DoubleDelay1nsInclusive", 1);
   // fChain->SetBranchAddress("HLT_HT200_L1SingleLLPJet_DelayedJet40_DoubleDelay1nsInclusive", &HLT_HT200_L1SingleLLPJet_DelayedJet40_DoubleDelay1nsInclusive, &b_HLT_HT200_L1SingleLLPJet_DelayedJet40_DoubleDelay1nsInclusive);
   // fChain->SetBranchStatus("HLT_HT200_L1SingleLLPJet_DisplacedDijet30_Inclusive1PtrkShortSig5", 1);
   // fChain->SetBranchAddress("HLT_HT200_L1SingleLLPJet_DisplacedDijet30_Inclusive1PtrkShortSig5", &HLT_HT200_L1SingleLLPJet_DisplacedDijet30_Inclusive1PtrkShortSig5, &b_HLT_HT200_L1SingleLLPJet_DisplacedDijet30_Inclusive1PtrkShortSig5);
   // fChain->SetBranchStatus("HLT_HT200_L1SingleLLPJet_DisplacedDijet35_Inclusive1PtrkShortSig5", 1);
   // fChain->SetBranchAddress("HLT_HT200_L1SingleLLPJet_DisplacedDijet35_Inclusive1PtrkShortSig5", &HLT_HT200_L1SingleLLPJet_DisplacedDijet35_Inclusive1PtrkShortSig5, &b_HLT_HT200_L1SingleLLPJet_DisplacedDijet35_Inclusive1PtrkShortSig5);
   // fChain->SetBranchStatus("HLT_HT200_L1SingleLLPJet_DisplacedDijet40_Inclusive1PtrkShortSig5", 1);
   // fChain->SetBranchAddress("HLT_HT200_L1SingleLLPJet_DisplacedDijet40_Inclusive1PtrkShortSig5", &HLT_HT200_L1SingleLLPJet_DisplacedDijet40_Inclusive1PtrkShortSig5, &b_HLT_HT200_L1SingleLLPJet_DisplacedDijet40_Inclusive1PtrkShortSig5);
   // fChain->SetBranchStatus("HLT_DiPhoton10Time1ns", 1);
   // fChain->SetBranchAddress("HLT_DiPhoton10Time1ns", &HLT_DiPhoton10Time1ns, &b_HLT_DiPhoton10Time1ns);
   // fChain->SetBranchStatus("HLT_DiPhoton10Time1p2ns", 1);
   // fChain->SetBranchAddress("HLT_DiPhoton10Time1p2ns", &HLT_DiPhoton10Time1p2ns, &b_HLT_DiPhoton10Time1p2ns);
   // fChain->SetBranchStatus("HLT_DiPhoton10Time1p4ns", 1);
   // fChain->SetBranchAddress("HLT_DiPhoton10Time1p4ns", &HLT_DiPhoton10Time1p4ns, &b_HLT_DiPhoton10Time1p4ns);
   // fChain->SetBranchStatus("HLT_DiPhoton10Time1p6ns", 1);
   // fChain->SetBranchAddress("HLT_DiPhoton10Time1p6ns", &HLT_DiPhoton10Time1p6ns, &b_HLT_DiPhoton10Time1p6ns);
   // fChain->SetBranchStatus("HLT_DiPhoton10Time1p8ns", 1);
   // fChain->SetBranchAddress("HLT_DiPhoton10Time1p8ns", &HLT_DiPhoton10Time1p8ns, &b_HLT_DiPhoton10Time1p8ns);
   // fChain->SetBranchStatus("HLT_DiPhoton10Time2ns", 1);
   // fChain->SetBranchAddress("HLT_DiPhoton10Time2ns", &HLT_DiPhoton10Time2ns, &b_HLT_DiPhoton10Time2ns);
   // fChain->SetBranchStatus("HLT_DiPhoton10sminlt0p1", 1);
   // fChain->SetBranchAddress("HLT_DiPhoton10sminlt0p1", &HLT_DiPhoton10sminlt0p1, &b_HLT_DiPhoton10sminlt0p1);
   // fChain->SetBranchStatus("HLT_DiPhoton10sminlt0p12", 1);
   // fChain->SetBranchAddress("HLT_DiPhoton10sminlt0p12", &HLT_DiPhoton10sminlt0p12, &b_HLT_DiPhoton10sminlt0p12);
   // fChain->SetBranchStatus("HLT_DiPhoton10sminlt0p14", 1);
   // fChain->SetBranchAddress("HLT_DiPhoton10sminlt0p14", &HLT_DiPhoton10sminlt0p14, &b_HLT_DiPhoton10sminlt0p14);
   // fChain->SetBranchStatus("HLT_DiPhoton10sminlt0p16", 1);
   // fChain->SetBranchAddress("HLT_DiPhoton10sminlt0p16", &HLT_DiPhoton10sminlt0p16, &b_HLT_DiPhoton10sminlt0p16);
   // fChain->SetBranchStatus("HLT_DiPhoton10_CaloIdL", 1);
   // fChain->SetBranchAddress("HLT_DiPhoton10_CaloIdL", &HLT_DiPhoton10_CaloIdL, &b_HLT_DiPhoton10_CaloIdL);
   // fChain->SetBranchStatus("HLT_DoubleEle4_eta1p22_mMax6", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle4_eta1p22_mMax6", &HLT_DoubleEle4_eta1p22_mMax6, &b_HLT_DoubleEle4_eta1p22_mMax6);
   // fChain->SetBranchStatus("HLT_DoubleEle4p5_eta1p22_mMax6", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle4p5_eta1p22_mMax6", &HLT_DoubleEle4p5_eta1p22_mMax6, &b_HLT_DoubleEle4p5_eta1p22_mMax6);
   // fChain->SetBranchStatus("HLT_DoubleEle5_eta1p22_mMax6", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle5_eta1p22_mMax6", &HLT_DoubleEle5_eta1p22_mMax6, &b_HLT_DoubleEle5_eta1p22_mMax6);
   // fChain->SetBranchStatus("HLT_DoubleEle5p5_eta1p22_mMax6", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle5p5_eta1p22_mMax6", &HLT_DoubleEle5p5_eta1p22_mMax6, &b_HLT_DoubleEle5p5_eta1p22_mMax6);
   // fChain->SetBranchStatus("HLT_DoubleEle6_eta1p22_mMax6", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle6_eta1p22_mMax6", &HLT_DoubleEle6_eta1p22_mMax6, &b_HLT_DoubleEle6_eta1p22_mMax6);
   // fChain->SetBranchStatus("HLT_DoubleEle6p5_eta1p22_mMax6", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle6p5_eta1p22_mMax6", &HLT_DoubleEle6p5_eta1p22_mMax6, &b_HLT_DoubleEle6p5_eta1p22_mMax6);
   // fChain->SetBranchStatus("HLT_DoubleEle7_eta1p22_mMax6", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle7_eta1p22_mMax6", &HLT_DoubleEle7_eta1p22_mMax6, &b_HLT_DoubleEle7_eta1p22_mMax6);
   // fChain->SetBranchStatus("HLT_DoubleEle7p5_eta1p22_mMax6", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle7p5_eta1p22_mMax6", &HLT_DoubleEle7p5_eta1p22_mMax6, &b_HLT_DoubleEle7p5_eta1p22_mMax6);
   // fChain->SetBranchStatus("HLT_DoubleEle8_eta1p22_mMax6", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle8_eta1p22_mMax6", &HLT_DoubleEle8_eta1p22_mMax6, &b_HLT_DoubleEle8_eta1p22_mMax6);
   // fChain->SetBranchStatus("HLT_DoubleEle8p5_eta1p22_mMax6", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle8p5_eta1p22_mMax6", &HLT_DoubleEle8p5_eta1p22_mMax6, &b_HLT_DoubleEle8p5_eta1p22_mMax6);
   // fChain->SetBranchStatus("HLT_DoubleEle9_eta1p22_mMax6", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle9_eta1p22_mMax6", &HLT_DoubleEle9_eta1p22_mMax6, &b_HLT_DoubleEle9_eta1p22_mMax6);
   // fChain->SetBranchStatus("HLT_DoubleEle9p5_eta1p22_mMax6", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle9p5_eta1p22_mMax6", &HLT_DoubleEle9p5_eta1p22_mMax6, &b_HLT_DoubleEle9p5_eta1p22_mMax6);
   // fChain->SetBranchStatus("HLT_DoubleEle10_eta1p22_mMax6", 1);
   // fChain->SetBranchAddress("HLT_DoubleEle10_eta1p22_mMax6", &HLT_DoubleEle10_eta1p22_mMax6, &b_HLT_DoubleEle10_eta1p22_mMax6);
   // fChain->SetBranchStatus("HLT_Diphoton20_14_eta1p5_R9IdL_AND_HE_AND_IsoTCaloIdT", 1);
   // fChain->SetBranchAddress("HLT_Diphoton20_14_eta1p5_R9IdL_AND_HE_AND_IsoTCaloIdT", &HLT_Diphoton20_14_eta1p5_R9IdL_AND_HE_AND_IsoTCaloIdT, &b_HLT_Diphoton20_14_eta1p5_R9IdL_AND_HE_AND_IsoTCaloIdT);
   // fChain->SetBranchStatus("HLT_Diphoton20_14_eta1p5_R9IdL_AND_HET_AND_IsoTCaloIdT", 1);
   // fChain->SetBranchAddress("HLT_Diphoton20_14_eta1p5_R9IdL_AND_HET_AND_IsoTCaloIdT", &HLT_Diphoton20_14_eta1p5_R9IdL_AND_HET_AND_IsoTCaloIdT, &b_HLT_Diphoton20_14_eta1p5_R9IdL_AND_HET_AND_IsoTCaloIdT);
   // fChain->SetBranchStatus("HLT_Diphoton22_14_eta1p5_R9IdL_AND_HE_AND_IsoTCaloIdT", 1);
   // fChain->SetBranchAddress("HLT_Diphoton22_14_eta1p5_R9IdL_AND_HE_AND_IsoTCaloIdT", &HLT_Diphoton22_14_eta1p5_R9IdL_AND_HE_AND_IsoTCaloIdT, &b_HLT_Diphoton22_14_eta1p5_R9IdL_AND_HE_AND_IsoTCaloIdT);
   // fChain->SetBranchStatus("HLT_Diphoton22_14_eta1p5_R9IdL_AND_HET_AND_IsoTCaloIdT", 1);
   // fChain->SetBranchAddress("HLT_Diphoton22_14_eta1p5_R9IdL_AND_HET_AND_IsoTCaloIdT", &HLT_Diphoton22_14_eta1p5_R9IdL_AND_HET_AND_IsoTCaloIdT, &b_HLT_Diphoton22_14_eta1p5_R9IdL_AND_HET_AND_IsoTCaloIdT);
   
   Notify();

}


Bool_t MainEvent::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

#endif // #ifdef MainEvent_cxx
