import os
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_DIR / "condor"))
sys.path.append(str(REPO_DIR / "list"))
import utils.version as version
from listDatasets_Run3 import datasets_info

# Define the path to your C++ executable.
cpp_executable = str(REPO_DIR / "bin" / "CreateTuple")

base_input_directory = "/eos/uscms/store/user/lpchmumu/mbarrial/analyzer_HiggsMuMu_v1.6/"
output_directory = "/eos/uscms/store/user/lpchmumu/mbarrial/analyzer_HiggsMuMu_v1.6/tuples_v1.6.test/"
os.makedirs(output_directory, exist_ok=True)

# eras = ["2022", "2022EE"]
# eras = ["2022"]
# eras = ["2022EE"]
# eras = ["2023", "2023BPix"]
eras = ["2023BPix"]

include_Z = "F"
include_H = "T"
jet_syst = os.getenv("JET_SYST", "nominal")
jet_syst = "nominal"

# t_Jet_pt_CMS_scale_j_FlavorQCD_up
# t_Jet_pt_CMS_scale_j_FlavorQCD_up
analyzer_file_name = os.getenv(
    "ANALYZER_FILE_NAME", "HiggsMuMu_v1.6_1.root".format(version.ANALYZER_VERSION_NUMBER)
)
weight_file_name = os.getenv("WEIGHT_FILE_NAME", "SumGenWeight.root")


data_datasets = [
    ## 2022
    # "DoubleMuon_2022C",
    "Muon_2022C",
    # "Muon_2022D",
    ## 2023E
    # "Muon_2022E",
    # "Muon_2022F",
    # "Muon_2022G",
    ## 2023
    # "Muon0_2023B",
    # "Muon1_2023B",
    # ## 2023
    # "Muon0_2023C_v1",
    # "Muon0_2023C_v2",
    # "Muon0_2023C_v3",
    # "Muon0_2023C_v4",
    # "Muon1_2023C_v1",
    # "Muon1_2023C_v2",
    # "Muon1_2023C_v3",
    # "Muon1_2023C_v4",
    # ## 2023Bpix
    # "Muon0_2023D_v1",
    # "Muon0_2023D_v2",
    # "Muon1_2023D_v1",
    # "Muon1_2023D_v2",
]
background_datasets = [
    # "TTto2L2Nu",
    # "TTtoLNu2Q",
    "DY50to120",
    "DY120to200",
    # "WWto2L2Nu",
    # "WZto2L2Q",
    # "WZto3LNu",
    # "ZZto2L2Nu",
    # "ZZto2L2Q",
    # "ZZto4L",
    # "EWK_2L2J",
    # "WWW_4F",
    # "DYto2L-2Jets",
]
signal_datasets = [
    # "ggH",
    # "VBF",
    # "ttH",
]


def campaign_suffix(era):
    if era == "2022":
        return "_Summer22"
    if era == "2022EE":
        return "_Summer22EE"
    if era == "2023":
        return "_Summer23"
    if era == "2023BPix":
        return "_Summer23BPix"
    if era == "2024":
        return "_Summer24"
    raise ValueError("Unsupported era: {}".format(era))


def add_arguments(arguments, input_dir, era, channel, is_data, is_signal):
    input_file = os.path.join(input_dir, analyzer_file_name)
    weight_file = os.path.join(input_dir, weight_file_name)
    arguments.append(
        [
            input_file,
            weight_file,
            output_directory,
            era,
            channel,
            is_data,
            is_signal,
            include_Z,
            include_H,
            jet_syst,
        ]
    )


# List of input arguments:
# ./bin/CreateTuple input.root SumGenWeight.root output_dir era channel is_data is_signal include_Z include_H jet_syst
input_arguments = []

for dataset in data_datasets:
    input_dir = os.path.join(base_input_directory, "Data", dataset)
    era = datasets_info[dataset][2]
    add_arguments(input_arguments, input_dir, era, dataset, "T", "F")

for era in eras:
    dataset_extra = campaign_suffix(era)

    for dataset in signal_datasets:
        dataset_name = dataset + dataset_extra
        input_dir = os.path.join(base_input_directory, "MC_signal", dataset_name)
        add_arguments(input_arguments, input_dir, era, dataset, "F", "T")

    for dataset in background_datasets:
        dataset_name = dataset + dataset_extra
        input_dir = os.path.join(base_input_directory, "MC_background", dataset_name)
        add_arguments(input_arguments, input_dir, era, dataset, "F", "F")

print(input_arguments)

# Loop over each set of input arguments and execute the C++ program.
for args in input_arguments:
    result = subprocess.run([cpp_executable] + args, capture_output=True, text=True)

    print("Output:", result.stdout)
    print("Errors:", result.stderr)
