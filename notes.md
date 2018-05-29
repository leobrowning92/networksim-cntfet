## electrical junction values:
Fuhrer: mm=200kOhm, ss=400kOhm
tombler : mm 400 to 600 ohm from on to off. compares ms junction to Ti electrode-s junction.
Nirmalraj : 98kOhm to 2.6MOhm for 1.2nm to 14nm diameter bundles.
Topinka : 200kOhm junction resistance from tombler. Treats ms junctions and crosses as nonconductive
Stadermann : 100MOhm at some steps along the scan, attributed to junctions.
Lyons : estimates interjunction resistance from 70kOhm to 3.5Mohm for bundles and tubes
E. Lee : "demonstrate that potential barriers
located at nanotube crossings become dominant in the OFF state of cross-junction devices, as a result of the flattening of Schottky barriers present at the electrical contacts. Consequently, under applied bias, the electrostatic potential drop, and thus the photoresponse, occurs predominantly at these positions."
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
