#include <iostream>
#include <algorithm>
#include <chrono>
#include <TFile.h>
#include <TSystem.h>
#include <TTree.h>
#include <TKey.h>

#include "DataFormats/FWLite/interface/Event.h"
#include "DataFormats/FWLite/interface/Handle.h"
#include "FWCore/FWLite/interface/FWLiteEnabler.h"

#include "DataFormats/FWLite/interface/Run.h"
#include "DataFormats/FWLite/interface/LuminosityBlock.h"
#include "DataFormats/Luminosity/interface/LumiSummary.h"
#include "PhysicsTools/FWLite/interface/CommandLineParser.h"

#include "FWCore/ParameterSet/interface/ProcessDesc.h"
#include "FWCore/PythonParameterSet/interface/PyBind11ProcessDesc.h"
#include "DataFormats/Provenance/interface/LuminosityBlockRange.h"

std::string RUN_BRANCH = "t_run";
std::string LUMI_BRANCH = "t_luminosityBlock";
std::string EVENTS_TREE = "tree";

bool jsonContainsEvent (const std::vector< edm::LuminosityBlockRange > &jsonVec, unsigned int run, unsigned int lumi)
{
  // if the jsonVec is empty, then no JSON file was provided so all
  // events should pass
  if (jsonVec.empty()) return true;
  for (std::vector<edm::LuminosityBlockRange>::const_iterator lumisBegin = jsonVec.begin(),
                                                              lumisEnd = jsonVec.end(),
                                                              ilumi = lumisBegin;
                                                              ilumi != lumisEnd;
                                                              ++ilumi) 
  {
    if (run >= ilumi->startRun() && run <= ilumi->endRun() &&
        lumi >= ilumi->startLumi() && lumi <= ilumi->endLumi()) return true;
  }
  return false;
}
/*
bool jsonContainsEvent(
    const std::unordered_map<unsigned int, std::vector<std::pair<unsigned int, unsigned int>>>& jsonMap,
    unsigned int run,
    unsigned int lumi)
{
    if (jsonMap.empty()) return true;

    auto it = jsonMap.find(run);
    if (it == jsonMap.end()) return false;

    const auto& lumiRanges = it->second;
    for (const auto& range : lumiRanges) {
        if (lumi >= range.first && lumi <= range.second)
            return true;
    }
    return false;
}*/
/*bool jsonContainsEvent(
    const std::map<unsigned int, std::vector<std::pair<unsigned int, unsigned int>>>& jsonMap,
    unsigned int run,
    unsigned int lumi)
{
    if (jsonMap.empty()) return true;

    auto it = jsonMap.find(run);
    if (it == jsonMap.end()) return false;

    const auto& ranges = it->second;

    int left = 0, right = ranges.size() - 1;
    while (left <= right) {
        int mid = (left + right) / 2;

        if (lumi < ranges[mid].first) {
            right = mid - 1;
        } else if (lumi > ranges[mid].second) {
            left = mid + 1;
        } else {
            return true;
        }
    }
    return false;
}*/
/*
bool jsonContainsEvent(const std::vector<edm::LuminosityBlockRange>& jsonVec,
                       unsigned int run,
                       unsigned int lumi)
{
    if (jsonVec.empty()) return true;

    // Find first range with startRun >= run
    auto it = std::lower_bound(
        jsonVec.begin(), jsonVec.end(), run,
        [](const edm::LuminosityBlockRange& range, unsigned int r) {
            return range.startRun() < r;
        });

    // Check this and possibly previous element
    for (int i = 0; i < 2; ++i) {
        if (it == jsonVec.end()) break;

        if (run >= it->startRun() && run <= it->endRun() &&
            lumi >= it->startLumi() && lumi <= it->endLumi()) {
            return true;
        }

        if (it == jsonVec.begin()) break;
        --it;
    }

    return false;
}*/

int main(int argc, char ** argv){
  // load framework libraries
  gSystem->Load( "libFWCoreFWLite" );
  FWLiteEnabler::enable();
  if (argc != 4) {
    std::cout << "Use as follows: FWLiteGoodLumi <pythonFileWithGoodLumiJson> <inputDataFilename> <outputDataFilename> \n";
    return 0;
  }

  std::cout << "Run Branch: " + RUN_BRANCH << std::endl;
  std::cout << "Lumi Branch: " + LUMI_BRANCH << std::endl;
  std::cout << "Events Tree: " + EVENTS_TREE << std::endl;

  std::vector<std::string> arguments(argv + 1, argv + argc);
  PyBind11ProcessDesc builder (argv[1], true, arguments);
  edm::ParameterSet const& inputs = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("inputs");

  std::vector<edm::LuminosityBlockRange> jsonVector;
  if ( inputs.exists("lumisToProcess") ) 
    {
      std::vector<edm::LuminosityBlockRange> const & lumisTemp =
	inputs.getUntrackedParameter<std::vector<edm::LuminosityBlockRange> > ("lumisToProcess");
      jsonVector.resize( lumisTemp.size() );
      copy( lumisTemp.begin(), lumisTemp.end(), jsonVector.begin() );
    }


  /*std::unordered_map<unsigned int, std::vector<std::pair<unsigned int, unsigned int>>> jsonMap;

  for (const auto& range : jsonVector) {
    for (unsigned int r = range.startRun(); r <= range.endRun(); ++r) {
        jsonMap[r].emplace_back(range.startLumi(), range.endLumi());
    }
}*/
  /*std::map<unsigned int, std::vector<std::pair<unsigned int, unsigned int>>> jsonMap;
  for (const auto& range : jsonVector) {
    unsigned int run = range.startRun();  // usually == endRun()
    jsonMap[run].emplace_back(range.startLumi(), range.endLumi());
  }

  for (auto& [run, ranges] : jsonMap) {
    std::sort(ranges.begin(), ranges.end());

    std::vector<std::pair<unsigned int, unsigned int>> merged;
    for (const auto& r : ranges) {
        if (merged.empty() || r.first > merged.back().second + 1) {
            merged.push_back(r);
        } else {
            merged.back().second = std::max(merged.back().second, r.second);
        }
    }
    ranges = std::move(merged);
  }

  std::sort(jsonVector.begin(), jsonVector.end(),
          [](const edm::LuminosityBlockRange& a,
             const edm::LuminosityBlockRange& b) {
              if (a.startRun() != b.startRun())
                  return a.startRun() < b.startRun();
              return a.startLumi() < b.startLumi();
          });
*/
  std::string inputFilename = argv[2];
  std::string outputFilename = argv[3];

  //create output file
  TFile *outputFile = TFile::Open( outputFilename.c_str(), "RECREATE");
  
  //loop over all TTrees in the file and add the weight branch to each of them
  TFile *inputFile = TFile::Open(inputFilename.c_str(), "READ");
  if (!inputFile || inputFile->IsZombie()) {
    std::cerr << "Error: cannot open file" << std::endl;
    return 1;
  }

  assert(inputFile);
  inputFile->cd();
  TIter nextkey(inputFile->GetListOfKeys());
  TKey *key;
  TKey *previous = NULL;
  while((key = (TKey*)nextkey())){
    std::string className = key->GetClassName();
    std::cout << "Getting key from file.  Class type: " << className << std::endl;
    if(className.compare("TTree") != 0){
      std::cout << "Skipping key (not a TTree)" << std::endl;
      outputFile->cd();
      TObject *outObj = key->ReadObj();
      outObj->Write();
      inputFile->cd();
      continue;
    }

    //if this key has the same name as the previous one, it's an unwanted cycle and we skip it
    if(previous != NULL && strcmp(key->GetName(), previous->GetName()) == 0)
    {
        continue;
    }
    previous = key;
    
    TTree *inputTree = (TTree*)key->ReadObj();
    if(inputTree->GetName() != EVENTS_TREE){
      std::cout << "Tree " << inputTree->GetName() << " is not " << EVENTS_TREE << std::endl;
      continue;
    }
    std::cout << "Processing tree " << inputTree->GetName() << std::endl;
    
    //create new normalized tree
    outputFile->cd();
    TTree *outputTree = inputTree->CloneTree(0);  
    std::cout << "Events in the ntuple: " << inputTree->GetEntries() << std::endl;
    
    UInt_t run = 0;
    UInt_t lumi = 0;
    int status = 0;
    status = inputTree->SetBranchAddress(RUN_BRANCH.c_str(), &run);
    if (status < 0) {
      std::cerr << "Error setting branch address for " << RUN_BRANCH << std::endl;
      return 1;
    }

    status = inputTree->SetBranchAddress(LUMI_BRANCH.c_str(), &lumi);
    if (status < 0) {
      std::cerr << "Error setting branch address for " << LUMI_BRANCH << std::endl;
      return 1;
    }

    std::cout << "Input Tree loaded" << std::endl;

    std::cout << "JSON ranges: " << jsonVector.size() << std::endl;

    auto start = std::chrono::high_resolution_clock::now();
    //store the weights
    for (int n=0;n<inputTree->GetEntries();n++) { 
      if (n == 0) std::cout << "Processing Events" << std::endl;
      if (n%10000==0){ 
        std::cout << "Processed Event " << n << "\n";
        auto now = std::chrono::high_resolution_clock::now();
        std::cout << "Time per 10k events: "
              << std::chrono::duration<double>(now - start).count()
              << " s\n";
        start = now;
      }

      inputTree->GetEntry(n);

      if(jsonContainsEvent(jsonVector, run, lumi) ) {	
      //if(jsonContainsEvent(jsonMap, run, lumi) ) {	
	        outputTree->Fill(); 
      }
      if (n == 0) std::cout << "1st Event Processed" << std::endl;
    }
    //save
    outputTree->Write();
    inputFile->cd();
    std::cout << "Output Number of Events: " << outputTree->GetEntries() << "\n";
  }
  inputFile->Close();
  std::cout << "Closing output file." << std::endl;    
  outputFile->Close();
  delete outputFile;   
  return 0;
}
