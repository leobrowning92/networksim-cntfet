import argparse
from network import Network
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
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

class Device(Network):
    def __init__(self,network_rows, network_columns, component, vds=1):
        ground_nodes = [(x+1)*network_columns-1 for x in range(network_rows)]
        voltage_sources = [[x*network_columns,vds] for x in range(network_rows)]
        Network.__init__(self,network_rows, network_columns, component, ground_nodes, voltage_sources)
        self.update_location()
        self.gate_areas=[]
    def update_location(self):
        max_dimension=max(self.network_rows,self.network_columns)
        for node in self.graph.nodes:
            self.graph.nodes[node]['pos'] = [node[1]/max_dimension, node[0]/max_dimension]
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
        plt.show()
    def plot_regions(self,ax):
        for a in self.gate_areas:
            ax.add_patch(patches.Rectangle((a[0][0],a[0][1]),a[0][2],a[0][3], edgecolor='b', fill=False))





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
