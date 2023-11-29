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

git clean -fdx
make clean

```

#### 覆盖率

1. 覆盖率(example)
将原文

```
# Replace the default implicit rule for *.cpp files

%: $(SRC)%.cpp $(MFEM_LIB_FILE) $(CONFIG_MK)

    $(MFEM_CXX) $(MFEM_FLAGS) $< -o $@ $(MFEM_LIBS)
```

替换为
```

# 添加覆盖率标志

CXXFLAGS += -fprofile-arcs -ftest-coverage
LDFLAGS += -lgcov

# Replace the default implicit rule for *.cpp files

%: $(SRC)%.cpp $(MFEM_LIB_FILE) $(CONFIG_MK)

    $(MFEM_CXX) $(MFEM_FLAGS) $(CXXFLAGS) $< -o $@ $(MFEM_LIBS) $(LDFLAGS)

```

覆盖率（mfem）

将原文
```
# Flags used for compiling all source files.
MFEM_BUILD_FLAGS = $(MFEM_PICFLAG) $(MFEM_CPPFLAGS) $(MFEM_CXXFLAGS)\
 $(MFEM_TPLFLAGS) $(CONFIG_FILE_DEF)

# Rules for compiling all source files.
$(OBJECT_FILES): $(BLD)%.o: $(SRC)%.cpp $(CONFIG_MK)
    $(MFEM_CXX) $(MFEM_BUILD_FLAGS) -c $(<) -o $(@)
```

替换为（$(MFEM_CXX)前面是tab空格）
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
复现bug后收集覆盖率命令：
fastcov --gcov gcov --exclude /usr/include --include /root/mfem coverage.json
fastcov --lcov -o coverage.info
genhtml coverage.info --output-directory coverage_report

### 覆盖率增加脚本

/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh

### 覆盖率增加2.0

先清空历史

make clean
git clean -fdx
git reset --hard

原文：

```

# The default value of CXXFLAGS is based on the value of MFEM_DEBUG
ifeq ($(MFEM_DEBUG),YES)
   CXXFLAGS ?= $(DEBUG_FLAGS)
endif
CXXFLAGS ?= $(OPTIM_FLAGS)


```

替换：

```

# 添加覆盖率标志
COVERAGE_FLAGS := -fprofile-arcs -ftest-coverage

# The default value of CXXFLAGS is based on the value of MFEM_DEBUG
ifeq ($(MFEM_DEBUG),YES)
   CXXFLAGS ?= $(DEBUG_FLAGS) $(COVERAGE_FLAGS)
endif
CXXFLAGS ?= $(OPTIM_FLAGS) $(COVERAGE_FLAGS)

LDFLAGS += -lgcov

```

然后运行命令

make config
make all -j

```
# 如何运行单个测试用例


# 先编译全部

cd mfem

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

```

## BUG复现命令

# v201

### issue 3691成功，但没有覆盖率
fix sha:a15866e212b167ab83d5384e7326cdd3fa0723b2
reset current branch to previous commit,hard reset
cd ~
cd mfem
make clean
make all -j
cd examples
mpirun -np 24 ex6p -m /root/mfem-code-analyzer/bugs/issue3691/p1_prism.msh -o 2

```

### issue 3566成功.
内存泄漏问题，不报错：
privious commit
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd ~/mfem/mfem/build/tests/unit
valgrind --leak-check=full ./unit_tests SubMesh
结果：
==267697== LEAK SUMMARY:
==267697==    definitely lost: 327,208 bytes in 192 blocks
==267697==    indirectly lost: 5,209,184 bytes in 24,887 blocks
==267697==      possibly lost: 14,520 bytes in 1 blocks
==267697==    still reachable: 0 bytes in 0 blocks
==267697==         suppressed: 0 bytes in 0 blocks
==267697==
==267697== For lists of detected and suppressed errors, rerun with: -s
==267697== ERROR SUMMARY: 20 errors from 20 contexts (suppressed: 0 from 0)

### issue 3332成功.
privious commit
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd ~/mfem/tests/unit
./unit_tests SubMesh

### issue3328成功
privious commit
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
把3328.cpp放入examples
cd examples
make 3328
./3328

### issue 2884失败
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

### issue 2878成功，但没有覆盖率
没有gcda文件，覆盖率失败
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
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 2878.cpp -o 2878 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
mpirun -np 5 2878 -m /root/mfem/data/beam-tet.mesh -o 1

### issue 2666成功，但没有覆盖率
覆盖率失败，没有gcno文件
url: https://github.com/mfem/mfem/issues/2666
第一种：运行ex15p
bug sha: 0843a87d7953cf23e556dcfd426d27bd9cfb3e21。
修复版本跑了没问题，bug版本卡在一个地方不跑了。
cd mfem
make clean
make all -j
cd examples
mpirun -np 2 ex15p -m /root/mfem/data/escher.mesh -r 2 -tf 0.3 -est 1

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

### 2779成功.
reset current branch to previous commit,hard reset
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 2779.cpp -o 2779 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
添加覆盖率：mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 2779.cpp -o 2779 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
./2779

### 2559成功.
reset current branch to previous commit,hard reset
去掉头文件#include "stokes.hpp"，因为编译不过去，然后把tst.cpp放入examples，把manifold.msh放入data
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include tst.cpp -o tst -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
（添加覆盖率的话使用：mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include tst.cpp -o tst -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov）

mpirun -np 4 tst -m /root/mfem-code-analyzer/bugs/issue2559/manifold.msh

### 1230成功.
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 1230.cpp -o 1230 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
mpirun -np 4 1230

### 1238成功.
rm -rf hypre
ln -s hypre-2.20.0 hypre
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 1238.cpp -o 1238 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
valgrind --leak-check=full mpirun -np 2 1238

### 2343成功.
切换到34ad9fca157368768af1869e9821876cf259f940
先使用三条命令清理，然后注释
将2343中的用例放入bug版本中
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd tests/unit
./unit_tests "First order ODE methods"
结果：
test cases:  1 |  0 passed | 1 failed
assertions: 33 | 26 passed | 7 failed

## 3332成功
切换到973b42c57a60ea4844dd09ff38e47ed89ead93ad
先使用三条命令清理，然后注释
将3332中的用例放入bug版本中
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd tests/unit
./unit_tests "SubMesh"
结果：
test cases:   1 |   0 passed | 1 failed
assertions: 132 | 131 passed | 1 failed



## V1

## 2563成功.
将ex1中的mesh文件替换
const char *mesh_file = "/root/mfem/mfem-code-analyzer/bugs/issue2563/origin_mesh_tri.vtu";
/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
./ex5


## 3712没有覆盖率
bug sha: b5491f763085b3cc917fed34a58ee816c1bc0cc9
把3712用例替换到bug版本
/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd tests/unit
./unit_tests "PA VectorDivergence"

## 1284成功.
切换e6385f2992b9c2d9001265fe3283403bec30b417
make clean
git clean -fdx
git reset --hard
/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
./ex5
fastcov --gcov gcov --exclude /usr/include --include /root/mfem coverage.json
fastcov --lcov -o coverage.info
genhtml coverage.info --output-directory coverage_report

### 2413
（未复现）编译失败
url: https://github.com/mfem/mfem/issues/2413
作者提供的网格和用例都放入issues2413中了
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 2413.cpp -o 2413 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt

### 2144成功.
切换privious commit和bug sha都可
/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
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

### 1928成功.
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

### 1887成功.
先切换分支，然后修改ex1中的网格文件，将const char *mesh_file = "../data/star.mesh";修改为beam-wedge.vtk，然后编译和运行用例：
/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
./ex1
bug版结果：Elements with wrong orientation: 8 / 8 (NOT FIXED)

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

### 685成功.
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

### 512成功
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

### 443成功.

bug版本使用fix的用例，运行ex19
/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
./ex19

### 310成功
privious commit
将310.cpp放入examples
make clean
make all -j
cd examples
make 310
./310

root@d8f6458e7cf3:~/mfem/mfem/examples# ./310
Simple reproducer for Lagrange 1D bug
Sampling Lagrange1DFiniteElement of order 1
         for sample -5 with isopar -0.5 weights are {1.5,-0.5} -- sum is 1
         for sample -4 with isopar -0.4 weights are {1.4,-0.4} -- sum is 1
         for sample -3 with isopar -0.3 weights are {1.3,-0.3} -- sum is 1
         for sample -2 with isopar -0.2 weights are {1.2,-0.2} -- sum is 1
         for sample -1 with isopar -0.1 weights are {1.1,-0.1} -- sum is 1
         for sample 0 with isopar 0 weights are {1,0} -- sum is 1
         for sample 1 with isopar 0.1 weights are {0.9,0.1} -- sum is 1
         for sample 2 with isopar 0.2 weights are {0.8,0.2} -- sum is 1
         for sample 3 with isopar 0.3 weights are {0.7,0.3} -- sum is 1
         for sample 4 with isopar 0.4 weights are {0.6,0.4} -- sum is 1
         for sample 5 with isopar 0.5 weights are {0.5,0.5} -- sum is 1
         for sample 6 with isopar 0.6 weights are {0.4,0.6} -- sum is 1
         for sample 7 with isopar 0.7 weights are {0.3,0.7} -- sum is 1
         for sample 8 with isopar 0.8 weights are {0.2,0.8} -- sum is 1
         for sample 9 with isopar 0.9 weights are {0.1,0.9} -- sum is 1
         for sample 10 with isopar 1 weights are {-0,1} -- sum is 1
         for sample 11 with isopar 1.1 weights are {-0.1,1.1} -- sum is 1
         for sample 12 with isopar 1.2 weights are {-0.2,1.2} -- sum is 1
         for sample 13 with isopar 1.3 weights are {-0.3,1.3} -- sum is 1
         for sample 14 with isopar 1.4 weights are {-0.4,1.4} -- sum is 1
         for sample 15 with isopar 1.5 weights are {0.25,-0.75} -- sum is -0.5
Sampling Lagrange1DFiniteElement of order 2
         for sample -5 with isopar -0.5 weights are {0,0,-0} -- sum is 0
         for sample -4 with isopar -0.4 weights are {0.252,0.072,-0.224} -- sum is 0.1
         for sample -3 with isopar -0.3 weights are {0.416,0.096,-0.312} -- sum is 0.2
         for sample -2 with isopar -0.2 weights are {1.68,0.28,-0.96} -- sum is 1
         for sample -1 with isopar -0.1 weights are {1.32,0.12,-0.44} -- sum is 1
         for sample 0 with isopar 0 weights are {1,-0,0} -- sum is 1
         for sample 1 with isopar 0.1 weights are {0.72,-0.08,0.36} -- sum is 1
         for sample 2 with isopar 0.2 weights are {0.48,-0.12,0.64} -- sum is 1
         for sample 3 with isopar 0.3 weights are {0.28,-0.12,0.84} -- sum is 1
         for sample 4 with isopar 0.4 weights are {0.12,-0.08,0.96} -- sum is 1
         for sample 5 with isopar 0.5 weights are {-0,0,1} -- sum is 1
         for sample 6 with isopar 0.6 weights are {-0.08,0.12,0.96} -- sum is 1
         for sample 7 with isopar 0.7 weights are {-0.12,0.28,0.84} -- sum is 1
         for sample 8 with isopar 0.8 weights are {-0.12,0.48,0.64} -- sum is 1
         for sample 9 with isopar 0.9 weights are {-0.08,0.72,0.36} -- sum is 1
         for sample 10 with isopar 1 weights are {0,1,-0} -- sum is 1
         for sample 11 with isopar 1.1 weights are {0.12,1.32,-0.44} -- sum is 1
         for sample 12 with isopar 1.2 weights are {0.28,1.68,-0.96} -- sum is 1
         for sample 13 with isopar 1.3 weights are {-0.096,-0.416,0.312} -- sum is -0.2
free(): invalid size
Aborted (core dumped)

### 64成功
privious commit
将64.cpp放入examples
make clean

cd examples
g++  -O3 -std=c++11 -I..  64.cpp -o 64 -L.. -lmfem -lrt
覆盖率的话修改为：g++ -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. 64.cpp -o 64 -L.. -lmfem -lrt -lgcov
./64
valgrind --leak-check=full mpirun -np 1 64

## v2101:

### 2494失败
cd mfem
make clean
make all -j
cd examples
mpirun -np 5 ex13p -o 2 > /root/mfem-code-analyzer/get_normal_testcase_covarage/log.txt

### 2413失败
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 2413.cpp -o 2413 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt

### 129成功.
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 129.cpp -o 129 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
cd examples
valgrind ./129

### 2062失败
mesh-explorer.cpp中修改mesh路径
cd mfem
make clean
make all -j
cd examples
/root/mfem/miniapps/meshing/mesh-explorer -np 16 -m /root/mfem/data/beam-hex
报错：
root@8403300dc1d0:~/mfem# /root/mfem/miniapps/meshing/mesh-explorer -np 16 -m beam-hex
Options used:
   --mesh beam-hex
   --num-proc 16
   --refinement
Can not open mesh file: beam-hex.000000!

### 2035成功
privious commit
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 2035.cpp -o 2035 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
添加覆盖率：mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 2035.cpp -o 2035 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
valgrind --leak-check=full mpirun -np 5 2035
结果：
==423008== LEAK SUMMARY:
==423008==    definitely lost: 6,905 bytes in 26 blocks
==423008==    indirectly lost: 101,467 bytes in 1,585 blocks
==423008==      possibly lost: 0 bytes in 0 blocks
==423008==    still reachable: 116,312 bytes in 147 blocks

### 1874成功
privious commit
在ex3p.cpp,在//4最后面添加：mesh->EnsureNCMesh(true);
cd mfem
make clean
make all -j
cd examples
mpirun -n 2 ./ex3p -m /root/mfem/data/inline-tet.mesh -o 2
结果：
MFEM abort: triangle face orientation 1 is not supported! Use Mesh::ReorientTetMesh to fix it.
 ... in function: virtual const int* mfem::ND_FECollection::DofOrderForOrientation(mfem::Geometry::Type, int) const
 ... in file: fem/fe_coll.cpp:2697

 ### 1578失败
 需要确保使用了cuda
privious commit
1578.cpp放入examples
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 1578.cpp -o 1578 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt

### 463成功
v2101
privious commit
463.cpp放入examples
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 463.cpp -o 463 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
添加覆盖率：mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 463.cpp -o 463 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov

mpirun -n 2 ./463
结果：
After creation : Boundary attribute size: 4
After creation : Boundary attribute size: 4
After refinement : Boundary attribute size: 4
After refinement : Boundary attribute size: 4
After derefinement : Boundary attribute size: 3
After derefinement : Boundary attribute size: 3


## 413成功
v2101，修复版本也有这个段错误
privious commit
413.cpp放入examples
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 413.cpp -o 413 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
包含覆盖率的命令：mpicxx -O3 -std=c++11 --coverage -I.. -I../../hypre/src/hypre/include 413.cpp -o 413 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
valgrind --leak-check=full mpirun -n 2 ./413
结果：
mpirun noticed that process rank 0 with PID 0 on node 8403300dc1d0 exited on signal 11 (Segmentation fault).
### 旧版mfem 复现

hyper 2.20

```

wget https://github.com/hypre-space/hypre/archive/refs/tags/v2.20.0.tar.gz
tar -xzvf v2.20.0.tar.gz


```

## 报错 unittestcase 无法编译的情况

根据报错情况，定位到报错位置，应该是
catch.hpp中的：
     constexpr std::size_t sigStackSize = 32768 >= MINSIGSTKSZ ? 32768 : MINSIGSTKSZ;
将其改为：
    constexpr std::size_t sigStackSize = 32768;
即可
make test