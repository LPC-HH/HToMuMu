import os
import time

import mplhep as hep
import numpy as np
import matplotlib.pyplot as plt
import uproot as ur

from .labels import x_labels, n_bins, x_range, variables_type
from .colors import get_color_list
from .helper import (
    get_canvas,
    save_figure,
    clean_null_values,
    get_output_directory,
)

MASS_VARIABLE = "diMuon_bsConstrainedMass"
MASS_WINDOW = (110.0, 150.0)

# Data events in the Higgs window of the beam-spot-constrained mass must never be plotted
# (blinding policy). Applied at read time, so these events never enter memory.
BLIND_WINDOW = (120.0, 130.0)
DATA_BLINDING_CUT = (
    f"~((diMuon_bsConstrainedMass > {BLIND_WINDOW[0]}) & (diMuon_bsConstrainedMass < {BLIND_WINDOW[1]}))"
)
DATA_LABEL = f"Data ({BLIND_WINDOW[0]:.0f}-{BLIND_WINDOW[1]:.0f} GeV blinded)"

CATEGORY_CUTS = {
    "inclusive": None,
    "ggH": "is_ggH_category",
    "VBF": "is_VBF_category",
}

# Files are streamed in chunks of this size so memory stays flat regardless of tuple size
STEP_SIZE = "200 MB"

# Fixed log binning for |weight| so histograms from different chunks/eras can be summed;
# empty bins are trimmed at draw time. Values outside are clipped into the edge bins.
WEIGHT_BINS = np.logspace(-10, 6, 161)

# Wide mass range for the hand-off check at LHE mll 105 / 160 GeV, jet-binned J <-> J + U (tuples keep 70-180)
MASS_WIDE_BINS = (110, (70.0, 180.0))

# Per-event "views" of a file: name -> (needs stitch_weight, function(chunk) -> (mask, weights)).
# stitch_weight (CreateTuple, all-aMC@NLO DY stitching, lib/DYStitching.h) is the fraction stitch_frac[cell]
# of the event's stitching cell (stitch_cell), 1 outside the 105-160 window, so dividing by it gives each
# sample's standalone prediction. Selections by cell use cell_view below.
VIEWS = {
    "all": (False, lambda c: (np.ones(len(c["weight"]), dtype=bool), c["weight"])),
    "raw": (True, lambda c: (np.ones(len(c["weight"]), dtype=bool), c["weight"] / c["stitch_weight"])),
}


def cell_view(cells, raw=False):
    """View of the events in the given DY stitching cells (stitch_cell branch, lib/DYStitching.h), with the
    stitched weight or, with raw=True, the sample's standalone weight (weight / stitch_weight).
    Can be used as a value of the `views` argument of fill_from_file, like the keys of VIEWS. It is a plain
    tuple (picklable, so it can be sent to worker processes); _resolve_view builds the selection."""
    return ("cells", tuple(int(cell) for cell in cells), bool(raw))


def _resolve_view(view):
    """(needs stitch_weight, function(chunk) -> (mask, weights), extra branches) of a VIEWS key or a cell_view"""
    if isinstance(view, str):
        needs, function = VIEWS[view]
        return needs, function, []
    _, cells, raw = view
    cells = np.asarray(cells)

    def function(c):
        mask = np.isin(c["stitch_cell"], cells)
        weights = c["weight"] / c["stitch_weight"] if raw else c["weight"]
        return mask, weights
    return True, function, ["stitch_cell"]


# Summary columns: N raw, sum w, sum w^2, N(w < 0), sum |w|
SUMMARY_SELECTIONS = ["all mass", "110-150"]


def select(branches, mask):
    return {key: value[mask] for key, value in branches.items()}


def category_mask(branches, category):
    cut_branch = CATEGORY_CUTS[category]
    if cut_branch is None:
        return np.ones(len(branches["weight"]), dtype=bool)
    return branches[cut_branch] == 1


def mass_window_mask(branches):
    mass = branches[MASS_VARIABLE]
    return (mass > MASS_WINDOW[0]) & (mass < MASS_WINDOW[1])


def blind_window_mask(branches):
    mass = branches[MASS_VARIABLE]
    return (mass > BLIND_WINDOW[0]) & (mass < BLIND_WINDOW[1])


def weighted_hist(values, weights, bins, hist_range=None):
    """Returns per-bin sum of weights, sum of squared weights and the bin edges."""
    sumw, edges = np.histogram(values, bins=bins, range=hist_range, weights=weights)
    sumw2, _ = np.histogram(values, bins=edges, weights=weights**2)
    return sumw, sumw2, edges


def effective_entries(sumw, sumw2):
    """N_eff = (sum w)^2 / sum w^2; bins with sum w <= 0 are set to NaN."""
    neff = np.full_like(sumw, np.nan, dtype=float)
    valid = (sumw > 0) & (sumw2 > 0)
    neff[valid] = sumw[valid] ** 2 / sumw2[valid]
    return neff


def weighted_ratio(num, num_w2, den, den_w2):
    """Ratio of two weighted histograms with uncorrelated error propagation."""
    ratio = np.full_like(num, np.nan, dtype=float)
    error = np.full_like(num, np.nan, dtype=float)
    valid = (den != 0) & (num != 0)
    ratio[valid] = num[valid] / den[valid]
    error[valid] = np.abs(ratio[valid]) * np.sqrt(
        num_w2[valid] / num[valid] ** 2 + den_w2[valid] / den[valid] ** 2
    )
    return ratio, error


def get_binning(variable, category):
    variable_bin = variable
    if variable + "_" + category in x_range:
        variable_bin += "_" + category
    return n_bins[variable_bin], x_range[variable_bin]


def get_neff_binning(variable, category):
    # The inclusive diJet_mass binning (250 bins) is too fine for N_eff
    bins, hist_range = get_binning(variable, category)
    return min(bins, 50), hist_range


def _cleaned(branches, variable):
    values = {variable: branches[variable], "weight": branches["weight"]}
    clean_null_values(values, [variable, "weight"], variables_type)
    return values[variable], values["weight"]


def _format_time(seconds):
    seconds = int(seconds)
    return f"{seconds // 3600:d}h{seconds % 3600 // 60:02d}m{seconds % 60:02d}s"


def _rss_gb():
    """Current resident memory of this process in GB (Linux only)."""
    try:
        with open("/proc/self/status") as status:
            for line in status:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024**2
    except OSError:
        pass
    return float("nan")


class HistogramSet:
    """Weighted histograms and yield summaries of one sample, per category.
    Filled chunk by chunk; two sets with the same binning can be added (e.g. to sum eras)."""

    def __init__(self):
        self.hists = {}  # (category, name) -> [sumw, sumw2, edges]
        self.summary = {}  # (category, selection) -> [N raw, sum w, sum w^2, N(w < 0), sum |w|]

    def fill(self, category, name, values, weights, bins, hist_range=None):
        sumw, sumw2, edges = weighted_hist(values, weights, bins, hist_range)
        key = (category, name)
        if key in self.hists:
            self.hists[key][0] += sumw
            self.hists[key][1] += sumw2
        else:
            self.hists[key] = [sumw, sumw2, edges]

    def fill_summary(self, category, selection, weights):
        values = np.array([len(weights), np.sum(weights), np.sum(weights**2),
                           np.sum(weights < 0), np.sum(np.abs(weights))], dtype=float)
        key = (category, selection)
        self.summary[key] = self.summary.get(key, 0) + values

    def get(self, category, name):
        return self.hists[(category, name)]

    def __iadd__(self, other):
        for key, (sumw, sumw2, edges) in other.hists.items():
            if key in self.hists:
                self.hists[key][0] = self.hists[key][0] + sumw
                self.hists[key][1] = self.hists[key][1] + sumw2
            else:
                self.hists[key] = [sumw.copy(), sumw2.copy(), edges]
        for key, values in other.summary.items():
            self.summary[key] = self.summary.get(key, 0) + values
        return self


def _fill_chunk(hset, chunk, categories, variables, neff_variables, is_data):
    if is_data:
        # Data is drawn as raw counts
        chunk["weight"] = np.ones(len(chunk["weight"]))
    for category in categories:
        in_category = select(chunk, category_mask(chunk, category))
        window = select(in_category, mass_window_mask(in_category))
        # Same mass region as blinded data (no-op for data, which is blinded at read time)
        blinded = select(window, ~blind_window_mask(window))

        bins, hist_range = get_binning(MASS_VARIABLE, category)
        hset.fill(category, "mass", in_category[MASS_VARIABLE], in_category["weight"], bins, hist_range)
        hset.fill(category, "mass_wide", in_category[MASS_VARIABLE], in_category["weight"], *MASS_WIDE_BINS)
        for variable in variables:
            bins, hist_range = get_binning(variable, category)
            hset.fill(category, "shape_" + variable, *_cleaned(window, variable), bins, hist_range)
            hset.fill(category, "blinded_" + variable, *_cleaned(blinded, variable), bins, hist_range)
        if is_data:
            continue

        hset.fill_summary(category, "all mass", in_category["weight"])
        hset.fill_summary(category, "110-150", window["weight"])
        for variable in neff_variables:
            bins, hist_range = get_neff_binning(variable, category)
            hset.fill(category, "neff_" + variable, *_cleaned(window, variable), bins, hist_range)
        weights = window["weight"]
        abs_weights = np.clip(np.abs(weights), WEIGHT_BINS[0], WEIGHT_BINS[-1] * 0.999)
        positive, negative = weights > 0, weights < 0
        hset.fill(category, "weights_pos", abs_weights[positive], np.ones(np.sum(positive)), WEIGHT_BINS)
        hset.fill(category, "weights_neg", abs_weights[negative], np.ones(np.sum(negative)), WEIGHT_BINS)


def fill_from_file(path, label, branches, categories, variables, neff_variables,
                   is_data=False, step_size=STEP_SIZE, verbose=True, views=None):
    """Streams tree_output of `path` in chunks and returns a filled HistogramSet,
    printing progress after each chunk (unless verbose=False, for many small files).
    With `views` (output name -> key of VIEWS), one pass over the file fills one HistogramSet per view
    and a dict output name -> HistogramSet is returned.
    Data files always get the blinding cut."""
    cut = None
    branches = list(branches)
    if is_data:
        branches = list(dict.fromkeys(branches + ["diMuon_bsConstrainedMass"]))
        cut = DATA_BLINDING_CUT
    if views is not None and not is_data:
        resolved = {name: _resolve_view(view) for name, view in views.items()}
        if any(needs for needs, _, _ in resolved.values()):
            branches = list(dict.fromkeys(branches + ["stitch_weight"]))
        for _, _, extra in resolved.values():
            branches = list(dict.fromkeys(branches + extra))

    hset = HistogramSet()
    view_sets = {name: HistogramSet() for name in views} if views is not None else None
    start = time.time()
    with ur.open(path) as file:
        tree = file["tree_output"]
        total = tree.num_entries
        if verbose:
            print(f"[{label}] Reading {total / 1e6:.2f}M entries from {path} "
                  f"({os.path.getsize(path) / 1024**3:.2f} GB)", flush=True)
        for chunk, report in tree.iterate(branches, cut=cut, step_size=step_size,
                                          library="np", report=True):
            if view_sets is None:
                _fill_chunk(hset, chunk, categories, variables, neff_variables, is_data)
            else:
                for name, view in views.items():
                    if is_data:
                        _fill_chunk(view_sets[name], dict(chunk), categories, variables, neff_variables, True)
                        continue
                    mask, weights = resolved[name][1](chunk)
                    selected = select(chunk, mask)
                    selected["weight"] = weights[mask]
                    _fill_chunk(view_sets[name], selected, categories, variables, neff_variables, False)
            if not verbose:
                continue
            done = report.tree_entry_stop
            elapsed = time.time() - start
            rate = done / elapsed if elapsed > 0 else 0.0
            eta = (total - done) / rate if rate > 0 else 0.0
            print(f"[{label}] {done / 1e6:7.2f}M / {total / 1e6:.2f}M ({100 * done / total:5.1f}%)"
                  f" | {rate / 1e6:.2f}M ev/s | elapsed {_format_time(elapsed)}"
                  f" | ETA {_format_time(eta)} | RSS {_rss_gb():.2f} GB", flush=True)
    if verbose:
        print(f"[{label}] Done in {_format_time(time.time() - start)}", flush=True)
    return hset if view_sets is None else view_sets


def print_summary(samples, category, era):
    print("\n" + "=" * 78)
    print(f"Era: {era}, category: {category}")
    print(f"{'sample':<22}{'selection':<14}{'N raw':>12}{'sum w':>14}{'N_eff':>14}{'neg frac':>10}")
    for label, hset in samples.items():
        for selection in SUMMARY_SELECTIONS:
            n_raw, sumw, sumw2, n_neg, _ = hset.summary[(category, selection)]
            neff = sumw**2 / sumw2 if sumw2 > 0 else 0.0
            neg_frac = n_neg / n_raw if n_raw else 0.0
            print(f"{label:<22}{selection:<14}{int(n_raw):>12d}{sumw:>14.2f}{neff:>14.1f}{neg_frac:>10.3f}")
    print("=" * 78, flush=True)


def _draw_data(ax, ratio_ax, counts, edges, reference, reference_w2, norm=1.0):
    """Data points (raw counts / norm, Poisson errors) and data / reference in the ratio panel.
    Empty bins (including the blinded window) are not drawn."""
    centers = 0.5 * (edges[:-1] + edges[1:])
    filled = counts > 0
    ax.errorbar(centers[filled], counts[filled] / norm, yerr=np.sqrt(counts[filled]) / norm,
                fmt="o", color="black", markersize=4, label=DATA_LABEL)
    ratio, error = weighted_ratio(counts / norm, counts / norm**2, reference, reference_w2)
    filled &= ~np.isnan(ratio)
    ratio_ax.errorbar(centers[filled], ratio[filled], yerr=error[filled],
                      fmt="o", color="black", markersize=4)


def _finish_plot(fig, ax, ratio_ax, era, xlabel, bins, has_data=False):
    hep.cms.label(data=has_data, label="", year=era, com="13.6", ax=ax)
    ax.set_xlim(bins[0], bins[-1])
    ax.legend(frameon=False, loc="upper right", fontsize=15)
    ax.tick_params(labelbottom=False)
    ratio_ax.set_xlim(bins[0], bins[-1])
    ratio_ax.set_xlabel(xlabel)
    ratio_ax.axhline(1.0, color="black", linestyle="--", linewidth=1)


def draw_neff(samples, variable, category, era, output_directory, name):
    """Effective MC statistics per bin of `variable` (stored histogram `name`) for each sample,
    with the ratio to the first sample."""
    plt.style.use(hep.style.CMS)
    colors = get_color_list(len(samples))
    fig, (ax, ratio_ax) = get_canvas(draw_ratio=True)

    neff_hists = {}
    for (label, hset), color in zip(samples.items(), colors):
        sumw, sumw2, edges = hset.get(category, name)
        neff = effective_entries(sumw, sumw2)
        neff_hists[label] = neff
        total_sumw2 = np.sum(sumw2)
        total_neff = np.sum(sumw) ** 2 / total_sumw2 if total_sumw2 > 0 else 0.0
        hep.histplot(
            np.nan_to_num(neff),
            edges,
            yerr=False,
            ax=ax,
            color=color,
            linewidth=2,
            label=f"{label} (total $N_{{eff}}$ = {total_neff:.3g})",
        )

    labels = list(samples.keys())
    reference = neff_hists[labels[0]]
    for label, color in zip(labels[1:], colors[1:]):
        ratio = np.full_like(reference, np.nan)
        valid = (reference > 0) & ~np.isnan(neff_hists[label])
        ratio[valid] = neff_hists[label][valid] / reference[valid]
        hep.histplot(np.nan_to_num(ratio), edges, yerr=False, ax=ratio_ax, color=color, linewidth=2)

    ax.set_yscale("log")
    ax.set_ylim(top=ax.get_ylim()[1] * 20)
    ax.set_ylabel(r"$N_{eff} = (\sum w)^2 / \sum w^2$ per bin")
    ratio_ax.set_ylabel(r"Ratio")
    ratio_ax.set_yscale("log")
    _finish_plot(fig, ax, ratio_ax, era, x_labels[variable], edges)

    save_figure(fig, output_directory, f"neff_{variable}_{category}_{era}")
    plt.close()


def draw_yield(samples, variable, category, era, output_directory, name="mass", data=None,
               label_suffix=""):
    """Weighted event yields per bin of `variable` (stored histogram `name`) with stat errors, and
    the ratio to the first sample. If `data` (filled with is_data=True) is given, it is overlaid
    as points. `label_suffix` is appended to each MC legend entry."""
    plt.style.use(hep.style.CMS)
    colors = get_color_list(len(samples))
    fig, (ax, ratio_ax) = get_canvas(draw_ratio=True)

    hists = {}
    for (label, hset), color in zip(samples.items(), colors):
        sumw, sumw2, edges = hset.get(category, name)
        hists[label] = (sumw, sumw2)
        hep.histplot(
            sumw,
            edges,
            yerr=np.sqrt(sumw2),
            ax=ax,
            color=color,
            linewidth=2,
            label=f"{label} ($\\sum w$ = {np.sum(sumw):.3g}){label_suffix}",
        )

    labels = list(samples.keys())
    ref_sumw, ref_sumw2 = hists[labels[0]]
    for label, color in zip(labels[1:], colors[1:]):
        ratio, error = weighted_ratio(*hists[label], ref_sumw, ref_sumw2)
        hep.histplot(np.nan_to_num(ratio), edges, yerr=np.nan_to_num(error),
                     ax=ratio_ax, color=color, histtype="errorbar")
    if data is not None:
        _draw_data(ax, ratio_ax, data.get(category, name)[0], edges, ref_sumw, ref_sumw2)

    ax.set_yscale("log")
    ax.set_ylim(top=ax.get_ylim()[1] * 20)
    ax.set_ylabel("Weighted events / bin")
    ratio_ax.set_ylabel(f"/ {labels[0]}")
    ratio_ax.set_yscale("log")
    _finish_plot(fig, ax, ratio_ax, era, x_labels[variable], edges, has_data=data is not None)

    save_figure(fig, output_directory, f"yield_{variable}_{category}_{era}")
    plt.close()


def draw_weight_distribution(samples, category, era, output_directory):
    """|weight| distributions in the mass window on a log axis, positive and negative weights
    drawn separately."""
    plt.style.use(hep.style.CMS)
    colors = get_color_list(len(samples))

    # Trim the fixed WEIGHT_BINS to the range that is filled in any sample
    filled = np.zeros(len(WEIGHT_BINS) - 1, dtype=bool)
    for hset in samples.values():
        filled |= (hset.get(category, "weights_pos")[0] > 0) | (hset.get(category, "weights_neg")[0] > 0)
    if not np.any(filled):
        print(f"[{era} {category}] No events in the mass window, skipping weight distribution")
        return
    first, last = np.flatnonzero(filled)[[0, -1]]
    bins = WEIGHT_BINS[first:last + 2]

    fig, ax = get_canvas()
    for (label, hset), color in zip(samples.items(), colors):
        n_raw, sumw, sumw2, n_neg, sum_abs = hset.summary[(category, "110-150")]
        neff = sumw**2 / sumw2 if sumw2 > 0 else 0.0
        if n_raw:
            print(
                f"[{era} {category}] {label}: negative-weight fraction = {n_neg / n_raw:.3f}, "
                f"N_eff/N_raw = {neff / n_raw:.3f}, mean |w| = {sum_abs / n_raw:.4g}"
            )
        positive = hset.get(category, "weights_pos")[0][first:last + 1]
        negative = hset.get(category, "weights_neg")[0][first:last + 1]
        hep.histplot(positive, bins, yerr=False, ax=ax, color=color, linewidth=2,
                     label=f"{label}, w > 0")
        if np.any(negative):
            hep.histplot(negative, bins, yerr=False, ax=ax, color=color, linewidth=2,
                         linestyle="--", label=f"{label}, w < 0")

    hep.cms.label(data=False, label="", year=era, com="13.6", ax=ax)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("|event weight|")
    ax.set_ylabel("Raw events")
    ax.set_xlim(bins[0], bins[-1])
    ax.legend(frameon=False, loc="upper right", fontsize="small")

    save_figure(fig, output_directory, f"weights_{category}_{era}")
    plt.close()


def draw_shape(samples, variable, category, era, output_directory, data=None, name=None):
    """Unit-normalized shapes of `variable` in the mass window with the ratio to the first sample.
    If `data` (filled with is_data=True) is given, its unit-normalized shape is overlaid as points.
    `name` is the stored histogram (default "shape_<variable>", the full 110-150 window). With data,
    use "blinded_<variable>" so MC and data cover the same mass region."""
    name = name or "shape_" + variable
    plt.style.use(hep.style.CMS)
    colors = get_color_list(len(samples))
    fig, (ax, ratio_ax) = get_canvas(draw_ratio=True)

    hists = {}
    for (label, hset), color in zip(samples.items(), colors):
        sumw, sumw2, edges = hset.get(category, name)
        norm = np.sum(sumw)
        if norm == 0:
            norm = 1.0
        hists[label] = (sumw / norm, sumw2 / norm**2)
        hep.histplot(sumw / norm, edges, yerr=np.sqrt(sumw2) / abs(norm), ax=ax,
                     color=color, linewidth=2, label=label)

    labels = list(samples.keys())
    ref, ref_w2 = hists[labels[0]]
    for label, color in zip(labels[1:], colors[1:]):
        ratio, error = weighted_ratio(*hists[label], ref, ref_w2)
        hep.histplot(np.nan_to_num(ratio), edges, yerr=np.nan_to_num(error),
                     ax=ratio_ax, color=color, histtype="errorbar")
    if data is not None:
        counts = data.get(category, name)[0]
        data_norm = np.sum(counts) if np.sum(counts) > 0 else 1.0
        _draw_data(ax, ratio_ax, counts, edges, ref, ref_w2, norm=data_norm)

    ax.set_ylabel("Events / Total events")
    ax.set_ylim(bottom=0)
    ratio_ax.set_ylabel(f"/ {labels[0]}")
    ratio_ax.set_ylim(0, 2)
    _finish_plot(fig, ax, ratio_ax, era, x_labels[variable], edges, has_data=data is not None)

    output_directory = get_output_directory(variable, output_directory, variables_type)
    save_figure(fig, output_directory, f"shape_{variable}_{category}_{era}")
    plt.close()


def sum_sets(*hsets):
    """New HistogramSet with the sum of `hsets` (the inputs are not modified)."""
    total = HistogramSet()
    for hset in hsets:
        total += hset
    return total


def draw_stack(components, overlays, variable, category, era, output_directory, name,
               data=None, label_suffix="", file_prefix="stack"):
    """Stacked weighted yields of `components` (label -> HistogramSet) for the stored histogram `name`,
    with `overlays` (label -> HistogramSet) as lines and `data` as points. The ratio panel shows data and
    each overlay over the stack total. Negative bin contents (possible with negative weights) are drawn
    as zero in the stack but kept in the total."""
    plt.style.use(hep.style.CMS)
    colors = get_color_list(len(components) + len(overlays))
    fig, (ax, ratio_ax) = get_canvas(draw_ratio=True)

    stack, stack_labels = [], []
    total, total_w2, edges = None, None, None
    for label, hset in components.items():
        sumw, sumw2, edges = hset.get(category, name)
        stack.append(np.clip(sumw, 0, None))
        stack_labels.append(f"{label} ({np.sum(sumw):.3g})")
        total = sumw.copy() if total is None else total + sumw
        total_w2 = sumw2.copy() if total_w2 is None else total_w2 + sumw2
    hep.histplot(stack, edges, stack=True, histtype="fill", ax=ax, color=colors[:len(stack)],
                 label=stack_labels, alpha=0.8)
    hep.histplot(total, edges, yerr=np.sqrt(total_w2), ax=ax, color="black", linewidth=1,
                 label=f"Stitched total ({np.sum(total):.3g}){label_suffix}")

    for (label, hset), color in zip(overlays.items(), colors[len(stack):]):
        sumw, sumw2, _ = hset.get(category, name)
        hep.histplot(sumw, edges, yerr=np.sqrt(sumw2), ax=ax, color=color, linewidth=2, linestyle="--",
                     label=f"{label} ({np.sum(sumw):.3g})")
        ratio, error = weighted_ratio(sumw, sumw2, total, total_w2)
        hep.histplot(np.nan_to_num(ratio), edges, yerr=np.nan_to_num(error), ax=ratio_ax, color=color,
                     histtype="errorbar")
    if data is not None:
        _draw_data(ax, ratio_ax, data.get(category, name)[0], edges, total, total_w2)

    ax.set_yscale("log")
    positive = total[total > 0]
    if len(positive):
        ax.set_ylim(max(positive.min() * 0.1, np.max(total) * 1e-6), np.max(total) * 500)
    ax.set_ylabel("Weighted events / bin")
    ratio_ax.set_ylabel("/ Stitched")
    ratio_ax.set_ylim(0.5, 1.5)
    _finish_plot(fig, ax, ratio_ax, era, x_labels[variable], edges, has_data=data is not None)
    ax.legend(frameon=False, loc="upper right", fontsize=12)

    save_figure(fig, output_directory, f"{file_prefix}_{variable}_{category}_{era}")
    plt.close()


def draw_composition(components, variable, category, era, output_directory, name):
    """Fraction of the summed yield contributed by each component, per bin of `variable`."""
    plt.style.use(hep.style.CMS)
    colors = get_color_list(len(components))
    fig, ax = get_canvas()

    hists = {label: hset.get(category, name) for label, hset in components.items()}
    edges = next(iter(hists.values()))[2]
    total = np.sum([sumw for sumw, _, _ in hists.values()], axis=0)
    valid = total > 0
    for (label, (sumw, _, _)), color in zip(hists.items(), colors):
        fraction = np.full_like(total, np.nan, dtype=float)
        fraction[valid] = sumw[valid] / total[valid]
        integral = np.sum(sumw) / np.sum(total) if np.sum(total) else np.nan
        hep.histplot(np.nan_to_num(fraction), edges, yerr=False, ax=ax, color=color, linewidth=2,
                     label=f"{label} ({100 * integral:.1f}%)")

    hep.cms.label(data=False, label="", year=era, com="13.6", ax=ax)
    ax.set_xlim(edges[0], edges[-1])
    ax.set_ylim(-0.05, 1.4)
    ax.set_xlabel(x_labels[variable])
    ax.set_ylabel("Fraction of stitched yield")
    ax.legend(frameon=False, loc="upper right", fontsize=13)

    save_figure(fig, output_directory, f"composition_{variable}_{category}_{era}")
    plt.close()


def chi2_ndf(first, second, normalize=False):
    """chi2 / ndf between two independent weighted histograms (sumw, sumw2), over the bins where
    either has entries. normalize=True compares unit-normalized shapes."""
    (a, a_w2), (b, b_w2) = first, second
    if normalize:
        norm_a, norm_b = np.sum(a), np.sum(b)
        if norm_a == 0 or norm_b == 0:
            return np.nan, 0
        a, a_w2, b, b_w2 = a / norm_a, a_w2 / norm_a**2, b / norm_b, b_w2 / norm_b**2
    variance = a_w2 + b_w2
    valid = variance > 0
    ndf = int(np.sum(valid)) - (1 if normalize else 0)
    if ndf <= 0:
        return np.nan, 0
    return float(np.sum((a[valid] - b[valid]) ** 2 / variance[valid])), ndf


def write_closure_table(first_label, first, second_label, second, categories, variables, path):
    """Normalization ratio and yield/shape chi2/ndf of two independent predictions of the same thing,
    per category and variable (histograms "shape_<variable>", the 110-150 window)."""
    lines = [f"Closure: {second_label} vs {first_label} (independent events; 110-150 GeV window)",
             f"{'category':<10}{'variable':<28}{'ratio':>16}{'yield chi2/ndf':>18}{'p':>8}"
             f"{'shape chi2/ndf':>18}{'p':>8}"]
    from scipy.stats import chi2 as chi2_distribution
    for category in categories:
        for variable in variables:
            a = first.get(category, "shape_" + variable)[:2]
            b = second.get(category, "shape_" + variable)[:2]
            sum_a, sum_b = np.sum(a[0]), np.sum(b[0])
            ratio = sum_b / sum_a if sum_a else np.nan
            ratio_error = abs(ratio) * np.sqrt(np.sum(a[1]) / sum_a**2 + np.sum(b[1]) / sum_b**2) \
                if sum_a and sum_b else np.nan
            row = f"{category:<10}{variable:<28}{ratio:>9.3f}+-{ratio_error:<5.3f}"
            for normalize in [False, True]:
                chi2_value, ndf = chi2_ndf(a, b, normalize)
                p_value = chi2_distribution.sf(chi2_value, ndf) if ndf else np.nan
                row += f"{chi2_value:>10.1f}/{ndf:<7d}{p_value:>8.3f}"
            lines.append(row)
        lines.append("")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as output:
        output.write("\n".join(lines) + "\n")
    print("\n".join(lines[:2] + [line for line in lines[2:] if line.split()[1:2] in
                                 [["diMuon_pt"], ["diJet_mass"], ["n_jet"]]]), flush=True)
    print(f"Closure table written to {path}", flush=True)
