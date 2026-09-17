# `python/fits/` — pyhf expected-significance cross-check

An **independent, binned likelihood-fit** estimate of the H→μμ expected
discovery significance, built directly from the BDT-category-split tuples. It is
a **sanity check** on the `flashggFinalFit` + Combine result, not a replacement.

| | Combine (`flashggFinalFit`) | this (`pyhf`) |
|---|---|---|
| likelihood | unbinned, parametric PDFs | binned HistFactory templates |
| background | `RooMultiPdf` envelope + discrete profiling | (A) analytic fit to data sidebands, or (B) MC templates |
| signal | sum-of-Gaussians / DCB, `MH` profiled | double Crystal Ball fit, sampled into bins |
| significance | `combine -M Significance -t -1 --expectSignal 1` | `Z = sqrt(q0)` on the μ=1 Asimov |

## Quick start

```bash
cd $CMSSW_BASE/src/HToMuMu           # must be the repo root
python3 -m venv --system-site-packages python/fits/.venv
source python/fits/.venv/bin/activate
pip install -r python/fits/requirements.txt

# headless, everything:
python -m python.fits.run_pyhf_fits --channels all --background both --save-workspace

# or the step-by-step notebook:
python -m ipykernel install --user --name hmm-pyhf --display-name hmm-pyhf
jupyter lab python/fits/pyhf_fits.ipynb        # pick the 'hmm-pyhf' kernel
```

Outputs (`python/fits/outputs/`): `significance_<method>_<channels>.csv`,
`significance_<channels>.json`, and `workspace_<method>_<channels>.json`
(a plain pyhf workspace you can re-open with `pyhf.Workspace(json.load(...))`).

## Inputs

`root_io/tuples/split_tuples/` (produced by `scripts/split_tuples.py`):

* `allData_combined.root` — `Data_13TeV_{ggHcat1..4, VBFcat1..7}`, **unweighted**.
* `ggH/output_signal_M125_13TeV_cats_pythia8.root` — `ggh_125_13TeV_<cat>`.
* `VBF/output_signal_M125_13TeV_cats_pythia8.root` — `vbf_125_13TeV_<cat>`.

Observable: `CMS_hgg_mass` (= `diMuon_bsConstrainedMass`), 110–150 GeV, 0.5 GeV bins.

**Signal normalisation:** the signal `weight` branch has the H→μμ BR *divided
back out*, so physical yield = `Σ weight · 2.176e-4`. `μ = 1` means SM H→μμ at
**~281.7 fb⁻¹** (the split tuples are the full 2022+2022EE+2023+2023BPix+2024+2025
set). Do **not** rescale with `xgb_utils.py`'s stale `luminosity["Combined"]`.

Background model B additionally reads the multi-GB upstream tuples
`root_io/tuples/BDT_score/{ggH,VBF}/BFull_SNottH/{DY,EWK,TT,DiBoson}_Combined_BFull_SNottH.root`
and re-applies the same BDT-score + category selection as `split_tuples.py`.

## Blinding

`fit_inputs.load_signal` drops all data with 120 ≤ m ≤ 130 GeV *before returning
anything* and asserts none survive. The expected significance uses an **Asimov
dataset** (`b + s(μ=1)`), where `b` in the blind window comes from the
**sideband** fit — so blinded data is never needed or seen.

## Method (see `pyhf_fits.ipynb` for the walk-through)

1. **`fit_inputs`** — load per-category `(mass, weight)` arrays.
2. **`signal_model`** — fit a double-sided Crystal Ball (fallback: 2 Gaussians)
   to the weighted ggH+VBF MC; sample into bins; make `MassScale` (±0.2%) and
   `MassReso` (±10%) shape variations.
3. **`background_model`**
   * `fit_sideband_background` — fit `exp / exp2 / pow / bern{3,4,5}` to the
     sideband bins, pick best by AIC, evaluate through the blind window;
     covariance eigen-directions → shape `histosys`; overall level is a free
     `normfactor`. `fit_sideband_all_families` returns one model per family for
     the **envelope study** (our stand-in for discrete profiling).
   * `mc_template_background` — DY+EWK+TT+DiBoson histogram + free `normfactor`
     + linear-tilt + quadratic-curvature `histosys` (no per-bin `staterror` —
     one gamma per bin is too slow for the combined fit).
4. **`workspace`** — one pyhf channel per category; samples `sig_ggH`, `sig_VBF`
   (shared POI `mu`), `background`. Asimov observation = `b + s(μ=1)`.
5. **`significance`** — `Z = sqrt(q0_Asimov)` via `pyhf.infer.test_statistics.q0`
   (this is `-2 ln L` internally, so **no extra factor of 2**). Per-category and
   combined.

## Results (as committed; `--channels all`, 0.5 GeV bins)

| | model A (sideband fit) | model B (MC template) | Combine ref |
|---|---|---|---|
| Run3 ggH+VBF combined | ~3.1 σ | higher (MC shape ~fixed) | 3.12 σ (2022–24) / ~4.8 σ (+2025) |

Model A tracks Combine closely. Model B runs high because a near-fixed MC
background shape leaves the narrow peak nowhere to hide — the standard reason
bump hunts don't use MC-template backgrounds. The spread A↔B and the
background-family envelope bracket the "background-modelling" uncertainty that
discrete profiling handles in Combine.

## Known limitations / TODO

* **No discrete profiling** — approximated by the background-family envelope.
* **MC-stat per-bin uncertainty is not in model B** (smooth tilt+curvature
  nuisances only) — matters for low-stats VBF categories.
* **Signal systematics are flat lnN placeholders** (`fit_config.SIGNAL_NORMSYS`,
  `SIGNAL_XS_NORMSYS`). To do it properly, extend `scripts/split_tuples.py` to
  carry the systematic weight branches (`pileup_weight_up/down`, the per-muon
  SF variations) and `relative_diMuon_bsConstrainedMass_error`, then replace the
  placeholders / add a per-event resolution treatment.
* **Low-stats VBF categories** (VBFcat1–2) have poorly constrained sideband fits
  — expect large per-category uncertainty there.
* Signal is split into `sig_ggH` / `sig_VBF` by yield fraction with a **shared
  shape** (ggH and VBF resolutions are very close); refine if needed.
* `MH` is effectively fixed at the MC value (~124.4–124.9 GeV from the fit, not
  125 — worth understanding separately; likely the bs-constrained mass scale).
