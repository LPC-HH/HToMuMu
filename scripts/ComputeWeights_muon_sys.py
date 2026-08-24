import os
import sys
import uproot
import numpy as np

sys.path.append('../condor/utils')
import version as v

sys.path.append('../list')
from listDatasets_Run3 import datasets_info

#EOS_PATH = f"/eos/uscms/store/group/lpchmumu/$USER/analyzer_HiggsMuMu_{v.ANALYZER_VERSION_NUMBER}/"

# Arguments
valid_muon_pt_systs = [
    "nominal",
    "scale_up",
    "scale_down",
    "smearing_up",
    "smearing_down",
]


systematics= [
    "scale_up",
    "scale_down",
    "smearing_up",
    "smearing_down",
]

if len(sys.argv) > 3:
    print("Usage: python3 scripts/ComputeWeights.py [T/F] [muon_pt_syst]")
    exit()

if len(sys.argv) >= 2:
    if sys.argv[1] not in ["T", "F"]:
        print("First argument is required! Add T or F if you want to recreate the SumGenWeight file")
        exit()
    recreate_weight_file = True if (sys.argv[1] == "T") else False
else:
    recreate_weight_file = False


muon_pt_syst_list = [sys.argv[2]] if len(sys.argv) == 3 else systematics

for muon_pt_syst in muon_pt_syst_list:


    if muon_pt_syst not in valid_muon_pt_systs:
        print("Unsupported muon pt systematic '{}'. Use one of: {}".format(
            muon_pt_syst, ", ".join(valid_muon_pt_systs)))
        exit()

    user = os.getenv('LOGNAME')
    EOS_PATH = "/eos/uscms/store/group/lpchmumu/" + user + "/analyzer_HiggsMuMu_" + v.ANALYZER_VERSION_NUMBER
    print("Muon pT systematic " + muon_pt_syst)

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
        "v13"
    ]

    list_datasets = datasets_info.keys()
# # Use in case you want to run over a specific list of datasets!
#list_datasets = [
#     "DY50to120_Summer24",
#     "DY120to200_Summer24",
         #"WWtoLNu2Q_Summer23BPix",
#]

    for dataset_name in list_datasets:
        match_pattern = [True for pattern in skip_pattern if pattern in dataset_name]
        if (dataset_name in skip_dataset) or (True in match_pattern):
            continue

        isData, _, _, type_info, _ = datasets_info[dataset_name]
        if muon_pt_syst != "nominal" and type_info != "MC_signal":
            print("Skipping non-signal sample for muon pT systematic.")
            continue


        FILESDIR = ""
        dataset_dir = dataset_name
        if muon_pt_syst != "nominal":
            dataset_dir += "_%s"%(muon_pt_syst)

        for dir_type in ["Data", "MC_background", "MC_signal"]:
            if os.path.exists(EOS_PATH + "/%s/%s"%(dir_type, dataset_dir)):
                print("Directory found!")
                FILESDIR = EOS_PATH + "/%s/%s"%(dir_type, dataset_dir)
                print(FILESDIR)
                break
        if not FILESDIR:
            print("No folder found for " + dataset_dir + " :(. Skipping.")
            continue

        analyzer_output_files = [file for file in os.listdir(FILESDIR) if "Higgs" in file]
        outputFile = FILESDIR + "/SumGenWeight.root"

        SumGenWeight_exists = os.path.exists(outputFile)
        if SumGenWeight_exists and not recreate_weight_file:
            print("SumGenWeight already exists!")
            continue

        with uproot.recreate(outputFile) as f:
            totalGenWeight = 0
            for analyzer_file in analyzer_output_files:
                with uproot.open(FILESDIR + "/" + analyzer_file + ":h_sumOfgenWeight") as h:
                    totalGenWeight += h.values()[0]
                    edges = h.axis().edges()

            print(f"Total generator weight for {dataset_dir}: {totalGenWeight}")
            f["h_sumOfgenWeight"] = np.histogram(np.array([0.5]), bins=[0,1], weights=[totalGenWeight])
            print(outputFile + " CREATED")
