#!/usr/bin/env python3

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import pandas as pd
import uproot as ur
from utils.helper import get_canvas, get_histograms_ratio, save_figure
from utils.labels import luminosity, n_bins, x_labels, x_range

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))
from bdt_categories_io import save_bdt_category

if len(sys.argv) < 3:
    print(
        "Arguments missing: "
        "Channel_under_study, era, background_subset, signal_subset"
    )
    sys.exit(1)

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
    sys.exit(1)

if len(sys.argv) == 3:
    background_subset = "Full"
    signal_subset = "NottH"
    print("Using default subsets:", background_subset, signal_subset)
elif len(sys.argv) == 5:
    background_subset = sys.argv[3]
    signal_subset = sys.argv[4]
else:
    print("Include subset of background AND signal only.")
    sys.exit(1)

print("Channel under study:", channel_US)
print("Eras:", eras)
print("Background subset:", background_subset)
print("Signal subset:", signal_subset)

subset_title = "B" + background_subset + "_S" + signal_subset
BDT_var = "BDT_" + channel_US
BDT_score_path = "../root_io/tuples/BDT_score/" + channel_US + "/" + subset_title + "/"

use_bsConstrain = True
signal_region = (122.5, 127.5)
sideband_mass_range = (110.0, 150.0)
blind_region = (120.0, 130.0)
draw_data = True

if use_bsConstrain:
    diMuon_mass_name = "diMuon_bsConstrainedMass"
else:
    diMuon_mass_name = "diMuon_mass"

print("diMuon mass variable name:", diMuon_mass_name)

USE_BDT_REWEIGHTING = True
if channel_US == "VBF":
    BDT_REWEIGHT_NBINS = 25  # width = 0.04
else:
    BDT_REWEIGHT_NBINS = 50  # width = 0.02


def asimov_significance(signal, background):
    if background <= 0 or signal <= 0:
        return 0.0

    return math.sqrt(
        2.0 * ((signal + background) * math.log(1.0 + signal / background) - signal)
    )


def get_yields(
    bkg_branches,
    signal_branches,
    bdt_categories,
    bdt_reweight_edges=None,
    bdt_reweight_weights=None,
):
    total_region = (110.0, 150.0)
    yields = []

    for i in range(len(bdt_categories) - 1):
        print(f"Cat: {len(bdt_categories) - i - 1} of {len(bdt_categories) - 1}")

        bdt_cut_min = bdt_categories[i]
        bdt_cut_max = bdt_categories[i + 1]

        # Total region
        bkg_bool_list_total = (
            (bkg_branches[diMuon_mass_name] > total_region[0])
            & (bkg_branches[diMuon_mass_name] < total_region[1])
            & (bkg_branches[BDT_var] > bdt_cut_min)
            & (bkg_branches[BDT_var] < bdt_cut_max)
            & (bkg_branches["is_" + channel_US + "_category"] == 1)
        )
        signal_bool_list_total = (
            (signal_branches[diMuon_mass_name] > total_region[0])
            & (signal_branches[diMuon_mass_name] < total_region[1])
            & (signal_branches[BDT_var] > bdt_cut_min)
            & (signal_branches[BDT_var] < bdt_cut_max)
            & (signal_branches["is_" + channel_US + "_category"] == 1)
        )

        signal_events_total = np.sum(signal_branches["weight"][signal_bool_list_total])

        bkg_nominal_weights_total = np.asarray(
            bkg_branches["weight"][bkg_bool_list_total],
            dtype=np.float64,
        )

        if bdt_reweight_edges is not None and bdt_reweight_weights is not None:
            bkg_bdt_weights_total = get_bdt_reweight_values(
                bkg_branches[BDT_var][bkg_bool_list_total],
                bdt_reweight_edges,
                bdt_reweight_weights,
            )

            bkg_events_total = np.sum(bkg_nominal_weights_total * bkg_bdt_weights_total)
        else:
            bkg_events_total = np.sum(bkg_nominal_weights_total)

        # Signal region

        bkg_bool_list_SR = (
            (bkg_branches[diMuon_mass_name] > signal_region[0])
            & (bkg_branches[diMuon_mass_name] < signal_region[1])
            & (bkg_branches[BDT_var] > bdt_cut_min)
            & (bkg_branches[BDT_var] < bdt_cut_max)
            & (bkg_branches["is_" + channel_US + "_category"] == 1)
        )

        signal_bool_list_SR = (
            (signal_branches[diMuon_mass_name] > signal_region[0])
            & (signal_branches[diMuon_mass_name] < signal_region[1])
            & (signal_branches[BDT_var] > bdt_cut_min)
            & (signal_branches[BDT_var] < bdt_cut_max)
            & (signal_branches["is_" + channel_US + "_category"] == 1)
        )

        signal_events_SR = np.sum(signal_branches["weight"][signal_bool_list_SR])

        bkg_nominal_weights_SR = np.asarray(
            bkg_branches["weight"][bkg_bool_list_SR],
            dtype=np.float64,
        )

        if bdt_reweight_edges is not None and bdt_reweight_weights is not None:
            bkg_bdt_weights_SR = get_bdt_reweight_values(
                bkg_branches[BDT_var][bkg_bool_list_SR],
                bdt_reweight_edges,
                bdt_reweight_weights,
            )

            bkg_events_SR = np.sum(bkg_nominal_weights_SR * bkg_bdt_weights_SR)
        else:
            bkg_events_SR = np.sum(bkg_nominal_weights_SR)

        # Save yields
        if bkg_events_SR > 0:
            s_over_sqrt_b = signal_events_SR / math.sqrt(bkg_events_SR)
        else:
            s_over_sqrt_b = 0.0

        yieldsCat = {
            "Category": channel_US + str(len(bdt_categories) - i - 1),
            "Total Sig": round(signal_events_total, 2),
            "Total Bkg": round(bkg_events_total, 2),
            "Sig SR": round(signal_events_SR, 2),
            "Bkg SR": round(bkg_events_SR, 2),
            "S/sqrt(B) SR": round(s_over_sqrt_b, 2),
        }

        yields.append(yieldsCat)

    return yields


def get_sideband_mask(branches):
    mass = branches[diMuon_mass_name]

    mass_mask = (
        (mass > sideband_mass_range[0])
        & (mass < sideband_mass_range[1])
        & ((mass < blind_region[0]) | (mass > blind_region[1]))
    )

    category_mask = branches["is_" + channel_US + "_category"] == 1

    return mass_mask & category_mask


def get_bdt_reweight_values(scores, bin_edges, bin_weights):
    scores = np.asarray(scores)

    event_weights = np.ones(
        len(scores),
        dtype=np.float64,
    )

    inside = (scores >= bin_edges[0]) & (scores <= bin_edges[-1])
    indices = np.searchsorted(bin_edges, scores[inside], side="right") - 1
    indices = np.clip(indices, 0, len(bin_weights) - 1)
    event_weights[inside] = bin_weights[indices]

    return event_weights


def calculate_bdt_reweighting(bkg_branches, data_branches):
    mc_mask = get_sideband_mask(bkg_branches)
    data_mask = get_sideband_mask(data_branches)

    mc_scores = np.asarray(bkg_branches[BDT_var][mc_mask])
    data_scores = np.asarray(data_branches[BDT_var][data_mask])

    mc_weights = np.asarray(bkg_branches["weight"][mc_mask], dtype=np.float64)

    data_weights = np.asarray(data_branches["weight"][data_mask], dtype=np.float64)

    bin_edges = np.linspace(0.0, 1.0, BDT_REWEIGHT_NBINS + 1)

    mc_hist, _ = np.histogram(mc_scores, bins=bin_edges, weights=mc_weights)
    data_hist, _ = np.histogram(data_scores, bins=bin_edges, weights=data_weights)

    mc_hist = np.asarray(mc_hist, dtype=np.float64)
    data_hist = np.asarray(data_hist, dtype=np.float64)

    mc_total = np.sum(mc_hist)
    data_total = np.sum(data_hist)

    if mc_total <= 0:
        raise RuntimeError(
            "Total weighted background MC sideband yield <= 0. "
            "Cannot derive the BDT reweighting."
        )

    if data_total <= 0:
        raise RuntimeError(
            "No data events found in the sidebands. "
            "Cannot derive the BDT reweighting."
        )

    mc_norm = mc_hist / mc_total
    data_norm = data_hist / data_total

    bdt_weights = np.ones(BDT_REWEIGHT_NBINS, dtype=np.float64)
    valid_mc_bins = mc_norm > 0
    bdt_weights[valid_mc_bins] = data_norm[valid_mc_bins] / mc_norm[valid_mc_bins]
    invalid_bins = np.where(~valid_mc_bins)[0]

    if len(invalid_bins) > 0:
        print(
            "WARNING: The following BDT-reweight bins have weighted MC <= 0. "
            "Their correction factor is kept at 1."
        )

        for i in invalid_bins:
            print(
                f"  bin {i}: "
                f"[{bin_edges[i]:.3f}, {bin_edges[i + 1]:.3f}) "
                f"MC={mc_hist[i]:.8f}, "
                f"Data={data_hist[i]:.0f}"
            )

    print("BDT REWEIGHTING: NORMALIZED DATA SIDEBAND / MC SIDEBAND")
    print(f"MC sideband weighted yield : {mc_total:.8f}")
    print(f"Data sideband events       : {data_total:.0f}")
    print(
        f"{'BDT range':<22}" f"{'MC norm':>14}" f"{'Data norm':>14}" f"{'weight':>14}"
    )
    print("-" * 64)

    for i in range(BDT_REWEIGHT_NBINS):
        print(
            f"[{bin_edges[i]:.3f}, {bin_edges[i + 1]:.3f})"
            f"{mc_norm[i]:>14.6f}"
            f"{data_norm[i]:>14.6f}"
            f"{bdt_weights[i]:>14.6f}"
        )

    print("============================================================")

    mc_bdt_weights = get_bdt_reweight_values(mc_scores, bin_edges, bdt_weights)

    mc_hist_reweighted, _ = np.histogram(
        mc_scores, bins=bin_edges, weights=mc_weights * mc_bdt_weights
    )

    mc_reweighted_total = np.sum(mc_hist_reweighted)

    if mc_reweighted_total > 0:
        mc_reweighted_norm = mc_hist_reweighted / mc_reweighted_total
    else:
        mc_reweighted_norm = np.zeros_like(mc_hist_reweighted, dtype=np.float64)

    print("Closure check after applying the BDT weights:")
    print(f"{'BDT range':<22}" f"{'Data norm':>14}" f"{'MC rw norm':>14}")
    print("-" * 50)

    for i in range(BDT_REWEIGHT_NBINS):
        print(
            f"[{bin_edges[i]:.3f}, {bin_edges[i + 1]:.3f})"
            f"{data_norm[i]:>14.6f}"
            f"{mc_reweighted_norm[i]:>14.6f}"
        )

    print()

    return bin_edges, bdt_weights


def prepare_significance_sample(
    branches,
    bdt_reweight_edges=None,
    bdt_reweight_weights=None,
):
    mask = (
        (branches[diMuon_mass_name] > signal_region[0])
        & (branches[diMuon_mass_name] < signal_region[1])
        & (branches["is_" + channel_US + "_category"] == 1)
    )

    scores = np.asarray(branches[BDT_var][mask])

    nominal_weights = np.asarray(branches["weight"][mask], dtype=np.float64)

    weights = nominal_weights.copy()

    if bdt_reweight_edges is not None and bdt_reweight_weights is not None:
        new_bdt_weights = get_bdt_reweight_values(
            scores,
            bdt_reweight_edges,
            bdt_reweight_weights,
        )

        weights = nominal_weights * new_bdt_weights

        print("Background yield in the signal region:")
        print(f"  Before BDT reweighting = " f"{np.sum(nominal_weights):.8f}")
        print(f"  After BDT reweighting  = " f"{np.sum(weights):.8f}")

    order = np.argsort(scores)

    scores = scores[order]
    weights = weights[order]
    cumulative_weights = np.empty(len(weights) + 1, dtype=np.float64)
    cumulative_weights[0] = 0.0

    np.cumsum(weights, out=cumulative_weights[1:])

    return scores, cumulative_weights


def get_weighted_yield(sample, bdt_min, bdt_max):
    scores, cumulative_weights = sample

    i_min = np.searchsorted(scores, bdt_min, side="right")
    i_max = np.searchsorted(scores, bdt_max, side="left")

    return cumulative_weights[i_max] - cumulative_weights[i_min]


def get_expected_significance(
    bkg_sample,
    signal_sample,
    bdt_categories,
):
    edges = [0.0] + sorted(bdt_categories) + [1.0]

    Z_by_cat = []

    for bdt_cut_min, bdt_cut_max in zip(edges[:-1], edges[1:]):

        signal_events = get_weighted_yield(signal_sample, bdt_cut_min, bdt_cut_max)
        bkg_events = get_weighted_yield(bkg_sample, bdt_cut_min, bdt_cut_max)
        Z_by_cat.append(asimov_significance(signal_events, bkg_events))

    Z_tot = math.sqrt(sum(Z**2 for Z in Z_by_cat))

    return Z_by_cat, Z_tot


def load_signal_background_data(era):
    mc_branches_to_read = [
        BDT_var,
        "weight",
        diMuon_mass_name,
        "is_" + channel_US + "_category",
    ]

    data_branches_to_read = [
        BDT_var,
        "weight",
        diMuon_mass_name,
        "is_" + channel_US + "_category",
    ]

    print(f"Loading ROOT trees for {era}...")

    with ur.open(BDT_score_path + "background_" + era + ".root:tree_output") as file:
        bkg_branches = file.arrays(
            mc_branches_to_read,
            library="np",
        )

    with ur.open(BDT_score_path + "signal_" + era + ".root:tree_output") as file:
        signal_branches = file.arrays(
            mc_branches_to_read,
            library="np",
        )

    with ur.open(BDT_score_path + "data_" + era + ".root:tree_output") as file:

        data_branches = file.arrays(
            data_branches_to_read,
            library="np",
        )

    return (
        bkg_branches,
        signal_branches,
        data_branches,
    )


def find_bdt_categories(
    era,
    bdt_categories,
    bkg_sample,
    signal_sample,
    iteration=0,
):
    print(f"BDT Categories iteration " f"{iteration}: " f"{bdt_categories}")

    max_categories = 8

    if len(bdt_categories) >= max_categories - 1:
        print(
            "Reached maximum number of categories:",
            max_categories,
        )
        print(
            "Final BDT Categories:",
            bdt_categories,
        )
        return

    Z_by_cat, Z_tot = get_expected_significance(
        bkg_sample,
        signal_sample,
        bdt_categories,
    )

    print(f"Total expected significance: " f"{Z_tot}")
    print(f"Expected significance by cat: " f"{Z_by_cat}")

    cut_step = 1 / 100 if channel_US == "ggH" else 1 / 150

    bdt_bins = np.arange(
        cut_step,
        1.0,
        cut_step,
    )

    Z_at_bin = np.empty(
        len(bdt_bins),
        dtype=np.float64,
    )

    for i, current_bdt_cut in enumerate(bdt_bins):
        bdt_categories_test = sorted(bdt_categories + [current_bdt_cut])

        _, Z_tot_test = get_expected_significance(
            bkg_sample,
            signal_sample,
            bdt_categories_test,
        )

        Z_at_bin[i] = Z_tot_test

    optimal_index = int(np.argmax(Z_at_bin))

    optimal_Z_tot = float(Z_at_bin[optimal_index])

    optimal_bdt_cut = float(bdt_bins[optimal_index])

    if Z_tot == 0:
        relative_increase = math.inf if optimal_Z_tot > 0 else 0.0
    else:
        relative_increase = (optimal_Z_tot - Z_tot) / Z_tot

    print(f"Adding category {iteration} is " f"{relative_increase * 100}% better")

    if relative_increase < 0.01:
        print(f"Category {iteration} only " f"{relative_increase * 100}% better")
        print(
            "Final BDT Categories:",
            bdt_categories,
        )
        return

    bdt_categories.append(optimal_bdt_cut)
    bdt_categories.sort()

    print(
        "New BDT Categories:",
        bdt_categories,
    )
    print(f"New cut at {optimal_bdt_cut} " f"with Z: {optimal_Z_tot} > {Z_tot}")

    fig, ax = get_canvas()

    ax.errorbar(
        bdt_bins,
        Z_at_bin,
        marker="o",
        linestyle="",
        markerfacecolor="black",
        color="black",
        markersize=5,
    )

    hep.cms.label(
        data="True",
        ax=ax,
        com="13.6",
    )

    print(
        f"MAX significance: " f"{optimal_Z_tot} " f"at BDT score: " f"{optimal_bdt_cut}"
    )

    for cut in bdt_categories:
        color_string = (
            "red"
            if np.isclose(
                cut,
                optimal_bdt_cut,
            )
            else "grey"
        )

        ax.axvline(
            x=cut,
            color=color_string,
            linestyle="--",
            alpha=0.5,
        )

    ax.set_ylim(
        0.975 * np.min(Z_at_bin),
        1.025 * optimal_Z_tot,
    )

    ax.set_xlim(
        bdt_bins[0],
        bdt_bins[-1],
    )

    ax.set_ylabel(
        r"S/$\sqrt{B}$",
        loc="center",
    )

    ax.set_xlabel("BDT Cut")

    output_directory = (
        "../plots/" + channel_US + "_category/" + "BDT_categories_data/cuts/"
    )

    save_name = "BDT_cuts_" + era + "_Cat" + str(iteration) + "_" + subset_title

    save_figure(
        fig,
        output_directory,
        save_name,
    )

    plt.close(fig)

    find_bdt_categories(
        era,
        bdt_categories,
        bkg_sample,
        signal_sample,
        iteration=iteration + 1,
    )


def draw_bdt_categories(era):
    plt.style.use(hep.style.CMS)

    bkg_branches, signal_branches, data_branches = load_signal_background_data(era)

    if USE_BDT_REWEIGHTING:
        print("Using DATA SIDEBAND / MC SIDEBAND " "BDT reweighting for background.")

        bdt_reweight_edges, bdt_reweight_weights = calculate_bdt_reweighting(
            bkg_branches, data_branches
        )

    else:
        print("BDT background reweighting disabled.")

        bdt_reweight_edges = None
        bdt_reweight_weights = None

    print("Preparing cumulative BDT distributions...")

    bkg_sample = prepare_significance_sample(
        bkg_branches,
        bdt_reweight_edges=(bdt_reweight_edges),
        bdt_reweight_weights=(bdt_reweight_weights),
    )

    signal_sample = prepare_significance_sample(signal_branches)
    bdt_categories = []
    find_bdt_categories(era, bdt_categories, bkg_sample, signal_sample)

    bdt_categories.append(1.0)
    bdt_categories.append(0.0)
    bdt_categories.sort()

    print("Era:", era)
    print("Categories:", bdt_categories)

    save_bdt_category(channel_US, era, subset_title, diMuon_mass_name, bdt_categories)

    print("Saved BDT categories to JSON.")

    yields = get_yields(
        bkg_branches,
        signal_branches,
        bdt_categories,
        bdt_reweight_edges,
        bdt_reweight_weights,
    )

    df_yields = pd.DataFrame(yields)

    # Add combined row
    combined_row = {
        "Category": "Combined",
        "Total Sig": round(df_yields["Total Sig"].sum(), 2),
        "Total Bkg": round(df_yields["Total Bkg"].sum(), 2),
        "Sig SR": round(df_yields["Sig SR"].sum(), 2),
        "Bkg SR": round(df_yields["Bkg SR"].sum(), 2),
        "S/sqrt(B) SR": round(
            np.sqrt(np.sum(df_yields["S/sqrt(B) SR"] ** 2)),
            2,
        ),
    }

    df_yields = pd.concat([df_yields, pd.DataFrame([combined_row])], ignore_index=True)

    csv_file = (
        "../plots/"
        + channel_US
        + "_category/BDT_categories_data/BDTcatYields"
        + channel_US
        + "_"
        + era
        + "_"
        + subset_title
        + ".csv"
    )

    print(f"Creating CSV file: {csv_file}")
    df_yields.to_csv(
        csv_file,
        index=False,
    )
    log_y = False

    # Background MC diagnostic selection

    if USE_BDT_REWEIGHTING:
        bkg_bool_list = get_sideband_mask(bkg_branches)
    else:
        bkg_bool_list = (
            (bkg_branches[diMuon_mass_name] > 110)
            & (bkg_branches[diMuon_mass_name] < 150)
            & (bkg_branches["is_" + channel_US + "_category"] == 1)
        )

    selected_bkg_scores = bkg_branches[BDT_var][bkg_bool_list]

    if len(selected_bkg_scores) > 0:
        print(f"Max BDTtrans value {np.max(np.arctanh(selected_bkg_scores))}")

    selected_bkg_nominal_weights = np.asarray(
        bkg_branches["weight"][bkg_bool_list],
        dtype=np.float64,
    )

    if USE_BDT_REWEIGHTING:
        selected_bkg_bdt_weights = get_bdt_reweight_values(
            selected_bkg_scores,
            bdt_reweight_edges,
            bdt_reweight_weights,
        )
        selected_bkg_reweighted_weights = (
            selected_bkg_nominal_weights * selected_bkg_bdt_weights
        )
    else:
        selected_bkg_reweighted_weights = selected_bkg_nominal_weights.copy()

    # Nominal background histogram
    bkg_hist_nominal, bkg_bins = np.histogram(
        selected_bkg_scores,
        bins=n_bins[BDT_var],
        range=(0, 1),
        weights=selected_bkg_nominal_weights,
    )

    bkg_sumw2_nominal, _ = np.histogram(
        selected_bkg_scores,
        bins=n_bins[BDT_var],
        range=(0, 1),
        weights=selected_bkg_nominal_weights**2,
    )

    bkg_error_nominal = np.sqrt(bkg_sumw2_nominal)

    # Reweighted background histogram
    bkg_hist_reweighted, _ = np.histogram(
        selected_bkg_scores,
        bins=n_bins[BDT_var],
        range=(0, 1),
        weights=selected_bkg_reweighted_weights,
    )

    bkg_sumw2_reweighted, _ = np.histogram(
        selected_bkg_scores,
        bins=n_bins[BDT_var],
        range=(0, 1),
        weights=selected_bkg_reweighted_weights**2,
    )

    bkg_error_reweighted = np.sqrt(bkg_sumw2_reweighted)

    # Data sideband histogram
    if draw_data:
        data_bool_list = get_sideband_mask(data_branches)

        data_weights = np.asarray(
            data_branches["weight"][data_bool_list], dtype=np.float64
        )

        data_hist, data_bins = np.histogram(
            data_branches[BDT_var][data_bool_list],
            bins=n_bins[BDT_var],
            range=(0, 1),
            weights=data_weights,
        )

        data_sumw2, _ = np.histogram(
            data_branches[BDT_var][data_bool_list],
            bins=n_bins[BDT_var],
            range=(0, 1),
            weights=data_weights**2,
        )

        data_error = np.sqrt(data_sumw2)

    # Signal histogram
    print("BDT bins:", n_bins[BDT_var])

    signal_bool_list = (
        (signal_branches[diMuon_mass_name] > 110)
        & (signal_branches[diMuon_mass_name] < 150)
        & (signal_branches["is_" + channel_US + "_category"] == 1)
    )

    selected_signal_scores = signal_branches[BDT_var][signal_bool_list]

    selected_signal_weights = signal_branches["weight"][signal_bool_list]

    signal_hist, signal_bins = np.histogram(
        selected_signal_scores,
        bins=n_bins[BDT_var],
        range=(0, 1),
        weights=selected_signal_weights,
    )

    signal_sumw2, _ = np.histogram(
        selected_signal_scores,
        bins=n_bins[BDT_var],
        range=(0, 1),
        weights=selected_signal_weights**2,
    )

    signal_error = np.sqrt(signal_sumw2)

    # Normalize shapes

    bkg_total_nominal = np.sum(bkg_hist_nominal)
    bkg_total_reweighted = np.sum(bkg_hist_reweighted)
    signal_total = np.sum(signal_hist)

    if bkg_total_nominal != 0:
        bkg_norm_nominal = bkg_hist_nominal / bkg_total_nominal
        bkg_error_norm_nominal = bkg_error_nominal / abs(bkg_total_nominal)
    else:
        bkg_norm_nominal = np.zeros_like(bkg_hist_nominal, dtype=np.float64)
        bkg_error_norm_nominal = np.zeros_like(bkg_hist_nominal, dtype=np.float64)

    if bkg_total_reweighted != 0:
        bkg_norm_reweighted = bkg_hist_reweighted / bkg_total_reweighted
        bkg_error_norm_reweighted = bkg_error_reweighted / abs(bkg_total_reweighted)
    else:
        bkg_norm_reweighted = np.zeros_like(bkg_hist_reweighted, dtype=np.float64)
        bkg_error_norm_reweighted = np.zeros_like(bkg_hist_reweighted, dtype=np.float64)

    signal_norm = signal_hist / signal_total
    signal_error_norm = signal_error / abs(signal_total)
    bkg_centers = 0.5 * (bkg_bins[:-1] + bkg_bins[1:])
    signal_centers = 0.5 * (signal_bins[:-1] + signal_bins[1:])

    # Plot normalized BDT distributions

    fig, axs = get_canvas(True)

    # Nominal background MC: red solid
    hep.histplot(
        bkg_norm_nominal,
        bkg_bins,
        label="Background MC",
        ax=axs[0],
        stack=True,
        linewidth=2,
        color="red",
        linestyle="-",
    )

    axs[0].errorbar(
        bkg_centers,
        bkg_norm_nominal,
        yerr=bkg_error_norm_nominal,
        fmt="none",
        color="red",
        linewidth=1,
        capsize=2,
    )

    # Reweighted background MC: same red, dashed
    if USE_BDT_REWEIGHTING:
        hep.histplot(
            bkg_norm_reweighted,
            bkg_bins,
            label="Background MC reweighted",
            ax=axs[0],
            linewidth=2,
            color="red",
            linestyle="--",
        )

    # Data sidebands
    if draw_data:
        data_total = np.sum(data_hist)
        data_norm = data_hist / data_total
        data_error_norm = data_error / data_total
        data_centers = 0.5 * (data_bins[:-1] + data_bins[1:])
        axs[0].errorbar(
            data_centers,
            data_norm,
            yerr=data_error_norm,
            xerr=0.5 * np.diff(data_bins),
            fmt="o",
            label="Data sidebands",
            color="black",
            markersize=4,
            linewidth=1,
            capsize=2,
        )

    # Signal
    hep.histplot(
        signal_norm,
        signal_bins,
        label="Signal",
        color="blue",
        linewidth=2,
        ax=axs[0],
    )

    axs[0].errorbar(
        signal_centers,
        signal_norm,
        yerr=signal_error_norm,
        fmt="none",
        color="blue",
        linewidth=1,
        capsize=2,
    )

    hep.cms.label(
        data="True",
        label="",
        com="13.6",
        ax=axs[0],
    )

    max_height = max(
        np.max(bkg_norm_nominal + bkg_error_norm_nominal),
        np.max(bkg_norm_reweighted + bkg_error_norm_reweighted),
        np.max(signal_norm + signal_error_norm),
    )

    if draw_data:
        max_height = max(
            max_height,
            np.max(data_norm + data_error_norm),
        )

    if log_y:
        axs[0].set_yscale("log")
        axs[0].set_ylim(1e-7, 10 * max_height)
    else:
        axs[0].set_ylim(0.0, 1.3 * max_height)

    axs[0].set_xlim(signal_bins[0], signal_bins[-1])

    axs[0].set_ylabel(r"Events/ Total events", loc="center")

    axs[0].legend(frameon=False, loc="upper right")

    # Significance in final categories
    signal = []
    bkg_sqrt = []

    for category in range(len(bdt_categories) - 1):
        if category != 0:
            axs[0].axvline(
                x=bdt_categories[category],
                color="grey",
                linestyle="--",
                alpha=0.5,
            )

        signal_events = get_weighted_yield(
            signal_sample,
            bdt_categories[category],
            bdt_categories[category + 1],
        )

        # bkg_sample already contains nominal_weight * BDT_weight.
        bkg_events = get_weighted_yield(
            bkg_sample,
            bdt_categories[category],
            bdt_categories[category + 1],
        )

        signal.append(signal_events)
        bkg_sqrt.append(math.sqrt(bkg_events) if bkg_events > 0 else 0.0)

    ratio_hist, ratio_error = get_histograms_ratio(
        np.array(signal),
        np.array(bkg_sqrt),
    )

    hep.histplot(
        ratio_hist,
        bdt_categories,
        yerr=ratio_error,
        xerr=True,
        histtype="errorbar",
        color="black",
        ax=axs[1],
    )

    print(ratio_hist)

    axs[1].set_ylabel(r"S/$\sqrt{B}$", loc="center")
    axs[1].set_ylim(0.0, 2.0)
    axs[1].set_xlim(signal_bins[0], signal_bins[-1])
    axs[1].set_xlabel(x_labels[BDT_var])

    output_directory = "../plots/" + channel_US + "_category/" + "BDT_categories_data/"
    save_name = "BDT_output_" + era + "_" + subset_title
    save_figure(fig, output_directory, save_name)
    plt.close(fig)


for era in eras:
    draw_bdt_categories(era)
