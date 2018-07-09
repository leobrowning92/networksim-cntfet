import percolation as perc




class TestTrivialNetwork():
    def setup(self):
        self.trivial=perc.StickCollection(n=10,scaling=1,l='exp',seed=2)
        print("setup the trivial network")
    def test_conduction(self):
        sum(self.trivial.cnet.source_currents)==0.03333333333333335
        pass
class TestRandomNetwork():
    pass
