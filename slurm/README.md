## Slurm instructions

for single measurements run

    subpy -P 32  measurenet.sh

where the measurement parameters are set in `measurenet.sh`

For measurement runs, use `batchmeasure.sh`, which generates measurement subdirectories, makes the measurenet files in each, and then runs the subpy.sh script on them. The parameters specified in batchmeasure will specify the network parameters




### slurm debugging
#### Issue

There is an error where all of the data produced from a given run is the same. ie all the same sticks, junctions and output for a 32 parameter step, 32 task job.

for a test 10 parameter space, 3 task job, every 3 parameter steps shows a different output.

Perhaps this indicates some kind of shared memory usage?
#### Solution

it turns out that when 32 tasks are made via slurm, and 32 jobs are made using pythons multiprocessing, the seeds used to generate the random numbers in the script, ie stick positions, lengths, metallic, are the same.

This results in the same system being run 32 times, which can be solved by calling `np.random.seed(x)` at the start of each measurement, where each seed `x` is different. This will ensure a different system.

An added bonus to this, is that systems can be regenerated from this seed without needing to save the entire system. The whole system can still be saved to reduce compute time needed later, but it isnt necessary for that to be the case.
