#!/bin/bash

#SBATCH -N 1      # nodes requested
#SBATCH -n 2     # tasks requested
#SBATCH -o outfile  # send stdout to outfile
#SBATCH -e errfile  # send stderr to errfile
#SBATCH -t 0:01:00  # time requested in hour:minute:second
#SBATCH --mem-per-cpu=1024
#SBATCH --mail-user=$USER@localhost

python3 ~/gitrepos/networksim-cntfet/measure_perc.py -t

