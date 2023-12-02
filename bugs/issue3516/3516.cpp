#include "mfem.hpp"

using namespace mfem;

int main()
{
    // 初始化一个小尺寸的块操作符
    int block_size = 2; // 假设有2个block
    BlockOperator *block_op = new BlockOperator(block_size, block_size);

    // 创建一些示例操作符并添加到BlockOperator中
    for (int i = 0; i < block_size; ++i)
    {
        for (int j = 0; j < block_size; ++j)
        {
            Operator *op = new DenseMatrix(10, 10); // 使用任意尺寸的DenseMatrix作为操作符
            block_op->SetBlock(i, j, op, true); // BlockOperator将拥有这个操作符并负责删除
        }
    }

    // 删除BlockOperator，此时应调用BlockOperator的析构函数
    delete block_op;

    // 程序结束后，检查是否有内存泄漏或其他异常
    return 0;
}
