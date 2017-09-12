import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

s=10
G=nx.grid_2d_graph(s,s)
pos={(n//s,n%s):np.array([n//s,n%s]) for n in range(s**2)}
for edge in G.edges():
    G.edge[edge[0]][edge[1]]['conductance']=np.random.uniform()
d=[]
for n1,n2,data in G.edges(data=True):
    d.append(data['conductance'])


# This returns the correct adjacency matrix for the network
print(nx.to_numpy_matrix(G,nodelist=sorted(G.nodes()),weight='conductance'))
nx.draw_networkx(G,pos,width=2,edge_cmap=plt.get_cmap('plasma'),edge_vmin=0,edge_vmax=1,edge_color=d)

plt.show()
