# bash timetest.sh 20 2 > test.log runs grids up to 20x20 on 2 cores
# cat test.log | grep -E 'sys|row' #see how things evolved over time
# note timing and printed info from resistorGrid missmatched
for i in $(seq 2 $1)
do
    sem -k -j $2 time python3 resistorGrid.py $i $i 2>&1
done
sem --wait
