#include "mfem.hpp"
#include <fstream>
#include <iostream>
using namespace std;
using namespace mfem;

int main(int argc, char *argv[])
{
    SparseMatrix *matA = new SparseMatrix(2, 2);
    matA->Set(0,0,11.);    matA->Set(0,1,12.);
    matA->Set(1,0,13.);    matA->Set(1,1,14.);

    SparseMatrix *matB = new SparseMatrix(2, 2);
    matB->Set(0,0,21.);    matB->Set(0,1,22.);
    matB->Set(1,0,23.);    matB->Set(1,1,24.);

    SparseMatrix *matC = new SparseMatrix(2, 2);
    matC->Set(0,0,31.);    matC->Set(0,1,32.);
    matC->Set(1,0,33.);    matC->Set(1,1,34.);

    SparseMatrix *matD = new SparseMatrix(2, 2);
    matD->Set(0,0,41.);    //matD->Set(0,1,42.);
    matD->Set(1,0,43.);    matD->Set(1,1,44.);

    Array<int> block_offsets(3);
    block_offsets[0] = 0;    block_offsets[1] = 2;    block_offsets[2] = 4;

    BlockMatrix *block_mat = new BlockMatrix(block_offsets,block_offsets);
    block_mat->SetBlock(0, 0, matA);    block_mat->SetBlock(0, 1, matB);
    block_mat->SetBlock(1, 0, matC);    block_mat->SetBlock(1, 1, matD);
    block_mat->Finalize();
    block_mat->Print();
}