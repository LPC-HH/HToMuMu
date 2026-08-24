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
    
    const std::vector<std::string> valid_eras = {"2022", "2022EE", "2023", "2023BPix", "2024", "2025"};
    
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

float LeptonEfficiencyCorrector::give_eff(
    const string& type,
    float muon_pt,
    float muon_eta)
{
    static const map<string, pair<string, string>> type_config = {
        {"TRIG", {"NUM_IsoMu24_DEN_CutBasedIdMedium_and_PFIsoMedium", "nominal"}},
        {"ID",   {"NUM_MediumID_DEN_TrackerMuons", "nominal"}},
        {"ISO",  {"NUM_LoosePFIso_DEN_MediumID", "nominal"}}
    };

    std::string category;

    if (type.find("TRIG") != std::string::npos)
        category = "TRIG";
    else if (type.find("ID") != std::string::npos)
        category = "ID";
    else if (type.find("ISO") != std::string::npos)
        category = "ISO";
    else
        throw std::runtime_error("No valid type: " + type);


    bool request_DATAeff =
        (type.find("DATAeff") != std::string::npos);

    bool request_MCeff =
        (type.find("MCeff") != std::string::npos);

    if (request_DATAeff && request_MCeff) {
        throw std::runtime_error(
            "Cannot request DATAeff and MCeff simultaneously: " + type);
    }

    float min_pt = 0.0;
    if (category == "TRIG")
        min_pt = 26.0;
    else if (category == "ID" || category == "ISO")
        min_pt = 20.0;

    if (muon_pt < min_pt) {

        // DATA/MC efficiencies below the valid range
        if (request_DATAeff || request_MCeff)
            return 0.0f;

        // Uncertainties below the valid range
        if ((type.find("SFerr") != std::string::npos) ||
            (type.find("_stat") != std::string::npos) ||
            (type.find("_syst") != std::string::npos))
            return 0.0f;

        return 1.0f;
    }



    const auto& config = type_config.at(category);
    const std::string& final_key = config.first;

    std::string scale_type = "nominal";
    if (type.find("_up") != std::string::npos)
        scale_type = "systup";
    else if (type.find("_down") != std::string::npos)
        scale_type = "systdown";
    else if (type.find("_stat") != std::string::npos)
        scale_type = "stat";
    else if (type.find("_syst") != std::string::npos)
        scale_type = "syst";


    // Add DATAeff / MCeff suffix when requested
    // nominal          -> nominal
    // nominal_DATAeff  -> data efficiency
    // nominal_MCeff    -> MC efficiency
    // systup_DATAeff, systup_MCeff, etc.
    if (request_DATAeff)
        scale_type += "_DATAeff";
    else if (request_MCeff)
        scale_type += "_MCeff";


    std::map<std::string, correction::Variable::Type> params = {
        {"pt", muon_pt},
        {"eta", muon_eta},
        {"scale_factors", scale_type}
    };

    return runner(cset, final_key, params);
}

