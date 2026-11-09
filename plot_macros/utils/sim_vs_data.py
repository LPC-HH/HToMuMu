import uproot as ur
import mplhep as hep
import numpy as np
import matplotlib.pyplot as plt
import awkward as ak
import os

from .labels import (
    x_labels,
    background_labels,
    luminosity,
    x_range,
    n_bins,
    variables_type,
)  # , y_labels
from .helper import (
    get_canvas,
    save_figure,
    get_histograms_ratio,
    get_output_directory,
    clean_null_values,
)
from .colors import(
    signal_colors,
    get_color_list,
)

def get_background_label_list(background_sources):
    labels_list = []
    for source in background_sources:
        labels_list.append(background_labels[source])
    return labels_list


# def get_histograms_from_tuple(
    # sources,
    # era,
    # variables,
    # is_background,
    # use_puweight,
    # production_channel,
    # bdt_cuts=[],
    # bdt_subset="",
    # lumi_rescale=False,
    # Z_study=False,
    # jet_pT_study=False,
    # version="2.0.0",
# ):
    
    # if not use_puweight:
        # variables.append("pileup_weight")
    # # variables.append("pileup_weight")
    # # variables.append("pileup_weight_down")


    # histograms_list = []
    # bins_list = []

    # # For 2025 data there is not simulations yet!!!
    # # so in the case we re escale the luminosity
    # era_reweight = 1
    # # if lumi_rescale:
        # # if era == "2024":
            # # era_reweight = float(luminosity["2024"]) / (float(luminosity["2024"]) + float(luminosity["2025"]))
            # # print("Re scaling lumi")
        # # if era == "2025":
            # # era_reweight = float(luminosity["2025"]) / (float(luminosity["2024"]) + float(luminosity["2025"]))
            # # era = "2024"
            # # print("Re scaling lumi")

    # variable_bin = variables[0]

    # if variable_bin + "_" + production_channel in x_range:
        # variable_bin += "_" + production_channel

    # # tuple_path = "../root_io/tuples/"
    # user = os.getenv("USER")
    # tuple_version = f"tuples_v{version}"
    # analyzer_version = ".".join(version.split(".")[:2])
    # analyzer_version = f"analyzer_HiggsMuMu_v{analyzer_version}"

    # tuple_path = (
        # f"/eos/uscms/store/group/lpchmumu/{user}/"
        # f"{analyzer_version}/{tuple_version}/haddTuples/"
    # )
    # if bdt_subset != "" or variables[0] == "BDT_" + production_channel:
        # tuple_path = "../root_io/tuples/"
        # tuple_path += "BDT_score/" + production_channel + "/" + bdt_subset + "/"

    # for source in sources:
        # file_name = source + "_" + era + "_tuples.root:tree_output"
        # if bdt_subset != "" or variables[0] == "BDT_" + production_channel:
            # file_name = source + "_" + era + "_" + bdt_subset + ".root:tree_output"

        # if ((variables[0] == "diMuon_mass") | (variables[0] == "diMuon_bsConstrainedMass")) and Z_study:
                # number_of_bins = 80; 
                # x_range_histos = (85,100)
        # else:
            # number_of_bins = n_bins[variable_bin]
            # x_range_histos = x_range[variable_bin]

        # histogram, bins = np.histogram(
                # [],
                # bins=number_of_bins,
                # range=x_range_histos,
        # )

        # for branches in ur.iterate(tuple_path + file_name, variables, library="np", step_size="500 MB"):
            # #print("TUPLE PATH in get Hist from tup_____: " + tuple_path)
            # bool_list = np.ones(len(branches[variables[0]]), dtype=bool)

            # if variables[0] != "diMuon_bsConstrainedMass" and ("bsConstrained" in variables[0]) and is_background:
                # bool_list = (bool_list) & (branches["diMuon_bsConstrainedMass"] > 130) | (
                    # branches["diMuon_bsConstrainedMass"] < 120
                # )
                # if not Z_study:
                    # bool_list = (bool_list) & (branches["diMuon_bsConstrainedMass"] > 110) & (
                        # branches["diMuon_bsConstrainedMass"] < 150
                    # )


            # elif variables[0] != "diMuon_mass" and ("bsConstrained" not in variables[0]) and is_background:
                # bool_list = (bool_list) & (
                    # ((branches["diMuon_mass"] > 130) | (branches["diMuon_mass"] < 120))
                # )
                # if not Z_study:
                    # bool_list = (bool_list) & (branches["diMuon_mass"] > 110) & (
                        # branches["diMuon_mass"] < 150
                    # )

            # if production_channel != "":
                # bool_list = (bool_list) & (
                    # branches["is_" + production_channel + "_category"] == 1
                # )

            # if len(bdt_cuts) > 1:
                # bdt_bool = (branches["BDT_" + production_channel] > bdt_cuts[0]) & (
                    # branches["BDT_" + production_channel] < bdt_cuts[1]
                # )
                # bool_list = (bool_list) & (bdt_bool)

            # if ("jet_pt" in variables[0]) and jet_pT_study:
                # etaVar = variables[0].split("_")[0] + "_jet_eta"
                # bool_list = (bool_list) & (branches[etaVar] >= 2.5) & (branches[etaVar] < 3)

            # for var in variables:
                # branches[var] = branches[var][bool_list]

            # clean_null_values(branches, variables, variables_type)

            # if "delta_phi" in variables[0]:
                # branches[variables[0]] = np.absolute(branches[variables[0]])

            # TempHistogram, bins = np.histogram(
                # branches[variables[0]],
                # bins=number_of_bins,
                # range=x_range_histos,
                # weights=(
                    # branches["weight"] * era_reweight
                    # # branches["weight"] * (branches["pileup_weight_down"] / branches["pileup_weight"])
                    # if use_puweight
                    # else branches["weight"] / branches["pileup_weight"]
                # ),
            # )
            # x = branches[variables[0]]
            # w = branches["weight"]

            # histogram = histogram + TempHistogram
        # histograms_list.append(histogram)
        # bins_list.append(bins)

    # return histograms_list, bins_list


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

    if (
        variable in ["diMuon_mass", "diMuon_bsConstrainedMass"]
        and Z_study
    ):
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
        cuts.append(
            f"is_{production_channel}_category == 1"
        )

    # BDT selection
    if len(bdt_cuts) > 1:
        cuts.append(
            f"(BDT_{production_channel} > {bdt_cuts[0]}) & "
            f"(BDT_{production_channel} < {bdt_cuts[1]})"
        )

    # Jet eta selection
    if ("jet_pt" in variable) and jet_pT_study:
        eta_var = variable.split("_")[0] + "_jet_eta"

        cuts.append(
            f"({eta_var} >= 2.5) & ({eta_var} < 3)"
        )

    cut = _join_cuts(cuts)

    # ------------------------------------------------------------
    # Only return branches actually needed by histogram
    # ------------------------------------------------------------

    read_variables = [variable, "weight"]

    if not use_puweight:
        read_variables.append("pileup_weight")

    read_variables = list(dict.fromkeys(read_variables))

    # ------------------------------------------------------------
    # Loop over samples
    # ------------------------------------------------------------

    histograms_list = []
    bins_list = []

    era_reweight = 1.0

    if lumi_rescale:
        if era == "2025":
            era_reweight = float(luminosity["2025"]) / (float(luminosity["2025"]) + float(luminosity["2026"]))
            print("Re scaling lumi")
        if era == "2026":
            #era_reweight = float(luminosity["2026"]) / (float(luminosity["2025"]) + float(luminosity["2026"]))
            era_reweight = 25.8433 / (float(luminosity["2025"]) + float(luminosity["2026"]))
            era = "2025"
            print("Re scaling lumi")
    for source in sources:

        if bdt_subset != "" or variable == "BDT_" + production_channel:

            file_name = (
                f"{source}_{era}_{bdt_subset}.root:tree_output"
            )

        else:

            file_name = (
                f"{source}_{era}_tuples.root:tree_output"
            )

        histogram = np.zeros(
            number_of_bins,
            dtype=np.float64,
        )

        bins = np.linspace(
            x_range_histos[0],
            x_range_histos[1],
            number_of_bins + 1,
        )

        # --------------------------------------------------------
        # Uproot now performs the event selection
        # --------------------------------------------------------

        for branches in ur.iterate(
            tuple_path + file_name,
            expressions=read_variables,
            cut=cut,
            library="np",
            step_size="500 MB",
        ):

            # Only clean the arrays we actually need
            clean_null_values(
                branches,
                read_variables,
                variables_type,
            )

            x = branches[variable]

            if "delta_phi" in variable:
                x = np.abs(x)

            if use_puweight:

                weights = (
                    branches["weight"]
                    * era_reweight
                )

            else:

                weights = (
                    branches["weight"]
                    / branches["pileup_weight"]
                )

            histogram += np.histogram(
                x,
                bins=bins,
                weights=weights,
            )[0]

        histograms_list.append(histogram)
        bins_list.append(bins)

    return histograms_list, bins_list



# def get_data_histograms_from_tuple(
    # era,
    # variables,
    # production_channel,
    # bdt_cuts,
    # bdt_subset="",
    # Z_study=False,
    # jet_pT_study=False,
    # version="2.0.0",
# ):
    # # tuple_path = "../root_io/tuples/"
    # user = os.getenv("USER")
    # tuple_version = f"tuples_v{version}"
    # analyzer_version = ".".join(version.split(".")[:2])
    # analyzer_version = f"analyzer_HiggsMuMu_v{analyzer_version}"

    # tuple_path = (
        # f"/eos/uscms/store/group/lpchmumu/{user}/"
        # f"{analyzer_version}/{tuple_version}/haddTuples/"
    # )
    # file_name = "Data_" + era + "_tuples.root:tree_output"
    # if bdt_subset != "" or variables[0] == "BDT_" + production_channel:
        # tuple_path = "../root_io/tuples/"
        # tuple_path += "BDT_score/" + production_channel + "/" + bdt_subset + "/"
        # file_name = "Data_" + era + "_" + bdt_subset + ".root:tree_output"

    # #with ur.open(tuple_path + file_name) as data_file:

    # variable_bin = variables[0]

    # if (( variables[0] == "diMuon_mass") | (variables[0] == "diMuon_bsConstrainedMass")) and Z_study:
            # number_of_bins = 80; 
            # x_range_histos = (85,100)
    # else:
        # number_of_bins = n_bins[variable_bin]
        # x_range_histos = x_range[variable_bin]

    # data_histogram = np.zeros(number_of_bins)

    # for branches in ur.iterate(tuple_path + file_name, variables, step_size=9000000, library="np"):
        # if variable_bin + "_" + production_channel in x_range:
            # variable_bin += "_" + production_channel


        # if "bsConstrained" in variables[0]:
            # bool_list = ((branches["diMuon_bsConstrainedMass"] > 130) | (branches["diMuon_bsConstrainedMass"] < 120))
            # if not Z_study:
                # bool_list = (bool_list) & (branches["diMuon_bsConstrainedMass"] > 110) & (
                    # branches["diMuon_bsConstrainedMass"] < 150
                # )
        # else:
            # bool_list = ((branches["diMuon_mass"] > 130) | (branches["diMuon_mass"] < 120))
            # if not Z_study:
                # bool_list = (bool_list) & (branches["diMuon_mass"] > 110) & (
                    # branches["diMuon_mass"] < 150
                # )
        
        # if production_channel != "":
            # bool_list = (bool_list) & (
                # branches["is_" + production_channel + "_category"] == 1
            # )

        # if len(bdt_cuts) > 1:
            # bdt_bool = (branches["BDT_" + production_channel] > bdt_cuts[0]) & (
                # branches["BDT_" + production_channel] < bdt_cuts[1]
            # )
            # bool_list = (bool_list) & (bdt_bool)

        # if ("jet_pt" in variables[0]) and jet_pT_study:
            # #print("adding jet pt")
            # etaVar = variables[0].split("_")[0] + "_jet_eta"
            # bool_list = (bool_list) & (branches[etaVar] >= 2.5) & (branches[etaVar] < 3)
        

        # for var in variables:
            # branches[var] = branches[var][bool_list]

        # clean_null_values(branches, variables, variables_type)

        # if "delta_phi" in variables[0]:
            # branches[variables[0]] = np.absolute(branches[variables[0]])

        
        # #print("Total number of Data Events: " + str(len(branches[variables[0]])))
        # data_histogram_chunk, data_bins = np.histogram(
            # branches[variables[0]],
            # bins=number_of_bins,
            # range=x_range_histos,
        # )

        # data_histogram += data_histogram_chunk

        # #print("Data events in the first bin: " + str(data_histogram[0]))

    # return data_histogram, data_bins

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
):

    variable = variables[0]

    # ------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------

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

        file_name = (
            f"Data_{era}_{bdt_subset}.root:tree_output"
        )

    # ------------------------------------------------------------
    # Histogram configuration
    # ------------------------------------------------------------

    variable_bin = variable

    if variable_bin + "_" + production_channel in x_range:
        variable_bin += "_" + production_channel

    if (
        variable in ["diMuon_mass", "diMuon_bsConstrainedMass"]
        and Z_study
    ):

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

    # ------------------------------------------------------------
    # Build selection
    # ------------------------------------------------------------

    # Data sidebands / blinding (always applied)
    cuts = _mass_window_cuts(variable, Z_study, veto_signal_region=True)

    if production_channel != "":
        cuts.append(
            f"is_{production_channel}_category == 1"
        )

    if len(bdt_cuts) > 1:

        cuts.append(
            f"(BDT_{production_channel} > {bdt_cuts[0]}) & "
            f"(BDT_{production_channel} < {bdt_cuts[1]})"
        )

    if ("jet_pt" in variable) and jet_pT_study:

        eta_var = variable.split("_")[0] + "_jet_eta"

        cuts.append(
            f"({eta_var} >= 2.5) & ({eta_var} < 3)"
        )

    cut = _join_cuts(cuts)

    # ------------------------------------------------------------
    # Read
    # ------------------------------------------------------------

    for branches in ur.iterate(
        tuple_path + file_name,
        expressions=[variable],
        cut=cut,
        step_size="500 MB",
        library="np",
    ):

        clean_null_values(
            branches,
            [variable],
            variables_type,
        )

        x = branches[variable]

        if "delta_phi" in variable:
            x = np.abs(x)

        data_histogram += np.histogram(
            x,
            bins=bins,
        )[0]

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
    #Data as raw counts
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
            shape, data_bins, yerr=False, label=source + " (norm. to data)", color=signal_colors[source], ax=axs[0]
        )

    hep.cms.label(data="True", label=label, year=era, com="13.6", lumi=luminosity[era], ax=axs[0])

    if category_boundaries is not None:
        for boundary in category_boundaries:
            if data_bins[0] < boundary < data_bins[-1]:
                for ax in axs:
                    ax.axvline(boundary, color="grey", linestyle="--", alpha=0.7)

    axs[0].set_ylabel("Events")
    axs[0].set_xlim(data_bins[0], data_bins[-1])
    axs[0].legend(
        frameon=False, loc="upper right", ncols=2, title=info_text, title_fontsize=18, alignment="left"
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

    y_max = max(np.max(data_shape), np.max(tot_bg_numpy_hist), max(np.max(s) for s in signal_shapes))
    axs[0].set_yscale("log")
    axs[0].set_ylim(1e-4 * y_max, 3e4 * y_max)
    save_figure(fig, output_directory, output_name)

    axs[0].set_yscale("linear")
    axs[0].set_ylim(0, 2.2 * y_max)
    save_figure(fig, output_directory, output_name + "_linear")

    plt.close()


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
):
    plt.style.use(hep.style.CMS)
    tuple_version = f"tuples_v{version}"
    print("*" * len("****** PLOTTING " + variable + era + " *****"))
    print("****** PLOTTING " + variable + " ERA " + era + " *****")
    print("*" * len("****** PLOTTING " + variable + era + " *****"))

    variables = [variable, "weight"] 
    if (("bsConstrained" in variable) and variable != "diMuon_bsConstrainedMass"):
        variables.append("diMuon_bsConstrainedMass")
    elif (variable != "diMuon_mass" and ("bsConstrained" not in variable)):
        variables.append("diMuon_mass")

    etaVar=""
    labelAdd=""
    if(("leading_jet_pt" == variable) and (jet_pT_study)):
        etaVar = "leading_jet_eta"
        variables.append("leading_jet_eta")
        labelAdd="inHorn"
    elif(("subleading_jet_pt" == variable) and jet_pT_study):
        etaVar = "subleading_jet_eta"
        variables.append("subleading_jet_eta")
        labelAdd="inHorn"


    # if variable != "diMuon_mass":
    if production_channel != "":
        variables.append("is_" + production_channel + "_category")
    if len(bdt_cuts) != 0:
        variables.append("BDT_" + production_channel)

    data_histogram, data_bins = get_data_histograms_from_tuple(
        era,
        variables,
        production_channel,
        bdt_cuts,
        bdt_subset,
        bdt_dir_suffix=bdt_dir_suffix,
        Z_study=Z_study,
        jet_pT_study=jet_pT_study,
        version=version,
    )


    if variable == "diMuon_mass" or variable == "diMuon_bsConstrainedMass":
        data_histogram[data_histogram == 0] = -100.0

    bkg_histograms_list, bkg_bins_list = get_histograms_from_tuple(
        background_sources,
        era,
        variables,
        True,
        use_puweight,
        production_channel,
        bdt_cuts,
        bdt_subset,
        bdt_dir_suffix,
        era in ["2026", "2025"],
        Z_study=Z_study,
        jet_pT_study=jet_pT_study,
        version=version,
    )

    signal_histograms_list, signal_bins_list = get_histograms_from_tuple(
        signal_sources,
        era,
        variables,
        False,
        use_puweight,
        production_channel,
        bdt_cuts,
        bdt_subset,
        bdt_dir_suffix,
        era in ["2025", "2026"],
        Z_study=Z_study,
        jet_pT_study=jet_pT_study,
        version=version,
    )

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
        frameon=False, loc="upper right", ncols=2, title=info_text, title_fontsize=18, alignment="left"
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
    #print("Total event ratio D/B: " + str(np.sum(data_histogram) / np.sum(tot_bg_numpy_hist)))

    hep.histplot(
        ratio_hist,
        data_bins,
        yerr=ratio_error,
        histtype="errorbar",
        label="data",
        color="black",
        ax=axs[1],
    )

    if(era == "2025"):
        axs[1].set_ylabel("Data/MC(2024)", loc="center")
    elif(era == "Combined"):
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
            + production_channel + bdt_dir_suffix + "_category/" + era + "/"
        )

        if len(bdt_cuts) > 1:
            output_directory = (
                f"../plots/ratio/{tuple_version}/"
                + production_channel + bdt_dir_suffix + "_category/bdt_selections/" + era + "/"
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

