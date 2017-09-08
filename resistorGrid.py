import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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
        self.edges=self.make_grid_edges()
        self.gate_voltage=0
        self.components=self.make_components(component)

        # to make the matrices necessary for the MNA matrix equation
        self.mna_G=self.make_G()
        self.mna_A=self.make_A()
        self.mna_z=self.make_z()
    def getG_trivial(self, n1,n2):
        """holds enough information to reconstruct r1,c1 to r2,c2 information which equates to physical position"""
        return 1
    def make_components(self,component):
        n=self.network_size
        components=np.empty((n,n),dtype=object)
        for i in range(n):
            for j in range(n):
                if self.edges[i,j]==1:
                    components[i,j]=component()
        return components
    def make_grid_edges(self):
        """makes the array that encodes the connections between nodes and
        their conductance for a grid where every node is connected to its
        neerest neighbor.

        note: for the n*n matrix (n=r*c) and point i,j:
        j=i+1 is the conductance to the node to the right of point i
        j=i-1 is the conductance to the node to the left of point i
        j=i-c is the conductance to the node above point i
        j=i+c is the conductance to the node below point i"""
        # define symbols
        r=self.network_rows
        c=self.network_columns
        n=self.network_size
        connections=np.zeros((n,n))
        for i in range(n):
            for j in range(n):
                if i in [x for x in range(0,c-1)]: #top row
                    if i==0 and j in [i+1,i+c]:#top left
                        connections[i,j]=1
                    elif i==(c-1) and j in [i-1,i+c]:#top right
                        Gconnections[i,j]=1
                    elif j in [i-1,i+1,i+c]: #all other top
                        connections[i,j]=1
                elif i in [x for x in range((n-1)*n,n*n)]: #bottom row
                    if i==(r-1)*c and j in[i+1,i-c]: #bottom left
                        connections[i,j]=1
                    elif i==r*c-1 and j in[i-1,i-c]: #bottom right
                        connections[i,j]=1
                    elif j in [i-1,i+1,i-c]: #all other bottom
                        connections[i,j]=1
                elif i%c==0: #left side
                    if j in [i+1,i+c,i-c]:
                        connections[i,j]=1
                elif (i+1)%c==0: # right side
                    if j in [i-1,i+c,i-c]:
                        connections[i,j]=1
                else:
                    if j in [i+1,i-1,i+c,i-c]:
                        connections[i,j]=1
        return connections
    def make_G(self):
        n=self.network_size
        G=np.zeros((n,n))
        for i in range(n):
            for j in range(n):
                if self.edges[i,j]==1:
                    G[i,j]=self.components[i,j].get_conductance(self.gate_voltage)
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
    def get_voltages(self):
        # inserts the ground voltages back into x
        x=self.mna_x
        for i in self.ground_nodes:
            x=np.insert(x,i,0,axis=0)
        #splits the source currents from x
        x=x[:-len(self.voltage_sources)]
        self.node_voltages=x
        return x
    def solve_mna(self):
        self.mna_x=np.linalg.solve(self.mna_A,self.mna_z)
        return self.get_voltages()
    def show_voltages(self):
        if not(hasattr(self, 'node_voltages')):
            #if not already solved, solve network
            self.solve_mna()
        sns.heatmap(np.reshape(self.node_voltages,(self.network_rows, self.network_columns)), linewidths=1, linecolor='grey', annot=True,fmt='.2g')
        plt.show()
    def set_gate(self,gate):
        n=self.network_size
        vg=np.empty((n,n))
        for i in range(n):
            for j in range(n):
                if self.edges[i,j]:
                    vg[i,j]=gate
        self.gate_voltage=vg

if __name__ == "__main__":
    net=Network(20,20,Resistor,ground_nodes=[139,279],voltage_sources=np.array([[120,5],[260,5]]))
    net.solve_mna()
    net.show_voltages()
