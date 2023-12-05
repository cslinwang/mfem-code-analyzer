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

    // 创建ParBilinearForm
    ParBilinearForm *a = new ParBilinearForm(fespace);
    a->UsePartialAssembly();

    // 添加一个内部面积分器
    a->AddInteriorFaceIntegrator(new DiffusionIntegrator);

    // 装配矩阵
    a->Assemble();

    // 创建两个向量
    Vector x(fespace->GetTrueVSize()), y(fespace->GetTrueVSize());
    x = 1.0; // 给x赋值

    // 调用TrueAddMult
    a->TrueAddMult(x, y);

    // 清理
    delete a;
    delete fespace;
    delete fec;
    delete pmesh;

    MPI_Finalize();
    return 0;
}
