import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
def getG(n1,n2):
    """holds enough information to reconstruct r1,c1 to r2,c2 information which equates to physical position"""
    return 1
def make_gridpattern(getG,r,c):
    """makes the """
    n=r*c
    Gvalues=np.zeros((n,n))
    for i in range(n):
        for j in range(n):

            if i in [x for x in range(0,c-1)]: #top row
                if i==0 and j in [i+1,i+c]:#top left
                    Gvalues[i,j]=getG(i,j)
                elif i==(c-1) and j in [i-1,i+c]:#top right
                    Gvalues[i,j]=getG(i,j)
                elif j in [i-1,i+1,i+c]:
                    Gvalues[i,j]=getG(i,j)
            elif i in [x for x in range((n-1)*n,n*n)]: #bottom row
                if i==(r-1)*c and j in[i+1,i-c]:
                    Gvalues[i,j]=getG(i,j)
                elif i==r*c-1 and j in[i-1,i-c]:
                    Gvalues[i,j]=getG(i,j)
                elif j in [i-1,i+1,i-c]:
                    Gvalues[i,j]=getG(i,j)
            elif i%c==0: #left side
                if j in [i+1,i+c,i-c]:
                    Gvalues[i,j]=getG(i,j)
            elif (i+1)%c==0: # right side
                if j in [i-1,i+c,i-c]:
                    Gvalues[i,j]=getG(i,j)
            else:
                if j in [i+1,i-1,i+c,i-c]:
                    Gvalues[i,j]=getG(i,j)
    return Gvalues

def make_G(pattern,gnd):
    n=len(pattern)
    G=pattern
    for i in range(n):
        for j in range(n):
            if i==j:
                G[i,j]=-sum(pattern[i])

    return np.delete(np.delete(G,gnd[0],0),gnd[0],1)

def make_A(G,Vsrc):
    n=len(G)
    B=np.zeros((n,len(Vsrc)))
    for i in range(n):
            if i in Vsrc:
                B[i,list(Vsrc).index(i)]=1
    D=np.zeros((len(Vsrc),len(Vsrc)))
    BTD=np.append(B.T,D,axis=1)
    return np.append(np.append(G,B,axis=1),BTD,axis=0)

def make_z(r,c,Vsrc):
    return np.append(np.zeros((r*c-1,1)),Vsrc[:,1][:,None],axis=0)


r=2
c=3
n=r*c
m=1
G=np.zeros((n,n))
Gvalues=np.zeros((n,n))
B=np.zeros((n,m))
C=B.T
D=np.zeros((n,n))
gnd=[n-1]
Vsrc=np.array([[0,5]])
z=make_z(r,c,Vsrc)

A=make_A(make_G(make_gridpattern(getG,r,c),gnd),Vsrc[:,0])
x=np.matmul(np.linalg.inv(A),z)
sns.heatmap(np.reshape(x,(r,c)),linewidths=1,linecolor='grey',annot=True)
plt.show()
