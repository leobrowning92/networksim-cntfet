#!/bin/bash
# specific gate sweep measurements

# partial gate with highest onoff 1297489092 density=9.5
# partial gate with onoff~1 1296295872 density=9.5
# high back onoff high density device 1197951452 density 11.5
# low back onoff high density device 1138375167 density 11.5
mkdir data
cd data
for omap in {0..1}
do

    density=9.5
    seed=1297489092
    n=$(echo $density*3600 | bc)
    n=${n%.*}
    echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1 --seed '$seed' --vgnum=11' > mns$seed'om'$omap'd'$density.sh
    subpy -P 1 -t 2-0 mns$seed'om'$omap'd'$density.sh

    density=9.5
    seed=1296295872
    n=$(echo $density*3600 | bc)
    n=${n%.*}
    echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1 --seed '$seed' --vgnum=11' > mns$seed'om'$omap'd'$density.sh
    subpy -P 1 -t 2-0 mns$seed'om'$omap'd'$density.sh

    density=11.5
    seed=1197951452
    n=$(echo $density*3600 | bc)
    n=${n%.*}
    echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1 --seed '$seed' --vgnum=11' > mns$seed'om'$omap'd'$density.sh
    subpy -P 1 -t 2-0 mns$seed'om'$omap'd'$density.sh

    density=11.5
    seed=1138375167
    n=$(echo $density*3600 | bc)
    n=${n%.*}
    echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1 --seed '$seed' --vgnum=11' > mns$seed'om'$omap'd'$density.sh
    subpy -P 1 -t 2-0 mns$seed'om'$omap'd'$density.sh


done
cd ..
