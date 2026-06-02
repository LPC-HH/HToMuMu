#include "../lib/JetCorrector.h"
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

unique_ptr<correction::CorrectionSet> csetVeto;
//unique_ptr<correction::CorrectionSet> csetID;
//correction::Correction::Ref sf;

const map<string, string> JetCorrector::keys = {
    {"2022", "Summer22_23Sep2023_RunCD_V1"},
    {"2022EE", "Summer22EE_23Sep2023_RunEFG_V1"},
    {"2023", "Summer23Prompt23_RunC_V1"},
    {"2023BPix", "Summer23BPixPrompt23_RunD_V1"},
    {"2024", "Summer24Prompt24_RunBCDEFGHI_V1"},
    {"2025", "Winter25Prompt25_RunCDEFG_V1"},
};

void JetCorrector::initializeCorrections(const std::string& year_num) {
    std::string basePath = "./data/jetCorrections/";
    
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

    csetVeto = loadCorrectionSet(basePath + "jetvetomaps.json.gz");
    jsonKey = keys.at(year_num);

    std::cout << "Jet corrections initialized" << std::endl;
}

bool JetCorrector::jetVeto(float jet_eta, float jet_phi){
    auto jetVetoMap = csetVeto->at(jsonKey);
    float val = jetVetoMap->evaluate({"jetvetomap", jet_eta, jet_phi});
    
    if (val > 0){
        cout << "Vetoing jet at Eta: " << jet_eta << " | Phi: " << jet_phi << std::endl;
    }

    return val > 0;
}