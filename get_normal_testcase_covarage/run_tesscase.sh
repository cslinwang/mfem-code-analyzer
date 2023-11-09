#!/bin/bash

test_case="${1:-"PA VectorDivergence"}"

echo "开始运行测试用例 $test_case ..."

# 进入测试用例的目录
cd /root/mfem/build/tests/unit

# 获取测试用例列表并将其存储到变量 test_case_list 中
test_case_list=$(./unit_tests --list-test-names-only)

# 检查 "$test_case" 是否在 test_case_list 中
if [[ $test_case_list =~ "$test_case" ]]; then
  echo "$test_case 存在于测试用例列表中"
else
  echo "$test_case 不存在于测试用例列表中"
fi

# 运行测试用例，注意变量的使用方式，确保保留空格和引号
./unit_tests "$test_case"