#include "mfem.hpp"
#include <fstream>
#include <iostream>

using namespace std;
using namespace mfem;

int main()
{
    // 创建一个简单的操作符，比如一个5x5的单位矩阵
    DenseMatrix A(5);
    A = 0.0;
    for (int i = 0; i < 5; ++i)
        A(i, i) = 1.0;

    // 在这里，A已经是一个Operator
    double scaling_factor = 2.0; // 选择一个缩放因子
    ScaledOperator scaled_op(&A, scaling_factor);

    // 创建向量进行测试
    Vector x(5), y(5), y_true(5);
    for (int i = 0; i < 5; ++i)
        x(i) = i;

    // 测试ScaledOperator
    scaled_op.Mult(x, y);
    cout << "ScaledOperator Mult result: ";
    y.Print(cout, 5);

    // scaled_op.MultTranspose(x, y_true);
    // cout << "ScaledOperator MultTranspose result: ";
    // y_true.Print(cout, 5);

    return 0;
}
