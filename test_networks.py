import traceback
import pytest
import numpy as np
import percolation as perc
import measure_perc as mp
from network import  Resistor, StepTransistor, FermiDiracTransistor

# all transistor elements must accept a type variable when initializing
class TestFermiDiracTransistor():
    def setup(self):
        self.element=FermiDiracTransistor(type='ms',offmap=0)
    def test_gate_voltage(self):
        assert self.element.gate_voltage==0
    def test_conductance(self):
        assert self.element.get_conductance(-1)>0
        assert self.element.get_conductance()>0



@pytest.mark.incremental
class TestTrivialNetwork():
    def setup_class(self):
        self.trivial=perc.CNTDevice(n=10,scaling=1,l='exp',seed=2,pm=0.5, element = FermiDiracTransistor)
        print("setup the trivial network")
    def test_conduction(self):
        assert self.trivial.global_gate(0)>0
    def test_gate_sweep(self):
        x=np.linspace(-20,20,11)
        y=[self.trivial.global_gate(i) for i in x]
        assert np.isfinite(y).all()
    def test_all_gates(self):
        for gate in ['back', 'total', 'partial']:
            assert self.trivial.gate(10,gate)>0

@pytest.mark.incremental
class TestRandomNetwork():
    def setup_class(self):
        self.trivial=perc.CNTDevice(n=500,scaling=5,l='exp', element = FermiDiracTransistor)
        print("setup the trivial network")
    def test_conduction(self):
        assert self.trivial.global_gate(0)>0
    def test_gate_sweep(self):
        x=np.linspace(-20,20,11)
        y=[self.trivial.global_gate(i) for i in x]
        assert np.isfinite(y).all()
    def test_all_gates(self):
        for gate in ['back', 'total', 'partial']:
            assert self.trivial.gate(10,gate)>0
