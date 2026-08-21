#include <TBranch.h>
#include <TFile.h>
#include <TROOT.h>
#include <TTree.h>
#include <iostream>
// g++ -o ./bin/SkimTuplesggH src/SkimTuplesggH.cc $(root-config --cflags
// --libs)

int main(int argc, char *argv[]) {

    if (argc != 6) {
        std::cerr << "Please give 5 arguments: input file, output file, era, "
                     "channel, is_data(T/F)"
                  << std::endl;
        return -1;
    }

    TString input(argv[1]);
    TString output(argv[2]);
    TString era(argv[3]);
    TString channel(argv[4]);
    const bool is_data = *argv[5] == 'T';
    std::cout << "era: " << era << std::endl;
    std::cout << "channel: " << channel << std::endl;

    // Open the input ROOT file and get the TTree
    TFile inputFile(input, "READ");
    if (inputFile.IsZombie()) {
        std::cerr << "Error opening input file!" << std::endl;
        return 0;
    }

    TTree *tree_input = (TTree *)inputFile.Get("tree_output");
    if (!tree_input) {
        std::cerr << "Tree output not found in file " << input << std::endl;
        return 0;
    }
    tree_input->SetBranchStatus("*", 0);

    for (auto ggh_branches : {"diMuon_mass",
                              "diMuon_bsConstrainedMass",
                              "diMuon_pt",
                              "diMuon_bsConstrainedPt",
                              "diMuon_rapidity",
                              "mu1_pt_mass_ratio",
                              "mu2_pt_mass_ratio",
                              "mu1_bsConstrainedPt_mass_ratio",
                              "mu2_bsConstrainedPt_mass_ratio",
                              "mu1_eta",
                              "mu2_eta",
                              "phi_CS",
                              "cos_theta_CS",
                              "n_jet",
                              "leading_jet_pt",
                              "subleading_jet_pt",
                              "leading_jet_eta",
                              "subleading_jet_eta",
                              "diJet_mass",
                              "delta_eta_diJet",
                              "delta_phi_diJet",
                              "z_zeppenfeld",
                              "min_delta_eta_diMuon_jet",
                              "min_delta_phi_diMuon_jet",
                              //"weight_no_lumi",
                              "weight",
                              "is_ggH_category",
			                  "relative_diMuon_mass_error",
                              "relative_diMuon_bsConstrainedMass_error",
                  })
        tree_input->SetBranchStatus(ggh_branches, 1);

    gROOT->cd();
    // Open the output ROOT file and create a new TTree
    TFile output_file("./root_io/skim/ggH/" + channel + "_" + era + "_skim.root",
                      "RECREATE");
    TTree *tree_output = tree_input->CloneTree(0); // Clone the structure only

    //tree_output = tree_input->CopyTree("(is_ggH_category == 1) && (diMuon_mass > 115. && diMuon_mass < 135.)");
    tree_output = tree_input->CopyTree("(is_ggH_category == 1) && (diMuon_bsConstrainedMass > 115. && diMuon_bsConstrainedMass < 135.)");

    // Write the selected tree to the output file

    output_file.cd();
    tree_output->Write();
    output_file.Close();
    inputFile.Close();
}
