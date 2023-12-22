# 编译 cd
# /root/mfem_issue3436/ 这个路径要改，改成 cd /root/mfem 因为到时候要复制一份，重命名成mfem运行。
# 现在是临时测试
# cd /root/mfem_issue3332/
cd /root/mfem/
make clean
find /root/mfem \( -name '*.gcda' -o -name '*.gcov' \) -delete
export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
# make all -j 这个命令可以优化，
make all -j
# make serial -j 编译串行
# make parallel -j 编译并行
# make examples -j 编译所有example
# make parallel -j
