

import networkx as nx
G=nx.grid_2d_graph(3,3)
pos={(n//3,n%3):np.array([n//3,n%3]) for n in range(9)}

# This returns the correct adjacency matrix for the network
nx.to_numpy_matrix(G,nodelist=sorted(G.nodes()))
nx.draw(G,pos)
plt.show
