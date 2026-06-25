#!/usr/bin/env python3
import correctionlib

json_path = "./jet_jerc.json.gz"
cset = correctionlib.CorrectionSet.from_file(json_path)

eta = 1.2
pt = 50.0

corr_names = [
    "Summer23Prompt23_V4_MC_Regrouped_RelativeBal_AK4PFPuppi",
    "Summer23Prompt23_V4_MC_Regrouped_RelativeSample_2023_AK4PFPuppi",
]

for corr_name in corr_names:
    print("\n==============================")
    print("Correction name:", corr_name)

    corr = cset[corr_name]

    print("Inputs:")
    for x in corr.inputs:
        print(" ", x.name, x.type)

    print("Output:")
    print(" ", corr.output.name, corr.output.type)

    unc = corr.evaluate(eta, pt)

    print("raw uncertainty =", unc)
    print("up factor       =", 1.0 + unc)
    print("down factor     =", 1.0 - unc)
    print("pt up           =", pt * (1.0 + unc))
    print("pt down         =", pt * (1.0 - unc))

    if "RelativeSample_2023" in corr_name:
        print(
            "t_Jet_pt_CMS_scale_j_RelativeSample_2023_down =",
            pt * (1.0 - unc)
        )
