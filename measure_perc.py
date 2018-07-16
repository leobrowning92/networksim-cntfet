import os,argparse,traceback,sys,py
import percolation as perc
from timeit import default_timer as timer
import pandas as pd
import numpy as np
import networkx as nx
from multiprocessing import Pool
import uuid as id
from cnet import LinExpTransistor




def checkdir(directoryname):
    """
    Args:
      directoryname: directory path to check
    if the directory doesn't exist the directory is created.
    """
    if os.path.isdir(directoryname) == False:
        os.system("mkdir " + directoryname)
    pass

def single_measure(n,scaling,l='exp', dump=False, savedir='test', seed=0, onoffmap=1, v=False, element= LinExpTransistor):
    datacol=['sticks', 'size', 'density', 'current', 'gatevoltage','gate', 'nclust', 'maxclust', 'charpath', 'clustercoeff', 'connectivity'  'fname','onoffmap', 'seed', 'runtime', 'element']
    d=n/scaling**2
    seed=np.random.randint(low=0,high=2**32)
    fname=os.path.join(savedir,"n{:05d}_d{:2.1f}_seed{:010d}".format(n,d,seed))
    start = timer()
    data=pd.DataFrame(columns = datacol)

    device=perc.CNTDevice(n,scaling=scaling,notes='run',l=l,seed=seed,onoffmap=onoffmap)
    device.label_clusters()

    nclust=len(device.sticks.cluster.drop_duplicates())
    try:
        maxclust=len(max(nx.connected_components(device.graph)))
    except:
        maxclust=0

    if dump:
        try:
            device.save_system(fname)
        except Exception as e:
            if v:
                print("measurement failed: error saving data")
                print("ERROR for {} sticks:\n".format(n),e)
                traceback.print_exc(file=sys.stdout)
    percolating=device.percolating

    end = timer()
    runtime=end - start
    data['runtime']=runtime

    data.to_csv(fname+"_data.csv")
    return data,fname

def measure_fullnet(n,scaling, l='exp', save=False, seed=0,onoffmap=1, v=False ,remote=False):

    datacol=['sticks', 'size', 'density', 'nclust', 'maxclust', 'ion', 'ioff','gate', 'fname','seed','onoffmap']
    start = timer()
    data=pd.DataFrame(columns = datacol)

    collection=perc.StickCollection(n,scaling=scaling,notes='run',l=l,seed=seed,onoffmap=onoffmap)
    collection.label_clusters()
    nclust=len(collection.sticks.cluster.drop_duplicates())
    try:
        maxclust=len(max(nx.connected_components(collection.graph)))
    except:
        maxclust=0
    fname=collection.fname
    percolating=collection.percolating

    if save:
        try:
            collection.save_system()
        except Exception as e:
            if v:
                print("measurement failed: error saving data")
                print("ERROR for {} sticks:\n".format(n),e)
                traceback.print_exc(file=sys.stdout)

    if percolating:
        try:
            ion=sum(collection.cnet.source_currents)
            collection.cnet.set_global_gate(10)
            collection.cnet.update()
            ioff=sum(collection.cnet.source_currents)
            gate='back'

        except Exception as e:
            if v:
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
        data.loc[0]=[n,scaling,n/scaling**2,nclust,maxclust,ion,ioff,'back',fname,seed,onoffmap]
        data.loc[1]=[n,scaling,n/scaling**2,nclust,maxclust,ion,ioff_totaltop,'total',fname,seed,onoffmap]
        data.loc[2]=[n,scaling,n/scaling**2,nclust,maxclust,ion,ioff_partialtop,'partial',fname,seed,onoffmap]
    else:
        ion=0
        ioff=0
        gate='back'
        data.loc[0]=[n,scaling,n/scaling**2,nclust,maxclust,ion,ioff,gate,fname,seed,onoffmap]
    end = timer()
    runtime=end - start
    data['runtime']=runtime
    if fname:
        data.to_csv(fname+"_data.csv")
    return data

def measure_async(cores, start, step, number, scaling, save=False, onoffmap=[1], seeds=[]):
    """
    Args:
      cores: number of cores to run the measurement on
      start: starting point for the range of number of sticks to simulate
      step: increment for the range of number of sticks to simulate
      number: total number of simulations to run, where the range of values simulated is specified by the start = start and end = start+sep*number
      scaling: size of the square system to simulate, in um
      save:  (Default value = False)
      onoffmap: Default value = 1)
      seeds: Default value = [])

    Returns:
        all of the data collected from each simulation with columns:
        ['sticks', 'size', 'density', 'nclust', 'maxclust', 'ion', 'ioff','gate', 'fname','seed','onoffmap']
    """
    uuid=id.uuid4()
    starttime = timer()
    nrange=[int(start+i*step) for i in range(number)]
    if not(len(seeds)==number):
        seeds=np.random.randint(low=0,high=2**32,size=number)
    if not(os.path.isfile("seeds_{}.csv".format(uuid))):
        np.savetxt("seeds_{}.csv".format(uuid), seeds, delimiter=",")
    pool=Pool(cores)
    results=[]
    for omap in onoffmap:
        results= results+[pool.apply_async(measure_fullnet, args=(nrange[i],scaling,'exp',save,seeds[i],omap)) for i in range(number)]
    print(len(results))
    output=[res.get() for res in results]
    endtime = timer()
    runtime=endtime - starttime
    print('finished with a runtime of {:.0f} '.format(runtime))
    data=pd.concat(output)
    if save:
        data.to_csv('measurement_batch_{}.csv'.format(uuid))
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t",'--test',action="store_true",default=False)
    parser.add_argument('-s','--save',action="store_true",default=False)
    parser.add_argument("--cores",type=int,default=1)
    parser.add_argument("--start",type=int)
    parser.add_argument("--step",type=int,default=0)
    parser.add_argument("--number",type=int)
    parser.add_argument("--scaling",type=int,default=5)
    parser.add_argument("--onoffmap",nargs='*',type=int)
    args = parser.parse_args()
    checkdir('data')
    if args.test:
        measure_async(2,500,0,10,5,save=True)
    else:
        measure_async(args.cores, args.start, args.step, args.number,args.scaling, args.save,args.onoffmap)
