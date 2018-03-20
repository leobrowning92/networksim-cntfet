class ConductionNetwork(object):
    """Solves for the conduction characteristics of a physical network"""
    def __init__(self,graph,ground_nodes,voltage_sources):
        self.graph=graph
        self.ground_nodes=ground_nodes
        self.voltage_sources=voltage_sources
