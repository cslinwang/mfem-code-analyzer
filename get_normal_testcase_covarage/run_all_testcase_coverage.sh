#!/bin/bash

export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
# 输入 默认两个值都是sha
# git_sha="${1:-9d8043b9e78dcdcd86639bbb28d3bd7b514fb5e2}"
# git_version="${2:-MFEM4.3}"
# git_sha="${1:-ed5604e0d350461f20842275578aa2f9e6a61343}"
# git_version="${2:-MFEM4.2}"
# git_sha="${1:-0715efbaf95990a4e76380ac69337096b1cd347d}"
# git_version="${2:-MFEM3.4}"
# git_sha="${1:-b7a4b61b5ce80b326a002aebccf7da7ad2432556}"
# git_version="${2:-MFEM4.5}"
# git_sha="${1:-00b2a0705f647e17a1d4ffcb289adca503f28d42}"
# git_version="${2:-MFEM4.5.2}"
# git_sha="${1:-c55c80d17b82d80de04b849dd526e17044f8c99a}"
# git_version="${2:-MFEM4.0.1}"
# git_sha="${1:-ff9819e4953668c38931f8aff27b403f34180af4}"
# git_version="${2:-MFEM4.0-rc1}"
git_sha="${1:-bc6b48421ac6506db6fea2f9d6222f145427f8c8}"
git_version="${2:-MFEM3.3.2}"
bash_start_time=$(date +%s.%N)

# 清空文件夹
testcase_coverage_save_file="/root/mfem_coverage/$git_version"
rm -rf $testcase_coverage_save_file
# 获取脚本的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
# 清除日志
rm -rf ./run_log.log
exec &> >(tee -a "./run_log.log")

# 1. 编译当前版本的FDS
echo "开始编译MFEM..."
# 切换版本
./switch_sha.sh $git_sha
# 编译
./add_coverage.sh
# 编译并检查是否出现特定错误
compile_status=$?

# 检查编译状态
if [ $compile_status -ne 0 ]; then
  # 检查日志文件中是否有特定的错误消息
  if grep -q "constexpr std::size_t sigStackSize" "./run_log.log"; then
    echo "特定错误发现：constexpr std::size_t sigStackSize。停止执行。"
    exit 1
  fi
fi


# 2. 循环运行样例
echo "开始运行样例..."
echo "开始运行example样例..."
# 2.1 运行example样例
cd ~/mfem/examples
# 计数器，用于统计可执行文件数量
count=0

# 循环遍历目录中的所有文件
for file in *; do
    # 检查文件是否为可执行文件
    if [[ -x "$file" && ! -d "$file" ]]; then
        # 如果是可执行文件，增加计数器
        count=$((count+1))
        # 清空覆盖率信息
        find ~/mfem \( -name '*.gcda' -o -name '*.gcov' \) -delete
        # 创建保存覆盖率的文件夹
        testcase_coverage_save_path="/root/mfem_coverage/$git_version/$file"
        mkdir -p $testcase_coverage_save_path
        # 执行文件
        echo "正在执行：$file"
        # 获取开始时间
        start_time=$(date +%s.%N)
        echo c | ./"$file"
        # 获取结束时间
        end_time=$(date +%s.%N)
        # 计算并输出运行时间
        duration=$(echo "$end_time - $start_time" | bc)
        echo "测试 $file 运行时间：$duration 秒"
        # 生成覆盖率报告
        fastcov --gcov gcov --exclude /usr/include --include /root/mfem -o $testcase_coverage_save_path/coverage.json
        fastcov --lcov -o $testcase_coverage_save_path/coverage.info
        genhtml $testcase_coverage_save_path/coverage.info --output-directory $testcase_coverage_save_path/coverage_report
    fi
done
echo "example样例共计 $count 个。"
echo "example样例运行完毕。"
# 2.2 运行unit_tests样例
echo "开始运行unit_tests样例..."
cd /root/mfem/tests/unit
# 计数器，用于统计可执行文件数量
count=0
# 保存原始的 IFS
OLDIFS=$IFS

# 设置 IFS 为换行符
IFS=$'\n'

# 获取并存储所有测试名称，跳过第一行
test_names=$(./unit_tests --list-test-names-only | tail -n +2)

# 遍历并执行每个测试
for test_name in $test_names; do
    # 如果是可执行文件，增加计数器
    count=$((count+1))
    # 清空覆盖率信息
    find ~/mfem \( -name '*.gcda' -o -name '*.gcov' \) -delete
    # 创建保存覆盖率的文件夹
    testcase_coverage_save_path="/root/mfem_coverage/$git_version/$test_name"
    mkdir -p $testcase_coverage_save_path
    # 执行文件
    echo "正在执行测试：$test_name"
    # ./unit_tests "VTU XML Reader"
    # 获取开始时间
    start_time=$(date +%s.%N)
    ./unit_tests "$test_name"
    # 获取结束时间
    end_time=$(date +%s.%N)
     # 计算并输出运行时间
    duration=$(echo "$end_time - $start_time" | bc)
    echo "测试 $test_name 运行时间：$duration 秒"
    # 生成覆盖率报告
    fastcov --gcov gcov --exclude /usr/include --include /root/mfem -o $testcase_coverage_save_path/coverage.json
    fastcov --lcov -o $testcase_coverage_save_path/coverage.info
    genhtml $testcase_coverage_save_path/coverage.info --output-directory $testcase_coverage_save_path/coverage_report
done
echo "unit_tests样例共计 $count 个。"
echo "unit_tests样例运行完毕。"
# 恢复原始的 IFS
IFS=$OLDIFS

echo -e "\n所有测试用例运行完毕。"
bash_end_time=$(date +%s.%N)
# 计算并输出运行时间
duration=$(echo "$bash_end_time - $bash_start_time" | bc)
echo "测试 总 运行时间：$duration 秒"
# End of script.
