#!/bin/bash
# this dictates the number of measurements to be made, and for what densities
mkdir data_7-12_10x
cd data_7-12_10x
for omap in {0..1}
do
    for step in {0..20}
    do
        density=$(echo 7+0.25*$step | bc)
        n=$(echo $density*3600 | bc)
        n=${n%.*}
        for x in {1..10}
        do
            echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1' > mnet$density'om'$omap.sh
            subpy -P 1 -t 2-0 mnet$density'om'$omap.sh
        done
    done
done
cd ..

mkdir data_1-20_1x
cd data_1-20_1x
for omap in {0..1}
do
    for step in {0..76}
    do
        density=$(echo 1+0.25*$step | bc)
        n=$(echo $density*3600 | bc)
        n=${n%.*}
        for x in {1}
        do
            echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1' > mnet$density'om'$omap.sh
            subpy -P 1 -t 2-0 mnet$density'om'$omap.sh
        done
    done
done
cd ..

mkdir data_9-11_100x
cd data_9-11_100x
for omap in {0..1}
do
    for step in {0..8}
    do
        density=$(echo 9+0.25*$step | bc)
        n=$(echo $density*3600 | bc)
        n=${n%.*}
        for x in {1..100}
        do
            echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1' > mnet$density'om'$omap.sh
            subpy -P 1 -t 2-0 mnet$density'om'$omap.sh
        done
    done
done
cd ..
