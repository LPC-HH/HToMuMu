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
if (len(sys.argv) == 1):
    recreate_weight_file = False
elif (len(sys.argv) == 2) and (sys.argv[1] not in ["T", "F"]):
    print("First argument is required! Add T or F if you want to recreate the SumGenWeight file")
    exit()
else:
    recreate_weight_file = True if (sys.argv[1] == "T") else False

user = os.getenv('LOGNAME')
EOS_PATH = "/eos/uscms/store/group/lpchmumu/" + user + "/analyzer_HiggsMuMu_" + v.ANALYZER_VERSION_NUMBER

# Skip these datasets
skip_dataset = [
    "DoubleMuon_2022A",
    "DoubleMuon_2022B",
    "DoubleMuon_2022C",
    "Muon0_2023B",
    "Muon1_2023B",
    #"TTtoLNu2Q_Summer24",
    #"WZto2L2Q_Summer24",
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

    print("\n----- %s -----"%(dataset_name))

    FILESDIR = ""
    for dir_type in ["Data", "MC_background", "MC_signal"]:
        if os.path.exists(EOS_PATH + "/%s/%s"%(dir_type, dataset_name)):
            print("Directory found!")
            FILESDIR = EOS_PATH + "/%s/%s"%(dir_type, dataset_name)
            print(FILESDIR)
            break
    if not FILESDIR:
        print("No folder found for " + dataset_name + " :(. Skipping.")
        continue
    
    analyzer_output_files = [file for file in os.listdir(FILESDIR) if "Higgs" in file]
    outputFile = FILESDIR + "/SumGenWeight.root"

    SumGenWeight_exists = os.path.exists(FILESDIR + "/SumGenWeight.root")
    if SumGenWeight_exists and not recreate_weight_file:
        print("SumGenWeight already exists!")
        continue
    
    with uproot.recreate(FILESDIR + "/SumGenWeight.root") as f:

        totalGenWeight = 0.0

        totalLHEPdfWeight = None
        totalLHEScaleWeight = None

        pdf_edges = None
        scale_edges = None

        for analyzer_file in analyzer_output_files:

            file_path = FILESDIR + "/" + analyzer_file

            with uproot.open(file_path) as input_file:

                h_gen = input_file["h_sumOfgenWeight"]
                totalGenWeight += h_gen.values()[0]

                h_pdf = input_file["h_sumOfLHEPdfWeight"]
                pdf_values = h_pdf.values()

                if totalLHEPdfWeight is None:
                    totalLHEPdfWeight = np.zeros_like(
                        pdf_values,
                        dtype=np.float64
                    )
                    pdf_edges = h_pdf.axis().edges()

                totalLHEPdfWeight += pdf_values

                h_scale = input_file["h_sumOfLHEScaleWeight"]

                scale_values = h_scale.values()

                if totalLHEScaleWeight is None:
                    totalLHEScaleWeight = np.zeros_like(
                        scale_values,
                        dtype=np.float64
                    )
                    scale_edges = h_scale.axis().edges()

                totalLHEScaleWeight += scale_values


        print(
            f"Total generator weight for {dataset_name}: {totalGenWeight}"
        )

        print(
            f"Number of PDF weights: {len(totalLHEPdfWeight)}"
        )

        print(
            f"Number of scale weights: {len(totalLHEScaleWeight)}"
        )


        f["h_sumOfgenWeight"] = np.histogram(
            np.array([0.5]),
            bins=[0, 1],
            weights=[totalGenWeight]
        )

        f["h_sumOfLHEPdfWeight"] = (
            totalLHEPdfWeight,
            pdf_edges
        )

        f["h_sumOfLHEScaleWeight"] = (
            totalLHEScaleWeight,
            scale_edges
        )


        print(FILESDIR + "/SumGenWeight.root CREATED")
