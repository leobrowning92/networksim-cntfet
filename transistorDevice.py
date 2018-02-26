from network import Network
class Transistor(object):
    def __init__(self,on_resistance,off_resistance,gate_voltage=0):
        self.on_resistance=on_resistance
        self.off_resistance=off_resistance
        self.threshold_voltage=threshold_voltage
        self.gate_voltage=gate_voltage
    def get_conductance(self,gate_voltage):
        if gate_voltage<self.threshold_voltage:
            return 1/self.on_resistance
        else:
            return 1/self.off_resistance
class Device(Network):
    def __init__(self,network_rows, network_columns, component, ground_nodes, voltage_sources):

        Network.__init__(network_rows, network_columns, self.distribute_components(component), ground_nodes, voltage_sources)
    def distribute_components(self,component):
        components=[]
        for i in range(len(self.graph.edges)):
            components.append(component(1,0.1))
        return components
    def set_global_gate(self,voltage):
        for edge in self.graph.edges:
            self.graph.edges[edge]['gate_voltage']=voltage


device=Device(3, 3, Transistor, [4], [[0,5]])
device.set_global_gate(0)
device.update()
