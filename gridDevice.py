import argparse
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.axes_grid1 import make_axes_locatable
import networkx as nx

class Transistor(object):
    def __init__(self,on_resistance=1,off_resistance=100,threshold_voltage=0, gate_voltage=0):
        assert on_resistance>0 and off_resistance>0, "ERROR: a component cannot have -ve resistance"
        self.on_resistance=on_resistance
        self.off_resistance=off_resistance
        self.threshold_voltage=threshold_voltage
        self.gate_voltage=gate_voltage

    def get_conductance(self):
        if self.gate_voltage<=self.threshold_voltage:
            return 1/self.on_resistance
        else:
            return 1/self.off_resistance
class Resistor(object):
    def __init__(self,R=1):
        assert R>0, "ERROR: a component cannot have -ve resistance"
        self.resistance=R
        self.conductance=1/R
    def get_conductance(self):
        return self.conductance
class Network(object):
    def __init__(self,network_rows, network_columns, component, ground_nodes, voltage_sources,v=False):
        #network parameters
        self.network_rows=network_rows
        self.network_columns=network_columns
        self.network_size=self.network_rows*self.network_columns
        self.ground_nodes=np.array(ground_nodes)
        self.voltage_sources=np.array(voltage_sources)
        self.check_values()
        #make the grid graph
        self.graph=nx.grid_2d_graph(self.network_rows,self.network_columns)
        self.scale_graph()
        #add the components
        self.add_components(component)

    def check_values(self):
        # ensures there are some non ground/source nodes
        assert len(self.voltage_sources) + len(self.ground_nodes) < self.network_size, "there are more voltage sources and ground nodes than network nodes"
        assert len(self.ground_nodes)<self.network_size, "ground nodes out of graph index"
        assert len(self.voltage_sources[:,0])<self.network_size, "ground nodes out of graph index"

    def scale_graph(self):
        max_dimension=max(self.network_rows,self.network_columns)-1
        rn={n:(n[0]/max_dimension,n[1]/max_dimension)for n in self.graph.nodes}
        self.graph=nx.relabel_nodes(self.graph,rn)
    def add_components(self,component):
        if type(component)==list:
            assert len(component)==len(self.graph.edges), "ERROR: There is a mismatch between the number of components added and the number of graph edges"
            for i in range(len(self.graph.edges)):
                self.graph.edges[sorted(self.graph.edges)[i]]['component'] = component[i]
            self.update_conductivity()
        elif component == None:
            print("Warning: No components added. This will be needed before updating the network")
            for edge in self.graph.edges():
                self.graph.edges[edge]['component']=None
        else:
            for edge in self.graph.edges():
                self.graph.edges[edge]['component']=component()
            self.update_conductivity()

    def make_G(self):
        """Generates the adjacency matrix of the graph as a numpy array and then sets the diagonal elements as the -ve sum of the conductances that attach to it.
        """
        G=np.array(nx.to_numpy_matrix(self.graph,nodelist=sorted(self.graph.nodes()),weight='conductance'))
        for i in range(self.network_size):
            for j in range(self.network_size):
                if i==j:
                    G[i,j]=-sum(G[i])
        return G
    def make_A(self, G):
        B=np.zeros((self.network_size,len(self.voltage_sources)))
        for i in range(self.network_size):
                if i in self.voltage_sources[:,0]:
                    B[i,list(self.voltage_sources[:,0]).index(i)]=1
        D=np.zeros((len(self.voltage_sources),len(self.voltage_sources)))
        BTD=np.append(B.T,D,axis=1)
        A=np.append(np.append(G,B,axis=1),BTD,axis=0)
        A=np.delete(np.delete(A,self.ground_nodes,0),self.ground_nodes,1)
        return A
    def make_z(self):
        z = np.append(np.zeros((self.network_size-len(self.ground_nodes),1)), self.voltage_sources[:,1][:,None], axis=0)
        return np.array(z)

    def solve_mna(self):
        mna_x=np.linalg.solve(self.make_A(self.make_G()), self.make_z())
        return mna_x
    def update_conductivity(self):
        for edge in self.graph.edges:
            G=self.graph.edges[edge]['component'].get_conductance()
            self.graph.edges[edge]['conductance']=G
            self.graph.edges[edge]['resistance']=1/G
    def update_voltages(self,x):
        for i in self.ground_nodes:
            x=np.insert(x,i,0,axis=0)
        self.source_currents=x[-len(self.voltage_sources):]
        x=x[:-len(self.voltage_sources)]
        for i in range(len(self.graph.nodes)) :
            node=sorted(self.graph.nodes())[i]
            self.graph.nodes[node]['voltage']=float(x[i])
    def update_currents(self):
        for n1,n2 in self.graph.edges:
            g = float(self.graph.edges[n1,n2]['conductance'])
            dV = float(self.graph.nodes[n1]['voltage']) - float(self.graph.nodes[n2]['voltage'])
            # to include current directionality one would have to
            #replace the abs with some sort of node-node direction rules
            self.graph.edges[n1,n2]['current']= abs(g * dV)
    def update(self,show=True,v=False):
        #process mna_x to seperate out relevant components
        self.update_conductivity()
        mna_x = self.solve_mna()
        self.update_voltages(mna_x)
        self.update_currents()
        if show:
            self.show_network(v=v)
        pass

    def save_network(self,fname):
        fname =fname+"_{}x{}graph.yaml".format(self.network_rows, self.network_columns)
        nx.write_yaml(self.graph,fname)
        return fname
    def load_network(self,fname):
        self.graph=nx.read_yaml(fname)
    def show_network(self,v=False):

        fig = plt.figure(figsize=(10,10),facecolor='white')
        ax1=plt.subplot(111)
        self.plot_network(ax1,v=v)
        plt.show()
    def plot_network(self,ax1,v=False):
        pos={k:[k[1],k[0]] for k in self.graph.nodes}
        # for i in range(self.network_rows):
        #     for j in range(self.network_columns):
        #         pos[(i,j)]=j,i
        edges,currents = zip(*nx.get_edge_attributes(self.graph,'current').items())

        nodes,voltages = zip(*nx.get_node_attributes(self.graph,'voltage').items())
        nodes=nx.draw_networkx_nodes(self.graph, pos, width=2,nodelist=nodes, node_color=voltages,  cmap=plt.get_cmap('YlOrRd'), node_size=30, ax=ax1)
        edges=nx.draw_networkx_edges(self.graph, pos, width=2, edgelist=edges, edge_color=currents,  edge_cmap=plt.get_cmap('YlGn'), ax=ax1)\

        if v:
            nodelabels=nx.get_node_attributes(self.graph,'voltage')
            nx.draw_networkx_labels(self.graph,pos,labels={k:'{}\n      {:.1e}V'.format(k,nodelabels[k]) for k in nodelabels})
            edgecurrents=nx.get_edge_attributes(self.graph,'current')
            edgeresistance=nx.get_edge_attributes(self.graph,'resistance')
            nx.draw_networkx_edge_labels(self.graph,pos, edge_labels={k:'{:.1e}A\n{:.1e}$\Omega$'.format(edgecurrents[k], edgeresistance[k]) for k in edgecurrents})
        divider1 = make_axes_locatable(ax1)
        cax1 = divider1.append_axes('right', size='5%', pad=0.5)
        cax2 = divider1.append_axes('right', size='5%', pad=0.5)
        plt.colorbar(edges,label="Current A",cax=cax2)
        plt.colorbar(nodes,label="Node Voltage V",cax=cax1)
class Device(Network):
    def __init__(self,network_rows, network_columns, component, vds=1):
        ground_nodes = [(x+1)*network_columns-1 for x in range(network_rows)]
        voltage_sources = [[x*network_columns,vds] for x in range(network_rows)]
        Network.__init__(self,network_rows, network_columns, component, ground_nodes, voltage_sources)
        self.vds=vds
        self.update_location()
        self.gate_areas=[]
    def update_location(self):
        for node in self.graph.nodes:
            self.graph.nodes[node]['pos'] = [node[1], node[0]]
        for n1,n2 in self.graph.edges:
            self.graph.edges[(n1,n2)]['pos'] = [ (self.graph.nodes[n1]['pos'][0]+self.graph.nodes[n1]['pos'][0])/2 , (self.graph.nodes[n2]['pos'][1]+self.graph.nodes[n2]['pos'][1])/2 ]

    def set_global_gate(self,voltage):
        for edge in self.graph.edges:
            self.graph.edges[edge]['component'].gate_voltage=voltage
    def set_local_gate(self,area,voltage):
        for edge in self.get_local_edges(area):
            self.graph.edges[edge]['component'].gate_voltage=voltage
        self.gate_areas.append([area,voltage])
    def check_in_area(self,point,area):
        """point is in [x,y], and area is [centerx,centery,xwidth,ylength]"""
        right=area[0]+area[2]/2
        left=area[0]-area[2]/2
        top=area[1]+area[3]/2
        bottom=area[1]-area[3]/2
        if left<=point[0]<=right and bottom<=point[1]<=top:
            return True
        else:
            return False
    def get_local_edges(self,area):
        local_edges=[]
        for edge in self.graph.edges:
            if self.check_in_area(self.graph.edges[edge]['pos'],area):
                local_edges.append(edge)
            else:
                pass
        return local_edges
    def distribute_transistors(self):
        """legacy code for making an inhomogenous film of transistors"""
        components=[Transistor(1*abs(np.random.normal(1,0.5)), 10*abs(np.random.normal(1,0.5)),np.random.normal(0,0.5)) for x in range(len(tft.graph.edges))]
        self.add_components(components)
    def show_device(self,v=False):
        fig = plt.figure(figsize=(10,10),facecolor='white')
        ax1=plt.subplot(111)
        self.plot_network(ax1,v=v)
        self.plot_regions(ax1)
        ax1.legend()
        plt.show()
    def plot_regions(self,ax):
        for a in self.gate_areas:
            ax.add_patch(patches.Rectangle( (a[0][0]-a[0][2]/2,a[0][1]-a[0][3]/2), a[0][2],a[0][3], edgecolor='b', fill=False, label="Local $V_G$ = {} V".format(a[1])))
        ax.add_patch(patches.Rectangle( (-1/self.network_columns/2,-1/self.network_rows/2), 1/self.network_columns,1+1/self.network_rows, edgecolor='r', fill=False,label="Source = {} V".format(self.vds)))
        ax.add_patch(patches.Rectangle( (1-1/self.network_columns/2,-1/self.network_rows/2), 1/self.network_columns,1+1/self.network_rows, edgecolor='k', fill=False, label="GND = 0 V"))






if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    tft=Device(20, 20, Transistor,vds=1 )
    print("device created")
    print("components added")
    tft.set_global_gate(0)
    tft.set_local_gate([0.5,.7,0.2,1], 10)
    tft.update(show=False)
    tft.show_device()
    print("on device displayed")
    # tft.set_global_gate(10)
    # tft.update(v=args.verbose)
    # print("off device displayed")
    # tft.set_global_gate(10)
    # tft.update(v=args.verbose)
