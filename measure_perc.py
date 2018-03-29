import os,argparse,traceback,sys
import percolation as perc
from timeit import default_timer as timer
import pandas as pd
import networkx as nx
from multiprocessing import Pool
import matplotlib
matplotlib.use("Qt5Agg")




def measure_fullnet(n,v=True,scaling=60,remote=False,l='exp',save=True):
    start = timer()
    data=pd.DataFrame(columns = ['sticks', 'size', 'density', 'nclust', 'maxclust', 'ion', 'ioff','ioff_totaltop', 'ioff_partialtop', 'runtime', 'fname'])
    if v:
        print("====== measuring {} sticks ======".format(n))
    try:
        collection=perc.StickCollection(n,scaling=scaling,notes='run',l=l)
        nclust=len(collection.sticks.cluster.drop_duplicates())
        maxclust=len(max(nx.connected_components(collection.graph)))
        fname=collection.fname
        percolating=collection.percolating
    except Exception as e:
        percolating=False
        nclust=0
        maxclust=0
        fname=0
        print("measurement failed: error making collection")
        print("ERROR for {} sticks:\n".format(n),e)
        traceback.print_exc(file=sys.stdout)
    if save:
        try:
            collection.save_system()
        except Exception as e:
            print("measurement failed: error saving data")
            print("ERROR for {} sticks:\n".format(n),e)
            traceback.print_exc(file=sys.stdout)
    if percolating:
        if not(remote):
            try:
                collection.show_system(show=False,save='on')
            except Exception as e:
                print("measurement failed: error saving image")
                print("ERROR for {} sticks:\n".format(n),e)
                traceback.print_exc(file=sys.stdout)
        try:
            ion=sum(collection.cnet.source_currents)
            collection.cnet.set_global_gate(10)
            collection.cnet.update()
            ioff=sum(collection.cnet.source_currents)
        except Exception as e:
            ion=0
            ioff=0
            print("measurement failed: error global gating")
            print("ERROR for {} sticks:\n".format(n),e)
            traceback.print_exc(file=sys.stdout)
        try:
            collection.cnet.set_global_gate(0)
            collection.cnet.set_local_gate([0.217,0.5,0.167,1.2], 10)
            collection.cnet.update()
            ioff_totaltop=sum(collection.cnet.source_currents)
            collection.cnet.set_global_gate(0)
            collection.cnet.set_local_gate([0.5,0,0.16,0.667], 10)
            collection.cnet.update()
            ioff_partialtop=sum(collection.cnet.source_currents)
        except:
            ioff_totaltop=0
            ioff_partialtop=0

        if not(remote):
            try:
                collection.show_system(show=False,save='off')
            except Exception as e:
                print("measurement failed: error saving image")
                print("ERROR for {} sticks:\n".format(n),e)
                traceback.print_exc(file=sys.stdout)
    else:
        ion=0
        ioff=0
        ioff_totaltop=0
        ioff_partialtop=0
    end = timer()
    runtime=end - start
    data.loc[0]=[n,scaling,n/scaling**2,nclust,maxclust,ion,ioff,ioff_totaltop,ioff_partialtop,runtime,fname]
    if fname:
        data.to_csv(fname+"_data.csv")
    return data
def n_vary_local(n):
    measure_fullnet(n,scaling=60)
def n_vary_remote(n):
    measure_fullnet(n,scaling=60,save=False)
def n_vary_expL_remote(n):
    measure_fullnet(n,scaling=60,remote=True)
def n_vary_066L_remote(n):
    measure_fullnet(n,l=0.66,scaling=60,remote=True)
def measure_number_series(remote=False):
    n=[1000]*1000+[1000]*1000+[14400]*1000+[28800]*1000+[36000]*1000+[54000]*100
    pool = Pool(os.cpu_count()-1)
    if remote:
        pool.map(n_vary_remote, n)
    else:
        pool.map(n_vary_local, n)

def measure_number_series_compareL(remote=True):
    nconst=[40000+n*2000 for n in range(1,10)]
    nexp=[30000+n*500 for n in range(1,20)]
    pool = Pool(os.cpu_count()-1)
    pool.map(n_vary_expL_remote, nexp)
    pool.map(n_vary_066L_remote, nconst)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t",'--test',action="store_true",default=False)
    parser.add_argument("-r",'--remote',action="store_true",default=False)
    args = parser.parse_args()

    if args.test:
        measure_fullnet(500,scaling=5,remote=args.remote)
    else:
        measure_number_series(remote=args.remote)
        measure_number_series_compareL(remote=args.remote)
