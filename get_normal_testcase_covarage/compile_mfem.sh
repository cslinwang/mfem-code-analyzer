#!/bin/bash


full_sha="${1:-b5491f763085b3cc917fed34a58ee816c1bc0cc9}"
is_fortan_replaced="${2:---none}"
mpirun_n="${3:-1}"
build_dir="${4:-ompi_gnu_linux}"
is_build="false"

echo "切换分支开始..."

# Extract short SHA from full SHA.
short_sha=$(echo "$full_sha" | cut -c 1-7)

# Reset repository and checkout master branch.
cd /root/mfem/mfem
git reset --hard HEAD
# 清理所有未跟踪的文件和目录
git clean -fdx
git checkout master

# Delete branch if it exists.
if git show-ref --quiet "refs/heads/$short_sha"; then
  git branch -D "$short_sha"
fi

# Create a new branch based on the specified SHA.
git checkout -b "$short_sha" "$full_sha"

echo "已切换到分支 $short_sha。"
echo "开始修改makefile，以支持代码覆盖率..."

# 增加覆盖率
## TODO

# 编译
mkdir build
cd build
cmake ..
make -j $(nproc)
make install
# 编译测试用例
cd tests
make -j $(nproc)
