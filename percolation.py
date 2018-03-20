import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

class StickCollection(object):
    def __init__(self,n,l,sticks=None):
        if sticks:
            self.sticks=self.make_clusters(sticks)
        self.sticks, self.intersects  = self.make_clusters(self.make_sticks(n,l=l))

    def check_intersect(self, s1,s2):
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
    def get_ends(self, row):
        xc,yc,angle,length = row[0],row[1],row[2],row[3]
        x1=xc-length/2*np.cos(angle)
        x2=xc+length/2*np.cos(angle)
        y1=yc+length/2*np.sin(angle)
        y2=yc-length/2*np.sin(angle)
        return np.array([ [x1,y1],[x2,y2] ])

    def make_stick(self,l=None,kind='s'):
        """makes a stick with [xc, yc, angle, length, kind, endarray]
        the end array is of the form [ [x1,y1],[x2,y2] ]"""
        if l:
            stick=[np.random.rand(), np.random.rand(), np.random.rand()*2*np.pi, l,kind]
        else:
            stick= [np.random.rand(), np.random.rand(), np.random.rand()*2*np.pi, abs(np.random.normal(0.66,0.44))/60,kind]
        stick.append(self.get_ends(stick))
        return stick

    def make_sticks(self, n,**kwargs):
        # adds a vertical source and drain stick on left and right respectively
        source=[0.01, 0.5,np.pi/2-1e-6,1,'v']
        source.append(self.get_ends(source))
        drain=[.99, 0.5,np.pi/2-1e-6,1,'g']
        drain.append(self.get_ends(drain))
        return pd.DataFrame( [source]+[self.make_stick(**kwargs) for i in range(n)]+[drain] ,columns=[ "xc", "yc", "angle", "length",'kind', "endarray"])

    def make_clusters(self, sticks):
        # initializes all sticks in their own cluster
        sticks['cluster']=sticks.index
        intersects=[]
        # this section might be emberassingly parallel, but it would have to be
        # addapted to add the cluster number of both intersecting sticks to both.
        # then at the end the final cluster is the minimum of all the cluster
        # intersects?
        for i in range(len(sticks)):
            for j in range(i,len(sticks)):
                intersection=self.check_intersect(sticks.iloc[i].endarray, sticks.iloc[j].endarray)
                if intersection and 0<=intersection[0]<=1 and 0<=intersection[1]<=1:
                    sticks.loc[sticks.cluster==sticks.loc[j,'cluster'],'cluster'] = sticks.loc[i,'cluster']
                    intersects.append([i,j,*intersection, sticks.iloc[i].kind+sticks.iloc[j].kind])
        return sticks,pd.DataFrame(intersects, columns=["stick1",'stick2','x','y','kind'])

    def show_sticks(self,intersects=True):
        sticks=self.sticks
        fig=plt.figure(figsize=(5,5))
        ax=fig.add_subplot(111)
        colors=np.random.rand(len(sticks),3)
        colorpattern=[colors[i] for i in sticks.cluster.values]
        collection=LineCollection(sticks.endarray.values,linewidth=0.5,colors=colorpattern)
        ax.add_collection(collection)
        if intersects:
            ax.scatter(self.intersects.x, self.intersects.y, c="r", s=30, linewidth=0.8, marker="x")
        plt.show()

# show_sticks(make_sticks(10,l=1))
collection=StickCollection(50,l=0.5)
print(len(collection.sticks.cluster.drop_duplicates()))
collection.show_sticks()
