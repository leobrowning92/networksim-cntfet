#!/bin/bash
# specific gate sweep measurements

# partial gate with highest onoff 1297489092 density=9.5
# partial gate with onoff~1 1296295872 density=9.5
# high back onoff high density device 1197951452 density 11.5
# low back onoff high density device 1138375167 density 11.5
mkdir data
cd data
omap=0

density=9.5
seed=3712050199
n=$(echo $density*3600 | bc)
n=${n%.*}
echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1 --seed '$seed' --vgnum=11' > mns$seed'om'$omap'd'$density.sh
subpy -P 1 -t 2-0 mns$seed'om'$omap'd'$density.sh

density=9.75
seed=393068919
n=$(echo $density*3600 | bc)
n=${n%.*}
echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1 --seed '$seed' --vgnum=11' > mns$seed'om'$omap'd'$density.sh
subpy -P 1 -t 2-0 mns$seed'om'$omap'd'$density.sh

density=10.25
seed=245645779
n=$(echo $density*3600 | bc)
n=${n%.*}
echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1 --seed '$seed' --vgnum=11' > mns$seed'om'$omap'd'$density.sh
subpy -P 1 -t 2-0 mns$seed'om'$omap'd'$density.sh

density=10
seed=2120982883
n=$(echo $density*3600 | bc)
n=${n%.*}
echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1 --seed '$seed' --vgnum=11' > mns$seed'om'$omap'd'$density.sh
subpy -P 1 -t 2-0 mns$seed'om'$omap'd'$density.sh

density=12
seed=2548038466
n=$(echo $density*3600 | bc)
n=${n%.*}
echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1 --seed '$seed' --vgnum=11' > mns$seed'om'$omap'd'$density.sh
subpy -P 1 -t 2-0 mns$seed'om'$omap'd'$density.sh

density=12
seed=41991611272
n=$(echo $density*3600 | bc)
n=${n%.*}
echo 'python3 ~/gitrepos/networksim-cntfet/measure_perc.py singlecore -s -v  -n '$n' --scaling 60 --onoffmap '$omap' --element 1 --seed '$seed' --vgnum=11' > mns$seed'om'$omap'd'$density.sh
subpy -P 1 -t 2-0 mns$seed'om'$omap'd'$density.sh


cd ..
