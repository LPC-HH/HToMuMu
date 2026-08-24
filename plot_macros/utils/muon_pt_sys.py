"""Nominal/NanoAOD and muon-momentum systematic comparison plots."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import matplotlib


matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np

from .bdt_category_histograms import (
    FailureRecord,
    append_failure,
    build_category_selections,
    category_output_directory,
    get_requested_systematic_pairs,
    group_selections_by_category_channel,
    read_nominal_and_nanoaod_histograms,
    read_variation_histograms,
    relative_difference,
    resolve_category_nanoaod_file,
    resolve_category_nominal_file,
    resolve_category_systematics_directory,
    selection_branches,
    validate_tuple_file,
    write_failure_report,
)
from .helper import get_canvas, save_figure
from .labels import n_bins, x_labels, x_range


MUON_VARIABLES = (
    "diMuon_bsConstrainedMass",
    "mu1_bsConstrainedPt",
    "mu2_bsConstrainedPt",
)


def _bins_by_variable() -> Dict[str, np.ndarray]:
    bins: Dict[str, np.ndarray] = {}
    for variable in MUON_VARIABLES:
        if variable not in n_bins:
            raise KeyError(f"Missing n_bins entry for '{variable}'")
        if variable not in x_range:
            raise KeyError(f"Missing x_range entry for '{variable}'")
        histogram_range = tuple(x_range[variable])
        bins[variable] = np.linspace(
            histogram_range[0],
            histogram_range[1],
            int(n_bins[variable]) + 1,
        )
    return bins


def _inside_plot_label(
    production_channel: str,
    category_name: Optional[str],
    systematic_name: str,
) -> str:
    lines = [f"{production_channel} samples"]
    if category_name is not None:
        lines.append(category_name)
    lines.append(systematic_name.replace("_", " "))
    return "\n".join(lines)


def _set_log_y_range(axis, histograms: Sequence[np.ndarray]) -> None:
    positive = np.concatenate(
        [histogram[histogram > 0.0] for histogram in histograms]
    )
    if positive.size:
        axis.set_ylim(
            max(1.0e-3, 0.5 * np.min(positive)),
            10.0 * np.max(positive),
        )


def _ratio_half_range(ratios: Sequence[np.ndarray]) -> float:
    finite = np.concatenate(
        [ratio[np.isfinite(ratio)] for ratio in ratios]
    )
    if not finite.size:
        return 0.1
    return min(0.5, max(0.05, 1.2 * np.max(np.abs(finite))))


def draw_muon_systematic(
    variable: str,
    production_channel: str,
    systematic_name: str,
    nominal_histogram: np.ndarray,
    nanoaod_histogram: np.ndarray,
    up_histogram: np.ndarray,
    down_histogram: np.ndarray,
    bins: np.ndarray,
    output_directory: Path,
    normalize: bool = False,
    category_name: Optional[str] = None,
) -> None:
    """Draw nominal, NanoAOD, up, and down muon distributions."""

    plt.style.use(hep.style.CMS)
    fig, axs = get_canvas(True)

    for histogram, label, color, linestyle in (
        (nominal_histogram, "Post-corr", "black", "-"),
        (nanoaod_histogram, "Pre-corr", "tab:green", "--"),
        (up_histogram, "Up", "tab:red", "-"),
        (down_histogram, "Down", "tab:blue", "-"),
    ):
        hep.histplot(
            histogram,
            bins,
            yerr=False,
            histtype="step",
            label=label,
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
    axs[0].text(
        0.03,
        0.95,
        _inside_plot_label(
            production_channel,
            category_name,
            systematic_name,
        ),
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
        (nominal_histogram, nanoaod_histogram, up_histogram, down_histogram),
    )
    axs[0].legend(frameon=False, loc="upper right")
    axs[0].tick_params(
        axis="x", which="both", bottom=True, top=True, labelbottom=False
    )

    nanoaod_ratio = relative_difference(nanoaod_histogram, nominal_histogram)
    up_ratio = relative_difference(up_histogram, nominal_histogram)
    down_ratio = relative_difference(down_histogram, nominal_histogram)

    axs[1].axhline(y=0.0, color="grey", linestyle="--", alpha=0.5)
    for histogram, label, color, linestyle in (
        (up_ratio, "Up", "tab:red", "-"),
        (down_ratio, "Down", "tab:blue", "-"),
        (nanoaod_ratio, "Pre-corr", "tab:green", "--"),
    ):
        hep.histplot(
            histogram,
            bins,
            yerr=False,
            histtype="step",
            label=label,
            color=color,
            linestyle=linestyle,
            linewidth=2,
            ax=axs[1],
        )

    half_range = _ratio_half_range(
        (nanoaod_ratio, up_ratio, down_ratio)
    )
    axs[1].set_ylabel(
        r"$\frac{\mathrm{Var}-\mathrm{Nom}}{\mathrm{Nom}}$",
        fontsize=19,
        loc="center",
    )
    axs[1].set_ylim(-half_range, half_range)
    axs[1].set_xlim(bins[0], bins[-1])
    axs[1].set_xlabel(x_labels.get(variable, variable))

    plot_directory = category_output_directory(
        output_directory,
        category_name,
    )
    category_suffix = f"_{category_name}" if category_name else ""
    normalization_suffix = "_normalized" if normalize else ""
    output_name = (
        f"{variable}_{production_channel}{category_suffix}_{systematic_name}"
        f"{normalization_suffix}"
    )
    save_figure(fig, str(plot_directory) + "/", output_name)
    plt.close(fig)


def draw_data_nominal_nanoaod(
    variable: str,
    nominal_histogram: np.ndarray,
    nanoaod_histogram: np.ndarray,
    bins: np.ndarray,
    output_directory: Path,
    normalize: bool = False,
    category_name: Optional[str] = None,
) -> None:
    """Draw blinded nominal and NanoAOD-reference data distributions."""

    plt.style.use(hep.style.CMS)
    fig, axs = get_canvas(True)

    for histogram, label, color, linestyle in (
        (nominal_histogram, "Post-corr", "black", "-"),
        (nanoaod_histogram, "Pre-corr", "tab:green", "--"),
    ):
        hep.histplot(
            histogram,
            bins,
            yerr=False,
            histtype="step",
            label=label,
            color=color,
            linestyle=linestyle,
            linewidth=2,
            ax=axs[0],
        )

    hep.cms.label(
        data=True,
        rlabel="22–24   (13.6 TeV)",
        loc=0,
        ax=axs[0],
    )

    label_lines = ["Data"]
    if category_name is not None:
        label_lines.append(category_name)
    label_lines.append("Blinded: 120–130 GeV")

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
        (nominal_histogram, nanoaod_histogram),
    )
    axs[0].legend(frameon=False, loc="upper right")
    axs[0].tick_params(
        axis="x",
        which="both",
        bottom=True,
        top=True,
        labelbottom=False,
    )

    nanoaod_ratio = relative_difference(
        nanoaod_histogram,
        nominal_histogram,
    )

    axs[1].axhline(
        y=0.0,
        color="grey",
        linestyle="--",
        alpha=0.5,
    )

    hep.histplot(
        nanoaod_ratio,
        bins,
        yerr=False,
        histtype="step",
        label="Pre-corr",
        color="tab:green",
        linestyle="--",
        linewidth=2,
        ax=axs[1],
    )

    half_range = _ratio_half_range((nanoaod_ratio,))

    axs[1].set_ylabel(
        r"$\frac{\mathrm{Pre-corr}-\mathrm{Post-corr}}"
        r"{\mathrm{Post-corr}}$",
        fontsize=17,
        loc="center",
    )
    axs[1].set_ylim(-half_range, half_range)
    axs[1].set_xlim(bins[0], bins[-1])
    axs[1].set_xlabel(x_labels.get(variable, variable))

    plot_directory = category_output_directory(
        output_directory,
        category_name,
    )

    category_suffix = f"_{category_name}" if category_name else ""
    normalization_suffix = "_normalized" if normalize else ""

    output_name = (
        f"{variable}_data{category_suffix}_nominal_vs_nanoaod"
        f"{normalization_suffix}"
    )

    save_figure(
        fig,
        str(plot_directory) + "/",
        output_name,
    )
    plt.close(fig)


def draw_all_muon_systematics(
    production_channel: str,
    nominal_file: Path,
    nanoaod_file: Path,
    systematics_directory: Path,
    output_directory: Path,
    systematic_names: Sequence[str],
    normalize: bool = False,
    bdt_cuts: Optional[Mapping[str, Sequence[float]]] = None,
    bdt_category_channels: Sequence[str] = ("ggH", "VBF"),
    bdt_nominal_subdirectories: Optional[Mapping[str, Path]] = None,
    bdt_nanoaod_subdirectories: Optional[Mapping[str, Path]] = None,
    bdt_systematics_subdirectories: Optional[Mapping[str, Path]] = None,
    blind_data_mass_window: Optional[Tuple[float, float]] = None,
) -> int:
    """Create inclusive or per-BDT-category muon-systematic plots.

    In BDT-category mode, nominal, NanoAOD-reference, and systematic tuples are selected by
    the BDT category family. For example, ggH categories use the scored tuples
    below ``BDT_score/ggH/BFull_SNottH`` and VBF categories use those below
    ``BDT_score/VBF/BFull_SNottH``.
    """

    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    failed_files: List[FailureRecord] = []

    is_data = production_channel.strip().lower() == "data"

    blind_mass_window = (
        blind_data_mass_window if is_data else None
    )

    if blind_mass_window is not None:
        print(
            f"Blinding data events with "
            f"{blind_mass_window[0]} <= diMuon_bsConstrainedMass "
            f"<= {blind_mass_window[1]} GeV"
        )


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

        category_nanoaod_file = resolve_category_nanoaod_file(
            nanoaod_file,
            production_channel,
            category_channel,
            bdt_nanoaod_subdirectories,
        )
        print(
            f"NanoAOD tuple for {category_label} categories: "
            f"{category_nanoaod_file}"
        )

        group_category_branches = selection_branches(group_selections)
        nominal_required_branches = [
            *MUON_VARIABLES,
            "weight",
            *group_category_branches,
        ]
        nominal_is_valid, reason = validate_tuple_file(
            category_nominal_file,
            nominal_required_branches,
        )
        if not nominal_is_valid:
            print(
                f"[WARNING] Skipping {production_channel} / "
                f"{category_label} categories: invalid nominal tuple "
                f"{category_nominal_file}"
            )
            print(f"          {reason}")
            append_failure(failed_files, category_nominal_file, reason)
            continue

        nanoaod_is_valid, reason = validate_tuple_file(
            category_nanoaod_file,
            nominal_required_branches,
        )
        if not nanoaod_is_valid:
            print(
                f"[WARNING] Skipping {production_channel} / "
                f"{category_label} categories: invalid NanoAOD tuple "
                f"{category_nanoaod_file}"
            )
            print(f"          {reason}")
            append_failure(failed_files, category_nanoaod_file, reason)
            continue

        print(f"Reading nominal tuple once: {category_nominal_file}")
        print(f"Reading NanoAOD tuple once: {category_nanoaod_file}")
        try:
            nominal_histograms, nanoaod_histograms = (
                read_nominal_and_nanoaod_histograms(
                    category_nominal_file,
                    category_nanoaod_file,
                    MUON_VARIABLES,
                    group_selections,
                    bins_by_variable,
                    normalize,
                    use_weights=True,
                    minimum_value=0.0,
                    include_minimum=False,
                    blind_mass_window=blind_mass_window,
                )
            )
        except Exception as error:
            reason = (
                "failed while reading nominal histograms: "
                f"{type(error).__name__}: {error}"
            )
            print(
                f"[WARNING] Skipping {production_channel} / "
                f"{category_label} categories: {reason}"
            )
            append_failure(failed_files, category_nominal_file, reason)
            append_failure(failed_files, category_nanoaod_file, reason)
            continue
         
        if production_channel.strip().lower() == "data":
            print(
                f"Data sample: skipping systematic variations for "
                f"{category_label} categories."
            )

            for selection in group_selections:
                for variable in MUON_VARIABLES:
                    nominal_histogram, nominal_bins = nominal_histograms[
                        selection.key
                    ][variable]

                    nanoaod_histogram, nanoaod_bins = nanoaod_histograms[
                        selection.key
                    ][variable]

                    if not np.array_equal(
                        nominal_bins,
                        nanoaod_bins,
                    ):
                        print(
                            f"[WARNING] Skipping data / "
                            f"{selection.key} / {variable}: "
                            "inconsistent nominal/NanoAOD binning."
                        )
                        continue

                    draw_data_nominal_nanoaod(
                        variable=variable,
                        nominal_histogram=nominal_histogram,
                        nanoaod_histogram=nanoaod_histogram,
                        bins=nominal_bins,
                        output_directory=output_directory,
                        normalize=normalize,
                        category_name=selection.display_name,
                    )

                    number_of_plots += 1

            # Move to the next BDT family without searching for
            # data systematic files.
            continue       

        category_systematics_directory = resolve_category_systematics_directory(
            systematics_directory,
            category_channel,
            bdt_systematics_subdirectories,
        )
        print(
            f"Systematic directory for {category_label} categories: "
            f"{category_systematics_directory}"
        )
        if not category_systematics_directory.is_dir():
            reason = "systematics directory does not exist"
            print(
                f"[WARNING] Skipping {production_channel} / "
                f"{category_label} categories: {reason}: "
                f"{category_systematics_directory}"
            )
            append_failure(
                failed_files,
                category_systematics_directory,
                reason,
            )
            continue

        pairs = get_requested_systematic_pairs(
            production_channel,
            category_systematics_directory,
            systematic_names,
            failed_files,
        )
        if not pairs:
            print(
                f"[WARNING] No complete requested systematic pairs were found "
                f"for {production_channel} / {category_label} categories."
            )
            continue

        required_variation_branches = [
            *MUON_VARIABLES,
            "weight",
            *group_category_branches,
        ]
        print(
            f"Found {len(pairs)} complete requested systematic pair(s) for "
            f"{production_channel} / {category_label} categories."
        )

        for systematic_number, (systematic_name, variation_files) in enumerate(
            pairs.items(), start=1
        ):
            up_file, down_file = variation_files
            print(
                f"[{systematic_number}/{len(pairs)}] "
                f"{production_channel} / {category_label}: {systematic_name}"
            )

            pair_is_valid = True
            for direction, variation_file in (
                ("up", up_file),
                ("down", down_file),
            ):
                is_valid, reason = validate_tuple_file(
                    variation_file,
                    required_variation_branches,
                )
                if not is_valid:
                    pair_is_valid = False
                    print(
                        f"[WARNING] Skipping {production_channel} / "
                        f"{category_label} / {systematic_name}: invalid "
                        f"{direction} tuple {variation_file}"
                    )
                    print(f"          {reason}")
                    append_failure(failed_files, variation_file, reason)
            if not pair_is_valid:
                continue

            try:
                up_histograms = read_variation_histograms(
                    up_file,
                    MUON_VARIABLES,
                    group_selections,
                    bins_by_variable,
                    normalize,
                    use_weights=True,
                    minimum_value=0.0,
                    include_minimum=False,
                    blind_mass_window=blind_mass_window,
                )

                down_histograms = read_variation_histograms(
                    down_file,
                    MUON_VARIABLES,
                    group_selections,
                    bins_by_variable,
                    normalize,
                    use_weights=True,
                    minimum_value=0.0,
                    include_minimum=False,
                    blind_mass_window=blind_mass_window,
                )
            except Exception as error:
                reason = (
                    "failed while reading variation histograms: "
                    f"{type(error).__name__}: {error}"
                )
                print(
                    f"[WARNING] Skipping {category_label} / "
                    f"{systematic_name}: {reason}"
                )
                append_failure(failed_files, up_file, reason)
                append_failure(failed_files, down_file, reason)
                continue

            for selection in group_selections:
                for variable in MUON_VARIABLES:
                    nominal_histogram, nominal_bins = nominal_histograms[
                        selection.key
                    ][variable]
                    nanoaod_histogram, nanoaod_bins = nanoaod_histograms[
                        selection.key
                    ][variable]
                    up_histogram, up_bins = up_histograms[selection.key][variable]
                    down_histogram, down_bins = down_histograms[
                        selection.key
                    ][variable]

                    if not (
                        np.array_equal(nominal_bins, nanoaod_bins)
                        and np.array_equal(nominal_bins, up_bins)
                        and np.array_equal(nominal_bins, down_bins)
                    ):
                        print(
                            f"[WARNING] Skipping {production_channel} / "
                            f"{selection.key} / {systematic_name} / "
                            f"{variable}: inconsistent binning."
                        )
                        continue

                    draw_muon_systematic(
                        variable,
                        production_channel,
                        systematic_name,
                        nominal_histogram,
                        nanoaod_histogram,
                        up_histogram,
                        down_histogram,
                        nominal_bins,
                        output_directory,
                        normalize,
                        selection.display_name,
                    )
                    number_of_plots += 1

    write_failure_report(output_directory, production_channel, failed_files)
    return number_of_plots
