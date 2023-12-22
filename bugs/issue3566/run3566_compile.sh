# 测试用
# cd /root/mfem_issue3566/
# 实际用
cd /root/mfem/

# 编译
make clean
find /root/mfem \( -name '*.gcda' -o -name '*.gcov' \) -delete
export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
make all -j
# make examples -j
# make serial -j
# make parallel -j
