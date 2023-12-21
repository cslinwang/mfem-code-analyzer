#include "mfem.hpp"
#include <iostream>
#ifdef __GNUC__
extern "C" void __gcov_flush(void);
#endif
using namespace mfem;
using namespace std;

int main()
{
    // 创建两个DenseTensor对象
    int dim1 = 2, dim2 = 3, dim3 = 4;
    DenseTensor dt1(dim1, dim2, dim3);
    DenseTensor dt2(dim3, dim2, dim1);

    // 手动填充DenseTensor对象
    for (int i = 0; i < dt1.SizeI(); i++) {
        for (int j = 0; j < dt1.SizeJ(); j++) {
            for (int k = 0; k < dt1.SizeK(); k++) {
                dt1(i, j, k) = (double)rand() / RAND_MAX;
            }
        }
    }
    for (int i = 0; i < dt2.SizeI(); i++) {
        for (int j = 0; j < dt2.SizeJ(); j++) {
            for (int k = 0; k < dt2.SizeK(); k++) {
                dt2(i, j, k) = (double)rand() / RAND_MAX;
            }
        }
    }

    // 打印原始尺寸
    cout << "Original dt1 sizes: " << dt1.SizeI() << ", " << dt1.SizeJ() << ", " << dt1.SizeK() << endl;
    cout << "Original dt2 sizes: " << dt2.SizeI() << ", " << dt2.SizeJ() << ", " << dt2.SizeK() << endl;

    // 交换两个DenseTensor对象
    dt1.Swap(dt2);

    // 打印交换后的尺寸
    cout << "Swapped dt1 sizes: " << dt1.SizeI() << ", " << dt1.SizeJ() << ", " << dt1.SizeK() << endl;
    cout << "Swapped dt2 sizes: " << dt2.SizeI() << ", " << dt2.SizeJ() << ", " << dt2.SizeK() << endl;

    return 0;
}
