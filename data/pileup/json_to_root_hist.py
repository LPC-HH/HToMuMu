import correctionlib
import ROOT as rt

files = [
    "/cvmfs/cms-griddata.cern.ch/cat/metadata/LUM/Run3-22CDSep23-Summer22-NanoAODv12/latest/puWeights",
    "/cvmfs/cms-griddata.cern.ch/cat/metadata/LUM/Run3-22EFGSep23-Summer22EE-NanoAODv12/latest/puWeights",
    "/cvmfs/cms-griddata.cern.ch/cat/metadata/LUM/Run3-23CSep23-Summer23-NanoAODv12/latest/puWeights",
    "/cvmfs/cms-griddata.cern.ch/cat/metadata/LUM/Run3-23DSep23-Summer23BPix-NanoAODv12/latest/puWeights",
    "/cvmfs/cms-griddata.cern.ch/cat/metadata/LUM/Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15/latest/puWeights_BCDEFGHI",
    "/cvmfs/cms-griddata.cern.ch/cat/metadata/LUM/Run3-25Prompt-Summer24-NanoAODv15/latest/puWeights_2025pp_Golden_Summer24_25ns_69200ub",
    "/cvmfs/cms-griddata.cern.ch/cat/metadata/LUM/Run3-25Prompt-Summer24-NanoAODv15/latest/puWeights_2025pp_Golden_Summer24_25ns_69200ub",
]

eras = ["Summer22", "Summer22EE", "Summer23", "Summer23BPix", "Summer24", "Summer25", "Summer26"]
for name, era in zip(files, eras):
    ceval = correctionlib.CorrectionSet.from_file(name + ".json.gz")
    outFile = rt.TFile("PileupReweight_" + era + ".root", "RECREATE")

    for corr in ceval.values():
        key = corr.name
        print(f"Correction {corr.name} has {len(corr.inputs)} inputs")
        for ix in corr.inputs:
            print(f"   Input {ix.name} ({ix.type}): {ix.description}")
            print(len(ix.description))
    print(key)
    for weight in ["nominal", "up", "down"]:
        hist = rt.TH1F(
            "npu_{}".format(weight), "npu_{}".format(weight), 100, -0.5, 99.5
        )
        for i in range(hist.GetNbinsX()):
            hist.SetBinContent(
                i + 1, ceval[key].evaluate(hist.GetBinCenter(i + 1), weight)
            )

        outFile.WriteTObject(hist, "npu_{}".format(weight), "WriteDelete")

    outFile.Close()
