#include "mfem.hpp"
using namespace mfem;
using namespace std; // 添加这行

int main()
{
    // 创建简单的2D网格
    Mesh *mesh = new Mesh("simple_2d_mesh.mesh");

    // 创建一阶ND_FECollection有限元空间
    ND_FECollection fec(1, mesh->Dimension());
    FiniteElementSpace fespace(mesh, &fec);

    // 遍历网格中的每个DoF并调用GetElementForDof()
    for (int dof = 0; dof < fespace.GetNDofs(); ++dof)
    {
        int elem = fespace.GetElementForDof(dof);
        if (elem == -1)
        {
            // 输出出现问题的DoF
            cout << "DoF " << dof << " has an issue (returns -1)." << endl;
        }
    }

    // 清理资源
    delete mesh;

    return 0;
}
