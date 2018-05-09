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

## electrical junction values:
Fuhrer: mm=200kOhm, ss=400kOhm
tombler : mm 400 to 600 ohm from on to off
## Optimization
use cProfile and the [gprof2dot](https://github.com/jrfonseca/gprof2dot).py script to generate profiles of time spent for running the script.
explicit number to run optimization on is:

    kd_percolation.py 300 --pm 0.135 --length 0 --scaling 5

and corresponds to 300 sticks on a 5um square area with a length distribution of 0.66pm0.44um corresponding to my experimental results. conduction is calculated in each case.

which is run in sequence as:
    (python -m cProfile -o output.pstats kd_percolation.py 300; python gprof2dot.py -n 1 -f pstats output.pstats | dot -Tpng -o output.png)

The total run time over 5 or 6 tries is between 14 and 15 seconds (user time) when running `time python kd_percolation.py 300` for the original brute force cluster search.

Using a kdtree with a sorted length list and length dependant search radius the same run times are 3.6 to 3.8 seconds. 3.2s over 5 repeats.

#### optimization improvements

- define endpoints from sticks before query loops 1.65 seconds over 5 repeats.
- define kind of sticks outside querry loop 1.48 s over 5 repeats
- made interval checks early in the intersection check code 1.34 over 10 repeats
- moved cluster calculation over to the graph structure, so that only interstects are calculated pre graph. 0.35 over 10 repeats.

### Running remotely

to get the data from the baptiste's grid run

    scp -r leo@10.30.128.49:/home/leo/gitrepos/networksim-cntfet/data /home/leo/Desktop/

### Running on heisenberg
put the srun script into a seperate directory for the data runtime
then edit the number of cores for the measure_perc.py to match the number of tasks in the SBATCH section
then run:

    sbatch srun.sh

To check on the job, use:

    squeue -o "%.18i %.9P %.8j %.8u %.2t %.8M %.5D %.4C %R"

usage of `squeue` found [here](https://slurm.schedmd.com/squeue.html)
