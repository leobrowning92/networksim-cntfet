#!/bin/bash
# this dictates the number of measurements to be made, and for what densities
for density in 4 9 10 11 14 20
do
    n=$(echo $density*3600 | bc)
    mkdir meas_32x$density
    echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py -s --cores 32 --start '$n' --step 0 --number 32 --scaling 60' > meas_32x$density/measurenet.sh
    cd meas_32x$density/
    subpy -P 32 -t 24:00:00 measurenet.sh
    cd ..
done
