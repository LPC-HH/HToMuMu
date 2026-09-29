import uproot as ur
import mplhep as hep
import numpy as np
import math
import matplotlib.pyplot as plt
import sys
import csv
import pandas as pd
from pathlib import Path

from utils.labels import luminosity, x_range, n_bins, x_labels
from utils.helper import get_canvas, save_figure, get_histograms_ratio

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))
from bdt_categories_io import save_bdt_category

if len(sys.argv) < 3:
    print(
        "Arguments missing: Channel_under_study, era, bdt/kin categorization, background_subset, signal_subset"
    )
    exit()
channel_US = sys.argv[1]
era_input = sys.argv[2]

ifKfold = False
if "--legacy" in sys.argv:
    print("Not using k-fold BDT")
    ifKfold = True
else:
    print("Using k-fold BDT")

if "--only" in sys.argv:
    sys.argv.remove("--only")
    eras = [era_input]
elif era_input == "2022":
    eras = ["2022", "2022EE", "2022Combined"]
elif era_input == "2023":
    eras = ["2023", "2023BPix", "2023Combined"]
elif era_input == "2024":
    eras = ["2024"]
elif era_input == "2025":
    eras = ["2025"]
elif era_input == "Combined":
    eras = ["Combined"]
elif era_input == "All":
    eras = ["2022", "2022EE", "2023", "2023BPix", "2024", "Combined"]
else:
    print("Set era to be one of the available sets:")
    print(" > 2022, 2023, 2024, Combined, All")
    exit()

category_var = "category"
file_append = ""
if len(sys.argv) == 3:
    background_subset = "Full"
    signal_subset = "NottH"
    print("Using default subsets:", background_subset, signal_subset)
elif len(sys.argv) == 4:
    background_subset = "Full"
    signal_subset = "NottH"
    print("Using default subsets:", background_subset, signal_subset)

    flag = sys.argv[3]
    print("Using " + flag + " categorization")
    if flag == "bdt":
        category_var = "categoryBDT"
        file_append = "reCat"
    elif flag == "kin":
        category_var = "category"
    if ifKfold:
        # the pre-K-fold single-model scores (train.py --stage legacy). Reads
        # BDT_score/<channel>legacy/ and saves its boundaries under the key "<channel>legacy",
        # so the fold-matched boundaries under "<channel>" are left untouched. Those MC scores
        # are in-sample for 60% of the MC, so the resulting significance is optimistically
        # biased -- for comparison only.
        file_append += "legacy"
    else:
        print("Set production categorization to be:")
        print(" > bdt, kin")
        exit()
    print("BDT categorization var: " + category_var)
elif len(sys.argv) == 6:
    background_subset = sys.argv[4]
    signal_subset = sys.argv[5]
else:
    print("Include subset of background AND signal only.")
    exit()

print("Channel under study: ", channel_US)
print("Eras: ", eras)
print("Background subset: ", background_subset)
print("Signal subset: ", signal_subset)
print("Production category: " + category_var)

subset_title = "B" + background_subset + "_S" + signal_subset
BDT_var = "BDT_" + channel_US

# The hadded BDT_score files are tens of GB. uproot's default source memory-maps the whole
# file, which alone exhausts the 16 GiB per-process virtual-memory limit on the LPC login
# nodes (MemoryError); this handler reads the file in chunks instead. Accepted by both the
# CMSSW uproot (5.0.7) and current versions.
UPROOT_OPEN = dict(file_handler=ur.MultithreadedFileSource)
# BDT_score_path = "/eos/uscms/store/user/lpchmumu/esledge/analyzer_HiggsMuMu_v1.5/tuples_v1.5.0/BDT_score/" + channel_US + "/" + subset_title + "/"
BDT_score_path = "../root_io/tuples/BDT_score/" + channel_US + file_append + "/" + subset_title + "/"
#N_max_iterations = 4 if channel_US == "ggH" else 4
use_bsConstrain = True
#signal_region = (122.5 , 127.5)
signal_region = (121.0 , 129.0)
draw_data = True

if use_bsConstrain:
    diMuon_mass_name = "diMuon_bsConstrainedMass"
else:
    diMuon_mass_name = "diMuon_mass"
print("diMuon mass variable name: ", diMuon_mass_name)
print(f"BDT Score Path {BDT_score_path}")

def asimov_significance(signal, background):
    if background <= 0 or signal <= 0:
        return 0.0

    return math.sqrt(
        2.0 * (
            (signal + background) * math.log(1.0 + signal / background)
            - signal
        )
    )

#def create_bool_list(bkg_branches, signal_branches, bdt_min, bdt_max)

def get_yields(bkg_branches, signal_branches, bdt_categories):
    signal_yield_total = 0
    signal_yield_SR = 0
    bkg_yield_total = 0
    bkg_yield_SR = 0

    total_region = (110.0, 150.0)
    yields = []
    for i in range(len(bdt_categories) - 1):
        print(f'Cat: {len(bdt_categories) - i - 1} of {len(bdt_categories) - 1}')
        bdt_cut_min = bdt_categories[i]
        bdt_cut_max = bdt_categories[i+1]

        bkg_bool_list_total = (
            (bkg_branches[diMuon_mass_name] > total_region[0])
            & (bkg_branches[diMuon_mass_name] < total_region[1])
            & (bkg_branches[BDT_var] > bdt_cut_min)
            & (bkg_branches[BDT_var] < bdt_cut_max)
            & (bkg_branches["is_" + channel_US + "_" + category_var] == 1)
        )
        signal_bool_list_total = (
            (signal_branches[diMuon_mass_name] > total_region[0])
            & (signal_branches[diMuon_mass_name] < total_region[1])
            & (signal_branches[BDT_var] > bdt_cut_min)
            & (signal_branches[BDT_var] < bdt_cut_max)
            & (signal_branches["is_" + channel_US + "_" + category_var] == 1)
        )

        bkg_bool_list_SR = (
            (bkg_branches[diMuon_mass_name] > signal_region[0])
            & (bkg_branches[diMuon_mass_name] < signal_region[1])
            & (bkg_branches[BDT_var] > bdt_cut_min)
            & (bkg_branches[BDT_var] < bdt_cut_max)
            & (bkg_branches["is_" + channel_US + "_" + category_var] == 1)
        )
        signal_bool_list_SR = (
            (signal_branches[diMuon_mass_name] > signal_region[0])
            & (signal_branches[diMuon_mass_name] < signal_region[1])
            & (signal_branches[BDT_var] > bdt_cut_min)
            & (signal_branches[BDT_var] < bdt_cut_max)
            & (signal_branches["is_" + channel_US + "_" + category_var] == 1)
        )

        signal_events_total = np.sum(
            signal_branches["weight"][signal_bool_list_total]
        )
        bkg_events_total = np.sum(
            bkg_branches["weight"][bkg_bool_list_total]
        )

        signal_events_SR = np.sum(
            signal_branches["weight"][signal_bool_list_SR]
        )
        bkg_events_SR = np.sum(
            bkg_branches["weight"][bkg_bool_list_SR]
        )
        category_name = f"{channel_US}cat{len(bdt_categories) - i - 1}"
        yieldsCat = {'Category': channel_US+str(len(bdt_categories) - i - 1), 'Total Sig': round(signal_events_total, 2), 'Total Bkg': round(bkg_events_total, 2), 'Sig SR': round(signal_events_SR, 2), 'Bkg SR': round(bkg_events_SR, 2), 'S/sqrt(B) SR': round(signal_events_SR/math.sqrt(bkg_events_SR), 2)}
        yields.append(yieldsCat)
    return yields




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
            & (bkg_branches["is_" + channel_US + "_" + category_var] == 1)
        )
        signal_bool_list = (
            (signal_branches[diMuon_mass_name] > signal_region[0])
            & (signal_branches[diMuon_mass_name] < signal_region[1])
            & (signal_branches[BDT_var] > bdt_cut_min)
            & (signal_branches[BDT_var] < bdt_cut_max)
            & (signal_branches["is_" + channel_US + "_" + category_var] == 1)
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
            # Z = signal_events / math.sqrt(bkg_events)
            Z = asimov_significance(signal_events, bkg_events)
        #print(f'Significance in cat {i+1} of {len(bdt_categories) + 1}: {Z}')
        Z_by_cat.append(Z)

    Z_tot = math.sqrt(sum(x**2 for x in Z_by_cat))

    return Z_by_cat, Z_tot

def find_bdt_categories(era, bkg_branches, signal_branches, bdt_categories, bdt_cut_max=1, iteration=0):
    print(f"BDT Categories iteration {iteration}: {bdt_categories}")

    max_categories = 8

    # Number of categories = number of cuts + 1
    if len(bdt_categories) >= max_categories - 1:
        print(f"Reached maximum number of categories: {max_categories}")
        print(f"Final BDT Categories: {bdt_categories}")
        return
    #print("Iteration:", iteration)
    plt.style.use(hep.style.CMS)
    '''with ur.open(
        BDT_score_path + "background_" + era + ".root:tree_output"
    ) as file:
        bkg_branches = file.arrays(
            [BDT_var, "weight", diMuon_mass_name, "is_" + channel_US + "_categoryBDT"], library="np"
        )
    with ur.open(
        BDT_score_path + "signal_" + era + ".root:tree_output"
    ) as file:
        signal_branches = file.arrays(
            [BDT_var, "weight", diMuon_mass_name, "is_" + channel_US + "_categoryBDT"], library="np"
        )'''

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
    N_max_iterations = 8 if channel_US == "ggH" else 8
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
    hep.cms.label(data="True", ax=ax, com="13.6", lumi=luminosity[era])

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

    output_directory = "../plots/" + channel_US + file_append + "_category/BDT_categories/cuts/"
    save_name = "BDT_cuts_" + era + "_Cat" + str(iteration) + "_" + subset_title
    save_figure(fig, output_directory, save_name)


    

    find_bdt_categories(era, bkg_branches, signal_branches, bdt_categories, iteration=iteration+1)

def draw_bdt_categories(era):
    plt.style.use(hep.style.CMS)
    fname = BDT_score_path + "background_" + era + ".root:tree_output"
    print(f"Opening {fname}")
    with ur.open(
        fname, **UPROOT_OPEN
    ) as file:
        bkg_branches = file.arrays(
            [BDT_var, "weight", diMuon_mass_name, "is_" + channel_US + "_" + category_var], library="np"
        )
        bkg_bool_list = (
            (bkg_branches[diMuon_mass_name] > 110)
            & (bkg_branches[diMuon_mass_name] < 150)
            & ((bkg_branches[diMuon_mass_name] < 120)
            | (bkg_branches[diMuon_mass_name] > 130))
            & (bkg_branches["is_" + channel_US + "_" + category_var] == 1)
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
            BDT_score_path + "data_" + era + ".root:tree_output", **UPROOT_OPEN
        ) as file:
            data_branches = file.arrays(
                [BDT_var, diMuon_mass_name, "is_" + channel_US + "_" + category_var], library="np"
            )
            data_bool_list = (
                (data_branches[diMuon_mass_name] > 110)
                & (data_branches[diMuon_mass_name] < 150)
                & ((data_branches[diMuon_mass_name] < 120)
                | (data_branches[diMuon_mass_name] > 130))
                & (data_branches["is_" + channel_US + "_" + category_var] == 1)
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
        BDT_score_path + "signal_" + era + ".root:tree_output", **UPROOT_OPEN
    ) as file:
        signal_branches = file.arrays(
            [BDT_var, "weight", diMuon_mass_name,"is_" + channel_US + "_" + category_var], library="np"
        )
        signal_bool_list = (
            (signal_branches[diMuon_mass_name] > 110)
            & (signal_branches[diMuon_mass_name] < 150)
            & (signal_branches["is_" + channel_US + "_" + category_var] == 1)
        )
        signal_hist, signal_bins = np.histogram(
            #np.arctanh(signal_branches[BDT_var][signal_bool_list]),
            signal_branches[BDT_var][signal_bool_list],
            bins=n_bins[BDT_var],
            #range=x_range[BDT_var],
            range=(0,1),
            weights=signal_branches["weight"][signal_bool_list],
        )
    bdt_categories = []
    find_bdt_categories(era, bkg_branches, signal_branches, bdt_categories)
    Z_by_cat, Z_tot = get_expected_significance(bkg_branches, signal_branches, bdt_categories)
    print(f'FINAL Total expected significance: {Z_tot}')
    print(f'FINAL Expected significance by cat: {Z_by_cat}')
    bdt_categories.append(1.0)
    bdt_categories.append(0.0)
    bdt_categories.sort()
    save_bdt_category(channel_US + file_append, era, subset_title, diMuon_mass_name, bdt_categories)
    log_y = False

    print("Era: ", era)
    print("Categories: ", bdt_categories)

    yields = get_yields(bkg_branches, signal_branches, bdt_categories)

    df_yields = pd.DataFrame(yields)
    # Add combined row
    combined_row = {
        "Category": "Combined",
        "Total Sig": round(df_yields["Total Sig"].sum(), 2),
        "Total Bkg": round(df_yields["Total Bkg"].sum(), 2),
        "Sig SR": round(df_yields["Sig SR"].sum(), 2),
        "Bkg SR": round(df_yields["Bkg SR"].sum(), 2),
        "S/sqrt(B) SR": round(np.sqrt(np.sum(df_yields["S/sqrt(B) SR"]**2)), 2),
    }

    df_yields = pd.concat(
        [df_yields, pd.DataFrame([combined_row])],
        ignore_index=True
    )
    csv_file = f"../yields/BDTcatYields{channel_US}{file_append}.csv"
    print(f"Creating CSV file: {csv_file}")
    df_yields.to_csv(csv_file, index=False)

    draw_bdt_output_plot(era, bkg_hist, bkg_bins, data_hist, data_bins, signal_hist, signal_bins,
                          bkg_branches, signal_branches, bdt_categories, normalize=True)
    draw_bdt_output_plot(era, bkg_hist, bkg_bins, data_hist, data_bins, signal_hist, signal_bins,
                          bkg_branches, signal_branches, bdt_categories, normalize=False)


def draw_bdt_output_plot(era, bkg_hist, bkg_bins, data_hist, data_bins, signal_hist, signal_bins,
                          bkg_branches, signal_branches, bdt_categories, normalize=True):
    log_y = False

    signal_mult = 100
    bkg_y = bkg_hist / np.sum(bkg_hist) if normalize else bkg_hist
    data_y = data_hist / np.sum(data_hist) if normalize else data_hist
    signal_y = signal_hist / np.sum(signal_hist) if normalize else signal_hist*signal_mult

    fig, axs = get_canvas(True)

    hep.histplot(
        bkg_y,
        bkg_bins,
        label="Background",
        ax=axs[0],
        stack=True,
        linewidth=2,
        color="red",
    )
    if draw_data:
        hep.histplot(
            data_y,
            data_bins,
            label="Data (Sidebands)",
            ax=axs[0],
            stack=True,
            linewidth=2,
            color="black",
        )

    hep.histplot(
        signal_y,
        signal_bins,
        label="Signal" if normalize else f"Signal*{signal_mult}",
        color="blue",
        linewidth=2,
        ax=axs[0],
    )

    hep.cms.label(
        data="True",
        label="",
        com="13.6",
        lumi=luminosity[era],
        ax=axs[0],
    )


    if log_y:
        max_height = max(np.max(signal_y), np.max(bkg_y))
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
                np.max(signal_y),
                np.max(bkg_y),
            ),
        )
    axs[0].set_xlim(signal_bins[0], signal_bins[-1])
    #axs[0].set_xlim(0, 2)
    axs[0].set_ylabel(r"Events/ Total events" if normalize else r"Events", loc="center")
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
            & (bkg_branches["is_" + channel_US + "_" + category_var] == 1)
        )
        signal_bool_list = (
            (signal_branches[diMuon_mass_name] > signal_region[0])
            & (signal_branches[diMuon_mass_name] < signal_region[1])
            & (signal_branches[BDT_var] > bdt_categories[category])
            & (signal_branches[BDT_var] < bdt_categories[category + 1])
            & (signal_branches["is_" + channel_US + "_" + category_var] == 1)
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

    output_directory = "../plots/" + channel_US + file_append + "_category/BDT_categories/"
    save_name = ("BDT_output_" if normalize else "BDT_output_raw_") + era + "_" + subset_title
    save_figure(fig, output_directory, save_name)


for era in eras:
    draw_bdt_categories(era)
    # find_bdt_categories(era)
