#!/bin/bash
# this dictates the number of measurements to be made, and for what densities
for density in 4 9 10 11 14 20
do
    n=$(echo $density*3600 | bc)
    for x in {1..10}
    do
        echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s  -n '$n' --scaling 60 --onoffmap 0 --element 1 --seed '$x > mnet$density's'$x.sh
        subpy -P 1 -t 24:00:00 mnet$density's'$x.sh
    done
done
