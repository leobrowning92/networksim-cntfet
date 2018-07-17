#!/bin/bash
# run in the directory where data is to be saved
mkdir linexp
cd linexp
for x in {1..10}
do
    echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s  -n 500 --scaling 5 --onoffmap 0 --element 1 --seed '$x > mnet$x.sh
    subpy -P 1 -t 24:00:00 mnet$x.sh
done
cd ..

mkdir fd
cd fd
for x in {1..10}
do
    echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s  -n 500 --scaling 5 --onoffmap 0 --element 0 --seed '$x > mnet$x.sh
    subpy -P 1 -t 24:00:00 mnet$x.sh
done
cd ..
