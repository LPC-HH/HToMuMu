#ifndef LIB_UTILS_H
#define LIB_UTILS_H

#include "Constants.h"
#include "Run3Constants.h"
#include <TFile.h>
#include <TH1F.h>
#include <TLorentzVector.h>
#include <TMath.h>
#include <TVector3.h>
#include <memory>

long double GetGenWeightSum(const TString &input_name) {

    std::unique_ptr<TFile> histogram_file(TFile::Open(input_name, "READ"));

    if (!histogram_file || histogram_file->IsZombie()) {
        throw std::runtime_error(
            "Histogram file was not found or is is Zombie: " +
            std::string(input_name));
        return -1;
    }
    TH1F *gen_weight_sum_histogram =
        static_cast<TH1F *>(histogram_file->Get("h_sumOfgenWeight"));

    if (!gen_weight_sum_histogram) {
        throw std::runtime_error("Sum gen weight histogram WAS NOT found");
        return -1;
    }

    long double gen_weight_sum = gen_weight_sum_histogram->GetBinContent(1);
    std::cout << "The sum of gen weights is: " << gen_weight_sum << std::endl;
    histogram_file->Close();
    return gen_weight_sum;
}

double GetScaleFactor(const float &luminosity, const float &cross_section,
                      const long double &gen_weight_sum) {
    return luminosity * (cross_section * 1000) / gen_weight_sum;
}

double GetEventWeight(const float &gen_weight, const float &pileup_weight,
                      const float &scale_factor, const float &mu_trig_eff_SF,
                      const float &mu_ID_eff_SF, const float &mu_ISO_eff_SF) {
    return gen_weight * pileup_weight * scale_factor * mu_trig_eff_SF *
           mu_ID_eff_SF * mu_ISO_eff_SF;
}

std::pair<float, float> CSAngles(TLorentzVector vector_1,
                                 TLorentzVector vector_2, const int charge) {
    // https://github.com/alisw/AliPhysics/blob/master/PWGDQ/dielectron/core/AliDielectronPair.cxx
    TLorentzVector proton_1_vector(
        0., 0., -BEAM_ENERGY_GEV,
        TMath::Sqrt((BEAM_ENERGY_GEV / 2) * (BEAM_ENERGY_GEV / 2) +
                    PROTON_MASS * PROTON_MASS));
    TLorentzVector proton_2_vector(
        0., 0., BEAM_ENERGY_GEV,
        TMath::Sqrt((BEAM_ENERGY_GEV / 2) * (BEAM_ENERGY_GEV / 2) +
                    PROTON_MASS * PROTON_MASS));

    TLorentzVector higgs_vector = vector_1 + vector_2;
    vector_1.Boost(-(higgs_vector.BoostVector())); // go to Higgs RFR
    vector_2.Boost(-(higgs_vector.BoostVector()));
    proton_1_vector.Boost(-(higgs_vector.BoostVector()));
    proton_2_vector.Boost(-(higgs_vector.BoostVector()));

    TVector3 y_axis =
        ((proton_1_vector.Vect()).Cross(proton_2_vector.Vect())).Unit();
    TVector3 z_Axis_CS =
        ((proton_1_vector.Vect()).Unit() - (proton_2_vector.Vect()).Unit())
            .Unit();
    TVector3 x_axis_CS = (y_axis.Cross(z_Axis_CS)).Unit();

    float cos_theta_CS;
    float phi_CS;
    if (charge > 0) {
        cos_theta_CS = z_Axis_CS.Dot((vector_2.Vect()).Unit());
        phi_CS = TMath::ATan2((vector_2.Vect()).Dot(y_axis),
                              (vector_2.Vect()).Dot(x_axis_CS));
    } else {
        cos_theta_CS = z_Axis_CS.Dot((vector_1.Vect()).Unit());
        phi_CS = TMath::ATan2((vector_1.Vect()).Dot(y_axis),
                              (vector_1.Vect()).Dot(x_axis_CS));
    }

    return std::pair<float, float>(cos_theta_CS, phi_CS);
}

float DeltaPhi(const float &phi_1, const float &phi_2) {

    float delta_phi = phi_1 - phi_2;
    while (delta_phi > PI)
        delta_phi -= TWO_PI;
    while (delta_phi <= -PI)
        delta_phi += TWO_PI;
    return delta_phi;
}

float DeltaEta(const float &eta_1, const float &eta_2) {

    return TMath::Abs(eta_1 - eta_2);
}

float GetZZeppenfeldVariable(const float &diMuon_rapidity,
                             const std::vector<float> *const &jet_pt,
                             const std::vector<float> *const &jet_phi,
                             const std::vector<float> *const &jet_eta,
                             const std::vector<float> *const &jet_mass) {

    if (jet_pt->size() < 2) {
        std::cout << "There isn't 2 jets in this event, returning 0 for the "
                     "Z Zeppenfeld variable\n";
        return 0.;
    }
    TLorentzVector leading_jet_vector, subleading_jet_vector;
    leading_jet_vector.SetPtEtaPhiM((*jet_pt)[0], (*jet_eta)[0], (*jet_phi)[0],
                                    (*jet_mass)[0]);
    subleading_jet_vector.SetPtEtaPhiM((*jet_pt)[1], (*jet_eta)[1],
                                       (*jet_phi)[1], (*jet_mass)[1]);

    float leading_jet_rapidity, subleading_jet_rapidity;
    leading_jet_rapidity = leading_jet_vector.Rapidity();
    subleading_jet_rapidity = subleading_jet_vector.Rapidity();
    return (diMuon_rapidity -
            (leading_jet_rapidity + subleading_jet_rapidity) / 2) /
           (TMath::Abs(leading_jet_rapidity - subleading_jet_rapidity));
}

float GetPtBalanceVariable(const TLorentzVector &diMuon_vec,
                            const std::vector<float> *const &jet_pt,
                            const std::vector<float> *const &jet_phi,
                            const std::vector<float> *const &jet_eta,
                            const std::vector<float> *const &jet_mass) {
    if (jet_pt->size() < 2) {
        std::cout << "Less than 2 jets in this event, returning -1 for the "
                     "Pt balance\n";
        return -1;
    }
    TLorentzVector leading_jet_vector, subleading_jet_vector, total_vector;
    leading_jet_vector.SetPtEtaPhiM((*jet_pt)[0], (*jet_eta)[0], (*jet_phi)[0],
                                    (*jet_mass)[0]);
    subleading_jet_vector.SetPtEtaPhiM((*jet_pt)[1], (*jet_eta)[1],
                                       (*jet_phi)[1], (*jet_mass)[1]);
    total_vector = leading_jet_vector + subleading_jet_vector + diMuon_vec;
    float total_pt, leading_jet_pt, subleading_jet_pt;
    total_pt = total_vector.Pt();
    leading_jet_pt = (*jet_pt)[0];
    subleading_jet_pt = (*jet_pt)[1];

    return TMath::Abs(total_pt) / (TMath::Abs(leading_jet_pt) +
            TMath::Abs(subleading_jet_pt) + TMath::Abs(diMuon_vec.Pt()));
}

float GetPtCentralityVariable(const float &diMuon_pt,
                            const std::vector<float> *const &jet_pt,
                            const std::vector<float> *const &jet_phi,
                            const std::vector<float> *const &jet_eta,
                            const std::vector<float> *const &jet_mass) {
    if (jet_pt->size() < 2) {
        std::cout << "Less than 2 jets in this event, returning -1 for the "
                     "Pt balance\n";
        return -1;
    }
    TLorentzVector leading_jet_vector, subleading_jet_vector;
    leading_jet_vector.SetPtEtaPhiM((*jet_pt)[0], (*jet_eta)[0], (*jet_phi)[0],
                                    (*jet_mass)[0]);
    subleading_jet_vector.SetPtEtaPhiM((*jet_pt)[1], (*jet_eta)[1],
                                       (*jet_phi)[1], (*jet_mass)[1]);
    float jet_sum_pt, jet_dif_pt;
    jet_sum_pt = (leading_jet_vector + subleading_jet_vector).Pt();
    jet_dif_pt = (leading_jet_vector - subleading_jet_vector).Pt();

    return (diMuon_pt - TMath::Abs(jet_sum_pt)/2) / TMath::Abs(jet_dif_pt);
}

#endif // if LIB_UTILS_H
