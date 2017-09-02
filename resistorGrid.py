import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Network(object):
    def __init__(self,network_rows, network_columns, ground_nodes=[-1], voltage_source_nodes=np.array([[0,5]])):
        self.network_rows=network_rows
        self.network_columns=network_columns
        self.network_size=self.network_rows*self.network_columns
        self.ground_nodes=ground_nodes
        self.voltage_source_nodes=voltage_source_nodes
        self.grid_connections=self.make_grid_connections(self.getG, self.network_rows, self.network_columns)
        # to make the matrices necessary for the MNA matrix equation
        self.mna_A=self.make_A(self.grid_connections, self.ground_nodes, self.voltage_source_nodes)
        self.mna_z=self.make_z(self.network_rows, self.network_columns, self.voltage_source_nodes)

    def getG(self, n1,n2):
        """holds enough information to reconstruct r1,c1 to r2,c2 information which equates to physical position"""
        return 1
    def make_grid_connections(self, getG,r,c):
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


    def make_A(self, connections,gnd,Vsrc):
        G=connections
        n=len(G)
        for i in range(n):
            for j in range(n):
                if i==j:
                    G[i,j]=-sum(connections[i])

        G=np.delete(np.delete(G,gnd[0],0),gnd[0],1)
        n=len(G)
        B=np.zeros((n,len(Vsrc)))
        for i in range(n):
                if i in Vsrc[:,0]:
                    B[i,list(Vsrc[:,0]).index(i)]=1
        D=np.zeros((len(Vsrc),len(Vsrc)))
        BTD=np.append(B.T,D,axis=1)
        return np.append(np.append(G,B,axis=1),BTD,axis=0)

    def make_z(self, r,c,Vsrc):
        return np.append(np.zeros((r*c-1,1)),Vsrc[:,1][:,None],axis=0)
    def solve_mna(self,show=True):
        x=np.matmul(np.linalg.inv(self.mna_A),self.mna_z)
        if show:
            sns.heatmap(np.reshape(x,(self.network_rows, self.network_columns)), linewidths=1, linecolor='grey', annot=True)
            plt.show()
        return x



# r=2
# c=3
# n=r*c
# gnd=[n-1]
# Vsrc=np.array([[0,5]])
# z=make_z(r,c,Vsrc)
#
# A=make_A(make_G(make_gridpattern(getG,r,c),gnd),Vsrc[:,0])
# x=np.matmul(np.linalg.inv(A),z)
# sns.heatmap(np.reshape(x,(r,c)),linewidths=1,linecolor='grey',annot=True)
# plt.show()
net=Network(2,3)
print(net.solve_mna())
