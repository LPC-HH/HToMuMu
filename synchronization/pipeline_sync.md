# H→μμ Run 3 — Analysis Pipeline Synchronization (up to BDT)

Nominal analysis configuration as implemented in `HToMuMu`. NanoAOD → `HmmAnalyzer` → `CreateTuple` → hadd → BDT.

## 1. Datasets

### Eras

| Era | Data runs | MC campaign | NanoAOD | L (fb⁻¹) | Golden JSON |
|---|---|---|---|---|---|
| 2022 | C–D | Run3Summer22 | v12 | 7.9804 | `Cert_Collisions2022_355100_362760_Golden.json` |
| 2022EE | E–G | Run3Summer22EE | v12 | 26.6717 | `Cert_Collisions2022_355100_362760_Golden.json` |
| 2023 | C | Run3Summer23 | v12 | 17.96 | `Cert_Collisions2023_366442_370790_Golden.json` |
| 2023BPix | D | Run3Summer23BPix | v12 | 9.68 | `Cert_Collisions2023_366442_370790_Golden.json` |
| 2024 | C–I | RunIII2024Summer24 | v15 | 109.95 | `Cert_Collisions2024_378981_386951_Golden.json` |
| 2025 | B–G | RunIII2024Summer24 | v15 | 110.63 | `Cert_Collisions2025_391658_398903_Golden.json` |
| 2026 | A–D (data only) | — | v15 | 25.84 | — |

- 2024 and 2025 MC are the **same Summer24 samples**, split by event number: 2024 keeps odd `event`, 2025 keeps even `event`.
- 2025 MC is normalised to L(2025) + L(2026).
- The golden JSON is applied to data after `HmmAnalyzer`, with `FWLiteGoodLumi`.

!!! note "To confirm"
    2026 data is merged into `Data_Combined`, but no 2026 golden JSON is mapped in the condor job scripts. `Cert_Collisions2026_401624_403937_golden.json` exists in `RazorCommon/data/Run3/`.

### Data

| Era | Dataset |
|---|---|
| 2022 | `/Muon/Run2022C-22Sep2023-v1/NANOAOD` |
| 2022 | `/Muon/Run2022D-22Sep2023-v1/NANOAOD` |
| 2022 | `/SingleMuon/Run2022C-22Sep2023-v1/NANOAOD` |
| 2022EE | `/Muon/Run2022E-22Sep2023-v1/NANOAOD` |
| 2022EE | `/Muon/Run2022F-22Sep2023-v2/NANOAOD` |
| 2022EE | `/Muon/Run2022G-22Sep2023-v1/NANOAOD` |
| 2023 | `/Muon0/Run2023C-22Sep2023_v1-v1/NANOAOD` |
| 2023 | `/Muon0/Run2023C-22Sep2023_v2-v1/NANOAOD` |
| 2023 | `/Muon0/Run2023C-22Sep2023_v3-v1/NANOAOD` |
| 2023 | `/Muon0/Run2023C-22Sep2023_v4-v1/NANOAOD` |
| 2023 | `/Muon1/Run2023C-22Sep2023_v1-v1/NANOAOD` |
| 2023 | `/Muon1/Run2023C-22Sep2023_v2-v1/NANOAOD` |
| 2023 | `/Muon1/Run2023C-22Sep2023_v3-v1/NANOAOD` |
| 2023 | `/Muon1/Run2023C-22Sep2023_v4-v2/NANOAOD` |
| 2023BPix | `/Muon0/Run2023D-22Sep2023_v1-v1/NANOAOD` |
| 2023BPix | `/Muon0/Run2023D-22Sep2023_v2-v1/NANOAOD` |
| 2023BPix | `/Muon1/Run2023D-22Sep2023_v1-v1/NANOAOD` |
| 2023BPix | `/Muon1/Run2023D-22Sep2023_v2-v1/NANOAOD` |
| 2024 | `/Muon0/Run2024C-MINIv6NANOv15-v1/NANOAOD` |
| 2024 | `/Muon0/Run2024D-MINIv6NANOv15-v1/NANOAOD` |
| 2024 | `/Muon0/Run2024E-MINIv6NANOv15-v1/NANOAOD` |
| 2024 | `/Muon0/Run2024F-MINIv6NANOv15-v1/NANOAOD` |
| 2024 | `/Muon0/Run2024G-MINIv6NANOv15-v1/NANOAOD` |
| 2024 | `/Muon0/Run2024H-MINIv6NANOv15-v1/NANOAOD` |
| 2024 | `/Muon0/Run2024I-MINIv6NANOv15-v1/NANOAOD` |
| 2024 | `/Muon0/Run2024I-MINIv6NANOv15_v2-v1/NANOAOD` |
| 2024 | `/Muon1/Run2024C-MINIv6NANOv15-v1/NANOAOD` |
| 2024 | `/Muon1/Run2024D-MINIv6NANOv15-v1/NANOAOD` |
| 2024 | `/Muon1/Run2024E-MINIv6NANOv15-v1/NANOAOD` |
| 2024 | `/Muon1/Run2024F-MINIv6NANOv15-v1/NANOAOD` |
| 2024 | `/Muon1/Run2024G-MINIv6NANOv15-v2/NANOAOD` |
| 2024 | `/Muon1/Run2024H-MINIv6NANOv15-v2/NANOAOD` |
| 2024 | `/Muon1/Run2024I-MINIv6NANOv15-v1/NANOAOD` |
| 2024 | `/Muon1/Run2024I-MINIv6NANOv15_v2-v1/NANOAOD` |
| 2025 | `/Muon0/Run2025B-PromptReco-v1/NANOAOD` |
| 2025 | `/Muon0/Run2025C-PromptReco-v1/NANOAOD` |
| 2025 | `/Muon0/Run2025C-PromptReco-v2/NANOAOD` |
| 2025 | `/Muon0/Run2025D-PromptReco-v1/NANOAOD` |
| 2025 | `/Muon0/Run2025E-PromptReco-v1/NANOAOD` |
| 2025 | `/Muon0/Run2025F-PromptReco-v1/NANOAOD` |
| 2025 | `/Muon0/Run2025F-PromptReco-v2/NANOAOD` |
| 2025 | `/Muon0/Run2025G-PromptReco-v1/NANOAOD` |
| 2025 | `/Muon1/Run2025B-PromptReco-v1/NANOAOD` |
| 2025 | `/Muon1/Run2025C-PromptReco-v1/NANOAOD` |
| 2025 | `/Muon1/Run2025C-PromptReco-v2/NANOAOD` |
| 2025 | `/Muon1/Run2025D-PromptReco-v1/NANOAOD` |
| 2025 | `/Muon1/Run2025E-PromptReco-v1/NANOAOD` |
| 2025 | `/Muon1/Run2025F-PromptReco-v1/NANOAOD` |
| 2025 | `/Muon1/Run2025F-PromptReco-v2/NANOAOD` |
| 2025 | `/Muon1/Run2025G-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon0/Run2026A-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon0/Run2026B-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon0/Run2026C-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon0/Run2026D-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon1/Run2026A-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon1/Run2026B-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon1/Run2026C-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon1/Run2026D-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon2/Run2026A-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon2/Run2026B-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon2/Run2026C-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon2/Run2026D-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon3/Run2026A-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon3/Run2026B-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon3/Run2026C-PromptReco-v1/NANOAOD` |
| 2026 | `/Muon3/Run2026D-PromptReco-v1/NANOAOD` |

### Signal

ttH 2025 is not merged.

| Era | Group | Dataset |
|---|---|---|
| 2022 | ggH | `/GluGluHto2Mu_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v3/NANOAODSIM` |
| 2022EE | ggH | `/GluGluHto2Mu_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v1/NANOAODSIM` |
| 2023 | ggH | `/GluGluHto2Mu_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2/NANOAODSIM` |
| 2023BPix | ggH | `/GluGluHto2Mu_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2/NANOAODSIM` |
| 2024 | ggH | `/GluGluH-Hto2Mu_Par-M-125_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2025 | ggH | `/GluGluH-Hto2Mu_Par-M-125_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2022 | VBF | `/VBFHto2Mu_M-125_TuneCP5_withDipoleRecoil_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v3/NANOAODSIM` |
| 2022EE | VBF | `/VBFHto2Mu_M-125_TuneCP5_withDipoleRecoil_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v3/NANOAODSIM` |
| 2023 | VBF | `/VBFHto2Mu_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2/NANOAODSIM` |
| 2023BPix | VBF | `/VBFHto2Mu_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2/NANOAODSIM` |
| 2024 | VBF | `/VBFH-Hto2Mu_Par-M-125_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2025 | VBF | `/VBFH-Hto2Mu_Par-M-125_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2022 | ttH | `/TTH_Hto2Mu_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v3/NANOAODSIM` |
| 2022EE | ttH | `/TTH_Hto2Mu_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v3/NANOAODSIM` |
| 2023 | ttH | `/TTH_Hto2Mu_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2/NANOAODSIM` |
| 2023BPix | ttH | `/TTH_Hto2Mu_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2/NANOAODSIM` |
| 2024 | ttH | `/TTH-Hto2Mu_Par-M-125_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |

### Background

| Era | Group | Dataset |
|---|---|---|
| 2022 | DY | `/DYto2Mu_MLL-120to200_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM` |
| 2022 | DY | `/DYto2Mu_MLL-50to120_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM` |
| 2022EE | DY | `/DYto2Mu_MLL-120to200_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM` |
| 2022EE | DY | `/DYto2Mu_MLL-50to120_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM` |
| 2023 | DY | `/DYto2Mu_MLL-120to200_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2/NANOAODSIM` |
| 2023 | DY | `/DYto2Mu_MLL-50to120_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2/NANOAODSIM` |
| 2023BPix | DY | `/DYto2Mu_MLL-120to200_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3/NANOAODSIM` |
| 2023BPix | DY | `/DYto2Mu_MLL-50to120_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3/NANOAODSIM` |
| 2024 | DY | `/DYto2Mu_Bin-MLL-120to200_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2024 | DY | `/DYto2Mu_Bin-MLL-50to120_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2025 | DY | `/DYto2Mu_Bin-MLL-120to200_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2025 | DY | `/DYto2Mu_Bin-MLL-50to120_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2022 | EWK | `/EWK_2L2J_TuneCH3_13p6TeV_madgraph-herwig7/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM` |
| 2022EE | EWK | `/EWK_2L2J_TuneCH3_13p6TeV_madgraph-herwig7/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM` |
| 2023 | EWK | `/EWK_2L2J_TuneCH3_13p6TeV_madgraph-herwig7/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2/NANOAODSIM` |
| 2023BPix | EWK | `/EWK_2L2J_TuneCH3_13p6TeV_madgraph-herwig7/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2/NANOAODSIM` |
| 2024 | EWK | `/EWK-2L2J_Bin-MLL-50-MJJ-120_TuneCH3_13p6TeV_madgraph-herwig7/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2025 | EWK | `/EWK-2L2J_Bin-MLL-50-MJJ-120_TuneCH3_13p6TeV_madgraph-herwig7/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2022 | TT | `/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM` |
| 2022 | TT | `/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM` |
| 2022EE | TT | `/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM` |
| 2022EE | TT | `/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM` |
| 2023 | TT | `/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2/NANOAODSIM` |
| 2023 | TT | `/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2/NANOAODSIM` |
| 2023BPix | TT | `/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3/NANOAODSIM` |
| 2023BPix | TT | `/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3/NANOAODSIM` |
| 2024 | TT | `/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3/NANOAODSIM` |
| 2024 | TT | `/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2025 | TT | `/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3/NANOAODSIM` |
| 2025 | TT | `/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2022 | DiBoson | `/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM` |
| 2022 | DiBoson | `/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM` |
| 2022 | DiBoson | `/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM` |
| 2022 | DiBoson | `/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM` |
| 2022 | DiBoson | `/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM` |
| 2022 | DiBoson | `/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM` |
| 2022EE | DiBoson | `/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM` |
| 2022EE | DiBoson | `/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM` |
| 2022EE | DiBoson | `/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM` |
| 2022EE | DiBoson | `/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM` |
| 2022EE | DiBoson | `/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM` |
| 2022EE | DiBoson | `/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2/NANOAODSIM` |
| 2023 | DiBoson | `/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v4/NANOAODSIM` |
| 2023 | DiBoson | `/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v3/NANOAODSIM` |
| 2023 | DiBoson | `/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2/NANOAODSIM` |
| 2023 | DiBoson | `/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v3/NANOAODSIM` |
| 2023 | DiBoson | `/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v3/NANOAODSIM` |
| 2023 | DiBoson | `/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v3/NANOAODSIM` |
| 2023BPix | DiBoson | `/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3/NANOAODSIM` |
| 2023BPix | DiBoson | `/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v2/NANOAODSIM` |
| 2023BPix | DiBoson | `/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v2/NANOAODSIM` |
| 2023BPix | DiBoson | `/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3/NANOAODSIM` |
| 2023BPix | DiBoson | `/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3/NANOAODSIM` |
| 2023BPix | DiBoson | `/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3/NANOAODSIM` |
| 2024 | DiBoson | `/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2024 | DiBoson | `/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2024 | DiBoson | `/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2024 | DiBoson | `/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2024 | DiBoson | `/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2024 | DiBoson | `/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2025 | DiBoson | `/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2025 | DiBoson | `/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2025 | DiBoson | `/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2025 | DiBoson | `/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2025 | DiBoson | `/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |
| 2025 | DiBoson | `/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM` |

## 2. Trigger and event filters

| Requirement | Value |
|---|---|
| HLT | `HLT_IsoMu24` |
| MET filters | `Flag_goodVertices`, `Flag_globalSuperTightHalo2016Filter`, `Flag_HBHENoiseFilter`, `Flag_HBHENoiseIsoFilter`, `Flag_EcalDeadCellTriggerPrimitiveFilter`, `Flag_BadPFMuonFilter`, `Flag_BadChargedCandidateFilter` |
| Primary vertex | `PV_npvsGood > 0` |
| Muon multiplicity | `nMuon >= 2` |

### Trigger object

| Requirement | Value |
|---|---|
| `TrigObj_id` | 13 |
| `TrigObj_filterBits` | bit 1 (`1 << 1`) = `Iso` (same in v12 and v15) |

## 3. Object selection

All muon pT cuts use the **corrected** `Muon_bsConstrainedPt` (see [Corrections](#4-corrections)).

### Muons

| Cut | Leading μ | Subleading μ |
|---|---|---|
| pT (GeV) | > 26 | > 20 |
| \|η\| | < 2.4 | < 2.4 |
| ID | `Muon_isGlobal` && `Muon_mediumId` | `Muon_isGlobal` && `Muon_mediumId` |
| Isolation | `Muon_pfRelIso04_all` < 0.25 | `Muon_pfRelIso04_all` < 0.25 |
| Charge | opposite sign | opposite sign |

| Event-level | Value |
|---|---|
| Pair choice | pair with the largest pT₁ + pT₂; leading μ is the higher-pT muon of the pair |
| Extra-muon veto | exactly 2 muons with pT > 10, \|η\| < 2.4, `isGlobal`, `looseId`, `pfRelIso04_all` < 0.25 |
| Mass window | 100 < m(μμ) < 180 GeV (corrected bsConstrained pT, m_μ = 0.1056583745 GeV) |

### Trigger matching

At least one of the two selected muons must match:

| Cut | Value |
|---|---|
| ΔR(μ, TrigObj) | < 0.1 |
| ID | `Muon_tightId` |
| Isolation | `Muon_pfRelIso04_all` < 0.15 |
| pT (GeV) | > 26 |

!!! note "To confirm"
    The muon working points differ between three places:

    - **Trigger-matched muon:** `tightId`, iso < 0.15.
    - **Selected muons:** `mediumId`, iso < 0.25.
    - **Efficiency SFs:**
        - ID: `NUM_MediumID_DEN_TrackerMuons`
        - ISO: `NUM_LoosePFIso_DEN_MediumID`
        - Trigger: `NUM_IsoMu24_DEN_CutBasedIdMedium_and_PFIsoMedium`

### Electrons (veto)

The event is rejected if any electron passes all of:

| Cut | Value |
|---|---|
| pT (GeV) | > 10 |
| \|η\| | < 2.5 |
| \|dz\| (cm) | < 1.0 |
| \|dxy\| (cm) | < 0.5 |
| ID | `Electron_mvaIso_WP90` |

### Jets (AK4 PUPPI)

All pT cuts use the corrected jet pT: JES on data and MC, JES + JER on MC.

| Cut | Value |
|---|---|
| pT (GeV) | > 15 |
| \|η\| | < 4.7 |
| ID | Tight + LepVeto (below) |
| Muon cleaning | ΔR(jet, μ₁) ≥ 0.4 and ΔR(jet, μ₂) ≥ 0.4 |

#### Jet ID — Tight

| \|η\| | NanoAOD v12 (2022–2023BPix) | NanoAOD v15 (2024–2026) |
|---|---|---|
| ≤ 2.6 | `Jet_jetId & (1<<1)` | neHEF < 0.99, neEmEF < 0.9, chMult + neMult > 1, chHEF > 0.01, chMult > 0 |
| 2.6–2.7 | `Jet_jetId & (1<<1)` | neHEF < 0.90, neEmEF < 0.99 |
| 2.7–3.0 | `Jet_jetId & (1<<1)`, neHEF < 0.99 | neHEF < 0.99 |
| > 3.0 | `Jet_jetId & (1<<1)`, neEmEF < 0.4 | neMult ≥ 2, neEmEF < 0.4 |

#### Jet ID — LepVeto

| \|η\| | Additional cuts |
|---|---|
| ≤ 2.7 | muEF < 0.8, chEmEF < 0.8 |
| > 2.7 | none |

#### Jet veto map

The **whole event** is rejected if any jet satisfies all of the following. This is checked on all jets, before the jet pT/η/ΔR(μ) selection.

| Cut | Value |
|---|---|
| ID | Tight + LepVeto |
| pT (GeV) | > 15 (corrected) |
| chEmEF + neEmEF | < 0.9 |
| \|η\| | < 5.191 |
| Map value | > 0 (`jetvetomap` key) |

| Era | Veto map tag |
|---|---|
| 2022 | `Summer22_23Sep2023_RunCD_V1` |
| 2022EE | `Summer22EE_23Sep2023_RunEFG_V1` |
| 2023 | `Summer23Prompt23_RunC_V1` |
| 2023BPix | `Summer23BPixPrompt23_RunD_V1` |
| 2024 | `Summer24Prompt24_RunBCDEFGHI_V1` |
| 2025 | `Summer24Prompt25_RunCDEFG_V1` |
| 2026 | `Summer24Prompt26_RunBCD_V1` |

### b-tagging

Algorithm: `Jet_btagPNetB` (ParticleNet), evaluated on selected jets.

| Era | Loose | Medium |
|---|---|---|
| 2022 | 0.047 | 0.245 |
| 2022EE | 0.0499 | 0.2605 |
| 2023 | 0.0358 | 0.1917 |
| 2023BPix | 0.0359 | 0.1919 |
| 2024 | 0.0365 | 0.1990 |
| 2025 | 0.0365 | 0.1990 |
| 2026 | 0.0365 | 0.1990 |

- `nbJet` counts jets above the Medium WP; `nbJet_Loose` counts jets above the Loose WP.

!!! note "To confirm"
    The 2025 and 2026 WPs are copies of 2024. The code marks them as still to be checked.

## 4. Corrections

### Files

| Correction | Applied to | File |
|---|---|---|
| Muon scale and resolution | Data, MC | `data/leptonSF/<era>/muon_scalesmearing.json.gz` |
| Muon ID / ISO / trigger efficiency | MC | `data/leptonSF/<era>/muon_Z.json.gz` |
| Pileup | MC | `data/pileup/PileupReweight_Summer<era>.root` (`npu_nominal`, `npu_up`, `npu_down`) |
| JES, JER resolution and SF | Data (JES), MC | `data/jetCorrections/<era>/jet_jerc.json.gz` |
| JER smearing | MC | `data/jetCorrections/jer_smear.json.gz` |
| Jet veto map | Data, MC | `data/jetCorrections/<era>/jetvetomaps.json.gz` |
| Golden JSON | Data | `RazorCommon/data/Run3/Cert_*.json` |

### Muons

Input: `Muon_bsConstrainedPt`. The steps are applied in this order.

| Step | Data | MC | Detail |
|---|---|---|---|
| Scale | ✓ | ✓ | pT' = 1 / (m/pT + q·a), with `a_data`/`m_data` or `a_mc`/`m_mc` evaluated at (η, φ). Applied only if pT ≥ 26 GeV. |
| Resolution smearing | — | ✓ | pT' = pT (1 + k · σ(pT, η, nTrackerLayers) · r), with k = √(k_data² − k_mc²). The random number r is seeded by (η, φ, nTrackerLayers, event, lumi). Applied only for 26 ≤ pT ≤ 200 GeV, and skipped if pT'/pT is outside 0.1–2. |
| pT error | ✓ | ✓ | `bsConstrainedPtErr` × pT_corr / pT_raw |

Efficiency SFs (MC), evaluated per muon at (corrected pT, η) from `muon_Z.json.gz`:

| SF | Key | Min pT (GeV) | Event SF |
|---|---|---|---|
| ID | `NUM_MediumID_DEN_TrackerMuons` | 20 | SF(μ₁) × SF(μ₂) |
| ISO | `NUM_LoosePFIso_DEN_MediumID` | 20 | SF(μ₁) × SF(μ₂) |
| Trigger | `NUM_IsoMu24_DEN_CutBasedIdMedium_and_PFIsoMedium` | 26 | [1 − Π(1 − ε_data)] / [1 − Π(1 − ε_MC)] |

- Below the minimum pT, the ID/ISO SF is 1 and the trigger efficiencies are 0.

### Jets

| Step | Data | MC | Detail |
|---|---|---|---|
| Undo NanoAOD JEC | ✓ | ✓ | pT_raw = `Jet_pt` × (1 − `Jet_rawFactor`) |
| L1FastJet | ✓ | ✓ | inputs: area, η, pT, ρ (`Rho_fixedGridRhoFastjetAll`) |
| L2Relative | ✓ | ✓ | φ-dependent for 2023BPix, 2024, 2025 and 2026 |
| L2L3Residual | ✓ | — | run-dependent. For 2024, evaluated at pT = 30 GeV when pT < 30 and 2.0 < \|η\| < 2.5. |
| JER | — | ✓ | correctionlib `JERSmear` hybrid: gen-matched if ΔR < 0.2 and \|pT − pT_gen\| < 3σ·pT, stochastic otherwise. For 2022–2024, unmatched jets with 2.5 < \|η\| < 3.0 are not smeared. |
| Jet mass | ✓ | ✓ | scaled by the same JES (× JER) factor |

| Era | JES (MC / Data) | JER (MC) |
|---|---|---|
| 2022 | `Summer22_22Sep2023_V4_{MC,DATA}` | `Summer22_22Sep2023_JRV2_MC` |
| 2022EE | `Summer22EE_22Sep2023_V4_{MC,DATA}` | `Summer22EE_22Sep2023_JRV2_MC` |
| 2023 | `Summer23Prompt23_V4_{MC,DATA}` | `Summer23Prompt23_RunCv1234_JRV3_MC` |
| 2023BPix | `Summer23BPixPrompt23_V4_{MC,DATA}` | `Summer23BPixPrompt23_RunD_JRV3_MC` |
| 2024 | `Summer24Prompt24_V5_{MC,DATA}` | `Summer24Prompt24_JRV2_MC` |
| 2025 | `Summer24Prompt25_V3_{MC,DATA}` | `Summer24Prompt25_JRV2_MC` |

All tags are `AK4PFPuppi`.

### Event weight (MC)

w = genWeight × w_PU(`Pileup_nTrueInt`) × SF_trig × SF_ID × SF_ISO × L × σ / Σ genWeight

- σ is in pb and L in fb⁻¹ (scaled by 1000 in the code).
- Σ genWeight is summed over the processed events, after the 2024/2025 odd/even event split.
