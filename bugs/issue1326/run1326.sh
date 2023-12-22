# 运行
cd /root/mfem/examples
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include mpi.cpp -o mpi -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
mpirun -np 1 mpi