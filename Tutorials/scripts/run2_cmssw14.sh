#!/bin/bash
# Get the official Run 2 H->mumu datacards (HIG-19-006), patch them for CMSSW_14, and run the recommended commands.
# See "Tutorials/Tutorial - Run2 in CMSSW_14 and Run2+Run3 combination.md".
#
# Usage: bash run2_cmssw14.sh [--workdir DIR] [--cmssw-base PATH] [--jobs N] [stage ...]
#   --workdir DIR       Where everything goes. Default: $PWD/hmumu_run2_cmssw14
#   --cmssw-base PATH   Use this existing CMSSW_14_1_0_pre4 area, for example your Run 3 one, instead of creating one.
#                       Its Combine is kept as it is; the stage only adds the Run 2 PDFs.
#   --jobs N            Parallel text2workspace and combine jobs. Default: 4
#   stage               get setup cards fit check. Default: all of them, in this order.
set -eo pipefail

WORK=$PWD/hmumu_run2_cmssw14
CMSSW_AREA=""
JOBS=4
STAGES=()
while [ $# -gt 0 ]; do
  case $1 in
    --workdir) WORK=$(realpath -m "$2"); shift 2 ;;
    --cmssw-base) CMSSW_AREA=$(realpath -m "$2"); shift 2 ;;
    --jobs) JOBS=$2; shift 2 ;;
    get|setup|cards|fit|check) STAGES+=("$1"); shift ;;
    *) echo "Unknown argument: $1. See the top of this script for the usage." >&2; exit 2 ;;
  esac
done
[ ${#STAGES[@]} -gt 0 ] || STAGES=(get setup cards fit check)

SCRIPTS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RELEASE=CMSSW_14_1_0_pre4
CMSSW_AREA=${CMSSW_AREA:-$WORK/$RELEASE}
export MH=125.38
export FITS=$WORK/run2_recommended
HIG=$WORK/hig19006
HIG_URL=${HIG_URL:-ssh://git@gitlab.cern.ch:7999/cms-analysis/hig/HIG-19-006/datacards.git}
HIG_COMMIT=feec0bbab535f7d1e63f9721c972ee6bf5da9b93  # latest commit of the official repo, 5 Oct 2020
COMBINE_REF=${COMBINE_REF:-07b56c67ba6e4304b42c3a6cdba710d59c719192}  # v9.2.1-64, from the LPC-HH/flashggFinalFit README
HARVESTER_REF=94017ba5a3a657f7b88669b1a525b19d34ea41a2
CHANNELS="ggh vbf tth vh gghvbf comb"

die() { echo "ERROR: $*" >&2; exit 1; }

cms_env() {
  [ -d "$CMSSW_AREA/src" ] || die "no CMSSW area at $CMSSW_AREA, run the setup stage first"
  export SCRAM_ARCH=el9_amd64_gcc12
  source /cvmfs/cms.cern.ch/cmsset_default.sh
  cd "$CMSSW_AREA/src"
  eval "$(scramv1 runtime -sh)"
}

# CMSSW's git can't use Kerberos ("HTTP Basic: Access denied"), so this runs in a clean environment, even if the
# calling shell already did cmsenv.
system_git() {
  env -i HOME="$HOME" USER="${USER:-}" PATH=/usr/bin:/bin ${KRB5CCNAME:+KRB5CCNAME="$KRB5CCNAME"} \
    ${SSH_AUTH_SOCK:+SSH_AUTH_SOCK="$SSH_AUTH_SOCK"} git "$@"
}

stage_get() {
  mkdir -p "$WORK"
  [ -d "$HIG/.git" ] || system_git clone --filter=blob:none --no-checkout "$HIG_URL" "$HIG"
  # The whole repo is 1.3 GB. Only the 13 files used here are fetched.
  system_git -C "$HIG" sparse-checkout set --no-cone \
    /combination/check_2020_ggh.txt.gz /combination/check_2020_vbf.txt.gz \
    /combination/check_2020_tth.txt.gz /combination/check_2020_vh.txt.gz \
    /combination/check_2020_ggh125.38.inputs.root /combination/check_2020_vbf125.38.inputs.root \
    /combination/check_2020_tth125.38.inputs.root /combination/check_2020_wh125.38.inputs.root \
    /combination/check_2020_zh125.38.inputs.root \
    /combination/cms_hmm_combination.txt.gz /combination/cms_hmm.inputs125.38.root \
    '/ggH/ucsd/HMuMuRooPdfs.*'
  system_git -C "$HIG" -c advice.detachedHead=false checkout -q $HIG_COMMIT
  local n
  n=$(find "$HIG" -type f -not -path '*/.git/*' | wc -l)
  [ "$n" = 13 ] || die "expected 13 files in $HIG, found $n"
  echo "[get] 13 files at ${HIG_COMMIT:0:7}"
}

add_run2_pdfs() {
  # In their own package, so Combine's files stay unmodified. The sed points the #include at the package, and makes
  # 20 implicit double -> bool conversions explicit. ROOT 6.30 rejects them, and the behaviour doesn't change.
  local p=HMuMuRun2/Pdfs
  mkdir -p $p/interface $p/src
  cp "$HIG/ggH/ucsd/HMuMuRooPdfs.h" $p/interface/
  sed -E 's|#include "HMuMuRooPdfs.h"|#include "HMuMuRun2/Pdfs/interface/HMuMuRooPdfs.h"|; s/(this, *)(-?[0-9.]+)\)/\1static_cast<bool>(\2))/' \
    "$HIG/ggH/ucsd/HMuMuRooPdfs.cc" > $p/src/HMuMuRooPdfs.cc
  local n
  n=$(grep -c 'static_cast<bool>' $p/src/HMuMuRooPdfs.cc)
  [ "$n" = 20 ] || die "expected 20 patched lines in HMuMuRooPdfs.cc, found $n"
  echo '#include "HMuMuRun2/Pdfs/interface/HMuMuRooPdfs.h"' > $p/src/classes.h
  cat > $p/src/classes_def.xml <<'XML'
<lcgdict>
  <class name="RooSumTwoPowerLawPdf"/>
  <class name="RooPowerLawPdf"/>
  <class name="RooSumTwoExpPdf"/>
  <class name="RooExpPdf"/>
  <class name="RooModZPdf"/>
</lcgdict>
XML
  cat > $p/BuildFile.xml <<'XML'
<use name="root"/>
<use name="roofit"/>
<use name="rootdict"/>
<export>
  <lib name="1"/>
</export>
XML
}

stage_setup() {
  [ -f "$HIG/ggH/ucsd/HMuMuRooPdfs.cc" ] || die "no Run 2 PDF code in $HIG, run the get stage first"
  export SCRAM_ARCH=el9_amd64_gcc12
  source /cvmfs/cms.cern.ch/cmsset_default.sh
  if [ ! -d "$CMSSW_AREA/src" ]; then
    mkdir -p "$(dirname "$CMSSW_AREA")"
    (cd "$(dirname "$CMSSW_AREA")" && scram project -n "$(basename "$CMSSW_AREA")" CMSSW $RELEASE)
  fi
  cms_env
  if [ ! -d HiggsAnalysis/CombinedLimit ]; then
    git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
    git -C HiggsAnalysis/CombinedLimit fetch origin "$COMBINE_REF"
    git -C HiggsAnalysis/CombinedLimit -c advice.detachedHead=false checkout "$COMBINE_REF"
  fi
  if [ ! -d CombineHarvester ]; then
    bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/$HARVESTER_REF/CombineTools/scripts/sparse-checkout-https.sh)
    git -C CombineHarvester fetch origin $HARVESTER_REF
    git -C CombineHarvester -c advice.detachedHead=false checkout $HARVESTER_REF
  fi
  add_run2_pdfs
  scram b -j 8
  [ -e "$CMSSW_BASE/lib/$SCRAM_ARCH/libHMuMuRun2Pdfs.so" ] || die "the Run 2 PDF library wasn't built"
  echo "[setup] $CMSSW_BASE, Combine $(git -C HiggsAnalysis/CombinedLimit describe --tags --always)"
}

stage_cards() {
  cms_env
  mkdir -p "$FITS"
  cd "$FITS"
  local d=$HIG/combination c
  cp "$d"/check_2020_*125.38.inputs.root "$d"/cms_hmm.inputs125.38.root .
  for c in ggh vbf tth vh; do zcat "$d/check_2020_$c.txt.gz" > $c.txt; done
  combineCards.py ggh.txt vbf.txt > gghvbf.txt
  # ZH_13TeV uses qqZH_13TeV before it is defined, and without this swap text2workspace.py fails.
  zcat "$d/cms_hmm_combination.txt.gz" \
    | awk '/^ZH_13TeV +extArg/{hold=$0; next} {print} /^qqZH_13TeV +extArg/{print hold}' > comb.txt
  [ "$(zcat "$d/cms_hmm_combination.txt.gz" | wc -l)" = "$(wc -l < comb.txt)" ] || die "the ZH line swap changed the number of lines in comb.txt"
  export MH
  for c in $CHANNELS; do echo $c; done \
    | xargs -P "$JOBS" -I{} sh -c 'text2workspace.py {}.txt -o {}.root -m $MH higgsMassRange=122,128 > t2w_{}.log 2>&1 || echo "text2workspace failed for {}, see t2w_{}.log"'
  for c in $CHANNELS; do [ -s $c.root ] || die "no workspace $FITS/$c.root, see t2w_$c.log"; done
  echo "[cards] workspaces in $FITS"
}

# The ranges are required for every fit with the Run 2 ggH or ttH channels, see the tutorial.
run_one_fit() {
  local what=$1 c=$2 rg
  rg=$(python3 "$SCRIPTS/norm_ranges.py" $c.root 0.2)
  case $what in
    sig) combine -M Significance $c.root -n _sig_$c -m $MH -t -1 --expectSignal 1 --toysFrequentist --cminDefaultMinimizerTolerance 0.01 ${rg:+--setParameterRanges $rg} ;;
    lim) combine -M AsymptoticLimits $c.root -n _lim_$c -m $MH --run expected --cminDefaultMinimizerTolerance 0.01 ${rg:+--setParameterRanges $rg} ;;
  esac > ${what}_$c.log 2>&1 || echo "combine failed for $what $c, see ${what}_$c.log"
}

stage_fit() {
  cms_env
  cd "$FITS"
  export -f run_one_fit
  export SCRIPTS
  local c what
  for c in $CHANNELS; do for what in sig lim; do echo "$what $c"; done; done \
    | xargs -P "$JOBS" -L 1 bash -c 'run_one_fit "$0" "$1"'
  echo "[fit] logs in $FITS"
}

# A clean exit doesn't prove a fit worked (without the ranges, combine exits 0 and prints 299991), so compare the values.
stage_check() {
  cd "$FITS"
  python3 - <<'PY'
import re, sys
reference = {  # channel: significance, median expected limit, paper significance, paper limit
    "vbf": (1.77335, 1.2227, "1.77", "1.22"),
    "ggh": (1.55829, 1.2773, "1.56", "1.28"),
    "tth": (0.542755, 4.2031, "0.54", "4.20"),
    "vh": (0.42397, 5.1406, "0.42", "5.13"),
    "comb": (2.45936, 0.8242, "2.46", "0.82"),
    "gghvbf": (2.36162, 0.8633, "n/a", "n/a"),
}
def read(path, pattern):
    try:
        found = re.search(pattern, open(path).read())
    except OSError:
        return None
    return float(found.group(1)) if found else None
bad = 0
print("%-8s %10s %10s %6s | %10s %10s %6s" % ("channel", "signif.", "reference", "paper", "limit", "reference", "paper"))
for c, (sig_ref, lim_ref, sig_paper, lim_paper) in reference.items():
    sig = read("sig_%s.log" % c, r"Significance: (\S+)")
    lim = read("lim_%s.log" % c, r"Expected 50\.0%: r < (\S+)")
    ok = [v is not None and abs(v - ref) / ref < 1e-3 for v, ref in ((sig, sig_ref), (lim, lim_ref))]
    bad += ok.count(False)
    print("%-8s %10s %10s %6s | %10s %10s %6s %s" % (c, sig, sig_ref, sig_paper, lim, lim_ref, lim_paper, "ok" if all(ok) else "FAIL"))
print("ALL OK" if not bad else "FAILED: %d values differ from the reference by more than 0.1%%" % bad)
sys.exit(1 if bad else 0)
PY
}

for s in "${STAGES[@]}"; do "stage_$s"; done
