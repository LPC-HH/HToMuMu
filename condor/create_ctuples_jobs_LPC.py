#!/usr/bin/python

import os
import sys
import json
sys.path.append('../list')
from listDatasets_Run3 import datasets_info

import utils.version as v

# analyzer = "HmmAnalyzer"
# analysis = "HiggsMuMu"
# outputfile = analysis

# Skip these datasets
skip_dataset = [
    "DoubleMuon_2022A",
    "DoubleMuon_2022B",
    "DoubleMuon_2022C",
    "Muon0_2023B",
    "Muon1_2023B",
]
skip_pattern = [
    ## Unwanted sets
    "DYJetstoLL",
    "DYto2L-2Jets",
    "TWminusto4Q",
    "TWminustoLNu2Q",
    "Tbar",
    "TQbar",
    "t-channel",
    "s-channel",
    "ZZto2Nu2Q",
    "WWto4Q",
    "WWtoLNu2Q",
    "WZtoLNu2Q",
    "DYto2Mu-2Jets",
]




list_datasets = datasets_info.keys()
# # Use in case you want to run over a specific list of datasets!
#list_datasets = [
 #   "VBF_Summer22",
    #"VBF_Summer22EE",
    #"VBF_Summer23",
    #"VBF_Summer23BPix",
    #"VBF_Summer24",
    #"ggH_Summer22",
    #"ggH_Summer22EE",
    #"ggH_Summer23",
    #"ggH_Summer23BPix",
    #"ggH_Summer24",
     #"DY120to200_Summer24v13",
     #"DY50to120_Summer24v13",
     #"Muon0_2024E",
    # "Muon1_2024E",
    #"ggH_Summer24",
#]

include_Z = "F"
include_H = "T"
jet_syst = "nominal"

muon_pt_syst = os.getenv("MUON_PT_SYST", "nominal")
valid_muon_pt_systs = [
    "nominal",
    "scale_up",
    "scale_down",
    "smearing_up",
    "smearing_down",
]
if muon_pt_syst not in valid_muon_pt_systs:
    print("Unsupported MUON_PT_SYST '{}'. Use one of: {}".format(
        muon_pt_syst, ", ".join(valid_muon_pt_systs)))
    sys.exit(1)

if muon_pt_syst != "nominal" and jet_syst == "nominal":
    print("Either muon pt syst or jet syst must be nominal")
    exit()

# Arguments
if (len(sys.argv) == 1):
    recreate_hadded_file = False
elif (len(sys.argv) > 2) or (sys.argv[1] not in ["T", "F"]):
    print("One argument is required! Add T or F if you want to recreate the tuple file")
    exit()
else:
    recreate_hadded_file = True if (sys.argv[1] == "T") else False

# cmsswReleaseVersion = "CMSSW_10_6_5"
CMSSW_BASE_DIR = os.getenv('CMSSW_BASE')
CONDOR_BASE_DIR = os.getcwd() + "/"
ANALYZER_DIR = CONDOR_BASE_DIR.split("condor/")[0]
Inputfiles_DIR = ANALYZER_DIR + "list/"

cmsswReleaseVersion = CMSSW_BASE_DIR.split("/")[-1]
print("Using CMSSW version " + cmsswReleaseVersion)
print("Running tuples version " + v.TUPLES_VERSION_NUMBER)

# Create script to send all of the jobs directly
send_all_jobs = open(CONDOR_BASE_DIR + "/condor_ctuple_job_sender.sh", "w+")

total_job_number = 0

# Create directory for condor jobs
for dataset_name in list_datasets:
    match_pattern = [True for pattern in skip_pattern if pattern in dataset_name]
    if (dataset_name in skip_dataset) or (True in match_pattern): #or ("ext1" in dataset_name) or (True in match_pattern):
        continue

    print("\n----- %s -----"%(dataset_name))

    #isData, _, era, type_info, _ = datasets_info[dataset_name]
    isData, max_runs_per_job, era, type_info, _ = datasets_info[dataset_name]
    channel = dataset_name.split("_Summer")[0]

    user = os.getenv('LOGNAME')
    EOS_BASE_DIR = "/store/group/lpchmumu/" + user + "/analyzer_HiggsMuMu_" + v.ANALYZER_VERSION_NUMBER + "/"

    list_file = dataset_name + ".list"
    if not os.path.exists(Inputfiles_DIR + list_file):
        print("List file does not exist. Skipping!")
        continue

    list_all_runs = open(ANALYZER_DIR + "list/" + list_file, "r")


    if muon_pt_syst == "nominal":
        WEIGHT_FILE = EOS_BASE_DIR + type_info + "/%s/"%(dataset_name) + f"SumGenWeight.root"
    else:
        WEIGHT_FILE = EOS_BASE_DIR + type_info + "/%s"%(dataset_name) + "_%s/"%(muon_pt_syst) + f"SumGenWeight.root"

    if not os.path.exists("/eos/uscms/" + WEIGHT_FILE):
        print("Merged file does not exist. Skipping!")
        continue

    #if(isData=='T'):
    #    INPUT_FILE = EOS_BASE_DIR + type_info + "/%s/"%(dataset_name) + f"HiggsMuMu_" + v.ANALYZER_VERSION_NUMBER + "_$(I)_goodLumi.root"
    if muon_pt_syst == "nominal":
        INPUT_FILE = EOS_BASE_DIR + type_info + "/%s/"%(dataset_name) + f"HiggsMuMu_" + v.ANALYZER_VERSION_NUMBER + "_$(I).root"
    else:
        INPUT_FILE = EOS_BASE_DIR + type_info + "/%s"%(dataset_name) + "_%s/"%(muon_pt_syst) + f"HiggsMuMu_" + v.ANALYZER_VERSION_NUMBER + "_$(I).root"

    if muon_pt_syst != "nominal":
        OUTPUT_DIR = EOS_BASE_DIR + "tuples_" + v.TUPLES_VERSION_NUMBER  + "/%s"%(dataset_name) + "_%s/"%(muon_pt_syst)
    if jet_syst == "nominal":
        OUTPUT_DIR = EOS_BASE_DIR + "tuples_" + v.TUPLES_VERSION_NUMBER  + "/%s/"%(dataset_name)
    else:
        OUTPUT_DIR = EOS_BASE_DIR + "tuples_" + v.TUPLES_VERSION_NUMBER  + "/%s_"%(dataset_name)+ "%s/"%(jet_syst)

    os.system("xrdfs root://cmseos.fnal.gov mkdir -p "+ OUTPUT_DIR)

    file_name = channel + "_" + era + "_$(I)" + "_tuples.root"
    file_copy_name = channel + "_" + era + "_$(I)" + "_tuples_v1.root"

    hadd_exists = os.path.exists("/eos/uscms/" + OUTPUT_DIR + file_name)
    # print("Exists?", hadd_exists)
    hadd_copy_exists = os.path.exists("/eos/uscms/" + OUTPUT_DIR + file_copy_name)
    if hadd_exists:
        print("Tuples file already exists.")
        if recreate_hadded_file:
            if hadd_copy_exists:
                print("A tuple safe copy already exists! Overwriting.")
                comm = "xrdfs root://cmseos.fnal.gov rm /"
                comm+= OUTPUT_DIR + file_name
                os.system(comm)
            print("Creating new tuple safe copy!")
            comm = "xrdfs root://cmseos.fnal.gov mv /" + OUTPUT_DIR + file_name
            comm+= " /" + OUTPUT_DIR + file_copy_name
            os.system(comm)
        else:
            print("Skipping.")
            continue

    # JOB_DIR = CONDOR_BASE_DIR + "ctuples_" + v.TUPLES_VERSION_NUMBER + "/" + f"{dataset_name}/"# + "%s/"%(dataset_name) + blockString

    if muon_pt_syst != "nominal":
        JOB_DIR = CONDOR_BASE_DIR + "ctuples_" + v.TUPLES_VERSION_NUMBER + "/%s"%(dataset_name) + "_%s/"%(muon_pt_syst)# + "%s/"%(dataset_name) + blockString
    if jet_syst == "nominal":
        JOB_DIR = CONDOR_BASE_DIR + "ctuples_" + v.TUPLES_VERSION_NUMBER + "/" + f"{dataset_name}/"# + "%s/"%(dataset_name) + blockString
    else:
        JOB_DIR = CONDOR_BASE_DIR + "ctuples_" + v.TUPLES_VERSION_NUMBER + "/%s_"%(dataset_name)+ "%s/"%(jet_syst)# + "%s/"%(dataset_name) + blockString


    if os.path.exists(JOB_DIR):
        if len(os.listdir(JOB_DIR+"/log/")) != len(os.listdir(JOB_DIR+"/out/")):
            print("Previous job didn't finish well. Try running manually.")
            comm = "./CreateTuple /eos/uscms/" + INPUT_FILE + " "
            comm += "/eos/uscms/" + WEIGHT_FILE + " "
            comm += "/eos/uscms/" + OUTPUT_DIR + " " + era + " " + channel
            comm += " T" if "Data" in type_info else " F"
            comm += " T" if "signal" in type_info else " F"
            comm += " " + include_Z + " " + include_H + " " + jet_syst
            print(" > cd " + JOB_DIR + "; " + comm)
            send_all_jobs.write("cd " + JOB_DIR + "\n")
            send_all_jobs.write(comm + "\n")
            continue

    #print("Input file: " + INPUT_FILE)
    #print("Job dir: " + JOB_DIR)
    #print("Output dir: " + OUTPUT_DIR)
    print("Channel: " + channel)
    print("Type info: " + type_info)
    #continue

    
    # Create condor directories
    os.system("mkdir -p " + JOB_DIR)
    os.system("mkdir -p " + JOB_DIR + "/log/")
    os.system("mkdir -p " + JOB_DIR + "/out/")
    os.system("mkdir -p " + JOB_DIR + "/err/")


    n_runs_in_job = 0
    n_jobs = 1
    for run in list_all_runs:
        # Close current list of runs and open the next one
        if n_runs_in_job >= max_runs_per_job:
            n_runs_in_job = 0
            n_jobs += 1

        # Save run path in list
        n_runs_in_job += 1
    # Pack all txt files in a single tar file

    total_job_number += n_jobs

    ###################################################
    # Copy run script, executable, and required files
    ###################################################
    os.system("cp " + "%s/template_create_tuples_job_LPC.sh"%(CONDOR_BASE_DIR) + " " + "%s/run_job_LPC.sh"%(JOB_DIR))
    os.system("cp " + "%s/bin/CreateTuple"%(ANALYZER_DIR) + " " + JOB_DIR)

    #####################################
    # Create Condor JDL file
    #####################################
    jobfile_JDL = open(JOB_DIR + "/task.jdl", "w+")
    jobfile_JDL.write("Universe  = vanilla" + "\n")
    jobfile_JDL.write("Executable = ./run_job_LPC.sh" + "\n")

    args = INPUT_FILE + " " + WEIGHT_FILE + " " + OUTPUT_DIR + " " + era + " " + channel + " " + type_info + " "  + include_Z + " " + include_H + " " + jet_syst + " " + cmsswReleaseVersion + " " + "$(I)"
    jobfile_JDL.write("Arguments = " + args + "\n")

    jobfile_JDL.write("Log = log/jobR$(I).$(Cluster).$(Process).log" + "\n")
    jobfile_JDL.write("Output = out/jobR$(I).$(Cluster).$(Process).out" + "\n")
    jobfile_JDL.write("Error = err/jobR$(I).$(Cluster).$(Process).err" + "\n")
    jobfile_JDL.write("x509userproxy = $ENV(X509_USER_PROXY)" + "\n")

    transfer_files = JOB_DIR + "/run_job_LPC.sh, "
    transfer_files += JOB_DIR + "/CreateTuple, "
    jobfile_JDL.write("transfer_input_files = " + transfer_files + "\n")

    jobfile_JDL.write("should_transfer_files = YES" + "\n")
    jobfile_JDL.write("when_to_transfer_output = ON_EXIT" + "\n\n# Resources request\n")
    jobfile_JDL.write("RequestMemory = 2000 \n\n# Jobs selection\n")

    jobfile_JDL.write("Queue I from (")
    for i in range(1, n_jobs+1):
        jobfile_JDL.write(str(i)+"\n")
    jobfile_JDL.write(")\n")
    jobfile_JDL.close()

    print("Send single job with:")
    print(" > cd " + JOB_DIR + "; condor_submit task.jdl")
    send_all_jobs.write("cd " + JOB_DIR + "\n")
    send_all_jobs.write("condor_submit task.jdl" + "\n")

print("\n----- End -----")
print("Run all generated jobs with:")
print(" > bash condor_ctuple_job_sender.sh")

print("Expected number of jobs: {}".format(total_job_number))

with open("expected_ctup_job_number.json", "w") as f:
    json.dump({"EXPECTED_CTUPLE_JOBS": total_job_number}, f)

send_all_jobs.close()
