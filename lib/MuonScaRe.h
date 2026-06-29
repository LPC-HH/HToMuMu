#ifndef MuonScaRe_h
#define MuonScaRe_h

#include <correction.h>

#include <memory>
#include <string>

extern std::unique_ptr<correction::CorrectionSet> muon_scale_cset;

void initializeMuonScaReCorrections(const std::string &year_num);
double get_rndm(double eta, double phi, float nL, int evtNumber,
                int lumiNumber);
double get_std(double pt, double eta, float nL);
double get_k(double eta, std::string var);
double pt_resol(double pt, double eta, double phi, float nL, int evtNumber,
                int lumiNumber, double low_pt_threshold = 26);
double pt_resol_var(double pt_woresol, double pt_wresol, double eta,
                    std::string updn);
double pt_scale(bool is_data, double pt, double eta, double phi, int charge,
                double low_pt_threshold = 26);
double pt_scale_var(double pt, double eta, double phi, int charge,
                    std::string updn);

#endif
