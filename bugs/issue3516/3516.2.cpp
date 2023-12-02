#include "mfem.hpp"

using namespace mfem;

int main()
{
    // 假设每个块的大小是10
    int block_size = 10;
    Array<int> block_offsets(3); // 假设有2个block，所以需要3个偏移量
    block_offsets[0] = 0;
    block_offsets[1] = block_size;
    block_offsets[2] = 2 * block_size;

    // 使用行和列的偏移量创建BlockOperator
    BlockOperator *block_op = new BlockOperator(block_offsets, block_offsets);

    // 创建一些示例操作符并添加到BlockOperator中
    for (int i = 0; i < 2; ++i) // 2个块
    {
        for (int j = 0; j < 2; ++j)
        {
            Operator *op = new DenseMatrix(block_size, block_size);
            block_op->SetBlock(i, j, op, true);
        }
    }

    // 删除BlockOperator
    delete block_op;

    return 0;
}
