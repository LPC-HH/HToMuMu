#!/usr/bin/env python
# coding: utf-8
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_curve, roc_auc_score
import xgb_utils
import numpy as np
import pandas as pd
import math
import pickle as pickle
import os
import shutil
import uproot
import sys
# import optuna
# import optuna.visualization as vis
import matplotlib.pyplot as plt
import mplhep as hep
# import plotly.io as pio
# from plotly.io import show

if len(sys.argv) not in [7, 9]:
    print(
        "[ERROR] python3 train.py <Channel_under_study> <era> "
        "<ifRetrain T/F> <ifOptimize T/F> <doSystematics T/F> "
        "[bkg_subset sig_subset]"
    )
    exit()

channel_US, era = sys.argv[1], sys.argv[2]
ifRetrain = True if sys.argv[3] == "T" else False
ifOptimize = True if sys.argv[4] == "T" else False
doSystematics = True if sys.argv[5] == "T" else False
useRecategorization = True if sys.argv[6] == "T" else False
background_subset = sys.argv[6] if len(sys.argv) == 8 else "Full"
signal_subset = sys.argv[7] if len(sys.argv) == 8 else "NottH"


print("Channel under study: ", channel_US)
print("Era: ", era)
print("Retrain: ", ifRetrain)
print("Optimize: ", ifOptimize)
print("Do systematics: ",doSystematics)
print("Background subset: ", background_subset)
print("Signal subset: ", signal_subset)
print("Using recatagorization? ", useRecategorization) 


DRAW_CORRELATIONS = False
DO_STANDARDIZATION = True
USE_WEIGHT = False
USE_WEIGHT_MASS_RES = True
APPEND_VARIABLES = True
USE_BSCONSTRAIN = True 
PLOT_LOSS = True
SEED = 7
TEST_SIZE = 0.4
SAMPLE_SIZE = 1.0
SIGNAL_REGION = (121., 129.)
TRAIN_REGION = (115.,135.)

variables = xgb_utils.get_variables(channel_US, USE_BSCONSTRAIN)
print("number of variables", len(variables) - 3)


category_var = ""
file_append = ""
root_append = ""
if useRecategorization:
    plot_path = f"../../plots/xgboost/{channel_US}reCat/B{background_subset}_S{signal_subset}/"
    data_directory = f"../../root_io/skim/{channel_US}reCat/"
    category_var = "_categoryBDT"
    file_append = "reCat"
    root_append = "_categorized"
else:
    plot_path = f"../../plots/xgboost/{channel_US}/B{background_subset}_S{signal_subset}/"
    data_directory = f"../../root_io/skim/{channel_US}/"
    category_var = "_category"

test_name = f"{channel_US}{file_append}_{era}_B{background_subset}_S{signal_subset}"

signal_file_name = f"{data_directory}signal_{era}_skim_{signal_subset}.root"
bkg_file_name = f"{data_directory}background_{era}_skim_{background_subset}.root"

os.makedirs(plot_path, exist_ok=True)
for subdir in ["training", "results", "scores", "variables"]:
    os.makedirs(os.path.join(plot_path, subdir), exist_ok=True)
    shutil.copy("../index.php", os.path.join(plot_path, subdir))
os.makedirs("models", exist_ok=True)
os.makedirs("roc", exist_ok=True)

##Getting ROOT files into pandas
print("[INFO]: Creating data frames")
print(f"[INFO] Signal File Name: {signal_file_name}")
print(f"[INFO] Background File Name: {bkg_file_name}")

with uproot.open(signal_file_name) as file:
    df_signal = pd.DataFrame(
        file["tree_output"].arrays([var[0] for var in variables], library="np"),
    )
with uproot.open(bkg_file_name) as file:
    df_bkg = pd.DataFrame(
        file["tree_output"].arrays([var[0] for var in variables], library="np"),
    )

# NaN out dijet/leading-jet variables that lib/CreateTuple.h could only pad
# (n_jet < 2 / n_jet < 1) so the BDT does not read the 0/-1 padding as a
# physical jet system -- relevant now that the categorization BDT promotes
# single-jet events into the VBF channel.
xgb_utils.mask_undefined_jet_features(df_signal)
xgb_utils.mask_undefined_jet_features(df_bkg)

print("[INFO]: Data frames created successfully")

if USE_BSCONSTRAIN:
    mass_var_name = "diMuon_bsConstrainedMass"
else:
    mass_var_name = "diMuon_mass"

bkg_events = df_bkg["weight"][
    (df_bkg[mass_var_name] > SIGNAL_REGION[0])
    & (df_bkg[mass_var_name] < SIGNAL_REGION[1])
].sum()
signal_events = df_signal["weight"][
    (df_signal[mass_var_name] > SIGNAL_REGION[0])
    & (df_signal[mass_var_name] < SIGNAL_REGION[1])
].sum()

####  weight Normalization
signal_weight_sum = df_signal["weight"].sum()
bkg_weight_sum = df_bkg["weight"].sum()
df_signal["weight"] = df_signal["weight"] * (bkg_weight_sum / signal_weight_sum)

s_over_sqrt_b = signal_events / math.sqrt(bkg_events)
print(
    f"[INFO]: S = {signal_events:.3f}; B = {bkg_events:.3f}; S/sqrt(B) = {s_over_sqrt_b:.3f}"
)
print(f"[INFO]: Signal sample size: {len(df_signal.values)}")
print(f"[INFO]: Bkg sample size: {len(df_bkg.values)}")

x = np.concatenate([df_bkg.values, df_signal.values])
y = np.concatenate([np.zeros(len(df_bkg)), np.ones(len(df_signal))])

### Apply dimuon mass cut
print("len y pred cut:", len(y))
y = y[(x[:, -3] > TRAIN_REGION[0]) & (x[:, -3] < TRAIN_REGION[1])]
x = x[(x[:, -3] > TRAIN_REGION[0]) & (x[:, -3] < TRAIN_REGION[1])]
print("len y post cut:", len(y))

if DRAW_CORRELATIONS:
    xgb_utils.draw_correlation_matrix(
        signal_file_name, bkg_file_name, variables[:-2], plot_path, test_name
    )

# split data into train and test sets
SEED = 7
TEST_SIZE = 0.4
SAMPLE_SIZE = 1.0
x_train_p, x_test_p, y_train, y_test = train_test_split(
    x,
    y,
    train_size=SAMPLE_SIZE * (1 - TEST_SIZE),
    test_size=SAMPLE_SIZE * TEST_SIZE,
    random_state=SEED,
)

x_train = x_train_p[:, :-3]
x_test = x_test_p[:, :-3]
sample_weights_train = x_train_p[:, -1]
sample_weights_test = x_test_p[:, -1]

# +/-inf -> NaN; NaN (missing jet features and any accidental div-by-zero) is
# kept and handled natively by XGBoost's missing-value mechanism.
x_train[np.isinf(x_train)] = np.nan
x_test[np.isinf(x_test)] = np.nan

print("x_train:", x_train)
mean_map = {}
std_map = {}
if DO_STANDARDIZATION:
    for i, var in enumerate(variables[:-3]):
        print("standarizing : ", var[0])
        print("Iterator : ", i)

        # NaN entries (missing jet features) are excluded from the mean/std and
        # left as NaN for XGBoost's native missing-value handling; every finite
        # value is z-scored.
        mask_train = np.isfinite(x_train[:, i])
        mask_test = np.isfinite(x_test[:, i])
        mean_map[var[0]] = x_train[mask_train, i].mean()
        std_map[var[0]] = x_train[mask_train, i].std()
        print("[Info]: Train Sample Mean: ", mean_map[var[0]])
        print("[Info]: Train Sample std: ", std_map[var[0]])
        x_train[mask_train, i] = (x_train[mask_train, i] - mean_map[var[0]]) / std_map[
            var[0]
        ]
        x_test[mask_test, i] = (x_test[mask_test, i] - mean_map[var[0]]) / std_map[
            var[0]
        ]
print("x_train standaried:", x_train)

w_train = np.absolute(sample_weights_train) / np.array(x_train_p[:, -2])
w_test = np.absolute(sample_weights_test) / np.array(x_test_p[:, -2])

if ifRetrain:    
    def objective(trial):
    
        params = {
            "max_depth": trial.suggest_int("max_depth", 2, 5),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "n_estimators": 2000,
            "device": "cuda",
    
            "min_child_weight": trial.suggest_float("min_child_weight", 1.0, 20.0, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
    
            "reg_lambda": trial.suggest_float("reg_lambda", 0.1, 10.0, log=True),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-4, 1.0, log=True),
    
            "objective": "binary:logistic",
            "eval_metric": "logloss",
            "n_jobs": 4,
            "verbosity": 0,
            "early_stopping_rounds": 50,
            "missing": np.nan,
        }
    
        model = xgb.XGBClassifier(**params)
    
        model.fit(
            x_train,
            y_train,
            sample_weight=w_train,
            eval_set=[(x_train, y_train), (x_test, y_test)],
            sample_weight_eval_set=[w_train, w_test],
            verbose=False,
        )
    
        y_pred = model.predict_proba(x_test)[:, 1]
        
        #Z = compute_significance(y_test, y_pred, w_test)
    
        auc = roc_auc_score(
            y_test,
            y_pred,
            sample_weight=w_test,
        )
    
        return auc
    
    nTrials = 1000
    if(ifOptimize):
        optimization_plot_path = "optunaPlots/" + channel_US + "/"
        os.makedirs(optimization_plot_path, exist_ok=True)
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=nTrials)
    
        print("Best AUC:", study.best_value)
        print("Best parameters:")
        print(study.best_params)
    
        fig = vis.plot_optimization_history(study)
        fig.write_html(optimization_plot_path + "optimization_history.html")
        #fig.show()
    
        fig = vis.plot_param_importances(study)
        fig.write_html(optimization_plot_path + "param_importance.html")
        #fig.show()
    
        fig = vis.plot_slice(
        study,
        params=[
            "max_depth",
            "learning_rate",
            "min_child_weight",
            "subsample",
            "colsample_bytree",
            "reg_lambda",
            "reg_alpha",
        ],
        )
    
        fig.write_html(optimization_plot_path + "optuna_slice.html")
        best_params = study.best_params
        model = xgb.XGBClassifier(
            **best_params,
            n_estimators=2000,
            verbosity=2,
            n_jobs=4,
            eval_metric=["logloss", "auc"],
            early_stopping_rounds=50,
            missing=np.nan,
        )

        model.fit(
            x_train,
            y_train,
            sample_weight=w_train,
            eval_set=[(x_train, y_train), (x_test, y_test)],
            sample_weight_eval_set=[w_train, w_test],
        )
    
        results = model.evals_result()
    
        train_loss = results["validation_0"]["logloss"]
        test_loss  = results["validation_1"]["logloss"]
    
        xgb_utils.plot_loss(test_loss, train_loss, test_name, optimization_plot_path, era)
        
    # fit model no training data
    if(ifOptimize):
        model = xgb.XGBClassifier(
            **best_params,
            n_estimators=2000,
            verbosity=2,
            n_jobs=4,
            eval_metric=["logloss", "auc"],
            early_stopping_rounds=50,
            missing=np.nan,
        )

    else:
        '''if(channel_US == 'ggH'):
            print("USING GGH OPTIMIZED BDT PARAMETERS")
            opted_params = {'max_depth': 5, 'learning_rate': 0.17065960988185175, 'min_child_weight': 1.258974431208238,
                            'subsample': 0.9799252299722975, 'colsample_bytree': 0.9857090292326347, 
                            'reg_lambda': 0.17418443431820596, 'reg_alpha': 0.03970459451078197}
        else:
            print("USING VBF OPTIMIZED BDT PARAMETERS")
            opted_params = {'max_depth': 5, 'learning_rate': 0.019748925259387092, 'min_child_weight': 1.936502069113041,
                        'subsample': 0.8625503812499821, 'colsample_bytree': 0.822627756256343, 'reg_lambda': 1.45659504748671,
                        'reg_alpha': 0.010136874339606281}
        model = xgb.XGBClassifier(
            **opted_params,
            n_estimators=2000,
            verbosity=2,
            n_jobs=4,
            eval_metric=["logloss", "auc"],
            early_stopping_rounds=50
        )'''

        '''model = xgb.XGBClassifier(
            max_depth=3,
            learning_rate=0.1,
            n_estimators=400,
            verbosity=2,
            n_jobs=4,
            reg_lambda=1.0,
            device='cuda',
        )'''

        model = xgb.XGBClassifier(
            max_depth=3,
            learning_rate=0.1,
            n_estimators=400,
            verbosity=2,
            n_jobs=4,
            reg_lambda=1.0,
            eval_metric=["logloss", "auc"],
            device='cuda',
            missing=np.nan,
        )

    print("weights: ", sample_weights_train)
    print("abs(weights): ", np.absolute(sample_weights_train[y_train == 1]))
    print("abs(weights) mean: ", sample_weights_train[y_train == 1].mean())
    print("relative_diMuon_mass_error: ", x_test_p[:, -2])
    print("new error : ", np.absolute(sample_weights_train) / np.array(x_train_p[:, -2]))

    if not USE_WEIGHT and not USE_WEIGHT_MASS_RES:
        print("[Info]: Training without weights")
        model.fit(x_train, y_train)
    if USE_WEIGHT:
        print("[Info]: Training with regular  weights")
        model.fit(x_train, y_train, sample_weight=np.absolute(sample_weights_train))
    if USE_WEIGHT_MASS_RES:
        print("[Info]: Training with mass_res weights")
        model.fit(
            x_train,
            y_train,
            sample_weight=w_train,
            eval_set=[(x_train, y_train), (x_test, y_test)],
            sample_weight_eval_set=[w_train, w_test],
        )

    y_pred = model.predict_proba(x_test)[:, 1]
    y_pred_train = model.predict_proba(x_train)[:, 1]

    print("y_pred:", y_pred)
    print("y_test:", y_test)
    print("y_pred_train:", y_pred_train)
    predictions = [round(value) for value in y_pred]
    # evaluate predictions
    accuracy = accuracy_score(y_test, predictions)
    print("Accuracy: %.2f%%" % (accuracy * 100.0))

    AUC = roc_auc_score(y_test, y_pred)
    AUC_weighted = roc_auc_score(y_test, y_pred, sample_weight=w_test)
    print("AUC: " + str(AUC))
    print("Weighted AUC: " + str(AUC_weighted))
    diMuon_mass_test = x_test_p[:, -3]
    print(
        "diMuon_mass: ",
        diMuon_mass_test[(diMuon_mass_test < 130) & (diMuon_mass_test > 120)],
    )

    ## Go back to the normal signal weight
    sample_weights_test[y_test == 1] = sample_weights_test[y_test == 1] * (
        signal_weight_sum / bkg_weight_sum
    )
    sample_weights_train[y_train == 1] = sample_weights_train[y_train == 1] * (
        signal_weight_sum / bkg_weight_sum
    )

    signal_region_test_cuts = (x_test_p[:, -3] > SIGNAL_REGION[0]) & (
        x_test_p[:, -3] < SIGNAL_REGION[1]
    )
    fpr, tpr, thr = roc_curve(
        y_test[signal_region_test_cuts],
        y_pred[signal_region_test_cuts],
        sample_weight=sample_weights_test[signal_region_test_cuts],
    )

    significance, effSignal, effBkg, thresholds = (
        xgb_utils.extrac_information_from_roc_curve(
            fpr, tpr, thr, test_name, signal_events, bkg_events
        )
    )

    idx_max_significance = np.argmax(np.array(significance))
    print(
        f"[INFO]: S = {signal_events:.3f}; B = {bkg_events:.3f}; S/sqrt(B) = {signal_events / math.sqrt(bkg_events):.3f}"
    )
    print(f"[INFO]: Max: Significance = {significance[idx_max_significance]}")
    print(f"[INFO]: Max: Threshold = {thresholds[idx_max_significance]}")
    print(f"[INFO]: Max: Signal Efficiency = {effSignal[idx_max_significance]}")
    print(f"[INFO]: Max: Background Efficiency ={effBkg[idx_max_significance]}")

    for wp in [0.90, 0.80]:
        idx = np.argmin(np.abs(np.array(effSignal) - wp))
        s_wp = signal_events * wp
        b_wp = bkg_events * effBkg[idx]
        print(f"[INFO]: WP{int(wp*100)}: Significance = {significance[idx]}")
        print(f"[INFO]: WP{int(wp*100)}: Threshold = {thresholds[idx]}")
        print(f"[INFO]: WP{int(wp*100)}: Signal Efficiency = {effSignal[idx]}")
        print(f"[INFO]: WP{int(wp*100)}: Background Efficiency ={effBkg[idx]}")
        print(
            f"[INFO]: WP{int(wp*100)}: S = {signal_events:.3f}; B = {bkg_events:.3f}; S/sqrt(B) = {signal_events / math.sqrt(bkg_events):.3f}"
        )

    xgb_utils.plot_discriminator(
        y_test,
        y_pred,
        y_train,
        y_pred_train,
        sample_weights_test,
        sample_weights_train,
        era,
        plot_path,
        scale="log",
    )
    xgb_utils.plot_discriminator(
        y_test,
        y_pred,
        y_train,
        y_pred_train,
        sample_weights_test,
        sample_weights_train,
        era,
        plot_path,
        scale="linear",
    )

    xgb_utils.plot_BDT_sculpting(
        y_pred, 
        y_pred_train,
        y_test,
        y_train,
        x_test_p,
        x_train_p,
        channel_US,
        era,
        plot_path,
        bdt_divisions=6
    )

    results = model.evals_result()

    train_loss = results["validation_0"]["logloss"]
    test_loss  = results["validation_1"]["logloss"]

    xgb_utils.draw_roc_curve(fpr, tpr, test_name, plot_path, era, AUC)
    xgb_utils.draw_roc_curve(fpr, tpr, "weighted_" + test_name, plot_path, era, AUC_weighted)
    xgb_utils.save_model(model, test_name, USE_BSCONSTRAIN)
    xgb_utils.plot_feature_importances(model, variables, test_name, plot_path)
    xgb_utils.plot_xgb_tree(model, variables, test_name, plot_path)
    if PLOT_LOSS:
        xgb_utils.plot_loss(test_loss, train_loss, test_name, plot_path, era)






if not APPEND_VARIABLES:
    print("[INFO]: BDT score was not added to the trees")
else: 
    print("[INFO]: Adding BDT score to the nominal tuples")
    tuples = ["Data", "DY", "EWK", "TT", "DiBoson", "ggH", "VBF"]
    # tuples = ["Data","ggH", "VBF"]
    for file_type in tuples:
        xgb_utils.append_BDT_score(
            file_type,
            channel_US,
            era,
            "Combined",
            signal_subset,
            background_subset,
            variables[:-3],
            mean_map,
            std_map,
            DO_STANDARDIZATION,
            USE_BSCONSTRAIN,
            useRecategorization,
        )
        '''xgb_utils.append_BDT_score(
            file_type,
            channel_US,
            "2024",
            "Combined",
            signal_subset,
            background_subset,
            variables[:-3],
            mean_map,
            std_map,
            DO_STANDARDIZATION,
            USE_BSCONSTRAIN,
            )
        
        xgb_utils.append_BDT_score(
            file_type,
            channel_US,
            "2022",
            "Combined",
            signal_subset,
            background_subset,
            variables[:-3],
            mean_map,
            std_map,
            DO_STANDARDIZATION,
            USE_BSCONSTRAIN,
        )

        xgb_utils.append_BDT_score(
            file_type,
            channel_US,
            "2022EE",
            "Combined",
            signal_subset,
            background_subset,
            variables[:-3],
            mean_map,
            std_map,
            DO_STANDARDIZATION,
            USE_BSCONSTRAIN,
        )

        xgb_utils.append_BDT_score(
            file_type,
            channel_US,
            "2023",
            "Combined",
            signal_subset,
            background_subset,
            variables[:-3],
            mean_map,
            std_map,
            DO_STANDARDIZATION,
            USE_BSCONSTRAIN,
        )

        xgb_utils.append_BDT_score(
            file_type,
            channel_US,
            "2023BPix",
            "Combined",
            signal_subset,
            background_subset,
            variables[:-3],
            mean_map,
            std_map,
            DO_STANDARDIZATION,
            USE_BSCONSTRAIN,
        )
        
        xgb_utils.append_BDT_score(
            file_type,
            channel_US,
            "2024",
            "Combined",
            signal_subset,
            background_subset,
            variables[:-3],
            mean_map,
            std_map,
            DO_STANDARDIZATION,
            USE_BSCONSTRAIN,
        )'''

if doSystematics:
    print("[INFO]: Addeding BDT score to the systematic tuples")
    for tuple_type in ["ggH", "VBF"]:
        xgb_utils.append_BDT_score_to_sys(
            tuple_type,
            channel_US,
            era,
            "Combined",
            signal_subset,
            background_subset,
            variables[:-3],
            mean_map,
            std_map,
            DO_STANDARDIZATION,
            USE_BSCONSTRAIN,
        )
