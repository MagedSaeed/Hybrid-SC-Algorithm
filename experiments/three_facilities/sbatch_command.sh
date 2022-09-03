#!/usr/bin/env bash
#SBATCH --job-name=three_facilities_exp                               # Job name
#SBATCH --nodes=3                                                     # Run all processes on a single node	
#SBATCH --ntasks=81                                                   # Run a single task	
#SBATCH --cpus-per-task=1                                             # Number of CPU cores per task
#SBATCH --mem=8gb                                                     # Total memory limit
#SBATCH --output=/cpgpfs/home/ptashraf/MagedFiles/Hybrid-SC-Algorithm/experiments/three_facilities/log%j.out     # Standard output and error log

bash experiments/three_facilities/parallel_run.sh