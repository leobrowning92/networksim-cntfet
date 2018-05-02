## Slurm instructions

the `srun.sh` script is a standalone script to run a single slurm job in the current working directory. This should usually be run in its own directory as it will generate a number of outfiles, as well as data and job id files.

it can be run, once the desired slurm and python parameters for the job are set in `srun.sh`, using:

    sbatch srun.sh

The `sbatch.sh` file is used to batch creat a number of slurm jobs, and will generate its own measurement subdirectories for each parameter set. The example files will run 32 measurements on 32 cores for each job, and a job will be submitted for 6 stick densities, from 4 to 20 per um.

slurm parameters are set in the `srun_header.sh` file, while parameters for the python job are set in `sbatch.sh`. These must be checked to ensure they match, and for that reason could be integrated into a single script at some point. Usage is:

    bash sbatch.sh


### slurm debugging
#### Issue

There is an error where all of the data produced from a given run is the same. ie all the same sticks, junctions and output for a 32 parameter step, 32 task job.

for a test 10 parameter space, 3 task job, every 3 parameter steps shows a different output.

Perhaps this indicates some kind of shared memory usage?
#### Solution

it turns out that when 32 tasks are made via slurm, and 32 jobs are made using pythons multiprocessing, the seeds used to generate the random numbers in the script, ie stick positions, lengths, metallic, are the same.

This results in the same system being run 32 times, which can be solved by calling `np.random.seed(x)` at the start of each measurement, where each seed `x` is different. This will ensure a different system.

An added bonus to this, is that systems can be regenerated from this seed without needing to save the entire system. The whole system can still be saved to reduce compute time needed later, but it isnt necessary for that to be the case.
