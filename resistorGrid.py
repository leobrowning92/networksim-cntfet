import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
class FET(object):
    def __init__(self, on_conductance=1., off_conductance=0.1, threshold_voltage=-1.):
        self.on_conductance=on_conductance
        self.off_conductance=off_conductance
        self.threshold_voltage=threshold_voltage
    def get_conductance(self,gate_voltage):
        if gate_voltage<=self.threshold_voltage:
            return self.on_conductance
        else:
            return self.off_conductance
class Resistor(object):
    def __init__(self):
        self.conductance=1
    def get_conductance(self,dummy):
        return self.conductance
class Network(object):
    """
    This class implements a grid network of 1 Ohm resistors
    and allows specifying of the voltage sources and ground nodes
    the solve method returns the voltages at all of the nodes and
    saves them to an internal variable
    """
    def __init__(self,network_rows, network_columns, component, ground_nodes=[-1], voltage_sources=np.array([[0,5]])):
        #network parameters
        self.network_rows=network_rows
        self.network_columns=network_columns
        self.network_size=self.network_rows*self.network_columns

        #set network parameters
        if all(x>=0 for x in ground_nodes):
            self.ground_nodes=ground_nodes
        else:
            self.ground_nodes=[self.network_size-1]

        self.voltage_sources=voltage_sources
        self.network=nx.grid_2d_graph(self.network_rows,self.network_columns)
        self.adjacency_matrix=self.make_adjacency_matrix()
        self.gate_voltage=0
        self.make_components(component)

        # to make the matrices necessary for the MNA matrix equation
        self.mna_G=self.make_G()
        self.mna_A=self.make_A()
        self.mna_z=self.make_z()
    def getG_trivial(self, n1,n2):
        """holds enough information to reconstruct r1,c1 to r2,c2 information which equates to physical position"""
        return 1
    def make_components(self,component):
        for n1,n2 in self.network.edges():
            self.network.edge[n1][n2]['component']=component()
            self.network.edge[n1][n2]['conductance']=self.network.edge[n1][n2]['component'].get_conductance(1)
    def make_adjacency_matrix(self):
        adjacency_matrix=nx.to_numpy_matrix(self.network,nodelist=sorted(self.network.nodes()))
        return adjacency_matrix
    def make_G(self):
        n=self.network_size
        G=np.array(nx.to_numpy_matrix(self.network,nodelist=sorted(self.network.nodes()),weight='conductance'))
        for i in range(n):
            for j in range(n):
                if i==j:
                    G[i,j]=-sum(G[i])
        return G
    def make_A(self):
        # define symbols
        gnd=self.ground_nodes
        Vsrc=self.voltage_sources
        G=self.mna_G
        n=self.network_size


        B=np.zeros((n,len(Vsrc)))
        for i in range(n):
                if i in Vsrc[:,0]:
                    B[i,list(Vsrc[:,0]).index(i)]=1
        D=np.zeros((len(Vsrc),len(Vsrc)))
        BTD=np.append(B.T,D,axis=1)
        A=np.append(np.append(G,B,axis=1),BTD,axis=0)
        A=np.delete(np.delete(A,gnd,0),gnd,1)
        return A
    def make_z(self):
        r=self.network_rows
        c=self.network_columns
        return np.append(np.zeros((r*c-len(self.ground_nodes),1)), self.voltage_sources[:,1][:,None], axis=0)
    def make_voltages(self):
        # inserts the ground voltages back into x
        x=self.mna_x
        for i in self.ground_nodes:
            x=np.insert(x,i,0,axis=0)
        #splits the source currents from x
        x=x[:-len(self.voltage_sources)]
        self.node_voltages=x
        for node in sorted(self.network.nodes()):
            self.network.node[node]['voltage']=x[self.network.nodes().index(node)]
    def get_voltages(self):
        d=[]
        for node,data in self.network.nodes(data=True):
            d.append(data['voltage'])
        return d



    def solve_mna(self):
        self.mna_x=np.linalg.solve(self.mna_A,self.mna_z)
        self.update_network()
        return self.get_voltages()
    def update_network(self):
        self.make_voltages()
        self.make_currents()
    def show_network(self):
        r=self.network_rows
        c=self.network_columns
        pos={(x//r,x%c):np.array([x//r,x%c]) for x in range(r*c)}
        edges,weights = zip(*nx.get_edge_attributes(self.network,'current').items())

        nodes,voltages = zip(*nx.get_node_attributes(self.network,'voltage').items())

        nx.draw_networkx(self.network, pos, width=2, nodelist=nodes, node_color=voltages,  cmap=plt.get_cmap('plasma'), edge_cmap=plt.get_cmap('plasma'), edgelist=edges, edge_color=weights, node_size=30, with_labels=False)
        plt.show()
    def make_currents(self):
        for n1,n2 in self.network.edges():
            g = float(self.network.edge[n1][n2]['conductance'])
            dV = float(self.network.node[n1]['voltage']) - float(self.network.node[n2]['voltage'])
            self.network.edge[n1][n2]['current']= g * dV
    def get_currents(self):
        d=[]
        for n1,n2,data in self.network.edges(data=True):
            d.append(float(data['current']))
        return d


if __name__ == "__main__":
    net=Network(20,20,Resistor,ground_nodes=[139,279],voltage_sources=np.array([[120,5],[260,5]]))
    net.solve_mna()
    net.show_network()
