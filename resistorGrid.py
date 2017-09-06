import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Network(object):
    def __init__(self,network_rows, network_columns, ground_nodes=[-1], voltage_sources=np.array([[0,5]])):
        self.network_rows=network_rows
        self.network_columns=network_columns
        self.network_size=self.network_rows*self.network_columns
        if all(x>=0 for x in ground_nodes):
            self.ground_nodes=ground_nodes
        else:
            self.ground_nodes=[self.network_size-1]

        self.voltage_sources=voltage_sources
        self.grid_connections=self.make_grid_connections(self.getG)
        # to make the matrices necessary for the MNA matrix equation
        self.mna_A=self.make_A()
        self.mna_z=self.make_z()
        self.mna_x=np.matmul(np.linalg.inv(self.mna_A),self.mna_z)
        self.node_voltages=self.get_voltages()
    def getG(self, n1,n2):
        """holds enough information to reconstruct r1,c1 to r2,c2 information which equates to physical position"""
        return 1
    def make_grid_connections(self, getG):
        """makes the array that encodes the connections between nodes and
        their conductance for a grid where every node is connected to its
        neerest neighbor.

        the network is labeled from 0 to r*c-1
        to translate from r,c network index to i,j connection index.

        note: for the n*n matrix (n=r*c) and point i,j:
        j=i+1 is the conductance to the node to the right of point i
        j=i-1 is the conductance to the node to the left of point i
        j=i-c is the conductance to the node above point i
        j=i+c is the conductance to the node below point i"""
        # define symbols
        r=self.network_rows
        c=self.network_columns
        n=r*c
        Gvalues=np.zeros((n,n))
        for i in range(n):
            for j in range(n):
                if i in [x for x in range(0,c-1)]: #top row
                    if i==0 and j in [i+1,i+c]:#top left
                        Gvalues[i,j]=getG(i,j)
                    elif i==(c-1) and j in [i-1,i+c]:#top right
                        Gvalues[i,j]=getG(i,j)
                    elif j in [i-1,i+1,i+c]: #all other top
                        Gvalues[i,j]=getG(i,j)
                elif i in [x for x in range((n-1)*n,n*n)]: #bottom row
                    if i==(r-1)*c and j in[i+1,i-c]: #bottom left
                        Gvalues[i,j]=getG(i,j)
                    elif i==r*c-1 and j in[i-1,i-c]: #bottom right
                        Gvalues[i,j]=getG(i,j)
                    elif j in [i-1,i+1,i-c]: #all other bottom
                        Gvalues[i,j]=getG(i,j)
                elif i%c==0: #left side
                    if j in [i+1,i+c,i-c]:
                        Gvalues[i,j]=getG(i,j)
                elif (i+1)%c==0: # right side
                    if j in [i-1,i+c,i-c]:
                        Gvalues[i,j]=getG(i,j)
                else:
                    if j in [i+1,i-1,i+c,i-c]:
                        Gvalues[i,j]=getG(i,j)
        return Gvalues
    def make_A(self):
        # define symbols
        gnd=self.ground_nodes
        Vsrc=self.voltage_sources
        G=self.grid_connections
        n=self.network_size
        for i in range(n):
            for j in range(n):
                if i==j:
                    G[i,j]=-sum(G[i])
        G=np.delete(np.delete(G,gnd,0),gnd,1)
        n=len(G)
        B=np.zeros((n,len(Vsrc)))
        for i in range(n):
                if i in Vsrc[:,0]:
                    B[i,list(Vsrc[:,0]).index(i)]=1
        D=np.zeros((len(Vsrc),len(Vsrc)))
        BTD=np.append(B.T,D,axis=1)
        return np.append(np.append(G,B,axis=1),BTD,axis=0)
    def make_z(self):
        r=self.network_rows
        c=self.network_columns
        return np.append(np.zeros((r*c-len(self.ground_nodes),1)), self.voltage_sources[:,1][:,None], axis=0)
    def get_voltages(self):
        # inserts the ground voltages back into x
        x=np.insert(self.mna_x,self.ground_nodes,0,axis=0)
        #splits the source currents from x
        x=x[:-len(self.voltage_sources)]


        return x





net=Network(10,10,ground_nodes=[55,60],voltage_sources=np.array([[0,5],[3,3]]))

sns.heatmap(np.reshape(net.node_voltages,(net.network_rows, net.network_columns)), linewidths=1, linecolor='grey', annot=True)
plt.show()
