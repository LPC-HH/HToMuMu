#ifndef LIB_ZPTREWEIGHT_H
#define LIB_ZPTREWEIGHT_H

// DY boson qT (Z pT) reweighting with the DYTurbo/MC shape ratios in data/theory/qt_norm_reweight_{ZR,SB}.json
// (provenance: data/theory/README.md). Reproduces computeDYturbo of github.com/mariadalfonso/HmumuRun3
// (analysis/src/functionsObjCor.h): the gen boson mass selects the ratio (ZR: 70 < m <= 106, SB: 106 < m < 160,
// weight 1 elsewhere), qT is capped at QT_CAP, and a weight outside [W_MIN, W_MAX] is replaced by 1.
//
// HmmAnalyzer evaluates it for every MC event with a hard-process lepton pair and stores t_zpt_weight together with
// the pre-selection sums per Region() (h_sumOfgenWeight_zptRegion[_rw]); scripts/compute_DY_stitching.py turns the
// sums of the inclusive DY into one renormalization per region (stitch_zpt_norm), and CreateTuple applies weight x
// norm to the stitched DY only: the correction changes the qT shape but not the DY cross section of a region.
#include <correction.h>

#include <algorithm>
#include <memory>
#include <string>

namespace zpt_rw {

constexpr float ZR_MASS_LOW = 70.;
constexpr float ZR_MASS_HIGH = 106.;  // ZR: (70, 106], SB: (106, 160)
constexpr float SB_MASS_HIGH = 160.;
constexpr float QT_CAP = 50.;        // the ratio is evaluated at min(qT, QT_CAP)
constexpr float W_MIN = 0.01;        // weights outside [W_MIN, W_MAX] are replaced by 1
constexpr float W_MAX = 1.5;
constexpr const char *CORRECTION_NAME = "qt_norm_reweight";
constexpr const char *ZR_FILE = "./data/theory/qt_norm_reweight_ZR.json";
constexpr const char *SB_FILE = "./data/theory/qt_norm_reweight_SB.json";

// Region index, also the bin index - 1 of h_sumOfgenWeight_zptRegion[_rw] and of stitch_zpt_norm in SumGenWeight.root
constexpr int REGION_OTHER = 0;  // no gen boson, or mass outside 70-160 GeV (weight 1)
constexpr int REGION_ZR = 1;
constexpr int REGION_SB = 2;
constexpr int N_REGIONS = 3;

inline int Region(float gen_mass) {
    if (gen_mass > ZR_MASS_LOW && gen_mass <= ZR_MASS_HIGH)
        return REGION_ZR;
    if (gen_mass > ZR_MASS_HIGH && gen_mass < SB_MASS_HIGH)
        return REGION_SB;
    return REGION_OTHER;
}

class Reweighter {
  public:
    Reweighter(const std::string &zr_file = ZR_FILE, const std::string &sb_file = SB_FILE)
        : zr_set_(correction::CorrectionSet::from_file(zr_file)),
          sb_set_(correction::CorrectionSet::from_file(sb_file)),
          zr_(zr_set_->at(CORRECTION_NAME)),
          sb_(sb_set_->at(CORRECTION_NAME)) {}

    // gen_pt / gen_mass: the generator-level boson (hard-process lepton pair); negative values (no boson) give 1
    double Weight(float gen_pt, float gen_mass) const {
        const int region = Region(gen_mass);
        if (region == REGION_OTHER || gen_pt < 0)
            return 1.;
        const double qt = std::min(gen_pt, QT_CAP);
        const double w = (region == REGION_ZR ? zr_ : sb_)->evaluate({qt});
        if (w > W_MAX || w < W_MIN)
            return 1.;
        return w;
    }

  private:
    std::unique_ptr<correction::CorrectionSet> zr_set_;
    std::unique_ptr<correction::CorrectionSet> sb_set_;
    correction::Correction::Ref zr_;
    correction::Correction::Ref sb_;
};

} // namespace zpt_rw

#endif
