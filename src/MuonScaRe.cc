#include "../lib/MuonScaRe.h"

#include <boost/math/special_functions/erf.hpp>

#include <algorithm>
#include <cmath>
#include <filesystem>
#include <iostream>
#include <stdexcept>

std::unique_ptr<correction::CorrectionSet> muon_scale_cset;

namespace {

struct CrystalBall {
    double pi = 3.14159;
    double sqrtPiOver2 = std::sqrt(pi / 2.0);
    double sqrt2 = std::sqrt(2.0);
    double m;
    double s;
    double a;
    double n;
    double B;
    double C;
    double D;
    double N;
    double NA;
    double Ns;
    double NC;
    double F;
    double G;
    double k;
    double cdfMa;
    double cdfPa;

    CrystalBall() : m(0), s(1), a(10), n(10) { init(); }
    CrystalBall(double mean, double sigma, double alpha, double n)
        : m(mean), s(sigma), a(alpha), n(n) {
        init();
    }

    void init() {
        double fa = std::fabs(a);
        double ex = std::exp(-fa * fa / 2);
        double A = std::pow(n / fa, n) * ex;
        double C1 = n / fa / (n - 1) * ex;
        double D1 = 2 * sqrtPiOver2 * std::erf(fa / sqrt2);
        B = n / fa - fa;
        C = (D1 + 2 * C1) / C1;
        D = (D1 + 2 * C1) / 2;
        N = 1.0 / s / (D1 + 2 * C1);
        k = 1.0 / (n - 1);
        NA = N * A;
        Ns = N * s;
        NC = Ns * C1;
        F = 1 - fa * fa / n;
        G = s * n / fa;
        cdfMa = cdf(m - a * s);
        cdfPa = cdf(m + a * s);
    }

    double cdf(double x) const {
        double d = (x - m) / s;
        if (d < -a) return NC / std::pow(F - s * d / G, n - 1);
        if (d > a) return NC * (C - std::pow(F + s * d / G, 1 - n));
        return Ns * (D - sqrtPiOver2 * std::erf(-d / sqrt2));
    }

    double invcdf(double u) const {
        if (u < cdfMa) return m + G * (F - std::pow(NC / u, k));
        if (u > cdfPa) return m - G * (F - std::pow(C - u / NC, -k));
        return m - sqrt2 * s *
                   boost::math::erf_inv((D - u / Ns) / sqrtPiOver2);
    }
};

const correction::CorrectionSet &MuonScaleCorrectionSet() {
    if (!muon_scale_cset) {
        throw std::runtime_error("Muon scale/smearing corrections are not initialized");
    }
    return *muon_scale_cset;
}

}  // namespace

void initializeMuonScaReCorrections(const std::string &year_num) {
    std::string path = "./data/leptonSF/" + year_num + "/muon_scalesmearing.json.gz";

    std::cout << "Loading muon scale/smearing JSON file: " << path << std::endl;
    if (!std::filesystem::exists(path)) {
        throw std::runtime_error("muon pt scale json file was not found: " + path);
    }

    muon_scale_cset = correction::CorrectionSet::from_file(path);
    std::cout << "muon pt scale json file loaded" << std::endl;
}

double get_rndm(double eta, double phi, float nL, int evtNumber,
                int lumiNumber) {
    const auto &cset = MuonScaleCorrectionSet();
    double mean = cset.at("cb_params")->evaluate({std::abs(eta), nL, 0});
    double sigma = cset.at("cb_params")->evaluate({std::abs(eta), nL, 1});
    double n = cset.at("cb_params")->evaluate({std::abs(eta), nL, 2});
    double alpha = cset.at("cb_params")->evaluate({std::abs(eta), nL, 3});

    CrystalBall cb(mean, sigma, alpha, n);
    double rndm = cset.at("RandomSmearing")->evaluate(
        {evtNumber, lumiNumber, phi});

    return cb.invcdf(rndm);
}

double get_std(double pt, double eta, float nL) {
    const auto &cset = MuonScaleCorrectionSet();
    double param_0 = cset.at("poly_params")->evaluate({std::abs(eta), nL, 0});
    double param_1 = cset.at("poly_params")->evaluate({std::abs(eta), nL, 1});
    double param_2 = cset.at("poly_params")->evaluate({std::abs(eta), nL, 2});

    double sigma = param_0 + param_1 * pt + param_2 * pt * pt;
    if (sigma < 0) sigma = 0;
    return sigma;
}

double get_k(double eta, std::string var) {
    const auto &cset = MuonScaleCorrectionSet();
    double k_data = cset.at("k_data")->evaluate({std::abs(eta), var});
    double k_mc = cset.at("k_mc")->evaluate({std::abs(eta), var});

    double k = 0;
    if (k_mc < k_data) k = std::sqrt(k_data * k_data - k_mc * k_mc);
    return k;
}

double pt_resol(double pt, double eta, double phi, float nL, int evtNumber,
                int lumiNumber, double low_pt_threshold) {
    double rndm = get_rndm(eta, phi, nL, evtNumber, lumiNumber);
    double std = get_std(pt, eta, nL);
    double k = get_k(eta, "nom");

    double ptc = pt * (1 + k * std * rndm);
    if (std::isnan(ptc)) ptc = pt;
    if (ptc / pt > 2 || ptc / pt < 0.1 || ptc < 0 ||
        pt < low_pt_threshold || pt > 200) {
        ptc = pt;
    }
    return ptc;
}

double pt_resol_var(double pt_woresol, double pt_wresol, double eta,
                    std::string updn) {
    const auto &cset = MuonScaleCorrectionSet();
    double k = get_k(eta, "nom");

    if (k == 0) return pt_wresol;

    double k_unc = cset.at("k_mc")->evaluate({std::abs(eta), "stat"});
    double std_x_rndm = (pt_wresol / pt_woresol - 1) / k;
    double pt_var = pt_wresol;

    if (updn == "up") {
        pt_var = pt_woresol * (1 + (k + k_unc) * std_x_rndm);
    } else if (updn == "down") {
        pt_var = pt_woresol * (1 + (k - k_unc) * std_x_rndm);
    } else {
        std::cout << "ERROR: updn must be 'up' or 'down'" << std::endl; 
    }

    if (pt_var / pt_woresol > 2 || pt_var / pt_woresol < 0.1 || pt_var < 0) {
        pt_var = pt_woresol;
    }

    return pt_var;
}

double pt_scale(bool is_data, double pt, double eta, double phi, int charge,
                double low_pt_threshold) {
    const auto &cset = MuonScaleCorrectionSet();
    std::string dtmc = is_data ? "data" : "mc";

    double a = cset.at("a_" + dtmc)->evaluate({eta, phi, "nom"});
    double m = cset.at("m_" + dtmc)->evaluate({eta, phi, "nom"});
    if (pt < low_pt_threshold) return pt;

    return 1. / (m / pt + charge * a);
}

double pt_scale_var(double pt, double eta, double phi, int charge,
                    std::string updn) {
    const auto &cset = MuonScaleCorrectionSet();
    double stat_a = cset.at("a_mc")->evaluate({eta, phi, "stat"});
    double stat_m = cset.at("m_mc")->evaluate({eta, phi, "stat"});
    double stat_rho = cset.at("m_mc")->evaluate({eta, phi, "rho_stat"});

    double unc = pt * pt *
                 std::sqrt(stat_m * stat_m / (pt * pt) + stat_a * stat_a +
                           2 * charge * stat_rho * stat_m / pt * stat_a);

    double pt_var = pt;
    if (updn == "up") {
        pt_var = pt + unc;
    } else if (updn == "down") {
        pt_var = pt - unc;
    }

    return pt_var;
}
