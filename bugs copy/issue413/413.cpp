
#include "mfem.hpp"
#include <fstream>
#include <iostream>

using namespace std;
using namespace mfem;

int main(int argc, char *argv[])
{
    int num_procs, myid;
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &num_procs);
    MPI_Comm_rank(MPI_COMM_WORLD, &myid);

    SparseMatrix A(2, 2);
    A.Add(0, 0, 1.0);
    A.Add(0, 1, 0.0);
    A.Add(1, 0, 0.0);
    A.Add(1, 1, 2.0);
    A.Finalize();

    HYPRE_Int row_starts[2];
    row_starts[0] = myid * 2;
    row_starts[1] = (myid + 1) * 2;

    HypreParMatrix A_par(MPI_COMM_WORLD, num_procs * 2, row_starts, &A);

    A_par.Threshold(1e-8);
}