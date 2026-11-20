#!/bin/bash

###############################
# Define input parameters
###############################
CTUPLE_VERSION_NUMBER=$1

if [[ -z "$CTUPLE_VERSION_NUMBER" ]]; then
    echo "Usage: $0 CTUPLE_VERSION_NUMBER"
    echo "Example: $0 1.6"
    exit 1
fi

DIR="ctuples_v$CTUPLE_VERSION_NUMBER"

# Output file for failures
OUTFILE="ctuple_error_datasets.txt"
> "$OUTFILE"

RESUBMIT_ALL_SCRIPT="submit_all_failed_ctuple_jobs.sh"

cat > "$RESUBMIT_ALL_SCRIPT" <<EOF
#!/bin/bash
set -e

# Go to the directory where this script is located
cd "\$(dirname "\$0")"

EOF

chmod +x "$RESUBMIT_ALL_SCRIPT"

fail_count=0
n_resubmit_files=0

to_seconds() {
  IFS=: read -r h m s <<< "$1"
  echo $((10#$h*3600 + 10#$m*60 + 10#$s))
}

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
# The original checker forked several processes per job (head/tail/grep/sed/to_seconds)
# and read every .log several times over NFS.  Below, each block's files are read once by
# one awk per block, with no per-job forks.  Checks and output are unchanged.

HARMLESS_ERR_LINE="WARNING: In non-interactive mode release checks e.g. deprecated releases, production architectures are disabled."
export HARMLESS_ERR_LINE

# On the LPC NFS disk a cold file open costs ~0.1-0.4 s, so reading many small files one
# after another is slow.  Before scanning a block, read all of its .err/.log files in
# parallel to pull them into the page cache; the serial scan then hits the cache.  This only
# reads the files (output to /dev/null), so it cannot change any result.  Lower
# CHECKER_PARALLEL_READS to be gentler on the file server.
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

# stdin: one .err path per line. stdout per file: 1 if its last line (tail -n 1) is the harmless one, else 0.
scan_err_files() {
    LC_ALL=C awk '
        {
            f = $0; last = ""
            while ((getline line < f) > 0) last = line
            close(f)
            print (last == ENVIRON["HARMLESS_ERR_LINE"] ? 1 : 0)
        }'
}

# stdin: one .log path per line. stdout per file: "<st>|<tt>|<ft>" in seconds since midnight,
# empty field when no HH:MM:SS was found.  Same lines as the original:
#   st: line 1                  (head -n 1)
#   tt: line 3, or last if < 3  (head -n 3 | tail -n 1)
#   ft: 20th line from the end, or line 1 if < 20 lines   (tail -n 20 | head -n 1)
# and the first HH:MM:SS in the line, as to_seconds used the first grep -o match.
scan_log_files() {
    LC_ALL=C awk '
        function secs(s,   t) {
            if (!match(s, /[0-9][0-9]:[0-9][0-9]:[0-9][0-9]/)) return ""
            t = substr(s, RSTART, RLENGTH)
            return (substr(t, 1, 2) + 0) * 3600 + (substr(t, 4, 2) + 0) * 60 + (substr(t, 7, 2) + 0)
        }
        {
            f = $0; n = 0; l1 = ""; l3 = ""; lN = ""
            delete ring
            while ((getline line < f) > 0) {
                n++
                if (n == 1) l1 = line
                if (n <= 3) l3 = line
                ring[n % 20] = line
            }
            close(f)
            if (n >= 20) lN = ring[(n - 19) % 20]
            else         lN = l1
            print secs(l1) "|" secs(l3) "|" secs(lN)
        }'
}

# Original per-file .err check (fallback if the scanner output does not line up).
check_err_slow() {
    local file="$1"

    job_i=$(get_job_I_from_filename "$file")
    last_line=$(tail -n 1 "$file")

    if [[ "$last_line" != "$HARMLESS_ERR_LINE" ]]; then
        blockError=true
        ((fail_count++))
        echo "$file" >> "$OUTFILE"
        mark_failed_job "$failed_jobs_file" "$job_i"
    fi
}

# Timing bookkeeping shared by the fast and slow paths: needs $file, $st, $tt, $ft (empty = missing).
record_ctuple_times() {
    if [[ -z "$st" || -z "$tt" || -z "$ft" ]]; then
        blockError=true
        ((fail_count++))
        job_i_from_path "$file"
        echo "$file has missing timing information" >> "$OUTFILE"
        mark_failed_job "$failed_jobs_file" "$job_i"
        return
    fi

    total_job_time=$(( ft - st ))
    running_job_time=$(( ft - tt))

    if (( total_job_time <= 0)); then
        total_job_time=$(( 86400 - st + ft))
    fi

    if (( running_job_time <= 0)); then
        running_job_time=$(( 86400 - tt + ft))
    fi

    total_job_times+=( "$total_job_time" )
    running_job_times+=( "$running_job_time" )
}

# Original per-file .log check (fallback if the scanner output does not line up).
check_log_slow() {
    local file="$1"

    first_line=$(head -n 1 "$file")
    second_line=$(head -n 3 "$file" | tail -n 1)
    last_line=$(tail -n 20 "$file" | head -n 1)

    submission_time=$(grep -oE '[0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$first_line")
    transfer_time=$(grep -oE '[0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$second_line")
    finish_time=$(grep -oE '[0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$last_line")

    st=""; tt=""; ft=""
    if [[ -n "$submission_time" && -n "$transfer_time" && -n "$finish_time" ]]; then
        st=$(to_seconds "$submission_time")
        tt=$(to_seconds "$transfer_time")
        ft=$(to_seconds "$finish_time")
    fi

    record_ctuple_times
}

total_job_times=()
running_job_times=()

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
        for file in "${err_files[@]}"; do
            check_err_slow "$file"
        done
    else
        for idx in "${!err_files[@]}"; do
            file="${err_files[idx]}"
            if [[ "${err_results[idx]}" != 1 ]]; then
                job_i_from_path "$file"
                blockError=true
                ((fail_count++))
                echo "$file" >> "$OUTFILE"
                mark_failed_job "$failed_jobs_file" "$job_i"
            fi
        done
    fi

    ###############################
    # Find ctuple timing information
    ###############################

    log_results=()
    if (( ${#log_files[@]} > 0 )); then
        mapfile -t log_results < <(printf '%s\n' "${log_files[@]}" | scan_log_files)
    fi

    if (( ${#log_results[@]} != ${#log_files[@]} )); then
        for file in "${log_files[@]}"; do
            check_log_slow "$file"
        done
    else
        for idx in "${!log_files[@]}"; do
            file="${log_files[idx]}"
            IFS='|' read -r st tt ft <<< "${log_results[idx]}"
            record_ctuple_times
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
    else
        rm -f "$failed_jobs_file"
    fi

    if $blockError; then
        echo "************** Errors found in $block **************"
    fi
done

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

echo "------------------------------ $DIR ------------------------------"

if [[ -f expected_ctup_job_number.json ]]; then
    EXPECTED_CTUPLE_JOBS=$(jq -r '.EXPECTED_CTUPLE_JOBS' expected_ctup_job_number.json)
else
    EXPECTED_CTUPLE_JOBS=${#total_job_times[@]}
fi

echo "Total job num: ${#total_job_times[@]} / $EXPECTED_CTUPLE_JOBS"

if (( ${#total_job_times[@]} < EXPECTED_CTUPLE_JOBS )); then
    echo "THE TOTAL NUMBER OF EXPECTED JOBS HAVE NOT BEEN RUN: ${#total_job_times[@]} / $EXPECTED_CTUPLE_JOBS"
    echo "THE TOTAL NUMBER OF EXPECTED JOBS HAVE NOT BEEN RUN: ${#total_job_times[@]} / $EXPECTED_CTUPLE_JOBS" >> "$OUTFILE"
fi

if (( ${#total_job_times[@]} > 0 )); then
    max_job_time=${total_job_times[0]}
    for x in "${total_job_times[@]}"; do
        ((x>max_job_time)) && max_job_time=$x
    done

    max_run_time=${running_job_times[0]}
    for x in "${running_job_times[@]}"; do
        ((x>max_run_time)) && max_run_time=$x
    done

    min_run_time=${running_job_times[0]}
    for x in "${running_job_times[@]}"; do
        ((x<min_run_time)) && min_run_time=$x
    done

    sum=0
    for x in "${running_job_times[@]}"; do
        ((sum+=x))
    done
    avg_run_time=$((sum/${#running_job_times[@]}))

    echo "The total job time is $(seconds_to_hms "$max_job_time")"
    echo "The max run time is $(seconds_to_hms "$max_run_time")"
    echo "The min run time is $(seconds_to_hms "$min_run_time")"
    echo "The avg run time is $(seconds_to_hms "$avg_run_time")"

    echo "Total job num: ${#total_job_times[@]}" >> "$OUTFILE"
    echo "------------------------------ $DIR ------------------------------" >> "$OUTFILE"
    echo "The total job time is $(seconds_to_hms "$max_job_time")" >> "$OUTFILE"
    echo "The max run time is $(seconds_to_hms "$max_run_time")" >> "$OUTFILE"
    echo "The min run time is $(seconds_to_hms "$min_run_time")" >> "$OUTFILE"
    echo "The avg run time is $(seconds_to_hms "$avg_run_time")" >> "$OUTFILE"
else
    echo "No completed jobs with valid timing were found."
    echo "No completed jobs with valid timing were found." >> "$OUTFILE"
fi

if [[ "$fail_count" -eq 0 ]]; then
    echo "No extra errors were thrown in any jobs"
    echo "Check $OUTFILE for timing info"
else
    echo "There are errors. Check $OUTFILE."
    if (( n_resubmit_files > 0 )); then
        echo "To resubmit all failed jobs, run:"
        echo "bash $RESUBMIT_ALL_SCRIPT"
    fi
fi
