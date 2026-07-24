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
year = "2024"
sample = "ttH"

files = {
    "pre-corr": (
        "/eos/uscms/store/user/lpchmumu/esledge/"
        "analyzer_HiggsMuMu_v1.5/tuples_v1.5.0/"
        f"haddTuples/{sample}_{year}_tuples.root"
    ),
    "post-corr": (
        "/eos/uscms/store/user/lpchmumu/mbarrial/"
        "analyzer_HiggsMuMu_v1.6/tuples_v1.6.1/"
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
]


output_directory = f"../plots/cut_flow/{sample}/"


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
    Percentage passing each cut relative to the previous cut:

        current / previous * 100
    """

    percentages = np.full(len(values), np.nan)

    for index in range(1, len(values)):
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
    sample_label,
    value_format,
):
    """Add labels above or below the plotted points."""

    vertical_offset = 10 if sample_label == "pre-corr" else -18

    for x_position, value in zip(x_positions, values):
        if not np.isfinite(value):
            continue

        axis.annotate(
            value_format.format(value),
            xy=(x_position, value),
            xytext=(0, vertical_offset),
            textcoords="offset points",
            ha="center",
            fontsize=POINT_LABEL_FONT_SIZE,
            color=line.get_color(),
        )


# ================================================================
# Read data and calculate efficiencies
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
# Print 1: Number of entries
# ================================================================

print("\nNumber of entries")
print(
    f"{'Selection':<25}"
    f"{'pre-corr':>18}"
    f"{'post-corr':>18}"
)
print("-" * 61)

for index, selection in enumerate(cut_labels):
    pre_entries = cutflows["pre-corr"][index]
    post_entries = cutflows["post-corr"][index]

    print(
        f"{selection:<25}"
        f"{pre_entries:>18,.0f}"
        f"{post_entries:>18,.0f}"
    )


# ================================================================
# Print 2: Step efficiency
# ================================================================

print("\nStep efficiency relative to the previous selection")
print(
    f"{'Selection':<25}"
    f"{'pre-corr':>18}"
    f"{'post-corr':>18}"
)
print("-" * 61)

for index, selection in enumerate(cut_labels[1:], start=1):
    pre_percentage = step_efficiencies["pre-corr"][index]
    post_percentage = step_efficiencies["post-corr"][index]

    print(
        f"{selection:<25}"
        f"{pre_percentage:>17.3f}%"
        f"{post_percentage:>17.3f}%"
    )


# ================================================================
# Print 3: Cumulative efficiency
# ================================================================

print("\nCumulative efficiency relative to all events")
print(
    f"{'Selection':<25}"
    f"{'pre-corr':>18}"
    f"{'post-corr':>18}"
)
print("-" * 61)

for index, selection in enumerate(cut_labels):
    pre_percentage = cumulative_efficiencies["pre-corr"][index]
    post_percentage = cumulative_efficiencies["post-corr"][index]

    print(
        f"{selection:<25}"
        f"{pre_percentage:>17.3f}%"
        f"{post_percentage:>17.3f}%"
    )


# ================================================================
# Plot 1: Number of entries
# ================================================================

x_positions = np.arange(len(cut_labels))

fig_entries, axis_entries = plt.subplots(figsize=(14, 8))

for label, values in cutflows.items():
    plotted_line = axis_entries.plot(
        x_positions,
        values,
        marker="o",
        linewidth=2,
        markersize=8,
        label=label,
    )[0]

    add_point_labels(
        axis=axis_entries,
        x_positions=x_positions,
        values=values,
        line=plotted_line,
        sample_label=label,
        value_format="{:,.0f}",
    )

axis_entries.set_xticks(x_positions)
axis_entries.set_xticklabels(
    cut_labels,
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

step_labels = cut_labels[1:]
step_x_positions = np.arange(len(step_labels))

fig_step, axis_step = plt.subplots(figsize=(14, 8))

for label, percentages in step_efficiencies.items():
    plotted_percentages = percentages[1:]

    plotted_line = axis_step.plot(
        step_x_positions,
        plotted_percentages,
        marker="o",
        linewidth=2,
        markersize=8,
        label=label,
    )[0]

    add_point_labels(
        axis=axis_step,
        x_positions=step_x_positions,
        values=plotted_percentages,
        line=plotted_line,
        sample_label=label,
        value_format="{:.2f}%",
    )

axis_step.set_xticks(step_x_positions)
axis_step.set_xticklabels(
    step_labels,
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

for label, percentages in cumulative_efficiencies.items():
    plotted_line = axis_cumulative.plot(
        x_positions,
        percentages,
        marker="o",
        linewidth=2,
        markersize=8,
        label=label,
    )[0]

    add_point_labels(
        axis=axis_cumulative,
        x_positions=x_positions,
        values=percentages,
        line=plotted_line,
        sample_label=label,
        value_format="{:.2f}%",
    )

axis_cumulative.set_xticks(x_positions)
axis_cumulative.set_xticklabels(
    cut_labels,
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
