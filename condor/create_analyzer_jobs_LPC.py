#!/usr/bin/python

import os
import sys
import json
sys.path.append('../list')
from listDatasets_Run3 import datasets_info

import utils.version as v

analyzer = "HmmAnalyzer"
analysis = "HiggsMuMu"
outputfile = analysis + "_" + v.ANALYZER_VERSION_NUMBER

golden_json = {
        '2022':'Cert_Collisions2022_355100_362760_Golden.json',
        '2022EE':'Cert_Collisions2022_355100_362760_Golden.json',
        '2023':'Cert_Collisions2023_366442_370790_Golden.json',
        '2023BPix':'Cert_Collisions2023_366442_370790_Golden.json',
        '2024':'Cert_Collisions2024_378981_386951_Golden.json',
        '2025':'Cert_Collisions2025_391658_398903_Golden.json'
        }

# Skip these datasets
skip_dataset = [
    "DoubleMuon_2022A",
    "DoubleMuon_2022B",
    "DoubleMuon_2022C",
    "Muon0_2023B",
    "Muon1_2023B",
]
skip_pattern = [
    # "Summer22",
    # "Summer22EE",
    # "_2022",
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
    #"VBF_Summer22",
    #"VBF_Summer22EE",
    #"VBF_Summer23",
    #"VBF_Summer23BPix",
    #"VBF_Summer24",
    #"ggH_Summer22",
    #"ggH_Summer22EE",
    #"ggH_Summer23",
    #"ggH_Summer23BPix",
    #"ggH_Summer24",
#    "DY50to120_Summer22",
#    "DY120to200_Summer24",
#    "WWtoLNu2Q_Summer22",
#    "Muon_2022C",
#    "Muon_2022D",
#    "SingleMuon_2022C",
#]

include_Z = "F"
include_H = "T"

# cmsswReleaseVersion = "CMSSW_10_6_5"
CMSSW_BASE_DIR = os.getenv('CMSSW_BASE')
SCRAM_ARCH = os.getenv('SCRAM_ARCH')
# Analyzer_DIR = CMSSW_BASE_DIR + "/src/HmmAna/HmmAna/"
Condor_BASE_DIR = os.getcwd() + "/"
Analyzer_DIR = Condor_BASE_DIR.split("condor/")[0]
# Condor_BASE_DIR = Analyzer_DIR + "condor/"
Inputfiles_DIR = Analyzer_DIR + "list/"

cmsswReleaseVersion = CMSSW_BASE_DIR.split("/")[-1]
print("Using CMSSW version " + cmsswReleaseVersion)
print("Running analysis version " + v.ANALYZER_VERSION_NUMBER)
print("Analyzer: " + "%s/bin/%s"%(Analyzer_DIR, analyzer))

# Create script to send all of the jobs directly
send_all_jobs = open(Condor_BASE_DIR + "/condor_job_sender.sh", "w+")

total_job_number = 0

# Create directory for condor jobs
for dataset_name in list_datasets:
    match_pattern = [True for pattern in skip_pattern if pattern in dataset_name]
    if (dataset_name in skip_dataset) or (True in match_pattern):
        continue

    list_file = dataset_name + ".list"
    print("\n----- %s -----"%(dataset_name))
    if not os.path.exists(Inputfiles_DIR + list_file):
        print("List file does not exist. Skipping!")
        continue

    list_all_runs = open(Inputfiles_DIR + list_file, "r")

    isData, max_runs_per_job, year, type_info, _ = datasets_info[dataset_name]

    Output_DIR = "analyzer_%s/"%(outputfile) + "%s/"%(dataset_name)
    Job_DIR = Condor_BASE_DIR + Output_DIR
    if os.path.exists(Job_DIR + "input_list.tgz"):
        print(" (!) Condor directory already exists. Skipping!")
        continue

    # Create condor directories
    os.system("mkdir -p " + Job_DIR)
    os.system("mkdir -p " + Job_DIR + "/log/")
    os.system("mkdir -p " + Job_DIR + "/out/")
    os.system("mkdir -p " + Job_DIR + "/err/")

    #####################################
    # Job splitting
    #####################################
    n_runs_in_job = 0
    n_jobs = 1
    list_runs_in_job = open(Job_DIR + "input_list_%i.txt"%(n_jobs), "w")
    for run in list_all_runs:
        # Close current list of runs and open the next one
        if n_runs_in_job >= max_runs_per_job:
            list_runs_in_job.close()
            n_runs_in_job = 0
            n_jobs += 1
            list_runs_in_job = open(Job_DIR + "input_list_%i.txt"%(n_jobs), "w")

        # Save run path in list
        list_runs_in_job.write(run)
        n_runs_in_job += 1
    total_job_number += n_jobs
    list_runs_in_job.close()
    # Pack all txt files in a single tar file
    os.system("cd " + Job_DIR + "; tar czf input_list.tgz input_list_*.txt")
    os.system("cd " + Job_DIR + "; rm input_list_*.txt")

    ###################################################
    # Copy run script, executable, and required files
    ###################################################
    os.system("cp " + "%s/condor/template_run_job_LPC.sh"%(Analyzer_DIR) + " " + "%s/run_job_LPC.sh"%(Job_DIR))
    os.system("cp " + "%s/bin/%s"%(Analyzer_DIR, analyzer) + " " + Job_DIR)
    Analyzer_Data_DIR = Analyzer_DIR + "data/"
    Job_Data_DIR = Job_DIR + "/data/"
    os.system("mkdir -p " + Job_Data_DIR)
    os.system("mkdir -p " + Job_Data_DIR + "Rocco/")
    os.system("cp " + "%s/Rocco/RoccoR%s.txt"%(Analyzer_Data_DIR, year) + " " + "%s/Rocco/"%(Job_Data_DIR))
    os.system("mkdir -p " + Job_Data_DIR + "btagSF/")
    os.system("cp " + "%s/btagSF/DeepCSV_94XSF_V3_B_F.csv"%(Analyzer_Data_DIR) + " " + "%s/btagSF/"%(Job_Data_DIR))
    # os.system("mkdir -p " + Job_Data_DIR + "leptonSF/%s"%(year))
    # os.system("cp " + "%s/leptonSF/%s/*.root"%(Analyzer_Data_DIR, year) + " " + "%s/leptonSF/%s/"%(Job_Data_DIR, year))

    #get RazorCommon as well
    if(isData=="T"):
        os.system("mkdir -p " + Job_DIR + "RazorCommon/data/")
        os.system("mkdir -p " + Job_DIR + "RazorCommon/bin/")
        os.system("mkdir -p " + Job_DIR + "RazorCommon/python/")
        os.system("cp -r " + "%s/RazorCommon/data/Run3/"%(Analyzer_DIR) + " " + "%s/RazorCommon/data/"%(Job_DIR))
        os.system("cp " + "%s/bin/%s/FWLiteGoodLumi"%(CMSSW_BASE_DIR,SCRAM_ARCH) + " " "%s/RazorCommon/bin/"%(Job_DIR))
        os.system("cp " + "%s/RazorCommon/python/loadJson.py"%(Analyzer_DIR) + " " "%s/RazorCommon/python/"%(Job_DIR))
    
    if(year != "2025"):
        os.system("mkdir -p " + Job_Data_DIR + "leptonSF/%s/"%(year))
        os.system("cp " + "%s/leptonSF/%s/*.gz"%(Analyzer_Data_DIR, year) + " " + "%s/leptonSF/%s/"%(Job_Data_DIR, year))
    os.system("mkdir -p " + Job_Data_DIR + "pileup")
    pileup_file = "PileupReweight_Summer%s"%(year[2:])
    if not os.path.exists(Analyzer_Data_DIR + "/pileup/%s.root"%(pileup_file)):
        print(" (!) Pileup file not found for this era. Using 2016 as default.")
        pileup_file = "RunII_2016_data"
    os.system("cp " + Analyzer_Data_DIR + "/pileup/%s.root"%(pileup_file) + " " + "%s/pileup/"%(Job_Data_DIR))

    #####################################
    # Create Condor JDL file
    #####################################
    jobfile_JDL = open(Job_DIR + "/task.jdl", "w+")
    jobfile_JDL.write("Universe  = vanilla" + "\n")
    jobfile_JDL.write("Executable = ./run_job_LPC.sh" + "\n")

    EOS_SUBPATH = os.getenv('LOGNAME') + "/analyzer_%s/"%(outputfile) + type_info + "/%s/"%(dataset_name)
    os.system("xrdfs root://cmseos.fnal.gov mkdir -p /store/group/lpchmumu/"+ EOS_SUBPATH)
    args = outputfile + " $(I) " + isData + " " + year + " " + EOS_SUBPATH + " " + cmsswReleaseVersion + " "  + include_Z + " " + include_H
    jobfile_JDL.write("Arguments = " + args + "\n")

    jobfile_JDL.write("Log = log/jobR$(I).$(Cluster).$(Process).log" + "\n")
    jobfile_JDL.write("Output = out/jobR$(I).$(Cluster).$(Process).out" + "\n")
    jobfile_JDL.write("Error = err/jobR$(I).$(Cluster).$(Process).err" + "\n")
    jobfile_JDL.write("x509userproxy = $ENV(X509_USER_PROXY)" + "\n")

    transfer_files = Job_DIR + "/run_job_LPC.sh, "
    transfer_files += Job_DIR + "/input_list.tgz, "
    transfer_files += Job_DIR + "/" + analyzer + ", "
    transfer_files += Job_Data_DIR + "/Rocco/RoccoR" + year + ".txt, "
    transfer_files += Job_Data_DIR + "/btagSF/DeepCSV_94XSF_V3_B_F.csv, "

    if(year != "2025"):
        transfer_files += Job_Data_DIR + "/leptonSF/" + year + "/muon_Z.json.gz, "
    if(isData=="T"):
        transfer_files += Job_DIR + "/RazorCommon/bin/FWLiteGoodLumi, "
        transfer_files += Job_DIR + "/RazorCommon/data/Run3/" + golden_json[year] + ", "
        transfer_files += Job_DIR + "/RazorCommon/python/loadJson.py, "

    transfer_files += Job_Data_DIR + "/pileup/" + pileup_file + ".root"
    jobfile_JDL.write("transfer_input_files = " + transfer_files + "\n")

    jobfile_JDL.write("should_transfer_files = YES" + "\n")
    jobfile_JDL.write("when_to_transfer_output = ON_EXIT" + "\n\n# Resources request\n")
    jobfile_JDL.write("RequestMemory = 4500 \n\n# Jobs selection\n")

    jobfile_JDL.write("Queue I from (")
    for i in range(1, n_jobs+1):
        jobfile_JDL.write(str(i)+"\n")
    jobfile_JDL.write(")\n")
    jobfile_JDL.close()

    print("Send single job with:")
    print(" > cd " + Job_DIR + "; condor_submit task.jdl")
    send_all_jobs.write("cd " + Job_DIR + "\n")
    send_all_jobs.write("condor_submit task.jdl" + "\n")

print("\n----- End -----")
print("Run all generated jobs with:")
print(" > bash condor_job_sender.sh")
print("Expected number of jobs: {}".format(total_job_number))

with open("expected_ana_job_number.json", "w") as f:
    json.dump({"EXPECTED_ANALYZER_JOBS": total_job_number}, f)
    
send_all_jobs.close()
