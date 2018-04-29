import argparse, os, time,traceback,sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
from percolation import StickCollection

class Netviewer(StickCollection):
    def __init__(self,fname,directory='data',scaling=5):
        StickCollection.__init__(self,fname=fname,directory=directory,scaling=scaling)
    # from network
    def show_network(self,v=False):

        fig = plt.figure(figsize=(10,10),facecolor='white')
        ax1=plt.subplot(111)
        self.plot_network(ax1,v=v)
        plt.show()
    def show_device(self,v=False,ax=False):
        if not(ax):
            fig = plt.figure(figsize=(10,10),facecolor='white')
            ax=plt.subplot(111)
        self.plot_network(ax,v=v)
        self.plot_regions(ax)

        # ax.legend()
        if not(ax):
            plt.show()
    def plot_regions(self,ax):
        for a in self.cnet.gate_areas:
            ax.add_patch(patches.Rectangle( (a[0][0]-a[0][2]/2,a[0][1]-a[0][3]/2), a[0][2],a[0][3], edgecolor='b', fill=False, label="Local $V_G$ = {} V".format(a[1])))
        ax.add_patch(patches.Rectangle( (-0.02,.48), 0.04,0.04, edgecolor='r', fill=False,label="Source = {} V".format(self.cnet.vds)))
        ax.add_patch(patches.Rectangle( (.98,0.48), 0.04,0.04, edgecolor='k',
        fill=False, label="GND = 0 V"))
    def plot_network(self,ax1,v=False):
        pos={k:self.cnet.graph.nodes[k]['pos'] for k in self.cnet.graph.nodes}
        # for i in range(self.network_rows):
        #     for j in range(self.network_columns):
        #         pos[(i,j)]=j,i
        edges,currents = zip(*nx.get_edge_attributes(self.cnet.graph,'current').items())

        nodes,voltages = zip(*nx.get_node_attributes(self.cnet.graph,'voltage').items())
        nodes=nx.draw_networkx_nodes(self.cnet.graph, pos, width=2,nodelist=nodes, node_color=voltages,  cmap=plt.get_cmap('YlOrRd'), node_size=30, ax=ax1)
        edges=nx.draw_networkx_edges(self.cnet.graph, pos, width=2, edgelist=edges, edge_color=currents,  edge_cmap=plt.get_cmap('YlGn'), ax=ax1)\

        if v:
            nodelabels=nx.get_node_attributes(self.graph,'voltage')
            nx.draw_networkx_labels(self.graph,pos,labels={k:'{}\n      {:.1e}V'.format(k,nodelabels[k]) for k in nodelabels})
            edgecurrents=nx.get_edge_attributes(self.graph,'current')
            edgeresistance=nx.get_edge_attributes(self.graph,'resistance')
            nx.draw_networkx_edge_labels(self.graph,pos, edge_labels={k:'{:.1e}A\n{:.1e}$\Omega$'.format(edgecurrents[k], edgeresistance[k]) for k in edgecurrents})

    # from percolation
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
            self.show_device(ax=axes[2])
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
    parser.add_argument("-t", "--test", action="store_true")
    parser.add_argument('--fname',type=str,default='')
    args = parser.parse_args()

    if args.test:
        collection=StickCollection(500)
        collection.save_system()
        netview=Netviewer(fname=(os.path.basename(collection.fname)))
        netview.show_system()
