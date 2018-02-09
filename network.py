#!/usr/bin/env python3
import unittest, argparse
import networkx as nx
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt

class Resistor(object):
    def __init__(self,R=1):
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
        #add the components
        for edge in self.graph.edges():
            self.graph.edges[edge]['component']=component()

    def check_values(self):
        # ensures there are some non ground/source nodes
        assert len(self.voltage_sources) + len(self.ground_nodes) < self.network_size, "there are more voltage sources and ground nodes than network nodes"
        assert len(self.ground_nodes)<self.network_size, "ground nodes out of graph index"
        assert len(self.voltage_sources[:,0])<self.network_size, "ground nodes out of graph index"

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
    def update_graph(self):
        #process mna_x to seperate out relevant components
        mna_x = self.solve_mna()
        for i in self.ground_nodes:
            mna_x=np.insert(mna_x,i,0,axis=0)
        source_currents=mna_x[-len(self.voltage_sources)]
        mna_x=mna_x[:-len(self.voltage_sources)]
        # update graph nodes with voltage values
        i=0
        for index in self.graph.node():
            self.graph.node[index]['voltage']=float(mna_x[i])
            i+=1
        #update graph edges with current values
        for n1,n2 in self.graph.edges():
            g = float(self.graph.edges[n1,n2]['component'].get_conductance())
            dV = float(self.graph.node[n1]['voltage']) - float(self.graph.node[n2]['voltage'])
            self.graph.edges[(n1,n2)]['current']=abs(g*dV)









class NetworkTest_twobytwo(unittest.TestCase):
    # can write a test to compare the source currents from mna_x with the currents out of source nodes, and also compare the currents into ground nodes and out of source nodes
    def setUp(self):
        self.net=Network(2,2, Resistor,[3],[[0,5]])
        self.testG = np.array(
              [[-2.,1.,1.,0.],
               [1.,-2.,0.,1.],
               [1.,0.,-2.,1.],
               [0.,1.,1.,-2.]])
        self.testA = np.array(
              [[-2.,1.,1.,1.],
               [1.,-2.,0.,0.],
               [1.,0.,-2.,0.],
               [1.,0.,0.,0.]])
        self.testz=np.array([[0.],[0.],[0.],[5.]])
        self.testx=np.array([[5.000000000000001], [2.5000000000000004], [2.5], [5.000000000000001]])
    def test_makeG(self):
        self.assertSequenceEqual(self.net.make_G().tolist(), self.testG.tolist())
    def test_makeA(self):
        self.assertSequenceEqual(self.net.make_A(self.net.make_G()).tolist(), self.testA.tolist())
    def test_makez(self):
        self.assertSequenceEqual(self.net.make_z().tolist(), self.testz.tolist())
    def test_solveMNA(self):
        self.assertSequenceEqual(self.net.solve_mna().tolist(), self.testx.tolist())
    def test_components(self):
        self.assertEqual(type(self.net.graph.edges[((0,1),(0,0))]["component"]),  Resistor)
        self.assertEqual(self.net.graph.edges[((0,1),(0,0))]["component"].get_conductance(), 1.)
    def tearDown(self):
        pass




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", action="store_true")
    args = parser.parse_args()
    if args.test:
        suite = unittest.TestLoader().loadTestsFromTestCase(NetworkTest_twobytwo)
        unittest.TextTestRunner(verbosity=3).run(suite)
