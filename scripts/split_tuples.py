import os
from sys import argv, path as sys_path
import uproot
import numpy as np
from pathlib import Path

sys_path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))
from bdt_categories_io import load_bdt_categories, get_bdt_cuts

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
                & (branches["CMS_hgg_mass"] < 150)
                & (branches["CMS_hgg_mass"] > 109.999)
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

    mass_variable = "diMuon_bsConstrainedMass" if use_bsConstrain else "diMuon_mass"
    bdt_categories_info = load_bdt_categories()
    bdt_cuts = {
        ch: get_bdt_cuts(bdt_categories_info, ch, "Combined", "BFull_SNottH", mass_variable)
        for ch in ["ggH", "VBF"]
    }

    input_file_name = get_input_file_name(data_type, input_path)
    output_file_name = get_output_file_name(data_type, out_path)
    split_tuples_by_category(
        data_type, channel, output_file_name, input_file_name, branching_ratio, 
        bdt_cuts, use_bsConstrain
    )
