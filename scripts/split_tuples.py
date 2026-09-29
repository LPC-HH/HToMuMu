import argparse
import os
from sys import path as sys_path
import uproot

# Read the (tens of GB) BDT_score files in chunks rather than memory-mapping them whole:
# the whole-file map alone exceeds the 16 GiB per-process limit on the LPC login nodes.
UPROOT_OPEN = dict(file_handler=uproot.MultithreadedFileSource)
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


def get_input_file_name(data_type, channel, path):
    return os.path.join(
        path,
        {
            "data": "data_Combined.root",
            "signal": f"{channel}_Combined_BFull_SNottH.root",
        }[data_type],
    )


def get_tree_name(data_type, channel, category_name):
    return {
        "data": f"Data_13TeV_{category_name}",
        "signal": f"{channel.lower()}_125_13TeV_{category_name}",
    }[data_type]


def split_tuples_by_category(
    data_type,
    channel,
    output_file_name,
    branching_ratio,
    bdt_cuts,
    use_bsConstrain,
):

    samples = [channel]
    if data_type != "data":
        samples = ["ggHreCat", "VBFreCat"] if RECATEGORIZE else ["ggH","VBF"]
    with uproot.recreate(output_file_name) as file_output:

        for sample in samples:

            input_path = f"./root_io/tuples/BDT_score/{sample}/BFull_SNottH/"
            input_file_name = get_input_file_name(data_type, channel[:3] if RECATEGORIZE else channel, input_path)

            branches = {}
            BDT_branch = f"BDT_{sample[:3]}" if RECATEGORIZE else f"BDT_{sample}"
            CAT_branch = f"is_{sample[:3]}_categoryBDT" if RECATEGORIZE else f"is_{sample}_category"
            selected_branches = [
                "pileup_weight",
                "diMuon_mass",
                "diMuon_bsConstrainedMass",
                BDT_branch,
                CAT_branch,
                "weight_no_lumi",
                "weight",
                "leading_jet_eta",
                "subleading_jet_eta",
            ]

            # print(f"[Info] Processing sample: {channel}")
            print(f"[Info] Opening input file: {input_file_name}")
            print(f"[Info] Using BDT branch: {BDT_branch}")
            print(f"[Info] Using CAT branch: {CAT_branch}")
            # print(f"[Info] Opening input file: {input_file_name}")

            reweight = 1

            # if(data_type=="signal"):
            #     print("Reweighting signal MC")
            #     reweight = 281.7/170.97

            branches = uproot.open(input_file_name, **UPROOT_OPEN)["tree_output"].arrays(
                selected_branches, library="np"
            )
            # Changing the weight from xs*gen_weight*pu*br*1000/SumGenweight to xs*gen_weight*1000/SumGenweight
            nominal_mass = branches["diMuon_mass"]
            bs_mass = branches["diMuon_bsConstrainedMass"]

            print(
                "[Mass migration] nominal <= 110, BS > 110:",
                np.count_nonzero((nominal_mass <= 110) & (bs_mass > 110)),
            )

            print(
                "[Mass migration] nominal > 110, BS <= 110:",
                np.count_nonzero((nominal_mass > 110) & (bs_mass <= 110)),
            )

            print(
                "[Input nominal below 110]:",
                np.count_nonzero(nominal_mass < 110),
            )

            print(
                "[Input BS below 110]:",
                np.count_nonzero(bs_mass < 110),
            )

            if data_type != "data":
                branches["weight"] = branches["weight"] / (branching_ratio) * reweight

            # Renameing the mass variable to use the hgg fits code
            if use_bsConstrain:
                branches["CMS_hgg_mass"] = branches["diMuon_bsConstrainedMass"]
            else:
                # print("we here right")
                branches["CMS_hgg_mass"] = branches["diMuon_mass"]
            for category in range(len(bdt_cuts[sample]) - 1):

                cuts = []
                selected_events = {}
                print(f"[Info] Inital events: {len(branches['diMuon_mass'])}")
                print(category)

                mass_nominal = branches["diMuon_mass"]
                mass_bs = branches["diMuon_bsConstrainedMass"]
                score = branches[BDT_branch]
                is_category = branches[CAT_branch] == 1

                lower_bdt = bdt_cuts[sample][category]
                upper_bdt = bdt_cuts[sample][category + 1]

                bdt_selection = (score >= lower_bdt) & (score < upper_bdt) & is_category

                category_name = f"{sample[0:3]}cat{len(bdt_cuts[sample]) - category - 1}"

                print(f"\n[CHECK] {category_name}")
                print(f"BDT range: {lower_bdt} to {upper_bdt}")

                print(
                    "Nominal <= 110, BS in first bin:",
                    np.count_nonzero(
                        bdt_selection
                        & (mass_nominal <= 110)
                        & (mass_bs > 110)
                        & (mass_bs < 110.25)
                    ),
                )

                print(
                    "Nominal > 110, BS <= 110:",
                    np.count_nonzero(
                        bdt_selection & (mass_nominal > 110) & (mass_bs <= 110)
                    ),
                )

                print(
                    "BS first bin 110-110.25:",
                    np.count_nonzero(
                        bdt_selection & (mass_bs > 110) & (mass_bs < 110.25)
                    ),
                )

                print(
                    "BS second bin 110.25-110.50:",
                    np.count_nonzero(
                        bdt_selection & (mass_bs >= 110.25) & (mass_bs < 110.50)
                    ),
                )

                print(
                    "Exactly BS mass = 110:",
                    np.count_nonzero(bdt_selection & (mass_bs == 110)),
                )



                cuts = (
                    (branches[BDT_branch] > bdt_cuts[sample][category])
                    & (branches[BDT_branch] < bdt_cuts[sample][category + 1])
                    & (branches[CAT_branch] == 1)
                    & (branches["CMS_hgg_mass"] <= 150)
                    & (branches["CMS_hgg_mass"] >= 110)
                )

                selected_events = {
                    name: array[cuts] for name, array in branches.items()
                }

                print(f"[Info] Final events: {len(branches['diMuon_mass'][cuts])}")
                print(f"[Info] Final selected events: {len(selected_events['diMuon_mass'])}")


                category_name = (
                    sample + "cat" + str(len(bdt_cuts[sample]) - category - 1)
                )
                if RECATEGORIZE:
                    category_name = f"{sample[:3]}cat{len(bdt_cuts[sample]) - category - 1}"
                else:
                    category_name = f"{sample}cat{len(bdt_cuts[sample]) - category - 1}"
                tree_name = get_tree_name(data_type, channel[:3] if RECATEGORIZE else channel, category_name)

                file_output[tree_name] = selected_events

    print(f"[Done] Created: {output_file_name}")


RECATEGORIZE = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split BDT-scored tuples into per-category trees."
    )
    parser.add_argument("data_type", choices=["data", "signal"])
    parser.add_argument("channel", choices=["ggH", "VBF"])
    parser.add_argument(
        "-r",
        "--recategorize",
        action="store_true",
        help="use the re-categorization BDT branches/cuts",
    )
    args = parser.parse_args()

    RECATEGORIZE = args.recategorize
    data_type = args.data_type
    channel = args.channel
    branching_ratio = 2.176e-4
    use_bsConstrain = True

    if RECATEGORIZE:
        channel = channel + "reCat"
    out_path = f"./root_io/tuples/split_tuples/{channel}"
    input_path = f"./root_io/tuples/BDT_score/{channel}/BFull_SNottH/"
    output_file_name = get_output_file_name(data_type, out_path)

    print(f"[Config] Using data_type = {data_type}")
    print(f"[Config] Using channel   = {channel}")
    print(f"[Config] Output file= {output_file_name}")
    print(f"[Config] Branching Ratio = {branching_ratio}")
    print(f"[Config] Use bsConstrain = {use_bsConstrain}")
    print(f'[Config] Using BDT reCat = {RECATEGORIZE}')

    os.makedirs(out_path, exist_ok=True)

    mass_variable = "diMuon_bsConstrainedMass" if use_bsConstrain else "diMuon_mass"
    bdt_categories_info = load_bdt_categories()
    ch_list = ["ggHreCat", "VBFreCat"] if RECATEGORIZE else ["ggH", "VBF"]
    bdt_cuts = {
        ch: get_bdt_cuts(bdt_categories_info, ch, "Combined", "BFull_SNottH", mass_variable)
        for ch in ch_list
    }

    split_tuples_by_category(
        data_type, channel, output_file_name, branching_ratio, bdt_cuts, use_bsConstrain
    )
