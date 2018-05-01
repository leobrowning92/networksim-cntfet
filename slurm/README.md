## Slurm instructions

the `srun.sh` script is a standalone script to run a single slurm job in the current working directory. This should usually be run in its own directory as it will generate a number of outfiles, as well as data and job id files.

it can be run, once the desired slurm and python parameters for the job are set in `srun.sh`, using:

    sbatch srun.sh

The `sbatch.sh` file is used to batch creat a number of slurm jobs, and will generate its own measurement subdirectories for each parameter set. The example files will run 32 measurements on 32 cores for each job, and a job will be submitted for 6 stick densities, from 4 to 20 per um.

slurm parameters are set in the `srun_header.sh` file, while parameters for the python job are set in `sbatch.sh`. These must be checked to ensure they match, and for that reason could be integrated into a single script at some point. Usage is:

    bash sbatch.sh
