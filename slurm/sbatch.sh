#!/bin/bash
# this dictates the number of measurements to be made, and for what densities
for density in 4 9 10 11 14 20
do
    n=$(echo $density*3600 | bc)
    echo $n
    mkdir meas_32x$density
    cp srun_header.sh meas_32x$density/srun.sh
    echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py -s --cores 32 --start '$n' --step 0 --number 32 --scaling 60'>>meas_32x$density/srun.sh
    cd meas_32x$density/
    output=$(sbatch srun.sh)
    echo $output
    touch 'jobid_'${output:20}
    cd ..
done
