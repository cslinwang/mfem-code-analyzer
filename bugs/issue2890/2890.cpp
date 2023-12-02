#include "mfem.hpp"
using namespace mfem;
using namespace std;

int main(int argc, char *argv[])
{
    // 为避免歧义，显式地指定构造函数的所有参数
    Mesh *mesh = new Mesh(2, 2, 2, Element::HEXAHEDRON);

    // 创建测试空间 - 3D ND空间
    int order_nd = 2;
    FiniteElementCollection *fec_nd = new ND_FECollection(order_nd, 3);
    FiniteElementSpace *fespace_nd = new FiniteElementSpace(mesh, fec_nd);

    // 创建试验空间 - 3D H1空间
    int order_h1 = 2;
    FiniteElementCollection *fec_h1 = new H1_FECollection(order_h1, 3);
    FiniteElementSpace *fespace_h1 = new FiniteElementSpace(mesh, fec_h1);

    // 创建MixedBilinearForm
    MixedBilinearForm *a = new MixedBilinearForm(fespace_nd, fespace_h1);

    // 创建一个 VectorArrayCoefficient 对象
    VectorConstantCoefficient f(Vector(3, 1.0));

    // 添加边界积分器
    // 注意，这里我们使用了一个 ConstantCoefficient 对象
    a->AddDomainIntegrator(new VectorFEDivergenceIntegrator(f));

    // 组装MixedBilinearForm
    a->Assemble();

    // 应用边界条件
    a->Finalize();

    // 打印矩阵到标准输出，验证其尺寸
    SparseMatrix &mat = a->SpMat();
    mat.Print();

    // 清理资源
    delete a;
    delete fespace_h1;
    delete fec_h1;
    delete fespace_nd;
    delete fec_nd;
    delete mesh;

    return 0;
}
