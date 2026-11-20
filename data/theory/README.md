# Theory corrections

## DY boson qT (Z pT) reweighting: `qt_norm_reweight_{ZR,SB}.json`

- **Source:** github.com/mariadalfonso/HmumuRun3, `analysis/config/THeory/`, pinned to commit
  `308618ea785b588d2fd50cdd262d2e84522fb34d` (2026-09-01). Copied unchanged.
- **Content:** correctionlib (schema v2) correction `qt_norm_reweight`. A per-event weight as a function of the
  generator-level boson qT, in 1 GeV bins up to 200 GeV and coarser above, with clamped flow.
  - Her code loads it as "DYturbo", so it is a DYTurbo (resummed theory) / MC ratio of the qT shape, normalized
    ("norm").
- **Mass regions** (generator-level boson mass):

  | file | mass range |
  |---|---|
  | `_ZR` | 70 < m ≤ 106 GeV |
  | `_SB` | 106 < m < 160 GeV |

  The weight is 1 outside 70–160 GeV.
- **How it is evaluated** (as in her `computeDYturbo`, reproduced in `lib/ZptReweight.h`):
  - at min(qT, 50 GeV);
  - a weight outside [0.01, 1.5] is replaced by 1.
- **Samples:** she applies it to the aMC@NLO FxFx DY samples only. Here CreateTuple applies it to the stitched DY
  datasets.
- **Not yet known** (ask Maria):
  - which MC sample and era is the denominator;
  - the DYTurbo order, PDF and scale choices;
  - the qT range over which the ratio was normalized;
  - whether scale-variation versions exist.
