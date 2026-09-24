"""Shared helpers for filling inclusive or BDT-category ROOT histograms."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Mapping, NamedTuple, Optional, Sequence, Tuple

import numpy as np
import uproot as ur

# Read the (tens of GB) BDT_score files in chunks rather than memory-mapping them whole:
# the whole-file map alone exceeds the 16 GiB per-process limit on the LPC login nodes.
UPROOT_OPEN = dict(file_handler=ur.MultithreadedFileSource)


TREE_NAME = "tree_output"
INCLUSIVE_SELECTION_KEY = "inclusive"

# Systematic tuples with recomputed BDT scores are stored below the base
# systematics input directory. The directory is selected by the BDT category
# family being plotted, not by the production sample.
DEFAULT_BDT_NOMINAL_SUBDIRECTORIES = {
    "ggH": Path("BDT_score/ggH/BFull_SNottH"),
    "VBF": Path("BDT_score/VBF/BFull_SNottH"),
}

DEFAULT_BDT_NANOAOD_SUBDIRECTORIES = {
    "ggH": Path("BDT_score/ggH/BFull_SNottH"),
    "VBF": Path("BDT_score/VBF/BFull_SNottH"),
}

DEFAULT_BDT_SYSTEMATICS_SUBDIRECTORIES = {
    "ggH": Path("BDT_score/ggH/BFull_SNottH"),
    "VBF": Path("BDT_score/VBF/BFull_SNottH"),
}

FailureRecord = Tuple[Path, str]
Histogram = Tuple[np.ndarray, np.ndarray]
HistogramSet = Dict[str, Histogram]
GroupedHistograms = Dict[str, HistogramSet]


class CategorySelection(NamedTuple):
    """One inclusive or BDT-category event selection."""

    key: str
    display_name: Optional[str]
    category_branch: Optional[str]
    score_branch: Optional[str]
    lower_bdt: Optional[float]
    upper_bdt: Optional[float]
    include_upper_edge: bool


def _inclusive_category_branch(production_channel: str) -> Optional[str]:
    if production_channel == "ggH":
        return "is_ggH_category"
    if production_channel == "VBF":
        return "is_VBF_category"
    return None


def build_category_selections(
    production_channel: str,
    bdt_cuts: Optional[Mapping[str, Sequence[float]]] = None,
    bdt_category_channels: Sequence[str] = ("ggH", "VBF"),
) -> List[CategorySelection]:
    """Build all BDT categories, or preserve the previous inclusive behavior.

    Category numbering is reversed relative to the cut-list index: the
    highest-score interval is category 1 and the lowest-score interval is
    category N. All intervals use ``lower <= score < upper`` except the final
    highest-score interval, which includes its upper edge so score == 1 is kept.
    """

    if not bdt_cuts:
        return [
            CategorySelection(
                key=INCLUSIVE_SELECTION_KEY,
                display_name=None,
                category_branch=_inclusive_category_branch(production_channel),
                score_branch=None,
                lower_bdt=None,
                upper_bdt=None,
                include_upper_edge=False,
            )
        ]

    selections: List[CategorySelection] = []
    for category_channel in bdt_category_channels:
        if category_channel not in bdt_cuts:
            raise KeyError(
                f"Missing BDT cuts for category channel '{category_channel}'."
            )

        cuts = [float(value) for value in bdt_cuts[category_channel]]
        if len(cuts) < 2:
            raise ValueError(
                f"At least two BDT boundaries are required for "
                f"'{category_channel}'."
            )
        if any(upper <= lower for lower, upper in zip(cuts, cuts[1:])):
            raise ValueError(
                f"BDT boundaries for '{category_channel}' must be strictly "
                "increasing."
            )

        number_of_categories = len(cuts) - 1
        for category_index in range(number_of_categories):
            category_number = number_of_categories - category_index
            category_name = f"{category_channel}cat{category_number}"
            selections.append(
                CategorySelection(
                    key=category_name,
                    display_name=category_name,
                    category_branch=f"is_{category_channel}_category",
                    score_branch=f"BDT_{category_channel}",
                    lower_bdt=cuts[category_index],
                    upper_bdt=cuts[category_index + 1],
                    include_upper_edge=(category_index == number_of_categories - 1),
                )
            )

    return selections


def selection_branches(
    selections: Sequence[CategorySelection],
) -> List[str]:
    """Return unique ROOT branches needed to evaluate all selections."""

    branches: List[str] = []
    for selection in selections:
        if selection.category_branch is not None:
            branches.append(selection.category_branch)
        if selection.score_branch is not None:
            branches.append(selection.score_branch)
    return list(dict.fromkeys(branches))


def category_channel_for_selection(
    selection: CategorySelection,
) -> Optional[str]:
    """Return the BDT family (ggH/VBF) associated with a selection."""

    if selection.score_branch is None:
        return None
    if not selection.score_branch.startswith("BDT_"):
        raise ValueError(
            f"Cannot infer category channel from score branch "
            f"'{selection.score_branch}'."
        )
    return selection.score_branch.removeprefix("BDT_")


def group_selections_by_category_channel(
    selections: Sequence[CategorySelection],
) -> Dict[Optional[str], List[CategorySelection]]:
    """Group selections so each BDT-score directory is read only once."""

    grouped: Dict[Optional[str], List[CategorySelection]] = {}
    for selection in selections:
        category_channel = category_channel_for_selection(selection)
        grouped.setdefault(category_channel, []).append(selection)
    return grouped


def resolve_category_nominal_file(
    nominal_file: Path,
    production_channel: str,
    category_channel: Optional[str],
    bdt_nominal_subdirectories: Optional[Mapping[str, Path]] = None,
) -> Path:
    """Resolve the nominal tuple for one inclusive/BDT category family.

    Inclusive plots use ``nominal_file`` directly. BDT-category plots use the
    scored nominal tuple below ``nominal_file.parent``. The directory is chosen
    by the BDT category family, while the filename is chosen by the production
    sample being plotted.
    """

    nominal_file = Path(nominal_file).expanduser().resolve()
    if category_channel is None:
        return nominal_file

    subdirectories = dict(DEFAULT_BDT_NOMINAL_SUBDIRECTORIES)
    if bdt_nominal_subdirectories is not None:
        subdirectories.update(
            {
                str(channel): Path(path)
                for channel, path in bdt_nominal_subdirectories.items()
            }
        )

    if category_channel not in subdirectories:
        raise KeyError(
            f"Missing nominal subdirectory for BDT category channel "
            f"'{category_channel}'."
        )

    subdirectory = Path(subdirectories[category_channel])
    if subdirectory.is_absolute():
        category_directory = subdirectory.resolve()
    else:
        category_directory = (nominal_file.parent / subdirectory).resolve()

    if production_channel.strip().lower() == "data":
        filename = "data_Combined.root"
    else:
        filename = f"{production_channel}_Combined_BFull_SNottH.root"

    return category_directory / filename



def resolve_category_nanoaod_file(
    nanoaod_file: Path,
    production_channel: str,
    category_channel: Optional[str],
    bdt_nanoaod_subdirectories: Optional[Mapping[str, Path]] = None,
) -> Path:
    """Resolve the separate NanoAOD-reference tuple for one category family.

    Inclusive plots use ``nanoaod_file`` directly. BDT-category plots use a
    same-named scored tuple below ``nanoaod_file.parent``. The branch names in
    this file are the ordinary variable names, not ``*_nanoAOD`` branches.
    """

    nanoaod_file = Path(nanoaod_file).expanduser().resolve()
    if category_channel is None:
        return nanoaod_file

    subdirectories = dict(DEFAULT_BDT_NANOAOD_SUBDIRECTORIES)
    if bdt_nanoaod_subdirectories is not None:
        subdirectories.update(
            {
                str(channel): Path(path)
                for channel, path in bdt_nanoaod_subdirectories.items()
            }
        )

    if category_channel not in subdirectories:
        raise KeyError(
            f"Missing NanoAOD subdirectory for BDT category channel "
            f"'{category_channel}'."
        )

    subdirectory = Path(subdirectories[category_channel])
    if subdirectory.is_absolute():
        category_directory = subdirectory.resolve()
    else:
        category_directory = (nanoaod_file.parent / subdirectory).resolve()

    if production_channel.strip().lower() == "data":
        filename = "data_Combined.root"
    else:
        filename = f"{production_channel}_Combined_BFull_SNottH.root"

    return category_directory / filename

def resolve_category_systematics_directory(
    systematics_directory: Path,
    category_channel: Optional[str],
    bdt_systematics_subdirectories: Optional[Mapping[str, Path]] = None,
) -> Path:
    """Resolve the systematic input directory for one category family.

    Inclusive plots use ``systematics_directory`` directly. BDT-category plots
    use a category-specific path relative to that base directory.
    """

    base_directory = Path(systematics_directory).expanduser().resolve()
    if category_channel is None:
        return base_directory

    subdirectories = dict(DEFAULT_BDT_SYSTEMATICS_SUBDIRECTORIES)
    if bdt_systematics_subdirectories is not None:
        subdirectories.update(
            {
                str(channel): Path(path)
                for channel, path in bdt_systematics_subdirectories.items()
            }
        )

    if category_channel not in subdirectories:
        raise KeyError(
            f"Missing systematic subdirectory for BDT category channel "
            f"'{category_channel}'."
        )

    subdirectory = Path(subdirectories[category_channel])
    if subdirectory.is_absolute():
        return subdirectory.resolve()
    return (base_directory / subdirectory).resolve()


def selection_mask(
    arrays: Mapping[str, np.ndarray],
    selection: CategorySelection,
    number_of_events: int,
) -> np.ndarray:
    """Evaluate one inclusive/category selection for an uproot chunk."""

    mask = np.ones(number_of_events, dtype=bool)

    if selection.category_branch is not None:
        mask &= arrays[selection.category_branch] == 1

    if selection.score_branch is not None:
        score = arrays[selection.score_branch]
        mask &= np.isfinite(score)
        mask &= score >= selection.lower_bdt
        if selection.include_upper_edge:
            mask &= score <= selection.upper_bdt
        else:
            mask &= score < selection.upper_bdt

    return mask


def append_failure(
    failed_files: List[FailureRecord],
    file_path: Path,
    reason: str,
) -> None:
    """Store a failed tuple path and a one-line explanation."""

    clean_reason = " ".join(str(reason).split())
    failed_files.append((Path(file_path), clean_reason))


def validate_tuple_file(
    file_path: Path,
    required_branches: Iterable[str],
) -> Tuple[bool, str]:
    """Check that a ROOT file opens and contains the requested tuple tree."""

    file_path = Path(file_path)
    if not file_path.is_file():
        return False, "file does not exist"

    try:
        with ur.open(file_path, **UPROOT_OPEN) as root_file:
            if TREE_NAME not in root_file:
                return False, f"missing TTree '{TREE_NAME}'"

            available_branches = set(root_file[TREE_NAME].keys())
            missing_branches = [
                branch
                for branch in dict.fromkeys(required_branches)
                if branch not in available_branches
            ]
            if missing_branches:
                return False, "missing branch(es): " + ", ".join(missing_branches)
    except Exception as error:
        return False, f"cannot open/read ROOT file: {type(error).__name__}: {error}"

    return True, ""


def write_failure_report(
    output_directory: Path,
    production_channel: str,
    failed_files: List[FailureRecord],
) -> None:
    """Write and print the files skipped while processing one sample."""

    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    report_path = output_directory / "failed_tuple_files.txt"

    unique_failures: List[FailureRecord] = []
    seen = set()
    for file_path, reason in failed_files:
        key = (str(file_path), reason)
        if key not in seen:
            seen.add(key)
            unique_failures.append((file_path, reason))

    if not unique_failures:
        if report_path.exists():
            report_path.unlink()
        print(f"No tuple files failed for {production_channel}.")
        return

    with report_path.open("w", encoding="utf-8") as report:
        report.write(f"Sample: {production_channel}\n")
        report.write(f"Failed tuple files: {len(unique_failures)}\n\n")
        for file_path, reason in unique_failures:
            report.write(f"{file_path}\n")
            report.write(f"  Reason: {reason}\n\n")

    print("\nFailed tuple files:")
    for file_path, reason in unique_failures:
        print(f"  - {file_path}")
        print(f"    Reason: {reason}")
    print(f"Failure report: {report_path}")


def get_requested_systematic_pairs(
    production_channel: str,
    systematics_directory: Path,
    systematic_names: Sequence[str],
    failed_files: Optional[List[FailureRecord]] = None,
) -> Dict[str, Tuple[Path, Path]]:
    """Return complete up/down file pairs for requested systematic names."""

    systematics_directory = Path(systematics_directory).expanduser().resolve()
    if not systematics_directory.is_dir():
        raise NotADirectoryError(
            f"Systematics directory not found: {systematics_directory}"
        )

    pairs: Dict[str, Tuple[Path, Path]] = {}
    for systematic_name in dict.fromkeys(systematic_names):
        prefix = f"{production_channel}_Combined_{systematic_name}"
        up_file = systematics_directory / f"{prefix}_up_tuples.root"
        down_file = systematics_directory / f"{prefix}_down_tuples.root"

        missing_files = [
            path for path in (up_file, down_file) if not path.is_file()
        ]
        if missing_files:
            print(
                f"[WARNING] Skipping {production_channel} / {systematic_name}: "
                "missing variation file(s):"
            )
            for missing_file in missing_files:
                print(f"          {missing_file}")
                if failed_files is not None:
                    append_failure(
                        failed_files,
                        missing_file,
                        "file does not exist",
                    )
            continue

        pairs[systematic_name] = (up_file, down_file)

    return pairs


def initialize_grouped_histograms(
    variables: Sequence[str],
    selections: Sequence[CategorySelection],
    bins_by_variable: Mapping[str, np.ndarray],
) -> Dict[str, Dict[str, np.ndarray]]:
    """Allocate one histogram per variable and category selection."""

    return {
        selection.key: {
            variable: np.zeros(len(bins_by_variable[variable]) - 1, dtype=float)
            for variable in variables
        }
        for selection in selections
    }


def finalize_grouped_histograms(
    histograms: Dict[str, Dict[str, np.ndarray]],
    bins_by_variable: Mapping[str, np.ndarray],
    normalize: bool,
    source_name: str,
) -> GroupedHistograms:
    """Attach bins and optionally normalize each category independently."""

    output: GroupedHistograms = {}
    for selection_key, variable_histograms in histograms.items():
        output[selection_key] = {}
        for variable, histogram in variable_histograms.items():
            if normalize:
                integral = np.sum(histogram)
                if integral > 0.0:
                    histogram = histogram / integral
                else:
                    print(
                        f"[WARNING] Cannot normalize {source_name} / "
                        f"{selection_key} / {variable}: integral is zero."
                    )
            output[selection_key][variable] = (
                histogram,
                bins_by_variable[variable],
            )
    return output


def _valid_values(
    values: np.ndarray,
    minimum_value: float,
    include_minimum: bool,
) -> np.ndarray:
    valid = np.isfinite(values)
    if include_minimum:
        valid &= values >= minimum_value
    else:
        valid &= values > minimum_value
    return valid

def _outside_blind_mass_window(
    arrays: Mapping[str, np.ndarray],
    number_of_events: int,
    blind_mass_window: Optional[Tuple[float, float]],
    blind_mass_branch: str,
) -> np.ndarray:
    """Return an event mask excluding the requested dimuon-mass window."""

    mask = np.ones(number_of_events, dtype=bool)

    if blind_mass_window is None:
        return mask

    lower_mass, upper_mass = map(float, blind_mass_window)

    if upper_mass <= lower_mass:
        raise ValueError(
            "The upper blinding boundary must be greater than the lower one."
        )

    mass = arrays[blind_mass_branch]

    mask &= np.isfinite(mass)

    # Blind the complete closed interval:
    # lower_mass <= mass <= upper_mass
    mask &= (mass < lower_mass) | (mass > upper_mass)

    return mask



def read_nominal_and_nanoaod_branch_histograms(
    file_path: Path,
    variables: Sequence[str],
    selections: Sequence[CategorySelection],
    bins_by_variable: Mapping[str, np.ndarray],
    normalize: bool,
    use_weights: bool,
    minimum_value: float,
    include_minimum: bool,
    blind_mass_window: Optional[Tuple[float, float]] = None,
    blind_mass_branch: str = "diMuon_bsConstrainedMass",
) -> Tuple[GroupedHistograms, GroupedHistograms]:
    """Read nominal and ``*_nanoAOD`` branches from the same ROOT file.

    This compatibility function is used by the jet workflow. The muon workflow
    continues to use :func:`read_nominal_and_nanoaod_histograms`, which reads
    the nominal and NanoAOD reference distributions from two separate files.
    """

    nanoaod_branches = {
        variable: f"{variable}_nanoAOD" for variable in variables
    }
    branches_to_read = [
        *variables,
        *nanoaod_branches.values(),
        *selection_branches(selections),
    ]
    if use_weights:
        branches_to_read.append("weight")
    branches_to_read = list(dict.fromkeys(branches_to_read))

    nominal_histograms = initialize_grouped_histograms(
        variables,
        selections,
        bins_by_variable,
    )
    nanoaod_histograms = initialize_grouped_histograms(
        variables,
        selections,
        bins_by_variable,
    )

    tree_path = f"{Path(file_path)}:{TREE_NAME}"
    for arrays in ur.iterate(
        tree_path,
        branches_to_read,
        library="np",
        step_size="50 MB",
        **UPROOT_OPEN,
    ):
        number_of_events = len(arrays[variables[0]])
        if use_weights:
            weights = arrays["weight"]
            valid_weight = np.isfinite(weights)
        else:
            weights = np.ones(number_of_events, dtype=float)
            valid_weight = np.ones(number_of_events, dtype=bool)

        masks = {
            selection.key: selection_mask(arrays, selection, number_of_events)
            for selection in selections
        }

        for variable in variables:
            nominal_values = arrays[variable]
            nanoaod_values = arrays[nanoaod_branches[variable]]
            nominal_value_mask = _valid_values(
                nominal_values,
                minimum_value,
                include_minimum,
            )
            nanoaod_value_mask = _valid_values(
                nanoaod_values,
                minimum_value,
                include_minimum,
            )

            for selection in selections:
                base_mask = valid_weight & masks[selection.key]
                nominal_valid = base_mask & nominal_value_mask
                nanoaod_valid = base_mask & nanoaod_value_mask

                nominal_chunk, _ = np.histogram(
                    nominal_values[nominal_valid],
                    bins=bins_by_variable[variable],
                    weights=weights[nominal_valid],
                )
                nanoaod_chunk, _ = np.histogram(
                    nanoaod_values[nanoaod_valid],
                    bins=bins_by_variable[variable],
                    weights=weights[nanoaod_valid],
                )
                nominal_histograms[selection.key][variable] += nominal_chunk
                nanoaod_histograms[selection.key][variable] += nanoaod_chunk

    return (
        finalize_grouped_histograms(
            nominal_histograms,
            bins_by_variable,
            normalize,
            "nominal",
        ),
        finalize_grouped_histograms(
            nanoaod_histograms,
            bins_by_variable,
            normalize,
            "NanoAOD",
        ),
    )


def read_nominal_and_nanoaod_histograms(
    nominal_file_path: Path,
    nanoaod_file_path: Path,
    variables: Sequence[str],
    selections: Sequence[CategorySelection],
    bins_by_variable: Mapping[str, np.ndarray],
    normalize: bool,
    use_weights: bool,
    minimum_value: float,
    include_minimum: bool,
    blind_mass_window: Optional[Tuple[float, float]] = None,
    blind_mass_branch: str = "diMuon_bsConstrainedMass",
) -> Tuple[GroupedHistograms, GroupedHistograms]:
    """Read nominal and NanoAOD-reference histograms from separate files."""

    nominal_histograms = read_variation_histograms(
        nominal_file_path,
        variables,
        selections,
        bins_by_variable,
        normalize,
        use_weights,
        minimum_value,
        include_minimum,
        blind_mass_window=blind_mass_window,
        blind_mass_branch=blind_mass_branch,
    )

    nanoaod_histograms = read_variation_histograms(
        nanoaod_file_path,
        variables,
        selections,
        bins_by_variable,
        normalize,
        use_weights,
        minimum_value,
        include_minimum,
        blind_mass_window=blind_mass_window,
        blind_mass_branch=blind_mass_branch,
    )

    return nominal_histograms, nanoaod_histograms

def read_variation_histograms(
    file_path: Path,
    variables: Sequence[str],
    selections: Sequence[CategorySelection],
    bins_by_variable: Mapping[str, np.ndarray],
    normalize: bool,
    use_weights: bool,
    minimum_value: float,
    include_minimum: bool,
    blind_mass_window: Optional[Tuple[float, float]] = None,
    blind_mass_branch: str = "diMuon_bsConstrainedMass",
) -> GroupedHistograms:
    """Read all requested categories from one variation file in one pass."""

    branches_to_read = [*variables, *selection_branches(selections)]

    if blind_mass_window is not None:
        branches_to_read.append(blind_mass_branch)

    if use_weights:
        branches_to_read.append("weight")

    branches_to_read = list(dict.fromkeys(branches_to_read))

    histograms = initialize_grouped_histograms(
        variables,
        selections,
        bins_by_variable,
    )

    tree_path = f"{Path(file_path)}:{TREE_NAME}"
    for arrays in ur.iterate(
        tree_path,
        branches_to_read,
        library="np",
        step_size="50 MB",
        **UPROOT_OPEN,
    ):
        number_of_events = len(arrays[variables[0]])
        if use_weights:
            weights = arrays["weight"]
            valid_weight = np.isfinite(weights)
        else:
            weights = np.ones(number_of_events, dtype=float)
            valid_weight = np.ones(number_of_events, dtype=bool)

        blind_mass_mask = _outside_blind_mass_window(
            arrays,
            number_of_events,
            blind_mass_window,
            blind_mass_branch,
        )

        masks = {
            selection.key: selection_mask(arrays, selection, number_of_events)
            for selection in selections
        }

        for variable in variables:
            values = arrays[variable]
            value_mask = _valid_values(
                values,
                minimum_value,
                include_minimum,
            )

            for selection in selections:
                valid = (
                    valid_weight
                    & blind_mass_mask
                    & masks[selection.key]
                    & value_mask
                )

                chunk_histogram, _ = np.histogram(
                    values[valid],
                    bins=bins_by_variable[variable],
                    weights=weights[valid],
                )

                histograms[selection.key][variable] += chunk_histogram

    return finalize_grouped_histograms(
        histograms,
        bins_by_variable,
        normalize,
        str(file_path),
    )


def relative_difference(
    variation: np.ndarray,
    nominal: np.ndarray,
) -> np.ndarray:
    """Calculate ``(variation - nominal) / nominal`` safely."""

    difference = np.full(nominal.shape, np.nan, dtype=float)
    valid = (
        np.isfinite(nominal)
        & np.isfinite(variation)
        & (nominal != 0.0)
    )
    np.divide(
        variation - nominal,
        nominal,
        out=difference,
        where=valid,
    )
    return difference


def category_output_directory(
    output_directory: Path,
    category_name: Optional[str],
) -> Path:
    """Put each BDT category in its own subdirectory."""

    output_directory = Path(output_directory)
    if category_name is not None:
        output_directory = output_directory / category_name
    output_directory.mkdir(parents=True, exist_ok=True)
    return output_directory
