#include "mfem.hpp"
#include <iostream>
#include <fstream>

using namespace std;
using namespace mfem;

int main()
{
    // 指定VTK文件的路径
    const char *filename = "/root/mfem-code-analyzer/bugs/issue2001/2001.vtk";

    // 尝试读取VTK文件
    ifstream vtk_file(filename);
    if (!vtk_file)
    {
        cerr << "无法打开VTK文件: " << filename << endl;
        return 1;
    }

    // 创建Mesh对象并从VTK文件加载网格
    Mesh *mesh = NULL;
    try
    {
        mesh = new Mesh(vtk_file, 1, 1, false);
    }
    catch (const exception &e)
    {
        cerr << "读取VTK文件时出错: " << e.what() << endl;
        return 2;
    }

    // 打印网格信息
    cout << "成功加载VTK网格！" << endl;
    cout << "网格中的元素数量: " << mesh->GetNE() << endl;
    cout << "网格中的顶点数量: " << mesh->GetNV() << endl;

    // 清理资源
    delete mesh;

    return 0;
}
