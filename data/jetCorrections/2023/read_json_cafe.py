#!/usr/bin/env python3

import awkward as ak
import correctionlib

json_path = "./jet_jerc.json.gz"
cset = correctionlib.CorrectionSet.from_file(json_path)

corr_names = [
    "Summer23Prompt23_V4_MC_Regrouped_RelativeBal_AK4PFPuppi",
    "Summer23Prompt23_V4_MC_Regrouped_RelativeSample_2023_AK4PFPuppi",
    "Summer23Prompt23_V4_MC_Regrouped_RelativeBal_AK4PFPuppi"
]

Jet_eta = ak.Array([[-3.517578, 0.517578, 0.517578, 3.517578]])
Jet_pt  = ak.Array([[25.0, 25.0, 25.0, 25.0]])


variations = {}
uncertantie = {}

for corr_name in corr_names:
    corr = cset[corr_name]
    print(corr)

    # Extract nice systematic name:
    # Summer23Prompt23_V4_MC_Regrouped_RelativeSample_2023_AK4PFPuppi
    # -> RelativeSample_2023
    #source_name = corr_name.split("_Regrouped_")[1].replace("_AK4PFPuppi", "")
    source_name = corr_name
    eta_flat = ak.to_numpy(ak.flatten(Jet_eta))
    pt_flat  = ak.to_numpy(ak.flatten(Jet_pt))

    unc_flat = corr.evaluate(eta_flat, pt_flat)

    # Restore jagged event/jet structure
    unc = ak.unflatten(unc_flat, ak.num(Jet_pt))

    variations[f"t_Jet_pt_CMS_scale_j_{source_name}_up"] = Jet_pt * (1.0 + unc)
    variations[f"t_Jet_pt_CMS_scale_j_{source_name}_down"] = Jet_pt * (1.0 - unc)
    uncertantie[f"CMS_scale_j_{source_name}"] = unc

for name, value in variations.items():
    print(name, "=", ak.to_list(value))
for name, value in uncertantie.items():
    print(name, "=", ak.to_list(value))
