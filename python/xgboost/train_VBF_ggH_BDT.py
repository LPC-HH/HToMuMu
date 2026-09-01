#!/usr/bin/env python
# coding: utf-8
"""
Train two BDTs (n_jet == 1 and n_jet >= 2) to discriminate VBF from ggH
topology, pick a per-region operating point that maximizes
N_VBF / sqrt(N_VBF + N_ggH) (using event weights), and append the resulting
0/1 prediction (is_VBF_categoryBDT) onto copies of the ggH/VBF tuples.
"""
import gc
import math
import os
import pickle
import shutil
import sys
from array import array

import awkward as ak
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import pandas as pd
import ROOT as root
import seaborn as sns
import uproot
import xgboost as xgb
from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import xgb_utils

sys.path.insert(0, "../../plot_macros")
from utils.labels import n_bins as PLOT_N_BINS  # noqa: E402
from utils.labels import x_labels as PLOT_X_LABELS  # noqa: E402
from utils.labels import x_range as PLOT_X_RANGE  # noqa: E402
from utils.ggH_vs_VBF import draw_ggH_vs_VBF_comparison

root.gROOT.SetBatch(True)
plt.style.use(hep.style.CMS)

SEED = 7
TEST_SIZE = 0.4
SAMPLE_SIZE = 1.0
ERA = "Combined"
SIGNAL_REGION = (121, 129)
MASS_VAR = "diMuon_bsConstrainedMass"
BACKGROUND_NAMES = ("DY", "EWK", "TT", "DiBoson")
USE_BSCONSTRAIN = True

plot_path = "../../plots/xgboost/categorization/"
tuple_dir = "../../root_io/tuples/"

bdt_variables = [
    "diJet_mass",
    "pt_balance",
    "pt_centrality",
    "leading_jet_eta",
    "subleading_jet_eta",
    "delta_eta_diJet",
    "delta_phi_diJet",
    "n_jet",
    "leading_jet_pt",
    "subleading_jet_pt",
    "min_delta_eta_diMuon_jet",
    "min_delta_phi_diMuon_jet",
    "diMuon_bsConstrainedPt",
    "diMuon_rapidity",
    "HT",
    "HT_pt2",
    "HT_pt5",
    "HT_pt10",
    "z_zeppenfeld",
    "is_ggH_category",
    "is_VBF_category",
    "weight",
    MASS_VAR,
]

bdt_variables1 = [
    "leading_jet_eta",
    "n_jet",
    "leading_jet_pt",
    "min_delta_eta_diMuon_jet",
    "min_delta_phi_diMuon_jet",
    "diMuon_bsConstrainedPt",
    "diMuon_rapidity",
    "HT",
    "HT_pt2",
    "HT_pt5",
    "HT_pt10",
    "is_ggH_category",
    "is_VBF_category",
    "weight",
    MASS_VAR,
]

REGIONS = {
    "multijet": {"variables": bdt_variables, "n_jet_cut": lambda n: n >= 2},
    "onejet": {"variables": bdt_variables1, "n_jet_cut": lambda n: n == 1},
}


def plot_confusion_matrix(
    y_true, y_pred, counts, plot_path, region_name, labels=("ggH", "VBF"), sample_weight=None
):
    ggH_events, VBF_events = counts

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1], sample_weight=sample_weight)
    cm_percent = cm.astype(float) / cm.sum(axis=1, keepdims=True) * 100
    ggH_event_arr = np.array([[1, 1], [0, 0]]) * ggH_events
    VBF_event_arr = np.array([[0, 0], [1, 1]]) * VBF_events
    cm_event_arr = cm_percent / 100 * ggH_event_arr + cm_percent / 100 * VBF_event_arr

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.heatmap(
        cm_percent, annot=True, fmt=".1f", cmap="Blues", vmin=0, vmax=100,
        xticklabels=labels, yticklabels=labels, ax=axes[0],
    )
    axes[0].set_xlabel("Predicted")
    axes[0].set_ylabel("True")
    axes[0].set_title(f"Confusion Matrix (%) {region_name}")

    sns.heatmap(
        cm_event_arr, annot=True, fmt=".1f", cmap="Blues",
        xticklabels=labels, yticklabels=labels, ax=axes[1],
    )
    axes[1].set_xlabel("Predicted")
    axes[1].set_ylabel("True")
    axes[1].set_title(f"Expected Events {region_name}")

    plt.tight_layout()
    os.makedirs(f"{plot_path}training/", exist_ok=True)
    plt.savefig(f"{plot_path}training/confusion_matrix_{region_name}.png")
    plt.savefig(f"{plot_path}training/confusion_matrix_{region_name}.pdf")
    plt.close(fig)


def asimov_significance(S, B):
    """Elementwise Asimov significance Z = sqrt(2*((S+B)*ln(1+S/B) - S)).
    Returns 0 wherever B <= 0 or S < 0 (undefined / non-physical bins, e.g. from
    threshold values where negative-weight fluctuations push a yield below 0)."""
    S = np.asarray(S, dtype=float)
    B = np.asarray(B, dtype=float)
    valid = (B > 0) & (S >= 0)
    ratio = np.divide(S, B, out=np.zeros_like(S), where=valid)
    z = np.zeros_like(S)
    z_valid = np.sqrt(np.clip(2 * ((S + B) * np.log1p(ratio) - S), 0, None))
    z[valid] = z_valid[valid]
    return z


def weighted_yield_above_threshold(score, weight, thr):
    """For each threshold t in thr, sum(weight[score > t]) -- vectorized via
    sorting instead of an O(len(thr) * len(score)) loop. Matches roc_curve's
    tpr/fpr convention (score > threshold counts as "positive")."""
    order = np.argsort(score)
    sorted_score = score[order]
    sorted_weight = weight[order]
    cum_from_left = np.cumsum(sorted_weight)
    total = cum_from_left[-1] if len(cum_from_left) else 0.0
    idx = np.searchsorted(sorted_score, thr, side="right")
    below = np.where(idx > 0, cum_from_left[np.clip(idx - 1, 0, None)], 0.0)
    return total - below


def find_best_cut(y_test, y_score, w_test, bkg_score, bkg_weight):
    """Threshold maximizing N_VBF / sqrt(N_VBF + N_ggH + N_bkg), using event
    weights and the real (DY+EWK+TT+DiBoson) background yield in the signal
    region. Also computes a diagnostic combined two-category Asimov
    significance curve (VBF-like category vs. ggH-like category, both treating
    ggH+VBF as signal and the real background as background), but the cut is
    always chosen from the first (simple) FOM."""
    fpr, tpr, thr = roc_curve(y_test, y_score, sample_weight=w_test)

    VBF_total = w_test[y_test == 1].sum()
    ggH_total = w_test[y_test == 0].sum()
    bkg_total = bkg_weight.sum()

    N_VBF = tpr * VBF_total
    N_ggH = fpr * ggH_total
    N_bkg = weighted_yield_above_threshold(bkg_score, bkg_weight, thr)

    denom = np.sqrt(N_VBF + N_ggH + N_bkg)
    denom_noBKG = np.sqrt(N_VBF + N_ggH)
    fom_simple = np.divide(N_VBF, denom, out=np.zeros_like(N_VBF), where=denom > 0)
    fom_simple_noBKG = np.divide(N_VBF, denom_noBKG, out=np.zeros_like(N_VBF), where=denom > 0)

    S_VBFcat = N_VBF + N_ggH
    B_VBFcat = N_bkg
    S_ggHcat = (VBF_total + ggH_total) - S_VBFcat
    B_ggHcat = bkg_total - B_VBFcat
    Z_VBFcat = asimov_significance(S_VBFcat, B_VBFcat)
    Z_ggHcat = asimov_significance(S_ggHcat, B_ggHcat)
    fom_asimov = np.sqrt(Z_VBFcat**2 + Z_ggHcat**2)

    #best_idx = np.argmax(fom_simple)
    best_idx = np.argmax(fom_simple)
    return (
        thr[best_idx],
        fom_simple[best_idx],
        N_VBF[best_idx],
        N_ggH[best_idx],
        N_bkg[best_idx],
        (fpr, tpr, thr, fom_simple, fom_asimov, fom_simple_noBKG, Z_ggHcat, Z_VBFcat),
    )


def weighted_roc_point(y_test, pred, w_test):
    """Weighted (ggH mismatch rate, VBF efficiency) point for any 0/1 prediction
    array (kinematic cut, a fixed BDT cut, ...), for direct comparison to a BDT
    ROC curve."""
    ggH_total = w_test[y_test == 0].sum()
    VBF_total = w_test[y_test == 1].sum()
    fpr_point = w_test[(y_test == 0) & (pred == 1)].sum() / ggH_total
    tpr_point = w_test[(y_test == 1) & (pred == 1)].sum() / VBF_total
    return fpr_point, tpr_point


def plot_roc_curve(fpr, tpr, kin_point, bdt_point, plot_path, region_name, AUC):
    kin_fpr, kin_tpr = kin_point
    bdt_fpr, bdt_tpr = bdt_point
    fig = plt.figure()
    lw = 2
    plt.plot(fpr, tpr, color="darkorange", lw=lw, label="BDT ROC curve")
    plt.plot([0, 1], [0, 1], color="navy", lw=lw, linestyle="--")
    plt.scatter(
        kin_fpr, kin_tpr, color="black", s=80, marker="o", zorder=5,
        label="Kinematic point",
    )
    plt.scatter(
        bdt_fpr, bdt_tpr, color="red", s=80, marker="o", zorder=5,
        label="BDT cut point (FOM-optimal)",
    )
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.ylabel("VBF Efficiency")
    plt.xlabel("ggH Mismatch Rate")
    plt.text(0.5, 0.3, "AUC = %.4f" % AUC)
    plt.legend(loc="lower right")
    hep.cms.label(data="True", label="", year=ERA, com="13.6", lumi=str(xgb_utils.luminosity[ERA]))
    os.makedirs(f"{plot_path}training/", exist_ok=True)
    plt.savefig(f"{plot_path}training/myroc_{region_name}.png")
    plt.savefig(f"{plot_path}training/myroc_{region_name}.pdf")
    plt.close(fig)


def plot_fom_curve(thr, fom_simple, fom_asimov, fom_simple_noBKG, Z_ggH, Z_VBF, best_idx, plot_path, region_name):
    """Plots both FOM curves on twin y-axes. The vertical line marks the cut
    chosen from fom_simple (the FOM actually used by find_best_cut) -- the
    fom_asimov curve is diagnostic-only and may peak elsewhere."""
    fig, ax1 = plt.subplots()

    color_simple = "darkorange"
    color_asimov = "steelblue"
    color_simple_noBKG = "green"
    color_ggH = "red"
    color_VBF = "blue"

    ax1.plot(
        thr, fom_simple/np.sum(fom_simple), color=color_simple, lw=2,
        label=r"$N_{VBF}/\sqrt{N_{VBF}+N_{ggH}+N_{bkg}}$ norm (used for cut)",
    )
    ax1.plot(
        thr, fom_simple_noBKG/np.sum(fom_simple_noBKG), color=color_simple_noBKG, lw=2,
        label=r"$N_{VBF}/\sqrt{N_{VBF}+N_{ggH}}$ norm",
    )
    ax1.set_xlabel("BDT score threshold")
    ax1.set_ylabel(r"$N_{VBF} / \sqrt{N_{VBF} + N_{ggH} (+ N_{bkg}})$", color=color_simple)
    ax1.tick_params(axis="y", labelcolor=color_simple)
    ax1.set_xlim([0.0, 1.0])

    ax2 = ax1.twinx()
    ax2.plot(
        thr, fom_asimov, color=color_asimov, lw=2,
        label="Combined Asimov significance",
    )
    ax2.plot(
        thr, Z_ggH*np.sum(fom_asimov)/np.sum(Z_ggH), color=color_ggH, lw=2,
        label="ggH Asimov Sig",
    )
    ax2.plot(
        thr, Z_VBF*np.sum(fom_asimov)/np.sum(Z_VBF), color=color_VBF, lw=2,
        label="VBF Asimov Sig",
    )
    ax2.set_ylabel("Combined Asimov significance", color=color_asimov)
    ax2.tick_params(axis="y", labelcolor=color_asimov)

    ax1.axvline(thr[best_idx], color="black", linestyle="--", label=f"cut = {thr[best_idx]:.3f}")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="best", fontsize="small")

    hep.cms.label(data="True", label="", year=ERA, com="13.6", lumi=str(xgb_utils.luminosity[ERA]))
    os.makedirs(f"{plot_path}training/", exist_ok=True)
    plt.savefig(f"{plot_path}training/fom_curve_{region_name}.png")
    plt.savefig(f"{plot_path}training/fom_curve_{region_name}.pdf")
    plt.close(fig)


def plot_feature_importance(model, feature_vars, plot_path, region_name):
    model.get_booster().feature_names = feature_vars
    fig = plt.figure()
    xgb.plot_importance(model, xlabel="F score (weight)")
    plt.tight_layout()
    os.makedirs(f"{plot_path}training/", exist_ok=True)
    plt.savefig(f"{plot_path}training/feature_importance_{region_name}.png", bbox_inches="tight")
    plt.savefig(f"{plot_path}training/feature_importance_{region_name}.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_discriminator_with_background(
    y_test, y_pred, y_train, y_pred_train, w_test, w_train, bkg_score, bkg_weight,
    era, plot_path, scale="log",
):
    """Same signal (VBF) / ggH test-vs-train discriminator histograms as
    xgb_utils.plot_discriminator, plus one more series for the real
    (DY+EWK+TT+DiBoson) background, already restricted to the SIGNAL_REGION
    mass window by the caller."""
    y_frame = pd.DataFrame({"truth": y_test, "disriminator": y_pred, "weight": w_test})
    y_frame_train = pd.DataFrame({"truth": y_train, "disriminator": y_pred_train, "weight": w_train})

    discriminator_ggH = y_frame[y_frame["truth"] == 0]["disriminator"].values
    discriminator_ggH_train = y_frame_train[y_frame_train["truth"] == 0]["disriminator"].values
    discriminator_VBF = y_frame[y_frame["truth"] == 1]["disriminator"].values
    discriminator_VBF_train = y_frame_train[y_frame_train["truth"] == 1]["disriminator"].values
    weight_ggH = y_frame[y_frame["truth"] == 0]["weight"].values
    weight_ggH_train = y_frame_train[y_frame_train["truth"] == 0]["weight"].values
    weight_VBF = y_frame[y_frame["truth"] == 1]["weight"].values
    weight_VBF_train = y_frame_train[y_frame_train["truth"] == 1]["weight"].values

    fig = plt.figure()
    plt.hist(
        discriminator_VBF, density=True, bins=100, alpha=1.0, histtype="step", lw=2,
        label="VBF - test", weights=weight_VBF,
    )
    plt.hist(
        discriminator_VBF_train, density=True, bins=100, alpha=1.0, histtype="step", lw=2,
        label="VBF - train", weights=weight_VBF_train,
    )
    plt.hist(
        discriminator_ggH, density=True, bins=100, alpha=1.0, histtype="step", lw=2,
        label="ggH - test", weights=weight_ggH,
    )
    plt.hist(
        discriminator_ggH_train, density=True, bins=100, alpha=1.0, histtype="step", lw=2,
        label="ggH - train", weights=weight_ggH_train,
    )
    plt.hist(
        bkg_score, density=True, bins=100, alpha=1.0, histtype="step", lw=2,
        label="Bkg (DY+EWK+TT+DiBoson), SR", weights=bkg_weight,
    )
    plt.yscale(scale)
    plt.xlim([0.0, 1.0])
    if scale == "log":
        plt.ylim([0.001, 1000.0])
    plt.legend(loc="upper right", fontsize="small")
    plt.xlabel("BDT response")
    plt.ylabel("Events")
    hep.cms.label(data="True", label="", year=era, com="13.6", lumi=str(xgb_utils.luminosity[era]))
    os.makedirs(f"{plot_path}training/", exist_ok=True)
    plt.savefig(f"{plot_path}training/mydiscriminator_{scale}Y.pdf")
    plt.savefig(f"{plot_path}training/mydiscriminator_{scale}Y.png")
    plt.close(fig)


def train_region(bdt_df, variables, region_name, region_plot_path, region_bkg_df):
    print(f"[INFO] Training region: {region_name}")

    feature_vars = variables[:-4] + ["HT_extra"]

    X = bdt_df[feature_vars]
    Y = bdt_df["y_truth"]

    scaler = StandardScaler()
    scaler.set_output(transform="pandas")
    X_scaled = scaler.fit_transform(X)

    signal_counts = np.array(
        [
            bdt_df.loc[bdt_df.y_truth == 0, "weight"].sum(),
            bdt_df.loc[bdt_df.y_truth == 1, "weight"].sum(),
        ]
    )

    x_train, x_test, y_train, y_test, w_train, w_test, kin_train, kin_test = train_test_split(
        X_scaled.values,
        Y.values,
        bdt_df["weight"].values,
        bdt_df["is_VBF_category"].values,
        train_size=SAMPLE_SIZE * (1 - TEST_SIZE),
        test_size=SAMPLE_SIZE * TEST_SIZE,
        random_state=SEED,
    )

    model = xgb.XGBClassifier(
        objective="binary:logistic",
        n_estimators=2000,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        verbosity=1,
        n_jobs=4,
        eval_metric=["logloss", "auc"],
        device="cuda",
        early_stopping_rounds=50,
    )

    model.fit(
        x_train,
        y_train,
        eval_set=[(x_train, y_train), (x_test, y_test)],
    )

    y_score = model.predict_proba(x_test)[:, 1]
    y_score_train = model.predict_proba(x_train)[:, 1]

    AUC = roc_auc_score(y_test, y_score)
    AUC_weighted = roc_auc_score(y_test, y_score, sample_weight=np.absolute(w_test))
    print(f"[INFO] {region_name}: AUC = {AUC:.4f}, weighted AUC = {AUC_weighted:.4f}")

    sr_mask = region_bkg_df[MASS_VAR].between(*SIGNAL_REGION)
    bkg_sr_df = region_bkg_df[sr_mask]
    bkg_score = model.predict_proba(
        scaler.transform(bkg_sr_df[feature_vars]).values
    )[:, 1]
    bkg_weight = bkg_sr_df["weight"].values
    print(
        f"[INFO] {region_name}: background (DY+EWK+TT+DiBoson) SR events = "
        f"{len(bkg_sr_df)}, weighted yield = {bkg_weight.sum():.3f}"
    )

    bdt_cut, fom_best, N_VBF_best, N_ggH_best, N_bkg_best, (fpr, tpr, thr, fom_simple, fom_asimov, fom_simple_noBKG, Z_ggH, Z_VBF) = (
        find_best_cut(y_test, y_score, w_test, bkg_score, bkg_weight)
    )
    #best_idx = np.argmax(fom_simple)
    best_idx = np.argmax(fom_simple)
    print(
        f"[INFO] {region_name}: best cut = {bdt_cut:.4f}, "
        f"FOM_simple = {fom_best:.4f}, FOM_asimov (at cut) = {fom_asimov[best_idx]:.4f}, "
        f"N_VBF = {N_VBF_best:.3f}, N_ggH = {N_ggH_best:.3f}, N_bkg = {N_bkg_best:.3f}"
    )

    kin_point = weighted_roc_point(y_test, kin_test, w_test)
    print(
        f"[INFO] {region_name}: kinematic point (ggH mismatch, VBF eff) = "
        f"({kin_point[0]:.4f}, {kin_point[1]:.4f})"
    )

    bdt_point = (fpr[best_idx], tpr[best_idx])
    print(
        f"[INFO] {region_name}: BDT cut point (ggH mismatch, VBF eff) = "
        f"({bdt_point[0]:.4f}, {bdt_point[1]:.4f})"
    )

    os.makedirs(region_plot_path, exist_ok=True)
    plot_confusion_matrix(
        y_test, (y_score > bdt_cut).astype(int), signal_counts, region_plot_path, region_name
    )
    plot_confusion_matrix(
        y_test, kin_test, signal_counts, region_plot_path, f"{region_name}_kinematic"
    )
    plot_roc_curve(fpr, tpr, kin_point, bdt_point, region_plot_path, region_name, AUC_weighted)
    plot_fom_curve(thr, fom_simple, fom_asimov, fom_simple_noBKG, Z_ggH, Z_VBF, best_idx, region_plot_path, region_name)
    plot_discriminator_with_background(
        y_test, y_score, y_train, y_score_train, w_test, w_train, bkg_score, bkg_weight,
        ERA, region_plot_path, scale="log",
    )
    plot_discriminator_with_background(
        y_test, y_score, y_train, y_score_train, w_test, w_train, bkg_score, bkg_weight,
        ERA, region_plot_path, scale="linear",
    )
    plot_feature_importance(model, feature_vars, region_plot_path, region_name)

    os.makedirs("models", exist_ok=True)
    region_result = {
        "model": model,
        "scaler": scaler,
        "cut": float(bdt_cut),
        "features": feature_vars,
    }
    with open(f"models/model_VBFcat_{region_name}.pkl", "wb") as f:
        pickle.dump(region_result, f)

    eval_data = {
        "y_test": y_test,
        "y_score": y_score,
        "bdt_pred": (y_score > bdt_cut).astype(int),
        "kin_pred": kin_test,
        "w_test": w_test,
    }

    return region_result, eval_data


def draw_input_comparisons(bdt_df):
    """ggH-vs-VBF shape comparison (via utils.ggH_vs_VBF.draw_ggH_vs_VBF_comparison,
    the same helper SignalExtraction.ipynb uses) for every BDT input variable, run
    once for the combined (all n_jet) population and once per n_jet region -- using
    each region's own variable list (bdt_variables for multijet/combined,
    bdt_variables1 for onejet, since the latter excludes dijet-only variables that
    aren't meaningful for n_jet == 1 events)."""
    regions = {
        "combined": (bdt_df, bdt_variables[:-4]),
        "multijet": (bdt_df[REGIONS["multijet"]["n_jet_cut"](bdt_df["n_jet"])], bdt_variables[:-4]),
        "onejet": (bdt_df[REGIONS["onejet"]["n_jet_cut"](bdt_df["n_jet"])], bdt_variables1[:-4]),
    }
    for region_name, (region_df, variables) in regions.items():
        output_directory = f"{plot_path}{region_name}/inputs/"
        print(f"[INFO] Drawing ggH vs VBF input comparisons: {region_name}")
        for variable in variables:
            draw_ggH_vs_VBF_comparison(region_df, variable, output_directory=output_directory)


def load_tuple(file_name):
    with uproot.open(file_name) as file:
        arrays = file["tree_output"].arrays(bdt_variables)
    df = ak.to_dataframe(arrays).reset_index(drop=True)
    df["HT_extra"] = df["HT"] - df["leading_jet_pt"]
    return df


def load_categorized_tuple(file_name, columns):
    """Like load_tuple, but for an arbitrary column list (used to read the
    *_categorized.root files for the sculpting diagnostic, whose column needs
    -- get_variables() physics inputs, not the categorization BDT's own
    feature list -- differ from bdt_variables)."""
    with uproot.open(file_name) as file:
        arrays = file["tree_output"].arrays(columns)
    return ak.to_dataframe(arrays).reset_index(drop=True)


def score_full_population(df, region_results):
    is_VBF_categoryBDT = np.zeros(len(df), dtype=np.int32)

    for region_name, region in REGIONS.items():
        result = region_results[region_name]
        mask = region["n_jet_cut"](df["n_jet"]).values
        if not mask.any():
            continue
        X = result["scaler"].transform(df.loc[mask, result["features"]]).values
        score = result["model"].predict_proba(X)[:, 1]
        is_VBF_categoryBDT[mask] = (score > result["cut"]).astype(np.int32)

    # n_jet == 0 events are covered by neither region and stay 0 (ggH-like).
    return is_VBF_categoryBDT


def add_ggH_category_branch(is_VBF_categoryBDT):
    """is_ggH_categoryBDT is the exact complement of is_VBF_categoryBDT (both 0/1)."""
    return (1 - is_VBF_categoryBDT).astype(np.int32)


def append_branch(input_path, output_path, branches):
    """Copy input_path to output_path and add the named int branches to tree_output.

    `branches` is a dict of {branch_name: np.ndarray[int]}, all written in a
    single pass so large files are only copied once.
    """
    print(f"[INFO] Writing {output_path}")
    shutil.copy2(input_path, output_path)

    root_file = root.TFile.Open(output_path, "UPDATE")
    tree = root_file.Get("tree_output")

    n_entries = tree.GetEntries()
    for branch_name, values in branches.items():
        if n_entries != len(values):
            root_file.Close()
            raise RuntimeError(
                f"Entry mismatch for {output_path}[{branch_name}]: tree has "
                f"{n_entries}, predictions have {len(values)}"
            )

    branch_values = {name: array("i", [0]) for name in branches}
    new_branches = {
        name: tree.Branch(name, branch_values[name], f"{name}/I")
        for name in branches
    }

    for i in range(n_entries):
        if i % 100000 == 0:
            print(f"[INFO] {output_path}: entry {i}/{n_entries}")
        for name, values in branches.items():
            branch_values[name][0] = int(values[i])
            new_branches[name].Fill()

    tree.Write("", root.TObject.kOverwrite)
    root_file.Close()


def apply_bdt_to_datasets(region_results, dataset_names, preloaded_dfs=None):
    for name in dataset_names:
        input_path = f"{tuple_dir}{name}_Combined_tuples.root"
        output_path = f"{tuple_dir}{name}_Combined_tuples_categorized.root"

        print(f"[INFO] Scoring {name}")
        if preloaded_dfs is not None and name in preloaded_dfs:
            df = preloaded_dfs[name]
        else:
            df = load_tuple(input_path)
        is_VBF_categoryBDT = score_full_population(df, region_results)
        is_ggH_categoryBDT = add_ggH_category_branch(is_VBF_categoryBDT)

        append_branch(
            input_path,
            output_path,
            {
                "is_VBF_categoryBDT": is_VBF_categoryBDT,
                "is_ggH_categoryBDT": is_ggH_categoryBDT,
            },
        )


def build_zero_jet_eval(bdt_df):
    """eval_data-shaped bundle for the n_jet == 0 events, which are covered by
    neither BDT: they always default to ggH-like (bdt_pred = 0, y_score = 0)."""
    zero_jet_df = bdt_df[bdt_df["n_jet"] == 0]
    return {
        "y_test": zero_jet_df["y_truth"].values,
        "y_score": np.zeros(len(zero_jet_df)),
        "bdt_pred": np.zeros(len(zero_jet_df), dtype=int),
        "kin_pred": zero_jet_df["is_VBF_category"].values,
        "w_test": zero_jet_df["weight"].values,
    }


def build_combined_eval(bdt_df, region_eval_data):
    """Pool the two regions' held-out test sets with the n_jet == 0 events into
    one 'combined' eval bundle, correcting for their different inclusion
    fractions: only TEST_SIZE of each region's rows are held out (the rest were
    used for training), while n_jet == 0 is included at 100% (no model is ever
    trained on it). Naively concatenating raw weights would understate the
    regions' true contribution relative to n_jet == 0 by ~1/TEST_SIZE. Since the
    test split is a uniform random TEST_SIZE subsample, scaling each region's
    held-out weight by 1/TEST_SIZE gives an unbiased estimate of that region's
    true full weighted contribution before pooling.
    """
    reweighted_regions = []
    for e in region_eval_data.values():
        scaled = dict(e)
        scaled["w_test"] = e["w_test"] / TEST_SIZE
        reweighted_regions.append(scaled)

    all_eval = reweighted_regions + [build_zero_jet_eval(bdt_df)]
    return {
        "y_test": np.concatenate([e["y_test"] for e in all_eval]),
        "y_score": np.concatenate([e["y_score"] for e in all_eval]),
        "bdt_pred": np.concatenate([e["bdt_pred"] for e in all_eval]),
        "w_test": np.concatenate([e["w_test"] for e in all_eval]),
    }


def plot_combined_confusion_matrices(bdt_df, region_eval_data, plot_path):
    """Combined (all n_jet) confusion matrices for the BDT categorization and the
    baseline kinematic (is_ggH_category/is_VBF_category) categorization.

    The BDT panel is built from the two regions' held-out test sets plus the
    (untrained) n_jet == 0 events, since evaluating the trained onejet/multijet
    models on their own training rows would be optimistically biased — weighted
    by build_combined_eval to correct for the regions' partial (TEST_SIZE)
    inclusion. The kinematic panel has no such leakage concern (is_VBF_category
    isn't model-derived), so it uses the full bdt_df, unweighted — matching
    SignalExtraction.ipynb's inclusive kinematic confusion matrix.
    """
    combined = build_combined_eval(bdt_df, region_eval_data)

    signal_counts = np.array(
        [
            bdt_df.loc[bdt_df.y_truth == 0, "weight"].sum(),
            bdt_df.loc[bdt_df.y_truth == 1, "weight"].sum(),
        ]
    )

    combined_plot_path = f"{plot_path}combined/"
    os.makedirs(combined_plot_path, exist_ok=True)
    plot_confusion_matrix(
        combined["y_test"], combined["bdt_pred"], signal_counts, combined_plot_path, "combined",
        sample_weight=combined["w_test"],
    )
    plot_confusion_matrix(
        bdt_df["y_truth"].values, bdt_df["is_VBF_category"].values,
        signal_counts, combined_plot_path, "combined_kinematic",
    )


def plot_combined_roc_curve(bdt_df, region_eval_data, plot_path):
    """Combined (all n_jet) ROC curve: pools the two regions' held-out scores
    (weighted by build_combined_eval to correct for their partial inclusion)
    with the n_jet == 0 events (fixed score of 0) and sweeps a single threshold
    over the whole population. Approximate, since the two regions' BDT scores
    aren't independently calibrated against each other, but both share the same
    binary:logistic output scale.

    The kinematic point has no train/test-leakage concern (is_VBF_category
    isn't model-derived), so — like plot_combined_confusion_matrices — it's
    computed on the full bdt_df rather than the held-out-only population used
    for the curve/AUC/BDT point.
    """
    combined = build_combined_eval(bdt_df, region_eval_data)
    y_test = combined["y_test"]
    y_score = combined["y_score"]
    w_test = combined["w_test"]
    bdt_pred = combined["bdt_pred"]

    fpr, tpr, thr = roc_curve(y_test, y_score, sample_weight=w_test)
    AUC_weighted = roc_auc_score(y_test, y_score, sample_weight=np.absolute(w_test))
    print(f"[INFO] combined: weighted AUC = {AUC_weighted:.4f}")

    kin_point = weighted_roc_point(
        bdt_df["y_truth"].values, bdt_df["is_VBF_category"].values, bdt_df["weight"].values
    )
    bdt_point = weighted_roc_point(y_test, bdt_pred, w_test)

    combined_plot_path = f"{plot_path}combined/"
    os.makedirs(combined_plot_path, exist_ok=True)
    plot_roc_curve(fpr, tpr, kin_point, bdt_point, combined_plot_path, "combined", AUC_weighted)


# get_variables() branch names that lib/CreateTuple.h only computes from a
# real dijet/leading-jet system -- for events without enough jets it leaves
# them at a 0 (or -1, for pt_balance/pt_centrality) padding value rather than
# a real measurement, so an n_jet floor is required to plot their true shape.
DIJET_VARIABLES = frozenset({
    "subleading_jet_pt", "diJet_mass", "delta_eta_diJet", "delta_phi_diJet",
    "z_zeppenfeld", "pt_balance", "pt_centrality",
})
SINGLE_JET_VARIABLES = frozenset({
    "leading_jet_pt", "leading_jet_eta", "min_delta_eta_diMuon_jet", "min_delta_phi_diMuon_jet",
})


def jet_requirement(branch_name):
    """Minimum n_jet for which branch_name is a real measurement rather than
    CreateTuple.h's padding value for a missing jet. Everything else (muon-level
    variables, n_jet itself, SoftActivityJet-derived HT/n_SoftJet_pt2 which are
    computed independent of the leading/subleading jet selection) is defined
    regardless of n_jet, so no extra restriction is applied."""
    if branch_name in DIJET_VARIABLES:
        return 2
    if branch_name in SINGLE_JET_VARIABLES:
        return 1
    return 0


def plot_variable_sculpting(channel_US, signal_df, background_df, plot_path):
    """For every xgb_utils.get_variables(channel_US, ...) input variable, overlay
    signal/background shapes selected by the kinematic category flag vs. the
    BDT category flag, to check whether switching to the BDT categorization
    sculpts the signal-extraction BDT's input population differently than the
    existing kinematic cut does. One plot per variable, saved separately;
    axis label/binning/range come from plot_macros/utils/labels.py where the
    variable is listed there (falling back to get_variables()'s own label and
    an auto-range 30-bin histogram otherwise)."""
    variables = xgb_utils.get_variables(channel_US, USE_BSCONSTRAIN)[:-3]
    kin_flag = f"is_{channel_US}_category"
    bdt_flag = f"is_{channel_US}_categoryBDT"

    sig_kin = signal_df[signal_df[kin_flag] == 1]
    sig_bdt = signal_df[signal_df[bdt_flag] == 1]
    bkg_kin = background_df[background_df[kin_flag] == 1]
    bkg_bdt = background_df[background_df[bdt_flag] == 1]

    sculpting_plot_path = f"{plot_path}sculpting/"
    os.makedirs(sculpting_plot_path, exist_ok=True)

    for branch_name, _, fallback_label in variables:
        min_n_jet = jet_requirement(branch_name)
        if min_n_jet > 0:
            s_kin = sig_kin[sig_kin["n_jet"] >= min_n_jet]
            s_bdt = sig_bdt[sig_bdt["n_jet"] >= min_n_jet]
            b_kin = bkg_kin[bkg_kin["n_jet"] >= min_n_jet]
            b_bdt = bkg_bdt[bkg_bdt["n_jet"] >= min_n_jet]
        else:
            s_kin, s_bdt, b_kin, b_bdt = sig_kin, sig_bdt, bkg_kin, bkg_bdt

        label = PLOT_X_LABELS.get(branch_name, fallback_label)
        if branch_name in PLOT_X_RANGE:
            bins = np.linspace(*PLOT_X_RANGE[branch_name], PLOT_N_BINS.get(branch_name, 30) + 1)
        else:
            combined = pd.concat(
                [s_kin[branch_name], s_bdt[branch_name], b_kin[branch_name], b_bdt[branch_name]]
            )
            bins = np.linspace(combined.min(), combined.max(), 31)

        fig, ax = plt.subplots()
        ax.hist(
            s_kin[branch_name], bins=bins, weights=s_kin["weight"], density=True,
            histtype="step", lw=2, linestyle="-", color="darkorange", label="Signal (kinematic cat)",
        )
        ax.hist(
            s_bdt[branch_name], bins=bins, weights=s_bdt["weight"], density=True,
            histtype="step", lw=2, linestyle="--", color="red", label="Signal (BDT cat)",
        )
        ax.hist(
            b_kin[branch_name], bins=bins, weights=b_kin["weight"], density=True,
            histtype="step", lw=2, linestyle="-", color="steelblue", label="Background (kinematic cat)",
        )
        ax.hist(
            b_bdt[branch_name], bins=bins, weights=b_bdt["weight"], density=True,
            histtype="step", lw=2, linestyle="--", color="green", label="Background (BDT cat)",
        )
        ax.set_xlim(bins[0], bins[-1])
        ax.set_xlabel(label)
        ax.set_ylabel("a.u.")
        ax.legend(loc="best", fontsize="small")
        hep.cms.label(data="True", label="", year=ERA, com="13.6", lumi=str(xgb_utils.luminosity[ERA]))

        # Both scales: a large fraction of a BDT-selected category's population
        # can sit at a padding/sentinel value (e.g. diJet_mass == 0 for n_jet==1
        # events picked up by the onejet region's BDT, which never sees
        # diJet_mass as a feature) -- on a linear axis that spike swamps the
        # rest of the shape, so a log-scale version is needed to see both.
        for scale in ("log", "linear"):
            ax.set_yscale(scale)
            plt.tight_layout()
            plt.savefig(f"{sculpting_plot_path}sculpting_{channel_US}_category_{branch_name}_{scale}Y.png")
            plt.savefig(f"{sculpting_plot_path}sculpting_{channel_US}_category_{branch_name}_{scale}Y.pdf")
        plt.close(fig)


PAIRS_2D = (
    ("diJet_mass", "delta_eta_diJet"),
    ("diJet_mass", "delta_phi_diJet"),
)


def bins_2d(branch_name, max_bins=40):
    """Bin edges for the 2D sculpting plots: same PLOT_X_RANGE window as the 1D
    plots, but capped at max_bins -- the 1D plots' bin counts (e.g. 150 for
    diJet_mass) are too fine to be legible once split across a second axis.
    Returns None if branch_name has no PLOT_X_RANGE entry, so the caller can
    fall back to an auto range."""
    if branch_name not in PLOT_X_RANGE:
        return None
    n = min(PLOT_N_BINS.get(branch_name, 30), max_bins)
    return np.linspace(*PLOT_X_RANGE[branch_name], n + 1)


def plot_variable_sculpting_2d(channel_US, signal_df, background_df, plot_path):
    """2D shape comparison (e.g. Mjj vs delta_eta_diJet) of pairs of the
    signal-extraction BDT's dijet input variables, split the same 4 ways as
    plot_variable_sculpting (signal/background x kinematic/BDT category) -- a
    correlated sculpting effect between two variables can be invisible in
    either variable's 1D projection alone."""
    kin_flag = f"is_{channel_US}_category"
    bdt_flag = f"is_{channel_US}_categoryBDT"

    subsets = {
        "signal_kinematic": signal_df[signal_df[kin_flag] == 1],
        "signal_bdt": signal_df[signal_df[bdt_flag] == 1],
        "background_kinematic": background_df[background_df[kin_flag] == 1],
        "background_bdt": background_df[background_df[bdt_flag] == 1],
    }

    sculpting_plot_path = f"{plot_path}sculpting/"
    os.makedirs(sculpting_plot_path, exist_ok=True)

    for x_var, y_var in PAIRS_2D:
        min_n_jet = max(jet_requirement(x_var), jet_requirement(y_var))

        x_bins = bins_2d(x_var)
        y_bins = bins_2d(y_var)
        if x_bins is None or y_bins is None:
            restricted = {
                name: (df[df["n_jet"] >= min_n_jet] if min_n_jet > 0 else df)
                for name, df in subsets.items()
            }
            if x_bins is None:
                combined_x = pd.concat([df[x_var] for df in restricted.values()])
                x_bins = np.linspace(combined_x.min(), combined_x.max(), 31)
            if y_bins is None:
                combined_y = pd.concat([df[y_var] for df in restricted.values()])
                y_bins = np.linspace(combined_y.min(), combined_y.max(), 31)

        for selection, subset in subsets.items():
            if min_n_jet > 0:
                subset = subset[subset["n_jet"] >= min_n_jet]

            fig, ax = plt.subplots()
            h, xe, ye = np.histogram2d(
                subset[x_var], subset[y_var], bins=[x_bins, y_bins], weights=subset["weight"],
            )
            mesh = ax.pcolormesh(xe, ye, h.T, cmap="viridis")
            fig.colorbar(mesh, ax=ax, label="Weighted events")
            ax.set_xlabel(PLOT_X_LABELS.get(x_var, x_var))
            ax.set_ylabel(PLOT_X_LABELS.get(y_var, y_var))
            ax.set_title(selection.replace("_", " "))
            hep.cms.label(data="True", label="", year=ERA, com="13.6", lumi=str(xgb_utils.luminosity[ERA]))
            plt.tight_layout()
            plt.savefig(
                f"{sculpting_plot_path}sculpting2D_{channel_US}_category_{x_var}_vs_{y_var}_{selection}.png"
            )
            plt.savefig(
                f"{sculpting_plot_path}sculpting2D_{channel_US}_category_{x_var}_vs_{y_var}_{selection}.pdf"
            )
            plt.close(fig)


def load_and_concat(names, columns):
    """Load each *_categorized.root file in `names` and fold it into a running
    concatenation one at a time, instead of holding all len(names) per-file
    DataFrames plus the concatenated result in memory simultaneously -- DY
    (~29M rows) and DiBoson (~9M rows) make that difference tens of GB."""
    result = None
    for name in names:
        print(f"[INFO] Loading {name} categorized tuple")
        df = load_categorized_tuple(f"{tuple_dir}{name}_Combined_tuples_categorized.root", columns)
        result = df if result is None else pd.concat([result, df], ignore_index=True)
        del df
        gc.collect()
    return result


def run_sculpting_diagnostics(plot_path):
    """Reads the *_categorized.root files (produced by apply_bdt_to_datasets)
    and checks whether the BDT category selection sculpts the signal-extraction
    BDT's input variables differently than the kinematic category selection,
    for both the ggH and VBF categories. Background = DY+EWK+TT+DiBoson only
    (no Data), consistent with the FOM/discriminator background scope above."""
    print("[INFO] Running input-variable sculpting diagnostic")
    ggH_vars = [v[0] for v in xgb_utils.get_variables("ggH", USE_BSCONSTRAIN)[:-3]]
    VBF_vars = [v[0] for v in xgb_utils.get_variables("VBF", USE_BSCONSTRAIN)[:-3]]
    print("[INFO] Loaded signal variables")
    columns = sorted(set(ggH_vars) | set(VBF_vars)) + [
        "is_ggH_category", "is_VBF_category", "is_ggH_categoryBDT", "is_VBF_categoryBDT", "weight",
    ]

    print("[INFO] Creating signal dataframe (ggH+VBF)")
    signal_df = load_and_concat(("ggH", "VBF"), columns)
    print("[INFO] Creating background dataframe (DY+EWK+TT+DiBoson)")
    background_df = load_and_concat(BACKGROUND_NAMES, columns)
    print("[INFO] Created signal/background dataframes")

    for channel_US in ("ggH", "VBF"):
        print("[INFO] Plotting " + channel_US + " BDT input sculpting")
        plot_variable_sculpting(channel_US, signal_df, background_df, plot_path)
        plot_variable_sculpting_2d(channel_US, signal_df, background_df, plot_path)


def main():
    ggH_file_name = f"{tuple_dir}ggH_Combined_tuples.root"
    VBF_file_name = f"{tuple_dir}VBF_Combined_tuples.root"

    PLOT_INPUTS = False
    RUN_SCULPTING_DIAGNOSTICS = False

    print("[INFO] Loading ggH/VBF tuples")
    ggH_df = load_tuple(ggH_file_name)
    VBF_df = load_tuple(VBF_file_name)

    ggH_df["y_truth"] = 0
    VBF_df["y_truth"] = 1

    bdt_df = pd.concat([ggH_df, VBF_df], ignore_index=True)
    neither = (bdt_df["is_ggH_category"] == 0) & (bdt_df["is_VBF_category"] == 0)
    bdt_df = bdt_df[~neither]

    if PLOT_INPUTS:
        draw_input_comparisons(bdt_df)

    print("[INFO] Loading background tuples (DY, EWK, TT, DiBoson)")
    bkg_dfs = {
        name: load_tuple(f"{tuple_dir}{name}_Combined_tuples.root") for name in BACKGROUND_NAMES
    }
    bkg_df = pd.concat(bkg_dfs.values(), ignore_index=True)

    region_results = {}
    region_eval_data = {}
    for region_name, region in REGIONS.items():
        region_mask = region["n_jet_cut"](bdt_df["n_jet"])
        region_df = bdt_df[region_mask]
        region_bkg_mask = region["n_jet_cut"](bkg_df["n_jet"])
        region_bkg_df = bkg_df[region_bkg_mask]
        region_results[region_name], region_eval_data[region_name] = train_region(
            region_df, region["variables"], region_name, f"{plot_path}{region_name}/", region_bkg_df
        )

    print("[INFO] Building combined (all n_jet) confusion matrices")
    plot_combined_confusion_matrices(bdt_df, region_eval_data, plot_path)

    print("[INFO] Building combined (all n_jet) ROC curve")
    plot_combined_roc_curve(bdt_df, region_eval_data, plot_path)

    print("[INFO] Scoring full population and appending BDT category branches")
    apply_bdt_to_datasets(
        region_results, ("ggH", "VBF"), preloaded_dfs={"ggH": ggH_df, "VBF": VBF_df}
    )

    print("[INFO] Applying the same working points to background/data tuples")
    apply_bdt_to_datasets(
        region_results, ("Data",) + BACKGROUND_NAMES, preloaded_dfs=bkg_dfs
    )

    if RUN_SCULPTING_DIAGNOSTICS:
        print("[INFO] Freeing training-time dataframes before the sculpting diagnostic")
        del ggH_df, VBF_df, bdt_df, bkg_df, bkg_dfs
        gc.collect()
        run_sculpting_diagnostics(plot_path)

    print("[INFO] Done")


if __name__ == "__main__":
    main()
