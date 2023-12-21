# 编译 cd
# /root/mfem_issue3436/ 这个路径要改，改成 cd /root/mfem 因为到时候要复制一份，重命名成mfem运行。
# 现在是临时测试
# cd /root/mfem_issue3328/
cd /root/mfem/
make clean
find /root/mfem \( -name '*.gcda' -o -name '*.gcov' \) -delete
# make all -j 这个命令可以优化，
# make all -j
# make serial -j 编译串行
# make parallel -j 编译并行
make examples -j
# make parallel -j
# 运行
cd examples
make 3328
./3328