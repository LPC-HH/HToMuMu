import uproot as ur
import mplhep as hep
import numpy as np
import math
import matplotlib.pyplot as plt
import sys

from utils.labels import luminosity, x_range, n_bins, x_labels
from utils.helper import get_canvas, save_figure, get_histograms_ratio

if len(sys.argv) < 3:
    print(
        "Arguments missing: Channel_under_study, era, background_subset, signal_subset"
    )
    exit()
channel_US = sys.argv[1]
era_input = sys.argv[2]

if "--only" in sys.argv:
    sys.argv.remove("--only")
    eras = [era_input]
elif era_input == "2022":
    eras = ["2022", "2022EE", "2022Combined"]
elif era_input == "2023":
    eras = ["2023", "2023BPix", "2023Combined"]
elif era_input == "2024":
    eras = ["2024"]
elif era_input == "Combined":
    eras = ["Combined"]
elif era_input == "All":
    eras = ["2022", "2022EE", "2023", "2023BPix", "2024", "Combined"]
else:
    print("Set era to be one of the available sets:")
    print(" > 2022, 2023, 2024, Combined, All")
    exit()

if len(sys.argv) == 3:
    background_subset = "Full"
    signal_subset = "NottH"
    print("Using default subsets:", background_subset, signal_subset)
elif len(sys.argv) == 5:
    background_subset = sys.argv[3]
    signal_subset = sys.argv[4]
else:
    print("Include subset of background AND signal only.")
    exit()

print("Channel under study: ", channel_US)
print("Eras: ", eras)
print("Background subset: ", background_subset)
print("Signal subset: ", signal_subset)

subset_title = "B" + background_subset + "_S" + signal_subset
BDT_var = "BDT_" + channel_US
BDT_score_path = "../root_io/tuples/BDT_score/" + channel_US + "/" + subset_title + "/"
#N_max_iterations = 4 if channel_US == "ggH" else 4
#N_max_iterations = 2 if channel_US == "ggH" else 2
use_bsConstrain = True
#signal_region = (122.5 , 127.5)
signal_region = (121 , 129)
draw_data = False

if use_bsConstrain:
    diMuon_mass_name = "diMuon_bsConstrainedMass"
else:
    diMuon_mass_name = "diMuon_mass"
print("diMuon mass variable name: ", diMuon_mass_name)

#def create_bool_list(bkg_branches, signal_branches, bdt_min, bdt_max)

def get_expected_significance(bkg_branches, signal_branches, bdt_categories):
    #print(f'BDT Categories: {bdt_categories}')

    Z_by_cat = []
    for i in range(0, len(bdt_categories) + 1):
        #print(f'Cat: {i + 1} of {len(bdt_categories) + 1}')
        bdt_cut_min = 0
        bdt_cut_max = 1
        if(i != 0):
            bdt_cut_min = bdt_categories[i-1]
        if(i != len(bdt_categories)):
            bdt_cut_max = bdt_categories[i]
        
        bkg_bool_list = (
            (bkg_branches[diMuon_mass_name] > signal_region[0])
            & (bkg_branches[diMuon_mass_name] < signal_region[1])
            & (bkg_branches[BDT_var] > bdt_cut_min)
            & (bkg_branches[BDT_var] < bdt_cut_max)
            & (bkg_branches["is_" + channel_US + "_category"] == 1)
        )
        signal_bool_list = (
            (signal_branches[diMuon_mass_name] > signal_region[0])
            & (signal_branches[diMuon_mass_name] < signal_region[1])
            & (signal_branches[BDT_var] > bdt_cut_min)
            & (signal_branches[BDT_var] < bdt_cut_max)
            & (signal_branches["is_" + channel_US + "_category"] == 1)
        )
        signal_events = np.sum(
            signal_branches["weight"][signal_bool_list]
        )
        bkg_events = np.sum(
            bkg_branches["weight"][bkg_bool_list]
        )

        #print(f'Signal in cat {i+1} of {len(bdt_categories) + 1}: {signal_events}')
        #print(f'Background in cat {i+1} of {len(bdt_categories) + 1}: {bkg_events}')
        if(bkg_events <= 0):
            Z = 0
        else:
            Z = signal_events / math.sqrt(bkg_events)
        #print(f'Significance in cat {i+1} of {len(bdt_categories) + 1}: {Z}')
        Z_by_cat.append(Z)

    Z_tot = math.sqrt(sum(x**2 for x in Z_by_cat))

    return Z_by_cat, Z_tot

def find_bdt_categories(era, bdt_categories, bdt_cut_max=1, iteration=0):
    print(f'BDT Categories interation {iteration}: {bdt_categories}')
    #print("Iteration:", iteration)
    plt.style.use(hep.style.CMS)
    with ur.open(
        BDT_score_path + "background_" + era + ".root:tree_output"
    ) as file:
        bkg_branches = file.arrays(
            [BDT_var, "weight", diMuon_mass_name, "is_" + channel_US + "_category"], library="np"
        )
    with ur.open(
        BDT_score_path + "signal_" + era + ".root:tree_output"
    ) as file:
        signal_branches = file.arrays(
            [BDT_var, "weight", diMuon_mass_name, "is_" + channel_US + "_category"], library="np"
        )

    Z_by_cat, Z_tot = get_expected_significance(bkg_branches, signal_branches, bdt_categories)

    print(f'Total expected significance: {Z_tot}')
    print(f'Expected significance by cat: {Z_by_cat}')

    '''max_Z = max(Z_by_cat)
    best_cat = Z_by_cat.index(max_Z)
    print(f'Best category is cat {best_cat + 1} with Z: {max_Z}')
    print(f'------------ Splitting category {best_cat + 1} ------------')
    if(len(bdt_categories) == 0):
        print("There are currently no BDT categories")
        bdt_cut_min = 0
        bdt_cut_max = 1
    else:
        if(best_cat == 0):
            print("best cat is lowest cat")
            bdt_cut_min = 0
            bdt_cut_max = bdt_categories[best_cat]
        elif(best_cat == (len(bdt_categories))):
            print("best cat is highest cat")
            bdt_cut_min = bdt_categories[best_cat - 1]
            bdt_cut_max = 1
        else:
            print("best cat is middle cat")
            bdt_cut_min = bdt_categories[best_cat - 1]
            bdt_cut_max = bdt_categories[best_cat]
    
    print(f'Making a new category between {bdt_cut_min} and {bdt_cut_max}')'''
    bdt_cut_min = 0
    bdt_cut_max = 1
    current_bdt_cut = bdt_cut_min
    N_max_iterations = 4 if channel_US == "ggH" else 4
    cut_step = 1/100 if channel_US == "ggH" else 1/150
    
    #if(bdt_cut_min == 0):
    #    optimal_bdt_cut = cut_step
    #else:
    #   optimal_bdt_cut = bdt_cut_min

    optimal_bdt_cut = bdt_cut_min    
    optimal_Z_tot = Z_tot
    bdt_bins = []
    Z_at_bin = []

    #while current_bdt_cut < bdt_cut_max:
    while current_bdt_cut < bdt_cut_max:
        #print("----------------------------------------------------------------")
        #print("min cut:", current_bdt_cut)
        #print("max cut:", bdt_cut_max)
        #print("----------------------------------------------------------------")
        bdt_categories_test = bdt_categories.copy()
        bdt_categories_test.append(current_bdt_cut)
        bdt_categories_test.sort()
        Z_by_cat_test, Z_tot_test = get_expected_significance(bkg_branches, signal_branches, bdt_categories_test)
        #if(Z_tot_test > optimal_Z_tot):
        #    optimal_Z_tot = Z_tot_test
        #    optimal_bdt_cut = current_bdt_cut

        bdt_bins.append(current_bdt_cut)
        Z_at_bin.append(Z_tot_test)
        current_bdt_cut += cut_step

    optimal_Z_tot = max(Z_at_bin)
    optimal_bdt_cut = bdt_bins[Z_at_bin.index(optimal_Z_tot)]

    relative_increase = (optimal_Z_tot - Z_tot)/Z_tot
    print(f"Adding catergory {iteration} is {relative_increase*100}% better")
    if(relative_increase < 0.01):
        print(f"Category {iteration} only {relative_increase*100}% better")
        print(f'Final BDT Categories: {bdt_categories}')
        return

    #bdt_categories.insert(best_cat, optimal_bdt_cut)
    bdt_categories.append(optimal_bdt_cut)
    bdt_categories.sort()
    print(f'New BDT Categories: {bdt_categories}')
    print(f'New cut at {optimal_bdt_cut} with Z: {optimal_Z_tot} > {Z_tot}')

    
    fig, ax = get_canvas()

    ax.errorbar(
        bdt_bins,
        Z_at_bin,
        #ey,
        marker="o",
        linestyle="",
        markerfacecolor="black",
        color="black",
        markersize=5,
        # label=labelList[j],
    )

    # hep.cms.label(
    # data="True", label="", year=era, com="13.6", lumi=luminosity[era], ax=ax
    # )
    hep.cms.label(data="True", ax=ax, com="13.6")

    print(f"MAX significance: {optimal_Z_tot} at BDT score: {optimal_bdt_cut}")

    for i in range(len(bdt_categories)):
        if(bdt_categories[i] == optimal_bdt_cut):
            color_string="red"
        else:
            color_string="grey"
        ax.axvline(
            x=bdt_categories[i],
            # ymin=0.001,
            color=color_string,
            linestyle="--",
            alpha=0.5,
        )

    ax.set_ylim(0.975 * min(Z_at_bin), 1.025 * optimal_Z_tot)
    ax.set_xlim(bdt_bins[0], bdt_bins[-1])
    ax.set_ylabel(r"S/$\sqrt{B}$", loc="center")
    ax.set_xlabel("BTD Cut")

    output_directory = "../plots/" + channel_US + "_category/BDT_categories/cuts/"
    save_name = "BDT_cuts_" + era + "_Cat" + str(iteration) + "_" + subset_title
    save_figure(fig, output_directory, save_name)


    

    find_bdt_categories(era, bdt_categories, iteration=iteration+1)

'''
def find_bdt_categories(era, bdt_categories, bdt_cut_max=1, iteration=0):
    print("Iteration:", iteration)
    plt.style.use(hep.style.CMS)
    with ur.open(
        BDT_score_path + "background_" + era + ".root:tree_output"
    ) as file:
        bkg_branches = file.arrays(
            [BDT_var, "weight", diMuon_mass_name, "is_" + channel_US + "_category"], library="np"
        )
    with ur.open(
        BDT_score_path + "signal_" + era + ".root:tree_output"
    ) as file:
        signal_branches = file.arrays(
            [BDT_var, "weight", diMuon_mass_name, "is_" + channel_US + "_category"], library="np"
        )

    #signal = []
    #bkg_sqrt = []
    #significance = []
    #bdf_cut_min = 0.0
    # bdf_cut_max = 1.0
    cut_step = 1/100
    #if channel_US == "VBF":
    #    cut_step = bdf_cut_max / k50
    #if iteration == 0:
        #cut_step = bdf_cut_max / 130
     #   cut_step = bdf_cut_max / 130
      #  if channel_US == "VBF":
       #     cut_step = bdf_cut_max / 200
    bins = []
    print(f'BDT categories: {bdt_categories}')
    signal = []
    bkg_sqrt = []
    significance = []
    bins = []

    bkg_bool_list_baseline = (
        (bkg_branches[diMuon_mass_name] > signal_region[0])
        & (bkg_branches[diMuon_mass_name] < signal_region[1])
        & (bkg_branches["is_" + channel_US + "_category"] == 1)
    )
    signal_bool_list_baseline = (
        (signal_branches[diMuon_mass_name] > signal_region[0])
        & (signal_branches[diMuon_mass_name] < signal_region[1])
        & (signal_branches["is_" + channel_US + "_category"] == 1)
    )
    signal_events_baseline = np.sum(
        signal_branches["weight"][signal_bool_list_baseline]
    )
    bkg_events_baseline = np.sum(
        bkg_branches["weight"][bkg_bool_list_baseline]
    )

    print(f'Baseline signal: {signal_events_baseline}')
    print(f'Baseline background: {bkg_events_baseline}')
    Z_baseline = signal_events_baseline / math.sqrt(bkg_events_baseline)
    print(f'Baseline significance: {Z_baseline}')
    quit()

    
    for i in range(0, len(bdt_categories) + 1):
        print(f'i: {i}')
        bdt_cut_min = 0
        bdt_cut_max = 1
        if(i != 0):
            bdt_cut_min = bdt_categories[i-1]
        if(i != len(bdt_categories)):
            bdt_cut_max = bdt_categories[i]
    
        print(f'BDT cut min: {bdt_cut_min} | BDT cut max: {bdt_cut_max}')

        #current_bdt_cut = bdt_cut_min

        bkg_bool_list = (
            (bkg_branches[diMuon_mass_name] > signal_region[0])
            & (bkg_branches[diMuon_mass_name] < signal_region[1])
            & (bkg_branches[BDT_var] > bdt_cut_min)
            & (bkg_branches[BDT_var] < bdt_cut_max)
            & (bkg_branches["is_" + channel_US + "_category"] == 1)
        )
        signal_bool_list = (
            (signal_branches[diMuon_mass_name] > signal_region[0])
            & (signal_branches[diMuon_mass_name] < signal_region[1])
            & (signal_branches[BDT_var] > bdt_cut_min)
            & (signal_branches[BDT_var] < bdt_cut_max)
            & (signal_branches["is_" + channel_US + "_category"] == 1)
        )
        signal_events = np.sum(
            signal_branches["weight"][signal_bool_list]
        )
        bkg_events = np.sum(
            bkg_branches["weight"][bkg_bool_list]
        )

        #if bkg_events <= 0:
        #    current_bdt_cut += cut_step
        #    continue

        signal.append(signal_events)
        bkg_sqrt.append(math.sqrt(bkg_events))
        signal = np.array(signal)
        bkg_sqrt = np.array(bkg_sqrt)
        bins.append(current_bdt_cut)
        significance = np.divide(signal_events / math.sqrt(bkg_events))
        #print(f'Current BDT cut significance: {significance[-1]}')

        while current_bdt_cut < bdt_cut_max:
            print("----------------------------------------------------------------")
            print("min cut:", current_bdt_cut)
            print("max cut:", bdt_cut_max)
            print("----------------------------------------------------------------")
            bkg_bool_list = (
                (bkg_branches[diMuon_mass_name] > signal_region[0])
                & (bkg_branches[diMuon_mass_name] < signal_region[1])
                & (bkg_branches[BDT_var] > current_bdt_cut)
                & (bkg_branches[BDT_var] < current_bdt_cut + cut_step)
                & (bkg_branches["is_" + channel_US + "_category"] == 1)
            )
            signal_bool_list = (
                (signal_branches[diMuon_mass_name] > signal_region[0])
                & (signal_branches[diMuon_mass_name] < signal_region[1])
                & (signal_branches[BDT_var] > current_bdt_cut)
                & (signal_branches[BDT_var] < current_bdt_cut + cut_step)
                & (signal_branches["is_" + channel_US + "_category"] == 1)
            )
            signal_events = np.sum(
                signal_branches["weight"][signal_bool_list]
            )
            bkg_events = np.sum(
                bkg_branches["weight"][bkg_bool_list]
            )

            if bkg_events <= 0:
                current_bdt_cut += cut_step
                continue
            signal.append(signal_events)
            bkg_sqrt.append(math.sqrt(bkg_events))
            bins.append(current_bdt_cut)
            significance.append(signal_events / math.sqrt(bkg_events))
            print(f'Current BDT cut significance: {significance[-1]}')

            current_bdt_cut += cut_step

    fig, ax = get_canvas()

    ey = (signal/bkg_sqrt)*(1/signal + 0.25/bkg_sqrt**2)**(0.5)
    print("significanse lend: ", len(significance))
    print("ey  lend: ", len(ey))
    ax.errorbar(
        bins,
        significance,
        #ey,
        marker="o",
        linestyle="",
        markerfacecolor="black",
        color="black",
        markersize=5,
        # label=labelList[j],
    )

    # hep.cms.label(
    # data="True", label="", year=era, com="13.6", lumi=luminosity[era], ax=ax
    # )
    hep.cms.label(data="True", ax=ax, com="13.6")

    max_height = max(significance)
    best_cut = bins[significance.index(max(significance))]
    print(f"MAX significance: {max(significance)} at BDT score: {best_cut}")

    #print(significance)
    ax.axvline(
        x=best_cut,
        # ymin=0.0,
        # ymax=max_height,
        color="red",
        linestyle="--",
        alpha=0.5,
    )

    # print("BDT > ", best_cut)
    # ax.set_yscale("log")
    # ax.set_ylim(
    # 0.001,
    # 10 * max_height,
    # )
    ax.set_ylim(0.0, 1.3 * max_height)
    ax.set_xlim(bins[0], bins[-1])
    #ax.set_xlim(0.75, 1.01)
    ax.set_ylabel(r"S/$\sqrt{B}$", loc="center")
    # ax.legend(frameon=False, loc="upper right")
    ax.set_xlabel("BTD Cut")

    output_directory = "../plots/" + channel_US + "_category/BDT_categories/cuts/"
    save_name = "BDT_cuts_" + era + "_Cat" + str(iteration) + "_" + subset_title
    save_figure(fig, output_directory, save_name)

    bdt_categories.append(best_cut)
    bdt_categories.sort()
    print(f'BDT categories at end: {bdt_categories}')
    #bdt_categories.append(round(best_cut, 1))
    # if max(significance) > 0.05:
    if iteration < N_max_iterations:
        find_bdt_categories(era, bdt_categories, best_cut, iteration + 1)

    
    while bdf_cut_min < bdf_cut_max:
        print("----------------------------------------------------------------")
        print("min cut:", bdf_cut_min)
        print("max cut:", bdf_cut_max)
        print("----------------------------------------------------------------")
        bkg_bool_list = (
            (bkg_branches[diMuon_mass_name] > signal_region[0])
            & (bkg_branches[diMuon_mass_name] < signal_region[1])
            & (bkg_branches[BDT_var] > bdf_cut_min)
            & (bkg_branches[BDT_var] < bdf_cut_max)
            & (bkg_branches["is_" + channel_US + "_category"] == 1)
        )
        signal_bool_list = (
            (signal_branches[diMuon_mass_name] > signal_region[0])
            & (signal_branches[diMuon_mass_name] < signal_region[1])
            & (signal_branches[BDT_var] > bdf_cut_min)
            & (signal_branches[BDT_var] < bdf_cut_max)
            & (signal_branches["is_" + channel_US + "_category"] == 1)
        )

        signal_events = np.sum(
            signal_branches["weight"][signal_bool_list]
        )
        bkg_events = np.sum(
            bkg_branches["weight"][bkg_bool_list]
        )
        # print("signal = ", signal_events)
        # print("bkg = ", bkg_events)
        # print("S/sqrt(bkg) = ", signal_events/ math.sqrt(bkg_events))
        # print("min cut= ", bdf_cut_min)
        # print("max cut= ", bdf_cut_max)
        if bkg_events <= 0:
           break
        signal.append(signal_events)
        bkg_sqrt.append(math.sqrt(bkg_events))
        bins.append(bdf_cut_min)
        significance.append(signal_events / math.sqrt(bkg_events))

        bdf_cut_min += cut_step

    fig, ax = get_canvas()

    signal = np.array(signal)
    bkg_sqrt = np.array(bkg_sqrt)
    ey = (signal/bkg_sqrt)*(1/signal + 0.25/bkg_sqrt**2)**(0.5)
    print("significanse lend: ", len(significance))
    print("ey  lend: ", len(ey))
    ax.errorbar(
        bins,
        significance,
        #ey,
        marker="o",
        linestyle="",
        markerfacecolor="black",
        color="black",
        markersize=5,
        # label=labelList[j],
    )

    # hep.cms.label(
    # data="True", label="", year=era, com="13.6", lumi=luminosity[era], ax=ax
    # )
    hep.cms.label(data="True", ax=ax, com="13.6")

    max_height = max(significance)
    best_cut = bins[significance.index(max(significance))]
    print("MAX significance: ", max(significance))
    #print(significance)
    ax.axvline(
        x=best_cut,
        # ymin=0.0,
        # ymax=max_height,
        color="red",
        linestyle="--",
        alpha=0.5,
    )

    # print("BDT > ", best_cut)
    # ax.set_yscale("log")
    # ax.set_ylim(
    # 0.001,
    # 10 * max_height,
    # )
    ax.set_ylim(0.0, 1.3 * max_height)
    ax.set_xlim(bins[0], bins[-1])
    #ax.set_xlim(0.75, 1.01)
    ax.set_ylabel(r"S/$\sqrt{B}$", loc="center")
    # ax.legend(frameon=False, loc="upper right")
    ax.set_xlabel("BTD Cut")

    output_directory = "../plots/" + channel_US + "_category/BDT_categories/cuts/"
    save_name = "BDT_cuts_" + era + "_Cat" + str(iteration) + "_" + subset_title
    save_figure(fig, output_directory, save_name)

    bdt_categories.append(best_cut)
    bdt_categories.sort()
    #bdt_categories.append(round(best_cut, 1))
    # if max(significance) > 0.05:
    if iteration < N_max_iterations:
        find_bdt_categories(era, bdt_categories, best_cut, iteration + 1)'''


def draw_bdt_categories(era):
    plt.style.use(hep.style.CMS)
    bdt_categories = []
    find_bdt_categories(era, bdt_categories)
    bdt_categories.append(1.0)
    bdt_categories.append(0.0)
    bdt_categories.sort()
    log_y = False

    print("Era: ", era)
    print("Categories: ", bdt_categories)

    with ur.open(
        BDT_score_path + "background_" + era + ".root:tree_output"
    ) as file:
        bkg_branches = file.arrays(
            [BDT_var, "weight", diMuon_mass_name, "is_" + channel_US + "_category"], library="np"
        )
        bkg_bool_list = (
            (bkg_branches[diMuon_mass_name] > 110)
            & (bkg_branches[diMuon_mass_name] < 150)
            & (bkg_branches["is_" + channel_US + "_category"] == 1)
        )
        print(f'Max BDTtrans value {np.max(np.arctanh(bkg_branches[BDT_var][bkg_bool_list]))}')
        bkg_hist, bkg_bins = np.histogram(
            #np.arctanh(bkg_branches[BDT_var][bkg_bool_list]),
            bkg_branches[BDT_var][bkg_bool_list],
            bins=n_bins[BDT_var],
            #range=x_range[BDT_var],
            range=(0,1),
            weights=bkg_branches["weight"][bkg_bool_list],
        )

    if draw_data:
        with ur.open(
            BDT_score_path + "data_" + era + ".root:tree_output"
        ) as file:
            data_branches = file.arrays(
                [BDT_var, diMuon_mass_name, "is_" + channel_US + "_category"], library="np"
            )
            data_bool_list = (
                (data_branches[diMuon_mass_name] > 110)
                & (data_branches[diMuon_mass_name] < 150)
                & ((data_branches[diMuon_mass_name] < 120)
                | (data_branches[diMuon_mass_name] > 130))
                & (data_branches["is_" + channel_US + "_category"] == 1)
            )
            data_hist, data_bins = np.histogram(
                #np.arctanh(data_branches[BDT_var][data_bool_list]),
                data_branches[BDT_var][data_bool_list],
                bins=n_bins[BDT_var],
                #range=x_range[BDT_var],
                range=(0,1),
            )

    print("BDT bins: ", n_bins[BDT_var])
    with ur.open(
        BDT_score_path + "signal_" + era + ".root:tree_output"
    ) as file:
        signal_branches = file.arrays(
            [BDT_var, "weight", diMuon_mass_name,"is_" + channel_US + "_category"], library="np"
        )
        signal_bool_list = (
            (signal_branches[diMuon_mass_name] > 110)
            & (signal_branches[diMuon_mass_name] < 150)
            & (signal_branches["is_" + channel_US + "_category"] == 1)
        )
        signal_hist, signal_bins = np.histogram(
            #np.arctanh(signal_branches[BDT_var][signal_bool_list]),
            signal_branches[BDT_var][signal_bool_list],
            bins=n_bins[BDT_var],
            #range=x_range[BDT_var],
            range=(0,1),
            weights=signal_branches["weight"][signal_bool_list],
        )
    fig, axs = get_canvas(True)

    hep.histplot(
        bkg_hist / np.sum(bkg_hist),
        bkg_bins,
        label="Background",
        ax=axs[0],
        stack=True,
        linewidth=2,
        color="red",
    )
    if draw_data:
        hep.histplot(
            data_hist / np.sum(data_hist),
            data_bins,
            label="Data",
            ax=axs[0],
            stack=True,
            linewidth=2,
            color="black",
        )

    hep.histplot(
        signal_hist / np.sum(signal_hist),
        signal_bins,
        label="Signal",
        color="blue",
        linewidth=2,
        ax=axs[0],
    )

    hep.cms.label(
        data="True",
        label="",
        com="13.6",
        # lumi=luminosity[era],
        ax=axs[0],
    )

    
    if log_y:
        max_height = max(np.max(signal_hist / np.sum(signal_hist)), np.max(bkg_hist / np.sum(bkg_hist)))
        axs[0].set_yscale("log")
        axs[0].set_ylim(
        0.0000001,
        10 * max_height,
        )
    else:
        axs[0].set_ylim(
            0.0,
            1.3
            * max(
                np.max(signal_hist / np.sum(signal_hist)),
                np.max(bkg_hist / np.sum(bkg_hist)),
            ),
        )
    axs[0].set_xlim(signal_bins[0], signal_bins[-1])
    #axs[0].set_xlim(0, 2)
    axs[0].set_ylabel(r"Events/ Total events", loc="center")
    axs[0].legend(frameon=False, loc="upper right")

    signal = []
    bkg_sqrt = []
    
    #Z_by_cat, Z_tot = get_expected_significance(bkg_branches, signal_branches, bdt_categories)

    for category in range(len(bdt_categories)-1):
        if category != 0:
            axs[0].axvline(
                #x=np.arctanh(bdt_categories[category]),
                x=bdt_categories[category],
                # ymin=0.001,
                color="grey",
                linestyle="--",
                alpha=0.5,
            )
        bkg_bool_list = (
            (bkg_branches[diMuon_mass_name] > signal_region[0])
            & (bkg_branches[diMuon_mass_name] < signal_region[1])
            & (bkg_branches[BDT_var] > bdt_categories[category])
            & (bkg_branches[BDT_var] < bdt_categories[category + 1])
            & (bkg_branches["is_" + channel_US + "_category"] == 1)
        )
        signal_bool_list = (
            (signal_branches[diMuon_mass_name] > signal_region[0])
            & (signal_branches[diMuon_mass_name] < signal_region[1])
            & (signal_branches[BDT_var] > bdt_categories[category])
            & (signal_branches[BDT_var] < bdt_categories[category + 1])
            & (signal_branches["is_" + channel_US + "_category"] == 1)
        )

        signal_events = np.sum(
            signal_branches["weight"][signal_bool_list]
        )
        bkg_events = np.sum(
           bkg_branches["weight"][bkg_bool_list]
        )
        signal.append(signal_events)
        bkg_sqrt.append(math.sqrt(bkg_events))

    ratio_hist, ratio_error = get_histograms_ratio(np.array(signal), np.array(bkg_sqrt))

    hep.histplot(
        ratio_hist,
        #np.arctanh(bdt_categories),
        bdt_categories,
        yerr=ratio_error,
        xerr=True,
        histtype="errorbar",
        color="black",
        ax=axs[1],
    )

    print(ratio_hist)
    

    axs[1].set_ylabel(r"S/$\sqrt{B}$", loc="center")
    axs[1].set_ylim(0.0, 2.000)
    axs[1].set_xlim(signal_bins[0], signal_bins[-1])
    #axs[1].set_xlim(0, 2)
    axs[1].set_xlabel(x_labels[BDT_var])

    output_directory = "../plots/" + channel_US + "_category/BDT_categories/"
    save_name = "BDT_output_" + era + "_" + subset_title
    save_figure(fig, output_directory, save_name)
'''
    fig, ax = get_canvas()

    #signal = np.array(signal)
    #bkg_sqrt = np.array(bkg_sqrt)
    #sig = np.divide(signal_hist, bkg_hist)
    print(signal_hist)
    print(bkg_hist)
    ax.errorbar(
        signal,
        sig,
        #ey,
        marker="o",
        linestyle="",
        markerfacecolor="black",
        color="black",
        markersize=5,
        # label=labelList[j],
    )

    # hep.cms.label(
    # data="True", label="", year=era, com="13.6", lumi=luminosity[era], ax=ax
    # )
    hep.cms.label(data="True", ax=ax, com="13.6")

    for category in range(len(bdt_categories) - 1):
        if category != 0:
            ax.axvline(
                x=bdt_categories[category],
                # ymin=0.001,
                color="red",
                linestyle="--",
                alpha=0.5,
            )

    # print("BDT > ", best_cut)
    # ax.set_yscale("log")
    # ax.set_ylim(
    # 0.001,
    # 10 * max_height,
    # )
    ax.set_ylim(0.0, 1.3 * max(sig))
    ax.set_xlim(signal_bins[0], signal_bins[-1])
    #ax.set_xlim(0.75, 1.01)
    ax.set_ylabel(r"S/$\sqrt{B}$", loc="center")
    # ax.legend(frameon=False, loc="upper right")
    ax.set_xlabel("BTD Cut")

    output_directory = "../plots/" + channel_US + "_category/BDT_categories/"
    save_name = "BDT_cuts_" + era
    save_figure(fig, output_directory, save_name)'''


for era in eras:
    draw_bdt_categories(era)
    # find_bdt_categories(era)
