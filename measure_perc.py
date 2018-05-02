import os,argparse,traceback,sys
import percolation as perc
from timeit import default_timer as timer
import pandas as pd
import networkx as nx
from multiprocessing import Pool

def checkdir(directoryname):
    if os.path.isdir(directoryname) == False:
        os.system("mkdir " + directoryname)
    pass


def measure_fullnet(n,scaling, l='exp', save=False, v=True ,remote=False):
    start = timer()
    data=pd.DataFrame(columns = ['sticks', 'size', 'density', 'nclust', 'maxclust', 'ion', 'ioff','ioff_totaltop', 'ioff_partialtop', 'runtime', 'fname'])
    try:
        collection=perc.StickCollection(n,scaling=scaling,notes='run',l=l)
        collection.label_clusters()
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

def measure_async(cores,start,step,number,scaling,save=False):
    starttime = timer()
    nrange=[int(start+i*step) for i in range(number)]

    pool=Pool(cores)
    results=[pool.apply_async(measure_fullnet,args=(n,scaling,'exp',save)) for n in nrange]
    output=[res.get() for res in results]

    endtime = timer()
    runtime=endtime - starttime
    print('finished with a runtime of {:.0f} seconds'.format(runtime))
    data=pd.concat(output)
    data.to_csv('measurement_cores{}_start{}_step{}_number{}_runtime{:.0f}.csv'.format(cores, start, step, number,runtime))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t",'--test',action="store_true",default=False)
    parser.add_argument('-s','--save',action="store_true",default=False)
    parser.add_argument("--cores",type=int,default=1)
    parser.add_argument("--start",type=int)
    parser.add_argument("--step",type=int,default=0)
    parser.add_argument("--number",type=int)
    parser.add_argument("--scaling",type=int,default=5)
    args = parser.parse_args()
    checkdir('data')
    if args.test:
        measure_async(2,500,0,10,5,save=True)
    else:
        measure_async(args.cores, args.start, args.step, args.number,args.scaling, args.save)
