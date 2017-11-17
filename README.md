# networksim-cntfet

## Modified Nodal Analysis (MNA)
The best and most comprehensive links for MNA on the web:
[MNA](https://www.swarthmore.edu/NatSci/echeeve1/Ref/mna/MNA2.html),
[Algorithm](https://www.swarthmore.edu/NatSci/echeeve1/Ref/mna/MNA3.html),
[Examples](https://www.swarthmore.edu/NatSci/echeeve1/Ref/mna/MNA4.html), and
[Matrix formation rules](https://www.swarthmore.edu/NatSci/echeeve1/Ref/mna/MNAMatrixRules.html).

the network is labeled:

|rows/columns->|0|1|2|...|c-1|
|---|:---:|:---:|:---:|:---:|:---:|
|0|0 |1  |2  | ... |c-1 |
|1|c |c+1|c+2|...|c+c-1|
|2|2c|2c+1|...|...|2c+c-1|
|...|...|...|...|...|...|
|(r-1)*c|(r-1)*c+1|...|...|...|(r-1)*c+c-1=r*c-1|

## Todo
- consider a way to visualize a current/resistance grid
- Impliment Updateable objects such as FETs/Memristors
- have update matrix U that changes/replaces G to allow for change ie switching
- have U made/updated by querying the edge objects that make up the network
- investigate the networkx package as a way to handle the network to matrix conversions and visualization

## flow
- make network with connections
- add components to edges
- make adjacency matrix from conductance of components
    - components must have a way to calculate conductance
- make mna matrix with additional data about sources and ground_nodes
- solve mna
- move mna solutions back to physical network, so that nodes have voltages,
and edges have currents
- update components and resolve
