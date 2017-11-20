#!/usr/bin/env python3
import argparse, unittest, textwrap, datetime, os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
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
    def __init__(self,network_rows, network_columns, component, ground_nodes=[-1], voltage_sources=np.array([[0,5]]),save=False):
        #network parameters
        self.network_rows=network_rows
        self.network_columns=network_columns
        self.network_size=self.network_rows*self.network_columns
        self.save=save

        #set network attributes
        if all(x>=0 for x in ground_nodes):
            self.ground_nodes=ground_nodes
        else:
            self.ground_nodes=[self.network_size-1]

        self.voltage_sources=voltage_sources
        self.network=nx.grid_2d_graph(self.network_rows,self.network_columns)
        self.adjacency_matrix=self.make_adjacency_matrix()
        self.gate_voltage=0
        self.component=component
        self.add_components(component)
        self.fname=self.make_name()
    def getG_trivial(self, n1,n2):
        """holds enough information to reconstruct r1,c1 to r2,c2 information which equates to physical position"""
        return 1
    def add_components(self,component):
        for n1,n2 in self.network.edges():
            self.network.edges[n1,n2]['component']=component()
            self.network.edges[n1,n2]['conductance']=self.network.edges[n1,n2]['component'].get_conductance(1)
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
        G=self.make_G()
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
        x=x[:-1]
        self.node_voltages=x
        i=0
        for node in sorted(self.network.nodes()):
            self.network.node[node]['voltage']=float(x[i])
            i+=1
    def get_voltages(self):
        d=[]
        for node,data in self.network.nodes(data=True):
            d.append(data['voltage'])
        return d
    def make_currents(self):
        for n1,n2 in self.network.edges():
            g = float(self.network.edges[n1,n2]['conductance'])
            dV = float(self.network.node[n1]['voltage']) - float(self.network.node[n2]['voltage'])
            # to include current directionality one would have to
            #replace the abs with some sort of node-node direction rules
            self.network.edges[n1,n2]['current']= abs(g * dV)
    def get_currents(self):
        d=[]
        for n1,n2,data in self.network.edges(data=True):
            d.append(float(data['current']))
        return d


    def solve_mna(self):
        mna_A=self.make_A()
        mna_z=self.make_z()
        self.mna_x=np.linalg.solve(mna_A,mna_z)
        self.update_network()
        return self.get_voltages()
    def update_network(self):
        self.make_voltages()
        self.make_currents()

    def show_network(self,save=False,show=True):
        r=self.network_rows
        c=self.network_columns
        pos={}
        for i in range(r):
            for j in range(c):
                pos[(i,j)]=j,i
        edges,weights = zip(*nx.get_edge_attributes(self.network,'current').items())

        nodes,voltages = zip(*nx.get_node_attributes(self.network,'voltage').items())

        fig = plt.figure(figsize=(10,20),facecolor='white')
        ax1=plt.subplot(211)
        ax2=plt.subplot(212)

        nodes=nx.draw_networkx_nodes(self.network, pos, width=2, nodelist=nodes, node_color=voltages,  cmap=plt.get_cmap('winter'), node_size=30, with_labels=False, ax=ax1)
        edges=nx.draw_networkx_edges(self.network, pos, width=2, edgelist=edges, edge_color=weights,  edge_cmap=plt.get_cmap('autumn'), node_size=30, with_labels=False, ax=ax2)

        divider = make_axes_locatable(ax1)
        cax1 = divider.append_axes('right', size='5%', pad=0.05)
        divider = make_axes_locatable(ax2)
        cax2 = divider.append_axes('right', size='5%', pad=0.05)
        fig.colorbar(edges,label="Current",cax=cax2)
        fig.colorbar(nodes,label="Node Voltage",cax=cax1)
        if save:
            plt.savefig("{}.png".format(self.fname))
        if show:
            plt.show()
    def make_currents(self):
        for n1,n2 in self.network.edges():
            g = float(self.network.edge[n1][n2]['conductance'])
            dV = float(self.network.node[n1]['voltage']) - float(self.network.node[n2]['voltage'])
            # to include current directionality one would have to
            #replace the abs with some sort of node-node direction rules
            self.network.edge[n1][n2]['current']= abs(g * dV)
    def get_currents(self):
        d=[]
        for n1,n2,data in self.network.edges(data=True):
            d.append(float(data['current']))
        return d

    def save_network(self):
        nx.write_yaml(self.network,"{}.yaml".format(self.fname))
    def load_network(self):
        self.network=nx.read_yaml("{}.yaml".format(self.fname))
    def make_name(self):
        info="{}x{}net_{}_VG{}".format(self.network_rows,self.network_columns,self.component.__name__, self.gate_voltage)
        return "{}_{:%Y-%m-%d-%H:%M:%S.%f}".format(info,datetime.datetime.now())
    def print_info(self):
        print("{} rows, {} columns, {} total size".format(self.network_rows, self.network_columns, self.network_size))


class NetworkTest(unittest.TestCase):
    def setUp(self):
        self.net=Network(3,3, Resistor)

    def test_presolve_conductance(self):
        for n1,n2 in self.net.network.edges():
            self.assertEqual(self.net.network.edges[n1,n2]["conductance"],1)
    def test_save(self):
        self.net.solve_mna()
        self.net.save_network()
        self.net.load_network()
        self.test_solve_stability()

    def test_solve_stability(self):
        self.net.solve_mna()
        prenet=self.net.network
        self.net.solve_mna()
        postnet=self.net.network
        self.assertEqual(prenet,postnet)

    def test_show(self):
        self.net.solve_mna()
        # self.net.show_network()
    def tearDown(self):
        if os.path.isfile("{}.yaml".format(self.net.fname)):
            os.remove("{}.yaml".format(self.net.fname))





if __name__ == "__main__":
    parser = argparse.ArgumentParser( formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent("""\
            Description of the various functions available:
                plotall   -  plots all data for each chip on a seperate plot and store in subdir plots/
                test      -  simply loads datasets use -i for interactive and -f to force reload"""))
    parser.add_argument("rows",type=int)
    parser.add_argument("columns",type=int)
    parser.add_argument("-t", "--test", action="store_true")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--save")
    args = parser.parse_args()

    net=Network(args.rows,args.columns,Resistor,ground_nodes=[args.rows*args.columns-1],voltage_sources=np.array([[0,5]]),save=args.save)
    net.solve_mna()
    net.print_info()
    if args.show:
        net.show_network()
    if args.test:
        suite = unittest.TestLoader().loadTestsFromTestCase(NetworkTest)
        unittest.TextTestRunner(verbosity=3).run(suite)
    # net=Network(3,2,Resistor,ground_nodes=[3],voltage_sources=np.array([[1,5]]))
    # net.solve_mna()
    # net.show_network()
