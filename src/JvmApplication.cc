#include "JvmApplication.h"
#include <cmath>

namespace JvmApplication {

VetoChecker::VetoChecker(const correction::Correction::Ref& jvmRef, std::string jvmKeyName) {
    setJvm(jvmRef, std::move(jvmKeyName));
}

void VetoChecker::setJvm(const correction::Correction::Ref& jvmRef, std::string jvmKeyName) {
    jvmRef_     = jvmRef;
    jvmKeyName_ = std::move(jvmKeyName);
    jvmValid_   = static_cast<bool>(jvmRef_);
}

bool VetoChecker::checkJetInVetoRegion(double eta, double phi, double pt, int jetId,
                                       double chEmEF, double neEmEF) const {
    if (!jvmValid_) return false;
    JetInputs j{eta, phi, pt, jetId, chEmEF, neEmEF};
    if (!passMinimalSelection(j)) return false;
    return insideVeto(j);
}

bool VetoChecker::passMinimalSelection(const JetInputs& j) const {
    if (std::abs(j.eta) > kMaxEtaInMap) return false;
    if (std::abs(j.phi) > kMaxPhiInMap) return false;
    //if (j.jetId < kMinJetId)            return false;
    if (j.pt < kMinPt)                  return false;
    if ((j.chEmEF + j.neEmEF) > kMaxEmFrac) return false;
    return true;
}

bool VetoChecker::insideVeto(const JetInputs& j) const {
    // By convention: 0.0 outside veto, 100.0 (or >0) inside veto
    const double val = jvmRef_->evaluate({ jvmKeyName_, j.eta, j.phi });
    return (val > 0.0);
}

} // namespace JvmApplication

