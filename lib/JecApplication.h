#pragma once
#include <correction.h>

#include <cmath>
#include <optional>
#include <string>
#include <unordered_set>
#include <vector>

#include <TLorentzVector.h>
#include <TVector2.h>

#include "JecConfigReader.h"   

namespace JecApplication {

// -------- Utilities (headers only) --------
inline bool hasPhiDependentL2(const std::string& year) {
    return (year == "2023Post" || year == "2024" || year == "2025");
}
inline bool requiresRunBasedResidual(const std::string& year) {
    return (
            year == "2016Pre" || year == "2016Post" ||
            year == "2017" || year == "2018" ||
            year == "2022Pre" || year == "2022Post" ||
            year == "2023Pre" || year == "2023Post" || 
            year == "2024" || year == "2025"
           );
}
inline bool usesPuppiMet(const std::string& year) {
    static const std::unordered_set<std::string> years{
        "2022Pre", "2022Post", "2023Pre", "2023Post", "2024", "2025"
    };
    return years.count(year) != 0;
}
inline double deltaR(double eta1, double phi1, double eta2, double phi2) {
    const double dEta = eta1 - eta2;
    const double dPhi = TVector2::Phi_mpi_pi(phi1 - phi2);
    return std::sqrt(dEta * dEta + dPhi * dPhi);
}

// -------- Input PODs --------
struct JesInputs {
    double pt{0.0};         
    double eta{0.0};
    double phi{0.0};
    double area{0.0};
    double rho{0.0};
    double rawFactor{0.0};  
};

struct JerInputs {
    bool   hasGen{false};
    double genPt{0.0};
    double genEta{0.0};
    double genPhi{0.0};
    double rho{0.0};
    unsigned long long event{0};
    double maxDr{0.2};      // ~0.2 (AK4), ~0.4–0.8 (AK8)
};

struct JetForMet {
    double phi{0.0};
    double eta{0.0};
    double area{0.0};
    double rawPt{0.0};
    double muonSubtrFactor{0.0};
    double chEmEf{0.0};
    double neEmEf{0.0};
};

struct MetInputs {
    double metPt{0.0};
    double metPhi{0.0};
};

struct SystematicOptions {
    // JER: "nom" | "up" | "down"
    std::string jerVar{"nom"};
    std::optional<JecConfigReader::JerBin> jerRegion{std::nullopt};

    // JES (MC only): provide the correction ref and direction ("Up"/"Down")
    std::optional<correction::Correction::Ref> jesSystRef{};
    std::string jesSystVar{};   // "Up" or "Down"
};

// -------- Handles & context --------
struct JesHandles {
    correction::Correction::Ref l1FastJet;
    correction::Correction::Ref l2Relative;
    std::optional<correction::Correction::Ref> l2l3Residual; // Data only
};

struct JerHandles {
    std::optional<correction::Correction::Ref> ptResolution; // MC only
    std::optional<correction::Correction::Ref> scaleFactor;  // MC only
    std::optional<correction::Correction::Ref> sfUncertainty; // MC only, new split JER SF uncertainty
    correction::Correction::Ref smear;                       // always (json-based RNG)
};

struct JecContext {
    std::string year{};
    bool isData{false};
    std::optional<double> runNumber{std::nullopt};
    bool isDebug{false};
    JesHandles jes{};
    JerHandles jer{};
};

// ======================================================
// Class: Applier (stateless compute API; context-owned)
// ======================================================
class Applier {
public:
    // Factory builders (context creation)
    static Applier DataAK4(JecConfigReader::JecConfig& cfg, const std::string& year,
                           const std::string& era, bool debug=false,
                           std::optional<double> runNumber=std::nullopt);
    static Applier DataAK8(JecConfigReader::JecConfig& cfg, const std::string& year,
                           const std::string& era, bool debug=false,
                           std::optional<double> runNumber=std::nullopt);
    static Applier McAK4(JecConfigReader::JecConfig& cfg, const std::string& year, bool debug=false);
    static Applier McAK8(JecConfigReader::JecConfig& cfg, const std::string& year, bool debug=false);

    // Access context
    const JecContext& context() const { return ctx_; }

    // -------- Core computations (no setters; all inputs-by-arg) --------

    // 1) JES nominal multiplicative factor
    double jesFactorNominal(const JesInputs& j) const;

    // 2) One JES component systematics multiplicative factor on top of ptAfterJes
    static double jesComponentSyst(const correction::Correction::Ref& systRef,
                                   const std::string& var,   // "Up"|"Down"
                                   double eta,
                                   double ptAfterJes,
                                   bool isDebug=false);

    // 3) JER multiplicative factor (expects jAfterJes.pt is post-JES)
    double jerFactor(const JesInputs& jAfterJes,
                     const JerInputs& jer,
                     const SystematicOptions& syst = {}) const;

    // 4) Type-1 MET correction
    TLorentzVector correctedMet(const MetInputs& met,
                                const std::vector<JetForMet>& jets,
                                const std::vector<JerInputs>& jers, // same size for MC
                                double rhoForJets,
                                const SystematicOptions& syst = {}) const;

private:
    explicit Applier(JecConfigReader::JecConfig& cfg, JecContext ctx)
      : cfg_(cfg), ctx_(std::move(ctx)) {}

    // Internal helpers for building contexts
    static JecContext makeContextData(JecConfigReader::JecConfig& cfg,
                                      const std::string& year,
                                      const std::string& era,
                                      bool debug,
                                      std::optional<double> run,
                                      bool isAK8);
    static JecContext makeContextMc(JecConfigReader::JecConfig& cfg,
                                    const std::string& year,
                                    bool debug,
                                    bool isAK8);

private:
    JecConfigReader::JecConfig& cfg_;
    JecContext       ctx_;
};

} // namespace JecApplication
