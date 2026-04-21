#!/usr/bin/python

import os
import json
from listDatasets_Run3 import datasets_info

for dataset_name in datasets_info.keys():
    print("\n----- %s -----"%(dataset_name))

    if os.path.exists(dataset_name + ".list"):
        print("Run list already exists. Skipping!")
        continue

    DAS_path = datasets_info[dataset_name][-1]
    outputFile = open(dataset_name + ".list", "w")
    # command = "dasgoclient -query=\"file dataset=" + datasets[processName] + " instance=prod/phys03 \" -json > tmpOutput.json"
    command = (
        'dasgoclient -query="file dataset='
        + DAS_path
        + ' " -json > tmpOutput.json'
    )
    print(command)
    os.system(command)

    jsonFile = open("tmpOutput.json", "r")
    data = json.load(jsonFile)

    if(len(data) == 0):
        print("*************** NO ROOTFILES FOUND ***************")
        quit()
    for p in data:
        blockName = p["file"][0]["block.name"]
        fileName = p["file"][0]["name"]
        outputFile.write("root://cmsxrootd.fnal.gov/" + fileName + "\n")

    os.remove("tmpOutput.json")
