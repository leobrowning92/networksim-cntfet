import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

def check_intersect(s1,s2):
    #assert that x intervals overlap
    if max(s1[:,0])<min(s2[:,0]):
        return False # intervals do not overlap
    #gradients
    m1=(s1[0,1]-s1[1,1])/(s1[0,0]-s1[1,0])
    m2=(s2[0,1]-s2[1,1])/(s2[0,0]-s2[1,0])
    #intercepts
    b1=s1[0,1]-m1*s1[0,0]
    b2=s2[0,1]-m2*s2[0,0]
    if m1==m2:
        return False #lines are parallel
    #xi,yi on both lines
    xi=(b2-b1)/(m1-m2)
    yi=(b2*m1-b1*m2)/(m1-m2)
    if min(s1[:,0])<xi<max(s1[:,0]) and min(s2[:,0])<xi<max(s2[:,0]):
        return [xi,yi]
    else:
        return False
def get_ends(row):
    xc,yc,angle,length = row[1],row[2],row[3],row[4]
    x1=xc-length/2*np.cos(angle)
    x2=xc+length/2*np.cos(angle)
    y1=yc+length/2*np.sin(angle)
    y2=yc-length/2*np.sin(angle)
    return np.array( [ [x1,y1],[x2,y2] ] )
def make_stick(n,l=None):
    """makes a stick with [n, xc, yc, angle, length, endarray]
    the end array is of the form [ [x1,y1],[x2,y2] ]"""
    if l:
        stick=[n,np.random.rand(), np.random.rand(), np.random.rand()*2*np.pi, l]
    else:
        stick= [n,np.random.rand(), np.random.rand(), np.random.rand()*2*np.pi, abs(np.random.normal(0.66,0.44))/60]
    stick.append(get_ends(stick))
    return stick

def make_sticks(n,**kwargs):
    return pd.DataFrame( [make_stick(i,**kwargs) for i in range(n)] ,columns=["n", "xc", "yc", "angle", "length", "endarray"])

def make_clusters(sticks):
    # initializes all sticks in their own cluster
    sticks['cluster']=sticks['n']

    # this section might be emberassingly parallel, but it would have to be
    # addapted to add the cluster number of both intersecting sticks to both.
    # then at the end the final cluster is the minimum of all the cluster
    # intersects?
    for i in range(len(sticks)):
        for j in range(i,len(sticks)):
            if check_intersect(sticks.iloc[i].endarray,sticks.iloc[j].endarray):
                sticks.loc[sticks.cluster==sticks.loc[j,'cluster'],'cluster'] = sticks.loc[i,'cluster']
    return sticks

def show_sticks(sticks):
    fig=plt.figure(figsize=(5,5))
    ax=fig.add_subplot(111)
    colors=np.random.rand(len(sticks),3)
    colorpattern=[colors[i] for i in sticks.cluster.values]
    collection=LineCollection(sticks.endarray.values,linewidth=0.5,colors=colorpattern)
    ax.add_collection(collection)
    plt.show()

# show_sticks(make_sticks(10,l=1))
sticks=make_clusters(make_sticks(50,l=.5))
print(len(sticks.cluster.drop_duplicates()))
show_sticks(sticks)
