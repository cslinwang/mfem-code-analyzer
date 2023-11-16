# MFEM Code Analyzer

## 项目结构说明

- mfem-code-analyzer
  - bugs
    - bugs.yaml 报错所有bug的信息
    - issue3804 测试用例对应issue
      - test_psubmesh.cpp 测试用例文件

  - get_normal_testcase_coverage 获取测试用例覆盖率
    - complete_mfem.sh 编译脚本
    - run_mfem_testcase.py 读取bugs.yaml，运行测试用例

## 测试说明

### 测试用例

mfem issue3840:
  bug sha: 86ec2bfa8d4b38f06f8699ddd853f785f19aec91
  修复sha: 8a9ca138551bb0b3668da6a40cd636985f21039e
  testcase: tests/unit/mesh/test_psubmesh.cpp
  url: https://github.com/mfem/mfem/commit/8a9ca138551bb0b3668da6a40cd636985f21039e

### 复现分析

每个测试用例都是位于原先的tests文件下的CPP，因此可以考虑：

将每个测试用例的修复版本放到指定文件夹下，即bugs。后续直接读取。

- bug的文件夹名字是bugsha-fixsha。

### 如何运行

记得先清空所有git无效文件

```

git clean -fd

```

#### 覆盖率

覆盖率(example)
原文

```
# Replace the default implicit rule for *.cpp files

%: $(SRC)%.cpp $(MFEM_LIB_FILE) $(CONFIG_MK)

    $(MFEM_CXX) $(MFEM_FLAGS) $< -o $@ $(MFEM_LIBS)
```

替换
```
# 添加覆盖率标志

CXXFLAGS += -fprofile-arcs -ftest-coverage
LDFLAGS += -lgcov

# Replace the default implicit rule for *.cpp files

%: $(SRC)%.cpp $(MFEM_LIB_FILE) $(CONFIG_MK)

    $(MFEM_CXX) $(MFEM_FLAGS) $(CXXFLAGS) $< -o $@ $(MFEM_LIBS) $(LDFLAGS)

```

覆盖率（unitest）

原文
```
# Flags used for compiling all source files.

MFEM_BUILD_FLAGS = $(MFEM_PICFLAG) $(MFEM_CPPFLAGS) $(MFEM_CXXFLAGS)\

 $(MFEM_TPLFLAGS) $(CONFIG_FILE_DEF)



# Rules for compiling all source files.

$(OBJECT_FILES): $(BLD)%.o: $(SRC)%.cpp $(CONFIG_MK)

    $(MFEM_CXX) $(MFEM_BUILD_FLAGS) -c $(<) -o $(@)
```

替换
```
CXXFLAGS += -fprofile-arcs -ftest-coverage
LDFLAGS += -lgcov

# Flags used for compiling all source files.

MFEM_BUILD_FLAGS = $(MFEM_PICFLAG) $(MFEM_CPPFLAGS) $(MFEM_CXXFLAGS)\

 $(MFEM_TPLFLAGS) $(CONFIG_FILE_DEF) $(CXXFLAGS)

# Rules for compiling all source files.

$(OBJECT_FILES): $(BLD)%.o: $(SRC)%.cpp $(CONFIG_MK)

    $(MFEM_CXX) $(MFEM_BUILD_FLAGS) -c $(<) -o $(@) $(LDFLAGS)
```


### 覆盖率增加脚本

/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh

```

# 如何运行单个测试用例


# 先编译全部

  cd mefm
  make all -j

        # 并行
        export OMPI_ALLOW_RUN_AS_ROOT=1
        export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

        cd mfem/mefem/examples
        mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 2413.cpp -o 2413 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt


        # 串行
        cd examples
        make ex0
        ./ex0

# 收集覆盖率

fastcov --gcov gcov --exclude /usr/include --include /root/mfem coverage.json
fastcov --lcov -o coverage.info
genhtml coverage.info --output-directory coverage_report

```

## BUG复现命令

### issue 3691成功

fix sha:a15866e212b167ab83d5384e7326cdd3fa0723b2
reset current branch to previous commit,hard reset
cd ~
cd mfem
make clean
make all -j
cd examples
mpirun -np 24 ex6p -m /root/mfem-code-analyzer/bugs/issue3691/p1_prism.msh -o 2

### issue 2884
(未复现) 编译就过不去。 修复版本编译也过不去。
url: https://github.com/mfem/mfem/issues/2884
修改test_pa_coeff.cpp中的测试用例Hcurl/Hdiv pa_coeff的299行的if语句为：mesh = Mesh::LoadFromFile("/root/mfem/data/star.mesh");
fix sha: 987d2e043bad3a99841b88354dce0c0932cb8642
cd ~
cd mfem
make clean
make unittest -j
cd tests/unit
./unit_tests --list-test-names-only
./unit_tests "Hcurl/Hdiv pa_coeff"

### issue 2878成功

url: https://github.com/mfem/mfem/issues/2878
bug sha:使用的是50cd7da165999d4c65a6875a24c39317acaa2c3e
修改ex3p.cpp中204行a->AddDomainIntegrator(new VectorFEMassIntegrator(*sigma)); 为：
a->AddDomainIntegrator(new VectorFEMassIntegrator(*sigma));
a->AddBoundaryIntegrator(new VectorFEMassIntegrator(*sigma));

fix sha: a4504c3c083e8d13c89c0cf72f8eb36ef3aed642
cd ~
cd mfem
make clean
make all -j
cd examples
mpirun -np 5 ex3p -m /root/mfem/data/beam-tet.mesh -o 1

### issue 2666
（未复现）

url: https://github.com/mfem/mfem/issues/2666
第一种：运行ex15p
作者可以在以下两个版本复现0843a87d7953cf23e556dcfd426d27bd9cfb3e21，9d8043b9e78dcdcd86639bbb28d3bd7b514fb5e2(这个编译不过去，这个是V4.3),我不行呜呜。修复版本跑了没问题，bug版本卡在一个地方不跑了。
cd mfem
make clean
make all -j
cd examples
mpirun -np 2 ex15p -m /root/mfem/data/escher.mesh -r 2 -tf 0.3 -est 1

第二种：运行作者提供的测试用例，已放入2666
报错：root@eaa7a2b03f3a:~/mfem/examples# mpirun -np 2 nc-tet-mwe -m /root/mfem/data/escher.mesh
--------------------------------------------------------------------------
mpirun was unable to find the specified executable file, and therefore
did not launch the job.  This error was first reported for process
rank 0; it may have occurred for other processes as well.

NOTE: A common cause for this error is misspelling a mpirun command
      line parameter option (remember that mpirun interprets the first
      unrecognized command line token as the executable).

Node:       eaa7a2b03f3a
Executable: nc-tet-mwe
--------------------------------------------------------------------------
2 total processes failed to start

cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 2666.cpp -o 2666 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
mpirun -np 2 nc-tet-mwe -m /root/mfem/data/escher.mesh

### 2982
（未复现）编译出错
url: https://github.com/mfem/mfem/issues/2982
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 2982.cpp -o 2982 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include ex1.cpp -o ex1 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
报错：
root@eaa7a2b03f3a:~/mfem/examples# mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 2982.cpp -o 2982 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
2982.cpp: In function ‘void transfer_field_distributed(mfem::ParGridFunction*, mfem::ParGridFunction*, double)’:
2982.cpp:46:5: error: ‘FindPointsGSLIB’ was not declared in this scope
   46 |     FindPointsGSLIB finder(MPI_COMM_WORLD);
      |     ^~~~~~~~~~~~~~~
2982.cpp:47:5: error: ‘finder’ was not declared in this scope; did you mean ‘rindex’?
   47 |     finder.SetDefaultInterpolationValue(NAN);
      |     ^~~~~~
      |     rindex
可能是FindPointsGSLIB依赖于外部库或模块,FindPointsGSLIB位于miniapps/gslib中的pfindpts和field-interp，应该要编译miniapps

### 2779成功
reset current branch to previous commit,hard reset
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 2779.cpp -o 2779 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
./2779

### 2559成功
reset current branch to previous commit,hard reset
去掉头文件#include "stokes.hpp"，因为编译不过去，然后把tst.cpp放入examples，把manifold.msh放入data
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include tst.cpp -o tst -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
mpirun -np 4 tst -m /root/mfem/data/manifold.msh


### 2413
（未复现）编译失败
url: https://github.com/mfem/mfem/issues/2413
作者提供的网格和用例都放入issues2413中了
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 2413.cpp -o 2413 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt

### 2144成功
切换privious commit和bug sha都可
make clean
make all -j
cd examples
make 2144
./2144
结果：
root@d8f6458e7cf3:~/mfem/mfem/examples# ./2144
***********************************************************
Nodes on N face: 2 3
Nodes on S face: 0 1
Nodes on E face: 1 3
Nodes on W face: 0 2
***********************************************************
[row 0]
 (1,1) (0,1) (3,1)
[row 1]
 (1,1) (0,1) (3,1)
[row 2]
[row 3]
 (1,1) (0,1) (3,1)

### 1937成功
切换privious commit和bug sha都可
把1937issue中的msh文件复制到data中，让ex1.cpp读取，运行会卡到这里不动，修复版本会跑出结果
make clean
make all -j
cd examples
./ex1
结果：
root@d8f6458e7cf3:~/mfem/mfem/examples# ./ex1
Options used:
   --mesh /root/mfem/mfem/data/periodic_no_affine.msh
   --order 1
   --no-static-condensation
   --no-partial-assembly
   --device cpu
   --visualization
Device configuration: cpu
Memory configuration: host-std

### 1930成功
issue中的1930放入examples中
bug sha:4bc51ae3b85d91e6d51320236101b9b815742b0d
make clean
make all -j
cd examples
make 1930
./1930
结果：
root@d8f6458e7cf3:~/mfem/mfem/examples# ./1930
[row +0]
+1.100000e+01 +1.200000e+01 +2.100000e+01 +2.200000e+01

[row +1]
+1.300000e+01 +1.400000e+01

BlockMatrix::Elem
Aborted (core dumped)

### 1928成功
privious commit
将square_2mat_per.msh放入data，将test_full_periodic放入examples
make clean
make all -j
cd examples
make test_full_periodic
./test_full_periodic
root@d8f6458e7cf3:~/mfem/mfem/examples# ./test_full_periodic
Options used:
   --mesh /root/mfem/mfem/data/square_2mat_per.msh
   --order 1
   --tcase 1
Number of finite element unknowns: 34 ndof: 17 dim: 2
Assembling: Size of linear system: 34
   Iteration :   0  (B r, r) = 55.2655
   Iteration :   1  (B r, r) = 0.236595
   Iteration :   2  (B r, r) = 0.211833
   Iteration :   3  (B r, r) = 0.192955
   Iteration :   4  (B r, r) = 0.0125361
   Iteration :   5  (B r, r) = 0.00605776
   Iteration :   6  (B r, r) = 0.00605607
   Iteration :   7  (B r, r) = 0.000233384
   Iteration :   8  (B r, r) = 2.66252e-06
   Iteration :   9  (B r, r) = 7.90989e-08
   Iteration :  10  (B r, r) = 1.66475e-09
   Iteration :  11  (B r, r) = 1.21259e-11
   Iteration :  12  (B r, r) = 8.69257e-14
   Iteration :  13  (B r, r) = 1.36064e-16
   Iteration :  14  (B r, r) = 4.44607e-19
Average reduction factor = 0.191576

tcase 1 -- L2 norm: 0.151905
Fail

### 1413失败
privious commit
将1413_2放入examples
make clean
make all -j
cd examples
make 1413_2
for i in {1..10000}; do ./1413_2; done

### 1326失败
privious commit
将serior放入examples
make clean
make all -j
cd examples
make serior
./serior

### 1322失败
无论哪个sha都是以下结果：
root@d8f6458e7cf3:~/mfem/mfem/examples# ./1322
Options used:
   --device cpu
Device configuration: cpu
0 0 0 0 0 0 0 0
1 1 1 1 1 1 1 1
2 2 2 2 2 2 2 2

### 685成功
privious commit
将685.cpp放入examples
make clean
make all -j
cd examples
make 685
./685
[row +1]
+3.026530e-02 -4.801480e-01 +4.820680e-01 +4.719240e-01
修复版本下[row +1]
+3.026530e-02 +1.198990e-03 +4.820680e-01 +4.719240e-01

### 516成功
privious commit
将516.cpp放入examples
make clean
make all -j
cd examples
make 516
./516
root@d8f6458e7cf3:~/mfem/mfem/examples# ./516
munmap_chunk(): invalid pointer
Aborted (core dumped)

### 512
privious commit
修改ex6,在140行的for循环内插入：
      Vector v1, v2;
      mesh.PrintCharacteristics(&v1, &v2, std::cout);
且修改为const int max_dofs = 500000;
网格文件替换：const char *mesh_file = "/root/mfem/mfem/data/inline-tet.mesh";
make clean
make all -j
cd examples
./ex6
结果：kappa max：
2.56155
3.94272
6.24804
6.98736
6.98736
9.44001
11.4124
29.8203
29.8203
29.8203
34.5041
34.5041
41.3223
41.3223
41.3223
42.2025