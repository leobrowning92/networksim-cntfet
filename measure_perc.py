import os
import percolation as perc
from timeit import default_timer as timer
import pandas as pd
import networkx as nx
from multiprocessing import Pool




def measure_fullnet(n,v=True,scaling=60):
    start = timer()
    data=pd.DataFrame(columns = ['sticks', 'size', 'density', 'nclust', 'maxclust', 'ion', 'ioff', 'runtime', 'fname'])
    try:
        collection=perc.StickCollection(n,scaling=scaling,notes='run')

        nclust=len(collection.sticks.cluster.drop_duplicates())
        maxclust=len(max(nx.connected_components(collection.graph)))
        fname=collection.fname
    except Exception as e:
        nclust=0
        maxclust=0
        fname=0
        print("measurement failed: error making collection")
        print("ERROR : ",e)
    try:
        collection.save_system()
    except Exception as e:
        print("measurement failed: error saving data")
        print("ERROR : ",e)
    try:
        collection.show_system(show=False,save='on')
    except Exception as e:
        print("measurement failed: error saving image")
        print("ERROR : ",e)
    try:
        ion=sum(collection.cnet.source_currents)
        collection.cnet.set_global_gate(10)
        collection.cnet.update()
        collection.show_system(show=False,save='off')
        ioff=sum(collection.cnet.source_currents)
    except Exception as e:
        ion=0
        ioff=0
        print("measurement failed: error gating")
        print("ERROR : ",e)

    end = timer()
    runtime=end - start
    data.loc[0]=[n,scaling,n/scaling,nclust,maxclust,ion,ioff,runtime,fname]
    if fname:
        data.to_csv(fname+"_data.csv")
    return data
def n_measure(n):
    measure_fullnet(n,scaling=60)
def measure_number_series():
    n=[n*100 for n in range(1,9)] + [n*1000 for n in range(1,9)] + [n*1000 for n in range(1,9)]
    pool = Pool(os.cpu_count()-1)
    pool.map(n_measure, n)



if __name__ == '__main__':
    measure_number_series()
