#!/bin/bash

set -uo pipefail

#######################
# Helper functions
#######################

error_exit() {
    echo "[ERROR] $1" >&2
    exit "${2:-1}"
}

make_xrootd_url() {
    local path="$1"

    if [[ "$path" == root://* ]]; then
        printf '%s\n' "$path"
    else
        # Remove leading slashes and then construct the standard
        # root://host//store/... URL.
        printf 'root://cmseos.fnal.gov//%s\n' "${path#/}"
    fi
}

xrdcp_with_retry() {
    local source="$1"
    local destination="$2"
    local description="$3"
    local max_attempts="${4:-5}"
    local retry_delay="${5:-20}"

    local attempt
    local status=1
    local error_file

    error_file=$(mktemp) || {
        echo "[ERROR] Could not create temporary error file." >&2
        return 1
    }

    for ((attempt = 1; attempt <= max_attempts; attempt++)); do
        : > "$error_file"

        # Remove an incomplete local destination left by an earlier attempt.
        if [[ "$destination" != root://* ]]; then
            rm -f "$destination"
        fi

        echo "${description}: attempt ${attempt}/${max_attempts}"

        if xrdcp -f "$source" "$destination" 2>"$error_file"; then
            echo "${description}: successful"
            rm -f "$error_file"
            return 0
        else
            status=$?
        fi

        if ((attempt < max_attempts)); then
            echo "${description}: attempt failed; retrying in ${retry_delay} seconds"
            sleep "$retry_delay"
        fi
    done

    echo "[ERROR] ${description} failed after ${max_attempts} attempts." >&2
    echo "[ERROR] Source: ${source}" >&2
    echo "[ERROR] Destination: ${destination}" >&2
    cat "$error_file" >&2

    rm -f "$error_file"
    return "$status"
}

#######################
# Debug information
#######################

echo "========================================"
echo "Initial working directory: $(pwd)"
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo "========================================"

voms-proxy-info --all || true
ls -l

###############################
# Check input parameters
###############################

if (( $# < 11 )); then
    echo "Usage:" >&2
    echo "$0 input_file weight_file output_folder era channel file_type ifZ ifH jet_syst cmssw_version job_number" >&2
    exit 2
fi

input_file="$1"
weight_file="$2"
output_folder="$3"
era="$4"
channel="$5"
file_type="$6"
ifZ="$7"
ifH="$8"
jet_syst="$9"
cmssw_version="${10}"
job_number="${11}"

is_data="F"
if [[ "$file_type" == *"Data"* ]]; then
    is_data="T"
fi

is_signal="F"
if [[ "$file_type" == *"signal"* ]]; then
    is_signal="T"
fi

###############################
# Define paths
###############################

work_dir=$(pwd)
executable="CreateTuple"

input_url=$(make_xrootd_url "$input_file")
weight_url=$(make_xrootd_url "$weight_file")

output_file="${channel}_${era}_tuples.root"
remote_output_path="${output_folder%/}/${channel}_${era}_${job_number}_tuples.root"
output_url=$(make_xrootd_url "$remote_output_path")

echo "Input URL:       $input_url"
echo "Weight URL:      $weight_url"
echo "Output URL:      $output_url"
echo "CMSSW version:   $cmssw_version"
echo "Era:             $era"
echo "Channel:         $channel"
echo "Data:            $is_data"
echo "Signal:          $is_signal"
echo "Jet systematic:  $jet_syst"

###############################
# Set up CMSSW
###############################

source /cvmfs/cms.cern.ch/cmsset_default.sh ||
    error_exit "Could not source the CMS environment." 10

export SCRAM_ARCH=el9_amd64_gcc12

if [[ ! -d "$cmssw_version/src" ]]; then
    scramv1 project CMSSW "$cmssw_version" ||
        error_exit "Could not create CMSSW project $cmssw_version." 11
fi

[[ -x "$executable" ]] ||
    error_exit "Executable not found or not executable: ${work_dir}/${executable}" 12

cp "$executable" "$cmssw_version/src/" ||
    error_exit "Could not copy $executable into $cmssw_version/src/." 13

###############################
# Copy input files
###############################

xrdcp_with_retry \
    "$input_url" \
    "$cmssw_version/src/input_file.root" \
    "Copying analyzer input file" \
    5 \
    20 ||
    error_exit "Unable to obtain the analyzer input file. CreateTuple will not be run." 20

xrdcp_with_retry \
    "$weight_url" \
    "$cmssw_version/src/weight_file.root" \
    "Copying weight file" \
    5 \
    20 ||
    error_exit "Unable to obtain the weight file. CreateTuple will not be run." 21

[[ -s "$cmssw_version/src/input_file.root" ]] ||
    error_exit "input_file.root is missing or empty after xrdcp." 22

[[ -s "$cmssw_version/src/weight_file.root" ]] ||
    error_exit "weight_file.root is missing or empty after xrdcp." 23

###############################
# Enter CMSSW environment
###############################

cd "$cmssw_version/src/" ||
    error_exit "Could not enter $cmssw_version/src/." 30

eval "$(scram runtime -sh)" ||
    error_exit "Could not initialize the CMSSW runtime." 31

###############################
# Run CreateTuple
###############################

echo "========================================"
echo "Executing CreateTuple:"
echo "./${executable} input_file.root weight_file.root ./ ${era} ${channel} ${is_data} ${is_signal} ${ifZ} ${ifH} ${jet_syst}"
echo "========================================"

if ! "./${executable}" \
    input_file.root \
    weight_file.root \
    ./ \
    "$era" \
    "$channel" \
    "$is_data" \
    "$is_signal" \
    "$ifZ" \
    "$ifH" \
    "$jet_syst"; then

    error_exit "CreateTuple exited with an error." 40
fi

###############################
# Check generated output
###############################

ls -lh

if [[ ! -s "$output_file" ]]; then
    error_exit "CreateTuple finished, but output file $output_file was not created or is empty." 41
fi

###############################
# Copy output to EOS
###############################

xrdcp_with_retry \
    "$output_file" \
    "$output_url" \
    "Uploading tuple output" \
    5 \
    20 ||
    error_exit "Output upload failed. The local output file was not removed." 50

echo "Output file successfully saved at:"
echo "$output_url"

rm -f "$output_file"

cd "$work_dir" || exit 0

echo "Job completed successfully."
exit 0
