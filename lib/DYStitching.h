#ifndef LIB_DYSTITCHING_H
#define LIB_DYSTITCHING_H

// DY stitching cells, shared by HmmAnalyzer (pre-selection sums of genWeight per cell), CreateTuple
// (per-event stitch_weight lookup) and scripts/compute_DY_stitching.py (fractions per cell, which
// hardcodes the same layout).
//
// All DY is aMC@NLO FxFx:
//   J_p : DYto2{L,Mu}-2Jets MLL-50 binned in the Born parton multiplicity p = LHE_NpNLO (0, 1, 2)
//   U   : DYto2Mu-2Jets MLL-105to160 (all p)
//   F   : DYto2Mu-2Jets MLL-105to160 VBFFilter (all p, only kept where the emulated filter passes)
// Outside W = {LHE mumu mll in [105, 160)} only J_p contributes (weight 1). Inside W the samples covering
// a cell (p, R), R = emulated VBF filter pass, are combined with effective-luminosity fractions.
//
// Cell index (also the bin index - 1 of h_sumOfgenWeight_stitchCells):
//   0           : outside W, or not a mumu event at LHE level
//   1 + 2p + R  : inside W, p = 0, 1, 2 and R = 0, 1 (cells 1..6)
//   7           : inside W with p outside 0..2 (should be empty for FxFx samples)
namespace dy_stitch {

constexpr float MLL_LOW = 105.;
constexpr float MLL_HIGH = 160.;
constexpr int N_PARTON_BINS = 3;
constexpr int N_CELLS = 8;
constexpr int CELL_OUTSIDE_WINDOW = 0;
constexpr int CELL_UNKNOWN_MULTIPLICITY = 7;

inline bool InWindow(float lhe_mll) { return lhe_mll >= MLL_LOW && lhe_mll < MLL_HIGH; }

inline int Cell(float lhe_mll, int n_partons, bool pass_VBF_filter) {
    if (!InWindow(lhe_mll))
        return CELL_OUTSIDE_WINDOW;
    if (n_partons < 0 || n_partons >= N_PARTON_BINS)
        return CELL_UNKNOWN_MULTIPLICITY;
    return 1 + 2 * n_partons + (pass_VBF_filter ? 1 : 0);
}

} // namespace dy_stitch

#endif
