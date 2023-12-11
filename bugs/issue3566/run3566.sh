# 测试用
# cd /root/mfem_issue3566/
# 实际用
cd /root/mfem/

# 编译
make clean
make all -j
# make examples -j
# make serial -j
# make parallel -j

# 运行
cd tests/unit
valgrind --leak-check=full ./unit_tests PAIdentityInterp
