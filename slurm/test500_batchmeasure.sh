#!/bin/bash
# run in the directory where data is to be saved
for x in {1..50}
do
    n=500
    echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s  -n 500 --scaling 5' > measurenet.sh
    subpy -P 1 -t 24:00:00 measurenet.sh
done
