#!/bin/bash
# this dictates the number of measurements to be made, and for what densities
mkdir data
cd data
for omap in {0..2}
do
    for density in {9..14}
    do
        n=$(echo $density*3600 | bc)
        for x in {1..10}
        do
            echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1 --seed '$x > mnet$density'om'$omap's'$x.sh
            subpy -P 1 -t 2-0 mnet$density'om'$omap's'$x.sh
        done
    done
done
cd ..
