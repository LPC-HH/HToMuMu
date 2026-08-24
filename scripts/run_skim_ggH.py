import subprocess
import os


# Define the path to your C++ executable
cpp_executable = "./bin/SkimTuplesggH"

# base_input_directory = "/eos/uscms/store/user/csanmart/analyzer_HiggsMuMu/"
base_input_directory = "./root_io/tuples/"
output_directory = "./root_io/skim/"
os.makedirs(output_directory + "ggH/", exist_ok=True)

# eras = ["2022", "2022EE"]
#eras = ["2024"]
eras = ["2022EE", "2022", "2023", "2023BPix", "2024"]
eras = ["Combined"]


# data_datasets = ["DoubleMuon_2022C", "Muon_2022C", "Muon_2022D", "Muon_2022E", "Muon_2022F", "Muon_2022G"]
# data_datasets = ["DoubleMuon_2022C"]
# data_datasets = ["Muon_2022C"]
# data_datasets = ["Muon_2022D"]
background_datasets = [
    # "TTto2L2Nu",
    # "TTtoLNu2Q",
    # "DY50to120",
    # "DY120to200",
    # "WWto2L2Nu",
    # "WZto2L2Q",
    # "WZto3LNu",
    # "ZZto2L2Nu",
    # "ZZto2L2Q",
    # "ZZto4L",
    # "EWK_2L2J",
    "DY",
    "TT",
    "DiBoson",
    "EWK",
    #"WWW_4F",
]
signal_datasets = [
     "ggH",
     "VBF",
     "ttH",
]

# List of input arguments
input_arguments = []

for era in eras:
    input = base_input_directory + "Data_" + era + "_tuples.root"
    input_arguments.append([input, output_directory, era, "Data", "T"])
    for dataset in signal_datasets:
        input = base_input_directory + dataset + "_" + era + "_tuples.root"
        input_arguments.append([input, output_directory, era, dataset, "F"])
    for dataset in background_datasets:
        input = base_input_directory + dataset + "_" + era + "_tuples.root"
        input_arguments.append([input, output_directory, era, dataset, "F"])

#input_arguments.append([base_input_directory + "Data_2025_tuples.root", output_directory, "2025", "Data", "T"])
print(input_arguments)

# Loop over each set of input arguments and execute the C++ program
for args in input_arguments:
    # Run the C++ executable with the current arguments
    result = subprocess.run([cpp_executable] + args, capture_output=True, text=True)

    # Print the output and any error messages
    print("Output:", result.stdout)
    print("Errors:", result.stderr)
