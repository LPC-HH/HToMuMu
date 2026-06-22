#pragma once

#include <nlohmann/json.hpp>
#include <correction.h>

#include <iostream>
#include <fstream>
#include <string>
#include <optional>
#include <vector>
#include <stdexcept>
#include <unordered_map>
#include <map>
#include <memory>
#include <utility>
#include <mutex>

namespace JecConfigReader {

/// Jet collection kind
enum class JetKind { AK4, AK8 };

/// File locations for config JSONs
struct ConfigPaths {
    std::string ak4 = "JecConfigAK4.json";
    std::string ak8 = "JecConfigAK8.json";
};

/// Small PODs kept public for ergonomic access
struct JesDataRefs {
    std::shared_ptr<correction::CorrectionSet> cs;
    correction::Correction::Ref l1FastJet;
    correction::Correction::Ref l2Relative;
    correction::Correction::Ref l2l3Residual;  // required for Data
};

struct JesMcRefs {
    std::shared_ptr<correction::CorrectionSet> cs;
    correction::Correction::Ref l1FastJet;
    correction::Correction::Ref l2Relative;
};

struct JerMcRefs {
    std::shared_ptr<correction::CorrectionSet> cs;
    correction::Correction::Ref ptResolution;
    correction::Correction::Ref scaleFactor;
    std::optional<correction::Correction::Ref> sfUncertainty;
};

struct JerBin { double etaMin{}, etaMax{}, ptMin{}, ptMax{}; };

struct JesUncSetRefs {
    // CMS_name -> Correction::Ref
    std::map<std::string, correction::Correction::Ref> full;
    std::map<std::string, correction::Correction::Ref> reduced;
    std::map<std::string, correction::Correction::Ref> total;
};

struct JerUncSets {
    // label -> bin
    std::map<std::string, JerBin> full;
    std::map<std::string, JerBin> total;
};

/// Main class that owns paths, caches, and exposes query methods
class JecConfig {
public:
    /// Construct with config paths and optional JER smearing JSON path
    explicit JecConfig(ConfigPaths paths,
                       std::string jerSmearPath = "../jer_smear.json.gz")
      : paths_(std::move(paths)), jerSmearPath_(std::move(jerSmearPath)) {}

    JecConfig(const JecConfig&)            = delete;
    JecConfig& operator=(const JecConfig&) = delete;
    JecConfig(JecConfig&&)                 = delete;
    JecConfig& operator=(JecConfig&&)      = delete;

    // -------------------------------
    // Global-like default instance
    // -------------------------------
    static void setDefaultPaths(const ConfigPaths& p);
    static void setDefaultJerSmearPath(const std::string& p);
    static JecConfig& defaultInstance();

    // -------------------------------
    // JER smearing (json-based RNG (Random Number Generator)
    // -------------------------------
    [[nodiscard]] correction::Correction::Ref getJerSmearRef();
    [[nodiscard]] std::shared_ptr<correction::CorrectionSet> getJerSmearCorrectionSet();

    // -------------------------------
    // JERC path (shared)
    // -------------------------------
    [[nodiscard]] std::string getJercJsonPath(const std::string& year, JetKind kind);

    // -------------------------------
    // DATA: JesNominal → era -> refs (shared)
    // -------------------------------
    [[nodiscard]] std::map<std::string, JesDataRefs>
    getJesNominalDataRefs(const std::string& year, JetKind kind);

    [[nodiscard]] JesDataRefs
    getJesNominalDataEraRef(const std::string& year,
                            const std::string& era,
                            JetKind kind);

    // -------------------------------
    // MC: JesNominal / JerNominal → refs (shared)
    // -------------------------------
    [[nodiscard]] JesMcRefs  getJesNominalMcRefs(const std::string& year, JetKind kind);
    [[nodiscard]] JerMcRefs  getJerNominalMcRefs(const std::string& year, JetKind kind);

    // -------------------------------
    // MC: JES uncertainty sets → refs (shared)
    // -------------------------------
    [[nodiscard]] JesUncSetRefs getJesUncSetRefsMc(const std::string& year, JetKind kind);

    // -------------------------------
    // MC: JER uncertainty sets → bins (shared)
    // -------------------------------
    [[nodiscard]] JerUncSets getJerUncSetsMc(const std::string& year, JetKind kind);

    // -------------------------------
    // Thin AK4/AK8 wrappers
    // -------------------------------
    [[nodiscard]] std::string getJercJsonPathAK4(const std::string& year) {
        return getJercJsonPath(year, JetKind::AK4);
    }
    [[nodiscard]] std::string getJercJsonPathAK8(const std::string& year) {
        return getJercJsonPath(year, JetKind::AK8);
    }

    [[nodiscard]] std::map<std::string, JesDataRefs>
    getJesNominalDataAK4Ref(const std::string& year) {
        return getJesNominalDataRefs(year, JetKind::AK4);
    }
    [[nodiscard]] std::map<std::string, JesDataRefs>
    getJesNominalDataAK8Ref(const std::string& year) {
        return getJesNominalDataRefs(year, JetKind::AK8);
    }

    [[nodiscard]] JesDataRefs
    getJesNominalDataEraAK4Ref(const std::string& year, const std::string& era) {
        return getJesNominalDataEraRef(year, era, JetKind::AK4);
    }
    [[nodiscard]] JesDataRefs
    getJesNominalDataEraAK8Ref(const std::string& year, const std::string& era) {
        return getJesNominalDataEraRef(year, era, JetKind::AK8);
    }

    [[nodiscard]] JesMcRefs getJesNominalMcAK4Ref(const std::string& year) {
        return getJesNominalMcRefs(year, JetKind::AK4);
    }
    [[nodiscard]] JesMcRefs getJesNominalMcAK8Ref(const std::string& year) {
        return getJesNominalMcRefs(year, JetKind::AK8);
    }

    [[nodiscard]] JerMcRefs getJerNominalMcAK4Ref(const std::string& year) {
        return getJerNominalMcRefs(year, JetKind::AK4);
    }
    [[nodiscard]] JerMcRefs getJerNominalMcAK8Ref(const std::string& year) {
        return getJerNominalMcRefs(year, JetKind::AK8);
    }

    [[nodiscard]] JesUncSetRefs getJesUncSetsMcAK4Ref(const std::string& year) {
        return getJesUncSetRefsMc(year, JetKind::AK4);
    }
    [[nodiscard]] JesUncSetRefs getJesUncSetsMcAK8Ref(const std::string& year) {
        return getJesUncSetRefsMc(year, JetKind::AK8);
    }

    [[nodiscard]] JerUncSets getJerUncSetsMcAK4(const std::string& year) {
        return getJerUncSetsMc(year, JetKind::AK4);
    }
    [[nodiscard]] JerUncSets getJerUncSetsMcAK8(const std::string& year) {
        return getJerUncSetsMc(year, JetKind::AK8);
    }

private:
    // ---------- helpers ----------
    [[nodiscard]] const nlohmann::json& cfg(JetKind kind);
    [[nodiscard]] const nlohmann::json& requireYear(const nlohmann::json& cfgFile,
                                                    const std::string& year) const;
    [[nodiscard]] const nlohmann::json& requireYear(const std::string& year,
                                                    JetKind kind);
    [[nodiscard]] static std::string requireString(const nlohmann::json& j, const char* key);
    [[nodiscard]] static std::optional<std::string> optionalString(const nlohmann::json& j,
                                                                   const char* key);

    [[nodiscard]] static correction::Correction::Ref
    safeAt(const std::shared_ptr<correction::CorrectionSet>& cs, const std::string& name);

    [[nodiscard]] std::shared_ptr<correction::CorrectionSet>
    loadCsCached(const std::string& path);

private:
    // instance-scoped configuration
    ConfigPaths paths_;
    std::string jerSmearPath_;

    // caches (per instance)
    std::unordered_map<std::string, nlohmann::json> cfgCache_;  // path -> json
    std::map<std::string, std::shared_ptr<correction::CorrectionSet>> csCache_; // file -> CS

    // JER smear CS (lazy)
    std::shared_ptr<correction::CorrectionSet> jerSmearCs_;

    // guarding lazy loads
    std::mutex m_;

    // --------- defaults for singleton (Cling-safe, no call_once) ----------
    static ConfigPaths& defaults_paths_();
    static std::string& defaults_jer_path_();
    static bool&        instance_constructed_();
};

} // namespace JecConfigReader
