#!/bin/bash
# this dictates the number of measurements to be made, and for what densities
mkdir data
cd data
for omap in {0..1}
do
    for step in {0..50}
    do
        density=$(echo 9+0.04*$step | bc)
        n=$(echo $density*3600 | bc)
        echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1' > mnet$density'om'$omap.sh
        subpy -P 1 -t 2-0 mnet$density'om'$omap.sh

    done
done
cd ..
