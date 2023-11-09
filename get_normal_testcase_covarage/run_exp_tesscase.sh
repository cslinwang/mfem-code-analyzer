#!/bin/bash

test_case="${1:-"ex5"}"

echo "开始运行测试用例 $test_case ..."

# 进入测试用例的目录
cd /root/mfem/build/examples

# 运行测试用例，注意变量的使用方式，确保保留空格和引号
./"$test_case"