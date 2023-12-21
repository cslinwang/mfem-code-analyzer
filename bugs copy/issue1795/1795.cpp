#include "mfem.hpp"
using namespace mfem;
using namespace std;

int main()
{
    // 创建一个小的 2D 网格
    Mesh mesh = Mesh::MakeCartesian2D(4, 4, Element::QUADRILATERAL);

    // 定义一个有限元空间
    H1_FECollection fec(1, mesh.Dimension());
    FiniteElementSpace fespace(&mesh, &fec);

    // 创建一个线性系统
    BilinearForm bilinear_form(&fespace);
    bilinear_form.AddDomainIntegrator(new DiffusionIntegrator);
    bilinear_form.Assemble();
    bilinear_form.Finalize();
    SparseMatrix *matrix = bilinear_form.SpMat().Clone();

    // 创建一个 HypreSmoother 对象
    HypreSmoother smoother;
    smoother.SetType(5); // 设置为 "lumped Jacobi"

    // 使用第一个矩阵
    smoother.SetOperator(*matrix);
    smoother.Mult(matrix->GetRow(0), matrix->GetRow(0));

    // 改变矩阵并再次使用 HypreSmoother
    bilinear_form *= 2.0; // 修改矩阵的值
    smoother.SetOperator(*matrix); // 重新设置操作符
    smoother.Mult(matrix->GetRow(0), matrix->GetRow(0));

    delete matrix;

    return 0;
}
