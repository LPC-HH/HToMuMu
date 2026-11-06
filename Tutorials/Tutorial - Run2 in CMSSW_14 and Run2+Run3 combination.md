### Statement
Author: Yuxiang

This tutorial runs the official Run 2 datacards in `CMSSW_14_1_0_pre4` and combines them with Run 3. It updates the [Run2 & Run3 significance combination](Tutorial%20-%20After%20BDT%20trainig%20-%20Combine%20Sig%20and%20Impact.md) tutorial, which says Run 2 doesn't work in CMSSW_14 and uses CMSSW_11_3_4 instead. Both can now run in the same CMSSW_14 area, so `CMSSW_11_3_4` isn't needed.

It doesn't cover how to make the Run 3 datacard; for that, follow [LPC-HH/flashggFinalFit](https://github.com/LPC-HH/flashggFinalFit).

# Run 2 in CMSSW_14 and the Run 2 + Run 3 combination

**Run 3 is blinded.** The `tuples_v2.4.2` data tuples contain signal-region events, so the inputs don't enforce blinding. Workspaces from `text2workspace.py` hold those events in `data_obs`, and these commands fit them:

- `--toysFrequentist`. This includes Command 3 for Run 2 + Run 3 in the older tutorial.
- `AsymptoticLimits --run expected`.
- Any observed fit, GoF or fit diagnostics.

So always build workspaces with Run 3 channels with `build_workspace` from part 2, which replaces the real Run 3 events with Asimov. Also never pass `--unblind` to the plotting scripts.

All results here are expected values. The `--toysFrequentist` commands do fit the published Run 2 data.

## What's different in CMSSW_14

The Run 2 cards need three changes. The script in part 1 makes all of them.

| Problem | Symptom | Fix |
|---|---|---|
| The cards use custom PDFs such as `RooModZPdf`, whose code doesn't compile with ROOT 6.30 | `no matching function for call to 'RooTemplateProxy...` | Build the official PDF code in its own package, `HMuMuRun2/Pdfs`, with 20 lines patched. Combine's files stay unmodified |
| Background norms in the ggH and ttH cards have zero error and a range of ±1e30 | The fit **exits with code 0** and prints a significance like `299991` | Pass a finite range, ±20% around the stored value, with `--setParameterRanges` on every fit |
| In the 13 TeV combination card, `ZH_13TeV` uses `qqZH_13TeV` before it's defined | `text2workspace.py` fails | Swap the two lines |

**About the 20 patched lines:** lines like `m("m", "m", this, 91.2)` look like they set a value, but the fourth argument is `bool valueServer`. Old ROOT silently converted `91.2` to `true`, and `evaluate()` uses its own default values when `m` isn't connected. The patch writes that conversion out as `static_cast<bool>(91.2)`, so behaviour doesn't change: PDF values at 5 mass points are identical between CMSSW_11 and CMSSW_14.

**About the ranges:** they live on the command line, not in the workspace, so every fit needs them. VBF and VH have no such parameters. Because a broken fit still exits with 0, always check the value, not the exit code.

## Part 1: Run 2

### Run the script

You need lxplus (EL9), about 1 GB of disk and access to the CMS GitLab repo [HIG-19-006/datacards](https://gitlab.cern.ch/cms-analysis/hig/HIG-19-006/datacards). Then run:

```bash
export WORK=/path/to/an/empty/directory/hmumu_run2_cmssw14
export HMM=/path/to/HToMuMu/Tutorials/scripts
bash $HMM/run2_cmssw14.sh --workdir $WORK
```

It takes about 15 minutes and ends with a table of values and `ALL OK`. It can be started from any shell, with or without `cmsenv`.

It runs five stages, and you can also run them one at a time by naming them, for example `bash $HMM/run2_cmssw14.sh --workdir $WORK fit check`:

| Stage | What it does |
|---|---|
| `get` | Fetches 13 files from HIG-19-006 at commit `feec0bb` |
| `setup` | Creates the CMSSW area with Combine `07b56c67` and CombineHarvester `94017ba5` (the `LPC-HH/flashggFinalFit` versions), and builds the patched PDFs |
| `cards` | Unpacks the cards, makes `gghvbf.txt`, swaps the two ZH lines, and builds the workspaces in `$WORK/run2_recommended` |
| `fit` | Runs the recommended significance and limit commands below on 6 workspaces |
| `check` | Compares each value with the table below, and exits with an error if one differs by more than 0.1% |

If you already have a Run 3 area, add `--cmssw-base /path/to/CMSSW_14_1_0_pre4`. The script then keeps that area's Combine, adds the PDF package and rebuilds. This is what you want for part 2.

### The recommended commands

These reproduce the paper's expected significance and limits. They use the unmodified cards at `-m 125.38`, and tolerance 0.01:

```
RANGE=$(python3 $HMM/norm_ranges.py <workspace>.root 0.2)

combine -M Significance <workspace>.root -m 125.38 -t -1 --expectSignal 1 --toysFrequentist --cminDefaultMinimizerTolerance 0.01 --setParameterRanges $RANGE

combine -M AsymptoticLimits <workspace>.root -m 125.38 --run expected --cminDefaultMinimizerTolerance 0.01 --setParameterRanges $RANGE
```

For VBF and VH `RANGE` is empty, so leave out `--setParameterRanges`.

The values should be:

| Channel | Significance | Paper | Limit, median | Paper |
|---|---|---|---|---|
| VBF | 1.77335 | 1.77 | r < 1.2227 | 1.22 |
| ggH | 1.55829 | 1.56 | r < 1.2773 | 1.28 |
| ttH | 0.542755 | 0.54 | r < 4.2031 | 4.20 |
| VH | 0.42397 | 0.42 | r < 5.1406 | 5.13 |
| Combined 13 TeV | 2.45936 | 2.46 | r < 0.8242 | 0.82 |
| ggH+VBF | 2.36162 | n/a | r < 0.8633 | n/a |

The workspaces are built with:

```
text2workspace.py <card>.txt -o <workspace>.root -m 125.38 higgsMassRange=122,128
```

To use **Combine v10.6.1**, the last version for this release, run the script with `COMBINE_REF=v10.6.1` set in a new `--workdir`. All 12 values above are identical to every printed digit.

### Notes

- **Tolerance matters for ggH.** Tolerance 0.01 is what reproduces the paper, but it isn't converged. At 0.001 the ggH limit moves from 1.2773 to 1.3477 and the combination's from 0.8242 to 0.8477, while VBF, ttH and VH don't change. Scan the tolerance before comparing ggH values across setups.
- **`-m` changes the result.** `-m` sets `MH`, and the signal cross section and branching ratio depend on it. Going from 125 to 125.38 lowers ggH and qqH signal yields by about 1.3-1.5%.
- **Don't use Command 1 for Run 2 ggH.** Command 1 of the older tutorial uses the default tolerance of 0.1. Its 1.94943 for ggH is reproduced here, but the fit isn't converged: it falls to 1.7355 at tolerance 0.001. Run 2 VBF is stable.
- **The 1.57574 for Command 2 is off.** The value in the older tutorial's table comes from a fit in CMSSW_11 that stops close to the minimum. With a finite range, or at tolerance 0.001, Command 2 gives 1.5702 in CMSSW_11 as well.

### Optional: compare with the older tutorial's table at `-m 125`

The older table uses `-m 125`. The VBF templates in the input file are named for 125.38, so this needs `$MASS` replaced in the VBF card. This mixes two masses, templates at 125.38 and cross section and branching ratio at 125, so use it only for this comparison.

After the `get` and `setup` stages, in a shell with `cmsenv`:

```bash
mkdir -p $WORK/run2_m125 && cd $WORK/run2_m125
D=$WORK/hig19006/combination
cp $D/check_2020_ggh125.38.inputs.root $D/check_2020_vbf125.38.inputs.root .
zcat $D/check_2020_ggh.txt.gz > run2_ggH.txt
zcat $D/check_2020_vbf.txt.gz | sed 's/\$MASS/125.38/g' > run2_VBF.txt
combineCards.py run2_ggH.txt run2_VBF.txt > run2_ggH_VBF.txt
for c in ggH VBF ggH_VBF; do
  text2workspace.py run2_$c.txt -o run2_$c.root -m 125 higgsMassRange=122,128 > t2w_$c.log 2>&1
  RANGE=$(python3 $HMM/norm_ranges.py run2_$c.root 0.2)
  combine -M Significance run2_$c.root -n _cmd3_$c -m 125 -t -1 --expectSignal 1 --cminDefaultMinimizerTolerance 0.01 --toysFrequentist ${RANGE:+--setParameterRanges $RANGE} > cmd3_$c.log 2>&1
done
grep Significance: cmd3_*.log
```

| Channel | Command 3 here | Older table |
|---|---|---|
| ggH | 1.5702 | 1.57024 |
| VBF | 1.79575 | 1.79575 |
| ggH+VBF | 2.3868 | 2.38611 |

The last row is 0.03% off. The older value is from CMSSW_11 with no range on the norms, and changing the range moves this fit by a similar amount: ±50% gives 2.38787.

## Part 2: Run 2 + Run 3

### What you need

**One CMSSW area with both sets of PDFs.** A combined workspace needs the Run 2 PDFs and the Run 3 DY-core PDFs of `flashggFinalFit`, so use your Run 3 area and add the Run 2 PDFs in a new shell:

```bash
export WORK=/path/to/an/empty/directory/hmumu_run2_cmssw14
export HMM=/path/to/HToMuMu/Tutorials/scripts
export RUN3_AREA=/path/to/CMSSW_14_1_0_pre4     # contains src/flashggFinalFit with your Run 3 results
bash $HMM/run2_cmssw14.sh --workdir $WORK --cmssw-base $RUN3_AREA get setup
```

Starting from a CMSSW area made by part 1 also works. In that case, clone and build `flashggFinalFit` in it as in its README.

**Run 3 results from `flashggFinalFit`:** `Combine/Datacard_tutorial_All.txt`, its `Combine/Models/`, and the outputs in `Background/outdir_tutorial` and `Signal/outdir_packaged`.

Then, in every new shell, set up the environment:

```bash
export WORK=/path/to/an/empty/directory/hmumu_run2_cmssw14
export HMM=/path/to/HToMuMu/Tutorials/scripts
export RUN3_AREA=/path/to/CMSSW_14_1_0_pre4
export SCRAM_ARCH=el9_amd64_gcc12
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd $RUN3_AREA/src/flashggFinalFit
source setup.sh
export RUN3=$PWD
export COMB=$WORK/combination
export NORM_LOGS=$WORK/run3_norm_logs
source $HMM/combination_functions.sh
```

### Step 1: Get the blinded Run 3 background norms

The background norm stored in the Run 3 workspace isn't blinded. `fTest` fits the shape on the sidebands only, but sets the norm to the full data count, signal region included. The Asimov dataset is generated from this norm, so with the stored value the Run 3 expected result depends on blinded events.

The combination instead uses the sideband-scaled total of the best-fit PDF, which `makeMultipdfPlot.py` prints as `Bkg Yield Total`. The two values differ by the real signal-region count minus the one predicted from the sidebands:

```
stored norm     = sideband events + real signal-region events
Bkg Yield Total = sideband events + signal-region events predicted by the fit
```

**This potential differs from the 22 Oct 2026 slides.** The Run 3 values on those slides, including 3.05, are reproduced with the stored norm, so the slides possibly use it too. The Run 3 part of the combination uses the sideband norm, so it isn't quite the same setup.

If you already have the output of this script from your Run 3 chain as `plot_<category>.log` files, set `NORM_LOGS` to their directory. Otherwise, make them:

```bash
mkdir -p $NORM_LOGS
cd $RUN3/Plots
for c in $(python3 ../category_config.py all); do
  python3 makeMultipdfPlot.py --inputWSFile ../Background/outdir_tutorial/CMS-HGG_multipdf_$c.root --cat $c --ext tutorial --nBins 160 --mass 125.38 --inputSignalWSFile ../Signal/outdir_packaged/CMS-HGG_sigfit_packaged_$c.root --outCSV $NORM_LOGS/unused.csv > $NORM_LOGS/plot_$c.log 2>&1
done
```

### Step 2: Build the combined card and workspace

The Run 3 channels must have the label `run3`. The Run 2 part here is ggH + VBF; ttH and VH are at the end of this part.

```bash
mkdir -p $COMB && cd $COMB
D=$WORK/hig19006/combination
cp $D/check_2020_ggh125.38.inputs.root $D/check_2020_vbf125.38.inputs.root .
ln -sfn $RUN3/Combine/Models Models
cp $RUN3/Combine/Datacard_tutorial_All.txt run3_All.txt
zcat $D/check_2020_ggh.txt.gz > run2_ggH.txt
zcat $D/check_2020_vbf.txt.gz > run2_VBF.txt
combineCards.py run2ggh=run2_ggH.txt run2vbf=run2_VBF.txt > run2_All.txt
combineCards.py run2ggh=run2_ggH.txt run2vbf=run2_VBF.txt run3=run3_All.txt > comb_All.txt
build_workspace run2_All
build_workspace comb_All
```

`build_workspace` comes from [`scripts/combination_functions.sh`](scripts/combination_functions.sh). It runs `text2workspace.py` with the same options as part 1, and if the workspace has Run 3 channels, it then makes it safe to fit:

1. Generates the Asimov dataset (S+B, r=1) with `combine -M GenerateOnly`. No fit to data happens here.
2. Replaces `data_obs` for the Run 3 channels with that dataset. Run 2 channels keep their real events.
3. Sets the Run 3 norms to the sideband-scaled values of step 1.
4. Deletes the workspace that had the real Run 3 events.

The output should list the 22 channels with `ok` on each line, and then `datasets in the workspace: ['data_obs']`. Run 3 channels show only the status, without their totals.

Any fit to `data_obs` in this workspace is therefore a fit to Asimov for Run 3, and says nothing about real Run 3 data.

`flashggFinalFit` also has `Combine/replaceDataWithPseudoToy.py`, for pseudo-experiments on a whole workspace. It isn't used here, because it replaces every channel with a random toy, Run 2 data included, and generates the toy with the prefit Run 3 norms.

Run 2 ggH norms still need the range. Run 3 norms are already bounded.

### Step 3: Run the fits

```bash
cd $COMB
printf '%s\n' "asimov run2_All" "freq run2_All" "asimov comb_All" "freq comb_All" | xargs -P 4 -L 1 bash -c '"$0" "$1"'
grep Significance: *_asimov.log *_freq.log
```

The two functions run these commands, with `$RANGE` from `norm_ranges.py` as in part 1:

```
combine -M Significance comb_All.root -m 125.38 -t -1 --expectSignal 1 --freezeParameters MH --cminDefaultMinimizerTolerance 0.001 --setParameterRanges $RANGE

combine -M Significance comb_All.root -m 125.38 -t -1 --expectSignal 1 --freezeParameters MH --toysFrequentist --cminDefaultMinimizerTolerance 0.01 --setParameterRanges $RANGE
```

Each combined fit takes 5-10 minutes. The values should be:

| Setup, `-m 125.38` | Tolerance | Run 2 ggH+VBF | Run 2 + Run 3 |
|---|---|---|---|
| Asimov | 0.001 | 2.42825 | **3.93115** |
| `--toysFrequentist` on Run 2 data + Run 3 Asimov | 0.01 | 2.36162 | **3.88137** |

As a check on Run 3 on its own, this chain with DY-core PDFs on `tuples_v2.4.2` reproduces all 14 significances on the 22 Oct 2026 slides, including 3.05 for the combined categories, with the plain command of `Combine/run_sig.sh`. That check uses the stored norm, not the sideband norm of step 1.

**Which to use:** `--toysFrequentist` is what the Run 2 paper's values correspond to, so it's the one to compare with Run 2 results. Its Run 3 part isn't a true frequentist fit, because Run 3 is Asimov, so it may move at unblinding.

**Tolerance:** without `--toysFrequentist`, use 0.001 or tighter, because the fit isn't converged at larger values. At `-m 125` the Asimov combination gives:

| Tolerance | Run 2 | Run 2 + Run 3 |
|---|---|---|
| Default (0.1) | 2.62502 | 4.04466 |
| 0.01 | 2.41086 | 3.90997 |
| 0.001 | 2.47587 | 3.95014 |
| 0.0001 | 2.47599 | 3.95019 |

With `--toysFrequentist`, 0.01 and 0.001 agree: 3.88137 and 3.88117.

**Mass:** the Run 3 signal is built at 125 only, with its cross section constant and only the BR following `MH`, so `-m 125.38` isn't a fully consistent Run 3 model. At `-m 125` the combination is 3.950 (Asimov) and 3.885 (`--toysFrequentist`), so the effect is at most 0.5%. To run at `-m 125`, replace `$MASS` in the VBF card as in part 1, and change the mass in all the commands.

### Step 4: Correlate nuisances between Run 2 and Run 3

TBD. Combine correlates nuisances by name, and in the results above only `BR_hmm` and `CMS_scale_m` are shared, so theory, JES and luminosity are uncorrelated between Run 2 and Run 3.

### Step 5: Optional: include Run 2 ttH and VH

The official 13 TeV combination card has all four Run 2 channels, and goes through the same steps. The Run 2 ZH line swap from part 1 is needed here too:

```bash
cd $COMB
D=$WORK/hig19006/combination
cp $D/check_2020_*125.38.inputs.root $D/cms_hmm.inputs125.38.root .
zcat $D/cms_hmm_combination.txt.gz | awk '/^ZH_13TeV +extArg/{hold=$0; next} {print} /^qqZH_13TeV +extArg/{print hold}' > run2full.txt
combineCards.py run2full=run2full.txt run3=run3_All.txt > comb_full.txt
build_workspace comb_full
freq comb_full
grep Significance: comb_full_freq.log
```

This gives 3.9423 at tolerance 0.01, against 2.45936 for Run 2 alone.

## Not covered or not tested

- Expected limits, impacts, GoF and bias tests for the combination weren't run.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Significance like `299991` or `424264`, exit code 0 | Range option missing | Check that `python3 $HMM/norm_ranges.py <workspace>.root 0.2` prints parameters |
| `no matching function for call to 'RooTemplateProxy...` | Unpatched PDF code | Run the `setup` stage again |
| `HTTP Basic: Access denied` if you fetch the files yourself | CMSSW's `git` can't use Kerberos | Fetch in a fresh shell. The script's `get` stage handles this |
| `get` can't clone over SSH | No SSH access to GitLab | Set `HIG_URL` to a URL that works for you, in the environment |
| `combine: command not found` | New shell | Set up the environment again |
| Combined fit never finishes | Range option missing on the Run 2 ggH norms | Check as above. A combined fit without it hadn't finished after 90 minutes |
| `Invalid tool rootdict` or `Invalid tool python` during `scram b` | Harmless warnings | None |

## Where the numbers and files come from

- **Cards, inputs, PDF code:** official [HIG-19-006/datacards](https://gitlab.cern.ch/cms-analysis/hig/HIG-19-006/datacards) at `feec0bb`, under `combination/` and `ggH/ucsd/`. There's no official ggH+VBF-only card, so it's made with `combineCards.py`.
- **Run 3:** `LPC-HH/flashggFinalFit` at `8a0edee`, with `N_GGH = 6` in `category_config.py`, on `tuples_v2.4.2`.
- **Paper values:** the expected significances and limits of HIG-19-006.
