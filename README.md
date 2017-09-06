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
- initialize G with some variation
- have a way to update G
- consider making transistor objects that get updated based on parameters, or make it all a matrix thing. talk to matthias about this
