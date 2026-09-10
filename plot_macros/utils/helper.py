import matplotlib.pyplot as plt
import numpy as np
import uproot as ur
import os


def get_canvas(draw_ratio=False):
    """
    Creates a matplotlib figure and axes for plotting.

    Parameters:
    ----------
    draw_ratio : bool, optional
        If True, creates a figure with two subplots in a vertical layout
        for ratio plots (default is False).

    Returns:
    -------
    fig : matplotlib.figure.Figure
        The created figure for plotting.
    axs : matplotlib.axes.Axes or array of Axes
        The axes for plotting. If draw_ratio is False, a single Axes object
        is returned; otherwise, an array of two Axes objects.
    """
    if draw_ratio:
        fig, axs = plt.subplots(2, 1, height_ratios=[10, 2])
        fig.subplots_adjust(hspace=0.1)
        return fig, axs

    fig, axs = plt.subplots(1, 1)
    return fig, axs


def save_figure(fig, outputDirectory, name):
    """
    Saves a matplotlib figure in PDF and PNG.

    Parameters:
    ----------
    fig : matplotlib.figure.Figure
        The figure to be saved.
    outputDirectory : str
        Directory where the figure will be saved.
    name : str
        The base filename for the saved figure.

    Returns:
    -------
    None
    """

    os.makedirs(outputDirectory, exist_ok=True)
    fig.savefig(outputDirectory + name + ".pdf", bbox_inches="tight")
    fig.savefig(outputDirectory + name + ".png", dpi=300)
    print(outputDirectory + name + " Has been created")


def get_histograms(variable, sources, era):
    """
    Loads histograms from ROOT files using the uproot library.

    Parameters:
    ----------
    variable : str
        The name of the variable or histogram to retrieve.
    sources : list of str
        List of proccess sources (e.g., "DY50to120", "TTto2L2Q", etc) to be loaded.
    era : str
        A string representing the data-taking period ("2022", "2022EE", etc.).

    Returns:
    -------
    histograms : List of ROOT histograms.
    """
    histograms = []
    for source in sources:
        with ur.open("../root_io/" + source + "_" + era + "_histograms.root") as file:
            histograms.append(file[variable])

    return histograms


def get_histograms_ratio(numerator_histogram, denominator_histogram):
    """
    Calculates the ratio of two histograms with error propagation.

    Parameters:
    ----------
    numerator_histogram : numpy.ndarray
        The histogram values for the numerator.
    denominator_histogram : numpy.ndarray
        The histogram values for the denominator.

    Returns:
    -------
    ratio : numpy.ndarray
        Numpy array with the ratio of the two histograms.
    error : numpy.ndarray
        Numpy array with the erros of ratio of the two histograms.

    Notes:
    ------
    If any elements in the denominator are zero, they are excluded from the calculation.
    """
    ratio = np.divide(
        numerator_histogram, denominator_histogram, where=(denominator_histogram != 0)
    )
    error = np.divide(
        numerator_histogram * np.sqrt(denominator_histogram)
        + denominator_histogram * np.sqrt(numerator_histogram),
        np.power(denominator_histogram, 2),
        where=(denominator_histogram != 0),
    )
    if len(error[error < 0.0]):
        msg = (
            "Unexpected negative ratio-error values found."
            "Setting them to zero.\n > Re-run. If the value changes, "
            "it might have to do with the minimum subnormal number bug!"
        )
        print(msg)
        print("Error; length")
        print(error[error < 0.0], len(error[error < 0.0]))
        print("Ratio values")
        print(ratio[np.where(error < 0.0)])
        error[error < 0.0] = 0.0

    return ratio, error


def get_output_directory(variable, base_directory, variables_dic):
    for var_type, var_list in variables_dic.items():
        if variable in var_list:
            return base_directory + var_type + "/"
    return base_directory


def clean_null_values(branches, variables, variables_dic):
    if (
        variables[0] not in variables_dic["diJet"]
        and variables[0] not in variables_dic["jet"]
    ):
        return

    if variables[0] == "n_jet":
        return

    null_value = 0
    if variables[0] in ["delta_phi_diJet", "pt_balance"]:
        null_value = -1

    bool_list = branches[variables[0]] != null_value
    for var in variables:
        branches[var] = branches[var][bool_list]
