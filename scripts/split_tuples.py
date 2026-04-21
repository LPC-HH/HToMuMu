import os
from sys import argv
import uproot
import numpy as np

def get_output_file_name(data_type, path):
    return os.path.join(
        path,
        {
            "data": "allData_combined.root",
            "signal": "output_signal_M125_13TeV_cats_pythia8.root",
        }[data_type],
    )


def get_input_file_name(data_type, path):
    return os.path.join(
        path,
        {"data": "data_Combined.root", "signal": "signal_Combined.root"}[data_type],
    )


def get_tree_name(data_type, channel, category_name):
    return {
        "data": f"Data_13TeV_{category_name}",
        "signal": f"{channel.lower()}_125_13TeV_{category_name}",
    }[data_type]


def split_tuples_by_category(
    data_type, channel, output_file_name, input_file_name, branching_ratio, bdt_cuts, use_bsConstrain,
):

    with uproot.recreate(output_file_name) as file_output:
        branches = {}
        selected_branches = [
            "pileup_weight",
            "diMuon_mass",
            "diMuon_bsConstrainedMass",
            f"BDT_{channel}",
            f"is_{channel}_category",
            "weight_no_lumi",
            "weight",
            "leading_jet_eta",
            "subleading_jet_eta"
        ]
        print(f"[Info] Opening input file: {input_file_name}")

        reweight = 1

        #if(data_type=="signal"):
        #    print("Reweighting signal MC")
        #    reweight = 281.7/170.97

        branches = uproot.open(input_file_name)["tree_output"].arrays(
            selected_branches, library="np"
        )
        # Changing the weight from gen_weight*pu*br*1000/SumGenweight to gen_weight/SumGenweight
        branches["weight"] = branches["weight"] / (
            branching_ratio * branches["pileup_weight"]
        ) * reweight
        
        # Renameing the mass variable to use the hgg fits code
        if use_bsConstrain:
            branches["CMS_hgg_mass"] = branches["diMuon_bsConstrainedMass"]
        else:
            #print("we here right")
            branches["CMS_hgg_mass"] = branches["diMuon_mass"]
        for category in range(len(bdt_cuts[channel]) - 1):

            cuts = []
            selected_events = {}
            print(f"[Info] Inital events: {len(branches['diMuon_mass'])}")
            print(category)

            eta_horn_cuts = (
                (abs(branches["leading_jet_eta"]) > 2.5)
                & (abs(branches["leading_jet_eta"]) < 3)
                & (abs(branches["subleading_jet_eta"]) > 2.5)
                & (abs(branches["subleading_jet_eta"]) < 3)
            )

            print(f"[Info] Initial events in horn: {len(branches['diMuon_mass'][eta_horn_cuts])}")

            cuts = (
                (branches["BDT_" + channel] > bdt_cuts[channel][category])
                & (branches["BDT_" + channel] < bdt_cuts[channel][category + 1])
                & (branches["is_" + channel + "_category"] == 1)
                & (branches["CMS_hgg_mass"] < 180)
                & (branches["CMS_hgg_mass"] > 100)
            )

            selected_events = {name: array[cuts] for name, array in branches.items()}

            eta_horn_selected = (
                (abs(selected_events["leading_jet_eta"]) > 2.5)
                & (abs(selected_events["leading_jet_eta"]) < 3)
                & (abs(selected_events["subleading_jet_eta"]) > 2.5)
                & (abs(selected_events["subleading_jet_eta"]) < 3)
            )

            #print(f"[Info] Final events: {len(branches['diMuon_mass'][cuts])}")
            #print(f"[Info] Final selected events: {len(selected_events['diMuon_mass'])}")

            #print(f"[Info] Final selected events in horn: {len(selected_events['diMuon_mass'][eta_horn_selected])}")

            category_name = channel + "cat" + str(len(bdt_cuts[channel]) - category - 1)

            category_name = f"{channel}cat{len(bdt_cuts[channel]) - category - 1}"
            tree_name = get_tree_name(data_type, channel, category_name)

            file_output[tree_name] = selected_events

    print(f"[Done] Created: {output_file_name}")


if __name__ == "__main__":
    if len(argv) != 3:
        print("[Error] python script.py <data_type: data|signal> <channel: ggH|VBF>")

    data_type = argv[1]
    channel = argv[2]
    branching_ratio = 2.176e-4
    use_bsConstrain = True 

    if data_type not in ["data", "signal"]:
        print("[Error]: use data or signal for data_type")
        exit()
    if channel not in ["ggH", "VBF"]:
        print("[Error]: use ggH or VBF for production channel")
        exit()

    print(f"[Config] Using data_type = {data_type}")
    print(f"[Config] Using channel   = {channel}")
    print(f"[Config] Branching Ratio = {branching_ratio}")
    print(f"[Config] Use bsConstrain = {use_bsConstrain}")

    out_path = f"./root_io/tuples/split_tuples/{channel}"
    input_path = f"./root_io/tuples/BDT_score/{channel}/BFull_SNottH/"
    os.makedirs(out_path, exist_ok=True)
    if use_bsConstrain:
        #bdt_cuts = {
        #    "ggH": [0.0, 0.20969230769230757, 0.44615384615384546, 1.0],
        #    "VBF": [0.0, 0.44603999999999994, 0.7559999999999996, 0.9450000000000007, 1.0], 
        #}
        bdt_cuts = {"ggH" : [0.0, 0.4400000000000002, 0.6100000000000003, 0.8100000000000005, 0.9200000000000006, 1.0], 
                    "VBF": [0.0, 0.646666666666667, 0.8800000000000018, 0.9466666666666689, 0.9733333333333357, 1.0]
                    }
    else:
        #bdt_cuts = {
            #"ggH": [0.0, 0.18615384615384592, 0.42307692307692246, 1.0],
#            "ggH": [0.0, 0.19184615384615372, 0.44615384615384546, 1.0],
       #     "VBF": [0.0, 0.3448846153846141, 0.7038461538461517, 0.938461538461536, 1.0],
            #"VBF" :[0.0, 0.3614625000000003, 0.7087499999999998, 0.9450000000000007, 1.0],

       # }
        bdt_cuts = {"ggH" : [0.0, 0.19730769230769193, 0.4384615384615378, 1.0], "VBF": [0.0, 0.19152000000000016, 0.5472000000000005, 0.8550000000000006, 1.0]}

    input_file_name = get_input_file_name(data_type, input_path)
    output_file_name = get_output_file_name(data_type, out_path)
    split_tuples_by_category(
        data_type, channel, output_file_name, input_file_name, branching_ratio, 
        bdt_cuts, use_bsConstrain
    )
