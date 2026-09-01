import mplhep as hep
import numpy as np
import matplotlib.pyplot as plt

from .labels import x_labels, n_bins, x_range, variables_type
from .helper import get_canvas, save_figure, clean_null_values
from .colors import signal_colors


def draw_ggH_vs_VBF_comparison(
    df,
    variable,
    weight_column="weight",
    truth_column="y_truth",
    output_directory=None,
):
    """
    Plot a weighted, unit-area-normalized shape comparison of `variable`
    for ggH (truth_column == 0) vs VBF (truth_column == 1) events in `df`.
    """
    plt.style.use(hep.style.CMS)

    fig, ax = get_canvas()

    histograms = {}
    bins = None
    for label, truth_value in [("ggH", 0), ("VBF", 1)]:
        subset = df[df[truth_column] == truth_value]

        branches = {
            variable: subset[variable].to_numpy(),
            weight_column: subset[weight_column].to_numpy(),
        }
        clean_null_values(branches, [variable, weight_column], variables_type)

        values = branches[variable]
        if "delta_phi" in variable:
            values = np.absolute(values)

        histogram, bins = np.histogram(
            values,
            bins=n_bins[variable],
            range=x_range[variable],
            weights=branches[weight_column],
        )
        histograms[label] = histogram / np.sum(histogram)

    for label in ["ggH", "VBF"]:
        hep.histplot(
            histograms[label],
            bins,
            yerr=False,
            histtype="fill",
            label=label,
            ax=ax,
            color=signal_colors[label],
            alpha=0.4,
        )
        hep.histplot(
            histograms[label],
            bins,
            yerr=False,
            ax=ax,
            color=signal_colors[label],
            linewidth=2,
        )

    hep.cms.label(data="True", label="", year="Combined", com="13.6", ax=ax)

    ax.set_xlabel(x_labels[variable])
    ax.set_ylabel("Events / Total events")
    ymax = max(np.max(histograms["ggH"]), np.max(histograms["VBF"]))
    ax.set_ylim(0.0, 1.3 * ymax)
    ax.set_xlim(bins[0], bins[-1])
    ax.legend(frameon=False, loc="upper right", ncols=1)

    if output_directory is not None:
        save_figure(fig, output_directory, variable + "_ggH_vs_VBF")

    plt.show()
    plt.close(fig)
