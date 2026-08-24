#!/bin/bash

###############################
# Define input parameters
###############################
ANALYZER_VERSION_NUMBER=$1

if [[ -z "$ANALYZER_VERSION_NUMBER" ]]; then
    echo "Usage: $0 ANALYZER_VERSION_NUMBER"
    echo "Example: $0 1.7"
    exit 1
fi

DIR="analyzer_HiggsMuMu_v$ANALYZER_VERSION_NUMBER"

if [[ ! -d "$DIR" ]]; then
    echo "ERROR: directory does not exist: $DIR"
    exit 1
fi

###############################
# Output file for failures
###############################
OUTFILE="analyzer_error_datasets.txt"
> "$OUTFILE"

fail_count=0
n_long_jobs=0

total_job_times=()
running_job_times=()

###############################
# Helper functions
###############################
seconds_to_hms() {
    local total_seconds=$1
    local hours=$(( total_seconds / 3600 ))
    local minutes=$(( (total_seconds % 3600) / 60 ))
    local seconds=$(( total_seconds % 60 ))
    printf "%02d:%02d:%02d\n" "$hours" "$minutes" "$seconds"
}

get_expected_jobs_from_jdl() {
    local jdl_file="$1"

    if [[ ! -f "$jdl_file" ]]; then
        echo 0
        return
    fi

    local queue_line
    queue_line=$(grep -i '^Queue' "$jdl_file" | tail -n 1)

    # Examples:
    # Queue
    # Queue 10
    # Queue JOBID from something.txt
    if [[ "$queue_line" =~ ^[Qq]ueue[[:space:]]+([0-9]+)$ ]]; then
        echo "${BASH_REMATCH[1]}"
    elif [[ "$queue_line" =~ ^[Qq]ueue$ ]]; then
        echo 1
    else
        # Fallback to your old method
        local old_guess
        old_guess=$(tail -n 2 "$jdl_file" | head -n 1)

        if [[ "$old_guess" =~ ^[0-9]+$ ]]; then
            echo "$old_guess"
        elif [[ "$old_guess" == *"Queue"* ]]; then
            echo 1
        else
            echo 0
        fi
    fi
}

###############################
# Loop over datasets/blocks
###############################
for block in "$DIR"/*; do
    [[ -d "$block" ]] || continue

    echo "Checking $block files"
    blockError=false

    ###############################
    # Check number of output files
    ###############################
    nFilesExpected=$(get_expected_jobs_from_jdl "$block/task.jdl")

    if [[ -d "$block/out" ]]; then
        nFilesOut=$(find "$block/out" -maxdepth 1 -type f | wc -l)
    else
        nFilesOut=0
    fi

    if [[ "$nFilesExpected" -eq 0 ]]; then
        blockError=true
        ((fail_count++))
        echo "$block has no valid expected job count from task.jdl" >> "$OUTFILE"
    elif [[ "$nFilesExpected" -ne "$nFilesOut" ]]; then
        blockError=true
        ((fail_count++))
        missingFiles=$((nFilesExpected - nFilesOut))
        echo "$block has $missingFiles missing files: $nFilesOut / $nFilesExpected" >> "$OUTFILE"
    fi

    ###############################
    # Check stderr files
    ###############################
    for file in "$block"/err/*.err; do
        [[ -e "$file" ]] || continue

        last_line=$(tail -n 1 "$file")

        # This warning is ignored
        if [[ "$last_line" != "cp: cannot stat 'data/pileup/*.root': No such file or directory" ]]; then
            blockError=true
            ((fail_count++))
            echo "$file" >> "$OUTFILE"
        fi
    done

    ###############################
    # Check Condor timing information
    ###############################
    for file in "$block"/log/*.log; do
        [[ -e "$file" ]] || continue

        submit_line=$(grep -E '^000 \([0-9]+\.[0-9]+\.[0-9]+\) [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} Job submitted' "$file" | head -n 1)

        execute_line=$(grep -E '^001 \([0-9]+\.[0-9]+\.[0-9]+\) [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} Job executing' "$file" | head -n 1)

        finish_line=$(grep -E '^005 \([0-9]+\.[0-9]+\.[0-9]+\) [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} Job terminated\.$' "$file" | tail -n 1)

        if [[ -z "$submit_line" || -z "$execute_line" || -z "$finish_line" ]]; then
            blockError=true
            ((fail_count++))

            echo "Incomplete Condor timing info in $file" >> "$OUTFILE"

            if [[ -z "$submit_line" ]]; then
                echo "  missing submit line 000" >> "$OUTFILE"
            fi

            if [[ -z "$execute_line" ]]; then
                echo "  missing execute line 001" >> "$OUTFILE"
            fi

            if [[ -z "$finish_line" ]]; then
                echo "  missing terminate line 005" >> "$OUTFILE"
            fi

            continue
        fi

        submission_datetime=$(grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$submit_line")
        execute_datetime=$(grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$execute_line")
        finish_datetime=$(grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$finish_line")

        if [[ -z "$submission_datetime" || -z "$execute_datetime" || -z "$finish_datetime" ]]; then
            blockError=true
            ((fail_count++))

            echo "Could not parse datetime in $file" >> "$OUTFILE"
            echo "  submit line:  $submit_line" >> "$OUTFILE"
            echo "  execute line: $execute_line" >> "$OUTFILE"
            echo "  finish line:  $finish_line" >> "$OUTFILE"

            continue
        fi

        st=$(date -d "$submission_datetime" +%s)
        et=$(date -d "$execute_datetime" +%s)
        ft=$(date -d "$finish_datetime" +%s)

        total_job_time=$(( ft - st ))
        running_job_time=$(( ft - et ))

        if (( total_job_time < 0 || running_job_time < 0 )); then
            blockError=true
            ((fail_count++))

            echo "Bad timing calculation in $file" >> "$OUTFILE"
            echo "  submit:  $submission_datetime" >> "$OUTFILE"
            echo "  execute: $execute_datetime" >> "$OUTFILE"
            echo "  finish:  $finish_datetime" >> "$OUTFILE"

            continue
        fi

        if (( running_job_time >= 36000 )); then
            ((n_long_jobs++))
            echo "long job in $file of $(seconds_to_hms "$running_job_time")"
            echo "long job in $file of $(seconds_to_hms "$running_job_time")" >> "$OUTFILE"
        fi

        total_job_times+=( "$total_job_time" )
        running_job_times+=( "$running_job_time" )
    done

    if $blockError; then
        echo "************** Errors found in $block **************"
    fi
done

###############################
# Summary
###############################
echo "------------------------------ $DIR ------------------------------"

EXPECTED_ANALYZER_JOBS=$(jq -r '.EXPECTED_ANALYZER_JOBS' expected_ana_job_number.json)

echo "Total job num: ${#total_job_times[@]} / $EXPECTED_ANALYZER_JOBS"

if (( ${#total_job_times[@]} < EXPECTED_ANALYZER_JOBS )); then
    echo "THE TOTAL NUMBER OF EXPECTED JOBS HAVE NOT BEEN RUN: ${#total_job_times[@]} / $EXPECTED_ANALYZER_JOBS"
    echo "THE TOTAL NUMBER OF EXPECTED JOBS HAVE NOT BEEN RUN: ${#total_job_times[@]} / $EXPECTED_ANALYZER_JOBS" >> "$OUTFILE"
fi

if (( ${#running_job_times[@]} == 0 )); then
    echo "No valid completed jobs with full timing information were found."
    echo "No valid completed jobs with full timing information were found." >> "$OUTFILE"
    exit 1
fi

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
    ((sum += x))
done

avg_run_time=$(( sum / ${#running_job_times[@]} ))

echo "total running job time: $sum"
echo "num jobs ${#running_job_times[@]}"

sumTot=0
for x in "${total_job_times[@]}"; do
    ((sumTot += x))
done

avg_run_timeTot=$(( sumTot / ${#total_job_times[@]} ))

echo "total job time: $sumTot"
echo "num jobs ${#total_job_times[@]}"

echo "The total job time is $(seconds_to_hms "$max_job_time")"
echo "The max run time is $(seconds_to_hms "$max_run_time")"
echo "The min run time is $(seconds_to_hms "$min_run_time")"
echo "The avg run time is $(seconds_to_hms "$avg_run_time")"
echo "The avg total time is $(seconds_to_hms "$avg_run_timeTot")"
echo "Total num of long jobs: $n_long_jobs"

###############################
# Write summary to output file
###############################
echo "------------------------------ $DIR ------------------------------" >> "$OUTFILE"
echo "Total num of long jobs: $n_long_jobs" >> "$OUTFILE"
echo "Total job num: ${#total_job_times[@]} / $EXPECTED_ANALYZER_JOBS" >> "$OUTFILE"

echo "The total job time is $(seconds_to_hms "$max_job_time")" >> "$OUTFILE"
echo "The max run time is $(seconds_to_hms "$max_run_time")" >> "$OUTFILE"
echo "The min run time is $(seconds_to_hms "$min_run_time")" >> "$OUTFILE"
echo "The avg run time is $(seconds_to_hms "$avg_run_time")" >> "$OUTFILE"
echo "The avg total time is $(seconds_to_hms "$avg_run_timeTot")" >> "$OUTFILE"

###############################
# Final message
###############################
if [[ "$fail_count" -eq 0 ]]; then
    echo "No extra errors were thrown in any jobs"
    echo "Check $OUTFILE for timing info"
else
    echo "There are errors. Check $OUTFILE for a list of problematic eras/files"
fi
