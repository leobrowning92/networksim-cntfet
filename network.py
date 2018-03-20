import numpy as np
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

class ConductionNetwork(object):
    """Solves for the conduction characteristics of a physical network"""
    def __init__(self,graph,ground_nodes,voltage_sources):
        self.graph=graph
        self.ground_nodes=np.array(ground_nodes)
        self.voltage_sources=np.array(voltage_sources)
        self.network_size=len(self.graph)
    def update_conductivity(self):
        for edge in self.graph.edges:
            G=self.graph.edges[edge]['component'].get_conductance()
            self.graph.edges[edge]['conductance']=G
            self.graph.edges[edge]['resistance']=1/G
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
    def solve_mna(self):
        mna_x=np.linalg.solve(self.make_A(self.make_G()), self.make_z())
        return mna_x
    def update(self,show=True,v=False):
        #process mna_x to seperate out relevant components
        self.update_conductivity()
        mna_x = self.solve_mna()
        self.update_voltages(mna_x)
        self.update_currents()
        pass
