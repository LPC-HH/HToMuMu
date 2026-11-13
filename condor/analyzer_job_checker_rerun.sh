#!/bin/bash

###############################
# Define input parameters
###############################
ANALYZER_VERSION_NUMBER=$1

if [[ -z "$ANALYZER_VERSION_NUMBER" ]]; then
    echo "Usage: $0 ANALYZER_VERSION_NUMBER"
    echo "Example: $0 1.6"
    exit 1
fi

DIR="analyzer_HiggsMuMu_v$ANALYZER_VERSION_NUMBER"

OUTFILE="analyzer_error_datasets.txt"
> "$OUTFILE"

RESUBMIT_ALL_SCRIPT="submit_all_failed_jobs.sh"

cat > "$RESUBMIT_ALL_SCRIPT" <<EOF
#!/bin/bash
set -e

# Go to the directory where this script is located
cd "\$(dirname "\$0")"

EOF

chmod +x "$RESUBMIT_ALL_SCRIPT"

n_resubmit_files=0

fail_count=0
total_job_times=()
running_job_times=()
n_long_jobs=0

AUTO_RESUBMIT=0
# Set to 1 if you want the script to automatically run condor_submit
# AUTO_RESUBMIT=1

seconds_to_hms() {
    local total_seconds=$1
    local hours=$(( total_seconds / 3600 ))
    local minutes=$(( (total_seconds % 3600) / 60 ))
    local seconds=$(( total_seconds % 60 ))
    printf "%02d:%02d:%02d\n" "$hours" "$minutes" "$seconds"
}

get_job_I_from_filename() {
    local file="$1"
    basename "$file" | sed -E 's/^jobR([0-9]+)\..*/\1/'
}

get_expected_jobs_from_jdl() {
    local jdl="$1"

    awk '
        BEGIN { in_queue = 0 }

        /^[[:space:]]*Queue[[:space:]]+I[[:space:]]+from[[:space:]]*\(/ {
            in_queue = 1
            sub(/^.*\(/, "")
            sub(/\).*/, "")
            if ($0 != "") print $0
            next
        }

        in_queue == 1 {
            if ($0 ~ /\)/) {
                sub(/\).*/, "")
                if ($0 != "") print $0
                in_queue = 0
                next
            }

            if ($0 != "") print $0
        }
    ' "$jdl" | awk '{print $1}' | grep -E '^[0-9]+$'
}

create_resubmit_jdl() {
    local original_jdl="$1"
    local failed_jobs_file="$2"
    local resubmit_jdl="$3"

    awk '
        BEGIN { in_queue = 0 }

        /^[[:space:]]*Queue[[:space:]]+I[[:space:]]+from[[:space:]]*\(/ {
            in_queue = 1
            next
        }

        in_queue == 1 {
            if ($0 ~ /\)/) {
                in_queue = 0
            }
            next
        }

        {
            print
        }
    ' "$original_jdl" > "$resubmit_jdl"

    {
        echo ""
        echo "# Resubmit only failed jobs"
        echo "Queue I from ("
        cat "$failed_jobs_file"
        echo ")"
    } >> "$resubmit_jdl"
}

mark_failed_job() {
    local failed_jobs_file="$1"
    local job_i="$2"

    if [[ -n "$job_i" && "$job_i" =~ ^[0-9]+$ ]]; then
        echo "$job_i" >> "$failed_jobs_file"
    fi
}

###############################
# Fast batch scanners
###############################
# The original checker forked ~20 processes per job (grep/sed/tail/date per file) and
# read every .log/.err three times over NFS, which took >1 h on ~40k jobs.  The functions
# below read each file exactly once with one awk per dataset and convert all datetimes
# with one `date -f` per dataset.  The checks and messages are unchanged; any unusual case
# falls back to the original per-file code (check_err_slow / check_log_slow), so the
# output is identical to the old script, except that a .log whose datetime `date` cannot
# parse is now flagged ("unparseable timing information") instead of getting a bogus time.
# Known non-replicated corner case: a .log containing NUL bytes (grep would print
# "Binary file matches"); condor user logs are plain text.

HARMLESS_ERR_LINE="cp: cannot stat 'data/pileup/*.root': No such file or directory"
export HARMLESS_ERR_LINE

# On the LPC NFS disk a cold file open costs ~0.1-0.4 s, so reading ~80k small files one
# after another takes hours even with no forks.  Before scanning a block, read all of its
# .err/.log files in parallel to pull them into the page cache; the serial scan that follows
# then hits the cache.  This only reads the files (output to /dev/null), so it cannot
# change any result.  Lower CHECKER_PARALLEL_READS to be gentler on the file server.
CHECKER_PARALLEL_READS=${CHECKER_PARALLEL_READS:-32}

prefetch_files() {
    (( $# > 0 )) || return 0
    printf '%s\0' "$@" | xargs -0 -P "$CHECKER_PARALLEL_READS" -n 16 cat > /dev/null 2>&1 || true
}

# Same as get_job_I_from_filename (basename | sed), without forking. Result in $job_i.
job_i_from_path() {
    local base="${1##*/}"
    if [[ "$base" =~ ^jobR([0-9]+)\. ]]; then
        job_i="${BASH_REMATCH[1]}"
    else
        job_i="$base"
    fi
}

# stdin: one .err path per line. stdout per file: "<n lines matching corrupt-read regex>|<1 if last line is the harmless one>"
scan_err_files() {
    LC_ALL=C awk '
        {
            f = $0; n = 0; last = ""
            while ((getline line < f) > 0) {
                if (line ~ /R__unzip|ReadBasketBuffers|TBranch::GetBasket/) n++
                last = line
            }
            close(f)
            print n "|" (last == ENVIRON["HARMLESS_ERR_LINE"] ? 1 : 0)
        }'
}

# stdin: one .log path per line. stdout per file: "<submit dt>|<execute dt>|<finish dt>|<multi>"
# Same line selection as the original greps: first 000 line, first 001 line, last
# "005 ... Job terminated." line; dt = first YYYY-MM-DD HH:MM:SS in that line.
# multi=1 if a selected line holds more than one datetime (grep -o would have returned
# several lines) -> caller uses the original code for that file.
scan_log_files() {
    LC_ALL=C awk '
        BEGIN {
            DT    = "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]"
            SUBRE = "^000 \\([0-9]+\\.[0-9]+\\.[0-9]+\\)"
            EXERE = "^001 \\([0-9]+\\.[0-9]+\\.[0-9]+\\)"
            FINRE = "^005 \\([0-9]+\\.[0-9]+\\.[0-9]+\\) " DT " Job terminated\\.$"
        }
        function first_dt(s,   out) {
            NDT = 0; out = ""
            while (match(s, DT)) {
                if (NDT == 0) out = substr(s, RSTART, RLENGTH)
                NDT++
                s = substr(s, RSTART + RLENGTH)
            }
            return out
        }
        {
            f = $0; s = ""; e = ""; fin = ""; hs = 0; he = 0
            while ((getline line < f) > 0) {
                if (!hs && line ~ SUBRE) { s = line; hs = 1 }
                if (!he && line ~ EXERE) { e = line; he = 1 }
                if (line ~ FINRE) fin = line
            }
            close(f)
            multi = 0
            sd = first_dt(s);   if (NDT > 1) multi = 1
            ed = first_dt(e);   if (NDT > 1) multi = 1
            fd = first_dt(fin); if (NDT > 1) multi = 1
            print sd "|" ed "|" fd "|" multi
        }'
}

# Original per-file .err check (fallback). Uses the same globals as the main loop.
check_err_slow() {
    local file="$1"

    job_i=$(get_job_I_from_filename "$file")

    n_corrupt=$(grep -cE 'R__unzip|ReadBasketBuffers|TBranch::GetBasket' "$file")
    if (( n_corrupt > 0 )); then
        bad_inputs=$(grep -oE 'File: [^ ,]+\.root' "$file" | sed 's#.*/##' | sort -u | tr '\n' ' ')
        blockError=true
        ((fail_count++))
        echo "$file has $n_corrupt corrupted-read errors, bad input: ${bad_inputs:-unknown}" >> "$OUTFILE"
        mark_failed_job "$failed_jobs_file" "$job_i"
        return
    fi

    last_line=$(tail -n 1 "$file")

    if [[ "$last_line" != "$HARMLESS_ERR_LINE" ]]; then
        blockError=true
        ((fail_count++))
        echo "$file" >> "$OUTFILE"
        mark_failed_job "$failed_jobs_file" "$job_i"
    fi
}

# Timing bookkeeping shared by the fast and slow paths: needs $file, $job_i, $st, $tt, $ft.
record_job_times() {
    total_job_time=$(( ft - st ))
    running_job_time=$(( ft - tt ))

    if (( total_job_time <= 0 || running_job_time <= 0 )); then
        blockError=true
        ((fail_count++))
        echo "$file has invalid timing information" >> "$OUTFILE"
        mark_failed_job "$failed_jobs_file" "$job_i"
        return
    fi

    if (( running_job_time >= 36000 )); then
        ((n_long_jobs++))
        echo "long job in $file of $(seconds_to_hms "$running_job_time")"
    fi

    total_job_times+=( "$total_job_time" )
    running_job_times+=( "$running_job_time" )
}

record_missing_timing() {
    blockError=true
    ((fail_count++))
    echo "$file has missing timing information" >> "$OUTFILE"
    mark_failed_job "$failed_jobs_file" "$job_i"
}

# Original per-file .log check (fallback).
check_log_slow() {
    local file="$1"

    job_i=$(get_job_I_from_filename "$file")

    submission_line=$(grep -E '^000 \([0-9]+\.[0-9]+\.[0-9]+\)' "$file" | head -n 1)
    execute_line=$(grep -E '^001 \([0-9]+\.[0-9]+\.[0-9]+\)' "$file" | head -n 1)
    finish_line=$(grep -E '^005 \([0-9]+\.[0-9]+\.[0-9]+\) [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} Job terminated\.$' "$file" | tail -n 1)

    submission_datetime=$(grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$submission_line")
    transfer_datetime=$(grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$execute_line")
    finish_datetime=$(grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$finish_line")

    if [[ -z "$submission_datetime" || -z "$transfer_datetime" || -z "$finish_datetime" ]]; then
        record_missing_timing
        return
    fi

    # An unparseable datetime (e.g. month 13, or two datetimes on one line) used to leave
    # st/tt/ft empty, which bash arithmetic treats as 0 -> absurd job times.  Flag it instead.
    if ! st=$(date -d "$submission_datetime" +%s 2>/dev/null) ||
       ! tt=$(date -d "$transfer_datetime" +%s 2>/dev/null) ||
       ! ft=$(date -d "$finish_datetime" +%s 2>/dev/null); then
        blockError=true
        ((fail_count++))
        echo "$file has unparseable timing information" >> "$OUTFILE"
        mark_failed_job "$failed_jobs_file" "$job_i"
        return
    fi

    record_job_times
}

###############################
# Main loop over datasets
###############################

for block in "$DIR"/*; do
    [[ -d "$block" ]] || continue

    echo "Checking $block files"

    blockError=false
    task_jdl="$block/task.jdl"

    if [[ ! -f "$task_jdl" ]]; then
        blockError=true
        ((fail_count++))
        echo "$block has no task.jdl" >> "$OUTFILE"
        echo "************** Errors found in $block **************"
        continue
    fi

    failed_jobs_file="$block/failed_jobs.txt"
    > "$failed_jobs_file"

    mapfile -t expected_jobs < <(get_expected_jobs_from_jdl "$task_jdl")
    nFilesExpected=${#expected_jobs[@]}

    if (( nFilesExpected == 0 )); then
        blockError=true
        ((fail_count++))
        echo "$block has zero expected jobs parsed from task.jdl" >> "$OUTFILE"
        echo "Could not parse Queue I from (...) in $task_jdl" >> "$OUTFILE"
        echo "************** Errors found in $block **************"
        continue
    fi

    ###############################
    # Check missing output files
    ###############################

    # One directory listing per block (bash glob, no fork) instead of one compgen per job.
    # The regex is the exact equivalent of the old glob "jobR${job_i}.*.*.out".
    unset have_out
    declare -A have_out=()
    for f in "$block"/out/*.out; do
        if [[ "${f##*/}" =~ ^jobR([0-9]+)\..*\..*\.out$ ]]; then
            have_out["${BASH_REMATCH[1]}"]=1
        fi
    done

    for job_i in "${expected_jobs[@]}"; do
        if [[ -z "${have_out[$job_i]+x}" ]]; then
            blockError=true
            ((fail_count++))
            echo "$block is missing output for job I=$job_i" >> "$OUTFILE"
            mark_failed_job "$failed_jobs_file" "$job_i"
        fi
    done

    ###############################
    # Check .err files
    ###############################

    # Corrupted input reads (e.g. R__unzipLZMA): the job still exits 0 with garbage in the affected entries.
    # A resubmit fixes a corrupted transfer; if the source file itself is bad (adler32 matches DAS), drop it
    # from the job's input_list.tgz and from list/ before resubmitting.
    # The only accepted last line is $HARMLESS_ERR_LINE (missing pileup copy).

    err_files=()
    for file in "$block"/err/*.err; do
        [[ -e "$file" ]] && err_files+=( "$file" )
    done

    log_files=()
    for file in "$block"/log/*.log; do
        [[ -e "$file" ]] && log_files+=( "$file" )
    done

    prefetch_files "${err_files[@]}" "${log_files[@]}"

    err_results=()
    if (( ${#err_files[@]} > 0 )); then
        mapfile -t err_results < <(printf '%s\n' "${err_files[@]}" | scan_err_files)
    fi

    if (( ${#err_results[@]} != ${#err_files[@]} )); then
        # Scanner output does not line up: use the original per-file check.
        for file in "${err_files[@]}"; do
            check_err_slow "$file"
        done
    else
        for idx in "${!err_files[@]}"; do
            file="${err_files[idx]}"
            res="${err_results[idx]}"
            n_corrupt="${res%%|*}"
            last_ok="${res##*|}"

            job_i_from_path "$file"

            if (( n_corrupt > 0 )); then
                # Rare: run the original pipeline so the bad-input text is identical.
                bad_inputs=$(grep -oE 'File: [^ ,]+\.root' "$file" | sed 's#.*/##' | sort -u | tr '\n' ' ')
                blockError=true
                ((fail_count++))
                echo "$file has $n_corrupt corrupted-read errors, bad input: ${bad_inputs:-unknown}" >> "$OUTFILE"
                mark_failed_job "$failed_jobs_file" "$job_i"
                continue
            fi

            if [[ "$last_ok" != 1 ]]; then
                blockError=true
                ((fail_count++))
                echo "$file" >> "$OUTFILE"
                mark_failed_job "$failed_jobs_file" "$job_i"
            fi
        done
    fi

    ###############################
    # Check timing information
    ###############################

    log_results=()
    if (( ${#log_files[@]} > 0 )); then
        mapfile -t log_results < <(printf '%s\n' "${log_files[@]}" | scan_log_files)
    fi

    # Convert every datetime of the block with a single `date -f` (same parser as `date -d`).
    log_fast=true
    epochs=()
    if (( ${#log_results[@]} != ${#log_files[@]} )); then
        log_fast=false
    else
        dts=()
        for res in "${log_results[@]}"; do
            IFS='|' read -r sd ed fd multi <<< "$res"
            if [[ "$multi" == 0 && -n "$sd" && -n "$ed" && -n "$fd" ]]; then
                dts+=( "$sd" "$ed" "$fd" )
            fi
        done
        if (( ${#dts[@]} > 0 )); then
            if epoch_out=$(printf '%s\n' "${dts[@]}" | date -f - +%s 2>/dev/null); then
                mapfile -t epochs <<< "$epoch_out"
                (( ${#epochs[@]} == ${#dts[@]} )) || log_fast=false
            else
                log_fast=false
            fi
        fi
    fi

    if ! $log_fast; then
        # Unusual dates or scanner mismatch: use the original per-file check for the whole block.
        for file in "${log_files[@]}"; do
            check_log_slow "$file"
        done
    else
        k=0
        for idx in "${!log_files[@]}"; do
            file="${log_files[idx]}"
            IFS='|' read -r sd ed fd multi <<< "${log_results[idx]}"

            if [[ "$multi" != 0 ]]; then
                check_log_slow "$file"
                continue
            fi

            job_i_from_path "$file"

            if [[ -z "$sd" || -z "$ed" || -z "$fd" ]]; then
                record_missing_timing
                continue
            fi

            st="${epochs[k]}"; tt="${epochs[k+1]}"; ft="${epochs[k+2]}"
            (( k += 3 ))

            record_job_times
        done
    fi

    ###############################
    # Create resubmit JDL if needed
    ###############################

    sort -n -u "$failed_jobs_file" -o "$failed_jobs_file"

    if [[ -s "$failed_jobs_file" ]]; then
        resubmit_jdl="$block/task_resubmit_failed.jdl"
        create_resubmit_jdl "$task_jdl" "$failed_jobs_file" "$resubmit_jdl"

        resubmit_jdl_name=$(basename "$resubmit_jdl")

        {
            echo "echo \"Cleaning old failed job files in $block\""
            echo "( cd \"$block\" && while read -r job_i; do"
            echo "    rm -f err/jobR\${job_i}.*.err"
            echo "    rm -f log/jobR\${job_i}.*.log"
            echo "    rm -f out/jobR\${job_i}.*.out"
            echo "done < failed_jobs.txt )"
            echo ""
            echo "echo \"Submitting failed jobs in $block\""
            echo "( cd \"$block\" && condor_submit \"$resubmit_jdl_name\" )"
            echo ""
        } >> "$RESUBMIT_ALL_SCRIPT"

        ((n_resubmit_files++))

        echo "Failed jobs in $block:"
        cat "$failed_jobs_file"

        echo "Created resubmit file:"
        echo "$resubmit_jdl"

        echo "$block failed jobs:" >> "$OUTFILE"
        cat "$failed_jobs_file" >> "$OUTFILE"
        echo "Resubmit with: ( cd $block && condor_submit $resubmit_jdl_name )" >> "$OUTFILE"

        if (( AUTO_RESUBMIT == 1 )); then
            echo "Auto-resubmitting failed jobs in $block"
            (
                cd "$block" || exit 1
                condor_submit "$resubmit_jdl_name"
            )
        else
            echo "To resubmit failed jobs for this sample, run:"
            echo "( cd $block && condor_submit $resubmit_jdl_name )"
        fi
    else
        rm -f "$failed_jobs_file"
    fi

    if $blockError; then
        echo "************** Errors found in $block **************"
    fi

done

###############################
# Global resubmit script summary
###############################

if (( n_resubmit_files > 0 )); then
    echo ""
    echo "Created global resubmit script:"
    echo "$RESUBMIT_ALL_SCRIPT"
    echo ""
    echo "To resubmit ALL failed jobs, run:"
    echo "bash $RESUBMIT_ALL_SCRIPT"

    echo "" >> "$OUTFILE"
    echo "Global resubmit script: $RESUBMIT_ALL_SCRIPT" >> "$OUTFILE"
    echo "Run: bash $RESUBMIT_ALL_SCRIPT" >> "$OUTFILE"
else
    echo ""
    echo "No failed-job resubmit script was needed."
fi

###############################
# Final summary
###############################

echo "------------------------------ $DIR ------------------------------"

if [[ -f expected_ana_job_number.json ]]; then
    EXPECTED_ANALYZER_JOBS=$(jq -r '.EXPECTED_ANALYZER_JOBS' expected_ana_job_number.json)
else
    EXPECTED_ANALYZER_JOBS=${#total_job_times[@]}
fi

echo "Total job num: ${#total_job_times[@]} / $EXPECTED_ANALYZER_JOBS"

if (( ${#total_job_times[@]} < EXPECTED_ANALYZER_JOBS )); then
    echo "THE TOTAL NUMBER OF EXPECTED JOBS HAVE NOT BEEN RUN: ${#total_job_times[@]} / $EXPECTED_ANALYZER_JOBS"
    echo "THE TOTAL NUMBER OF EXPECTED JOBS HAVE NOT BEEN RUN: ${#total_job_times[@]} / $EXPECTED_ANALYZER_JOBS" >> "$OUTFILE"
fi

if (( ${#total_job_times[@]} > 0 )); then
    max_job_time=${total_job_times[0]}
    for x in "${total_job_times[@]}"; do
        (( x > max_job_time )) && max_job_time=$x
    done

    max_run_time=${running_job_times[0]}
    for x in "${running_job_times[@]}"; do
        (( x > max_run_time )) && max_run_time=$x
    done

    min_run_time=${running_job_times[0]}
    for x in "${running_job_times[@]}"; do
        (( x < min_run_time )) && min_run_time=$x
    done

    sum=0
    for x in "${running_job_times[@]}"; do
        (( sum += x ))
    done
    avg_run_time=$(( sum / ${#running_job_times[@]} ))

    sumTot=0
    for x in "${total_job_times[@]}"; do
        (( sumTot += x ))
    done
    avg_run_timeTot=$(( sumTot / ${#total_job_times[@]} ))

    echo "total running job time: $sum"
    echo "num jobs ${#running_job_times[@]}"
    echo "total job time: $sumTot"
    echo "num jobs ${#total_job_times[@]}"

    echo "The total job time is $(seconds_to_hms "$max_job_time")"
    echo "The max run time is $(seconds_to_hms "$max_run_time")"
    echo "The min run time is $(seconds_to_hms "$min_run_time")"
    echo "The avg run time is $(seconds_to_hms "$avg_run_time")"
    echo "The avg total time is $(seconds_to_hms "$avg_run_timeTot")"

    echo "------------------------------ $DIR ------------------------------" >> "$OUTFILE"
    echo "Total num of long jobs: $n_long_jobs" >> "$OUTFILE"
    echo "Total job num: ${#total_job_times[@]}" >> "$OUTFILE"
    echo "The total job time is $(seconds_to_hms "$max_job_time")" >> "$OUTFILE"
    echo "The max run time is $(seconds_to_hms "$max_run_time")" >> "$OUTFILE"
    echo "The min run time is $(seconds_to_hms "$min_run_time")" >> "$OUTFILE"
    echo "The avg run time is $(seconds_to_hms "$avg_run_time")" >> "$OUTFILE"
    echo "The avg total time is $(seconds_to_hms "$avg_run_timeTot")" >> "$OUTFILE"
else
    echo "No completed jobs with valid timing were found."
    echo "No completed jobs with valid timing were found." >> "$OUTFILE"
fi

echo "Total num of long jobs: $n_long_jobs"

if [[ "$fail_count" -eq 0 ]]; then
    echo "No extra errors were thrown in any jobs"
    echo "Check $OUTFILE for timing info"
else
    echo "There are errors. Check $OUTFILE."
    echo "To resubmit all failed jobs, run:"
    echo "bash $RESUBMIT_ALL_SCRIPT"
fi
