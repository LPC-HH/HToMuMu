#!/usr/bin/env python3
"""Calculate ggH/VBF signal cross-contamination in every BDT category.

For each categorization channel (ggH and VBF), this script reads the separate
ggH and VBF signal tuples from that channel's BDT-score directory and applies
the same selection to both samples.

Example for the ggH categorization:
    ggH inclusive / ggHcat1 / ... / ggHcat5

For every selection, the script calculates:
    * the signed weighted ggH yield;
    * the signed weighted VBF yield;
    * the combined ggH + VBF yield;
    * the fraction contributed by each process;
    * the contamination fraction:
        - VBF contamination in the ggH categorization;
        - ggH contamination in the VBF categorization;
    * MC statistical uncertainties from sqrt(sum(w^2)).

The inclusive selection requires only:
    is_<channel>_category == 1

The category selections additionally apply the configured BDT intervals.
The highest-score interval is cat1.

Negative weights are used exactly as stored. Fractions are not clipped, so in
the presence of strong signed-weight cancellations they may fall outside the
usual [0, 1] interval.

Run:
    python3 calculate_signal_contamination.py
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import uproot as ur

sys_path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))
from bdt_categories_io import load_bdt_categories, get_bdt_cuts

# Read the (tens of GB) BDT_score files in chunks rather than memory-mapping them whole:
# the whole-file map alone exceeds the 16 GiB per-process limit on the LPC login nodes.
UPROOT_OPEN = dict(file_handler=ur.MultithreadedFileSource)


MASS_BRANCH = "diMuon_bsConstrainedMass"
WEIGHT_BRANCH = "weight_no_eff_sf"
TREE_NAME = "tree_output"

BASE_DIR = Path("../root_io/tuples/BDT_score")
BASE_DIR = Path("../root_io/tuples/BDT_score/v1p7p0/")
BDT_SUBSET = "BFull_SNottH"
OUTPUT_DIR = Path("../plots/contamination")
STEP_SIZE = "500 MB"

# Signal mass window used for every yield.
SIGNAL_MIN = 123.5
SIGNAL_MAX = 126.5

# Files are resolved independently inside each BDT categorization directory:
#
#   BDT_score/ggH/BFull_SNottH/<file>
#   BDT_score/VBF/BFull_SNottH/<file>
#
PROCESS_FILE_NAMES = {
    "ggH": f"ggH_Combined_{BDT_SUBSET}.root",
    "VBF": f"VBF_Combined_{BDT_SUBSET}.root",
}

# BDT category boundaries in ascending score order.
# The highest-score interval is category 1.
ch_list = ["ggH", "VBF"]
bdt_cuts = {
    ch: get_bdt_cuts(bdt_categories_info, ch, "Combined", "BFull_SNottH", mass_variable)
} 


@dataclass
class WeightedYield:
    """Signed weighted yield and its MC statistical information."""

    sumw: float = 0.0
    sumw2: float = 0.0
    n_events: int = 0

    @property
    def uncertainty(self) -> float:
        return float(np.sqrt(self.sumw2))

    def add(self, weights: np.ndarray) -> None:
        weights = np.asarray(weights, dtype=float)
        self.sumw += float(np.sum(weights))
        self.sumw2 += float(np.sum(weights**2))
        self.n_events += int(weights.size)


@dataclass
class ContaminationResult:
    categorization: str
    category: int | str
    bdt_low: float
    bdt_high: float
    target_process: str
    contaminant_process: str
    ggh: WeightedYield
    vbf: WeightedYield
    total_yield: float
    total_uncertainty: float
    ggh_fraction: float
    vbf_fraction: float
    contamination_fraction: float
    contamination_fraction_uncertainty: float
    contamination_to_target_ratio: float


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
    number_of_categories = cuts.size - 1
    intervals: list[tuple[int, float, float, bool]] = []

    for category in range(1, number_of_categories + 1):
        interval_index = number_of_categories - category
        low = float(cuts[interval_index])
        high = float(cuts[interval_index + 1])

        # Only the highest interval includes its upper boundary, so a BDT score
        # of exactly 1.0 is retained without double-counting any other edge.
        include_high_edge = interval_index == number_of_categories - 1
        intervals.append((category, low, high, include_high_edge))

    return intervals


def initialize_accumulators(
    intervals: list[tuple[int, float, float, bool]],
) -> dict[int | str, WeightedYield]:
    accumulators: dict[int | str, WeightedYield] = {
        "inclusive": WeightedYield()
    }

    for category, *_ in intervals:
        accumulators[category] = WeightedYield()

    return accumulators


def load_process_yields(
    file_path: Path,
    categorization: str,
    cuts: np.ndarray,
) -> dict[int | str, WeightedYield]:
    """Calculate inclusive and category yields for one production process."""
    bdt_branch = f"BDT_{categorization}"
    category_branch = f"is_{categorization}_category"
    branches = [
        MASS_BRANCH,
        WEIGHT_BRANCH,
        bdt_branch,
        category_branch,
    ]

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
    yields = initialize_accumulators(intervals)
    tree_path = f"{file_path}:{TREE_NAME}"

    for arrays in ur.iterate(
        tree_path,
        expressions=branches,
        library="np",
        step_size=STEP_SIZE,
        **UPROOT_OPEN,
    ):
        masses = np.asarray(arrays[MASS_BRANCH], dtype=float)
        weights = np.asarray(arrays[WEIGHT_BRANCH], dtype=float)
        bdt_values = np.asarray(arrays[bdt_branch], dtype=float)
        is_category = np.asarray(arrays[category_branch]) == 1

        finite = (
            np.isfinite(masses)
            & np.isfinite(weights)
            & np.isfinite(bdt_values)
        )
        signal_window = (
            (masses >= SIGNAL_MIN)
            & (masses <= SIGNAL_MAX)
        )

        base_selection = finite & is_category & signal_window

        # Inclusive means is_<categorization>_category == 1 with no BDT cut.
        yields["inclusive"].add(weights[base_selection])

        for category, low, high, include_high_edge in intervals:
            if include_high_edge:
                bdt_selection = (bdt_values >= low) & (bdt_values <= high)
            else:
                bdt_selection = (bdt_values >= low) & (bdt_values < high)

            selection = base_selection & bdt_selection
            yields[category].add(weights[selection])

    return yields


def fraction_and_uncertainty(
    numerator: WeightedYield,
    other: WeightedYield,
) -> tuple[float, float]:
    """Return numerator/(numerator+other) and propagated MC uncertainty."""
    total = numerator.sumw + other.sumw

    if not np.isfinite(total) or total == 0.0:
        return np.nan, np.nan

    fraction = numerator.sumw / total

    # For f = N / (N + O):
    #   df/dN = O / (N + O)^2
    #   df/dO = -N / (N + O)^2
    #
    # The ggH and VBF samples are treated as statistically independent.
    derivative_numerator = other.sumw / total**2
    derivative_other = -numerator.sumw / total**2

    variance = (
        (derivative_numerator * numerator.uncertainty) ** 2
        + (derivative_other * other.uncertainty) ** 2
    )

    return float(fraction), float(np.sqrt(variance))


def build_results(
    categorization: str,
    cuts: np.ndarray,
    ggh_yields: dict[int | str, WeightedYield],
    vbf_yields: dict[int | str, WeightedYield],
) -> list[ContaminationResult]:
    intervals = category_intervals(cuts)

    selections: list[tuple[int | str, float, float]] = [
        ("inclusive", np.nan, np.nan)
    ]
    selections.extend(
        (category, low, high)
        for category, low, high, _ in intervals
    )

    target_process = categorization
    contaminant_process = "VBF" if categorization == "ggH" else "ggH"

    results: list[ContaminationResult] = []

    for category, bdt_low, bdt_high in selections:
        ggh = ggh_yields[category]
        vbf = vbf_yields[category]

        total_yield = ggh.sumw + vbf.sumw
        total_uncertainty = float(
            np.sqrt(ggh.sumw2 + vbf.sumw2)
        )

        ggh_fraction, _ = fraction_and_uncertainty(ggh, vbf)
        vbf_fraction, _ = fraction_and_uncertainty(vbf, ggh)

        if categorization == "ggH":
            contaminant = vbf
            target = ggh
        else:
            contaminant = ggh
            target = vbf

        contamination_fraction, contamination_uncertainty = (
            fraction_and_uncertainty(contaminant, target)
        )

        if target.sumw != 0.0:
            contamination_to_target_ratio = contaminant.sumw / target.sumw
        else:
            contamination_to_target_ratio = np.nan

        results.append(
            ContaminationResult(
                categorization=categorization,
                category=category,
                bdt_low=bdt_low,
                bdt_high=bdt_high,
                target_process=target_process,
                contaminant_process=contaminant_process,
                ggh=ggh,
                vbf=vbf,
                total_yield=total_yield,
                total_uncertainty=total_uncertainty,
                ggh_fraction=ggh_fraction,
                vbf_fraction=vbf_fraction,
                contamination_fraction=contamination_fraction,
                contamination_fraction_uncertainty=contamination_uncertainty,
                contamination_to_target_ratio=contamination_to_target_ratio,
            )
        )

    return results


def format_category(result: ContaminationResult) -> str:
    if result.category == "inclusive":
        return f"{result.categorization} inclusive"
    return f"{result.categorization}cat{result.category}"


def format_bdt_interval(result: ContaminationResult) -> str:
    if result.category == "inclusive":
        return "No BDT cut"

    right_bracket = "]" if result.category == 1 else ")"
    return f"[{result.bdt_low:.5g}, {result.bdt_high:.5g}{right_bracket}"


def print_results(results: list[ContaminationResult]) -> None:
    if not results:
        return

    categorization = results[0].categorization
    contaminant = results[0].contaminant_process

    print(
        f"\n{categorization} categorization: "
        f"{contaminant} is treated as the contamination"
    )

    header = (
        f"{'Selection':<16} "
        f"{'BDT interval':<22} "
        f"{'ggH yield':>20} "
        f"{'VBF yield':>20} "
        f"{'Total':>20} "
        f"{'Contamination':>20}"
    )
    print(header)
    print("-" * len(header))

    for result in results:
        ggh_text = (
            f"{result.ggh.sumw:.6g} +/- {result.ggh.uncertainty:.3g}"
        )
        vbf_text = (
            f"{result.vbf.sumw:.6g} +/- {result.vbf.uncertainty:.3g}"
        )
        total_text = (
            f"{result.total_yield:.6g} +/- "
            f"{result.total_uncertainty:.3g}"
        )

        if np.isfinite(result.contamination_fraction):
            contamination_text = (
                f"{100.0 * result.contamination_fraction:.3f}% +/- "
                f"{100.0 * result.contamination_fraction_uncertainty:.3f}%"
            )
        else:
            contamination_text = "nan"

        print(
            f"{format_category(result):<16} "
            f"{format_bdt_interval(result):<22} "
            f"{ggh_text:>20} "
            f"{vbf_text:>20} "
            f"{total_text:>20} "
            f"{contamination_text:>20}"
        )


def write_csv(
    results: list[ContaminationResult],
    output_path: Path,
) -> None:
    fieldnames = [
        "categorization",
        "category",
        "bdt_low",
        "bdt_high",
        "signal_min_GeV",
        "signal_max_GeV",
        "target_process",
        "contaminant_process",
        "ggH_n_events",
        "ggH_yield",
        "ggH_mcstat_uncertainty",
        "VBF_n_events",
        "VBF_yield",
        "VBF_mcstat_uncertainty",
        "total_yield",
        "total_mcstat_uncertainty",
        "ggH_fraction_of_total",
        "ggH_percent_of_total",
        "VBF_fraction_of_total",
        "VBF_percent_of_total",
        "contamination_fraction_of_total",
        "contamination_percent_of_total",
        "contamination_fraction_uncertainty",
        "contamination_percent_uncertainty",
        "contamination_to_target_ratio",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            is_inclusive = result.category == "inclusive"

            writer.writerow(
                {
                    "categorization": result.categorization,
                    "category": result.category,
                    "bdt_low": "" if is_inclusive else result.bdt_low,
                    "bdt_high": "" if is_inclusive else result.bdt_high,
                    "signal_min_GeV": SIGNAL_MIN,
                    "signal_max_GeV": SIGNAL_MAX,
                    "target_process": result.target_process,
                    "contaminant_process": result.contaminant_process,
                    "ggH_n_events": result.ggh.n_events,
                    "ggH_yield": result.ggh.sumw,
                    "ggH_mcstat_uncertainty": result.ggh.uncertainty,
                    "VBF_n_events": result.vbf.n_events,
                    "VBF_yield": result.vbf.sumw,
                    "VBF_mcstat_uncertainty": result.vbf.uncertainty,
                    "total_yield": result.total_yield,
                    "total_mcstat_uncertainty": result.total_uncertainty,
                    "ggH_fraction_of_total": result.ggh_fraction,
                    "ggH_percent_of_total": 100.0 * result.ggh_fraction,
                    "VBF_fraction_of_total": result.vbf_fraction,
                    "VBF_percent_of_total": 100.0 * result.vbf_fraction,
                    "contamination_fraction_of_total": (
                        result.contamination_fraction
                    ),
                    "contamination_percent_of_total": (
                        100.0 * result.contamination_fraction
                    ),
                    "contamination_fraction_uncertainty": (
                        result.contamination_fraction_uncertainty
                    ),
                    "contamination_percent_uncertainty": (
                        100.0 * result.contamination_fraction_uncertainty
                    ),
                    "contamination_to_target_ratio": (
                        result.contamination_to_target_ratio
                    ),
                }
            )


def main() -> None:
    if SIGNAL_MIN >= SIGNAL_MAX:
        raise ValueError("The signal window must satisfy SIGNAL_MIN < SIGNAL_MAX.")

    cuts_by_channel = {
        channel: validate_cuts(cuts, channel)
        for channel, cuts in bdt_cuts.items()
    }

    all_results: list[ContaminationResult] = []

    for categorization in ("ggH", "VBF"):
        input_dir = BASE_DIR / categorization / BDT_SUBSET

        process_paths = {
            process: input_dir / file_name
            for process, file_name in PROCESS_FILE_NAMES.items()
        }

        print(f"\nReading {categorization} categorization")
        print(f"  ggH: {process_paths['ggH']}")
        print(f"  VBF: {process_paths['VBF']}")

        ggh_yields = load_process_yields(
            file_path=process_paths["ggH"],
            categorization=categorization,
            cuts=cuts_by_channel[categorization],
        )
        vbf_yields = load_process_yields(
            file_path=process_paths["VBF"],
            categorization=categorization,
            cuts=cuts_by_channel[categorization],
        )

        results = build_results(
            categorization=categorization,
            cuts=cuts_by_channel[categorization],
            ggh_yields=ggh_yields,
            vbf_yields=vbf_yields,
        )

        print_results(results)
        all_results.extend(results)

    output_path = OUTPUT_DIR / "signal_contamination_summary.csv"
    write_csv(all_results, output_path)

    print(f"\nSummary written to {output_path}")
    print(
        "Note: all yields and fractions use signed weight_no_eff_sf values "
        "without clipping negative weights."
    )


if __name__ == "__main__":
    main()
