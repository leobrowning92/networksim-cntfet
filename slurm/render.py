import sys
sys.path.insert(0, "/home/leo/gitrepos/networksim-cntfet")
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import seaborn as sns
import networkx as nx
import numpy as np

import matplotlib.pyplot as plt
import glob,os
import viewnet
from timeit import default_timer as timer
from multiprocessing import Pool



scriptstart=timer()
data=pd.read_csv("alldata.csv")
fnames=data[data.current!=0].fname.drop_duplicates().values


def checkdir(directoryname):
    if os.path.isdir(directoryname) == False:
        os.system("mkdir " + directoryname)







def render_gatesweeps(nv,gatetype,plottype,directory):
    for vg in range(-10,11,2):
        nv.gate(vg,gatetype)
        nv.plot_contour(plottype,show=False, save="{}/{}_{}{}{:04.1f}_contour".format(directory,vg+10,gatetype,plottype,vg))


for fname in fnames:
    filestart=timer()
    print("start: ",fname)
    nv=viewnet.Netviewer(directory="data/", fname=fname)
    print("{:08.1f} s load {}".format(timer()-filestart,fname),)
    checkdir(fname)
    gstart=timer()
    pool=Pool(1)
    for plottype in ["voltage","current"]:
        results=[]
        for gatetype in ['back','partial','total']:
            directory=os.path.join(fname,gatetype+"_"+plottype)
            checkdir(directory)
            results= results+[pool.apply_async(render_gatesweeps, args=(nv,gatetype,plottype,directory))]
        print(len(results), "jobs running")
        output=[res.get() for res in results]
    print("{:08.1f} s gate {}".format(timer()-gstart,fname),)
print("{:08.1f} s script {}".format(timer()-scriptstart,fname),)
