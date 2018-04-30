#!/bin/bash
#SBATCH -N 1      # nodes requested
#SBATCH -n 32     # tasks requested. default is one core per task
#SBATCH -o outfile  # send stdout to outfile
#SBATCH -e errfile  # send stderr to errfile
#SBATCH -t 10:00:00  # time requested in hour:minute:second
#SBATCH --mem-per-cpu=1024
#SBATCH --mail-user=$USER@localhost
python3 ~/gitrepos/networksim-cntfet/measure_perc.py -s --cores 32 --start 36000 --step 0 --number 32 --scaling 60
