import os,argparse,traceback,sys
import percolation as perc
from timeit import default_timer as timer
import pandas as pd
import numpy as np
import networkx as nx
from multiprocessing import Pool
import uuid as id

#### preset onoffmappings  #####
### 0 ###
# only intertube junctions have a 10^3 on off ratio
onoffmap0={'ms':1000,'sm':1000, 'mm':1,'ss':1,'vs':1,'sv':1,'vm':1,'mv':1}
### 1 ###
# all ms junctions including electrodes have a 10^3 on off ratio
onoffmap1={'ms':1000,'sm':1000, 'mm':1,'ss':1,'vs':1000,'sv':1000,'vm':1000,'mv':1000}
### 2 ###
# all junctions including electrodes have a 10^3 on off ratio
onoffmap2={'ms':1000,'sm':1000, 'mm':1000,'ss':1000,'vs':1000,'sv':1000,'vm':1000,'mv':1000}
onoffmappings=[onoffmap0,onoffmap1,onoffmap2]


def checkdir(directoryname):
    if os.path.isdir(directoryname) == False:
        os.system("mkdir " + directoryname)
    pass

def measure_fullnet(n,scaling, l='exp', save=False, seed=0,onoffmap=1, v=True ,remote=False):
    datacol=['sticks', 'size', 'density', 'nclust', 'maxclust', 'ion', 'ioff','gate', 'fname','seed','onoffmap']
    start = timer()
    data=pd.DataFrame(columns = datacol)
    try:
        collection=perc.StickCollection(n,scaling=scaling,notes='run',l=l,seed=seed,onoffmap=onoffmappings[onoffmap])
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
            gate='back'

        except Exception as e:
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

def measure_async(cores, start, step, number, scaling, save=False, onoffmap=1, seeds=[]):
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
    print('finished with a runtime of {:.0f} seconds'.format(runtime))
    data=pd.concat(output)
    data.to_csv('measurement_batch_{}.csv'.format(uuid))


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
