#ifndef LIB_SYNC_EVENT_DEBUG_H
#define LIB_SYNC_EVENT_DEBUG_H
#include <cstdint>
#include <iostream>
#include <utility>

// Fixed first 20 rows of evets_missing_in_Caltech_Data2024G.csv.
// Match full event identity; no runtime CSV dependency in batch jobs.
namespace SyncEventDebug {
inline bool selected(bool ifSync, std::uint64_t run, std::uint64_t lumi,
                     std::uint64_t event) {
    if (!ifSync) return false;
    struct Key { std::uint64_t run, lumi, event; };
    static constexpr Key events[] = {
        {385836, 116, 171248703},
        {385836, 116, 169911857},
        {385836, 116, 171146115},
        {385836, 116, 171094987},
        {385836, 116, 170470864},
        {385836, 116, 171137866},
        {385836, 116, 171157908},
        {385836, 116, 170422396},
        {385836, 116, 171867410},
        {385836, 116, 172053775},
        {385836, 117, 172243354},
        {385836, 117, 173220957},
        {385836, 117, 174286307},
        {385836, 117, 172528603},
        {385836, 117, 173818166},
        {385836, 117, 173286986},
        {385836, 117, 173040691},
        {385836, 117, 173816401},
        {385836, 117, 172107336},
        {385836, 118, 175622928},
    };
    for (const auto& key : events)
        if (run == key.run && lumi == key.lumi && event == key.event) return true;
    return false;
}
class Trace {
    bool enabled_;
    const char* stage_;
    std::uint64_t run_, lumi_, event_;
public:
    Trace(bool enabled, const char* stage, std::uint64_t run,
          std::uint64_t lumi, std::uint64_t event)
        : enabled_(enabled), stage_(stage), run_(run), lumi_(lumi), event_(event) {}
    template<class... Args> void log(Args&&... args) const {
        if (!enabled_) return;
        std::cout << "[SYNC DEBUG " << stage_ << " " << run_ << ":" << lumi_
                  << ":" << event_ << "] ";
        (std::cout << ... << std::forward<Args>(args));
        std::cout << std::endl;
    }
    void check(const char* selection, bool pass) const {
        log(selection, pass ? " PASS" : " ***** event not passing the selection *****");
    }
};
}
#endif
