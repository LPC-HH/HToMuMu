
## How to run
1. Make sure you have generated the list of runs of a dataset from `../list/makeListFromDAS_Run3.py`.
2. Add/remove/update dataset list in `create_analyzer_jobs_LPC.py` using the corresponding `.list` file as the key.
    - This also creates a json file to store the expected number of jobs as a check for later.
3. Change analyzer version number in utils/version.py
4. Make RazorCommon `cd ../RazorCommon` then `scramv1 b clean; scramv1 b` to have an up to date goodLumi check binary `FWLiteGoodLumi`
5. Run `python3 create_analyzer_jobs_LPC.py`. This will create an analyzer directory with a subfolder for each dataset in the list.
    - To submit a single job, run `condor_submit task.jdl` inside the corresponding dataset directory. Note that the output of step 2 provides a one-line command to do this!
    - You can also run `bash condor_job_sender.sh` to send the jobs for all of the new datasets!
    - After the jobs have run, run ` bash analyzer_job_checker.sh` in order to see if there were errors with any of the datasets. The problematic datasets are stored in an output text file.
7. Once all jobs have finished, compute the total SumGenWeight by running `python3 ../scripts/ComputeWeights.py <T/F>`
    - Then run `python3 ../scripts/compute_DY_stitching.py`. Besides the stitching, it writes `stitch_zpt_norm`, the per-mass-region renormalization of the DY Z pT reweighting (`lib/ZptReweight.h`, inputs in `data/theory/`). There is one factor per region for the inclusive DY of an era, and the script prints it.
    - CreateTuple applies the Z pT weight to the stitched DY only, folds it into `weight`, and writes `zpt_weight` and `weight_no_zpt`. Without `stitch_zpt_norm`, as for analyzer outputs from before the reweighting, it prints a warning and leaves the DY unreweighted.
8. Change tuples version number in utils/version.py
9. Run the tuplizer with `python3 create_ctuples_jobs.py`
    - Similar to the analyzer job generator, this also creates a json file to store the expected number of jobs as a check for later.
10. After the jobs have run, run `bash ctuple_job_checker.sh` in order to see if there were errors with any of the datasets. The problematic datasets are stored in an output text file.

## How to run histos
1. Run `python3 create_histo_jobs_LPC.py`. 
    - To submit run `bash condor_histo_job_sender.sh` to send the jobs

## Considerations
- The `/err/` folder in each dataset directory contains the error output of each job. Don't worry if there is a short list of missing files, since they were added in case you want to run the process manually. In some cases there might be missing branches from problematic runs that can be ignored. Any other error message might need to be reviewed.
- The `/out/` folder contains the output info. Inside the corresponding `.out` file you will find the final tuples path!