#!/usr/bin/python

# Size along each edge of the cube
nxo2=1
nx=2*nxo2+1
ny=5
nz=5
nxm1=nx-1
nym1=ny-1
nzm1=nz-1

xmin=0.0
ymin=0.0
zmin=0.0
xstep=1./nxm1
ystep=1./nym1
zstep=1./nzm1


# Periodicity
px=True
py=True
pz=True

def coord(*ix):
    """
    spatial coordinates for a given tuple
    :param ix: a tuple of index - (ix, iy, iz)
    """
    return (ix[2]*xstep+xmin,ix[1]*ystep+ymin,ix[0]*zstep+zmin)

def three_d_array(value, *dim):
    """
    Create 3D-array
    :param dim: a tuple of dimensions - (x, y, z)
    :param value: value with which 3D-array is to be filled
    :return: 3D-array
    """

    return [[[value for _ in xrange(dim[2])] 
             for _ in xrange(dim[1])] for _ in xrange(dim[0])]

if __name__ == "__main__":
    array = three_d_array(-1, *(nz, ny, nx))
    x1 = len(array)
    x2 = len(array[0])
    x3 = len(array[0][0])

    print("MFEM mesh v1.0\n\ndimension\n3")
    
    nbelts=(nx-1)*(ny-1)*(nz-1)
    print("\nelements\n%d" % nbelts)
    
    # loop over all nodes
    # if new, give it a new index
    # if periodic border, give the index already given previously
    c=0
    for z in range(nz):
        if (pz and z == nz-1):
            for y in range(ny):
                for x in range(nx):
                    array[z][y][x]=array[0][y][x]
        else:
            for y in range(ny):
                if (py and y == ny-1):
                    for x in range(nx):
                        array[z][y][x]=array[z][0][x]
                else:
                    for x in range(nx):
                        if (px and x == nx-1):
                            array[z][y][x]=array[z][y][0]
                        else:
                            array[z][y][x]=c
                            c=c+1

    for z in range(nz-1):
        for y in range(ny-1):
            for x in range(nxo2):
                print("1 5 %d %d %d %d %d %d %d %d" %
                      (array[z][y][x], array[z][y][x+1], 
                       array[z][y+1][x+1], array[z][y+1][x],
                       array[z+1][y][x], array[z+1][y][x+1], 
                       array[z+1][y+1][x+1], array[z+1][y+1][x]))
            for x in range(nxo2, nx-1):
                print("2 5 %d %d %d %d %d %d %d %d" %
                      (array[z][y][x], array[z][y][x+1], 
                       array[z][y+1][x+1], array[z][y+1][x],
                       array[z+1][y][x], array[z+1][y][x+1], 
                       array[z+1][y+1][x+1], array[z+1][y+1][x]))

    print("\nboundary\n%d" % (2*nxm1*nym1 + 2*nym1*nzm1 + 2*nxm1*nzm1))
    
    z=0;
    for y in range(ny-1):
        for x in range(nx-1):
            print("2 3 %d %d %d %d" %
                  (array[z][y][x], array[z][y][x+1], 
                   array[z][y+1][x+1], array[z][y+1][x]))
    z=nz-1;
    for y in range(ny-1):
        for x in range(nx-1):
            print("6 3 %d %d %d %d" %
                  (array[z][y][x], array[z][y][x+1], 
                   array[z][y+1][x+1], array[z][y+1][x]))
                
    x=0;
    for z in range(nz-1):
        for y in range(ny-1):
            print("5 3 %d %d %d %d" %
                  (array[z][y][x], array[z][y+1][x], 
                   array[z+1][y+1][x], array[z+1][y][x]))
    x=nx-1;
    for z in range(nz-1):
        for y in range(ny-1):
            print("3 3 %d %d %d %d" %
                  (array[z][y][x], array[z][y+1][x], 
                   array[z+1][y+1][x], array[z+1][y][x]))
                  
    y=0;
    for z in range(nz-1):
        for x in range(nx-1):
            print("1 3 %d %d %d %d" %
                  (array[z][y][x], array[z][y][x+1], 
                   array[z+1][y][x+1], array[z+1][y][x]))
    y=ny-1;
    for z in range(nz-1):
        for x in range(nx-1):
            print("4 3 %d %d %d %d" %
                  (array[z][y][x], array[z][y][x+1], 
                   array[z+1][y][x+1], array[z+1][y][x]))
                  
                    
    print("\nvertices\n%d\n" % c)
    print("nodes\nFiniteElementSpace\nFiniteElementCollection: L2_T1_3D_P1")
    print("VDim: 3\nOrdering: 1\n");

    for z in range(nz-1):
        for y in range(ny-1):
            for x in range(nx-1):
                print("%f %f %f" % (coord(*(z,y,x))))
                print("%f %f %f" % (coord(*(z,y,x+1))))
                print("%f %f %f" % (coord(*(z,y+1,x))))
                print("%f %f %f" % (coord(*(z,y+1,x+1))))
                print("%f %f %f" % (coord(*(z+1,y,x))))
                print("%f %f %f" % (coord(*(z+1,y,x+1))))
                print("%f %f %f" % (coord(*(z+1,y+1,x))))
                print("%f %f %f" % (coord(*(z+1,y+1,x+1))))
                
    
