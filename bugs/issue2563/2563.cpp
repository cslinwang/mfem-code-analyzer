#include "mfem.hpp"
#include <iostream>

using namespace mfem;

int main()
{
    const char *mesh_file = "/root/mfem/mfem-code-analyzer/bugs/issue2563/origin_mesh_tri.vtu";  // 更改为您的 VTU 文件路径

    try {
        Mesh *mesh = new Mesh(mesh_file, 1, 1);
        std::cout << "Mesh loaded successfully." << std::endl;
    }
    catch (std::exception &e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }

    return 0;
}
