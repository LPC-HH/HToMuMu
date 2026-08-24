#!/usr/bin/env python3
"""Make nominal/up/down plots for muon momentum corrections.

Run this script from any directory with

    python3 plot_muon_pt_sys.py

Edit DO_BDT_CATEGORIES, CHANNELS, and SYSTEMATICS below.
"""

from __future__ import annotations

import os

# Use a non-interactive Matplotlib backend on LPC/batch machines.
os.environ["MPLBACKEND"] = "Agg"

from pathlib import Path

from utils.muon_pt_sys import draw_all_muon_systematics


# -----------------------------------------------------------------------------
# User configuration
# -----------------------------------------------------------------------------

# Nominal tuples are stored inside the repository. The path is resolved relative
# to this script, not relative to the directory from which Python is launched.
NOMINAL_TUPLE_DIRECTORY = Path(__file__).resolve().parent / "../root_io/tuples"

# NanoAOD-reference tuples are separate older tuples. They use the same variable
# branch names as the nominal tuples (no ``*_nanoAOD`` suffix).
NANOAOD_TUPLE_DIRECTORY = (
    Path(__file__).resolve().parent / "../root_io/tuples/v1p5"
)

# Systematic tuples are stored on EOS.
SYSTEMATICS_DIRECTORY = Path(
    "/eos/uscms/store/user/lpchmumu/mbarrial/"
    "analyzer_HiggsMuMu_v1.6/tuples_v1.6.1/systematics"
)

# Plots always go to ../plots/systematics/muon_pt/<channel>/.
OUTPUT_BASE_DIRECTORY = (
    Path(__file__).resolve().parent / "../plots/systematics/muon_pt"
)

# Edit this list to select the production channels to process.
CHANNELS = [
    "signal",
    "Data",
#    "ggH",
#    "VBF",
]

# True: split every configured sample into ggHcat1-5 and VBFcat1-5.
# False: keep the previous inclusive category selection.
DO_BDT_CATEGORIES = True

BDT_CATEGORY_CHANNELS = [
    "ggH",
    "VBF",
]

# The highest-score interval is category 1; the lowest-score interval is
# category 5. The utility includes the upper edge of the final interval.
BDT_CUTS = {
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
        0.646666666666667,
        0.8800000000000018,
        0.9466666666666689,
        0.9733333333333357,
        1.0,
    ],
}

# Relative to SYSTEMATICS_DIRECTORY. The directory is selected by the BDT
# category family being plotted. The actual EOS directory is named VBF.
BDT_NOMINAL_SUBDIRECTORIES = {
    "ggH": Path("BDT_score/ggH/BFull_SNottH"),
    "VBF": Path("BDT_score/VBF/BFull_SNottH"),
}

BDT_NANOAOD_SUBDIRECTORIES = {
    "ggH": Path("ggH/BFull_SNottH"),
    "VBF": Path("VBF/BFull_SNottH"),
}

BDT_SYSTEMATICS_SUBDIRECTORIES = {
    "ggH": Path("BDT_score/ggH/BFull_SNottH"),
    "VBF": Path("BDT_score/VBF/BFull_SNottH"),
}

# valid_muon_pt_systs in tuple production contains:
#   scale_up, scale_down, smearing_up, smearing_down
#
# Here only use the base name because the plotting code automatically looks for
# both the corresponding _up_tuples.root and _down_tuples.root files.
SYSTEMATICS = [
    "scale",
    #"smearing",
]

# False: weighted event yields. True: independently normalize each histogram.
NORMALIZE_HISTOGRAMS = False

# Data events inside this dimuon-mass window are removed before filling
# any histogram.
DATA_BLIND_MASS_WINDOW = (120.0, 130.0)

# -----------------------------------------------------------------------------
# Plot production
# -----------------------------------------------------------------------------


def main() -> None:
    nominal_directory = NOMINAL_TUPLE_DIRECTORY.resolve()
    nanoaod_directory = NANOAOD_TUPLE_DIRECTORY.resolve()
    systematics_directory = SYSTEMATICS_DIRECTORY.resolve()
    output_base_directory = OUTPUT_BASE_DIRECTORY.resolve()

    if not nominal_directory.is_dir():
        raise NotADirectoryError(
            f"Nominal tuple directory not found: {nominal_directory}"
        )

    if not nanoaod_directory.is_dir():
        raise NotADirectoryError(
            f"NanoAOD tuple directory not found: {nanoaod_directory}"
        )

    if not systematics_directory.is_dir():
        raise NotADirectoryError(
            f"Systematics directory not found: {systematics_directory}"
        )

    if not CHANNELS:
        raise ValueError("CHANNELS is empty. Add at least one channel.")

    if not SYSTEMATICS:
        raise ValueError("SYSTEMATICS is empty. Add at least one systematic.")

    print(f"Nominal directory:    {nominal_directory}")
    print(f"NanoAOD directory:    {nanoaod_directory}")
    print(f"Systematics directory:{systematics_directory}")
    print(f"Output base directory:{output_base_directory}")
    print(f"Channels:             {', '.join(CHANNELS)}")
    print(f"Do BDT categories:    {DO_BDT_CATEGORIES}")
    print(f"Requested systematics:{len(SYSTEMATICS)}")

    total_plots = 0

    for channel in CHANNELS:
        if channel.lower() == "data":
            nominal_file = nominal_directory / "data_Combined.root"
            nanoaod_file = nanoaod_directory / "data_Combined.root"
        else:
            nominal_file = (
                nominal_directory / f"{channel}_Combined_tuples.root"
            )
            nanoaod_file = (
                nanoaod_directory / f"{channel}_Combined_tuples.root"
            )

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
            print(f"Nominal input base:  {nominal_directory}")
            print(f"NanoAOD input base:  {nanoaod_directory}")
            print("Tuple files:         selected by BDT category family")
        else:
            print(f"Nominal tuple:       {nominal_file}")
            print(f"NanoAOD tuple:       {nanoaod_file}")
        print(f"Output directory:    {output_directory}")
        print("=" * 80)

        channel_plots = draw_all_muon_systematics(
            production_channel=channel,
            nominal_file=nominal_file,
            nanoaod_file=nanoaod_file,
            systematics_directory=systematics_directory,
            output_directory=output_directory,
            systematic_names=SYSTEMATICS,
            normalize=NORMALIZE_HISTOGRAMS,
            bdt_cuts=BDT_CUTS if DO_BDT_CATEGORIES else None,
            bdt_category_channels=BDT_CATEGORY_CHANNELS,
            bdt_nominal_subdirectories=(
                BDT_NOMINAL_SUBDIRECTORIES
                if DO_BDT_CATEGORIES
                else None
            ),
            bdt_nanoaod_subdirectories=(
                BDT_NANOAOD_SUBDIRECTORIES
                if DO_BDT_CATEGORIES
                else None
            ),
            bdt_systematics_subdirectories=(
                BDT_SYSTEMATICS_SUBDIRECTORIES
                if DO_BDT_CATEGORIES
                else None
            ),
            blind_data_mass_window=DATA_BLIND_MASS_WINDOW,
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
