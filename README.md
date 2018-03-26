# networksim-cntfet

## Modified Nodal Analysis (MNA)
The best and most comprehensive links for MNA on the web:
[MNA](https://www.swarthmore.edu/NatSci/echeeve1/Ref/mna/MNA2.html),
[Algorithm](https://www.swarthmore.edu/NatSci/echeeve1/Ref/mna/MNA3.html),
[Examples](https://www.swarthmore.edu/NatSci/echeeve1/Ref/mna/MNA4.html), and
[Matrix formation rules](https://www.swarthmore.edu/NatSci/echeeve1/Ref/mna/MNAMatrixRules.html).

the network is labeled:

|rows/columns->|0|1|2|...|c-1|
|---|:---:|:---:|:---:|:---:|:---:|
|0|0 |1  |2  | ... |c-1 |
|1|c |c+1|c+2|...|c+c-1|
|2|2c|2c+1|...|...|2c+c-1|
|...|...|...|...|...|...|
|(r-1)*c|(r-1)*c+1|...|...|...|(r-1)*c+c-1=r*c-1|


## Optimization
use cProfile and the [gprof2dot](https://github.com/jrfonseca/gprof2dot).py script to generate profiles of time spent for running the script.
explicit number to run optimization on is:

    kd_percolation.py 300 --pm 0.135 --length 0 --scaling 5

and corresponds to 300 sticks on a 5um square area with a length distribution of 0.66pm0.44um corresponding to my experimental results. conduction is calculated in each case.

which is run in sequence as:
    (python -m cProfile -o output.pstats kd_percolation.py 300; python gprof2dot.py -n 1 -f pstats output.pstats | dot -Tpng -o output.png)

The total run time over 5 or 6 tries is between 14 and 15 seconds (user time) when running `time python kd_percolation.py 300` for the original brute force cluster search.

Using a kdtree with a sorted length list and length dependant search radius the same run times are 3.6 to 3.8 seconds.
