#include "mfem.hpp"
using namespace mfem;
using namespace std;

int main(int argc, char *argv[])
{
    // 初始化 MPI
    MPI_Init(&argc, &argv);
    int num_procs;
    MPI_Comm_size(MPI_COMM_WORLD, &num_procs);
    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    // 加载网格
    Mesh *mesh = new Mesh("/root/mfem-code-analyzer/bugs/issue2559/manifold.msh", 1, 1, true);
    MFEM_VERIFY(mesh != nullptr, "无法加载网格文件");

    // 将网格转换为并行网格
    ParMesh *pmesh = new ParMesh(MPI_COMM_WORLD, *mesh);
    delete mesh;
    MFEM_VERIFY(pmesh != nullptr, "无法创建并行网格");

    // 定义有限元空间
    H1_FECollection fec(1, pmesh->Dimension());
    ParFiniteElementSpace fespace(pmesh, &fec);

    // 定义必要的边界属性
    Array<int> ess_bdr(pmesh->bdr_attributes.Max());
    ess_bdr = 1;  // 假设所有边界属性都是必要的

    // 定义用于存储必要的真实自由度的数组
    Array<int> ess_tdof_list;
    fespace.GetEssentialTrueDofs(ess_bdr, ess_tdof_list);

    cout << "必要的真实自由度数量: " << ess_tdof_list.Size() << endl;

    // 清理
    delete pmesh;

    MPI_Finalize();
    return 0;
}
