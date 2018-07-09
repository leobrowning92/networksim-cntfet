import traceback
import percolation as perc
from network import  Resistor, StepTransistor, FermiDiracTransistor




class TestFermiDiracTransistor():
    def setup(self):
        self.element=FermiDiracTransistor(type='ms',offmap=0)
    def test_get(self):
        assert self.element.get_conductance(-1)==1.0
        assert self.element.get_conductance(0)==0.5005
        assert self.element.get_conductance(1)==0.001

class TestTrivialNetwork():
    def setup(self):
        self.trivial=perc.StickCollection(n=10,scaling=1,l='exp',seed=2)
        print("setup the trivial network")
    def test_conduction(self):
        sum(self.trivial.cnet.source_currents)==0.03333333333333335
        pass
class TestRandomNetwork():
    pass
