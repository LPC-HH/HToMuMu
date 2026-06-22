#pragma once
#include <nlohmann/json.hpp>
#include <correction.h>

#include <map>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>

namespace JvmConfigReader{

struct Jvm {
    correction::Correction::Ref ref{};  // valid if use == true
    std::string key{};
    bool use{false};
};

/**
 * @brief Jet Veto Map (JVM) config + caches.
 * - Cling-safe singleton via magic static (no std::call_once, no TLS).
 * - Per-instance mutex protects lazy loads & caches.
 * - Override default config path *before* first use if needed.
 */
class JvmConfig {
public:
    explicit JvmConfig(std::string cfgPath = "../JvmConfig.json")
        : cfgPath_(std::move(cfgPath)) {}

    JvmConfig(const JvmConfig&)            = delete;
    JvmConfig& operator=(const JvmConfig&) = delete;
    JvmConfig(JvmConfig&&)                 = delete;
    JvmConfig& operator=(JvmConfig&&)      = delete;

    // -------- Singleton --------
    static JvmConfig& defaultInstance();
    static void setDefaultConfigPath(const std::string& path);

    // -------- Instance API --------
    const std::string& configPath() const { return cfgPath_; }
    void setConfigPath(std::string path, bool reload = false);

    const nlohmann::json& config();   // lazy, cached
    void resetConfig();               // drop JSON (forces re-read)
    void clearCsCache();              // drop CorrectionSet cache

    // High-level query
    Jvm getJvmForYear(const std::string& year);

private:
    using CS = correction::CorrectionSet;

    std::shared_ptr<CS> loadCs(const std::string& file);

    // ---- singleton defaults (no call_once) ----
    static std::string& default_cfg_path_();
    static bool&        instance_constructed_();

private:
    // ---- per-instance state ----
    std::string    cfgPath_;
    bool           cfgLoaded_{false};
    nlohmann::json cfg_;

    // caches
    std::map<std::string, std::shared_ptr<CS>> csCache_;

    // guard
    std::mutex m_;
};

} // namespace JvmConfigReader

