#include "mfem.hpp"
#include <iostream>
#include <mpi.h>

using namespace mfem;
using namespace std;

int main(int argc, char *argv[])
{
    MPI_Init(&argc, &argv);

    // 创建并行网格
    const char *mesh_file = "/root/mfem/data/star.mesh";
    Mesh *mesh = new Mesh(mesh_file, 1, 1);
    ParMesh *pmesh = new ParMesh(MPI_COMM_WORLD, *mesh);
    delete mesh;

    // 定义有限元空间
    FiniteElementCollection *fec = new H1_FECollection(1, pmesh->Dimension());
    ParFiniteElementSpace *fespace = new ParFiniteElementSpace(pmesh, fec);

    // 创建ParLinearForm
    ParLinearForm *lf = new ParLinearForm(fespace);

    // 创建Coefficient
    ConstantCoefficient one(1.0);

    // 添加一个内部面积分器
    lf->AddInteriorFaceIntegrator(new DomainLFIntegrator(one));

    // 装配
    lf->Assemble();
    lf->AssembleSharedFaces();  // 这里可能出现bug

    // 清理
    delete lf;
    delete fespace;
    delete fec;
    delete pmesh;

    MPI_Finalize();
    return 0;
}
