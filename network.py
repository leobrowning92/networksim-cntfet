#!/usr/bin/env python3
import unittest, argparse
import networkx as nx
import numpy as np

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
        self.ground_nodes=ground_nodes
        self.voltage_sources=voltage_sources
        #make the grid graph
        self.graph=nx.grid_2d_graph(self.network_rows,self.network_columns)
        #add the components
        for edge in self.graph.edges():
            self.graph.edges[edge]['component']=component()

    def solve_mna(self):
        # solve linalg system Ax=z
        # update network voltages
        # update currents
        pass









class NetworkTest(unittest.TestCase):
    def setUp(self):
        self.net=Network(2,2, Resistor,[8],[[0,5]])

    def test_show_graph(self):
        self.assertEqual(self.net.graph.size(),4)
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
        suite = unittest.TestLoader().loadTestsFromTestCase(NetworkTest)
        unittest.TextTestRunner(verbosity=3).run(suite)
