import argparse, os, time,traceback,sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from network import ConductionNetwork, Resistor, Transistor
import networkx as nx
import scipy.spatial as spatial
from timeit import default_timer as timer
from datetime import datetime



class StickCollection(object):
    def __init__(self, n=2, l='exp', pm=0.135, scaling=1, fname='', directory='data', notes=''):
        self.scaling=scaling
        self.n=n
        self.pm=pm
        self.l=l
        self.notes=notes
        self.directory=directory
        self.percolating=False
        if not(fname):
            self.sticks, self.intersects  = self.make_intersects_kdtree( self.make_sticks(n, l=l, pm=pm, scaling=scaling))
            self.make_cnet()
            self.fname=self.make_fname()
        else:
            self.load_system(os.path.join(directory,fname))
    def check_intersect(self, s1,s2):
        #assert that x intervals overlap
        if max(s1[:,0])<min(s2[:,0]) and max(s1[:,1])<min(s2[:,1]):
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
        if type(l)!=str:
            stick=[np.random.rand(), np.random.rand(), np.random.rand()*2*np.pi, l/scaling,kind]
        elif l=='exp':
            stick= [np.random.rand(), np.random.rand(), np.random.rand()*2*np.pi, abs(np.random.normal(0.66,0.44))/scaling,kind]
        else:
            print('invalid L value')
        stick.append(self.get_ends(stick))
        return stick

    def make_sticks(self, n,**kwargs):
        # adds a vertical source and drain stick on left and right respectively
        source=[0.01, 0.5,np.pi/2-1e-6,100,'v']
        source.append(self.get_ends(source))
        drain=[.99, 0.5,np.pi/2-1e-6,100,'v']
        drain.append(self.get_ends(drain))
        return pd.DataFrame( [source]+[self.make_stick(**kwargs) for i in range(n)]+[drain] ,columns=[ "xc", "yc", "angle", "length",'kind', "endarray"])
        # return pd.DataFrame( [self.make_stick(**kwargs) for i in range(n)] ,columns=[ "xc", "yc", "angle", "length",'kind', "endarray"])




    def make_intersects_kdtree(self,sticks):
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
                        intersects.append([i,j,*intersection, kinds[i]+kinds[j]],)
        intersects=pd.DataFrame(intersects, columns=["stick1",'stick2','x','y','kind'])
        return sticks, intersects

    def make_trivial_sticks(self):
        source=[0.01, 0.5,np.pi/2-1e-6,1.002,'m']
        source.append(self.get_ends(source))
        drain=[.99, 0.5,np.pi/2-1e-6,1.001,'m']
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
        self.sticks, self.intersects  = self.make_intersects_kdtree(sticks)
        self.make_cnet()



    def make_graph(self):
        # only calculates the conduction through the spanning cluster of sticks
        # to avoid the creation of a singular adjacency matrix caused by
        # disconnected junctions becoming unconnected nodes in the cnet
        self.graph=nx.from_pandas_edgelist(self.intersects, source='stick1',target='stick2',edge_attr=True)
        for c in nx.connected_components(self.graph):
            if (0 in c) and (1 in c):
                self.percolating=True
                connected_graph=self.graph.subgraph(c)
        if self.percolating:
            self.ground_nodes=[1]
            self.voltage_sources=[[0,0.1]]
            self.populate_graph()
            for node in connected_graph.nodes():
                connected_graph.nodes[node]['pos'] = [self.sticks.loc[node,'xc'], self.sticks.loc[node,'yc']]
            for edge in connected_graph.edges():
                connected_graph.edges[edge]['pos'] = [connected_graph.edges[edge]['x'], connected_graph.edges[edge]['y']]
            return connected_graph
        else:
            return False,False,False

    def populate_graph(self):
        offmap={'ms':1000,'sm':1000, 'mm':1,'ss':1,'vs':1,'sv':1,'vm':1,'mv':1}
        for edge in self.graph.edges():
            self.graph.edges[edge]['component']=Transistor( off_resistance=offmap[self.graph.edges[edge]['kind']])

    def label_clusters(self):
        i=0
        for c in nx.connected_components(self.graph):
            for n in c:
                self.sticks.loc[n,'cluster']=i
            i+=1

    def make_cnet(self):
        try:
            connected_graph=self.make_graph()
            assert self.percolating, "The network is not conducting!"
            self.cnet=ConductionNetwork(connected_graph,self.ground_nodes,self.voltage_sources)
            self.cnet.set_global_gate(0)
            self.cnet.set_local_gate([0.5,0,0.16,0.667], 10)
            self.cnet.update()
        except:
            traceback.print_exc(file=sys.stdout)

    def timestamp(self):
        return datetime.now().strftime('%y-%m-%d_%H%M%S_%f')

    def make_fname(self):
        self.notes="{}_{}sticks_{}x{}um_{}L_{}".format( self.timestamp(),self.n,self.scaling,self.scaling,self.l,self.notes)
        fname=os.path.join(self.directory,self.notes)
        return fname

    def save_system(self):
        #saves the sticks DataFrame
        self.sticks.to_csv(self.fname+'_sticks.csv')
        #saves the intersects dataframe
        self.intersects.to_csv(self.fname+'_intersects.csv')
        #save the graph object
        # nx.write_yaml(self.graph,self.fname+'_graph.yaml')

    def load_system(self,fname,network=True):
        print("loading sticks")
        self.sticks=pd.read_csv(fname+'_sticks.csv',index_col=0)
        print("recalculating endpoints")
        self.sticks.endarray=[self.get_ends(row) for row in self.sticks.values]
        print("loading intersects")
        self.intersects=pd.read_csv(fname+'_intersects.csv',index_col=0)

        if network:
            print("making cnet")
            self.make_cnet()

    def show_system(self,clustering=True, junctions=True, conduction=True, show=True, save=False):
        fig = plt.figure(figsize=(15,5))
        axes=[fig.add_subplot(1,3,i+1) for i in range(3)]
        self.label_clusters()
        if clustering:
            self.show_clusters(ax=axes[0])
            axes[0].set_title("Cluster labeling")
        if junctions:
            self.show_sticks(sticks=self.sticks,intersects=self.intersects, ax=axes[1])
            axes[1].set_title("ms labeling and junctions")
        if conduction and self.percolating:
            self.cnet.show_device(ax=axes[2])
            axes[2].set_title("Conduction Graph")
        for ax in axes:
            ax.set_xticklabels(['']+['{:.1f}'.format(i/5*self.scaling) for i in range(6)])
            ax.set_yticklabels(['']+['{:.1f}'.format(i/5*self.scaling) for i in range(6)])
            ax.set_ylabel("$\mu m$")
            ax.set_xlabel("$\mu m$")
        if save:
            plt.savefig(self.fname+'_'+save+'_plots.png')
        if show:
            plt.show()

    def show_clusters(self,intersects=True,ax=False):
        sticks=self.sticks
        if not(ax):
            fig=plt.figure(figsize=(5,5))
            ax=fig.add_subplot(111)
        colors=np.append([[0,0,0]], np.random.rand(len(sticks),3), axis=0)
        colorpattern=[colors[i] for i in sticks.cluster.values]
        collection=LineCollection(sticks.endarray.values,linewidth=0.5,colors=colorpattern)
        ax.add_collection(collection)
        # if intersects:
        #     ax.scatter(self.intersects.x, self.intersects.y, c="r", s=30, linewidth=0.8, marker="x")
        ax.set_xlim((-0.02,1.02))
        ax.set_ylim((-0.02,1.02))
        # ax.set_title("$n_{{clusters}}$={}\nConnected={}".format(len(self.sticks.cluster.drop_duplicates()),str(self.percolating)))
        if not(ax):
            plt.show()
    def show_sticks(self,sticks,intersects,ax=False):
        if not(ax):
            fig=plt.figure(figsize=(5,5))
            ax=fig.add_subplot(111)
        stick_cmap={'s':'b','m':'r','v':'k'}
        stick_colors=[stick_cmap[i] for i in sticks.kind]
        collection=LineCollection(sticks.endarray.values,linewidth=0.5,colors=stick_colors)
        ax.add_collection(collection)
        isect_cmap={'ms':'g','sm':'g', 'mm':'k','ss':'k','vs':'k','sv':'k','vm':'k','mv':'k'}
        isect_colors=[isect_cmap[i] for i in self.intersects.kind]
        ax.scatter(intersects.x, intersects.y, c=isect_colors, s=20, linewidth=1, marker="x")
        ax.set_xlim((-0.02,1.02))
        ax.set_ylim((-0.02,1.02))
        if not(ax):
            plt.show()






if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-n',"--number",type=int)
    parser.add_argument("--pm",type=float,default=0.135)
    parser.add_argument("--length",default='exp')
    parser.add_argument("--scaling",type=float,default=5)
    parser.add_argument("-t", "--test", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--show", action="store_true",default=False)
    parser.add_argument('-s','--save', action="store_true",default=False)
    parser.add_argument("--time",default=0)
    parser.add_argument('--fname',type=str,default='')
    args = parser.parse_args()
    if args.time:
        if args.time== 'series':
            for i in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]:
                avtime=time_collection(i**2*16,1,i)
        elif type(args.time)==int:
            avtime=time_collection(args.number,args.time,args.scaling)
            print(avtime)


    elif args.test:
        collection=StickCollection(args.number,l=args.length,pm=args.pm,scaling=args.scaling)
        collection.make_trivial_sticks()

        collection.show_system()
    else:
        collection=StickCollection(n=args.number,l=args.length,pm=args.pm,scaling=args.scaling,fname=args.fname)
        if args.show:
            collection.show_system(save=args.save)
        if args.save:
            collection.save_system()

        # print(len(collection.sticks.cluster.drop_duplicates()))
