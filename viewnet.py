import argparse, os, time,traceback,sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.patches as patches
import matplotlib.tri as tri
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import networkx as nx
from percolation import StickCollection ,CNTDevice

def open_data(path):
    df=pd.read_csv(path)
    for device in df.seed.drop_duplicates():
        if len(df[df.seed==device])==1:
            pass
        else:
            for gatetype in ['back','partial','total']:
                try:
                    singlechipmask=(df.seed==device)&(df.gate==gatetype)
                    on=df.loc[singlechipmask&(df.gatevoltage==-10),'current'].values[0]
                    off=df.loc[singlechipmask&(df.gatevoltage==10),'current'].values[0]
                    df.loc[singlechipmask,'onoff']=on/off
                except:
                    print ("ERROR calculating onoff for device seed : {}".format(device))
    df['relative_maxclust']=df.maxclust/df.sticks
    df['logonoff']=np.log10(df.onoff)
    df = df[['seed', 'sticks', 'scaling', 'density', 'current', 'gatevoltage', 'gate', 'onoff','logonoff', 'nclust', 'maxclust', 'relative_maxclust', 'fname', 'onoffmap', 'runtime', 'element']]

    return df

class Netviewer(CNTDevice):
    def __init__(self,**kwargs):
        super(Netviewer, self).__init__(**kwargs)
        self.label_clusters()


    # from percolation
    def show_system(self,clustering=True, junctions=True, conduction=True, show=True, save=False,figsize=(6.3,4)):
        fig, axes = plt.subplots(nrows=2,ncols=3,figsize=figsize, sharex=True, sharey=True, gridspec_kw={'wspace':0.1, 'hspace':0.05})
        axes=axes.flat
        self.label_clusters()
        if clustering:
            self.show_sticks(ax=axes[0],junctions=False, clusters=True)
            axes[0].set_title("Sticks")
        if junctions:
            self.show_sticks(ax=axes[3],junctions=True, clusters=False)
            # axes[3].set_title("ms labeling and junctions")
        try:
            if conduction and self.percolating:
                self.plot_voltages(axes[1])
                self.plot_regions(axes[1])
                self.plot_currents(axes[2])
                self.plot_regions(axes[2])
                axes[1].set_title("Voltage")
                axes[2].set_title("Current")
                self.plot_contour('voltage',ax=axes[4])
                self.plot_contour('current',ax=axes[5])

        except Exception as e:
            print(e)
            pass
        for ax in axes:
            ax.tick_params(axis='both',direction='in',right=True, top =True)
        for ax in [axes[0],axes[3]]:
            ax.set_yticks([0,0.2,0.4,0.6,0.8,1])
            ax.set_yticklabels(['{:.0f}'.format(i/5*self.scaling) for i in range(6)])
            ax.set_ylabel("$\mu m$")
        for ax in [axes[3],axes[4],axes[5]]:
            ax.set_xticks([0,0.2,0.4,0.6,0.8,1])
            ax.set_xticklabels(['{:.0f}'.format(i/5*self.scaling) for i in range(6)])
            ax.set_xlabel("$\mu m$")
        plt.tight_layout()
        print(save)
        if save:
            print("saving system at {}".format(self.fname))
            plt.savefig(self.fname+'_plots.png')
            plt.savefig(self.fname+'_plots.pdf')
        if show:
            plt.show()
        return fig, axes

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
            isect_cmap={'ms':'g','sm':'g', 'mm':'None','ss':'None','vs':'None','sv':' ','vm':'None','mv':'None'}
            isect_colors=[isect_cmap[i] for i in self.intersects.kind]
            ax.scatter(intersects.x, intersects.y, edgecolors=isect_colors, facecolors='None', s=20, linewidth=1, marker="o",alpha=0.8)
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
            edges=nx.draw_networkx_edges(self.cnet.graph, pos, width=1, edgelist=edges, edge_color=currents,  edge_cmap=plt.get_cmap('YlGn'), ax=ax1)
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

        nodes=nx.draw_networkx_nodes(self.cnet.graph, pos, width=1,nodelist=nodes, node_color='k', node_size=1, ax=ax1)
        pass

    def plot_voltages(self,ax1,v=False):
        pos={k:self.cnet.graph.nodes[k]['pos'] for k in self.cnet.graph.nodes}

        edges,currents = zip(*nx.get_edge_attributes(self.cnet.graph,'current').items())

        nodes,voltages = zip(*nx.get_node_attributes(self.cnet.graph,'voltage').items())

        nodes=nx.draw_networkx_nodes(self.cnet.graph, pos, width=2,nodelist=nodes, node_color=voltages,  cmap=plt.get_cmap('YlOrRd'), node_size=30, ax=ax1,edgecolors='k')

        edges=nx.draw_networkx_edges(self.cnet.graph, pos, width=0.5, edgelist=edges, edge_color='k', ax=ax1)
        pass

    def plot_contour(self,value,scale=True,ax=False,show=False,save=False,colormap="YlOrRd"):
        if value=='current':
            z=np.array(list(nx.get_edge_attributes(self.cnet.graph,value).values()))
            pos=np.array(list(nx.get_edge_attributes(self.cnet.graph,'pos').values()))
            label= 'I'
        if value=='voltage':
            z=np.array(list(nx.get_node_attributes(self.cnet.graph,value).values()))
            pos=np.array(list(nx.get_node_attributes(self.cnet.graph,'pos').values()))
            label= 'V'
        x=pos[:,0]
        y=pos[:,1]


        #creat grid values
        xi = np.linspace(0,1,100)
        yi = np.linspace(0,1,100)

        # Perform linear interpolation of the data (x,y)
        # on a grid defined by (xi,yi)
        triang = tri.Triangulation(x, y)
        interpolator = tri.LinearTriInterpolator(triang, z)
        Xi, Yi = np.meshgrid(xi, yi)
        zi = interpolator(Xi, Yi)

        if not(ax):
            fig, ax = plt.subplots(1,figsize=(6.3,6.3))
            ax.set_title("{} gate = {:04.1f} V".format(self.gatetype,float(self.gatevoltage)))
        # ax.contour(xi, yi, zi, 14, linewidths=0.5, colors='k')
        cntr1 = ax.contourf(xi, yi, zi, 8, cmap=colormap,alpha=0.7)
        # if not(ax):
            # fig.colorbar(cntr1, ax=ax,label=value)
        #     ax.plot(x, y, 'wo', ms=3)
            # ax.axis((0,1,0,1))
        if save or show:
            ax.set_yticks([0,0.2,0.4,0.6,0.8,1])
            ax.set_yticklabels(['{:.0f}'.format(i/5*self.scaling) for i in range(6)])
            ax.set_xticks([0,0.2,0.4,0.6,0.8,1])
            ax.set_xticklabels(['{:.0f}'.format(i/5*self.scaling) for i in range(6)])
            ax.set_ylabel("$\mu m$")
            ax.set_xlabel("$\mu m$")


        if scale:
            axins = inset_axes(ax, width="40%",  height="5%", loc=9, bbox_to_anchor=(0, 0, 1, 1), bbox_transform=ax.transAxes, borderpad=0)
            values=[0,zi.max()]
            cbar=plt.colorbar(cntr1, cax=axins,ticks=values,format='%.0e', orientation='horizontal')
            # cbar.set_ticks([cmin+(0.1*range),cmax-(0.1*range)])
            cbar.set_ticklabels(["{:.1f}".format(values[0]),"{:.0e}".format(values[1])])
            cbar.set_label(label,labelpad=-10)
        if show:
            plt.show()
        if ax and save:
            plt.tight_layout()
            plt.savefig("{}.png".format(save))
            plt.savefig("{}.pdf".format(save))
            plt.close()
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
