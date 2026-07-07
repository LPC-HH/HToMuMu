#!/bin/bash

#######################
# Debugging purposes
#######################
voms-proxy-info --all
ls -l

###############################
# Define input parameters
###############################
input_file=$1
weight_file=$2
output_folder=$3
era=$4
channel=$5
file_type=$6
ifZ=$7
ifH=$8 
jet_syst=$9
cmssw_version=${10}
job_number=${11}

is_data="F"
if [[ $file_type == *"Data"* ]]; then is_data="T"; fi

is_signal="F"
if [[ $file_type == *"signal"* ]]; then is_signal="T"; fi

###############################
# Define exec and setup cmssw
###############################
workDir=`pwd`
executable="CreateTuple"
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc12
#tar -zxvf cms_setup.tar.gz
scramv1 project CMSSW $cmssw_version

#######################################
# Copy input and exec to cmssw folder
#######################################
cp ${executable} $cmssw_version/src/.
xrdcp root://cmseos.fnal.gov/${input_file} $cmssw_version/src/input_file.root
xrdcp root://cmseos.fnal.gov/${weight_file} $cmssw_version/src/weight_file.root

###########################
# Get cmssw environment
###########################
cd $cmssw_version/src/
eval `scram runtime -sh`

###########################
# Run executable
###########################
echo "Executing Create Tuple executable:"
echo "./${executable} input_file.root weight_file.root ./ ${era} ${channel} ${is_data} ${is_signal} ${ifZ} ${ifH} ${jet_syst}"
./${executable} input_file.root weight_file.root ./ ${era} ${channel} ${is_data} ${is_signal} ${ifZ} ${ifH} ${jet_syst}

# Copy output to output_folder
ls -l
################################################################
# Copy output file to /eos space -- define in submitter code
################################################################
echo ${output_folder}

xrdcp -f ${channel}_${era}_tuples.root root://cmseos.fnal.gov/${output_folder}${channel}_${era}_${job_number}_tuples.root
echo "Output file saved in root://cmseos.fnal.gov/${output_folder}${channel}_${era}_${job_number}_tuples.root"

rm ${channel}_${era}_tuples.root

cd -
