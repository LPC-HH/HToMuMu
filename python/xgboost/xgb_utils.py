import sys
import matplotlib
import mplhep as hep
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import pickle as pickle
import ROOT as root
import uproot as uproot
import xgboost as xgb

root.gROOT.Reset()
matplotlib.use("Agg")
plt.style.use(hep.style.CMS)
use_skim = False ###SHOULD THIS BE SET TO TRUE
root.gROOT.SetBatch(True)
root.gStyle.SetOptStat(0)
root.gStyle.SetOptFit(111)
root.gStyle.SetPaintTextFormat("2.1f")

luminosity = {
    "2022": 7.9804,
    "2022EE": 26.6717,
    "2022Combined": 34.6521,
    "2023": 17.794,
    "2023BPix": 9.451,
    "2023Combined": 27.245,
    "2024": 	109.08,
    # "Combined": 61.897,
    "Combined": 170.905,
}


def copy_and_skim_tree(tuple_path, tuple_name, BDT_path, BDT_name, channel_US, use_bsConstrain):

    original_file = root.TFile.Open(tuple_path + tuple_name)
    original_tree = original_file.Get("tree_output")
    if use_bsConstrain:
        cuts = (
            "diMuon_bsConstrainedMass > 100 && diMuon_bsConstrainedMass < 180 && is_" + channel_US + "_category == 1"
        )
    else:
        cuts = (
            "diMuon_mass > 100 && diMuon_mass < 180 && is_" + channel_US + "_category == 1"
        )
    skim_file = root.TFile.Open(BDT_path + BDT_name, "RECREATE")
    skim_tree = original_tree.CopyTree(cuts)
    skim_tree.Write("tree_output")
    skim_file.Close()
    original_file.Close()


def append_BDT_score(
    file_type,
    channel_US,
    era,
    model_era,
    signal_subset,
    background_subset,
    variables,
    mean_map,
    std_map,
    do_standardization,
    use_bsConstrain,
    use_skim=False,
):

    subset_title = f"B{background_subset}_S{signal_subset}"
    tuple_subset = ""
    if file_type == "background" or file_type == "bkg":
        tuple_subset = background_subset
    elif file_type == "signal":
        tuple_subset = signal_subset

    if not use_skim:
        tuple_path = "../../root_io/tuples/"
        tuple_name = f"{file_type}_{era}_tuples.root"
        BDT_path = f"{tuple_path}BDT_score/{channel_US}/{subset_title}/"
        BDT_name = f"{file_type}_{era}_{subset_title}.root"
    else:
        tuple_path = f"../../root_io/skim/{channel_US}/"
        tuple_name = f"{file_type}_{era}_skim_{tuple_subset}.root"
        BDT_path = f"../../root_io/skim/BDT_score/{channel_US}/"
        BDT_name = f"{file_type}_{era}_skim_{subset_title}.root"

    os.makedirs(BDT_path, exist_ok=True)
    file_name = BDT_path + BDT_name
    print(f"[INFO] Creating BDT file: {file_name}")

    copy_and_skim_tree(tuple_path, tuple_name, BDT_path, BDT_name, channel_US, use_bsConstrain)

    with uproot.open(file_name) as file:
        df = pd.DataFrame(
            file["tree_output"].arrays([var[0] for var in variables], library="np"),
        )

    file = root.TFile(file_name, "update")
    tree = file.Get("tree_output")

    model_file = f"./models/model_{channel_US}_{model_era}_{subset_title}.pkl" ###SHOULD WE SWITCH TO ERA NOT MODEL ERA
    if use_bsConstrain:
        model_file = f"./models/model_{channel_US}_{model_era}_{subset_title}_bsC.pkl"
        

    x_test = df.values
    if do_standardization:
        for i, var in enumerate(variables):
            print("standarizing : ", var[0])
            print("Iterator : ", i)
            null_value = 0
            if var[0] in ["delta_phi_diJet", "pt_balance"]:
                null_value = -1
            mask = x_test[:, i] != null_value
            x_test[mask, i] = (x_test[mask, i] - mean_map[var[0]]) / std_map[var[0]]

    # get model from file
    with open(model_file, "rb") as pkl_file:
        model = pickle.load(pkl_file)

    # make predictions for test data
    y_pred = model.predict_proba(x_test)[:, 1]
    print("y_pred", y_pred)
    # Debug histogram (optional)
    plt.figure()
    plt.hist(y_pred, bins=50, alpha=0.3)
    plt.title(f"Discriminator - {file_type} {era}")
    plt.savefig(f"mydiscriminator_{era}.png")

    ##Creating a new TTree with the discriminator

    n_entries = tree.GetEntries()
    print("n_entries = ", n_entries)
    BDT_var_name = "BDT_" + channel_US

    root.gROOT.ProcessLine("struct MyStruct{float BDT_var;};")

    from ROOT import MyStruct

    # Create branches in the tree
    my_struct = MyStruct()
    print(my_struct)
    print(root.addressof(my_struct))
    print(root.addressof(my_struct, "BDT_var"))
    root.addressof(my_struct, "BDT_var")
    new_branch = tree.Branch(
        BDT_var_name, root.addressof(my_struct, "BDT_var"), f"{BDT_var_name}/F"
    )

    for i in range(n_entries):
        tree.GetEntry(i)
        if i % 10000 == 0:
            print(f"[INFO] Processing entry {i} of {n_entries}")
        my_struct.BDT_var = y_pred[i]
        new_branch.Fill()

    tree.GetCurrentFile().Write()
    tree.GetCurrentFile().Close()

def get_variables(channel_US, use_bsConstrain):
    channel_vars = [
        ["diMuon_rapidity", "diMuon_rapidity", r"$y_{\mu\mu}$"],
        ["mu1_eta", "mu1_eta", r"$\eta_{\mu 1}$"],
        ["mu2_eta", "mu2_eta", r"$\eta_{\mu 2}$"],
        ["phi_CS", "phi_CS", r"$\phi_{CS}$"],
        ["cos_theta_CS", "cos_theta_CS", r"$cos(\theta_{CS})$"],
        # # Jet vchannel_vars
        ["n_jet", "n_jet", r"$N_{jets}$"],
        ["leading_jet_pt", "leading_jet_pt", r"$p_T^{j1}$"],
        ["leading_jet_eta", "leading_jet_eta", r"$\eta_{j1}$"],
        ["subleading_jet_pt", "subleading_jet_pt", r"$p_T^{j2}$ [GeV]"],
        ["diJet_mass", "diJet_mass", r"$m_{jj}$ [GeV]"],
        ["delta_eta_diJet", "delta_eta_diJet", r"$\Delta\eta_{jj}$"],
        ["delta_phi_diJet", "delta_phi_diJet", r"$\Delta\phi_{jj}$ [rad]"],
        ["z_zeppenfeld", "z_zeppenfeld", r"$Z^{*} Zeppendfeld$"],
        [
            "min_delta_eta_diMuon_jet",
            "min_delta_eta_diMuon_jet",
            r"min$|\Delta\eta_{\mu\mu,j}|$",
        ],
        [
            "min_delta_phi_diMuon_jet",
            "min_delta_phi_diMuon_jet",
            r"min$|\Delta\phi_{\mu\mu,j}|$ [rad]",
        ],
    ]
    if use_bsConstrain:
        channel_vars += [
            ["diMuon_bsConstrainedPt", "diMuon_bsConstrainedPt", r"$p_T^{\mu\mu}$ [GeV] (bsC)"],
            [
                "mu1_bsConstrainedPt_mass_ratio", 
                "mu1_bsConstrainedPt_mass_ratio", 
                r"$p_T^{\mu 1}/m_{\mu\mu} (bsC)$"
            ],
            [
                "mu2_bsConstrainedPt_mass_ratio", 
                "mu2_bsConstrainedPt_mass_ratio", 
                r"$p_T^{\mu 2}/m_{\mu\mu} (bsC)$"
            ],
        ]
    else: 
        channel_vars += [
            ["diMuon_pt", "diMuon_pt", r"$p_T^{\mu\mu}$ [GeV]"],
            ["mu1_pt_mass_ratio", "mu1_pt_mass_ratio", r"$p_T^{\mu 1}/m_{\mu\mu}$"],
            ["mu2_pt_mass_ratio", "mu2_pt_mass_ratio", r"$p_T^{\mu 2}/m_{\mu\mu}$"],
        ]
    if channel_US == "VBF":
        channel_vars += [
            # VBF sspecific vchannel_vars
            ["pt_balance", "pt_balance", r"$R(p_T)$"],
            ["pt_centrality", "pt_centrality", r"$p_{T}-centrality$"],
            ["n_SoftJet_pt2", "n_SoftJet_pt2", r"$N_{2}^{soft}$"],
            ["HT", "HT", r"$H_{T}^{2}(soft)$"],
        ]

    # DO NOT CHANGE THE ORDER OF THIS VARIABLES
    if use_bsConstrain:
        channel_vars += [
                        [
                            "diMuon_bsConstrainedMass",
                            "diMuon_bsConstrainedMass", 
                            "diMuon_bsConstrainedMass"
                        ],
                        [
                            "relative_diMuon_bsConstrainedMass_error", 
                            "relative_diMuon_bsConstrainedMass_error", 
                            "relative_diMuon_bsConstrainedMass_error"
                        ],
                        ["weight", "weight", "weight"]]
    else: 
        channel_vars += [["diMuon_mass", "diMuon_mass", "diMuon_mass"],
                        [
                            "relative_diMuon_mass_error",
                            "relative_diMuon_mass_error",
                            "relative_diMuon_mass_error"
                        ],
                        ["weight", "weight", "weight"]]
    return channel_vars

def plot_discriminator(
    y_test,
    y_pred,
    y_train,
    y_pred_train,
    sample_weights_test,
    sample_weights_train,
    era,
    plot_path,
    scale="log",
):
    y_frame = pd.DataFrame(
        {"truth": y_test, "disriminator": y_pred, "weight": sample_weights_test}
    )
    y_frame_train = pd.DataFrame(
        {
            "truth": y_train,
            "disriminator": y_pred_train,
            "weight": sample_weights_train,
        }
    )
    discriminator_bkg = y_frame[y_frame["truth"] == 0]["disriminator"].values
    discriminator_bkg_train = y_frame_train[y_frame_train["truth"] == 0][
        "disriminator"
    ].values
    discriminator_signal = y_frame[y_frame["truth"] == 1]["disriminator"].values
    discriminator_signal_train = y_frame_train[y_frame_train["truth"] == 1][
        "disriminator"
    ].values
    weight_bkg = y_frame[y_frame["truth"] == 0]["weight"].values
    weight_bkg_train = y_frame_train[y_frame_train["truth"] == 0]["weight"].values
    weight_signal = y_frame[y_frame["truth"] == 1]["weight"].values
    weight_signal_train = y_frame_train[y_frame_train["truth"] == 1]["weight"].values

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.hist(
        discriminator_signal,
        density=True,
        bins=100,
        alpha=1.0,
        histtype="step",
        lw=2,
        label="Signal - test",
        weights=weight_signal,
    )
    plt.hist(
        discriminator_signal_train,
        density=True,
        bins=100,
        alpha=1.0,
        histtype="step",
        lw=2,
        label="Signal  - train",
        weights=weight_signal_train,
    )

    plt.hist(
        discriminator_bkg,
        density=True,
        bins=100,
        alpha=1.0,
        histtype="step",
        lw=2,
        label="Bkg - test",
        weights=weight_bkg,
    )
    plt.hist(
        discriminator_bkg_train,
        density=True,
        bins=100,
        alpha=1.0,
        histtype="step",
        lw=2,
        label="Bkg - train",
        weights=weight_bkg_train,
    )
    plt.yscale(scale)
    plt.xlim([0.0, 1.0])

    if scale == "log":
        plt.ylim([0.001, 1000.0])
    plt.xlim([0.0, 1.0])
    plt.legend(loc="upper right")
    plt.xlabel("BDT response")
    plt.ylabel("Events")
    hep.cms.label(
        data="True",
        label="",
        year=era,
        com="13.6",
        lumi=str(luminosity[era]),
    )
    plt.savefig(f"{plot_path}training/mydiscriminator_{scale}Y.pdf")
    plt.savefig(f"{plot_path}training/mydiscriminator_{scale}Y.png")
    plt.close()


def draw_correlation_matrix(
    signal_file_name, bkg_file_name, correlation_vars, plot_path, test_name
):
    signal_file = root.TFile(signal_file_name)
    tree_signal = signal_file.Get("tree_output")
    bkg_file = root.TFile(bkg_file_name)
    tree_bkg = bkg_file.Get("tree_output")
    n_corr = len(correlation_vars)
    h2_corr_sig = root.TH2F(
        "h2_corr_sig", "h2_corr_sig", n_corr, 0, n_corr, n_corr, 0, n_corr
    )
    h2_corr_bkg = root.TH2F(
        "h2_corr_bkg", "h2_corr_bkg", n_corr, 0, n_corr, n_corr, 0, n_corr
    )

    for idx1 in range(n_corr):
        for idx2 in range(n_corr):
            tree_signal.Draw(
                f"{correlation_vars[idx1][0]}:{correlation_vars[idx2][0]}>>temp_sig"
            )
            tree_bkg.Draw(
                f"{correlation_vars[idx1][0]}:{correlation_vars[idx2][0]}>>temp_bkg"
            )
            sig_hist = root.gDirectory.Get("temp_sig")
            h2_corr_sig.SetBinContent(
                idx1 + 1, idx2 + 1, sig_hist.GetCorrelationFactor()
            )
            bkg_hist = root.gDirectory.Get("temp_bkg")
            h2_corr_bkg.SetBinContent(
                idx1 + 1, idx2 + 1, bkg_hist.GetCorrelationFactor()
            )
            root.gDirectory.Delete("temp_sig")
            root.gDirectory.Delete("temp_bkg")
            h2_corr_sig.GetZaxis().SetRangeUser(-1.0, 1.0)
            h2_corr_bkg.GetZaxis().SetRangeUser(-1.0, 1.0)
            for idx in range(n_corr):
                h2_corr_sig.GetXaxis().SetBinLabel(idx + 1, correlation_vars[idx][2])
                h2_corr_sig.GetYaxis().SetBinLabel(idx + 1, correlation_vars[idx][2])
                h2_corr_bkg.GetXaxis().SetBinLabel(idx + 1, correlation_vars[idx][2])
                h2_corr_bkg.GetYaxis().SetBinLabel(idx + 1, correlation_vars[idx][2])

    h2_corr_sig.LabelsOption("v", "X")
    h2_corr_bkg.LabelsOption("v", "X")
    my_canvas = root.TCanvas("my_canvas", "my_canvas", 200, 10, 900, 800)
    my_canvas.SetHighLightColor(2)
    my_canvas.SetFillColor(0)
    my_canvas.SetBorderMode(0)
    my_canvas.SetBorderSize(2)
    my_canvas.SetLeftMargin(0.12)
    my_canvas.SetRightMargin(0.12)
    my_canvas.SetBottomMargin(0.12)
    my_canvas.SetTopMargin(0.12)
    my_canvas.SetFrameBorderMode(0)
    my_canvas.SetFrameBorderMode(0)

    stops = np.array([0.00, 0.34, 0.61, 0.84, 1.00])
    red = np.array([0.50, 0.50, 1.00, 1.00, 1.00])
    green = np.array([0.50, 1.00, 1.00, 0.60, 0.50])
    blue = np.array([1.00, 1.00, 0.50, 0.40, 0.50])
    root.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, 255)
    root.gStyle.SetNumberContours(255)

    h2_corr_sig.Draw("COLZTEXT")
    h2_corr_sig.SetTitle("")
    my_canvas.SaveAs(f"{plot_path}variables/{test_name}_correlation_matrix_sig.png")
    my_canvas.SaveAs(f"{plot_path}variables/{test_name}_correlation_matrix_bkg.png")
    my_canvas.SaveAs(f"{plot_path}variables/{test_name}_correlation_matrix_bkg.C")


def extrac_information_from_roc_curve(
    fpr, tpr, thr, test_name, signal_events, bkg_events
):
    significance = []
    effSignal = []
    effBkg = []
    thresholds = []
    ctr = 0
    f_roc = open(f"roc/{test_name}_roc.txt", "w")
    for i in range(len(fpr)):
        if fpr[i] > 1e-5 and tpr[i] > 1e-5:
            # print(
            # "thr = " + str(thr[i]) + ", fpr = " + str(fpr[i]) + ", tpr = " + str(tpr[i])
            # )
            f_roc.write(
                "thr = "
                + str(thr[i])
                + ", fpr = "
                + str(fpr[i])
                + ", tpr = "
                + str(tpr[i])
                + " \n"
            )
            significance.append(signal_events * tpr[i] / math.sqrt(fpr[i] * bkg_events))
            effSignal.append(tpr[i])
            effBkg.append(fpr[i])
            thresholds.append(thr[i])
            # print significance[ctr], ' ' , fpr[ctr], ' ', tpr[ctr]
            ctr = ctr + 1
    f_roc.close()
    return significance, effSignal, effBkg, thresholds

def draw_roc_curve(fpr, tpr, test_name, plot_path, era, AUC):
    f = plt.figure()
    # ax = f.add_subplot(111)
    lw = 2
    plt.plot(fpr, tpr, color="darkorange", lw=lw, label="ROC curve")
    plt.plot([0, 1], [0, 1], color="navy", lw=lw, linestyle="--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.ylabel("Signal Efficiency")
    plt.xlabel("Background Efficiency")
    # plt.axhline(y=0.9, color="black", linestyle="--")
    # plt.axhline(y=0.8, color="black")
    # plt.text(0.5,0.1,'WP80: bkg eff = %.4f'%WP80_effBkg, fontsize=12)
    # plt.text(0.5,0.2,'WP90: bkg eff = %.4f'%WP90_effBkg, fontsize=12)
    # plt.text(0.5,0.3,'WP90: S/sqrt(B) = %.2f'%WP90_significance, fontsize=12)
    # plt.text(0.5, 0.3, "AUC = %.4f" % AUC, hhhontsize=12)
    plt.text(0.5, 0.3, "AUC = %.4f" % AUC)
    # plt.title('Receiver operating characteristic example')
    # plt.legend(loc="lower right")

    hep.cms.label(
        data="True",
        label="",
        year=era,
        com="13.6",
        lumi=str(luminosity[era]),
    )
    plt.savefig(f"{plot_path}training/myroc_{test_name}.pdf")
    plt.savefig(f"{plot_path}training/myroc_{test_name}.png")


def plot_feature_importances(model, variables, test_name, plot_path):
    model.get_booster().feature_names = [row[2] for row in variables[:-3]]
    xgb.plot_importance(
        model, max_num_features=len(variables) - 3, xlabel="F score (weight)"
    )
    plt.savefig(
        f"{plot_path}training/myImportances_Fscore_{test_name}.pdf",
        bbox_inches="tight",
    )
    plt.savefig(
        f"{plot_path}training/myImportances_Fscore_{test_name}.png",
        bbox_inches="tight",
    )

def plot_xgb_tree(model, variables, test_name, plot_path):
    model.get_booster().feature_names = [row[1] for row in variables[:-3]]
    xgb.plot_tree(model)
    fig = plt.gcf()
    fig.set_size_inches(150, 100)
    # fig.set_size_inches(500, 50)
    plt.draw()
    plt.savefig(f"{plot_path}training/myTree_{test_name}.pdf")
    plt.savefig(f"{plot_path}training/myTree_{test_name}.png")


def save_model(model, test_name, use_bsConstrain):
    # Pickle dictionary using protocol 0.
    if use_bsConstrain:
        test_name = f"{test_name}_bsC"
    output = open("models/model_" + test_name + ".pkl", "wb")
    pickle.dump(model, output)
    output.close()
    model.get_booster().dump_model(f"models/model_{test_name}.txt")
    model.get_booster().save_model(f"models/model_{test_name}.xgb")

def plot_loss(test_loss, train_loss, test_name, plot_path, era):
    plt.style.use(hep.style.CMS)

    f = plt.figure()
    plt.plot(train_loss, label="Train")
    plt.plot(test_loss, label="Test")
    plt.xlabel("Boosting round")
    plt.ylabel("Log loss")
    plt.legend()
    #hep.cms.label("Preliminary", data=False, lumi=170.905, com=13.6)
    hep.cms.label(
        data="False",
        label="",
        year=era,
        com="13.6",
        lumi=str(luminosity[era]),
    )
    plt.tight_layout()
    plt.show()

    os.makedirs(f"{plot_path}training/", exist_ok=True)
    plt.savefig(f"{plot_path}training/loss_{test_name}.pdf")
    plt.savefig(f"{plot_path}training/loss_{test_name}.png")

'''
if __name__ == "__main__":
    import sys
    HIGGS_CHANNEL = sys.argv[1]
    ERA = sys.argv[2]
    MODEL_ERA = sys.argv[3]
    TUPLE_TYPE = sys.argv[4]
    BKG_SUBSET = sys.argv[5]
    SIG_SUBSET = sys.argv[6]

    DO_STANDARDIZATION = True
    USE_BSCONSTRAIN = True 

    variables = xgb_utils.get_variables(HIGGS_CHANNEL, USE_BSCONSTRAIN)

    xgb_utils.append_BDT_score(
        TUPLE_TYPE,
        HIGGS_CHANNEL,
        ERA,
        MODEL_ERA,
        SIG_SUBSET,
        BKG_SUBSET,
        variables[:-3],
        mean_map,
        std_map,
        DO_STANDARDIZATION,
        USE_BSCONSTRAIN,
    )'''