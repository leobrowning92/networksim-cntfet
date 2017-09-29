from multiprocessing import Process, Pool
from resistorGrid import Resistor,Network
import time, datetime, sys
import numpy as np
def time_resistor_net(size):
    start_time=time.time()
    net=Network(size,size,Resistor)
    net.solve_mna()
    end_time=time.time()
    runtime=str(datetime.timedelta(seconds=end_time-start_time))
    print("{}, {}, {}, {}".format(size,size,size**2,runtime))
if __name__ == "__main__":
    print("rows, columns, nodeNumber, runtime")
    pool = Pool(processes=2)
    pool.map(time_resistor_net, [*list(range(2,10)),*list(range(10,30,10))])
