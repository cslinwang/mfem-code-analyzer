#include "mfem.hpp"
using namespace mfem;
using namespace std;

int main()
{
    // 创建一个简单的网格
    Mesh mesh = Mesh::MakeCartesian2D(2, 2, Element::QUADRILATERAL);

    // 定义有限元空间
    H1_FECollection fec(1, mesh.Dimension());
    FiniteElementSpace fespace(&mesh, &fec);

    // 创建一个网格函数
    GridFunction grid_function(&fespace);
    grid_function = 1.0; // 只是一个示例值

    // 设置数据集名称，其中包含多个下划线
    string collection_name = "test_data_collection_with_underscores";

    // 创建并保存 VisIt 数据集
    VisItDataCollection data_collection(collection_name, &mesh);
    data_collection.RegisterField("Solution", &grid_function);
    data_collection.SetCycle(0);
    data_collection.SetTime(0.0);
    data_collection.Save();

    // 尝试重新加载数据集
    data_collection.Load(0);

    // 验证重新加载的数据（根据具体情况来实现验证逻辑）

    return 0;
}
