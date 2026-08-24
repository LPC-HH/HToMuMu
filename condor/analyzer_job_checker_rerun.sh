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

    for job_i in "${expected_jobs[@]}"; do
        if ! compgen -G "$block/out/jobR${job_i}.*.*.out" > /dev/null; then
            blockError=true
            ((fail_count++))
            echo "$block is missing output for job I=$job_i" >> "$OUTFILE"
            mark_failed_job "$failed_jobs_file" "$job_i"
        fi
    done

    ###############################
    # Check .err files
    ###############################

    for file in "$block"/err/*.err; do
        [[ -e "$file" ]] || continue

        job_i=$(get_job_I_from_filename "$file")
        last_line=$(tail -n 1 "$file")

        # This is the one known harmless message
        if [[ "$last_line" != "cp: cannot stat 'data/pileup/*.root': No such file or directory" ]]; then
            blockError=true
            ((fail_count++))
            echo "$file" >> "$OUTFILE"
            mark_failed_job "$failed_jobs_file" "$job_i"
        fi
    done

    ###############################
    # Check timing information
    ###############################

    for file in "$block"/log/*.log; do
        [[ -e "$file" ]] || continue

        job_i=$(get_job_I_from_filename "$file")

        submission_line=$(grep -E '^000 \([0-9]+\.[0-9]+\.[0-9]+\)' "$file" | head -n 1)
        execute_line=$(grep -E '^001 \([0-9]+\.[0-9]+\.[0-9]+\)' "$file" | head -n 1)
        finish_line=$(grep -E '^005 \([0-9]+\.[0-9]+\.[0-9]+\) [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} Job terminated\.$' "$file" | tail -n 1)

        submission_datetime=$(grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$submission_line")
        transfer_datetime=$(grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$execute_line")
        finish_datetime=$(grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$finish_line")

        if [[ -z "$submission_datetime" || -z "$transfer_datetime" || -z "$finish_datetime" ]]; then
            blockError=true
            ((fail_count++))
            echo "$file has missing timing information" >> "$OUTFILE"
            mark_failed_job "$failed_jobs_file" "$job_i"
            continue
        fi

        st=$(date -d "$submission_datetime" +%s)
        tt=$(date -d "$transfer_datetime" +%s)
        ft=$(date -d "$finish_datetime" +%s)

        total_job_time=$(( ft - st ))
        running_job_time=$(( ft - tt ))

        if (( total_job_time <= 0 || running_job_time <= 0 )); then
            blockError=true
            ((fail_count++))
            echo "$file has invalid timing information" >> "$OUTFILE"
            mark_failed_job "$failed_jobs_file" "$job_i"
            continue
        fi

        if (( running_job_time >= 36000 )); then
            ((n_long_jobs++))
            echo "long job in $file of $(seconds_to_hms "$running_job_time")"
        fi

        total_job_times+=( "$total_job_time" )
        running_job_times+=( "$running_job_time" )
    done

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
