#include "JecConfigReader.h"

namespace JecConfigReader {

// -------------------------------
// Static defaults (singleton support)
// -------------------------------
ConfigPaths& JecConfig::defaults_paths_() {
    static ConfigPaths p; // defaults can be overridden before first construction
    return p;
}
std::string& JecConfig::defaults_jer_path_() {
    static std::string p = "jer_smear.json.gz";
    return p;
}
bool& JecConfig::instance_constructed_() {
    static bool v = false;
    return v;
}

void JecConfig::setDefaultPaths(const ConfigPaths& p) {
    // Allow changing defaults only before the singleton is constructed
    if (!instance_constructed_()) {
        defaults_paths_() = p;
    } else {
        // optional: std::cerr << "[JecConfig] setDefaultPaths ignored after first use\n";
    }
}

void JecConfig::setDefaultJerSmearPath(const std::string& p) {
    if (!instance_constructed_()) {
        defaults_jer_path_() = p;
    } else {
        // optional: std::cerr << "[JecConfig] setDefaultJerSmearPath ignored after first use\n";
    }
}

JecConfig& JecConfig::defaultInstance() {
    static JecConfig inst{defaults_paths_(), defaults_jer_path_()};
    instance_constructed_() = true;
    return inst;
}

// -------------------------------
// Private helpers
// -------------------------------
const nlohmann::json& JecConfig::cfg(JetKind kind) {
    const std::string& path = (kind == JetKind::AK4) ? paths_.ak4 : paths_.ak8;

    if (auto it = cfgCache_.find(path); it != cfgCache_.end())
        return it->second;

    std::lock_guard<std::mutex> lock(m_);
    if (auto it = cfgCache_.find(path); it != cfgCache_.end())
        return it->second;

    std::ifstream f(path);
    if (!f.is_open())
        throw std::runtime_error("Cannot open JSON config: " + path);

    nlohmann::json j; f >> j;
    auto [it2, _] = cfgCache_.emplace(path, std::move(j));
    return it2->second;
}

const nlohmann::json& JecConfig::requireYear(const nlohmann::json& cfgFile,
                                             const std::string& year) const {
    auto it = cfgFile.find(year);
    if (it == cfgFile.end() || !it->is_object())
        throw std::runtime_error("Year key not found or not an object in cfgFile: " + year);
    return *it;
}
const nlohmann::json&
JecConfig::requireYear(const std::string& year, JetKind kind){
    // 1) Try the primary config (AK4 or AK8, depending on kind)
    const auto& primaryCfg = cfg(kind);
    if (auto it = primaryCfg.find(year);
        it != primaryCfg.end() && it->is_object()) {
        return *it;
    }

/*
    // 2) Fallback: if AK8 is missing this year, try AK4
    if (kind == JetKind::AK8) {
        const auto& fallbackCfg = cfg(JetKind::AK4);
        if (auto it2 = fallbackCfg.find(year);
            it2 != fallbackCfg.end() && it2->is_object()) {
            //std::cerr << "[JecConfig] Warning: AK8 JEC config for year "
            //          << year << " not found. Falling back to AK4.\n";
            return *it2;
        }
    }
*/

    // 3) Nothing found → hard error
    throw std::runtime_error(
        "JecConfig::requireYear: year \"" + year +
        "\" not found for jet kind " +
        std::string(kind == JetKind::AK4 ? "AK4" : "AK8") +
        " (and AK8→AK4 fallback failed).");
}


std::string JecConfig::requireString(const nlohmann::json& j, const char* key) {
    auto it = j.find(key);
    if (it == j.end() || !it->is_string())
        throw std::runtime_error(std::string("Missing required string key: ") + key);
    return it->get<std::string>();
}

std::optional<std::string> JecConfig::optionalString(const nlohmann::json& j, const char* key) {
    auto it = j.find(key);
    if (it == j.end() || it->is_null()) return std::nullopt;
    if (!it->is_string())
        throw std::runtime_error(std::string("Optional key must be a string when present: ") + key);
    return it->get<std::string>();
}

correction::Correction::Ref
JecConfig::safeAt(const std::shared_ptr<correction::CorrectionSet>& cs,
                  const std::string& name) {
    try { return cs->at(name); }
    catch (const std::exception& e) {
        throw std::runtime_error("[JecConfig::safeAt]: Failed to retrieve correction \"" + name + "\": " + std::string(e.what()));
    }
}

std::shared_ptr<correction::CorrectionSet>
JecConfig::loadCsCached(const std::string& path) {
    if (auto it = csCache_.find(path); it != csCache_.end())
        return it->second;

    std::lock_guard<std::mutex> lock(m_);
    if (auto it = csCache_.find(path); it != csCache_.end())
        return it->second;

    using CS = correction::CorrectionSet;

    // correctionlib returns unique_ptr; promote to shared_ptr
    std::unique_ptr<CS> up = CS::from_file(path);
    std::shared_ptr<CS> sp(std::move(up));

    auto [it2, _] = csCache_.emplace(path, sp);
    return it2->second;
}

// -------------------------------
// JER smearing
// -------------------------------
std::shared_ptr<correction::CorrectionSet> JecConfig::getJerSmearCorrectionSet() {
    // Fast path: if already initialized, no locking needed
    if (jerSmearCs_) return jerSmearCs_;

    // Slow path: let loadCsCached handle locking + caching
    jerSmearCs_ = loadCsCached(jerSmearPath_);
    return jerSmearCs_;
}


correction::Correction::Ref JecConfig::getJerSmearRef() {
    auto cs = getJerSmearCorrectionSet();
    try { return cs->at("JERSmear"); }
    catch (const std::exception& e) {
        throw std::runtime_error(
            "Could not get correction 'JERSmear' from " + jerSmearPath_ + ": " + e.what()
        );
    }
}

// -------------------------------
// JERC path
// -------------------------------
std::string JecConfig::getJercJsonPath(const std::string& year, JetKind kind) {
    const auto& y = requireYear(year, kind);
    return requireString(y, "jercJsonPath");
}

// -------------------------------
// DATA JesNominal
// -------------------------------
std::map<std::string, JesDataRefs>
JecConfig::getJesNominalDataRefs(const std::string& year, JetKind kind) {
    const auto& y = requireYear(year, kind);

    const auto itApply = y.find("ApplyOnData");
    if (itApply == y.end() || !itApply->is_object())
        throw std::runtime_error("ApplyOnData not found for year " + year);

    const auto& jesNom = itApply->at("JesNominal");
    if (!jesNom.is_object())
        throw std::runtime_error("ApplyOnData.JesNominal must be an object for year " + year);

    const auto jercPath = requireString(y, "jercJsonPath");
    //std::cout<<jercPath<<std::endl;
    auto cs = loadCsCached(jercPath);

    std::map<std::string, JesDataRefs> out;
    for (auto it = jesNom.begin(); it != jesNom.end(); ++it) {
        const std::string era = it.key();
        const auto& eraObj = it.value();

        const auto l1  = requireString(eraObj, "tagNameL1FastJet");
        const auto l2  = requireString(eraObj, "tagNameL2Relative");
        const auto l23 = requireString(eraObj, "tagNameL2L3Residual");

        JesDataRefs r;
        r.cs           = cs;
        r.l1FastJet    = safeAt(cs, l1);
        r.l2Relative   = safeAt(cs, l2);
        r.l2l3Residual = safeAt(cs, l23);
        out.emplace(era, std::move(r));
    }
    return out;
}

JesDataRefs
JecConfig::getJesNominalDataEraRef(const std::string& year,
                                   const std::string& era,
                                   JetKind kind) {
    auto all = getJesNominalDataRefs(year, kind);
    auto it = all.find(era);
    if (it == all.end())
        throw std::runtime_error("Era \"" + era + "\" not found for year " + year);
    return it->second;
}

// -------------------------------
// MC JesNominal / JerNominal
// -------------------------------
JesMcRefs JecConfig::getJesNominalMcRefs(const std::string& year, JetKind kind) {
    const auto& y   = requireYear(year, kind);
    const auto& mc  = y.at("ApplyOnMC");
    const auto& jes = mc.at("JesNominal");

    const auto l1 = requireString(jes, "tagNameL1FastJet");
    const auto l2 = requireString(jes, "tagNameL2Relative");

    const auto jercPath = requireString(y, "jercJsonPath");
    //std::cout<<jercPath<<std::endl;
    auto cs = loadCsCached(jercPath);

    JesMcRefs r;
    r.cs          = cs;
    r.l1FastJet   = safeAt(cs, l1);
    r.l2Relative  = safeAt(cs, l2);
    return r;
}

JerMcRefs JecConfig::getJerNominalMcRefs(const std::string& year, JetKind kind) {
    const auto& y   = requireYear(year, kind);
    const auto& mc  = y.at("ApplyOnMC");
    const auto& jer = mc.at("JerNominal");

    const auto reso = requireString(jer, "tagNamePtResolution");
    const auto sf   = requireString(jer, "tagNameJerScaleFactor");
    const auto sfUnc = optionalString(jer, "tagNameJerSFUncertainty");

    const auto jercPath = requireString(y, "jercJsonPath");
    //std::cout<<jercPath<<std::endl;
    auto cs = loadCsCached(jercPath);

    JerMcRefs r;
    r.cs           = cs;
    r.ptResolution = safeAt(cs, reso);
    r.scaleFactor  = safeAt(cs, sf);
    if (sfUnc) {
        try {
            r.sfUncertainty = safeAt(cs, *sfUnc);
        } catch (const std::exception& e) {
            std::cerr << "[JecConfig] Warning: JER SF uncertainty correction \""
                      << *sfUnc << "\" is not available in " << jercPath
                      << ". JER up/down variations will fall back to the scale-factor payload only: "
                      << e.what() << '\n';
        }
    }
    return r;
}

// -------------------------------
// MC: JES uncertainty sets → refs
// -------------------------------
JesUncSetRefs JecConfig::getJesUncSetRefsMc(const std::string& year, JetKind kind) {
    const auto& y = requireYear(year, kind);
    JesUncSetRefs s;

    const auto itMc  = y.find("ApplyOnMC");
    if (itMc == y.end() || !itMc->is_object()) return s;
    const auto itJes = itMc->find("JesUncertaintySet");
    if (itJes == itMc->end() || !itJes->is_object()) return s;

    const auto jercPath = requireString(y, "jercJsonPath");
    //std::cout<<jercPath<<std::endl;
    auto cs = loadCsCached(jercPath);

    auto fillRefs = [&](const char* key, std::map<std::string, correction::Correction::Ref>& dst) {
        auto itS = itJes->find(key);
        if (itS != itJes->end() && itS->is_object()) {
            for (auto jt = itS->begin(); jt != itS->end(); ++jt) {
                const auto cmsName = jt.key();
                const auto& v = jt.value();
                if (!v.is_string()) continue;
                dst.emplace(cmsName, safeAt(cs, v.get<std::string>()));
            }
        }
    };

    fillRefs("JesUncertaintySetFull",    s.full);
    fillRefs("JesUncertaintySetReduced", s.reduced);
    fillRefs("JesUncertaintySetTotal",   s.total);
    return s;
}

// -------------------------------
// MC: JER uncertainty sets → bins
// -------------------------------
JerUncSets JecConfig::getJerUncSetsMc(const std::string& year, JetKind kind) {
    const auto& y = requireYear(year, kind);
    JerUncSets s;

    const auto itMc  = y.find("ApplyOnMC");
    if (itMc == y.end() || !itMc->is_object()) return s;
    const auto itJer = itMc->find("JerUncertaintySet");
    if (itJer == itMc->end() || !itJer->is_object()) return s;

    auto fill = [&](const char* key, std::map<std::string, JerBin>& dst) {
        auto itS = itJer->find(key);
        if (itS != itJer->end() && itS->is_object()) {
            for (auto jt = itS->begin(); jt != itS->end(); ++jt) {
                const auto& arr = jt.value();
                if (!arr.is_array() || arr.size() != 4)
                    throw std::runtime_error(std::string("JerUncertaintySet bin must be [etaMin,etaMax,ptMin,ptMax] for key: ")+jt.key());
                dst.emplace(jt.key(), JerBin{
                    arr[0].get<double>(), arr[1].get<double>(),
                    arr[2].get<double>(), arr[3].get<double>()
                });
            }
        }
    };

    fill("JerUncertaintySetFull",  s.full);
    fill("JerUncertaintySetTotal", s.total);
    return s;
}

} // namespace JecConfigReader
