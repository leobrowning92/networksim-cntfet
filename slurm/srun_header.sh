#!/bin/bash
#SBATCH -N 1      # nodes requested
#SBATCH -n 32     # tasks requested. default is one core per task
#SBATCH -o outfile  # send stdout to outfile
#SBATCH -e errfile  # send stderr to errfile
#SBATCH --mem-per-cpu=1024
#SBATCH -t 24:00:00  # time requested in hour:minute:second
#SBATCH --mail-user=$USER@localhost
