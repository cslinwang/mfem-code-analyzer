#!/bin/bash

# 定义根目录
ROOT_DIR="/root/mfem-code-analyzer/mutate/result"

# 遍历根目录下的所有一级子目录
for dir in "$ROOT_DIR"/issue*; do
    # 检查是否为目录
    if [ -d "$dir" ]; then
        # 在每个一级子目录内，删除除了 all_branch.xlsx 以外的所有文件和文件夹
        find "$dir" -mindepth 1 ! -name "all_branch.xlsx" -exec rm -rf {} +

        # 检查是否删除操作成功
        if [ $? -ne 0 ]; then
            echo "删除 $dir 中的文件和文件夹（除了 all_branch.xlsx）失败"
        else
            echo "删除 $dir 中的文件和文件夹（除了 all_branch.xlsx）成功"
        fi
    fi
done

echo "所有操作完成。"
