#!/usr/bin/env bash
#SBATCH --job-name=eighteen_facilities_exp                            # Job name
#SBATCH --nodes=3                                                     # Run all processes on a single node	
#SBATCH --ntasks=81                                                  # Run a single task	
#SBATCH --mem=8gb                                                     # Total memory limit
#SBATCH --output=/cpgpfs/home/ptashraf/MagedFiles/Hybrid-SC-Algorithm/experiments/eighteen_facilities/log%j.out     # Standard output and error log

bash experiments/eighteen_facilities/parallel_run.sh