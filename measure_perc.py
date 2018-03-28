import os,argparse,traceback
import percolation as perc
from timeit import default_timer as timer
import pandas as pd
import networkx as nx
from multiprocessing import Pool
import matplotlib
matplotlib.use("Qt5Agg")




def measure_fullnet(n,v=True,scaling=60,remote=False,l='exp'):
    start = timer()
    data=pd.DataFrame(columns = ['sticks', 'size', 'density', 'nclust', 'maxclust', 'ion', 'ioff', 'runtime', 'fname'])
    if v:
        print("====== measuring {} sticks ======".format(n))
    try:
        collection=perc.StickCollection(n,scaling=scaling,notes='run',l=l)
        nclust=len(collection.sticks.cluster.drop_duplicates())
        maxclust=len(max(nx.connected_components(collection.graph)))
        fname=collection.fname
    except Exception as e:
        nclust=0
        maxclust=0
        fname=0
        print("measurement failed: error making collection")
        print("ERROR for {} sticks:\n".format(n),e)
        traceback.print_exc()
    try:
        collection.save_system()
    except Exception as e:
        print("measurement failed: error saving data")
        print("ERROR for {} sticks:\n".format(n),e)
        traceback.print_exc()
    if collection.percolating:
        if not(remote):
            try:
                collection.show_system(show=False,save='on')
            except Exception as e:
                print("measurement failed: error saving image")
                print("ERROR for {} sticks:\n".format(n),e)
                traceback.print_exc()
        try:
            ion=sum(collection.cnet.source_currents)
            collection.cnet.set_global_gate(10)
            collection.cnet.update()
            ioff=sum(collection.cnet.source_currents)
        except Exception as e:
            ion=0
            ioff=0
            print("measurement failed: error gating")
            print("ERROR for {} sticks:\n".format(n),e)
            traceback.print_exc()
        if not(remote):
            try:
                collection.show_system(show=False,save='off')
            except Exception as e:
                print("measurement failed: error saving image")
                print("ERROR for {} sticks:\n".format(n),e)
                traceback.print_exc()
    else:
        ion=0
        ioff=0
    end = timer()
    runtime=end - start
    data.loc[0]=[n,scaling,n/scaling**2,nclust,maxclust,ion,ioff,runtime,fname]
    if fname:
        data.to_csv(fname+"_data.csv")
    return data
def n_vary_local(n):
    measure_fullnet(n,scaling=60)
def n_vary_expL_remote(n):
    measure_fullnet(n,scaling=60,remote=True)
def n_vary_066L_remote(n):
    measure_fullnet(n,l=0.66,scaling=60,remote=True)
def measure_number_series(remote=False):
    n=[n*100 for n in range(1,10)] + [n*1000 for n in range(1,10)] + [n*10000 for n in range(1,10)]+[10000+n*2000 for n in range(1,15)]
    pool = Pool(os.cpu_count()-1)
    if remote:
        pool.map(n_vary_remote, n)
    else:
        pool.map(n_vary_local, n)
def measure_number_series_compareL(remote=True):
    n=[n*100 for n in range(1,10)] + [n*1000 for n in range(1,10)] + [n*10000 for n in range(1,10)]+[10000+n*2000 for n in range(1,15)]
    pool = Pool(os.cpu_count()-1)
    pool.map(n_vary_expL_remote, n)
    pool.map(n_vary_066L_remote, n)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t",'--test',action="store_true",default=False)
    parser.add_argument("-r",'--remote',action="store_true",default=False)
    args = parser.parse_args()

    if args.test:
        measure_fullnet(500,scaling=5,remote=args.remote)
    else:
        measure_number_series(remote=args.remote)
