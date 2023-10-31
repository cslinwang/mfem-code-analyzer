#!/bin/bash

# 脚本输入为：测试用例文件路径，覆盖率保存路径

# 脚本输入参数
test_case_file=$1  # 测试用例文件路径
coverage_save_path=$2  # 覆盖率保存路径
is_fortan_replaced="${3:---none}"
mpirun_n="${4:-1}"
build_dir="${5:-ompi_gnu_linux}"
is_build="false"
test_case_path=$(dirname "$test_case_file")
coverage_save_path=$(realpath "$coverage_save_path")
# 1. 清空覆盖率文件
echo "删除历史覆盖率信息"
find /home/my/fds \( -name '*.gcda' -o -name '*.gcov' \) -delete

# 2. 运行测试用例
cd ~/fds
echo "开始运行样例..."
# Check if make_fds.sh exists in the specified build directory.
if ls "Build/$build_dir" &>/dev/null && [ -f "Build/$build_dir/make_fds.sh" ]; then
  is_build="true"
  # Run FDS using mpirun.
  cd $test_case_path
  # Print cmd.
  cmd="mpirun -n $mpirun_n -oversubscribe ~/fds/Build/$build_dir/fds_$build_dir $test_case_file"
  echo "如果运行样例失败，请运行下列命令(自行修改 -n 后边的数字)："
  echo $cmd

  mpirun -n $mpirun_n -oversubscribe /home/my/fds/Build/$build_dir/fds_$build_dir $test_case_file
  # Print cmd.
  cmd="mpirun -n $mpirun_n -oversubscribe ~/fds/Build/$build_dir/fds_$build_dir $test_case_file"
  echo "如果运行样例失败，请运行下列命令(自行修改 -n 后边的数字)："
  echo $cmd

# else
#   echo "Makefile or make_fds.sh not found in Build/$build_dir directory."
fi

# Check if make_fds.sh exists in the mpi_gnu_linux_64 directory.
build_dir="mpi_gnu_linux_64"

if ls "Build/$build_dir" &>/dev/null && [ -f "Build/$build_dir/make_fds.sh" ]; then
  # Remove all files except for .sh files in the build directory.
  is_build="true"

  # Run FDS using mpirun.
  cd $test_case_path
  # Print cmd.
  cmd="mpirun -n $mpirun_n -oversubscribe ~/fds/Build/$build_dir/fds_$build_dir $test_case_file"
  echo "如果运行样例失败，请运行下列命令(自行修改 -n 后边的数字)："
  echo $cmd

  mpirun -n $mpirun_n -oversubscribe /home/my/fds/Build/$build_dir/fds_$build_dir $test_case_file
  # Print cmd.
  cmd="mpirun -n $mpirun_n -oversubscribe ~/fds/Build/$build_dir/fds_$build_dir $test_case_file"
  echo "如果运行样例失败，请运行下列命令(自行修改 -n 后边的数字)："
  echo $cmd

# else
#   echo "Makefile or make_fds.sh not found in Build/$build_dir directory."
fi

# Check if no build is found
if [ "$is_build" = "false" ]; then
  echo "在指定的目录中未找到编译文件, 请联系脚本作者。"
  echo "No build found in the specified directory."
else
  # 收集并保存覆盖率文件
  cd ~
  echo "开始生成代码覆盖率报告..."
  python3 -m gcovr --html -o ${coverage_save_path}/report.html -r /home/my/fds
  python3 -m gcovr --json -o ${coverage_save_path}/report.json -r /home/my/fds
  echo "代码覆盖率报告生成完成。路径："
  echo "$coverage_save_path"
fi
# End of script.