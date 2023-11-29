#!/bin/bash

# 进入 mfem/examples 目录
cd ~/mfem/examples

# 计数器，用于统计可执行文件数量
count=0

# 循环遍历目录中的所有文件
for file in *; do
    # 检查文件是否为可执行文件
    if [[ -x "$file" && ! -d "$file" ]]; then
        # 如果是可执行文件，增加计数器
        count=$((count+1))
        # 执行文件
        echo "正在执行：$file"
        ./"$file"

    fi
done

# 打印可执行文件的总数
echo "可执行文件总数：$count"
