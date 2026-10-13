#!/usr/bin/env python3

import ROOT
import mplhep as hep
import matplotlib.pyplot as plt
import numpy as np

from utils.helper import save_figure


ROOT.gROOT.SetBatch(True)
hep.style.use("CMS")

X_TICK_FONT_SIZE = 8
POINT_LABEL_FONT_SIZE = 14

year = "Combined"
sample = "VBF"


# ================================================================
# Files to compare
# ================================================================

files = {
    "v2.3.0": (
        "root://cmseos.fnal.gov//store/user/lpchmumu/mbarrial/"
        "analyzer_HiggsMuMu_v2.3/tuples_v2.3.0/"
        f"haddTuples/{sample}_{year}_tuples.root"
    ),
    "v2.4.2": (
        "root://cmseos.fnal.gov//store/user/lpchmumu/mbarrial/"
        "analyzer_HiggsMuMu_v2.4/tuples_v2.4.2/"
        f"haddTuples/{sample}_{year}_tuples.root"
    ),
}


cutflow_histograms = [
    ("h_nEntries", "All events"),
    ("h_nTrigger", "Trigger"),
    ("h_nTwoMuons", "Two muons"),
    ("h_nNoExtraMuon", "No extra muon"),
    ("h_nNoExtraElectron", "No extra electron"),
    ("h_nTriggerMatch", "Trigger match"),
    # ("h_nInFinalMassRange", "Final mass range"),
    ("h_nBjetRejection", "b-jet rejection"),
    ("h_nggHCat", "ggH category"),
    ("h_nVBFCat", "VBF category"),
]


output_directory = f"../plots/cut_flow/{sample}/"


# ================================================================
# Useful indices
# ================================================================

histogram_names = [
    histogram_name
    for histogram_name, _ in cutflow_histograms
]

BJET_INDEX = histogram_names.index("h_nBjetRejection")
GGH_INDEX = histogram_names.index("h_nggHCat")
VBF_INDEX = histogram_names.index("h_nVBFCat")

CATEGORY_X_POSITION = BJET_INDEX + 1


# ================================================================
# Functions
# ================================================================

def read_cutflow(file_path):
    """Read the number of events stored in each cut-flow histogram."""

    root_file = ROOT.TFile.Open(file_path, "READ")

    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"Could not open file:\n{file_path}")

    values = []

    for histogram_name, _ in cutflow_histograms:
        histogram = root_file.Get(histogram_name)

        if not histogram:
            root_file.Close()
            raise RuntimeError(
                f"Histogram '{histogram_name}' not found in:\n"
                f"{file_path}"
            )

        value = histogram.Integral(
            0,
            histogram.GetNbinsX() + 1,
        )

        values.append(value)

    root_file.Close()

    return np.asarray(values, dtype=float)


def calculate_step_efficiency(values):
    """
    Percentage passing each cut relative to the previous cut.

    ggH and VBF categories are both calculated relative to
    h_nBjetRejection because they are parallel branches.
    """

    percentages = np.full(len(values), np.nan)

    for index in range(1, len(values)):

        if index in (GGH_INDEX, VBF_INDEX):
            previous = values[BJET_INDEX]
        else:
            previous = values[index - 1]

        current = values[index]

        if previous != 0:
            percentages[index] = current / previous * 100.0

    return percentages


def calculate_cumulative_efficiency(values):
    """
    Percentage remaining relative to h_nEntries:

        current / n_entries * 100
    """

    percentages = np.full(len(values), np.nan)

    n_entries = values[0]

    if n_entries != 0:
        percentages = values / n_entries * 100.0

    return percentages


def add_point_labels(
    axis,
    x_positions,
    values,
    line,
    series_index,
    n_series,
    value_format,
    point_names=None,
):
    """Add labels near plotted points."""

    if n_series == 1:
        vertical_offset = 10
    else:
        vertical_offset = 12 + series_index * 12

    for index, (x_position, value) in enumerate(
        zip(x_positions, values)
    ):

        if not np.isfinite(value):
            continue

        text = value_format.format(value)

        if point_names is not None:
            point_name = point_names[index]

            if point_name:
                text = f"{point_name}: {text}"

        axis.annotate(
            text,
            xy=(x_position, value),
            xytext=(0, vertical_offset),
            textcoords="offset points",
            ha="center",
            fontsize=POINT_LABEL_FONT_SIZE,
            color=line.get_color(),
        )


def plot_branched_cutflow(
    axis,
    values,
    label,
):
    """
    Plot the common cut flow up to b-jet rejection, then branch into
    ggH and VBF categories at the same x position.
    """

    common_x_positions = np.arange(BJET_INDEX + 1)

    plotted_line = axis.plot(
        common_x_positions,
        values[:BJET_INDEX + 1],
        marker="o",
        linewidth=2,
        markersize=8,
        label=label,
    )[0]

    color = plotted_line.get_color()

    # ggH branch
    axis.plot(
        [BJET_INDEX, CATEGORY_X_POSITION],
        [values[BJET_INDEX], values[GGH_INDEX]],
        marker="o",
        linewidth=2,
        markersize=8,
        color=color,
    )

    # VBF branch
    axis.plot(
        [BJET_INDEX, CATEGORY_X_POSITION],
        [values[BJET_INDEX], values[VBF_INDEX]],
        marker="s",
        linewidth=2,
        markersize=8,
        color=color,
    )

    return plotted_line


def print_table(title, values_dict, value_format, skip_first=False):
    """Print a generic comparison table for all versions."""

    labels = list(values_dict.keys())

    print(f"\n{title}")

    column_width = 18

    header = f"{'Selection':<25}"

    for label in labels:
        header += f"{label:>{column_width}}"

    print(header)
    print("-" * (25 + column_width * len(labels)))

    start_index = 1 if skip_first else 0

    for index in range(start_index, len(cut_labels)):
        row = f"{cut_labels[index]:<25}"

        for label in labels:
            value = values_dict[label][index]
            row += f"{value_format.format(value):>{column_width}}"

        print(row)


# ================================================================
# Read data
# ================================================================

cutflows = {
    label: read_cutflow(file_path)
    for label, file_path in files.items()
}

step_efficiencies = {
    label: calculate_step_efficiency(values)
    for label, values in cutflows.items()
}

cumulative_efficiencies = {
    label: calculate_cumulative_efficiency(values)
    for label, values in cutflows.items()
}


cut_labels = [
    cut_label
    for _, cut_label in cutflow_histograms
]


# ================================================================
# Plot positions
# ================================================================

# ggH and VBF occupy the same final x position
x_positions = np.asarray(
    list(range(BJET_INDEX + 1))
    + [CATEGORY_X_POSITION, CATEGORY_X_POSITION]
)

point_names = (
    [""] * (BJET_INDEX + 1)
    + ["ggH", "VBF"]
)

tick_positions = np.arange(CATEGORY_X_POSITION + 1)

tick_labels = (
    cut_labels[:BJET_INDEX + 1]
    + ["Category"]
)


# ================================================================
# Print tables
# ================================================================

print_table(
    title="Number of entries",
    values_dict=cutflows,
    value_format="{:,.0f}",
)

print_table(
    title="Step efficiency relative to the previous selection",
    values_dict=step_efficiencies,
    value_format="{:.3f}%",
    skip_first=True,
)

print_table(
    title="Cumulative efficiency relative to all events",
    values_dict=cumulative_efficiencies,
    value_format="{:.3f}%",
)


# ================================================================
# Plot 1: Number of entries
# ================================================================

fig_entries, axis_entries = plt.subplots(figsize=(14, 8))

n_series = len(cutflows)

for series_index, (label, values) in enumerate(cutflows.items()):

    plotted_line = plot_branched_cutflow(
        axis=axis_entries,
        values=values,
        label=label,
    )

    add_point_labels(
        axis=axis_entries,
        x_positions=x_positions,
        values=values,
        line=plotted_line,
        series_index=series_index,
        n_series=n_series,
        value_format="{:,.0f}",
        point_names=point_names,
    )


axis_entries.set_xticks(tick_positions)

axis_entries.set_xticklabels(
    tick_labels,
    rotation=35,
    ha="right",
    fontsize=X_TICK_FONT_SIZE,
)

axis_entries.set_yscale("log")

axis_entries.set_ylabel("Number of entries")
axis_entries.set_xlabel("Selection")

axis_entries.grid(
    True,
    which="both",
    linestyle="--",
    alpha=0.35,
)

axis_entries.legend()

hep.cms.label(
    "",
    data=True,
    year=year,
    ax=axis_entries,
)

fig_entries.tight_layout()

save_figure(
    fig_entries,
    output_directory,
    f"cut_flow_{year}_entries",
)

plt.close(fig_entries)


# ================================================================
# Plot 2: Step efficiency
# ================================================================

fig_step, axis_step = plt.subplots(figsize=(14, 8))

n_series = len(step_efficiencies)

for series_index, (label, percentages) in enumerate(
    step_efficiencies.items()
):

    plotted_line = plot_branched_cutflow(
        axis=axis_step,
        values=percentages,
        label=label,
    )

    add_point_labels(
        axis=axis_step,
        x_positions=x_positions,
        values=percentages,
        line=plotted_line,
        series_index=series_index,
        n_series=n_series,
        value_format="{:.2f}%",
        point_names=point_names,
    )


axis_step.set_xticks(tick_positions[1:])

axis_step.set_xticklabels(
    tick_labels[1:],
    rotation=35,
    ha="right",
    fontsize=X_TICK_FONT_SIZE,
)

axis_step.set_ylabel("Step efficiency [%]")
axis_step.set_xlabel("Selection")

axis_step.set_ylim(0, 110)

axis_step.grid(
    True,
    linestyle="--",
    alpha=0.35,
)

axis_step.legend()

hep.cms.label(
    "Preliminary",
    data=True,
    year=year,
    ax=axis_step,
)

fig_step.tight_layout()

save_figure(
    fig_step,
    output_directory,
    f"cut_flow_{year}_step_efficiency",
)

plt.close(fig_step)


# ================================================================
# Plot 3: Cumulative efficiency
# ================================================================

fig_cumulative, axis_cumulative = plt.subplots(figsize=(14, 8))

n_series = len(cumulative_efficiencies)

for series_index, (label, percentages) in enumerate(
    cumulative_efficiencies.items()
):

    plotted_line = plot_branched_cutflow(
        axis=axis_cumulative,
        values=percentages,
        label=label,
    )

    add_point_labels(
        axis=axis_cumulative,
        x_positions=x_positions,
        values=percentages,
        line=plotted_line,
        series_index=series_index,
        n_series=n_series,
        value_format="{:.2f}%",
        point_names=point_names,
    )


axis_cumulative.set_xticks(tick_positions)

axis_cumulative.set_xticklabels(
    tick_labels,
    rotation=35,
    ha="right",
    fontsize=X_TICK_FONT_SIZE,
)

axis_cumulative.set_ylabel("Cumulative efficiency [%]")
axis_cumulative.set_xlabel("Selection")

axis_cumulative.set_ylim(0, 110)

axis_cumulative.grid(
    True,
    linestyle="--",
    alpha=0.35,
)

axis_cumulative.legend()

hep.cms.label(
    "Preliminary",
    data=True,
    year=year,
    ax=axis_cumulative,
)

fig_cumulative.tight_layout()

save_figure(
    fig_cumulative,
    output_directory,
    f"cut_flow_{year}_cumulative_efficiency",
)

plt.close(fig_cumulative)
