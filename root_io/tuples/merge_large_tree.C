// hadd replacement used by hadd_tuples_EOS.sh.
//
// hadd cannot raise TTree::fgMaxTreeSize (default 100 GB): past that, ROOT silently
// switches the output to <name>_1.root, splitting the tree across files. This merges
// with TFileMerger (what hadd uses) after raising the limit, so the output stays one file.
//
// Usage: root -l -b -q 'merge_large_tree.C+("out.root","inputs.txt")'
//   inputs.txt: one input file path/URL per line.

#include <fstream>
#include <iostream>
#include <string>

#include "TFileMerger.h"
#include "TROOT.h"
#include "TSystem.h"
#include "TTree.h"

void merge_large_tree(const char* out, const char* listFile)
{
    TTree::SetMaxTreeSize(10000000000000LL);  // 10 TB: effectively no split

    std::ifstream in(listFile);
    if (!in) {
        std::cerr << "[ERROR] cannot read input list " << listFile << std::endl;
        gSystem->Exit(1);
    }

    TFileMerger merger(kFALSE);
    if (!merger.OutputFile(out, "RECREATE")) {
        std::cerr << "[ERROR] cannot open output " << out << std::endl;
        gSystem->Exit(1);
    }

    int nFiles = 0;
    std::string line;
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        if (!merger.AddFile(line.c_str(), kFALSE)) {
            std::cerr << "[ERROR] cannot add input " << line << std::endl;
            gSystem->Exit(1);
        }
        ++nFiles;
    }
    if (nFiles == 0) {
        std::cerr << "[ERROR] no input files in " << listFile << std::endl;
        gSystem->Exit(1);
    }

    std::cout << "Merging " << nFiles << " files into " << out << std::endl;
    if (!merger.Merge()) {
        std::cerr << "[ERROR] merge failed for " << out << std::endl;
        gSystem->Exit(1);
    }
}
