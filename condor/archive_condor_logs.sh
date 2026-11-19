#!/bin/bash
# Archive old condor job/log folders to EOS to free local disk space and inodes.
# Usage (from anywhere; the script works in its own directory):
# nohup bash archive_condor_logs.sh > archive.log 2>&1 &   # archive everything not in KEEP
#
# Restore a folder:
#   xrdcp root://cmseos.fnal.gov//store/user/$USER/condor_logs/<dir>.tar.gz - | tar -xzf -
#
# Destination: /store/user/<your username>/condor_logs (set EOS_USER or EOS_DEST to change it).

set -uo pipefail

EOS_HOST="root://cmseos.fnal.gov"
EOS_USER="${EOS_USER:-${USER:-$(id -un)}}"
EOS_DEST="${EOS_DEST:-/store/user/${EOS_USER}/condor_logs}"
# Folders that stay local (current campaigns; job checkers read them).
KEEP=(ctuples_v2.6.0 ctuples_v2.7.0 ctuples_v2.8.0 analyzer_HiggsMuMu_v2.8)

DRY_RUN=0
SIZES=0
KEEP_LOCAL=0
DIRS=()
for arg in "$@"; do
    case "$arg" in
        --dry-run)    DRY_RUN=1 ;;
        --sizes)      SIZES=1 ;;   # with --dry-run: also du/find each folder (slow on NFS)
        --keep-local) KEEP_LOCAL=1 ;;
        -h|--help)    sed -n '2,9p' "$0"; exit 0 ;;
        -*)           echo "Unknown option $arg" >&2; exit 1 ;;
        *)            DIRS+=("${arg%/}") ;;
    esac
done

cd "$(dirname "$(readlink -f "$0")")" || exit 1

is_kept() {
    local k
    for k in "${KEEP[@]}"; do [[ "$1" == "$k" ]] && return 0; done
    return 1
}

if [[ ${#DIRS[@]} -eq 0 ]]; then
    for d in analyzer_HiggsMuMu_v* ctuples_v* hadd_v*; do
        [[ -d "$d" ]] || continue
        is_kept "$d" && continue
        DIRS+=("$d")
    done
fi

if [[ ${#DIRS[@]} -eq 0 ]]; then
    echo "Nothing to archive."
    exit 0
fi

# Number of entries in the EOS tarball (empty output on read/gzip failure).
remote_count() {
    local listing
    # pipefail: the assignment fails if xrdcp or tar fails (bad read / corrupt gzip)
    listing=$(xrdcp -s "${EOS_HOST}/${EOS_DEST}/$1.tar.gz" - 2>/dev/null | tar -tzf - 2>/dev/null) || return 0
    printf '%s\n' "$listing" | wc -l
}

remote_exists() {
    xrdfs "$EOS_HOST" stat "${EOS_DEST}/$1.tar.gz" &>/dev/null
}

if [[ $DRY_RUN -eq 1 ]]; then
    echo "[dry-run] destination ${EOS_HOST}/${EOS_DEST}"
    echo "[dry-run] kept local: ${KEEP[*]}"
    for d in "${DIRS[@]}"; do
        if [[ ! -d "$d" ]]; then echo "  MISSING  $d"; continue; fi
        if [[ $SIZES -eq 1 ]]; then
            printf "  %-40s %8s %9d files\n" "$d" "$(du -sh "$d" | cut -f1)" "$(find "$d" | wc -l)"
        else
            echo "  $d"
        fi
    done
    exit 0
fi

echo "Quota before:"; quota -s 2>/dev/null | tail -3
xrdfs "$EOS_HOST" mkdir -p "$EOS_DEST" || { echo "Cannot create ${EOS_DEST} on EOS (kinit?)"; exit 1; }

ARCHIVED=(); FAILED=()
for d in "${DIRS[@]}"; do
    if [[ ! -d "$d" ]]; then echo "[skip] $d: not a directory"; continue; fi
    if is_kept "$d"; then echo "[skip] $d is in KEEP"; continue; fi
    echo "=== $d  ($(date '+%F %T'))"
    nlocal=$(find "$d" | wc -l)

    nremote=""
    if remote_exists "$d"; then
        nremote=$(remote_count "$d")
        if [[ "$nremote" == "$nlocal" ]]; then
            echo "    already on EOS and verified ($nremote entries)"
        else
            echo "    existing EOS tarball does not match (${nremote:-unreadable} vs $nlocal); re-uploading"
            nremote=""
        fi
    fi

    if [[ -z "$nremote" ]]; then
        tar -czf - "$d" | xrdcp -f -s - "${EOS_HOST}/${EOS_DEST}/$d.tar.gz"
        st=("${PIPESTATUS[@]}")
        if [[ ${st[0]} -ne 0 || ${st[1]} -ne 0 ]]; then
            echo "    FAILED upload (tar=${st[0]}, xrdcp=${st[1]}); local folder kept"
            FAILED+=("$d"); continue
        fi
        nremote=$(remote_count "$d")
    fi

    if [[ "$nremote" != "$nlocal" ]]; then
        echo "    FAILED verification (EOS ${nremote:-unreadable} vs local $nlocal entries); local folder kept"
        FAILED+=("$d"); continue
    fi
    echo "    verified $nlocal entries -> ${EOS_DEST}/$d.tar.gz"

    if [[ $KEEP_LOCAL -eq 0 ]]; then
        rm -rf -- "$d" && echo "    removed local $d"
    fi
    ARCHIVED+=("$d")
done

echo
echo "Archived (${#ARCHIVED[@]}): ${ARCHIVED[*]:-}"
echo "Failed   (${#FAILED[@]}): ${FAILED[*]:-}"
echo "Quota after:"; quota -s 2>/dev/null | tail -3
[[ ${#FAILED[@]} -eq 0 ]]
