import os,argparse,traceback,sys,textwrap
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
def add_voltagemeas(device, data, vgrange=10, vgnum=3):
    gate=[]
    gatevoltage=[]
    current=[]
    vgvalues=np.linspace(-vgrange,vgrange,vgnum)
    for g in ['back', 'partial', 'total']:
        for vg in vgvalues:
            c=device.gate(vg,g)
            current.append(c)
            gate.append(g)
            gatevoltage.append(vg)
    data.gate=gate
    data.gatevoltage=gatevoltage
    data.current=current
    return data
def single_measure(n,scaling,l='exp', dump=False, savedir='test', seed=0, onoffmap=1, v=False, element= LinExpTransistor):
    datacol=['sticks', 'scaling', 'density', 'current', 'gatevoltage','gate', 'nclust', 'maxclust', 'fname','onoffmap', 'seed', 'runtime', 'element']
    checkdir(savedir)
    start = timer()

    # variables initialized

    d=n/scaling**2
    seed=np.random.randint(low=0,high=2**32)
    fname=os.path.join(savedir,"n{:05d}_d{:2.1f}_seed{:010d}".format(n,d,seed))
    data=pd.DataFrame(columns = datacol)
    if v:
        print("=== measurement start ===\nn{:05d}_d{:2.1f}_seed{:010d}".format( n, d, seed))

    #device created
    device=perc.CNTDevice(n,scaling=scaling,notes='run',l=l,seed=seed,onoffmap=onoffmap,element=element)
    if v:
        print("=== physical device made t = {:0.2}".format(timer()-start))

    # cluster information collected
    device.label_clusters()
    nclust=len(device.sticks.cluster.drop_duplicates())
    try:
        maxclust=len(max(nx.connected_components(device.graph)))
    except:
        maxclust=0
    if v:
        print("=== cluster info collected t = {:0.2}".format(timer()-start))


    # dump full device system of sticks and intersects
    if dump:
        try:
            device.save_system(fname)
        except Exception as e:
            if v:
                print("measurement failed: error saving data")
                print("ERROR for {} sticks:\n".format(n),e)
                traceback.print_exc(file=sys.stdout)
        if v:
            print("=== device dump complete t = {:0.2}".format(timer()-start))


    # perform gate voltage sweeps on all gate configurations
    if device.percolating:
        data=add_voltagemeas(device, data, vgrange=10, vgnum=3)
        if v:
            print("=== gate sweeps complete t = {:0.2}".format(timer()-start))
    # add network characteristics
    # connectivity=nx.average_node_connectivity(device.graph)
    # charpath=nx.average_shortest_path_length(device.graph)
    # clustercoeff=nx.clustering(device.graph)
    # if v:
    #     print("=== graph info complete t = {:0.2}".format(timer()-start))

    # add parameters and constants to data
    data.sticks=n
    data.scaling=scaling
    data.density=d

    data.nclust=nclust
    data.maxclust=maxclust

    # data.charpath=charpath
    # data.clustercoeff=clustercoeff
    # data.connectivity=connectivity

    data.seed=seed
    data.element=element
    data.onoffmap=onoffmap
    data.fname=fname
    if v:
        print("=== data added to frame t = {:0.2}".format(timer()-start))
    end = timer()
    runtime=end - start
    data['runtime']=runtime

    data.to_csv(fname+"_data.csv")
    if v:
        print("=== data saved t = {:0.2}".format(timer()-start))
        print("=== measurement done ===")
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
    parser = argparse.ArgumentParser( formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent("""\
            script for handling the measurement of a system
            designed to interact with the shell.
            """))
    parser.add_argument("function", type=str, choices=["multicore","singlecore"],
        help="measurement function to use: %(choices)s")
    parser.add_argument("-d",'--directory',type=str,default='')
    parser.add_argument("-t",'--test',action="store_true",default=False)
    parser.add_argument('-s','--save',action="store_true",default=False)
    parser.add_argument("--cores",type=int,default=1)
    parser.add_argument("--start",type=int)
    parser.add_argument("--step",type=int,default=0)
    parser.add_argument('-n',"--number",type=int)
    parser.add_argument("--scaling",type=int,default=5)
    parser.add_argument("--onoffmap",nargs='*',type=int,default=0)
    args = parser.parse_args()
    if args.function=="multicore":
        if args.test:
            measure_async(2,500,0,10,5,save=True)
        else:
            measure_async(args.cores, args.start, args.step, args.number,args.scaling, args.save,args.onoffmap)
    elif args.function=="singlecore":
        single_measure(args.number, args.scaling, savedir=args.directory, dump=args.save)
