#!/usr/bin/env python

import sys
import matplotlib
import os

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

# import math
import pickle as pickle
import ROOT as root
import uproot as uproot

root.gROOT.Reset()

use_skim = False
if "--skim" in sys.argv:
    sys.argv.remove("--skim")
    print(" > Appending BDT to skim file instead of tuple!")
    use_skim = True

if len(sys.argv) < 4:
    print(
        "Arguments missing: Channel_under_study, era, file_type,\
          background_subset, signal_subset"
    )
    exit()
channel_US = sys.argv[1]
era = sys.argv[2]
model_era = sys.argv[3]
file_type = sys.argv[4]
if len(sys.argv) == 5:
    background_subset = "Full"
    signal_subset = "NottH"
    print("Using default subsets:", background_subset, signal_subset)
elif len(sys.argv) == 7:
    background_subset = sys.argv[5]
    signal_subset = sys.argv[6]
else:
    print("Include subset of background AND signal only.")
    exit()

use_bsConstrain = True
print("Channel under study: ", channel_US)
print("Era: ", era)
print("Background subset: ", background_subset)
print("Signal subset: ", signal_subset)
print("Type of file: ", file_type)

subset_title = "B" + background_subset + "_S" + signal_subset
tuple_subset = ""
if file_type == "background" or file_type == "bkg":
    tuple_subset = background_subset
elif file_type == "signal":
    tuple_subset = signal_subset

if not use_skim:
    tuple_path = "../../root_io/tuples/"
    tuple_name = file_type + "_" + era + "_tuples.root"
    BDT_path = tuple_path + "BDT_score/" + channel_US + "/" + subset_title + "/"
    # BDT_name = file_type + "_" + era + "_tuples.root"
    BDT_name = file_type + "_" + era + "_" + subset_title + ".root"
else:
    tuple_path = "../../root_io/skim/" + channel_US + "/"
    tuple_name = file_type + "_" + era + "_skim_" + tuple_subset + ".root"
    # BDT_path = tuple_path + "BDT_score/"
    BDT_path = "../../root_io/skim/BDT_score/" + channel_US + "/"
    BDT_name = file_type + "_" + era + "_skim_" + subset_title + ".root"
    #if channel_US == "VBF":
    #    tuple_path += "merged/"

os.system("mkdir -p " + BDT_path)
print("File name: ", BDT_name)
os.system("cp " + tuple_path + tuple_name + " " + BDT_path + BDT_name)

FileName = BDT_path + BDT_name
File = root.TFile(FileName, "update")
Tree = File.Get("tree_output")

#model_name = channel_US + "_" + era + "_" + subset_title
model_name = channel_US + "_" + model_era + "_" + subset_title
model_file = "./models/model_" + model_name + ".pkl"

if use_bsConstrain:
    model_file = "./models/model_" + model_name + "_bsC.pkl"

variables = [
    ["diMuon_rapidity", "diMuon_rapidity", r"$y_{\mu\mu}$"],
    ["diMuon_pt", "diMuon_pt", r"$p_T^{\mu\mu}$ [GeV]"],
    ["mu1_pt_mass_ratio", "mu1_pt_mass_ratio", r"$p_T^{\mu 1}/m_{\mu\mu}$"],
    ["mu2_pt_mass_ratio", "mu2_pt_mass_ratio", r"$p_T^{\mu 2}/m_{\mu\mu}$"],
    ["mu1_eta", "mu1_eta", r"$\eta_{\mu 1}$"],
    ["mu2_eta", "mu2_eta", r"$\eta_{\mu 2}$"],
    ["phi_CS", "phi_CS", r"$\phi_{CS}$"],
    ["cos_theta_CS", "cos_theta_CS", r"$cos(\theta_{CS})$"],
    # # Jet variables
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
if channel_US == "VBF":
    variables += [
        # VBF sspecific variables
        ["pt_balance", "pt_balance", r"$R(p_T)$"],
        ["pt_centrality", "pt_centrality", r"$p_{T}-centrality$"],
        ["n_SoftJet_pt2", "n_SoftJet_pt2", r"$N_{2}^{soft}$"],
        ["HT", "HT", r"$H_{T}^{2}(soft)$"],
    ]


# print(len(variables))
# my_variables = []
# for var in variables:
#     print(var[0])
#     my_variables.append(var[0])

with uproot.open(FileName) as file:
    df = pd.DataFrame(
        file["tree_output"].arrays([row[0] for row in variables], library="np"),
        # flatten=False,
    )

# getting a numpy array from two pandas data frames
x_test = df.values
# creating numpy array for target variables
y_test = np.zeros(len(df))


############################
# get model from file
############################
with open(model_file, "rb") as pkl_file:
    model = pickle.load(pkl_file)


# make predictions for test data
y_pred = model.predict_proba(x_test)[:, 1]
print("y_pred", y_pred)
predictions = [round(value) for value in y_pred]

# print y_pred
##########################################################
# make histogram of discriminator value for signal and bkg
##########################################################
y_frame = pd.DataFrame({"truth": y_test, "disc": y_pred})
print("y_frame", y_frame)
disc = y_frame[y_frame["truth"] == 0]["disc"].values
# disc    = y_frame[y_frame['truth'] == 1]['disc'].values
plt.figure()
plt.hist(disc, bins=50, alpha=0.3)
plt.savefig("mydiscriminator_" + era + ".png")
# print("disc_bkg: ", disc)
# print y_pred

#############################################
##Creating a new TTree with the discriminator
#############################################

nEntries = Tree.GetEntries()
print("nEntries = ", nEntries)
_disc_var_name = "BDT_" + channel_US

root.gROOT.ProcessLine("struct MyStruct{float disc;};")

from ROOT import MyStruct

# Create branches in the tree
my_s = MyStruct()
print(my_s)
print(root.addressof(my_s))
print(root.addressof(my_s, "disc"))
root.addressof(my_s, "disc")
bpt = Tree.Branch(_disc_var_name, root.addressof(my_s, "disc"), _disc_var_name + "/F")

for i in range(nEntries):
    Tree.GetEntry(i)
    if i % 10000 == 0:
        print("Processing event nr. %i of %i" % (i, nEntries))
    my_s.disc = disc[i]
    bpt.Fill()

# Tree.Print()
Tree.GetCurrentFile().Write()
Tree.GetCurrentFile().Close()
