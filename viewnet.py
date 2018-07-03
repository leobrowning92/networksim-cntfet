import argparse, os, time,traceback,sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.patches as patches
import networkx as nx
from percolation import StickCollection

class Netviewer(StickCollection):
    def __init__(self,**kwargs):
        super(Netviewer, self).__init__(**kwargs)
        self.label_clusters()


    # from percolation
    def show_system(self,clustering=True, junctions=True, conduction=True, show=True, save=False,figsize=(6.3,6.3)):
        fig = plt.figure(figsize=figsize)
        axes=[fig.add_subplot(2,2,i+1) for i in range(4)]
        self.label_clusters()
        if clustering:
            self.show_sticks(ax=axes[0],junctions=False, clusters=True)
            axes[0].set_title("Cluster labeling")
        if junctions:
            self.show_sticks(ax=axes[1],junctions=True, clusters=False)
            axes[1].set_title("ms labeling and junctions")
        if conduction and self.percolating:
            self.plot_voltages(axes[2])
            self.plot_regions(axes[2])
            self.plot_currents(axes[3])
            self.plot_regions(axes[3])
            axes[2].set_title("Voltage")
            axes[3].set_title("Current")
        for ax in axes:
            ax.set_xticklabels(['']+['{:.1f}'.format(i/5*self.scaling) for i in range(6)])
            ax.set_yticklabels(['']+['{:.1f}'.format(i/5*self.scaling) for i in range(6)])
            ax.set_ylabel("$\mu m$")
            ax.set_xlabel("$\mu m$")
        plt.tight_layout()
        if save:
            plt.savefig(self.fname+'_'+save+'_plots.png')
        if show:
            plt.show()
        pass



    def show_sticks(self,ax=False, clusters=False, junctions=True):
        sticks=self.sticks
        intersects=self.intersects
        if not(ax):
            fig = plt.figure(figsize=(5,5),facecolor='white')
            ax=fig.add_subplot(111)
        if clusters:
            colors=np.append([[0,0,0]], np.random.rand(len(sticks),3), axis=0)
            stick_colors=[colors[i] for i in sticks.cluster.values]
        else:
            stick_cmap={'s':'b','m':'r','v':'k'}
            stick_colors=[stick_cmap[i] for i in sticks.kind]
        collection=LineCollection(sticks.endarray.values,linewidth=0.5,colors=stick_colors)
        ax.add_collection(collection)
        if junctions:
            isect_cmap={'ms':'g','sm':'g', 'mm':'k','ss':'k','vs':'k','sv':'k','vm':'k','mv':'k'}
            isect_colors=[isect_cmap[i] for i in self.intersects.kind]
            ax.scatter(intersects.x, intersects.y, c=isect_colors, s=20, linewidth=0.5, marker="o",alpha=0.5)
        ax.set_xlim((-0.02,1.02))
        ax.set_ylim((-0.02,1.02))
        if not(ax):
            plt.show()
        pass

    # from network
    def show_cnet(self,ax=False,v=False, current = True, voltage=True):
        if not(ax):
            fig = plt.figure(figsize=(5,5),facecolor='white')
            ax=plt.subplot(111)
        self.plot_cnet(ax,v=v, current = current, voltage=voltage)
        if not(ax):
            plt.show()
        pass

    def show_device(self,v=False,ax=False,current = True, voltage=True,legend=False):
        if not(ax):
            fig = plt.figure(figsize=(5,5),facecolor='white')
            ax=plt.subplot(111)
        self.plot_cnet(ax,v=v, current = current, voltage=voltage)
        self.plot_regions(ax)
        if legend:
            ax.legend()
        if not(ax):
            plt.show()
        pass

    def plot_regions(self,ax):
        for a in self.cnet.gate_areas:
            ax.add_patch(patches.Rectangle( (a[0][0]-a[0][2]/2,a[0][1]-a[0][3]/2), a[0][2],a[0][3], edgecolor='b', fill=False, label="Local $V_G$ = {} V".format(a[1])))
        ax.add_patch(patches.Rectangle( (-0.02,.48), 0.04,0.04, edgecolor='r', fill=False,label="Source = {} V".format(self.cnet.vds)))
        ax.add_patch(patches.Rectangle( (.98,0.48), 0.04,0.04, edgecolor='k',
        fill=False, label="GND = 0 V"))
        pass

    def plot_cnet(self,ax1,v=False,current=True,voltage=True):
        pos={k:self.cnet.graph.nodes[k]['pos'] for k in self.cnet.graph.nodes}
        # for i in range(self.network_rows):
        #     for j in range(self.network_columns):
        #         pos[(i,j)]=j,i
        edges,currents = zip(*nx.get_edge_attributes(self.cnet.graph,'current').items())

        nodes,voltages = zip(*nx.get_node_attributes(self.cnet.graph,'voltage').items())
        if voltage:
            nodes=nx.draw_networkx_nodes(self.cnet.graph, pos, width=2,nodelist=nodes, node_color=voltages,  cmap=plt.get_cmap('YlOrRd'), node_size=30, ax=ax1,edgecolors='k')
        else:
            nodes=nx.draw_networkx_nodes(self.cnet.graph, pos, width=2,nodelist=nodes, node_color='r', node_size=30, ax=ax1)

        if current:
            edges=nx.draw_networkx_edges(self.cnet.graph, pos, width=2, edgelist=edges, edge_color=currents,  edge_cmap=plt.get_cmap('YlGn'), ax=ax1)
        else:
            edges=nx.draw_networkx_edges(self.cnet.graph, pos, width=2, edgelist=edges, edge_color='b', ax=ax1)

        if v:
            nodelabels=nx.get_node_attributes(self.graph,'voltage')
            nx.draw_networkx_labels(self.graph,pos,labels={k:'{}\n      {:.1e}V'.format(k,nodelabels[k]) for k in nodelabels})

            edgecurrents=nx.get_edge_attributes(self.graph,'current')
            edgeresistance=nx.get_edge_attributes(self.graph,'resistance')
            nx.draw_networkx_edge_labels(self.graph,pos, edge_labels={k:'{:.1e}A\n{:.1e}$\Omega$'.format(edgecurrents[k], edgeresistance[k]) for k in edgecurrents})
        pass

    def plot_currents(self,ax1,v=False):
        pos={k:self.cnet.graph.nodes[k]['pos'] for k in self.cnet.graph.nodes}

        edges,currents = zip(*nx.get_edge_attributes(self.cnet.graph,'current').items())

        nodes,voltages = zip(*nx.get_node_attributes(self.cnet.graph,'voltage').items())

        edges=nx.draw_networkx_edges(self.cnet.graph, pos, width=2, edgelist=edges, edge_color=currents,  edge_cmap=plt.get_cmap('YlOrRd'), ax=ax1)

        nodes=nx.draw_networkx_nodes(self.cnet.graph, pos, width=2,nodelist=nodes, node_color='k', node_size=2, ax=ax1)
        pass



    def plot_voltages(self,ax1,v=False):
        pos={k:self.cnet.graph.nodes[k]['pos'] for k in self.cnet.graph.nodes}

        edges,currents = zip(*nx.get_edge_attributes(self.cnet.graph,'current').items())

        nodes,voltages = zip(*nx.get_node_attributes(self.cnet.graph,'voltage').items())

        nodes=nx.draw_networkx_nodes(self.cnet.graph, pos, width=2,nodelist=nodes, node_color=voltages,  cmap=plt.get_cmap('YlOrRd'), node_size=30, ax=ax1,edgecolors='k')

        edges=nx.draw_networkx_edges(self.cnet.graph, pos, width=0.5, edgelist=edges, edge_color='k', ax=ax1)
        pass

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
