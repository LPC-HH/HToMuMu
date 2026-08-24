#!/usr/bin/env python3
"""Plot the effect of removing muon trigger/ID/ISO efficiency scale factors."""

from __future__ import annotations

import os
from pathlib import Path

os.environ["MPLBACKEND"] = "Agg"

from utils.muon_eff_sf import draw_all_efficiency_sf_comparisons


# -----------------------------------------------------------------------------
# User configuration
# -----------------------------------------------------------------------------

NOMINAL_TUPLE_DIRECTORY = Path(__file__).resolve().parent / "../root_io/tuples"

OUTPUT_BASE_DIRECTORY = (
    Path(__file__).resolve().parent / "../plots/systematics/muon_eff_sf"
)

# MC samples only. Add/remove samples here as needed.
CHANNELS = [
    "signal",
    "ggH",
    "VBF",
    "DY",
]

# True: make ggHcat1-5 and VBFcat1-5 plots.
# False: use the old inclusive selection behavior.
DO_BDT_CATEGORIES = False

BDT_CATEGORY_CHANNELS = [
    "ggH",
    "VBF",
]

BDT_CUTS = {
    "ggH": [
        0.0,
        0.4300000000000002,
        0.6000000000000003,
        0.7100000000000004,
        0.8100000000000005,
        0.9100000000000006,
        1.0,
    ],
    "VBF": [
        0.0,
        0.646666666666667,
        0.8200000000000014,
        0.8866666666666685,
        0.9466666666666689,
        0.9600000000000023,
        1.0,
    ],
}

# Relative to NOMINAL_TUPLE_DIRECTORY.  These are the nominal tuples that
# already contain the BDT scores used for category assignment.
BDT_NOMINAL_SUBDIRECTORIES = {
    "ggH": Path("BDT_score/ggH/BFull_SNottH"),
    "VBF": Path("BDT_score/VBF/BFull_SNottH"),
}

# False: compare weighted event yields.
# True: normalize every one of the five histograms independently.
NORMALIZE_HISTOGRAMS = False


# -----------------------------------------------------------------------------
# Plot production
# -----------------------------------------------------------------------------


def main() -> None:
    nominal_directory = NOMINAL_TUPLE_DIRECTORY.resolve()
    output_base_directory = OUTPUT_BASE_DIRECTORY.resolve()

    if not nominal_directory.is_dir():
        raise NotADirectoryError(
            f"Nominal tuple directory not found: {nominal_directory}"
        )

    if not CHANNELS:
        raise ValueError("CHANNELS is empty. Add at least one MC sample.")

    print(f"Nominal directory:    {nominal_directory}")
    print(f"Output base directory:{output_base_directory}")
    print(f"Channels:             {', '.join(CHANNELS)}")
    print(f"Do BDT categories:    {DO_BDT_CATEGORIES}")

    total_plots = 0

    for channel in CHANNELS:
        if channel.strip().lower() == "data":
            print("[WARNING] Skipping Data: efficiency SFs apply to MC.")
            continue

        nominal_file = nominal_directory / f"{channel}_Combined_tuples.root"
        output_directory = output_base_directory / channel

        if not DO_BDT_CATEGORIES and not nominal_file.is_file():
            print(
                f"[WARNING] Skipping {channel}: nominal tuple not found: "
                f"{nominal_file}"
            )
            continue

        print("\n" + "=" * 80)
        print(f"Processing channel: {channel}")
        if DO_BDT_CATEGORIES:
            print(f"Nominal input base: {nominal_directory}")
            print("Tuple file:         selected by BDT category family")
        else:
            print(f"Nominal tuple:      {nominal_file}")
        print(f"Output directory:   {output_directory}")
        print("=" * 80)

        channel_plots = draw_all_efficiency_sf_comparisons(
            production_channel=channel,
            nominal_file=nominal_file,
            output_directory=output_directory,
            normalize=NORMALIZE_HISTOGRAMS,
            bdt_cuts=BDT_CUTS if DO_BDT_CATEGORIES else None,
            bdt_category_channels=BDT_CATEGORY_CHANNELS,
            bdt_nominal_subdirectories=(
                BDT_NOMINAL_SUBDIRECTORIES
                if DO_BDT_CATEGORIES
                else None
            ),
        )

        total_plots += channel_plots
        print(f"Created {channel_plots} plot(s) for {channel}")

    print("\n" + "=" * 80)
    print(f"Finished. Created {total_plots} plot(s) in total.")
    if DO_BDT_CATEGORIES:
        print(
            "Plots are under: "
            f"{output_base_directory}/<sample>/<BDT category>/"
        )
    else:
        print(f"Plots are under: {output_base_directory}/<sample>/")


if __name__ == "__main__":
    main()
