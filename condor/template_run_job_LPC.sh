#!/bin/bash

#######################
# Debugging purposes
#######################
voms-proxy-info --all
ls -l

###############################
# Define input parameters
###############################
output_name=$1
job_number=$2
is_data=$3
year=$4
output_Directory=$5
cmssw_version=$6
ifZ=$7
ifH=$8

file_type="data"
if [ "$is_data" == "F" ]; then file_type="mc"; fi
muon_pt_syst=${9:-nominal}
ifSync=${10}

###############################
# Define exec and setup cmssw
###############################
workDir=`pwd`
executable="HmmAnalyzer"
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc12
#tar -zxvf cms_setup.tar.gz
scramv1 project CMSSW $cmssw_version

DATA_FOLDER="$cmssw_version/src/data/"

###########################################
# Copy input list and exec to cmssw folder
###########################################
cp input_list.tgz $cmssw_version/src/
cp ${executable} $cmssw_version/src/.

mkdir -p ${DATA_FOLDER}/Rocco/
cp RoccoR${year}.txt ${DATA_FOLDER}/Rocco/

mkdir -p ${DATA_FOLDER}/btagSF/
cp DeepCSV_94XSF_V3_B_F.csv ${DATA_FOLDER}/btagSF/

mkdir -p ${DATA_FOLDER}/leptonSF/${year}/
mkdir -p ${DATA_FOLDER}/jetCorrections/${year}/

#cp jetvetomaps.json.gz ${DATA_FOLDER}/jetCorrections/${year}/
#cp jet_jerc.json.gz ${DATA_FOLDER}/jetCorrections/${year}/
#cp JecConfigAK4.json ${DATA_FOLDER}/jetCorrections/${year}/
#cp JecConfigAK8.json ${DATA_FOLDER}/jetCorrections/${year}/
#cp jer_smear.json.gz ${DATA_FOLDER}/jetCorrections/${year}/
#cp JvmConfig.json ${DATA_FOLDER}/jetCorrections/${year}/

cp jetvetomaps.json.gz ${DATA_FOLDER}/jetCorrections/${year}/
cp jet_jerc.json.gz ${DATA_FOLDER}/jetCorrections/${year}/
cp JecConfigAK4.json ${DATA_FOLDER}/jetCorrections/
cp JecConfigAK8.json ${DATA_FOLDER}/jetCorrections/
cp jer_smear.json.gz ${DATA_FOLDER}/jetCorrections/
cp JvmConfig.json ${DATA_FOLDER}/jetCorrections/



mkdir -p ${cmssw_version}/src/RazorCommon/data/
mkdir -p ${cmssw_version}/src/RazorCommon/bin/
mkdir -p ${cmssw_version}/src/RazorCommon/python/
cp muon_scalesmearing.json.gz ${DATA_FOLDER}/leptonSF/${year}/
cp muon_Z.json.gz ${DATA_FOLDER}/leptonSF/${year}/

cp FWLiteGoodLumi ${cmssw_version}/src/RazorCommon/bin/
cp Cert* ${cmssw_version}/src/RazorCommon/data/
cp loadJson.py ${cmssw_version}/src/RazorCommon/python/

mkdir -p ${DATA_FOLDER}/pileup/
cp Pileup*.root ${DATA_FOLDER}/pileup/
cp RunII_*.root ${DATA_FOLDER}/pileup/

########################################################################
# Copy when running manually (this will lead to unharmed errors in job)
########################################################################
cp data/Rocco/RoccoR${year}.txt ${DATA_FOLDER}/Rocco/
cp data/btagSF/DeepCSV_94XSF_V3_B_F.csv ${DATA_FOLDER}/btagSF/
#cp data/leptonSF/2016/*.root ${DATA_FOLDER}/leptonSF/2016/
#cp data/jetCorrections/${year}/jetvetomaps.json.gz ${DATA_FOLDER}/jetCorrections/${year}/
#cp data/jetCorrections/${year}/jet_jerc.json.gz ${DATA_FOLDER}/jetCorrections/${year}/
#cp data/jetCorrections/JecConfigAK4.json ${DATA_FOLDER}/jetCorrections/${year}/
#cp data/jetCorrections/JecConfigAK8.json ${DATA_FOLDER}/jetCorrections/${year}/
#cp data/jetCorrections/jer_smear.json.gz ${DATA_FOLDER}/jetCorrections/${year}/
#cp data/jetCorrections/JvmConfig.json ${DATA_FOLDER}/jetCorrections/${year}/

cp data/jetCorrections/${year}/jetvetomaps.json.gz ${DATA_FOLDER}/jetCorrections/${year}/
cp data/jetCorrections/${year}/jet_jerc.json.gz ${DATA_FOLDER}/jetCorrections/${year}/
cp data/jetCorrections/JecConfigAK4.json ${DATA_FOLDER}/jetCorrections
cp data/jetCorrections/JecConfigAK8.json ${DATA_FOLDER}/jetCorrections
cp data/jetCorrections/jer_smear.json.gz ${DATA_FOLDER}/jetCorrections
cp data/jetCorrections/JvmConfig.json ${DATA_FOLDER}/jetCorrections

cp data/leptonSF/${year}/muon_scalesmearing.json.gz ${DATA_FOLDER}/leptonSF/${year}/
cp data/leptonSF/${year}/muon_Z.json.gz ${DATA_FOLDER}/leptonSF/${year}/
cp data/pileup/*.root ${DATA_FOLDER}/pileup/

###########################
# Get cmssw environment
###########################
cd $cmssw_version/src/
eval `scram runtime -sh`
tar vxzf input_list.tgz
inputfilelist=input_list_${job_number}.txt
echo "input file: " $inputfilelist

###################################
# Copy input files ahead of time
###################################
rm -rf inputs
mkdir -p inputs

rm -f tmp_input_list.txt
touch tmp_input_list.txt

max_retries=6
copy_failed=0
n_copied=0

while IFS= read -r input_file || [ -n "$input_file" ]; do

    [ -z "$input_file" ] && continue

    base_file=$(basename "$input_file")
    output_file="inputs/${base_file}"

    echo "----------------------------------------"
    echo "Copying Input File:"
    echo "  source:      ${input_file}"
    echo "  destination: ${output_file}"

    success=0
    xrdcp_log="xrdcp_${base_file}.log"

    rm -f "${xrdcp_log}"

    for attempt in $(seq 1 ${max_retries}); do
        echo "xrdcp attempt ${attempt}/${max_retries}"

        rm -f "${output_file}"

        # Save stdout/stderr to a log file, do NOT send it directly to .err
        xrdcp -f --nopbar "${input_file}" "${output_file}" > "${xrdcp_log}" 2>&1
        xrdcp_status=$?

        if [ ${xrdcp_status} -eq 0 ] && [ -s "${output_file}" ]; then
            echo "Copy succeeded: ${output_file}"
            success=1
            rm -f "${xrdcp_log}"
            break
        else
            echo "[WARNING] Copy failed on attempt ${attempt}/${max_retries}"
            echo "[WARNING] xrdcp status: ${xrdcp_status}"

            if [ -e "${output_file}" ]; then
                echo "[WARNING] Output file exists but may be empty/corrupt:"
                ls -lh "${output_file}"
            fi

            if [ ${attempt} -lt ${max_retries} ]; then
                echo "[WARNING] Will retry in 10 seconds..."
                sleep 10
            fi
        fi
    done

    if [ ${success} -eq 1 ]; then
        echo "${output_file}" >> tmp_input_list.txt
        n_copied=$((n_copied + 1))
    else
        echo "[ERROR] Failed to copy file after ${max_retries} attempts:" >&2
        echo "[ERROR] ${input_file}" >&2
        echo "[ERROR] Final xrdcp output:" >&2
        cat "${xrdcp_log}" >&2

        copy_failed=1
    fi

done < "${inputfilelist}"

echo "----------------------------------------"
echo "Finished copying input files"
echo "Number of copied files: ${n_copied}"
echo "Contents of inputs/:"
ls -lh inputs/

echo "Contents of tmp_input_list.txt:"
cat tmp_input_list.txt

if [ ${copy_failed} -ne 0 ]; then
    echo "[ERROR] At least one input file failed to copy. Exiting job." >&2
    exit 20
fi

if [ ${n_copied} -eq 0 ]; then
    echo "[ERROR] No input ROOT files were copied. Exiting job." >&2
    exit 21
fi

if ! ls inputs/*.root >/dev/null 2>&1; then
    echo "[ERROR] No .root files found in inputs/. Exiting job." >&2
    exit 22
fi

if [ ! -s tmp_input_list.txt ]; then
    echo "[ERROR] tmp_input_list.txt is empty. Exiting job." >&2
    exit 23
fi

ls -lh inputs/*.root
file inputs/*.root


###########################
# Run executable
###########################
echo "Executing Analysis executable:"
echo "./${executable} tmp_input_list.txt ${output_name}_${job_number}.root ${file_type} ${is_data} ${year} ${ifZ} ${ifH} ${muon_pt_syst} ${ifSync}"
./${executable} tmp_input_list.txt ${output_name}_${job_number}.root ${file_type} ${is_data} ${year} ${ifZ} ${ifH} ${muon_pt_syst} ${ifSync}


ls -l

###########################
# Run goodLumi Validation
###########################

if [[ "$file_type" == "data" ]]; then
    echo "Executing goodLumi check:"
    cd RazorCommon/bin
    cert_file=$(ls ../data/)

    echo "./FWLiteGoodLumi ../python/loadJson.py ../../${output_name}_${job_number}.root ../../${output_name}_${job_number}_GoodLumi.root"
    sed -i "/JSONfile =/c\JSONfile = '../data/${cert_file}'" ../python/loadJson.py
    #echo "Output goodLumi file: " $outfile
    ./FWLiteGoodLumi ../python/loadJson.py ../../${output_name}_${job_number}.root ../../${output_name}_${job_number}_GoodLumi.root

    cd ../../
    
    echo "changing outfile to be named like infile"
    mv ${output_name}_${job_number}_GoodLumi.root ${output_name}_${job_number}.root
fi

################################################################
# Copy output file to /eos space -- define in submitter code
################################################################
echo ${output_Directory}
xrdfs root://cmseos.fnal.gov mkdir -p /store/group/lpchmumu/${output_Directory}

xrdcp -f ${output_name}_${job_number}.root root://cmseos.fnal.gov//store/group/lpchmumu/${output_Directory}/${output_name}_${job_number}.root
echo "Output file saved in root://cmseos.fnal.gov//store/group/lpchmumu/${output_Directory}/${output_name}_${job_number}.root"
rm ${output_name}_${job_number}.root

rm inputs -rv

cd -
