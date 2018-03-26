import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from network import ConductionNetwork, Resistor, Transistor
import networkx as nx
import scipy.spatial as spatial
from timeit import default_timer as timer



class StickCollection(object):
    def __init__(self,n,l,sticks=None,pm=0,scaling=1):
        if sticks:
            self.sticks, self.intersects = self.make_clusters(sticks)
        self.sticks, self.intersects  = self.make_clusters_kdtree(self.make_sticks(n,l=l,pm=pm,scaling=scaling))
        self.make_cnet()
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
    def get_distance(self,p1,p2):
        return np.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)
    def get_ends(self, row):
        xc,yc,angle,length = row[0],row[1],row[2],row[3]
        x1=xc-length/2*np.cos(angle)
        x2=xc+length/2*np.cos(angle)
        y1=yc+length/2*np.sin(angle)
        y2=yc-length/2*np.sin(angle)
        return np.array([ [x1,y1],[x2,y2] ])

    def make_stick(self,l=None,kind='s',pm=0,scaling=1):
        """makes a stick with [xc, yc, angle, length, kind, endarray]
        the end array is of the form [ [x1,y1],[x2,y2] ]"""
        if np.random.rand()<=pm:
            kind='m'
        if l:
            stick=[np.random.rand(), np.random.rand(), np.random.rand()*2*np.pi, l/scaling,kind]
        else:
            stick= [np.random.rand(), np.random.rand(), np.random.rand()*2*np.pi, abs(np.random.normal(0.66,0.44))/scaling,kind]
        stick.append(self.get_ends(stick))
        return stick

    def make_sticks(self, n,**kwargs):
        # adds a vertical source and drain stick on left and right respectively
        source=[0.01, 0.5,np.pi/2-1e-6,1,'v']
        source.append(self.get_ends(source))
        drain=[.99, 0.5,np.pi/2-1e-6,1,'g']
        drain.append(self.get_ends(drain))
        return pd.DataFrame( [source]+[self.make_stick(**kwargs) for i in range(n)]+[drain] ,columns=[ "xc", "yc", "angle", "length",'kind', "endarray"])
        # return pd.DataFrame( [self.make_stick(**kwargs) for i in range(n)] ,columns=[ "xc", "yc", "angle", "length",'kind', "endarray"])


    def make_clusters(self, sticks):
        # initializes all sticks in their own cluster
        sticks['cluster']=sticks.index
        intersects=[]
        for i in range(len(sticks)):
            for j in range(i,len(sticks)):
                intersection=self.check_intersect(sticks.iloc[i].endarray, sticks.iloc[j].endarray)
                if intersection and 0<=intersection[0]<=1 and 0<=intersection[1]<=1:
                    sticks.loc[sticks.cluster==sticks.loc[j,'cluster'],'cluster'] = sticks.loc[i,'cluster']
                    intersects.append([i,j,*intersection, sticks.iloc[i].kind+sticks.iloc[j].kind],)
        self.percolating=sticks.loc[0,"cluster"]==sticks.loc[len(sticks)-1,"cluster"]
        intersects=pd.DataFrame(intersects, columns=["stick1",'stick2','x','y','kind'])
        intersects['cluster']=intersects['stick1'].apply(lambda x: sticks.iloc[x].cluster)
        return sticks, intersects

    def make_clusters_kdtree(self,sticks):
        sticks['cluster']=sticks.index
        sticks.sort_values('length',inplace=True,ascending=False)
        sticks.reset_index(drop=True,inplace=True)
        intersects=[]

        X=sticks.loc[:,'xc':'yc'].values
        endpoints=sticks.endarray.values
        kinds=sticks.kind.values
        lengths=sticks.length.values
        tree=spatial.KDTree(X)
        for i in range(len(sticks)):
            neighbors = tree.query_ball_point(X[i],lengths[i])
            for j in neighbors:
                # ensures no double counting and self counting
                if i<j:
                    intersection=self.check_intersect(endpoints[i],endpoints[j])
                    if intersection and 0<=intersection[0]<=1 and 0<=intersection[1]<=1:
                        sticks.loc[sticks.cluster==sticks.loc[j,'cluster'],'cluster'] = sticks.loc[i,'cluster']
                        intersects.append([i,j,*intersection, kinds[i]+kinds[j]],)
        self.percolating=sticks.loc[0,"cluster"]==sticks.loc[1,"cluster"]
        intersects=pd.DataFrame(intersects, columns=["stick1",'stick2','x','y','kind'])
        intersects['cluster']=intersects['stick1'].apply(lambda x: sticks.iloc[x].cluster)
        return sticks, intersects

    def make_trivial_sticks(self):
        source=[0.01, 0.5,np.pi/2-1e-6,1,'v']
        source.append(self.get_ends(source))
        drain=[.99, 0.5,np.pi/2-1e-6,1,'g']
        drain.append(self.get_ends(drain))
        st1=[0.3, 0.5,np.pi/4,1,'s']
        st1.append(self.get_ends(st1))
        st2=[0.7, 0.5,-np.pi/4,1,'s']
        st2.append(self.get_ends(st2))
        st3=[0.5, 0.5,-np.pi/4,0.1,'s']
        st3.append(self.get_ends(st3))
        st4=[0.5, 0.5,np.pi/4,0.1,'s']
        st4.append(self.get_ends(st4))
        sticks=pd.DataFrame([source]+[st1]+[st2]+[st3]+[st4]+[drain],columns=[ "xc", "yc", "angle", "length",'kind', "endarray"])
        self.sticks, self.intersects  = self.make_clusters(sticks)



    def make_graph(self):
        # only calculates the conduction through the spanning cluster of sticks
        # to avoid the creation of a singular adjacency matrix caused by
        # disconnected junctions becoming unconnected nodes in the cnet
        dom_cluster=self.intersects[self.intersects.cluster==self.sticks.loc[0,'cluster']]

        self.graph=nx.from_pandas_edgelist(dom_cluster, source='stick1',target='stick2',edge_attr=True)

        self.ground_nodes=[len(self.graph)-1]
        self.voltage_sources=[[0,0.1]]
        self.populate_graph()
        for node in self.graph.nodes():
            self.graph.nodes[node]['pos'] = [self.sticks.loc[node,'xc'], self.sticks.loc[node,'yc']]
        for edge in self.graph.edges():
            self.graph.edges[edge]['pos'] = [self.graph.edges[edge]['x'], self.graph.edges[edge]['y']]
        return self.graph, self.ground_nodes, self.voltage_sources

    def populate_graph(self):
        for edge in self.graph.edges():

            self.graph.edges[edge]['component']=Transistor()


    def make_cnet(self):
        assert self.percolating, "The network is not conducting!"
        self.cnet=ConductionNetwork(*self.make_graph())
        # print(self.cnet.make_G(),'\n')
        # print(self.cnet.make_A(self.cnet.make_G()))
        self.cnet.set_global_gate(0)
        # self.cnet.set_local_gate([0.5,0,0.4,1.2], 10)
        self.cnet.update()
        # print(self.cnet.source_currents)


    def show_system(self,clustering=True,junctions=True,conduction=True):
        fig = plt.figure(figsize=(15,5))
        axes=[fig.add_subplot(1,3,i+1) for i in range(3)]
        if clustering:
            self.show_clusters(ax=axes[0])
        if junctions:
            self.show_sticks(sticks=self.sticks,intersects=self.intersects, ax=axes[1])
        if conduction and self.percolating:
            self.make_cnet()
            self.cnet.show_device(ax=axes[2])
        plt.show()
    def show_clusters(self,intersects=True,ax=False):
        sticks=self.sticks
        if not(ax):
            fig=plt.figure(figsize=(5,5))
            ax=fig.add_subplot(111)
        colors=np.random.rand(len(sticks),3)
        colorpattern=[colors[i] for i in sticks.cluster.values]
        collection=LineCollection(sticks.endarray.values,linewidth=0.5,colors=colorpattern)
        ax.add_collection(collection)
        # if intersects:
        #     ax.scatter(self.intersects.x, self.intersects.y, c="r", s=30, linewidth=0.8, marker="x")
        ax.set_xlim((-0.02,1.02))
        ax.set_ylim((-0.02,1.02))
        ax.set_title("$n_{{clusters}}$={}\nConnected={}".format(len(self.sticks.cluster.drop_duplicates()),str(self.percolating)))
        if not(ax):
            plt.show()
    def show_sticks(self,sticks,intersects,ax=False):
        if not(ax):
            fig=plt.figure(figsize=(5,5))
            ax=fig.add_subplot(111)
        stick_cmap={'s':'b','m':'r','v':'y','g':'k'}
        stick_colors=[stick_cmap[i] for i in sticks.kind]
        collection=LineCollection(sticks.endarray.values,linewidth=0.5,colors=stick_colors)
        ax.add_collection(collection)
        isect_cmap={'ms':'g','sm':'g', 'mm':'k','ss':'k', 'vs':'k','sv':'k','vm':'k', 'sg':'k','gs':'k','mg':'k','gm':'k'}
        isect_colors=[isect_cmap[i] for i in self.intersects.kind]
        ax.scatter(intersects.x, intersects.y, c=isect_colors, s=20, linewidth=1, marker="x")
        ax.set_xlim((-0.02,1.02))
        ax.set_ylim((-0.02,1.02))
        if not(ax):
            plt.show()


# show_sticks(make_sticks(10,l=1))


def time_collection(n, iterations=5,scaling=5):
    times=[]
    from timeit import default_timer as timer
    for i in range(iterations):
        start = timer()
        try:
            collection=StickCollection(n,l=0,pm=0.135,scaling=scaling)
        except Exception as e:
            print(e)
        end = timer()
        print(end - start)
        times.append(end - start)
    return sum(times)/len(times)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("number",type=int)
    parser.add_argument("--pm",type=float,default=0.135)
    parser.add_argument("--length",type=float,default=0)
    parser.add_argument("--scaling",type=float,default=5)
    parser.add_argument("-t", "--test", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--show", action="store_true",default=False)
    parser.add_argument("--time",type=int,default=0)
    args = parser.parse_args()
    if args.time:
        avtime=time_collection(args.number,args.time,args.scaling)
        print(avtime)


    else:
        collection=StickCollection(args.number,l=args.length,pm=args.pm,scaling=args.scaling)
        if args.show:
            collection.show_system()
        # print(len(collection.sticks.cluster.drop_duplicates()))
