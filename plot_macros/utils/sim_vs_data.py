import os

import awkward as ak
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import uproot as ur

from .colors import get_color_list, signal_colors
from .helper import (
    clean_null_values,
    get_canvas,
    get_histograms_ratio,
    get_output_directory,
    save_figure,
)
from .labels import (
    background_labels,
    luminosity,
    n_bins,  # , y_labels
    variables_type,
    x_labels,
    x_range,
)


def get_background_label_list(background_sources):
    labels_list = []
    for source in background_sources:
        labels_list.append(background_labels[source])
    return labels_list


def _join_cuts(cuts):
    if not cuts:
        return None
    return " & ".join(f"({cut})" for cut in cuts)


def _mass_variable(variable):
    # BDT scores are trained/categorized on the bs-constrained mass
    if "bsConstrained" in variable or variable.startswith("BDT"):
        return "diMuon_bsConstrainedMass"
    return "diMuon_mass"


def _mass_window_cuts(variable, Z_study, veto_signal_region):
    mass = _mass_variable(variable)
    cuts = []
    if veto_signal_region:
        cuts.append(f"({mass} > 130) | ({mass} < 120)")
    if not Z_study:
        cuts.append(f"({mass} > 110) & ({mass} < 150)")
    return cuts


def fill_histograms(groups):
    # Read each file and apply each distinct cut once per chunk.
    for (path, cut, weight_mode, era_reweight), histograms in groups.items():
        expressions = list(dict.fromkeys(variable for variable, _, _ in histograms))
        if weight_mode is not None:
            expressions.append("weight")
            if not weight_mode:
                expressions.append("pileup_weight")

        for branches in ur.iterate(
            path,
            expressions=list(dict.fromkeys(expressions)),
            cut=cut,
            library="np",
            step_size="500 MB",
        ):
            weights = None
            if weight_mode is not None:
                weights = (
                    branches["weight"] * era_reweight
                    if weight_mode
                    else branches["weight"] / branches["pileup_weight"]
                )

            for variable, bins, histogram in histograms:
                values = {variable: branches[variable]}
                if weights is not None:
                    values["_histogram_weight"] = weights
                clean_null_values(values, list(values), variables_type)
                x = values[variable]
                if "delta_phi" in variable:
                    x = np.abs(x)
                histogram += np.histogram(
                    x, bins=bins, weights=values.get("_histogram_weight")
                )[0]


def get_histograms_from_tuple(
    sources,
    era,
    variables,
    is_background,
    use_puweight,
    production_channel,
    bdt_cuts=[],
    bdt_subset="",
    bdt_dir_suffix="",
    lumi_rescale=False,
    Z_study=False,
    jet_pT_study=False,
    version="2.0.0",
    *,
    groups=None,
):

    # Do NOT modify the original variables list
    variables = list(dict.fromkeys(variables))

    variable = variables[0]

    # ------------------------------------------------------------
    # Histogram configuration
    # ------------------------------------------------------------

    variable_bin = variable

    if variable_bin + "_" + production_channel in x_range:
        variable_bin += "_" + production_channel

    if variable in ["diMuon_mass", "diMuon_bsConstrainedMass"] and Z_study:
        number_of_bins = 80
        x_range_histos = (85, 100)
    else:
        number_of_bins = n_bins[variable_bin]
        x_range_histos = x_range[variable_bin]

    user = os.getenv("USER")

    tuple_version = f"tuples_v{version}"

    analyzer_version = ".".join(version.split(".")[:2])
    analyzer_version = f"analyzer_HiggsMuMu_v{analyzer_version}"

    tuple_path = (
        f"/eos/uscms/store/group/lpchmumu/{user}/"
        f"{analyzer_version}/{tuple_version}/haddTuples/"
    )

    if bdt_subset != "" or variable == "BDT_" + production_channel:
        tuple_path = (
            "../root_io/tuples/"
            f"BDT_score/{production_channel}{bdt_dir_suffix}/{bdt_subset}/"
        )

    # ------------------------------------------------------------
    # Build event selection ONCE
    # ------------------------------------------------------------

    cuts = []

    # Mass window: background on the same sidebands as data, signal on the full 110-150 window
    if variable != _mass_variable(variable):
        cuts += _mass_window_cuts(variable, Z_study, veto_signal_region=is_background)

    # Production category
    if production_channel != "":
        cuts.append(f"is_{production_channel}_category == 1")

    # BDT selection
    if len(bdt_cuts) > 1:
        cuts.append(
            f"(BDT_{production_channel} > {bdt_cuts[0]}) & "
            f"(BDT_{production_channel} < {bdt_cuts[1]})"
        )

    # Jet eta selection
    if ("jet_pt" in variable) and jet_pT_study:
        eta_var = variable.split("_")[0] + "_jet_eta"

        cuts.append(f"({eta_var} >= 2.5) & ({eta_var} < 3)")

    cut = _join_cuts(cuts)

    histogram_groups = {} if groups is None else groups

    histograms_list = []
    bins_list = []

    era_reweight = 1.0

    if lumi_rescale:
        if era == "2025":
            era_reweight = float(luminosity["2025"]) / (
                float(luminosity["2025"]) + float(luminosity["2026"])
            )
            print("Re scaling lumi")
        if era == "2026":
            # era_reweight = float(luminosity["2026"]) / (float(luminosity["2025"]) + float(luminosity["2026"]))
            era_reweight = 25.8433 / (
                float(luminosity["2025"]) + float(luminosity["2026"])
            )
            era = "2025"
            print("Re scaling lumi")
    for source in sources:

        if bdt_subset != "" or variable == "BDT_" + production_channel:

            file_name = f"{source}_{era}_{bdt_subset}.root:tree_output"

        else:

            file_name = f"{source}_{era}_tuples.root:tree_output"

        histogram = np.zeros(
            number_of_bins,
            dtype=np.float64,
        )

        bins = np.linspace(
            x_range_histos[0],
            x_range_histos[1],
            number_of_bins + 1,
        )

        key = (tuple_path + file_name, cut, bool(use_puweight), era_reweight)
        histogram_groups.setdefault(key, []).append((variable, bins, histogram))
        histograms_list.append(histogram)
        bins_list.append(bins)

    if groups is None:
        fill_histograms(histogram_groups)

    return histograms_list, bins_list


def get_data_histograms_from_tuple(
    era,
    variables,
    production_channel,
    bdt_cuts,
    bdt_subset="",
    bdt_dir_suffix="",
    Z_study=False,
    jet_pT_study=False,
    version="2.0.0",
    *,
    groups=None,
):

    variable = variables[0]

    user = os.getenv("USER")
    tuple_version = f"tuples_v{version}"

    analyzer_version = ".".join(version.split(".")[:2])
    analyzer_version = f"analyzer_HiggsMuMu_v{analyzer_version}"

    tuple_path = (
        f"/eos/uscms/store/group/lpchmumu/{user}/"
        f"{analyzer_version}/{tuple_version}/haddTuples/"
    )

    file_name = f"Data_{era}_tuples.root:tree_output"

    if bdt_subset != "" or variable == "BDT_" + production_channel:

        tuple_path = (
            "../root_io/tuples/"
            f"BDT_score/{production_channel}{bdt_dir_suffix}/{bdt_subset}/"
        )

        file_name = f"Data_{era}_{bdt_subset}.root:tree_output"

    variable_bin = variable

    if variable_bin + "_" + production_channel in x_range:
        variable_bin += "_" + production_channel

    if variable in ["diMuon_mass", "diMuon_bsConstrainedMass"] and Z_study:

        number_of_bins = 80
        x_range_histos = (85, 100)

    else:

        number_of_bins = n_bins[variable_bin]
        x_range_histos = x_range[variable_bin]

    bins = np.linspace(
        x_range_histos[0],
        x_range_histos[1],
        number_of_bins + 1,
    )

    data_histogram = np.zeros(
        number_of_bins,
        dtype=np.float64,
    )

    cuts = _mass_window_cuts(variable, Z_study, veto_signal_region=True)

    if production_channel != "":
        cuts.append(f"is_{production_channel}_category == 1")

    if len(bdt_cuts) > 1:

        cuts.append(
            f"(BDT_{production_channel} > {bdt_cuts[0]}) & "
            f"(BDT_{production_channel} < {bdt_cuts[1]})"
        )

    if ("jet_pt" in variable) and jet_pT_study:

        eta_var = variable.split("_")[0] + "_jet_eta"

        cuts.append(f"({eta_var} >= 2.5) & ({eta_var} < 3)")

    cut = _join_cuts(cuts)

    histogram_groups = {} if groups is None else groups
    key = (tuple_path + file_name, cut, None, 1.0)
    histogram_groups.setdefault(key, []).append((variable, bins, data_histogram))
    if groups is None:
        fill_histograms(histogram_groups)

    return data_histogram, bins


def _draw_normalized_shapes(
    data_histogram,
    data_bins,
    bkg_histograms_list,
    tot_bg_numpy_hist,
    signal_histograms_list,
    background_sources,
    signal_sources,
    era,
    label,
    info_text,
    category_boundaries,
    x_label,
    ratio_ylabel,
    output_directory,
    output_name,
):
    # Data as raw counts
    data_sum = np.sum(data_histogram)

    data_shape = data_histogram
    data_shape_error = np.sqrt(data_histogram)
    bkg_shapes = bkg_histograms_list
    signal_shapes = [h * data_sum / np.sum(h) for h in signal_histograms_list]

    fig, axs = get_canvas(True)

    hep.histplot(
        bkg_shapes,
        data_bins,
        histtype="fill",
        label=get_background_label_list(background_sources),
        ax=axs[0],
        stack=True,
        color=get_color_list(len(background_sources)),
    )
    hep.histplot(
        data_shape,
        data_bins,
        yerr=data_shape_error,
        histtype="errorbar",
        label="Data",
        color="black",
        ax=axs[0],
    )
    for source, shape in zip(signal_sources, signal_shapes):
        hep.histplot(
            shape,
            data_bins,
            yerr=False,
            label=source + " (norm. to data)",
            color=signal_colors[source],
            ax=axs[0],
        )

    hep.cms.label(
        data="True", label=label, year=era, com="13.6", lumi=luminosity[era], ax=axs[0]
    )

    if category_boundaries is not None:
        for boundary in category_boundaries:
            if data_bins[0] < boundary < data_bins[-1]:
                for ax in axs:
                    ax.axvline(boundary, color="grey", linestyle="--", alpha=0.7)

    axs[0].set_ylabel("Events")
    axs[0].set_xlim(data_bins[0], data_bins[-1])
    axs[0].legend(
        frameon=False,
        loc="upper right",
        ncols=2,
        title=info_text,
        title_fontsize=18,
        alignment="left",
    )
    axs[0].tick_params(axis="x", which="both", bottom=True, top=True, labelbottom=False)

    ratio_hist, ratio_error = get_histograms_ratio(data_histogram, tot_bg_numpy_hist)
    hep.histplot(
        ratio_hist,
        data_bins,
        yerr=ratio_error,
        histtype="errorbar",
        color="black",
        ax=axs[1],
    )
    axs[1].axhline(y=1, color="grey", linestyle="--", alpha=0.5)
    axs[1].set_ylabel(ratio_ylabel, loc="center")
    axs[1].set_ylim(0.5, 1.5)
    axs[1].set_xlim(data_bins[0], data_bins[-1])
    axs[1].set_xlabel(x_label)

    y_max = max(
        np.max(data_shape),
        np.max(tot_bg_numpy_hist),
        max(np.max(s) for s in signal_shapes),
    )
    axs[0].set_yscale("log")
    axs[0].set_ylim(1e-4 * y_max, 3e4 * y_max)
    save_figure(fig, output_directory, output_name)

    axs[0].set_yscale("linear")
    axs[0].set_ylim(0, 2.2 * y_max)
    save_figure(fig, output_directory, output_name + "_linear")

    plt.close()


def read_plot_histograms(
    variables,
    era,
    background_sources,
    signal_sources,
    use_puweight=True,
    production_channel="",
    bdt_cuts=(),
    bdt_subset="",
    bdt_dir_suffix="",
    Z_study=False,
    jet_pT_study=False,
    version="2.0.0",
):
    groups = {}
    histograms = {}
    options = dict(
        bdt_dir_suffix=bdt_dir_suffix,
        Z_study=Z_study,
        jet_pT_study=jet_pT_study,
        version=version,
        groups=groups,
    )
    for variable in dict.fromkeys(variables):
        data = get_data_histograms_from_tuple(
            era, [variable], production_channel, bdt_cuts, bdt_subset, **options
        )
        simulation = [
            get_histograms_from_tuple(
                sources,
                era,
                [variable],
                is_background,
                use_puweight,
                production_channel,
                bdt_cuts,
                bdt_subset,
                lumi_rescale=era in ("2025", "2026"),
                **options,
            )
            for sources, is_background in (
                (background_sources, True),
                (signal_sources, False),
            )
        ]
        histograms[variable] = (data, *simulation)
    fill_histograms(groups)
    return histograms


def draw_data_and_simul_and_ratio(
    variable,
    era,
    background_sources,
    signal_sources,
    use_puweight=True,
    production_channel="",
    bdt_cuts=[],
    bdt_subset="",
    bdt_dir_suffix="",
    Z_study=False,
    jet_pT_study=False,
    version="2.0.0",
    category_boundaries=None,
    *,
    histograms=None,
):
    plt.style.use(hep.style.CMS)
    tuple_version = f"tuples_v{version}"
    print("*" * len("****** PLOTTING " + variable + era + " *****"))
    print("****** PLOTTING " + variable + " ERA " + era + " *****")
    print("*" * len("****** PLOTTING " + variable + era + " *****"))

    labelAdd = (
        "inHorn"
        if jet_pT_study and variable in ("leading_jet_pt", "subleading_jet_pt")
        else ""
    )
    if histograms is None:
        histograms = read_plot_histograms(
            [variable],
            era,
            background_sources,
            signal_sources,
            use_puweight,
            production_channel,
            bdt_cuts,
            bdt_subset,
            bdt_dir_suffix,
            Z_study,
            jet_pT_study,
            version,
        )[variable]
    (
        (data_histogram, data_bins),
        (bkg_histograms_list, bkg_bins_list),
        (
            signal_histograms_list,
            signal_bins_list,
        ),
    ) = histograms

    if variable == "diMuon_mass" or variable == "diMuon_bsConstrainedMass":
        data_histogram = data_histogram.copy()
        data_histogram[data_histogram == 0] = -100.0

    fig, axs = get_canvas(True)

    hep.histplot(
        bkg_histograms_list,
        bkg_bins_list[0],
        yerr=True,
        histtype="fill",
        label=get_background_label_list(background_sources),
        ax=axs[0],
        stack=True,
        color=get_color_list(len(background_sources)),
    )

    hep.histplot(
        data_histogram,
        data_bins,
        yerr=True,
        histtype="errorbar",
        label="Data",
        color="black",
        ax=axs[0],
    )

    signal_scale_factor = 10
    for source, histogram in zip(signal_sources, signal_histograms_list):
        hep.histplot(
            histogram * signal_scale_factor,
            signal_bins_list[0],
            yerr=False,
            # yerr=True,
            label=source + " (x" + str(signal_scale_factor) + ")",
            color=signal_colors[source],
            ax=axs[0],
        )

    label = ""
    if not use_puweight:
        label = "No PU weight"
    if len(bdt_cuts) > 1:
        label = "Cat" + str(len(bdt_cuts) - 1)
    hep.cms.label(
        data="True",
        label=label,
        year=era,
        com="13.6",
        lumi=luminosity[era],
        ax=axs[0],
    )

    info_text = production_channel + " category" if production_channel != "" else None

    if category_boundaries is not None:
        for boundary in category_boundaries:
            if data_bins[0] < boundary < data_bins[-1]:
                for ax in axs:
                    ax.axvline(boundary, color="grey", linestyle="--", alpha=0.7)

    axs[0].set_ylabel(r"Events")
    axs[0].set_ylim(0.1, 1000 * np.max(data_histogram))
    axs[0].set_xlim(data_bins[0], data_bins[-1])
    axs[0].set_yscale("log")
    legend = axs[0].legend(
        frameon=False,
        loc="upper right",
        ncols=2,
        title=info_text,
        title_fontsize=18,
        alignment="left",
    )
    axs[0].tick_params(axis="x", which="both", bottom=True, top=True, labelbottom=False)

    plt.axhline(y=1, color="grey", linestyle="--", alpha=0.5)

    tot_bg_numpy_hist = np.array([])
    for i, bg_hist in enumerate(bkg_histograms_list):
        if i == 0:
            tot_bg_numpy_hist = bg_hist
        else:
            tot_bg_numpy_hist = tot_bg_numpy_hist + bg_hist

    ratio_hist, ratio_error = get_histograms_ratio(data_histogram, tot_bg_numpy_hist)
    # print("Total event ratio D/B: " + str(np.sum(data_histogram) / np.sum(tot_bg_numpy_hist)))

    hep.histplot(
        ratio_hist,
        data_bins,
        yerr=ratio_error,
        histtype="errorbar",
        label="data",
        color="black",
        ax=axs[1],
    )

    if era == "2025":
        axs[1].set_ylabel("Data/MC(2024)", loc="center")
    elif era == "Combined":
        axs[1].set_ylabel("Data/MC(pre25)", loc="center")
    else:
        axs[1].set_ylabel("Data/MC", loc="center")
    axs[1].set_ylim(0.5, 1.5)
    axs[1].set_xlim(data_bins[0], data_bins[-1])
    axs[1].set_xlabel(x_labels[variable])

    output_directory = f"../plots/ratio/{tuple_version}/" + era + "/"
    output_name = variable + "_" + era + "_MCData_ratio"
    if Z_study:
        output_name = variable + "_Z_included_" + era + "_MCData_ratio"

    if not use_puweight:
        output_directory = f"../plots/ratio/{tuple_version}/" + era + "/no_puWeight/"
    if production_channel != "":
        output_directory = (
            f"../plots/ratio/{tuple_version}/"
            + production_channel
            + bdt_dir_suffix
            + "_category/"
            + era
            + "/"
        )

        if len(bdt_cuts) > 1:
            output_directory = (
                f"../plots/ratio/{tuple_version}/"
                + production_channel
                + bdt_dir_suffix
                + "_category/bdt_selections/"
                + era
                + "/"
            )

    output_directory = get_output_directory(variable, output_directory, variables_type)

    save_figure(fig, output_directory, output_name + label + labelAdd)

    # BDT scores: also save a linear-y version, with headroom for the legend
    if variable.startswith("BDT"):
        y_max = max(
            np.max(data_histogram),
            np.max(tot_bg_numpy_hist),
            signal_scale_factor * max(np.max(h) for h in signal_histograms_list),
        )
        axs[0].set_yscale("linear")
        axs[0].set_ylim(0, 2.2 * y_max)
        save_figure(fig, output_directory, output_name + label + labelAdd + "_linear")

    plt.close()

    if variable.startswith("BDT"):
        _draw_normalized_shapes(
            data_histogram,
            data_bins,
            bkg_histograms_list,
            tot_bg_numpy_hist,
            signal_histograms_list,
            background_sources,
            signal_sources,
            era,
            label,
            info_text,
            category_boundaries,
            x_labels[variable],
            axs[1].get_ylabel(),
            output_directory,
            output_name + label + labelAdd + "_normalized",
        )

    if len(bdt_cuts) > 2:
        draw_data_and_simul_and_ratio(
            variable,
            era,
            background_sources,
            signal_sources,
            use_puweight=use_puweight,
            production_channel=production_channel,
            bdt_cuts=bdt_cuts[1:],
            bdt_subset=bdt_subset,
            bdt_dir_suffix=bdt_dir_suffix,
            Z_study=Z_study,
            jet_pT_study=jet_pT_study,
            version=version,
        )
