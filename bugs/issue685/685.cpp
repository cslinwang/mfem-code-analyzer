#include "mfem.hpp"
#include <iostream>

using namespace std;
using namespace mfem;

int main(int argc, char *argv[])
{
    // 1. Initialize MFEM
    InitMFEM();

    // 2. Load the high-order quad mesh
    const char *mesh_file = "star-q2.mesh";
    Mesh mesh(mesh_file, 1, 1);

    // 3. Look at element 0's element transformation's point matrix
    IsoparametricTransformation *iso_elem_trans =
        dynamic_cast<IsoparametricTransformation *>(mesh.GetElementTransformation(0));
    if (iso_elem_trans)
    {
        cout << "Element 0's point matrix before reordering:" << endl;
        iso_elem_trans->GetPointMat().Print();
    }

    // 4. Reorder mesh by switching around the last two elements of the mesh
    int nelem = mesh.GetNE();
    Array<int> reordering(nelem);
    for (int i = 0; i < nelem; ++i)
    {
        reordering[i] = i;
    }
    reordering[nelem - 1] = nelem - 2;
    reordering[nelem - 2] = nelem - 1;
    mesh.ReorderElements(reordering);

    // 5. Look at element 0's element transformation's point matrix again
    iso_elem_trans = dynamic_cast<IsoparametricTransformation *>(mesh.GetElementTransformation(0));
    if (iso_elem_trans)
    {
        cout << "Element 0's point matrix after reordering:" << endl;
        iso_elem_trans->GetPointMat().Print();
    }

    // 6. Finalize MFEM
    FinalizeMFEM();

    return 0;
}
