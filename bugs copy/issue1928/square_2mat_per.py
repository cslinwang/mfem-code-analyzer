#!/usr/bin/python

# Size along each edge of the cube
nxo2=2
nx=2*nxo2+1
ny=5
nxm1=nx-1
nym1=ny-1

xmin=0.0
ymin=0.0
xstep=1./nxm1
ystep=1./nym1


# Periodicity
px=True
py=True
def coord(*ix):
    """
    spatial coordinates for a given tuple
    :param ix: a tuple of index - (ix, iy, iz)
    """
    return (ix[1]*xstep+xmin,ix[0]*ystep+ymin)

def two_d_array(value, *dim):
    """
    Create 3D-array
    :param dim: a tuple of dimensions - (x, y, z)
    :param value: value with which 3D-array is to be filled
    :return: 3D-array
    """

    return [[value for _ in xrange(dim[1])] for _ in xrange(dim[0])]

if __name__ == "__main__":
    array = two_d_array(-1, *(ny, nx))
    x1 = len(array)
    x2 = len(array[0])

    print("MFEM mesh v1.0\n\ndimension\n2")
    
    nbelts=(nx-1)*(ny-1)
    print("\nelements\n%d" % nbelts)
    
    # loop over all nodes
    # if new, give it a new index
    # if periodic border, give the index already given previously
    c=0
    for y in range(ny):
        if (py and y == ny-1):
            for x in range(nx):
                array[y][x]=array[0][x]
        else:
            for x in range(nx):
                if (px and x == nx-1):
                    array[y][x]=array[y][0]
                else:
                    array[y][x]=c
                    c=c+1

    for y in range(ny-1):
        for x in range(nxo2):
            print("1 3 %d %d %d %d" %
                  (array[y][x], array[y][x+1], 
                   array[y+1][x+1], array[y+1][x]))
        for x in range(nxo2, nx-1):
            print("2 3 %d %d %d %d" %
                  (array[y][x], array[y][x+1], 
                   array[y+1][x+1], array[y+1][x]))
   
    print("\nboundary\n%d" % (2*nym1))
    
    x=0;
    for y in range(ny-1):
        print("3 1 %d %d" %
              (array[y][x], array[y+1][x]))
    x=nx-1;
    for y in range(ny-1):
        print("6 1 %d %d" %
              (array[y][x], array[y+1][x]))
                 
                    
    print("\nvertices\n%d\n" % c)
    print("nodes\nFiniteElementSpace\nFiniteElementCollection: L2_T1_2D_P1")
    print("VDim: 2\nOrdering: 1\n");

    for y in range(ny-1):
        for x in range(nx-1):
            print("%f %f" % (coord(*(y,x))))
            print("%f %f" % (coord(*(y,x+1))))
            print("%f %f" % (coord(*(y+1,x))))
            print("%f %f" % (coord(*(y+1,x+1))))
                
    
