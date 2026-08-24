import subprocess
import os

# Define the path to your C++ executable
cpp_executable = "./bin/SkimTuples_VBF"
#input_directory = "/eos/uscms/store/user/csanmart/analyzer_HiggsMuMu/tuples/"
input_directory = "./root_io/tuples/"
output_directory = "./root_io/skim/"
os.makedirs(output_directory + "VBF/", exist_ok=True)

eras = [
    "2022",
    "2022EE",
    "2023",
    "2023BPix",
    "2024"
]

eras = [
    "Combined"
]

background_datasets= [
    #"DY50to120",
    # "DY120to200",
    # "EWK_2L2J",
    # "TTto2L2Nu",
    # "TTtoLNu2Q",
    # "TWminusto2L2Nu",
    # # "TWminusto4Q",
    # # "TWminustoLNu2Q",
    # # "TbarWplusto2L2Nu",
    # # "TbarWplusto4Q",
    # # "TbarWplustoLNu2Q",
    # # "TbarQto2Q-t-channel",
    # # "TbarQtoLNu-t-channel",
    # # "TQbarto2Q-t-channel",
    # # "TQbartoLNu-t-channel",
    # # "TBbartoLplusNuBbar-s-channel",
    # # "TbarBtoLminusNuB-s-channel",
    # "WZto2L2Q",
    # "WZto3LNu",
    # "WZtoLNu2Q",
    # "ZZto2L2Nu",
    # "ZZto2L2Q",
    # # "ZZto2Nu2Q",
    # "ZZto4L",
    # "WWto2L2Nu",
    # # "WWto4Q",
    # "WWtoLNu2Q",
    # "WWW_4F",

    # "TWminusto2L2Nu",
    # "TWminustoLNu2Q",
    # "TbarWplusto2L2Nu",
    # "TbarQtoLNu-t-channel",
    # "TQbartoLNu-t-channel",
    # "TBbartoLplusNuBbar-s-channel",
    # "TbarBtoLminusNuB-s-channel",
    # "ZZZ",
    # "WZZ",
    # "WWZ_4F",
    # "WWW_4F",
    "DY",
    "TT",
    "DiBoson",
    "EWK",
]

signal_datasets= [
    "ggH",
    "VBF",
    #"ttH",
    # "WplusH",
    # "WminusH",
    # "ZH",
]

# List of input arguments
input_arguments = []
# TODO: Include datasets of data per era (they have different name)
# # Save data input
# input_arguments.append([input_directory, "Data", era])

for era in eras:
    input = input_directory + "Data_" + era + "_tuples.root"
    input_arguments.append([input, output_directory, era, "Data", "T"])
    for dataset in signal_datasets:
        input = input_directory + dataset + "_" + era + "_tuples.root"
        input_arguments.append([input, output_directory, era, dataset, "F"])
    for dataset in background_datasets:
        input = input_directory + dataset + "_" + era + "_tuples.root"
        input_arguments.append([input, output_directory, era, dataset, "F"])

input_arguments.append([input_directory + "Data_2025_tuples.root", output_directory, "2025", "Data", "T"])
print(input_arguments)

# Loop over each set of input arguments and execute the C++ program
for args in input_arguments:
    print("\n----- %s_%s -----"%(args[1], args[2]))

    # Run the C++ executable with the current arguments
    result = subprocess.run([cpp_executable] + args, capture_output=True, text=True)

    # Print the output and any error messages
    print("Output:", result.stdout)
    print("Errors:", result.stderr)
