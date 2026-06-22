#include "JvmConfigReader.h"
#include <fstream>

namespace JvmConfigReader {

// ---- singleton defaults ----
std::string& JvmConfig::default_cfg_path_() {
    static std::string p = "JvmConfig.json";
    return p;
}
bool& JvmConfig::instance_constructed_() {
    static bool v = false;
    return v;
}

JvmConfig& JvmConfig::defaultInstance() {
    static JvmConfig inst{default_cfg_path_()};
    instance_constructed_() = true;
    return inst;
}

void JvmConfig::setDefaultConfigPath(const std::string& path) {
    if (!instance_constructed_()) {
        default_cfg_path_() = path;
    } else {
        // optional: std::cerr << "[JvmConfig] setDefaultConfigPath ignored after first use\n";
    }
}

// ---- instance API ----
void JvmConfig::setConfigPath(std::string path, bool reload) {
    std::lock_guard<std::mutex> lock(m_);
    cfgPath_ = std::move(path);
    if (reload) {
        cfgLoaded_ = false;
        cfg_.clear();
    }
}

const nlohmann::json& JvmConfig::config() {
    if (cfgLoaded_) return cfg_;
    std::lock_guard<std::mutex> lock(m_);
    if (cfgLoaded_) return cfg_;

    std::ifstream f(cfgPath_);
    if (!f) {
        throw std::runtime_error(std::string("Cannot open JVM JSON config: ") + cfgPath_);
    }
    f >> cfg_;
    cfgLoaded_ = true;
    return cfg_;
}

void JvmConfig::resetConfig() {
    std::lock_guard<std::mutex> lock(m_);
    cfgLoaded_ = false;
    cfg_.clear();
}

void JvmConfig::clearCsCache() {
    std::lock_guard<std::mutex> lock(m_);
    csCache_.clear();
}

std::shared_ptr<correction::CorrectionSet>
JvmConfig::loadCs(const std::string& file) {
    if (auto it = csCache_.find(file); it != csCache_.end())
        return it->second;

    std::lock_guard<std::mutex> lock(m_);
    if (auto it = csCache_.find(file); it != csCache_.end())
        return it->second;

    // correctionlib returns unique_ptr → promote to shared_ptr
    std::unique_ptr<correction::CorrectionSet> up = correction::CorrectionSet::from_file(file);
    std::shared_ptr<correction::CorrectionSet> sp(std::move(up));
    csCache_.emplace(file, sp);
    return sp;
}

Jvm JvmConfig::getJvmForYear(const std::string& year) {
    const auto& j = config();
    const auto it = j.find(year);
    if (it == j.end()) return {}; // use=false

    const auto& y = *it;
    const std::string file = y.at("jvmFilePath").get<std::string>();
    const std::string tag  = y.at("jvmTagName").get<std::string>();
    const std::string key  = y.at("jvmKeyName").get<std::string>();

    auto cs = loadCs(file);
    return { cs->at(tag), key, true };
}

} // namespace JvmConfigReader

