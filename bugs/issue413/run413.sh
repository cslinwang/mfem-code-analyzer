# 运行
cd /root/mfem/examples
export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
valgrind --leak-check=full mpirun -n 2 ./413