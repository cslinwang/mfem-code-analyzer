#include "mfem.hpp"
#include <fstream>
#include <iostream>

using namespace mfem;

int main(int argc, char *argv[])
{
   // 初始化 MPI
   MPI_Init(&argc, &argv);

   // 创建3D网格
   int n = 1; // 网格划分数量
   Mesh mesh = Mesh::MakeCartesian3D(n, n, n, Element::TETRAHEDRON, 2.0, 3.0, 5.0);

   // 将Mesh转换为ParMesh
   ParMesh pmesh(MPI_COMM_WORLD, mesh);

   // 定义高阶Nedelec空间
   int order = 2; // 高阶
   ND_FECollection fec(order, pmesh.Dimension());
   ParFiniteElementSpace fespace(&pmesh, &fec);

    // 定义必要的边界条件
    Array<int> ess_bdr(pmesh.bdr_attributes.Max());
    ess_bdr = 1;  // 假设所有边界属性都是必要的

    Array<int> ess_tdof_list;
    fespace.GetEssentialTrueDofs(ess_bdr, ess_tdof_list);

    // 创建线性系统
    OperatorHandle A;
    Vector B, X;
    a.FormLinearSystem(ess_tdof_list, X, B, A);

    // 使用 Hypre AMS 求解器
    HypreAMS solver(A.As<HypreParMatrix>(), &fespace);
    solver.SetPrintLevel(1); // 设置打印级别以观察输出
    solver.Mult(B, X); // 解决线性系统

   // 检查收敛
   double error = B.Norml2();
   if (error < 1e-6)
   {
      std::cout << "Test passed, error = " << error << std::endl;
   }
   else
   {
      std::cout << "Test failed, error = " << error << std::endl;
   }

   // 清理资源
   MPI_Finalize();

   return 0;
}
