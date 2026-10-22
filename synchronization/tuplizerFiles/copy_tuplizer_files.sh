#!/bin/bash
# Usage: bash copy_analyzer_files.sh <analyzer_version>   (e.g. 2.4)

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <tuplizer_version>   (e.g. 2.4.2)"
    exit 1
fi

tuplizer_version=$1
analyzer_version=${1%.*}
host="root://cmseos.fnal.gov"
src_base="/store/user/lpchmumu/esledge/analyzer_HiggsMuMu_v${analyzer_version}/tuples_v${tuplizer_version}/"
dst_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo $dst_dir

# copy_dir <EOS source dir> <local destination dir> [file name prefix]
copy_dir() {
    mkdir -p "$2"
    xrdfs "$host" ls "$1" | grep -E "*.root" | while read -r src_file; do
        echo "Copying $src_file"
        xrdcp -f "$host/$src_file" "$2/$3$(basename "$src_file")"
    done
}

for dataset in Muon0_2024H Muon1_2024H; do
    copy_dir "$src_base/$dataset" "$dst_dir/data/$dataset"
    cd $dst_dir/data/$dataset
    hadd ${dataset}_CombinedTuples.root *.root
    rm *_tuples.root
done

for mode in ggH VBF; do
    copy_dir "$src_base/${mode}_Summer24" "$dst_dir/signal/$mode"
    # ext1 tuples share file names with the nominal ones, so prefix them before merging
    if [[ $mode == VBF ]]; then
        copy_dir "$src_base/${mode}_Summer24_ext1" "$dst_dir/signal/$mode" "ext1_"
    fi
    cd $dst_dir/signal/$mode
    hadd ${mode}_CombinedTuples.root *.root
    rm *_tuples.root
done
#cd ${src_base}/synchronization/
