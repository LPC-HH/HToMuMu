# Functions for the Run 2 + Run 3 combination, see "Tutorial - Run2 in CMSSW_14 and Run2+Run3 combination.md".
# Source this file with HMM and NORM_LOGS set, and run the functions from the directory with the cards.

# <workspace.root>: prints the channel prefix of the Run 3 norms ("run3_", or "" if unlabelled), or "none" for no Run 3 channels
run3_prefix() {
  python3 - "$1" <<'PY'
import sys
import ROOT
ROOT.gErrorIgnoreLevel = ROOT.kFatal
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
names = [v.GetName() for v in ROOT.TFile.Open(sys.argv[1]).Get("w").allVars()]
norms = [n for n in names if n.startswith("shapeBkg_bkg_mass_") and n.endswith("__norm")]
print("none" if not norms else "run3_" if any(n.startswith("shapeBkg_bkg_mass_run3_") for n in norms) else "")
PY
}

range_option() {  # <workspace.root>
  local rg
  rg=$(python3 "$HMM/norm_ranges.py" $1 0.2)
  echo ${rg:+--setParameterRanges $rg}
}

# <card name>: <name>.txt -> <name>.root. With Run 3 channels, real Run 3 data is replaced by Asimov in data_obs, and the
# Run 3 norms by their sideband-scaled values. The workspace with the real data is deleted. No fit to data happens here.
build_workspace() {
  local ws=$1 raw=$1_raw.root prefix norms
  rm -f $ws.root
  text2workspace.py $ws.txt -o $raw -m 125.38 higgsMassRange=122,128 > t2w_$ws.log 2>&1 || { echo "$ws: text2workspace failed, see t2w_$ws.log" >&2; return 1; }
  prefix=$(run3_prefix $raw)
  if [ "$prefix" = none ]; then
    mv $raw $ws.root
    return
  fi
  norms=$(python3 "$HMM/sideband_norms.py" "$NORM_LOGS" "$prefix") || return 1
  combine -M GenerateOnly $raw -n _asimovgen_$ws -m 125.38 -t -1 --saveToys --expectSignal 1 --freezeParameters MH $(range_option $raw) --setParameters $norms > gen_$ws.log 2>&1 || { echo "$ws: GenerateOnly failed, see gen_$ws.log" >&2; return 1; }
  python3 "$HMM/blind_run3_workspace.py" $raw higgsCombine_asimovgen_$ws.GenerateOnly.mH125.38.123456.root $ws.root "$norms" || { rm -f $ws.root; echo "$ws: blinding failed" >&2; return 1; }
  rm -f $raw higgsCombine_asimovgen_$ws.GenerateOnly.mH125.38.123456.root
}

# <workspace>: Asimov, nothing is fitted to data
asimov() {
  combine -M Significance $1.root -n _$1_asimov -m 125.38 -t -1 --expectSignal 1 --freezeParameters MH --cminDefaultMinimizerTolerance 0.001 $(range_option $1.root) > $1_asimov.log 2>&1
}

# <workspace>: --toysFrequentist on data_obs: Run 2 data, and Asimov for Run 3
freq() {
  combine -M Significance $1.root -n _$1_freq -m 125.38 -t -1 --expectSignal 1 --freezeParameters MH --toysFrequentist --cminDefaultMinimizerTolerance 0.01 $(range_option $1.root) > $1_freq.log 2>&1
}

export -f run3_prefix range_option build_workspace asimov freq
