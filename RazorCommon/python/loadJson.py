import FWCore.PythonUtilities.LumiList as LumiList
import FWCore.ParameterSet.Types as CfgTypes
import FWCore.ParameterSet.Config as cms

# setup process
process = cms.Process("FWLitePlots")
process.inputs = cms.PSet (
    lumisToProcess = CfgTypes.untracked(CfgTypes.VLuminosityBlockRange())
)

# get JSON file correctly parced
#####NEED TO FIX JSONfile
JSONfile = '/uscms_data/d3/esledge/CMSSW_15_0_9/src/HToMuMu/RazorCommon/data/Run3/Cert_Collisions2022_355100_362760_Golden.json'
myList = LumiList.LumiList (filename = JSONfile).getCMSSWString().split(',')

process.inputs.lumisToProcess.extend(myList)
