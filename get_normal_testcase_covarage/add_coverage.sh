#!/bin/bash
# 覆盖率增加脚本

# 进入mfem项目目录
# cd /root/mfem || exit 1 # 用实际路径替换 /path/to/mfem

# 清理构建和 Git 未跟踪文件
# make clean
# git clean -fdx
# git reset --hard

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
# make parallel -j
make serial -j # 使用适当数量的作业
make all -j # 使用适当数量的作业
exit 0
make clean
git clean -fdx
git reset --hard
/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
