#!/usr/bin/python

import os
import sys
import json

sys.path.append('../list')
from listDatasets_Run3 import datasets_info

import utils.version as v


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

list_datasets = [
    dataset_name
    for dataset_name in datasets_info.keys()
    if dataset_name.startswith(("ggH_", "VBF_"))
]
# # Use in case you want to run over a specific list of datasets!
# list_datasets = [
#     "VBF_Summer22",
#     "VBF_Summer22EE",
#     "VBF_Summer23",
#     "VBF_Summer23BPix",
#     "VBF_Summer24",
#     "ggH_Summer22",
#     "ggH_Summer22EE",
#     "ggH_Summer23",
#     "ggH_Summer23BPix",
#     "ggH_Summer24",
# ]

include_Z = "F"
include_H = "T"


valid_muon_pt_systs = [
    "scale_up",
    "scale_down",
    "smearing_up",
    "smearing_down",
]


jet_jes_syst_names = [
    "CMS_scale_j_FlavorQCD",
    "CMS_scale_j_RelativeBal",
    "CMS_scale_j_HF",
    "CMS_scale_j_BBEC1",
    "CMS_scale_j_EC2",
    "CMS_scale_j_Absolute",

    "CMS_scale_j_BBEC1_2022",
    "CMS_scale_j_RelativeSample_2022",
    "CMS_scale_j_EC2_2022",
    "CMS_scale_j_HF_2022",
    "CMS_scale_j_Absolute_2022",

    "CMS_scale_j_BBEC1_2022EE",
    "CMS_scale_j_RelativeSample_2022EE",
    "CMS_scale_j_EC2_2022EE",
    "CMS_scale_j_HF_2022EE",
    "CMS_scale_j_Absolute_2022EE",

    "CMS_scale_j_BBEC1_2023",
    "CMS_scale_j_RelativeSample_2023",
    "CMS_scale_j_EC2_2023",
    "CMS_scale_j_HF_2023",
    "CMS_scale_j_Absolute_2023",

    "CMS_scale_j_BBEC1_2023BPix",
    "CMS_scale_j_RelativeSample_2023BPix",
    "CMS_scale_j_EC2_2023BPix",
    "CMS_scale_j_HF_2023BPix",
    "CMS_scale_j_Absolute_2023BPix",

    "CMS_scale_j_BBEC1_2024",
    "CMS_scale_j_RelativeSample_2024",
    "CMS_scale_j_EC2_2024",
    "CMS_scale_j_HF_2024",
    "CMS_scale_j_Absolute_2024",

    "CMS_res_j_eta0to1p93_pt0toInf_2022",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2022",
    "CMS_res_j_eta2p5to3p0_pt0to50_2022",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2022",
    "CMS_res_j_eta3to5_pt0to50_2022",
    "CMS_res_j_eta3to5_pt50toInf_2022",

    "CMS_res_j_eta0to1p93_pt0toInf_2022EE",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2022EE",
    "CMS_res_j_eta2p5to3p0_pt0to50_2022EE",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2022EE",
    "CMS_res_j_eta3to5_pt0to50_2022EE",
    "CMS_res_j_eta3to5_pt50toInf_2022EE",

    "CMS_res_j_eta0to1p93_pt0toInf_2023",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2023",
    "CMS_res_j_eta2p5to3p0_pt0to50_2023",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2023",
    "CMS_res_j_eta3to5_pt0to50_2023",
    "CMS_res_j_eta3to5_pt50toInf_2023",

    "CMS_res_j_eta0to1p93_pt0toInf_2023BPix",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2023BPix",
    "CMS_res_j_eta2p5to3p0_pt0to50_2023BPix",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2023BPix",
    "CMS_res_j_eta3to5_pt0to50_2023BPix",
    "CMS_res_j_eta3to5_pt50toInf_2023BPix",

    "CMS_res_j_eta0to1p93_pt0toInf_2024",
    "CMS_res_j_eta1p93to2p5_pt0toInf_2024",
    "CMS_res_j_eta2p5to3p0_pt0to50_2024",
    "CMS_res_j_eta2p5to3p0_pt50toInf_2024",
    "CMS_res_j_eta3to5_pt0to50_2024",
    "CMS_res_j_eta3to5_pt50toInf_2024",
]


jet_systs = []
for jes_name in jet_jes_syst_names:
    jet_systs.append(jes_name + "_up")
    jet_systs.append(jes_name + "_down")


def get_syst_points():
    """
    Returns pairs of:
        muon_pt_syst, jet_syst

    This does NOT include nominal.

    Rules:
      - muon pT systematics use non-nominal muon_pt_syst and nominal jet_syst
      - JES systematics use nominal muon_pt_syst and non-nominal jet_syst
      - never run muon and jet systematics at the same time
    """

    syst_points = []

    for muon_pt_syst in valid_muon_pt_systs:
        syst_points.append((muon_pt_syst, "nominal"))

    for jet_syst in jet_systs:
        syst_points.append(("nominal", jet_syst))

    return syst_points


# Arguments
if len(sys.argv) == 1:
    recreate_hadded_file = False
elif len(sys.argv) > 2 or sys.argv[1] not in ["T", "F"]:
    print("One argument is required! Add T or F if you want to recreate the tuple file")
    exit()
else:
    recreate_hadded_file = True if sys.argv[1] == "T" else False


CMSSW_BASE_DIR = os.getenv("CMSSW_BASE")
CONDOR_BASE_DIR = os.getcwd() + "/"
ANALYZER_DIR = CONDOR_BASE_DIR.split("condor/")[0]
Inputfiles_DIR = ANALYZER_DIR + "list/"

cmsswReleaseVersion = CMSSW_BASE_DIR.split("/")[-1]
print("Using CMSSW version " + cmsswReleaseVersion)
print("Running tuples version " + v.TUPLES_VERSION_NUMBER)


# Create script to send all of the jobs directly
send_all_jobs = open(CONDOR_BASE_DIR + "/condor_ctuple_job_sender_syst.sh", "w+")

total_job_number = 0


# Create directory for condor jobs
for dataset_name in list_datasets:

    match_pattern = [True for pattern in skip_pattern if pattern in dataset_name]

    if dataset_name in skip_dataset or True in match_pattern:
        continue

    print("\n----- %s -----" % dataset_name)

    isData, max_runs_per_job, era, type_info, _ = datasets_info[dataset_name]
    channel = dataset_name.split("_Summer")[0]

    is_signal = (isData != "T") and ("signal" in type_info.lower())

    if not is_signal:
        print("Skipping because systematics are only run over MC signal.")
        print("Type info:", type_info)
        continue

    user = os.getenv("LOGNAME")
    EOS_BASE_DIR = (
        "/store/group/lpchmumu/"
        + user
        + "/analyzer_HiggsMuMu_"
        + v.ANALYZER_VERSION_NUMBER
        + "/"
    )

    list_file = dataset_name + ".list"

    if not os.path.exists(Inputfiles_DIR + list_file):
        print("List file does not exist. Skipping!")
        continue

    for muon_pt_syst, jet_syst in get_syst_points():

        print("\n  Muon pT syst:", muon_pt_syst)
        print("  Jet syst:", jet_syst)

        if muon_pt_syst != "nominal":
            syst_dataset_name = dataset_name + "_" + muon_pt_syst
        else:
            syst_dataset_name = dataset_name + "_" + jet_syst

        # ---------------------------------------------------
        # Input files
        # ---------------------------------------------------
        # Muon pT systematics come from analyzer outputs already
        # produced in dataset_syst directories.
        #
        # Jet systematics are made inside CreateTuple using jet_syst,
        # so they use the nominal analyzer input files.
        # ---------------------------------------------------

        if muon_pt_syst != "nominal":
            WEIGHT_FILE = (
                EOS_BASE_DIR
                + type_info
                + "/%s/" % syst_dataset_name
                + "SumGenWeight.root"
            )

            INPUT_FILE = (
                EOS_BASE_DIR
                + type_info
                + "/%s/" % syst_dataset_name
                + "HiggsMuMu_"
                + v.ANALYZER_VERSION_NUMBER
                + "_$(I).root"
            )

        else:
            WEIGHT_FILE = (
                EOS_BASE_DIR
                + type_info
                + "/%s/" % dataset_name
                + "SumGenWeight.root"
            )

            INPUT_FILE = (
                EOS_BASE_DIR
                + type_info
                + "/%s/" % dataset_name
                + "HiggsMuMu_"
                + v.ANALYZER_VERSION_NUMBER
                + "_$(I).root"
            )

        if not os.path.exists("/eos/uscms/" + WEIGHT_FILE):
            print("Merged file does not exist. Skipping!")
            print("Missing:", "/eos/uscms/" + WEIGHT_FILE)
            continue

        OUTPUT_DIR = (
            EOS_BASE_DIR
            + "tuples_"
            + v.TUPLES_VERSION_NUMBER
            + "/%s/" % syst_dataset_name
        )

        JOB_DIR = (
            CONDOR_BASE_DIR
            + "ctuples_"
            + v.TUPLES_VERSION_NUMBER
            + "/%s/" % syst_dataset_name
        )

        os.system("xrdfs root://cmseos.fnal.gov mkdir -p " + OUTPUT_DIR)

        file_name = channel + "_" + era + "_$(I)" + "_tuples.root"
        file_copy_name = channel + "_" + era + "_$(I)" + "_tuples_v1.root"

        hadd_exists = os.path.exists("/eos/uscms/" + OUTPUT_DIR + file_name)
        hadd_copy_exists = os.path.exists("/eos/uscms/" + OUTPUT_DIR + file_copy_name)

        if hadd_exists:
            print("Tuples file already exists.")

            if recreate_hadded_file:
                if hadd_copy_exists:
                    print("A tuple safe copy already exists! Overwriting.")
                    comm = "xrdfs root://cmseos.fnal.gov rm /"
                    comm += OUTPUT_DIR + file_name
                    os.system(comm)

                print("Creating new tuple safe copy!")
                comm = "xrdfs root://cmseos.fnal.gov mv /" + OUTPUT_DIR + file_name
                comm += " /" + OUTPUT_DIR + file_copy_name
                os.system(comm)

            else:
                print("Skipping.")
                continue

        if os.path.exists(JOB_DIR):
            log_dir = JOB_DIR + "/log/"
            out_dir = JOB_DIR + "/out/"

            if os.path.exists(log_dir) and os.path.exists(out_dir):
                if len(os.listdir(log_dir)) != len(os.listdir(out_dir)):
                    print("Previous job didn't finish well. Try running manually.")

                    comm = "./CreateTuple /eos/uscms/" + INPUT_FILE + " "
                    comm += "/eos/uscms/" + WEIGHT_FILE + " "
                    comm += "/eos/uscms/" + OUTPUT_DIR + " " + era + " " + channel
                    comm += " T" if "Data" in type_info else " F"
                    comm += " T" if "signal" in type_info.lower() else " F"
                    comm += " " + include_Z + " " + include_H + " " + jet_syst

                    print(" > cd " + JOB_DIR + "; " + comm)

                    send_all_jobs.write("cd " + JOB_DIR + "\n")
                    send_all_jobs.write(comm + "\n")
                    continue

        print("Channel: " + channel)
        print("Type info: " + type_info)
        print("Systematic dataset name: " + syst_dataset_name)

        # Create condor directories
        os.system("mkdir -p " + JOB_DIR)
        os.system("mkdir -p " + JOB_DIR + "/log/")
        os.system("mkdir -p " + JOB_DIR + "/out/")
        os.system("mkdir -p " + JOB_DIR + "/err/")

        n_runs_in_job = 0
        n_jobs = 1

        with open(ANALYZER_DIR + "list/" + list_file, "r") as list_all_runs:
            for run in list_all_runs:
                # Close current list of runs and open the next one
                if n_runs_in_job >= max_runs_per_job:
                    n_runs_in_job = 0
                    n_jobs += 1

                # Save run path in list
                n_runs_in_job += 1

        total_job_number += n_jobs

        ###################################################
        # Copy run script, executable, and required files
        ###################################################
        os.system(
            "cp "
            + "%s/template_create_tuples_job_LPC.sh" % CONDOR_BASE_DIR
            + " "
            + "%s/run_job_LPC.sh" % JOB_DIR
        )

        os.system(
            "cp "
            + "%s/bin/CreateTuple" % ANALYZER_DIR
            + " "
            + JOB_DIR
        )

        #####################################
        # Create Condor JDL file
        #####################################
        jobfile_JDL = open(JOB_DIR + "/task.jdl", "w+")

        jobfile_JDL.write("Universe  = vanilla" + "\n")
        jobfile_JDL.write("Executable = ./run_job_LPC.sh" + "\n")

        args = (
            INPUT_FILE
            + " "
            + WEIGHT_FILE
            + " "
            + OUTPUT_DIR
            + " "
            + era
            + " "
            + channel
            + " "
            + type_info
            + " "
            + include_Z
            + " "
            + include_H
            + " "
            + jet_syst
            + " "
            + cmsswReleaseVersion
            + " "
            + "$(I)"
        )

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

        for i in range(1, n_jobs + 1):
            jobfile_JDL.write(str(i) + "\n")

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
