from __future__ import annotations

import argparse
import csv
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import uproot as ur

# Read the (tens of GB) BDT_score files in chunks rather than memory-mapping them whole:
# the whole-file map alone exceeds the 16 GiB per-process limit on the LPC login nodes.
UPROOT_OPEN = dict(file_handler=ur.MultithreadedFileSource)

from utils.helper import get_canvas, save_figure
from utils.labels import luminosity, n_bins, x_labels, x_range


MASS_BRANCH = "diMuon_bsConstrainedMass"
WEIGHT_BRANCH = "weight_no_eff_sf"
TREE_NAME = "tree_output"

BASE_DIR = Path("../root_io/tuples/BDT_score")
BDT_SUBSET = "BFull_SNottH"
OUTPUT_DIR = Path("../plots/effctive_sigma")
ERA = "Combined"
STEP_SIZE = "500 MB"

SIGNAL_FILE_NAME = "signal_Combined.root"
DATA_FILE_NAME = "data_Combined.root"

# Signal yield window.
SIGNAL_YIELD_MIN = 123.5
SIGNAL_YIELD_MAX = 126.5

# Data sidebands. The inequalities are strict.
DATA_SB1_MIN = 110.0
DATA_SB1_MAX = 120.0
DATA_SB2_MIN = 130.0
DATA_SB2_MAX = 150.0

EFFECTIVE_FRACTION = 0.683

# BDT category boundaries in ascending score order.
bdt_cuts = {
    "ggH": [
        0.0,
        0.4400000000000002,
        0.6100000000000003,
        0.8100000000000005,
        0.9200000000000006,
        1.0,
    ],
    "VBF": [
        0.0,
        0.6466666666666667,
        0.8800000000000018,
        0.9466666666666689,
        0.9733333333333357,
        1.0,
    ],
}


@dataclass
class CategoryResult:
    sample_type: str
    channel: str
    category: int | str
    bdt_low: float
    bdt_high: float
    masses: np.ndarray
    weights: np.ndarray
    yield_value: float
    yield_uncertainty: float
    sigma_low: float
    sigma_high: float
    sigma_eff: float
    sigma_weight_mode: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot signal effective sigma or data sideband yields."
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Normalize every histogram to unit area.",
    )
    parser.add_argument(
        "--data",
        action="store_true",
        help=(
            "Run over data_Combined.root, count events in the two sidebands, "
            "and skip the effective-sigma calculation."
        ),
    )
    return parser.parse_args()


def validate_cuts(cuts: Iterable[float], channel: str) -> np.ndarray:
    cuts_array = np.asarray(list(cuts), dtype=float)

    if cuts_array.size < 2:
        raise ValueError(f"{channel}: at least two BDT boundaries are required.")
    if not np.all(np.isfinite(cuts_array)):
        raise ValueError(f"{channel}: all BDT boundaries must be finite.")
    if not np.all(np.diff(cuts_array) > 0):
        raise ValueError(f"{channel}: BDT boundaries must be strictly ascending.")

    return cuts_array


def category_intervals(cuts: np.ndarray) -> list[tuple[int, float, float, bool]]:
    """Return cat1, cat2, ..., with cat1 assigned to the highest BDT scores."""
    number_of_categories = len(cuts) - 1
    intervals = []

    for category in range(1, number_of_categories + 1):
        interval_index = number_of_categories - category
        low = float(cuts[interval_index])
        high = float(cuts[interval_index + 1])
        include_high_edge = interval_index == number_of_categories - 1
        intervals.append((category, low, high, include_high_edge))

    return intervals


def effective_sigma(
    values: np.ndarray,
    weights: np.ndarray,
    fraction: float = EFFECTIVE_FRACTION,
) -> tuple[float, float, float, str]:
    """Find the narrowest interval containing ``fraction`` of signed weight."""
    if not 0.0 < fraction < 1.0:
        raise ValueError("The effective-sigma fraction must be between 0 and 1.")

    finite = np.isfinite(values) & np.isfinite(weights)
    values = np.asarray(values[finite], dtype=float)
    weights = np.asarray(weights[finite], dtype=float)

    if values.size == 0:
        return np.nan, np.nan, np.nan, WEIGHT_BRANCH

    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    sorted_weights = weights[order]

    prefix = np.concatenate(([0.0], np.cumsum(sorted_weights)))
    total_signed_weight = float(prefix[-1])

    if not np.isfinite(total_signed_weight) or total_signed_weight <= 0.0:
        return np.nan, np.nan, np.nan, WEIGHT_BRANCH

    target_weight = fraction * total_signed_weight
    compressed_prefix = np.unique(prefix)
    fenwick = np.full(compressed_prefix.size + 1, -1, dtype=np.int64)

    def update(position: int, prefix_index: int) -> None:
        position += 1
        while position < fenwick.size:
            if prefix_index > fenwick[position]:
                fenwick[position] = prefix_index
            position += position & -position

    def query(position: int) -> int:
        position += 1
        best_index = -1
        while position > 0:
            if fenwick[position] > best_index:
                best_index = int(fenwick[position])
            position -= position & -position
        return best_index

    best_low = np.nan
    best_high = np.nan
    best_width = np.inf

    for right_prefix in range(1, sorted_values.size + 1):
        start_prefix_index = right_prefix - 1
        update_position = int(
            np.searchsorted(
                compressed_prefix,
                prefix[start_prefix_index],
                side="left",
            )
        )
        update(update_position, start_prefix_index)

        threshold = prefix[right_prefix] - target_weight
        query_position = int(
            np.searchsorted(compressed_prefix, threshold, side="right") - 1
        )

        if query_position < 0:
            continue

        left_index = query(query_position)
        if left_index < 0 or left_index >= right_prefix:
            continue

        low = float(sorted_values[left_index])
        high = float(sorted_values[right_prefix - 1])
        width = high - low

        if width < best_width:
            best_width = width
            best_low = low
            best_high = high

    if not np.isfinite(best_width):
        return np.nan, np.nan, np.nan, WEIGHT_BRANCH

    return best_low, best_high, 0.5 * best_width, WEIGHT_BRANCH


def signal_yield_selection(masses: np.ndarray) -> np.ndarray:
    return (masses >= SIGNAL_YIELD_MIN) & (masses <= SIGNAL_YIELD_MAX)


def data_sideband_selection(masses: np.ndarray) -> np.ndarray:
    left_sideband = (masses > DATA_SB1_MIN) & (masses < DATA_SB1_MAX)
    right_sideband = (masses > DATA_SB2_MIN) & (masses < DATA_SB2_MAX)
    return left_sideband | right_sideband


def make_result(
    sample_type: str,
    channel: str,
    category: int | str,
    bdt_low: float,
    bdt_high: float,
    masses: np.ndarray,
    weights: np.ndarray,
    sigma_range: tuple[float, float],
    fraction: float,
) -> CategoryResult:
    if sample_type == "data":
        yield_value = float(masses.size)
        yield_uncertainty = float(np.sqrt(yield_value))

        eff_low = np.nan
        eff_high = np.nan
        sigma_eff = np.nan
        weight_mode = ""
    else:
        selected_weights = weights[signal_yield_selection(masses)]
        yield_value = float(np.sum(selected_weights))
        yield_uncertainty = float(np.sqrt(np.sum(selected_weights**2)))

        sigma_low_limit, sigma_high_limit = sigma_range
        sigma_selection = (
            (masses >= sigma_low_limit)
            & (masses <= sigma_high_limit)
        )
        eff_low, eff_high, sigma_eff, weight_mode = effective_sigma(
            masses[sigma_selection],
            weights[sigma_selection],
            fraction=fraction,
        )

    return CategoryResult(
        sample_type=sample_type,
        channel=channel,
        category=category,
        bdt_low=bdt_low,
        bdt_high=bdt_high,
        masses=masses,
        weights=weights,
        yield_value=yield_value,
        yield_uncertainty=yield_uncertainty,
        sigma_low=eff_low,
        sigma_high=eff_high,
        sigma_eff=sigma_eff,
        sigma_weight_mode=weight_mode,
    )


def load_channel_categories(
    file_path: Path,
    channel: str,
    cuts: np.ndarray,
    sample_type: str,
    sigma_range: tuple[float, float],
    fraction: float,
    step_size: str,
) -> list[CategoryResult]:
    bdt_branch = f"BDT_{channel}"
    channel_branch = f"is_{channel}_category"

    branches = [MASS_BRANCH, bdt_branch, channel_branch]
    if sample_type == "signal":
        branches.append(WEIGHT_BRANCH)

    if not file_path.is_file():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with ur.open(file_path, **UPROOT_OPEN) as root_file:
        if TREE_NAME not in root_file:
            raise KeyError(f"Tree '{TREE_NAME}' not found in {file_path}")

        available_branches = set(root_file[TREE_NAME].keys())
        missing = [branch for branch in branches if branch not in available_branches]

        if missing:
            raise KeyError(
                f"Missing branches in {file_path}: {', '.join(missing)}"
            )

    intervals = category_intervals(cuts)

    inclusive_masses: list[np.ndarray] = []
    inclusive_weights: list[np.ndarray] = []

    masses_by_category: dict[int, list[np.ndarray]] = {
        category: [] for category, *_ in intervals
    }
    weights_by_category: dict[int, list[np.ndarray]] = {
        category: [] for category, *_ in intervals
    }

    tree_path = f"{file_path}:{TREE_NAME}"

    for arrays in ur.iterate(
        tree_path,
        expressions=branches,
        library="np",
        step_size=step_size,
        **UPROOT_OPEN,
    ):
        masses = np.asarray(arrays[MASS_BRANCH], dtype=float)
        bdt_values = np.asarray(arrays[bdt_branch], dtype=float)
        is_channel = np.asarray(arrays[channel_branch]) == 1

        if sample_type == "signal":
            weights = np.asarray(arrays[WEIGHT_BRANCH], dtype=float)
            finite_event = np.isfinite(masses) & np.isfinite(weights)
        else:
            weights = np.ones(masses.size, dtype=float)
            finite_event = np.isfinite(masses)

        inclusive_selection = finite_event & is_channel

        if sample_type == "data":
            inclusive_selection &= data_sideband_selection(masses)

        category_base_selection = inclusive_selection & np.isfinite(bdt_values)

        if np.any(inclusive_selection):
            inclusive_masses.append(masses[inclusive_selection])
            inclusive_weights.append(weights[inclusive_selection])

        for category, low, high, include_high_edge in intervals:
            if include_high_edge:
                bdt_selection = (bdt_values >= low) & (bdt_values <= high)
            else:
                bdt_selection = (bdt_values >= low) & (bdt_values < high)

            selection = category_base_selection & bdt_selection

            if np.any(selection):
                masses_by_category[category].append(masses[selection])
                weights_by_category[category].append(weights[selection])

    if inclusive_masses:
        all_inclusive_masses = np.concatenate(inclusive_masses)
        all_inclusive_weights = np.concatenate(inclusive_weights)
    else:
        all_inclusive_masses = np.array([], dtype=float)
        all_inclusive_weights = np.array([], dtype=float)

    results = [
        make_result(
            sample_type=sample_type,
            channel=channel,
            category="inclusive",
            bdt_low=np.nan,
            bdt_high=np.nan,
            masses=all_inclusive_masses,
            weights=all_inclusive_weights,
            sigma_range=sigma_range,
            fraction=fraction,
        )
    ]

    for category, bdt_low, bdt_high, _ in intervals:
        if masses_by_category[category]:
            masses = np.concatenate(masses_by_category[category])
            weights = np.concatenate(weights_by_category[category])
        else:
            masses = np.array([], dtype=float)
            weights = np.array([], dtype=float)

        results.append(
            make_result(
                sample_type=sample_type,
                channel=channel,
                category=category,
                bdt_low=bdt_low,
                bdt_high=bdt_high,
                masses=masses,
                weights=weights,
                sigma_range=sigma_range,
                fraction=fraction,
            )
        )

    return results


def category_label(result: CategoryResult) -> str:
    if result.category == "inclusive":
        return rf"{result.channel} inclusive"

    upper_operator = r"\leq" if result.category == 1 else "<"

    return (
        rf"{result.channel}cat{result.category}: "
        rf"${result.bdt_low:.3g} \leq \mathrm{{BDT}} "
        rf"{upper_operator} {result.bdt_high:.3g}$"
    )


def draw_channel(
    results: list[CategoryResult],
    era: str,
    output_dir: Path,
    fraction: float,
    normalize: bool,
) -> None:
    if not results:
        return

    variable = MASS_BRANCH
    plot_range = tuple(x_range[variable])
    number_of_bins = int(n_bins[variable])
    bins = np.linspace(plot_range[0], plot_range[1], number_of_bins + 1)
    bin_width = bins[1] - bins[0]

    plt.style.use(hep.style.CMS)

    for result in results:
        is_data = result.sample_type == "data"
        is_inclusive = result.category == "inclusive"

        fig, ax = get_canvas(False)
        signal_color = plt.rcParams["axes.prop_cycle"].by_key()["color"][0]

        histogram, _ = np.histogram(
            result.masses,
            bins=bins,
            weights=result.weights,
        )
        histogram_errors = np.sqrt(
            np.histogram(
                result.masses,
                bins=bins,
                weights=result.weights**2,
            )[0]
        )

        if normalize:
            normalization = np.sum(histogram)
            if normalization != 0.0:
                histogram = histogram / normalization
                histogram_errors = histogram_errors / abs(normalization)

        if is_data:
            blinded_bins = (
                (bins[:-1] >= DATA_SB1_MAX)
                & (bins[1:] <= DATA_SB2_MIN)
            )
            histogram = histogram.astype(float, copy=True)
            histogram_errors = histogram_errors.astype(float, copy=True)
            histogram[blinded_bins] = np.nan
            histogram_errors[blinded_bins] = np.nan

        label = category_label(result)

        if (
            not is_data
            and np.isfinite(result.sigma_low)
            and np.isfinite(result.sigma_high)
        ):
            step_x = np.repeat(bins, 2)[1:-1]
            step_y = np.repeat(histogram, 2)
            in_sigma_interval = (
                (step_x >= result.sigma_low)
                & (step_x <= result.sigma_high)
            )
            sigma_label = (
                rf"$\sigma_{{\mathrm{{eff}}}}={result.sigma_eff:.3f}$ GeV "
                rf"[{result.sigma_low:.3f}, {result.sigma_high:.3f}]"
            )

            ax.fill_between(
                step_x,
                0.0,
                step_y,
                where=in_sigma_interval,
                interpolate=True,
                color=signal_color,
                alpha=0.20,
                linewidth=0.0,
                label=sigma_label,
                zorder=1,
            )

        if is_data:
            # Mark the signal region as blinded, but never draw data values in it.
            ax.axvspan(
                DATA_SB1_MAX,
                DATA_SB2_MIN,
                facecolor="0.85",
                edgecolor="0.55",
                alpha=0.55,
                hatch="//",
                linewidth=0.0,
                label="Blinded",
                zorder=0,
            )

            hep.histplot(
                histogram,
                bins,
                histtype="errorbar",
                yerr=histogram_errors,
                color="black",
                label=label,
                ax=ax,
                zorder=2,
            )
        else:
            hep.histplot(
                histogram,
                bins,
                histtype="step",
                yerr=False,
                linewidth=1.8,
                color=signal_color,
                label=label,
                ax=ax,
                zorder=2,
            )

        fig.subplots_adjust(top=0.88)

        hep.cms.label(
            "Preliminary",
            data=is_data,
            com="13.6",
            lumi=luminosity[era],
            ax=ax,
        )

        ax.set_xlim(*plot_range)
        ax.set_xlabel(x_labels[variable])

        if normalize:
            ax.set_ylabel(f"Normalized events / {bin_width:g} GeV")
        elif is_data:
            ax.set_ylabel(f"Events / {bin_width:g} GeV")
        else:
            ax.set_ylabel(f"Weighted events / {bin_width:g} GeV")

        ax.set_yscale("log")
        positive_bins = histogram[np.isfinite(histogram) & (histogram > 0.0)]

        if positive_bins.size:
            if is_data and not normalize:
                ax.set_ylim(0.5, 10.0 * np.max(positive_bins))
            else:
                ax.set_ylim(0.001, 10.0 * np.max(positive_bins))

        ax.legend(frameon=False, loc="upper right", fontsize=15)

        if is_data:
            sideband_text = (
                rf"$N_{{\mathrm{{SB}}}}={result.yield_value:.0f}"
                rf"\pm {result.yield_uncertainty:.2f}$"
                "\n"
                rf"${DATA_SB1_MIN:g}<m_{{\mu\mu}}<{DATA_SB1_MAX:g}$ GeV or"
                "\n"
                rf"${DATA_SB2_MIN:g}<m_{{\mu\mu}}<{DATA_SB2_MAX:g}$ GeV"
            )
            ax.text(
                0.97,
                0.08,
                sideband_text,
                transform=ax.transAxes,
                ha="right",
                va="bottom",
                fontsize=15,
            )
        else:
            yield_label = f"{SIGNAL_YIELD_MIN:g}-{SIGNAL_YIELD_MAX:g}"
            ax.text(
                0.85,
                0.9,
                (
                    rf"$Y_{{{yield_label}}}={result.yield_value:.3g} "
                    rf"\pm {result.yield_uncertainty:.3g}$"
                ),
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=15,
            )
            ax.text(
                0.45,
                0.98,
                rf"Narrowest interval containing {100.0 * fraction:.1f}%",
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=15,
            )

        category_name = (
            f"{result.channel}_inclusive"
            if is_inclusive
            else f"{result.channel}cat{result.category}"
        )

        if is_data:
            output_name = f"data_{category_name}_{variable}_sideband_yield"
        else:
            output_name = f"{category_name}_{variable}_effective_sigma"

        if normalize:
            output_name += "_normalized"

        save_figure(fig, str(output_dir) + os.sep, output_name)
        plt.close(fig)


def write_signal_summary(
    results: list[CategoryResult],
    output_path: Path,
) -> None:
    fieldnames = [
        "channel",
        "category",
        "bdt_low",
        "bdt_high",
        "n_selected_events",
        "yield_min_GeV",
        "yield_max_GeV",
        "yield",
        "yield_mcstat_uncertainty",
        "sigma_eff_low",
        "sigma_eff_high",
        "sigma_eff",
        "sigma_weight_mode",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            is_inclusive = result.category == "inclusive"
            writer.writerow(
                {
                    "channel": result.channel,
                    "category": result.category,
                    "bdt_low": "" if is_inclusive else result.bdt_low,
                    "bdt_high": "" if is_inclusive else result.bdt_high,
                    "n_selected_events": len(result.masses),
                    "yield_min_GeV": SIGNAL_YIELD_MIN,
                    "yield_max_GeV": SIGNAL_YIELD_MAX,
                    "yield": result.yield_value,
                    "yield_mcstat_uncertainty": result.yield_uncertainty,
                    "sigma_eff_low": result.sigma_low,
                    "sigma_eff_high": result.sigma_high,
                    "sigma_eff": result.sigma_eff,
                    "sigma_weight_mode": result.sigma_weight_mode,
                }
            )


def write_data_summary(
    results: list[CategoryResult],
    output_path: Path,
) -> None:
    fieldnames = [
        "channel",
        "category",
        "bdt_low",
        "bdt_high",
        "n_selected_events",
        "sideband_1_min_GeV",
        "sideband_1_max_GeV",
        "sideband_2_min_GeV",
        "sideband_2_max_GeV",
        "sideband_yield",
        "sideband_stat_uncertainty",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            is_inclusive = result.category == "inclusive"
            writer.writerow(
                {
                    "channel": result.channel,
                    "category": result.category,
                    "bdt_low": "" if is_inclusive else result.bdt_low,
                    "bdt_high": "" if is_inclusive else result.bdt_high,
                    "n_selected_events": len(result.masses),
                    "sideband_1_min_GeV": DATA_SB1_MIN,
                    "sideband_1_max_GeV": DATA_SB1_MAX,
                    "sideband_2_min_GeV": DATA_SB2_MIN,
                    "sideband_2_max_GeV": DATA_SB2_MAX,
                    "sideband_yield": int(result.yield_value),
                    "sideband_stat_uncertainty": result.yield_uncertainty,
                }
            )


def print_signal_summary(results: list[CategoryResult]) -> None:
    yield_header = (
        f"Yield [{SIGNAL_YIELD_MIN:g},{SIGNAL_YIELD_MAX:g}]"
    )
    header = (
        f"{'Category':<14} {'BDT interval':<22} {yield_header:>18} "
        f"{'sigma_eff interval [GeV]':>28} {'sigma_eff [GeV]':>17}"
    )

    print("\n" + header)
    print("-" * len(header))

    for result in results:
        if result.category == "inclusive":
            category_name = f"{result.channel} inclusive"
            bdt_interval = "No BDT cut"
        else:
            category_name = f"{result.channel}cat{result.category}"
            bdt_interval = (
                f"[{result.bdt_low:.5g}, {result.bdt_high:.5g}]"
            )

        yield_text = (
            f"{result.yield_value:.6g} +/- "
            f"{result.yield_uncertainty:.3g}"
        )
        sigma_interval = (
            f"[{result.sigma_low:.4f}, {result.sigma_high:.4f}]"
        )

        print(
            f"{category_name:<14} {bdt_interval:<22} {yield_text:>18} "
            f"{sigma_interval:>28} {result.sigma_eff:>17.4f}"
        )


def print_data_summary(results: list[CategoryResult]) -> None:
    sideband_header = (
        f"N({DATA_SB1_MIN:g}<m<{DATA_SB1_MAX:g} or "
        f"{DATA_SB2_MIN:g}<m<{DATA_SB2_MAX:g})"
    )
    header = (
        f"{'Category':<14} {'BDT interval':<22} "
        f"{sideband_header:>38} {'Stat. uncertainty':>20}"
    )

    print("\n" + header)
    print("-" * len(header))

    for result in results:
        if result.category == "inclusive":
            category_name = f"{result.channel} inclusive"
            bdt_interval = "No BDT cut"
        else:
            category_name = f"{result.channel}cat{result.category}"
            bdt_interval = (
                f"[{result.bdt_low:.5g}, {result.bdt_high:.5g}]"
            )

        print(
            f"{category_name:<14} {bdt_interval:<22} "
            f"{result.yield_value:>38.0f} "
            f"{result.yield_uncertainty:>20.3f}"
        )


def main() -> None:
    args = parse_args()
    sample_type = "data" if args.data else "signal"

    cuts_by_channel = {
        channel: validate_cuts(cuts, channel)
        for channel, cuts in bdt_cuts.items()
    }

    plot_range = tuple(float(value) for value in x_range[MASS_BRANCH])
    sigma_range = plot_range

    if SIGNAL_YIELD_MIN >= SIGNAL_YIELD_MAX:
        raise ValueError(
            "The signal yield range must satisfy "
            "SIGNAL_YIELD_MIN < SIGNAL_YIELD_MAX."
        )

    if not (
        DATA_SB1_MIN < DATA_SB1_MAX
        and DATA_SB2_MIN < DATA_SB2_MAX
        and DATA_SB1_MAX <= DATA_SB2_MIN
    ):
        raise ValueError("The data sideband boundaries are not valid.")

    input_file_name = (
        DATA_FILE_NAME if sample_type == "data" else SIGNAL_FILE_NAME
    )

    input_files = {
        "ggH": BASE_DIR / "ggH" / BDT_SUBSET / input_file_name,
        "VBF": BASE_DIR / "VBF" / BDT_SUBSET / input_file_name,
    }

    all_results: list[CategoryResult] = []

    for channel in ("ggH", "VBF"):
        print(f"\nReading {input_files[channel]}")

        channel_results = load_channel_categories(
            file_path=input_files[channel],
            channel=channel,
            cuts=cuts_by_channel[channel],
            sample_type=sample_type,
            sigma_range=sigma_range,
            fraction=EFFECTIVE_FRACTION,
            step_size=STEP_SIZE,
        )

        if sample_type == "data":
            print_data_summary(channel_results)
        else:
            print_signal_summary(channel_results)

        draw_channel(
            results=channel_results,
            era=ERA,
            output_dir=OUTPUT_DIR,
            fraction=EFFECTIVE_FRACTION,
            normalize=args.normalize,
        )
        all_results.extend(channel_results)

    if sample_type == "data":
        summary_path = OUTPUT_DIR / "data_sideband_yield_summary.csv"
        write_data_summary(all_results, summary_path)
    else:
        summary_path = OUTPUT_DIR / "signal_effective_sigma_summary.csv"
        write_signal_summary(all_results, summary_path)

    print(f"\nSummary written to {summary_path}")


if __name__ == "__main__":
    main()
