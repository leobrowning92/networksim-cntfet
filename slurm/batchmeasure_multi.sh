#!/bin/bash
# this dictates the number of measurements to be made, and for what densities
mkdir data_8-12_800x
cd data_8-12_800x
omap=0
for step in {0..800}
do
    density=$(echo 8+0.005*$step | bc)
    n=$(echo $density*3600 | bc)
    n=${n%.*}
    for x in {1..100}
    do
        echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore  -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1' > mnet$density'om'$omap.sh
        subpy -P 1 -t 2-0 mnet$density'om'$omap.sh
    done
done
cd ..
