#include "mfem.hpp"
#include <iostream>
#include <fstream>
#include <sstream>

using namespace std;
using namespace mfem;

int main()
{
    // 初始化MFEM的MPI环境（如果您的MFEM库是并行版本的）
    // 对于非并行版本，可以省略这部分
    MPI_Session mpi;
    if (!mpi.Root()) { mfem::out.Disable(); mfem::err.Disable(); }

    // Gmsh文件路径
    const char *mesh_file = "/root/mfem-code-analyzer/bugs/issue2216/2216.msh";

    // 尝试读取Gmsh生成的网格文件
    try {
        Mesh *mesh = new Mesh(mesh_file, 1, 1);

        // 输出网格信息（可选）
        cout << "Mesh has been successfully loaded." << endl;
        cout << "Number of vertices: " << mesh->GetNV() << endl;
        cout << "Number of elements: " << mesh->GetNE() << endl;

        // 清理
        delete mesh;
    }
    catch (const std::exception &e) {
        cerr << "Error occurred while loading the mesh: " << e.what() << endl;
        return 1;
    }

    return 0;
}
