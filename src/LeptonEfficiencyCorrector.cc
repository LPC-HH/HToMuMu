#include "../lib/LeptonEfficiencyCorrector.h"
#include "correction.h"

#include <algorithm>
#include <stdexcept>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>
#include <cassert>
#include <filesystem>
#include <cmath>

using namespace std;
namespace fs = filesystem;

unique_ptr<correction::CorrectionSet> cset;

void LeptonEfficiencyCorrector::initializeCorrections(const std::string& year_num) {
    //std::string basePath = "/afs/cern.ch/user/y/yulou/CMSSW_14_0_14/src/HToMuMu/data/leptonSF/";
    std::string basePath = "./data/leptonSF/";
    
    const std::vector<std::string> valid_eras = {"2022", "2022EE", "2023", "2023BPix", "2024"};
    
    if (std::find(valid_eras.begin(), valid_eras.end(), year_num) != valid_eras.end()) {
        basePath += year_num + "/";
    } else {
        throw std::runtime_error("Unsupported era: " + year_num);
    }    

    auto loadCorrectionSet = [](const std::string& path) -> std::unique_ptr<correction::CorrectionSet> {
        std::cout << "Loading JSON file: " << path << std::endl;
        if (!std::filesystem::exists(path)) {
            throw std::runtime_error("File not found: " + path);
        }
        return correction::CorrectionSet::from_file(path);
    };

    cset = loadCorrectionSet(basePath + "muon_Z.json.gz");

    std::cout << "Muon efficiency corrections initialized" << std::endl;
}

float LeptonEfficiencyCorrector::runner(const unique_ptr<correction::CorrectionSet>& cset,
          const string& key,
          const map<string, correction::Variable::Type>& example)
{
    correction::Correction::Ref sf = cset->at(key);
    vector<correction::Variable::Type> inputs;
    for (const correction::Variable& input: sf->inputs())
        inputs.push_back(example.at(input.name()));
    float result = sf->evaluate(inputs);

    return result;
}

float LeptonEfficiencyCorrector::give_eff(const string& type, float muon_pt, float muon_eta) {

    //"We recommend you to use the latest version of high-pT muon ID for the full Run-2 and Run-3 analyses"
    //We only use medium pt json file, it covers muon_pt starting from 15.0 GeV.
    //you can change to the efficiencies you want here
    static const map<string, pair<string, string>> type_config = {
        {"TRIG", {"NUM_IsoMu24_DEN_CutBasedIdMedium_and_PFIsoMedium", "nominal"},},
        {"ID", {"NUM_MediumID_DEN_TrackerMuons", "nominal"},},
        {"ISO", {"NUM_LoosePFIso_DEN_MediumID", "nominal"},}
    };

    std::string category;
    if (type.find("TRIG") != std::string::npos)       category = "TRIG";
    else if (type.find("ID") != std::string::npos)    category = "ID";
    else if (type.find("ISO") != std::string::npos)   category = "ISO";
    else throw std::runtime_error("No valid type: " + type);

    // medium pt trigger eff start from 26.0 GeV 
    if (muon_pt < 26.0)      return ((type.find("SFerr") != std::string::npos)
                                    ||(type.find("_stat") != std::string::npos)
                                    ||(type.find("_syst") != std::string::npos)) ? 0.0f : 1.0f;

    const auto& config = type_config.at(category);
    const std::string& final_key = config.first;
    std::string scale_type = config.second; 

    if (type.find("_up") != std::string::npos)        scale_type = "systup";
    else if (type.find("_down") != std::string::npos) scale_type = "systdown";
    else if (type.find("stat") != std::string::npos)  scale_type = "stat";
    else if (type.find("syst") != std::string::npos)  scale_type = "syst";

    std::map<std::string, correction::Variable::Type> params = {
        {"pt", muon_pt}, {"eta", muon_eta}, {"scale_factors", scale_type}
    };

    
    return runner(cset, final_key, params);
}


/*
void LeptonEfficiencyCorrector::init(std::vector<std::string> files,
                                     std::vector<std::string> histos) {
    effmaps_.clear();
    if (files.size() != histos.size()) {
        std::cout << "ERROR! There should be one histogram per input file! "
                     "Returning 0 as SF."
                  << std::endl;
        return;
    }

    for (int i = 0; i < (int)files.size(); ++i) {
        TFile *f = TFile::Open(files[i].c_str(), "read");
        if (!f) {
            std::cout << "WARNING! File " << files[i]
                      << " cannot be opened. Skipping this scale factor "
                      << std::endl;
            continue;
        }
        TH2F *hist = (TH2F *)(f->Get(histos[i].c_str()))
                         ->Clone(("eff_" + histos[i]).c_str());
        hist->SetDirectory(0);
        if (!hist) {
            std::cout << "ERROR! Histogram " << histos[i] << " not in file "
                      << files[i] << ". Not considering this SF. " << std::endl;
            continue;
        } else {
            std::cout << "Loading histogram " << histos[i] << " from file "
                      << files[i] << "... " << std::endl;
        }
        effmaps_.push_back(hist);
        f->Close();
    }
}

void LeptonEfficiencyCorrector::setLeptons(int nLep, int *lepPdgId,
                                           float *lepPt, float *lepEta) {
    nLep_ = nLep;
    Lep_pdgId_ = lepPdgId;
    Lep_pt_ = lepPt;
    Lep_eta_ = lepEta;
}

float LeptonEfficiencyCorrector::getSF(int pdgid, float pt, float eta) {
    float out = 1.;
    float x = abs(pdgid) == 13 ? pt : eta;
    float y = abs(pdgid) == 13 ? fabs(eta) : pt;
    for (std::vector<TH2F *>::iterator hist = effmaps_.begin();
         hist < effmaps_.end(); ++hist) {
        WeightCalculatorFromHistogram wc(*hist);
        out *= wc.getWeight(x, y);
    }
    return out;
}

float LeptonEfficiencyCorrector::getSFAve(int pdgid, float pt, float eta,
                                          float weight) {
    float out = 0.;
    float x = abs(pdgid) == 13 ? pt : eta;
    float y = abs(pdgid) == 13 ? fabs(eta) : pt;
    int index = 0;
    for (std::vector<TH2F *>::iterator hist = effmaps_.begin();
         hist < effmaps_.end(); ++hist) {
        WeightCalculatorFromHistogram wc(*hist);
        index++;
        if (index == 1) {
            out += weight * wc.getWeight(x, y);
            // std::cout <<"1: "<<wc.getWeight(x,y)<<std::endl;
        } else if (index == 2) {
            out += (1. - weight) * wc.getWeight(x, y);
            // std::cout <<"2: "<<wc.getWeight(x,y)<<std::endl;
        } else
            out = -666.;
    }
    // std::cout <<"final: "<<out<<std::endl;
    return out;
}

float LeptonEfficiencyCorrector::getSFErr(int pdgid, float pt, float eta) {
    float out = 1.;
    float x = abs(pdgid) == 13 ? pt : eta;
    float y = abs(pdgid) == 13 ? fabs(eta) : pt;
    // float x = pt;
    // float y = abs(pdgid)==13 ? fabs(eta) : eta;
    for (std::vector<TH2F *>::iterator hist = effmaps_.begin();
         hist < effmaps_.end(); ++hist) {
        WeightCalculatorFromHistogram wc(*hist);
        out *= wc.getWeightErr(x, y);
    }
    return out;
}

const std::vector<float> &LeptonEfficiencyCorrector::run() {
    ret_.clear();
    for (int iL = 0, nL = nLep_; iL < nL; ++iL) {
        ret_.push_back(getSF((Lep_pdgId_)[iL], (Lep_pt_)[iL], (Lep_eta_)[iL]));
    }
    return ret_;
}
*/
