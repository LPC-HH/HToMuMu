#include "JecApplication.h"

#include <iostream>

namespace JecApplication {

// ---------------- Debug helper ----------------
static inline void dbg(bool on, const std::string& msg) {
    if (on) std::cout << "     " << msg << '\n';
}

// ---------------- Context builders ----------------
JecContext Applier::makeContextData(JecConfigReader::JecConfig& cfg,
                                    const std::string& year,
                                    const std::string& era,
                                    bool debug,
                                    std::optional<double> run,
                                    bool isAK8) {
    const auto byEra = isAK8 ? cfg.getJesNominalDataAK8Ref(year)
                             : cfg.getJesNominalDataAK4Ref(year);
    auto it = byEra.find(era);
    if (it == byEra.end()) {
        throw std::runtime_error("Era \"" + era + "\" not found for year " + year);
    }
    const auto& jesEra = it->second;

    JecContext ctx;
    ctx.year = year;
    ctx.isData = true;
    ctx.isDebug = debug;
    ctx.runNumber = run;
    ctx.jes = JesHandles{ jesEra.l1FastJet, jesEra.l2Relative, jesEra.l2l3Residual };
    ctx.jer = JerHandles{ std::nullopt, std::nullopt, std::nullopt, cfg.getJerSmearRef() };
    return ctx;
}

JecContext Applier::makeContextMc(JecConfigReader::JecConfig& cfg,
                                  const std::string& year,
                                  bool debug,
                                  bool isAK8) {
    const auto jes = isAK8 ? cfg.getJesNominalMcAK8Ref(year)
                           : cfg.getJesNominalMcAK4Ref(year);
    const auto jer = isAK8 ? cfg.getJerNominalMcAK8Ref(year)
                           : cfg.getJerNominalMcAK4Ref(year);

    JecContext ctx;
    ctx.year = year;
    ctx.isData = false;
    ctx.isDebug = debug;
    ctx.jes = JesHandles{ jes.l1FastJet, jes.l2Relative, std::nullopt };
    ctx.jer = JerHandles{ jer.ptResolution, jer.scaleFactor, jer.sfUncertainty, cfg.getJerSmearRef() };
    return ctx;
}

// ---------------- Factories ----------------
Applier Applier::DataAK4(JecConfigReader::JecConfig& cfg, const std::string& year,
                         const std::string& era, bool debug,
                         std::optional<double> runNumber) {
    return Applier(cfg, makeContextData(cfg, year, era, debug, runNumber, /*isAK8=*/false));
}
Applier Applier::DataAK8(JecConfigReader::JecConfig& cfg, const std::string& year,
                         const std::string& era, bool debug,
                         std::optional<double> runNumber) {
    return Applier(cfg, makeContextData(cfg, year, era, debug, runNumber, /*isAK8=*/true));
}
Applier Applier::McAK4(JecConfigReader::JecConfig& cfg, const std::string& year, bool debug) {
    return Applier(cfg, makeContextMc(cfg, year, debug, /*isAK8=*/false));
}
Applier Applier::McAK8(JecConfigReader::JecConfig& cfg, const std::string& year, bool debug) {
    return Applier(cfg, makeContextMc(cfg, year, debug, /*isAK8=*/true));
}

// ---------------- Core computations ----------------
double Applier::jesFactorNominal(const JesInputs& j) const {
    const double ptStart = j.pt;
    if (ptStart <= 0.0) return 1.0;
    // Undo NanoAOD to raw
    const double rawSf = 1.0 - j.rawFactor;
    double ptRaw = ptStart * rawSf;
    dbg(ctx_.isDebug, "JES: ptRaw=" + std::to_string(ptRaw) +
                      ", rawFactor=" + std::to_string(j.rawFactor) +
                      ", ptRaw=" + std::to_string(ptRaw));

    // L1FastJet
    double ptAfter = ptRaw;
    const double c1 = ctx_.jes.l1FastJet->evaluate({ j.area, j.eta, ptAfter, j.rho });
    ptAfter *= c1;
    dbg(ctx_.isDebug, "JES L1FastJet: c1=" + std::to_string(c1) +
                      ", ptAfter=" + std::to_string(ptAfter));

    // L2Relative
    double c2 = 1.0;
    if (hasPhiDependentL2(ctx_.year)) {
        c2 = ctx_.jes.l2Relative->evaluate({ j.eta, j.phi, ptAfter });
    } else {
        c2 = ctx_.jes.l2Relative->evaluate({ j.eta, ptAfter });
    }
    ptAfter *= c2;
    dbg(ctx_.isDebug, "JES L2Relative: c2=" + std::to_string(c2) +
                      ", ptAfter=" + std::to_string(ptAfter));

    // L2L3Residual (Data)
    if (ctx_.isData) {
        if (!ctx_.jes.l2l3Residual.has_value())
            throw std::runtime_error("Data path requires L2L3Residual handle");
        double cRes = 1.0;
        if (requiresRunBasedResidual(ctx_.year)) {
            const double run = ctx_.runNumber.value_or(0.0);
            cRes = (*ctx_.jes.l2l3Residual)->evaluate({ run, j.eta, ptAfter });
        } else {
            cRes = (*ctx_.jes.l2l3Residual)->evaluate({ j.eta, ptAfter });
        }
        ptAfter *= cRes;
        dbg(ctx_.isDebug, "JES Residuals: cRes=" + std::to_string(cRes) +
                          ", ptAfter=" + std::to_string(ptAfter));
    }

    const double scale = ptAfter / ptStart;
    dbg(ctx_.isDebug, "JES final scale=" + std::to_string(scale));
    dbg(ctx_.isDebug, std::string("pT after JES correction would be = ")
                     + std::to_string(ptAfter) + "\n");
    return scale;
}

double Applier::jesComponentSyst(const correction::Correction::Ref& systRef,
                                 const std::string& var,
                                 double eta,
                                 double ptAfterJes,
                                 bool isDebug) {
    const double scale = systRef->evaluate({ eta, ptAfterJes });
    const double factor = (var == "Up") ? (1.0 + scale) : (1.0 - scale);
    dbg(isDebug,"pt After JES = "+ std::to_string(ptAfterJes)+ 
                ", JES syst: var=" + var +
                 ", scale=" + std::to_string(scale) +
                 ", factor=" + std::to_string(factor));
    return factor;
}

double Applier::jerFactor(const JesInputs& jAfterJes,
                          const JerInputs& jer,
                          const SystematicOptions& syst) const {
    // Optional region gate
    const auto inRegion = [&](const JecConfigReader::JerBin& b) {
        const double aeta = std::fabs(jAfterJes.eta);
        return (aeta >= b.etaMin && aeta < b.etaMax &&
                jAfterJes.pt >= b.ptMin && jAfterJes.pt < b.ptMax);
    };
    const std::string useVar =
        (syst.jerRegion && !inRegion(*syst.jerRegion)) ? "nom" : syst.jerVar;

    if (!ctx_.jer.ptResolution || !ctx_.jer.scaleFactor) {
        // Data path or missing JER: no effect
        return 1.0;
    }

    const double reso = (*ctx_.jer.ptResolution)->evaluate({ jAfterJes.eta, jAfterJes.pt, jAfterJes.rho });

    auto evalScaleFactor = [&](const std::string& var) {
        try {
            return (*ctx_.jer.scaleFactor)->evaluate({ jAfterJes.eta, jAfterJes.pt });
        } catch (const std::exception&) {
            if (usesPuppiMet(ctx_.year)) {
                return (*ctx_.jer.scaleFactor)->evaluate({ jAfterJes.eta, jAfterJes.pt, var });
            }
            return (*ctx_.jer.scaleFactor)->evaluate({ jAfterJes.eta, var });
        }
    };

    double sf = 1.0;
    double sfUnc = 0.0;
    if (ctx_.jer.sfUncertainty) {
        sf = evalScaleFactor("nom");
        sfUnc = (*ctx_.jer.sfUncertainty)->evaluate({ jAfterJes.eta, jAfterJes.pt });
        if (useVar == "up") {
            sf = sf*(1+sfUnc);
        } else if (useVar == "down") {
            sf = sf*(1-sfUnc);
        }
    } else {
        sf = evalScaleFactor(useVar);
    }

    dbg(ctx_.isDebug, "JER inputs: useVar=" + useVar +
                      ", pT=" + std::to_string(jAfterJes.pt) +
                      ", reso=" + std::to_string(reso) +
                      ", sf=" + std::to_string(sf) +
                      ", sfUnc=" + std::to_string(sfUnc));

    bool matched = false;
    double genPtForSmear = -1.0;
    if (jer.hasGen) {
        const double dR = deltaR(jAfterJes.eta, jAfterJes.phi, jer.genEta, jer.genPhi);
        if (dR < jer.maxDr && std::abs(jAfterJes.pt - jer.genPt) < 3.0 * reso * jAfterJes.pt) {
            matched = true;
            genPtForSmear = jer.genPt;
        }
        dbg(ctx_.isDebug, "JER match: hasGen=1, dR=" + std::to_string(dR) +
                          ", matched=" + std::string(matched ? "1" : "0"));
    } else {
        dbg(ctx_.isDebug, "JER match: hasGen=0");
    }

    std::vector<correction::Variable::Type> vals;
    vals.reserve(7);
    vals.emplace_back(static_cast<double>(jAfterJes.pt));   // JetPt
    vals.emplace_back(static_cast<double>(jAfterJes.eta));  // JetEta
    vals.emplace_back(static_cast<double>(genPtForSmear));  // GenPt or -1
    vals.emplace_back(static_cast<double>(jAfterJes.rho));  // Rho
    vals.emplace_back(static_cast<int>(jer.event));         // EventID
    vals.emplace_back(static_cast<double>(reso));           // JER
    vals.emplace_back(static_cast<double>(sf));             // JERSF

    const double smear = ctx_.jer.smear->evaluate(vals);
    const double corr = (std::isfinite(smear) && smear > 0.0) ? smear : 1.0;

    dbg(ctx_.isDebug, std::string("JER via correctionlib: ")
                     + (matched ? "matched" : "stochastic")
                     + ", EventID=" + std::to_string(jer.event)
                     + ", corr=" + std::to_string(corr));
    dbg(ctx_.isDebug, std::string("pT after JER smearing would be = ")
                     + std::to_string(corr * jAfterJes.pt) + "\n");
    return corr;
}

TLorentzVector Applier::correctedMet(const MetInputs& met,
                                     const std::vector<JetForMet>& jets,
                                     const std::vector<JerInputs>& jers,
                                     double rhoForJets,
                                     const SystematicOptions& syst) const {
    double metPx = met.metPt * std::cos(met.metPhi);
    double metPy = met.metPt * std::sin(met.metPhi);
    dbg(ctx_.isDebug, "====> MET start: pt=" + std::to_string(met.metPt) +
                      ", phi=" + std::to_string(met.metPhi));

    if (!ctx_.isData && jers.size() != jets.size()) {
        dbg(true, "[WARNING] jers.size() != jets.size(); JER will index-assume.");
    }

    for (std::size_t i = 0; i < jets.size(); ++i) {
        const auto& v = jets[i];

        // Muon-subtracted raw pt
        const double ptRawMinusMuon = v.rawPt * (1.0 - v.muonSubtrFactor);
        dbg(ctx_.isDebug, "\nJet[" + std::to_string(i) + "] rawMinusMuon=" + std::to_string(ptRawMinusMuon));

        // --- L1 ---
        double ptCorr = ptRawMinusMuon;
        const double c1 = ctx_.jes.l1FastJet->evaluate({ v.area, v.eta, ptCorr, rhoForJets });
        ptCorr *= c1;
        const double ptCorrL1 = ptCorr;
        dbg(ctx_.isDebug, "  L1 c1=" + std::to_string(c1) +
                          ", ptCorrL1=" + std::to_string(ptCorrL1));

        // --- L2 ---
        double c2 = 1.0;
        if (hasPhiDependentL2(ctx_.year)) {
            c2 = ctx_.jes.l2Relative->evaluate({ v.eta, v.phi, ptCorr });
        } else {
            c2 = ctx_.jes.l2Relative->evaluate({ v.eta, ptCorr });
        }
        ptCorr *= c2;
        dbg(ctx_.isDebug, "  L2 c2=" + std::to_string(c2) +
                          ", ptAfterL2=" + std::to_string(ptCorr));

        // --- Residuals (Data) ---
        if (ctx_.isData) {
            if (!ctx_.jes.l2l3Residual.has_value())
                throw std::runtime_error("Data path requires L2L3Residual handle");
            double cRes = 1.0;
            if (requiresRunBasedResidual(ctx_.year)) {
                const double run = ctx_.runNumber.value_or(0.0);
                cRes = (*ctx_.jes.l2l3Residual)->evaluate({ run, v.eta, ptCorr });
            } else {
                cRes = (*ctx_.jes.l2l3Residual)->evaluate({ v.eta, ptCorr });
            }
            ptCorr *= cRes;
            dbg(ctx_.isDebug, "  Residuals cRes=" + std::to_string(cRes) +
                              ", ptAfterRes=" + std::to_string(ptCorr));
        }

        // --- JES syst (MC only) ---
        if (!ctx_.isData && syst.jesSystRef.has_value()) {
            const double jesShift = Applier::jesComponentSyst(*syst.jesSystRef, syst.jesSystVar, v.eta, ptCorr, ctx_.isDebug);
            ptCorr *= jesShift;
            dbg(ctx_.isDebug, "  JES syst factor=" + std::to_string(jesShift) +
                              ", ptAfterJESsyst=" + std::to_string(ptCorr));
        }

        // --- JER (MC only) ---
        if (!ctx_.isData) {
            JesInputs jAfter{ptCorr, v.eta, v.phi, v.area, rhoForJets, /*raw*/0.0};
            const JerInputs& jr = (i < jers.size()) ? jers[i] : JerInputs{};
            const double sJer = jerFactor(jAfter, jr, syst);
            ptCorr *= sJer;
            dbg(ctx_.isDebug, "  JER factor=" + std::to_string(sJer) +
                              ", ptAfterJER=" + std::to_string(ptCorr));
        }

        // --- Type-1 jet selection ---
        const bool passSel = (ptCorr > 15.0 &&
                              std::abs(v.eta) < 5.2 &&
                              (v.chEmEf + v.neEmEf) < 0.9);
        dbg(ctx_.isDebug, "  passType1Sel=" + std::string(passSel ? "true" : "false"));
        if (!passSel) continue;

        // Apply (full − L1) to MET
        const double dpt = (ptCorr - ptCorrL1);
        metPx -= dpt * std::cos(v.phi);
        metPy -= dpt * std::sin(v.phi);
        dbg(ctx_.isDebug, "  dpt=" + std::to_string(dpt) +
                          ", metPx=" + std::to_string(metPx) +
                          ", metPy=" + std::to_string(metPy));
    }

    const double metPt  = std::hypot(metPx, metPy);
    const double metPhi = std::atan2(metPy, metPx);
    dbg(ctx_.isDebug, "====> MET final: pt=" + std::to_string(metPt) +
                      ", phi=" + std::to_string(metPhi));

    TLorentzVector p4; p4.SetPtEtaPhiM(metPt, 0.0, metPhi, 0.0);
    return p4;
}

} // namespace JecApplication
