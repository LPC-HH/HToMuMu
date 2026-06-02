#ifndef LIB_JetCorrector_H
#define LIB_JetCorrector_H

#include <iostream>
#include <string>
#include <vector>
#include <TH2.h>
#include <TFile.h>
#include <memory>    
#include <map> 

#include "correction.h"

using namespace std;
namespace fs = filesystem;
extern std::unique_ptr<correction::CorrectionSet> cset;


class JetCorrector {
  public:
    void initializeCorrections(const std::string& year_num);
    bool jetVeto(float jet_eta, float jet_phi);

  private:
    string jsonKey;
    static const map<string, string> keys;
};
#endif