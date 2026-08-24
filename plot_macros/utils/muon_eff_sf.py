#Compare the effect of removing muon efficiency scale factors.


from __future__ import annotations

from pathlib import Path
from typing import Dict, Mapping, Optional, Sequence

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import uproot as ur

from .bdt_category_histograms import (
    FailureRecord,
    GroupedHistograms,
    append_failure,
    build_category_selections,
    category_output_directory,
    finalize_grouped_histograms,
    group_selections_by_category_channel,
    initialize_grouped_histograms,
    relative_difference,
    resolve_category_nominal_file,
    selection_branches,
    selection_mask,
    validate_tuple_file,
    write_failure_report,
)
from .helper import get_canvas, save_figure
from .labels import n_bins, x_labels, x_range


TREE_NAME = "tree_output"

VARIABLES = (
    "diMuon_bsConstrainedMass",
    "mu1_bsConstrainedPt",
    "mu2_bsConstrainedPt",
)

TRIG_SF_BRANCH = "mu_trig_eff_SF"
ID_SF_BRANCH = "mu_ID_eff_SF"
ISO_SF_BRANCH = "mu_ISO_eff_SF"

WEIGHT_LABELS = {
    "nominal": "Nominal",
    "no_trig": "No Trig SF",
    "no_id": "No ID SF",
    "no_iso": "No ISO SF",
    "no_sf": "No SF",
}


def _bins_by_variable() -> Dict[str, np.ndarray]:
    bins: Dict[str, np.ndarray] = {}
    for variable in VARIABLES:
        if variable not in n_bins:
            raise KeyError(f"Missing n_bins entry for '{variable}'")
        if variable not in x_range:
            raise KeyError(f"Missing x_range entry for '{variable}'")

        low, high = map(float, x_range[variable])
        bins[variable] = np.linspace(
            low,
            high,
            int(n_bins[variable]) + 1,
        )
    return bins


def _weights_without_scale_factors(
    arrays: Mapping[str, np.ndarray],
) -> Dict[str, np.ndarray]:
    """Construct the five requested event-weight definitions.

    nominal = weight
    no_trig = weight / trigger_SF
    no_id   = weight / ID_SF
    no_iso  = weight / ISO_SF
    no_sf   = weight / (trigger_SF * ID_SF * ISO_SF)

    """

    nominal = np.asarray(arrays["weight"], dtype=float)
    trig_sf = np.asarray(arrays[TRIG_SF_BRANCH], dtype=float)
    id_sf = np.asarray(arrays[ID_SF_BRANCH], dtype=float)
    iso_sf = np.asarray(arrays[ISO_SF_BRANCH], dtype=float)

    def divide_weight(denominator: np.ndarray) -> np.ndarray:
        output = np.full(nominal.shape, np.nan, dtype=float)
        valid = (
            np.isfinite(nominal)
            & np.isfinite(denominator)
            & (denominator != 0.0)
        )
        np.divide(
            nominal,
            denominator,
            out=output,
            where=valid,
        )
        return output

    return {
        "nominal": nominal,
        "no_trig": divide_weight(trig_sf),
        "no_id": divide_weight(id_sf),
        "no_iso": divide_weight(iso_sf),
        "no_sf": divide_weight(trig_sf * id_sf * iso_sf),
    }


def read_efficiency_sf_histograms(
    file_path: Path,
    variables: Sequence[str],
    selections,
    bins_by_variable: Mapping[str, np.ndarray],
    normalize: bool,
) -> Dict[str, GroupedHistograms]:

    branches_to_read = [
        *variables,
        "weight",
        TRIG_SF_BRANCH,
        ID_SF_BRANCH,
        ISO_SF_BRANCH,
        *selection_branches(selections),
    ]
    branches_to_read = list(dict.fromkeys(branches_to_read))

    raw_histograms = {
        weight_name: initialize_grouped_histograms(
            variables,
            selections,
            bins_by_variable,
        )
        for weight_name in WEIGHT_LABELS
    }

    tree_path = f"{Path(file_path)}:{TREE_NAME}"
    for arrays in ur.iterate(
        tree_path,
        branches_to_read,
        library="np",
        step_size="50 MB",
    ):
        number_of_events = len(arrays[variables[0]])
        weights = _weights_without_scale_factors(arrays)

        category_masks = {
            selection.key: selection_mask(
                arrays,
                selection,
                number_of_events,
            )
            for selection in selections
        }

        for variable in variables:
            values = np.asarray(arrays[variable], dtype=float)
            valid_value = np.isfinite(values) & (values > 0.0)

            for selection in selections:
                selection_valid = category_masks[selection.key] & valid_value

                for weight_name, event_weights in weights.items():
                    valid = selection_valid & np.isfinite(event_weights)
                    chunk_histogram, _ = np.histogram(
                        values[valid],
                        bins=bins_by_variable[variable],
                        weights=event_weights[valid],
                    )
                    raw_histograms[weight_name][selection.key][
                        variable
                    ] += chunk_histogram

    return {
        weight_name: finalize_grouped_histograms(
            histograms,
            bins_by_variable,
            normalize,
            weight_name,
        )
        for weight_name, histograms in raw_histograms.items()
    }


def _set_log_y_range(axis, histograms: Sequence[np.ndarray]) -> None:
    positive_parts = [hist[hist > 0.0] for hist in histograms if hist.size]
    if not positive_parts:
        return

    positive = np.concatenate(positive_parts)
    if positive.size:
        axis.set_ylim(
            max(1.0e-3, 0.5 * np.min(positive)),
            10.0 * np.max(positive),
        )


def _ratio_half_range(ratios: Sequence[np.ndarray]) -> float:
    finite_parts = [ratio[np.isfinite(ratio)] for ratio in ratios]
    if not finite_parts:
        return 0.05

    finite = np.concatenate(finite_parts)
    if not finite.size:
        return 0.05

    return min(0.5, max(0.02, 1.2 * np.max(np.abs(finite))))


def draw_efficiency_sf_comparison(
    variable: str,
    production_channel: str,
    histograms: Mapping[str, np.ndarray],
    bins: np.ndarray,
    output_directory: Path,
    normalize: bool = False,
    category_name: Optional[str] = None,
) -> None:
    """Draw Nominal, No Trig SF, No ID SF, No ISO SF, and No SF."""

    plt.style.use(hep.style.CMS)
    fig, axs = get_canvas(True)

    plot_styles = {
        "nominal": ("black", "-"),
        "no_trig": ("tab:red", "-"),
        "no_id": ("tab:blue", "-"),
        "no_iso": ("tab:green", "-"),
        "no_sf": ("tab:purple", "--"),
    }

    for weight_name in WEIGHT_LABELS:
        color, linestyle = plot_styles[weight_name]
        hep.histplot(
            histograms[weight_name],
            bins,
            yerr=False,
            histtype="step",
            label=WEIGHT_LABELS[weight_name],
            color=color,
            linestyle=linestyle,
            linewidth=2,
            ax=axs[0],
        )

    hep.cms.label(
        data=False,
        rlabel="Sim. 22–24   (13.6 TeV)",
        loc=0,
        ax=axs[0],
    )

    label_lines = [f"{production_channel} samples"]
    if category_name is not None:
        label_lines.append(category_name)
    label_lines.append("Muon efficiency SFs")

    axs[0].text(
        0.03,
        0.95,
        "\n".join(label_lines),
        transform=axs[0].transAxes,
        ha="left",
        va="top",
        fontsize=16,
        linespacing=1.15,
    )

    axs[0].set_ylabel("A.U." if normalize else "Events")
    axs[0].set_xlim(bins[0], bins[-1])
    axs[0].set_yscale("log")
    _set_log_y_range(
        axs[0],
        [histograms[name] for name in WEIGHT_LABELS],
    )
    axs[0].legend(frameon=False, loc="upper right")
    axs[0].tick_params(
        axis="x",
        which="both",
        bottom=True,
        top=True,
        labelbottom=False,
    )

    nominal = histograms["nominal"]
    ratios = {
        name: relative_difference(histograms[name], nominal)
        for name in ("no_trig", "no_id", "no_iso", "no_sf")
    }

    axs[1].axhline(
        y=0.0,
        color="grey",
        linestyle="--",
        alpha=0.5,
    )

    for weight_name, ratio in ratios.items():
        color, linestyle = plot_styles[weight_name]
        hep.histplot(
            ratio,
            bins,
            yerr=False,
            histtype="step",
            label=WEIGHT_LABELS[weight_name],
            color=color,
            linestyle=linestyle,
            linewidth=2,
            ax=axs[1],
        )

    half_range = _ratio_half_range(tuple(ratios.values()))
    axs[1].set_ylabel(
        r"$\frac{\mathrm{Var}-\mathrm{Nom}}{\mathrm{Nom}}$",
        fontsize=17,
        loc="center",
    )
    axs[1].set_ylim(-half_range, half_range)
    axs[1].set_xlim(bins[0], bins[-1])
    axs[1].set_xlabel(x_labels.get(variable, variable))

    plot_directory = output_directory
    category_suffix = f"_{category_name}" if category_name else ""
    normalization_suffix = "_normalized" if normalize else ""
    output_name = (
        f"{variable}_{production_channel}{category_suffix}_muon_eff_sf"
        f"{normalization_suffix}"
    )

    save_figure(fig, str(plot_directory) + "/", output_name)
    plt.close(fig)


def draw_all_efficiency_sf_comparisons(
    production_channel: str,
    nominal_file: Path,
    output_directory: Path,
    normalize: bool = False,
    bdt_cuts: Optional[Mapping[str, Sequence[float]]] = None,
    bdt_category_channels: Sequence[str] = ("ggH", "VBF"),
    bdt_nominal_subdirectories: Optional[Mapping[str, Path]] = None,
) -> int:

    if production_channel.strip().lower() == "data":
        raise ValueError(
            "Efficiency scale-factor comparisons are for MC samples, not data."
        )

    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    failed_files: list[FailureRecord] = []

    selections = build_category_selections(
        production_channel,
        bdt_cuts,
        bdt_category_channels,
    )
    selection_groups = group_selections_by_category_channel(selections)
    bins_by_variable = _bins_by_variable()
    number_of_plots = 0

    for category_channel, group_selections in selection_groups.items():
        category_label = category_channel or "inclusive"

        category_nominal_file = resolve_category_nominal_file(
            nominal_file,
            production_channel,
            category_channel,
            bdt_nominal_subdirectories,
        )

        print(
            f"Nominal tuple for {category_label} categories: "
            f"{category_nominal_file}"
        )

        required_branches = [
            *VARIABLES,
            "weight",
            TRIG_SF_BRANCH,
            ID_SF_BRANCH,
            ISO_SF_BRANCH,
            *selection_branches(group_selections),
        ]

        is_valid, reason = validate_tuple_file(
            category_nominal_file,
            required_branches,
        )
        if not is_valid:
            print(
                f"[WARNING] Skipping {production_channel} / "
                f"{category_label}: invalid nominal tuple "
                f"{category_nominal_file}"
            )
            print(f"          {reason}")
            append_failure(failed_files, category_nominal_file, reason)
            continue

        try:
            all_histograms = read_efficiency_sf_histograms(
                category_nominal_file,
                VARIABLES,
                group_selections,
                bins_by_variable,
                normalize,
            )
        except Exception as error:
            reason = (
                "failed while reading efficiency-SF histograms: "
                f"{type(error).__name__}: {error}"
            )
            print(
                f"[WARNING] Skipping {production_channel} / "
                f"{category_label}: {reason}"
            )
            append_failure(failed_files, category_nominal_file, reason)
            continue

        for selection in group_selections:
            for variable in VARIABLES:
                histograms_for_plot: Dict[str, np.ndarray] = {}
                reference_bins = None
                consistent_binning = True

                for weight_name in WEIGHT_LABELS:
                    histogram, bins = all_histograms[weight_name][selection.key][
                        variable
                    ]
                    histograms_for_plot[weight_name] = histogram

                    if reference_bins is None:
                        reference_bins = bins
                    elif not np.array_equal(reference_bins, bins):
                        consistent_binning = False

                if not consistent_binning or reference_bins is None:
                    print(
                        f"[WARNING] Skipping {production_channel} / "
                        f"{selection.key} / {variable}: inconsistent binning."
                    )
                    continue

                draw_efficiency_sf_comparison(
                    variable=variable,
                    production_channel=production_channel,
                    histograms=histograms_for_plot,
                    bins=reference_bins,
                    output_directory=output_directory,
                    normalize=normalize,
                    category_name=selection.display_name,
                )
                number_of_plots += 1

    write_failure_report(output_directory, production_channel, failed_files)
    return number_of_plots
