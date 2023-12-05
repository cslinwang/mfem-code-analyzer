#include "mfem.hpp"
#include <iostream>
#include <mpi.h>

using namespace mfem;
using namespace std;

int main(int argc, char *argv[])
{
    MPI_Init(&argc, &argv);

    int myid;
    MPI_Comm_rank(MPI_COMM_WORLD, &myid); // 获取当前进程ID

    // 创建并行网格（需要一个包含内部边界元素的网格）
    const char *mesh_file = "/root/mfem/data/beam-tri.mesh";
    Mesh *mesh = new Mesh(mesh_file, 1, 1);
    ParMesh *pmesh = new ParMesh(MPI_COMM_WORLD, *mesh);
    delete mesh;

    // 检查边界元素的方向
    int check_res = pmesh->Mesh::CheckBdrElementOrientation(false);
    if (check_res != 0)
    {
        if (myid == 0) // 根进程打印信息
        {
            cout << "CheckBdrElementOrientation failed." << endl;
        }
    }
    else
    {
        if (myid == 0) // 根进程打印信息
        {
            cout << "CheckBdrElementOrientation passed." << endl;
        }
    }

    // 清理
    delete pmesh;

    MPI_Finalize();
    return 0;
}
