#!/bin/bash

###############################
# Define input parameters
###############################
ANALYZER_VERSION_NUMBER=$1



DIR="analyzer_HiggsMuMu_v$ANALYZER_VERSION_NUMBER"

#for file in "$DIR"/*/err/*.err; do

# Output file for failures
OUTFILE="analyzer_error_datasets.txt"
> "$OUTFILE"  # clear it at start

fail_count=0

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

total_job_times=()
running_job_times=()

n_long_jobs=0

for block in "$DIR"/*; do
    echo "Checking $block files"
    blockError=false
    nFilesExpected=$(tail -n 2 $block/task.jdl | head -n 1)
    #echo "$nFilesExpected expected files"
    nFilesOut=$(ls $block/out/ | wc -l)
    #echo "$nFilesOut out files"

    #if [[ $block != "analyzer_HiggsMuMu_v1.5/Muon1_2024G" ]]; then
    #    continue
    #fi

    if [[ "$nFilesExpected" == *"Queue"* ]]; then
        nFilesExpected=1
    fi
    
    if [ $nFilesExpected -ne $nFilesOut ]; then
        #echo "************** Not all analyzer ran in $block **************"
        blockError=true
        ((fail_count++))
        missingFiles=$((nFilesExpected - nFilesOut))
        echo "$block has $missingFiles missing files" >> "$OUTFILE"
    fi

    #expectedFileNum=0
    for file in "$block"/err/*.err; do
        # Skip if no .err files exist
        [ -e "$file" ] || continue

        # Count lines (change to wc -c if you meant bytes instead)
        count=$(wc -l < "$file")
        #echo "File $file count $count"

        last_line=$(tail -n 1 "$file")

        if [[ "$last_line" != "cp: cannot stat 'data/pileup/*.root': No such file or directory" ]]; then
            blockError=true
            ((fail_count++))
            echo "$file" >> "$OUTFILE"
        fi

        #if [ "$count" -ge 7 ]; then
        #    #echo "File '$file' has length $count (greater than 6)"
        #    blockError=true
        #    ((fail_count++))
        #    echo "$file" >> "$OUTFILE"
        #fi

    done

    #Find analyzer timing information
    for file in "$block"/log/*.log; do
        #echo "$file"
        first_line=$(head -n 1 "$file")
        second_line=$(head -n 3 "$file" | tail -n 1)
        #last_line=$(tail -n 20 "$file" | head -n 1)
        #last_line=$(grep "Job terminated." "$file" | tail -n 1)
        last_line=$(grep -E '^005 \([0-9]+\.[0-9]+\.[0-9]+\) [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} Job terminated\.$' "$file" | tail -n 1)
        #echo "$last_line"

        submission_time=$(grep -oE '[0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$first_line")
        transfer_time=$(grep -oE '[0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$second_line")
        finish_time=$(grep -oE '[0-9]{2}:[0-9]{2}:[0-9]{2}' <<< "$last_line")

        #echo "SubTime: $submission_time"
        #echo "TransTime: $transfer_time"
        #echo "FinTime: $finish_time"

        st=$(to_seconds "$submission_time")
        tt=$(to_seconds "$transfer_time")
        ft=$(to_seconds "$finish_time")

        total_job_time=$(( ft - st ))
        running_job_time=$(( ft - tt))

        if (( $total_job_time <= 0)); then
            total_job_time=$(( 86400 - st + ft))
        fi

        if (( $running_job_time <= 0)); then
            running_job_time=$(( 86400 - tt + ft))
        fi

        if (( $running_job_time >= 36000)); then
            ((n_long_jobs++))
            echo "long job in $file of $(seconds_to_hms "$running_job_time")"
        fi

        total_job_times+=( $total_job_time )
        running_job_times+=( $running_job_time )
        #echo "$running_job_time"
    done

    if $blockError; then
        echo "************** Errors found in $block **************"
    fi

done


echo "------------------------------ $DIR ------------------------------"
EXPECTED_ANALYZER_JOBS=$(jq -r '.EXPECTED_ANALYZER_JOBS' expected_ana_job_number.json)
echo "Total job num: ${#total_job_times[@]} / $EXPECTED_ANALYZER_JOBS"

if (( ${#total_job_times[@]} < $EXPECTED_ANALYZER_JOBS )); then
    echo "THE TOTAL NUMBER OF EXPECTED JOBS HAVE NOT BEEN RUN: ${#total_job_times[@]} / $EXPECTED_ANALYZER_JOBS"
    echo "THE TOTAL NUMBER OF EXPECTED JOBS HAVE NOT BEEN RUN: ${#total_job_times[@]} / $EXPECTED_ANALYZER_JOBS" >> "$OUTFILE"
fi

max_job_time=${total_job_times[0]}; for x in "${total_job_times[@]}"; do ((x>max_job_time)) && max_job_time=$x; done
max_run_time=${running_job_times[0]}; for x in "${running_job_times[@]}"; do ((x>max_run_time)) && max_run_time=$x; done
min_run_time=${running_job_times[0]}; for x in "${running_job_times[@]}"; do ((x<min_run_time)) && min_run_time=$x; done

sum=0; for x in "${running_job_times[@]}"; do ((sum+=x)); done;
avg_run_time=$(($sum/${#running_job_times[@]}))
echo "total running job time: $sum"
echo "num jobs ${#running_job_times[@]}"

sumTot=0; for x in "${total_job_times[@]}"; do ((sumTot+=x)); done;
avg_run_timeTot=$(($sumTot/${#total_job_times[@]}))
echo "total job time: $sumTot"
echo "num jobs ${#running_job_times[@]}"

echo "The total job time is $(seconds_to_hms "$max_job_time")"
echo "The max run time is $(seconds_to_hms "$max_run_time")"
echo "The min run time is $(seconds_to_hms "$min_run_time")"
echo "The avg run time is $(seconds_to_hms "$avg_run_time")" 
echo "The avg total time is $(seconds_to_hms "$avg_run_timeTot")" 

echo "------------------------------ $DIR ------------------------------" >> "$OUTFILE"
echo "Total num of long jobs: $n_long_jobs"
echo "Total job num: ${#total_job_times[@]}" >> "$OUTFILE"

echo "The total job time is $(seconds_to_hms "$max_job_time")" >> "$OUTFILE"
echo "The max run time is $(seconds_to_hms "$max_run_time")" >> "$OUTFILE"
echo "The min run time is $(seconds_to_hms "$min_run_time")" >> "$OUTFILE"
echo "The avg run time is $(seconds_to_hms "$avg_run_time")" >> "$OUTFILE"

if [ "$fail_count" -eq 0 ]; then
    echo "No extra errors were thrown in any jobs"
    echo "Check $OUTFILE for timing info"
    #rm -f "$OUTFILE"
else
    echo "There are errors check $OUTFILE for a list of problematic eras"
fi