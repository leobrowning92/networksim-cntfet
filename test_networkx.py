import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


G=nx.grid_2d_graph(3,3)
pos={(n//3,n%3):np.array([n//3,n%3]) for n in range(9)}
for edge in G.edges():
    G.edge[edge[0]][edge[1]]['conductance']=np.random.uniform()
    d=[]
for n1,n2,data in G.edges(data=True):
    d.append(data['conductance'])


# This returns the correct adjacency matrix for the network
(nx.to_numpy_matrix(G,nodelist=sorted(G.nodes()),weight='conductance')
nx.draw_networkx(G,pos,width=2,edge_cmap=plt.get_cmap('plasma'),edge_vmin=0,edge_vmax=1,edge_color=d)

plt.show()
