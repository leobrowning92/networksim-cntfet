import argparse
from network import Network
import numpy as np
class Transistor(object):
    def __init__(self,on_resistance=1,off_resistance=100,threshold_voltage=0, gate_voltage=0):
        assert on_resistance>0 and off_resistance>0, "ERROR: a component cannot have -ve resistance"
        self.on_resistance=on_resistance
        self.off_resistance=off_resistance
        self.threshold_voltage=threshold_voltage
        self.gate_voltage=gate_voltage
    def get_conductance(self):
        if self.gate_voltage<self.threshold_voltage:
            return 1/self.on_resistance
        else:
            return 1/self.off_resistance

class Device(Network):
    def __init__(self,network_rows, network_columns, component, vds=1):
        ground_nodes = [(x+1)*network_columns-1 for x in range(network_rows)]
        voltage_sources = [[x*network_columns,vds] for x in range(network_rows)]
        Network.__init__(self,network_rows, network_columns, component, ground_nodes, voltage_sources)

    def set_global_gate(self,voltage):
        for edge in self.graph.edges:
            self.graph.edges[edge]['component'].gate_voltage=voltage
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    tft=Device(20, 20, None,vds=1 )

    print("device created")
    components=[Transistor(1*abs(np.random.normal(1,0.5)), 10*abs(np.random.normal(1,0.5)),np.random.normal(0,0.5)) for x in range(len(tft.graph.edges))]
    tft.add_components(components)
    print("components added")
    tft.set_global_gate(-10)
    tft.update(v=args.verbose,show=False)
    saved=tft.save_network('test')

    test=Device.load_network(fname)
    test.load_network(saved)
    test.update(show=True)
    print("on device displayed")
    # tft.set_global_gate(10)
    # tft.update(v=args.verbose)
    # print("off device displayed")
    # tft.set_global_gate(10)
    # tft.update(v=args.verbose)
