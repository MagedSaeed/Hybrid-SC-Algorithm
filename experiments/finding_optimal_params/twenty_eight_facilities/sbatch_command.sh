#!/usr/bin/env bash
#SBATCH --job-name=twenty_eight_facilities_exp                        # Job name
#SBATCH --nodes=9                                                     # Run all processes on a single node	
#SBATCH --ntasks=243                                                  # Run a single task	
#SBATCH --mem=4gb                                                     # Total memory limit
#SBATCH --output=/cpgpfs/home/ptashraf/MagedFiles/Hybrid-SC-Algorithm/experiments/twenty_eight_facilities/log%j.out     # Standard output and error log

bash experiments/twenty_eight_facilities/parallel_run.sh
