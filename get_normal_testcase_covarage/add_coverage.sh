#!/bin/bash
# 覆盖率增加脚本

# 设置环境变量
export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

# 进入mfem项目目录
cd /root/mfem || exit 1
# cd /root/mfem || exit 1 # 用实际路径替换 /path/to/mfem

# 清理构建和 Git 未跟踪文件
# make clean
# git clean -fdx
# git reset --hard
# 清除覆盖率信息
find /root/mfem \( -name '*.gcda' -o -name '*.gcov' \) -delete

# 使用 awk 进行替换
awk '
    /^# The default value of CXXFLAGS is based on the value of MFEM_DEBUG/,/^CXXFLAGS \?=/ {
        if (!done) {
            print "# 添加覆盖率标志\nCOVERAGE_FLAGS := -fprofile-arcs -ftest-coverage\n"
            print "# The default value of CXXFLAGS is based on the value of MFEM_DEBUG"
            print "ifeq ($(MFEM_DEBUG),YES)"
            print "   CXXFLAGS ?= $(DEBUG_FLAGS) $(COVERAGE_FLAGS)"
            print "else"
            print "   CXXFLAGS ?= $(OPTIM_FLAGS) $(COVERAGE_FLAGS)"
            print "endif\n"
            print "LDFLAGS += -lgcov"
            done = 1
        }
        next
    }
    { print }
' makefile > makefile.tmp && mv makefile.tmp makefile

# 运行配置和编译命令
make config
# 串行 make serial -j
make parallel -j
# make serial -j # 使用适当数量的作业
make all -j # 使用适当数量的作业

#############################################
# 常用命令
exit 0
make clean
git clean -fdx
git reset --hard
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh

rm -rf hypre
ln -s hypre-2.26.0 hypre

rm -rf hypre
ln -s hypre-2.20.0 hypre

# rm -rf hypre
# ln -s hypre-2.10.0b hypre

hypre-2.10.0b
hypre-2.20.0
hypre-2.26.0
fastcov --gcov gcov --exclude /usr/include --include /root/mfem coverage.json
fastcov --lcov -o coverage.info
genhtml coverage.info --output-directory coverage_report

tar -czvf mfem_bug.tar.gz /root/mfem-code-analyzer
tar -czvf mfem_pass.tar.gz /root/mfem_coverage

#ifdef __GNUC__
extern "C" void __gcov_flush(void);
#endif

__gcov_flush(); // 强制写入覆盖率数据

## 报错 unittestcase 无法编译的情况

根据报错情况，定位到报错位置，应该是
catch.hpp中的：
     constexpr std::size_t sigStackSize = 32768 >= MINSIGSTKSZ ? 32768 : MINSIGSTKSZ;
将其改为：
    constexpr std::size_t sigStackSize = 32768;
即可
make test

## 删除gcno文件
find . -name "*.gcno" -exec rm {} \;
# 清除覆盖率信息
find /root/mfem \( -name '*.gcda' -o -name '*.gcov' \) -delete

