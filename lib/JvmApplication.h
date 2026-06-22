#pragma once
#include <correction.h>
#include <string>

namespace JvmApplication {

struct JetInputs {
    double eta{0.0};
    double phi{0.0};
    double pt{0.0};
    int    jetId{0};
    double chEmEF{0.0};
    double neEmEF{0.0};
};

class VetoChecker {
public:
    // Selection / map limits (adjust centrally here if guidelines change)
    static constexpr double kMaxEtaInMap = 5.191;
    static constexpr double kMaxPhiInMap = 3.1415926;
    static constexpr double kMinPt       = 15.0;
    static constexpr int    kMinJetId    = 6;      // TightLepVeto ID
    static constexpr double kMaxEmFrac   = 0.90;   // (charged + neutral) EM fraction

    VetoChecker() = default;
    VetoChecker(const correction::Correction::Ref& jvmRef, std::string jvmKeyName);

    // Configure once per event/file
    void setJvm(const correction::Correction::Ref& jvmRef, std::string jvmKeyName);

    bool isConfigured() const { return jvmValid_; }
    const std::string& jvmKeyName() const { return jvmKeyName_; }

    // Stateless check (pass all jet inputs)
    bool checkJetInVetoRegion(double eta, double phi, double pt, int jetId,
                              double chEmEF, double neEmEF) const;

private:
    bool passMinimalSelection(const JetInputs& j) const;
    bool insideVeto(const JetInputs& j) const;

    correction::Correction::Ref jvmRef_{};
    std::string jvmKeyName_{};
    bool jvmValid_{false};
};

} // namespace JvmApplication

