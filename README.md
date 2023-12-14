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

# 21p02

### 3840
fix：8a9ca138551bb0b3668da6a40cd636985f21039e
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd tests/unit
./unit_tests "direct-serial"
结果：No tests ran

### 3436成功
553dc3109f5ddb03505fc7abc54edd08f36d9b3e的privious commit,修改exp0中的mesh
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
valgrind --leak-check=full ./ex0p

### 2838成功
复现sha：5fe211e3aecf2560c2d1872af425e2ea37c1fa8a
替换issue中的两个用例，修改catch.hpp
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd tests/unit
./unit_tests "PA Convection"
结果：
root@f64125032199:~/mfem/tests/unit# ./unit_tests "PA Convection"
INFO: Test filter: PA Convection ~[Parallel] ~[MFEMData]
Filters: PA Convection ~[Parallel] ~[MFEMData]

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
unit_tests is a Catch v2.13.2 host application.
Run with -? for options

-------------------------------------------------------------------------------
PA Convection
-------------------------------------------------------------------------------
/root/mfem/tests/unit/fem/test_pa_kernels.cpp:442
...............................................................................

/root/mfem/tests/unit/fem/test_pa_kernels.cpp:457: FAILED:
  {Unknown expression after the reported line}
due to a fatal error condition:
  mesh=../../data/periodic-square.mesh, order=2, prob=0, refinement=0
  SIGSEGV - Segmentation violation signal

===============================================================================
test cases: 1 | 1 failed
assertions: 2 | 1 passed | 1 failed

Segmentation fault (core dumped)

### 2809成功，没有覆盖率
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
make pmesh-bug
valgrind --leak-check=full mpirun -np 4 ./pmesh-bug

### 2703
复现sha：783f0e0304b6a16f9b0f777698007d0b2fe09f1a
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
make 2703
./2703
结果：
root@763087cd9a0c:~/mfem/examples# ./2703
ScaledOperator Mult result: 0 2 4 6 8

### 2699
复现sha：3d7b3b18fb980bb2c6f6bd00161b32fc05e83a1e
773ea0cc5d7f6004547f930b9a4793af583cf447的privious commit,替换issue中的两个用例
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
mpirun -np 2 ex1p
结果：
root@f64125032199:~/mfem/examples# mpirun -np 2 ex1p
Options used:
   --mesh ../data/star.mesh
   --order 1
   --no-static-condensation
   --no-partial-assembly
   --no-full-assembly
   --device cpu
   --visualization
Device configuration: cpu
Memory configuration: host-std
Number of finite element unknowns: 82561


 Num MPI tasks = 2

 Num OpenMP threads = 1


BoomerAMG SETUP PARAMETERS:

 Max levels = 25
 Num levels = 7

 Strength Threshold = 0.250000
 Interpolation Truncation Factor = 0.000000
 Maximum Row Sum Threshold for Dependency Weakening = 0.900000

 Coarsening Type = HMIS

 No. of levels of aggressive coarsening: 1

 Interpolation on agg. levels= multipass interpolation
 measures are determined locally


 No global partition option chosen.

 Interpolation = extended+i interpolation

Operator Matrix Information:

             nonzero            entries/row          row sums
lev    rows  entries sparse   min  max     avg      min         max
======================================================================
  0   82561   739201  0.000     4   11     9.0  -1.277e-15   1.915e+00
  1    4962    43648  0.002     3   11     8.8  -5.995e-15   5.834e+00
  2    1632    33284  0.012     7   28    20.4  -8.710e-15   7.383e+00
  3     531    14231  0.050    11   40    26.8  -1.227e-14   7.832e+00
  4     125     3241  0.207    11   45    25.9  -2.151e-14   5.852e+00
  5      24      402  0.698     9   24    16.8   1.173e+00   6.208e+00
  6       4       16  1.000     4    4     4.0   4.085e+00   5.839e+00


Interpolation Matrix Information:
                    entries/row        min        max            row sums
lev  rows x cols  min  max  avgW     weight      weight       min         max
================================================================================
  0 82561 x 4962    0    4   1.6   1.180e-02   1.000e+00   0.000e+00   1.000e+00
  1  4962 x 1632    1    4   4.0   1.554e-02   6.587e-01   3.036e-01   1.000e+00
  2  1632 x 531     1    4   3.9   9.934e-03   6.314e-01   2.070e-01   1.000e+00
  3   531 x 125     0    4   3.8   4.331e-03   7.090e-01   0.000e+00   1.000e+00
  4   125 x 24      0    4   3.7   2.908e-03   6.335e-01   0.000e+00   1.000e+00
  5    24 x 4       0    4   2.4   3.184e-03   3.894e-01   0.000e+00   1.000e+00


     Complexity:    grid = 1.088153
                operator = 1.128276
                memory = 1.328364




BoomerAMG SOLVER PARAMETERS:

  Maximum number of cycles:         1
  Stopping Tolerance:               0.000000e+00
  Cycle type (1 = V, 2 = W, etc.):  1

  Relaxation Parameters:
   Visiting Grid:                     down   up  coarse
            Number of sweeps:            1    1     1
   Type 0=Jac, 3=hGS, 6=hSGS, 9=GE:      8    8     9
   Point types, partial sweeps (1=C, -1=F):
                  Pre-CG relaxation (down):   0
                   Post-CG relaxation (up):   0
                             Coarsest grid:   0

   Iteration :   0  (B r, r) = 0.290049
   Iteration :   1  (B r, r) = 0.0200637
   Iteration :   2  (B r, r) = 0.000570177
   Iteration :   3  (B r, r) = 5.74965e-05
   Iteration :   4  (B r, r) = 2.46573e-06
   Iteration :   5  (B r, r) = 3.5549e-07
   Iteration :   6  (B r, r) = 3.79278e-08
   Iteration :   7  (B r, r) = 4.37046e-09
   Iteration :   8  (B r, r) = 6.30729e-10
   Iteration :   9  (B r, r) = 6.43674e-11
   Iteration :  10  (B r, r) = 6.02537e-12
   Iteration :  11  (B r, r) = 6.16521e-13
   Iteration :  12  (B r, r) = 4.45556e-14
   Iteration :  13  (B r, r) = 4.20101e-15
   Iteration :  14  (B r, r) = 3.88272e-16
   Iteration :  15  (B r, r) = 4.0686e-17
   Iteration :  16  (B r, r) = 4.1729e-18
   Iteration :  17  (B r, r) = 3.3523e-19
   Iteration :  18  (B r, r) = 2.83435e-20
   Iteration :  19  (B r, r) = 2.46983e-21
   Iteration :  20  (B r, r) = 2.01668e-22
   Iteration :  21  (B r, r) = 1.4673e-23
   Iteration :  22  (B r, r) = 1.20986e-24
   Iteration :  23  (B r, r) = 9.48848e-26
Average reduction factor = 0.29357

### 2363
cf90fad7fbfd56da3916b0adbb80d5174b7b5a06的privious commit,替换issue中的用例
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
mpicxx  -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 2363.cpp -o 2363 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
mpirun -np 2 2363

### 2157
复现sha:afde4abc8d3e3caebbc2127274a0de8097e257db
替换issue中的用例
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
make 2157
./2157
root@763087cd9a0c:~/mfem/examples# ./2157
Original dt1 sizes: 2, 3, 4
Original dt2 sizes: 4, 3, 2
Swapped dt1 sizes: 2, 3, 2
Swapped dt2 sizes: 4, 3, 4

### 2152
复现bug：72f7f26e08d740f861fa8ade08430c0a55dd5654
5335439a711bf589857651a4ef6bdf927567d83d的privious commit,将test_build放入tests/unit/fem
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd tests/unit
./unit_tests "Build Dof To Arrays"

root@763087cd9a0c:~/mfem/tests/unit# ./unit_tests "Build Dof To Arrays"
Filters: Build Dof To Arrays ~[Parallel]

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
unit_tests is a Catch v2.13.2 host application.
Run with -? for options

-------------------------------------------------------------------------------
Build Dof To Arrays
  Mesh Type: 1, Basis Type: 1
-------------------------------------------------------------------------------
/root/mfem/tests/unit/fem/test_build.cpp:94
...............................................................................

/root/mfem/tests/unit/fem/test_build.cpp:94: FAILED:
  {Unknown expression after the reported line}
due to a fatal error condition:
  SIGSEGV - Segmentation violation signal

===============================================================================
test cases:   1 |   0 passed | 1 failed
assertions: 577 | 576 passed | 1 failed

Segmentation fault (core dumped)

### 2119
复现sha:7b48468b24d0ec08a3fb1a1504af438c9897122f
替换ex1p中的mesh为2119.msh
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
./ex1p
结果：
root@f64125032199:~/mfem/examples# ./ex1p
Options used:
   --mesh /root/mfem-code-analyzer/bugs/issue2119/2119.msh
   --order 1
   --no-static-condensation
   --no-partial-assembly
   --device cpu
   --visualization
Device configuration: cpu
Memory configuration: host-std
Number of finite element unknowns: 144129


 Num MPI tasks = 1

 Num OpenMP threads = 1


BoomerAMG SETUP PARAMETERS:

 Max levels = 25
 Num levels = 8

 Strength Threshold = 0.250000
 Interpolation Truncation Factor = 0.000000
 Maximum Row Sum Threshold for Dependency Weakening = 0.900000

 Coarsening Type = HMIS

 No. of levels of aggressive coarsening: 1

 Interpolation on agg. levels= multipass interpolation
 measures are determined locally


 No global partition option chosen.

 Interpolation = extended+i interpolation

Operator Matrix Information:

             nonzero            entries/row          row sums
lev    rows  entries sparse   min  max     avg      min         max
======================================================================
  0  144129  1292545  0.000     4    9     9.0  -1.554e-15   1.762e+00
  1   11877   106009  0.001     5    9     8.9  -6.384e-15   3.116e+00
  2    5939   121455  0.003     8   21    20.5  -7.577e-15   3.854e+00
  3    1465    37283  0.017    11   27    25.4  -1.070e-14   4.606e+00
  4     365    10461  0.079    12   33    28.7  -2.066e-14   4.015e+00
  5      74     1932  0.353    13   37    26.1   2.072e-14   3.621e+00
  6      14      182  0.929    11   14    13.0   6.344e-01   3.557e+00
  7       1        1  1.000     1    1     1.0   4.443e+00   4.443e+00


Interpolation Matrix Information:
                      entries/row        min        max            row sums
lev   rows x cols   min  max  avgW     weight      weight       min         max
==================================================================================
  0 144129 x 11877    0    4   1.8   3.189e-02   1.000e+00   0.000e+00   1.000e+00
  1  11877 x 5939     1    4   4.0   1.338e-01   3.205e-01   5.880e-01   1.000e+00
  2   5939 x 1465     1    4   3.9   1.684e-02   4.242e-01   3.943e-01   1.000e+00
  3   1465 x 365      0    4   3.9   9.662e-03   4.110e-01   0.000e+00   1.000e+00
  4    365 x 74       1    4   3.6   4.093e-03   4.657e-01   9.128e-02   1.000e+00
  5     74 x 14       1    4   3.8   4.673e-03   4.972e-01   1.211e-01   1.000e+00
  6     14 x 1        1    1   1.0   9.033e-02   5.104e-01   9.033e-02   1.000e+00


     Complexity:    grid = 1.136926
                operator = 1.214556
                memory = 1.449518




BoomerAMG SOLVER PARAMETERS:

  Maximum number of cycles:         1
  Stopping Tolerance:               0.000000e+00
  Cycle type (1 = V, 2 = W, etc.):  1

  Relaxation Parameters:
   Visiting Grid:                     down   up  coarse
            Number of sweeps:            1    1     1
   Type 0=Jac, 3=hGS, 6=hSGS, 9=GE:      8    8     9
   Point types, partial sweeps (1=C, -1=F):
                  Pre-CG relaxation (down):   0
                   Post-CG relaxation (up):   0
                             Coarsest grid:   0

   Iteration :   0  (B r, r) = 0.0160505
   Iteration :   1  (B r, r) = 0.00053547
   Iteration :   2  (B r, r) = 1.09862e-05
   Iteration :   3  (B r, r) = 5.44557e-07
   Iteration :   4  (B r, r) = 1.74515e-08
   Iteration :   5  (B r, r) = 1.01077e-09
   Iteration :   6  (B r, r) = 3.27356e-11
   Iteration :   7  (B r, r) = 1.99797e-12
   Iteration :   8  (B r, r) = 8.27676e-14
   Iteration :   9  (B r, r) = 3.22111e-15
   Iteration :  10  (B r, r) = 2.08934e-16
   Iteration :  11  (B r, r) = 7.83638e-18
   Iteration :  12  (B r, r) = 3.45915e-19
   Iteration :  13  (B r, r) = 1.82573e-20
   Iteration :  14  (B r, r) = 9.79938e-22
   Iteration :  15  (B r, r) = 4.71128e-23
   Iteration :  16  (B r, r) = 1.99357e-24
   Iteration :  17  (B r, r) = 1.03881e-25
   Iteration :  18  (B r, r) = 4.28459e-27
Average reduction factor = 0.207683

### 2001
崩溃性bug，强行收集了覆盖率，但是没有覆盖到有效文件。
复现sha：cd788e83ff2b525edbd10855ac5168d21ecf2a69
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
make 2001
./2001
结果：
root@763087cd9a0c:~/mfem/examples# ./2001
MFEM abort: VTK mesh is not in ASCII format!
 ... in function: void mfem::Mesh::ReadVTKMesh(std::istream&, int&, int&, bool&)
 ... in file: mesh/mesh_readers.cpp:769
Aborted (core dumped)

### 1896
复现sha：759987ef3186d9c2ebeb82e6e340ebebfde6b0c2
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
./ex9
结果：
root@f64125032199:~/mfem/examples# ./ex9
Options used:
   --mesh ../data/periodic-hexagon.mesh
   --problem 0
   --refine 2
   --order 3
   --no-partial-assembly
   --no-element-assembly
   --no-full-assembly
   --device cpu
   --ode-solver 4
   --t-final 10
   --time-step 0.01
   --visualization
   --no-visit-datafiles
   --no-paraview-datafiles
   --ascii-datafiles
   --visualization-steps 5
Device configuration: cpu
Memory configuration: host-std
Number of unknowns: 3072
Unable to connect to GLVis server at localhost:19916
GLVis visualization disabled.
time step: 5, time: 0.05
time step: 10, time: 0.1
time step: 15, time: 0.15
time step: 20, time: 0.2
time step: 25, time: 0.25
time step: 30, time: 0.3
time step: 35, time: 0.35
time step: 40, time: 0.4
time step: 45, time: 0.45
time step: 50, time: 0.5
time step: 55, time: 0.55
time step: 60, time: 0.6
time step: 65, time: 0.65
time step: 70, time: 0.7
time step: 75, time: 0.75
time step: 80, time: 0.8
time step: 85, time: 0.85
time step: 90, time: 0.9
time step: 95, time: 0.95
time step: 100, time: 1
time step: 105, time: 1.05
time step: 110, time: 1.1
time step: 115, time: 1.15
time step: 120, time: 1.2
time step: 125, time: 1.25
time step: 130, time: 1.3
time step: 135, time: 1.35
time step: 140, time: 1.4
time step: 145, time: 1.45
time step: 150, time: 1.5
time step: 155, time: 1.55
time step: 160, time: 1.6
time step: 165, time: 1.65
time step: 170, time: 1.7
time step: 175, time: 1.75
time step: 180, time: 1.8
time step: 185, time: 1.85
time step: 190, time: 1.9
time step: 195, time: 1.95
time step: 200, time: 2
time step: 205, time: 2.05
time step: 210, time: 2.1
time step: 215, time: 2.15
time step: 220, time: 2.2
time step: 225, time: 2.25
time step: 230, time: 2.3
time step: 235, time: 2.35
time step: 240, time: 2.4
time step: 245, time: 2.45
time step: 250, time: 2.5
time step: 255, time: 2.55
time step: 260, time: 2.6
time step: 265, time: 2.65
time step: 270, time: 2.7
time step: 275, time: 2.75
time step: 280, time: 2.8
time step: 285, time: 2.85
time step: 290, time: 2.9
time step: 295, time: 2.95
time step: 300, time: 3
time step: 305, time: 3.05
time step: 310, time: 3.1
time step: 315, time: 3.15
time step: 320, time: 3.2
time step: 325, time: 3.25
time step: 330, time: 3.3
time step: 335, time: 3.35
time step: 340, time: 3.4
time step: 345, time: 3.45
time step: 350, time: 3.5
time step: 355, time: 3.55
time step: 360, time: 3.6
time step: 365, time: 3.65
time step: 370, time: 3.7
time step: 375, time: 3.75
time step: 380, time: 3.8
time step: 385, time: 3.85
time step: 390, time: 3.9
time step: 395, time: 3.95
time step: 400, time: 4
time step: 405, time: 4.05
time step: 410, time: 4.1
time step: 415, time: 4.15
time step: 420, time: 4.2
time step: 425, time: 4.25
time step: 430, time: 4.3
time step: 435, time: 4.35
time step: 440, time: 4.4
time step: 445, time: 4.45
time step: 450, time: 4.5
time step: 455, time: 4.55
time step: 460, time: 4.6
time step: 465, time: 4.65
time step: 470, time: 4.7
time step: 475, time: 4.75
time step: 480, time: 4.8
time step: 485, time: 4.85
time step: 490, time: 4.9
time step: 495, time: 4.95
time step: 500, time: 5
time step: 505, time: 5.05
time step: 510, time: 5.1
time step: 515, time: 5.15
time step: 520, time: 5.2
time step: 525, time: 5.25
time step: 530, time: 5.3
time step: 535, time: 5.35
time step: 540, time: 5.4
time step: 545, time: 5.45
time step: 550, time: 5.5
time step: 555, time: 5.55
time step: 560, time: 5.6
time step: 565, time: 5.65
time step: 570, time: 5.7
time step: 575, time: 5.75
time step: 580, time: 5.8
time step: 585, time: 5.85
time step: 590, time: 5.9
time step: 595, time: 5.95
time step: 600, time: 6
time step: 605, time: 6.05
time step: 610, time: 6.1
time step: 615, time: 6.15
time step: 620, time: 6.2
time step: 625, time: 6.25
time step: 630, time: 6.3
time step: 635, time: 6.35
time step: 640, time: 6.4
time step: 645, time: 6.45
time step: 650, time: 6.5
time step: 655, time: 6.55
time step: 660, time: 6.6
time step: 665, time: 6.65
time step: 670, time: 6.7
time step: 675, time: 6.75
time step: 680, time: 6.8
time step: 685, time: 6.85
time step: 690, time: 6.9
time step: 695, time: 6.95
time step: 700, time: 7
time step: 705, time: 7.05
time step: 710, time: 7.1
time step: 715, time: 7.15
time step: 720, time: 7.2
time step: 725, time: 7.25
time step: 730, time: 7.3
time step: 735, time: 7.35
time step: 740, time: 7.4
time step: 745, time: 7.45
time step: 750, time: 7.5
time step: 755, time: 7.55
time step: 760, time: 7.6
time step: 765, time: 7.65
time step: 770, time: 7.7
time step: 775, time: 7.75
time step: 780, time: 7.8
time step: 785, time: 7.85
time step: 790, time: 7.9
time step: 795, time: 7.95
time step: 800, time: 8
time step: 805, time: 8.05
time step: 810, time: 8.1
time step: 815, time: 8.15
time step: 820, time: 8.2
time step: 825, time: 8.25
time step: 830, time: 8.3
time step: 835, time: 8.35
time step: 840, time: 8.4
time step: 845, time: 8.45
time step: 850, time: 8.5
time step: 855, time: 8.55
time step: 860, time: 8.6
time step: 865, time: 8.65
time step: 870, time: 8.7
time step: 875, time: 8.75
time step: 880, time: 8.8
time step: 885, time: 8.85
time step: 890, time: 8.9
time step: 895, time: 8.95
time step: 900, time: 9
time step: 905, time: 9.05
time step: 910, time: 9.1
time step: 915, time: 9.15
time step: 920, time: 9.2
time step: 925, time: 9.25
time step: 930, time: 9.3
time step: 935, time: 9.35
time step: 940, time: 9.4
time step: 945, time: 9.45
time step: 950, time: 9.5
time step: 955, time: 9.55
time step: 960, time: 9.6
time step: 965, time: 9.65
time step: 970, time: 9.7
time step: 975, time: 9.75
time step: 980, time: 9.8
time step: 985, time: 9.85
time step: 990, time: 9.9
time step: 995, time: 9.95
time step: 1000, time: 10

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
复现sha：93393c5c58ecaa3eb6fb9bbd6a822e7c3fd96be5
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
复现sha：e6ba86462c0db85732c1ac33ce7615d79b555bfd
privious commit,替换test_submesh.cpp，修改/root/mfem/mesh/submesh/submesh_utils.cpp，最上面加入：
#ifdef __GNUC__
extern "C" void __gcov_flush(void);
#endif
if (T(j, k) != 0.0)这一行前写入：
__gcov_flush(); // 强制写入覆盖率数据

/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd tests/unit
./unit_tests SubMesh
结果：
root@f64125032199:~/mfem/tests/unit# ./unit_tests SubMesh
INFO: Test filter: SubMesh ~[Parallel] ~[MFEMData]
Filters: SubMesh ~[Parallel] ~[MFEMData]

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
unit_tests is a Catch v2.13.9 host application.
Run with -? for options

-------------------------------------------------------------------------------
SubMesh
  2D
-------------------------------------------------------------------------------
/root/mfem/tests/unit/mesh/test_submesh.cpp:405
...............................................................................

/root/mfem/tests/unit/mesh/test_submesh.cpp:407: FAILED:
  {Unknown expression after the reported line}
due to a fatal error condition:
  SIGSEGV - Segmentation violation signal

===============================================================================
test cases:   1 |   0 passed | 1 failed
assertions: 132 | 131 passed | 1 failed

Segmentation fault (core dumped)

### issue3328成功
复现sha：ca6588da7df13b299609098685b8e384abeea4ac
privious commit
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
把3328.cpp放入examples
cd examples
make 3328
./3328
结果：
root@f64125032199:~/mfem/examples# ./3328


MFEM Warning: Unable to open mesh file: test_000000/mesh.000000
 ... in function: void mfem::VisItDataCollection::LoadMesh()
 ... in file: fem/datacollection.cpp:574

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

### issue 2878成功
复现sha：50cd7da165999d4c65a6875a24c39317acaa2c3e
privious commit,替换issue中的ex3p.cpp
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
mpirun -np 5 ex3p -m /root/mfem/data/beam-tet.mesh -o 1
结果：
root@f64125032199:~/mfem/examples# mpirun -np 5 ex3p -m /root/mfem/data/beam-tet.mesh -o 1
Options used:
   --mesh /root/mfem/data/beam-tet.mesh
   --order 1
   --frequency 1
   --no-static-condensation
   --no-partial-assembly
   --device cpu
   --visualization
Device configuration: cpu
Memory configuration: host-std
Number of finite element unknowns: 32016


Verification failed: (Fo.Size() >= 1) is false:
 --> Face orientations are unset in ND_TriDofTransformation
 ... in function: virtual void mfem::ND_TriDofTransformation::TransformDual(double*) const
 ... in file: fem/doftrans.cpp:316

--------------------------------------------------------------------------
MPI_ABORT was invoked on rank 1 in communicator MPI_COMM_WORLD
with errorcode 1.

NOTE: invoking MPI_ABORT causes Open MPI to kill all MPI processes.
You may or may not see output from other processes, depending on
exactly when Open MPI kills them.
--------------------------------------------------------------------------


Verification failed: (Fo.Size() >= 1) is false:
 --> Face orientations are unset in ND_TriDofTransformation
 ... in function: virtual void mfem::ND_TriDofTransformation::TransformDual(double*) const
 ... in file: fem/doftrans.cpp:316



Verification failed: (Fo.Size() >= 1) is false:
 --> Face orientations are unset in ND_TriDofTransformation
 ... in function: virtual void mfem::ND_TriDofTransformation::TransformDual(double*) const
 ... in file: fem/doftrans.cpp:316



Verification failed: (Fo.Size() >= 1) is false:
 --> Face orientations are unset in ND_TriDofTransformation
 ... in function: virtual void mfem::ND_TriDofTransformation::TransformDual(double*) const
 ... in file: fem/doftrans.cpp:316



Verification failed: (Fo.Size() >= 1) is false:
 --> Face orientations are unset in ND_TriDofTransformation
 ... in function: virtual void mfem::ND_TriDofTransformation::TransformDual(double*) const
 ... in file: fem/doftrans.cpp:316

[f64125032199:731338] 4 more processes have sent help message help-mpi-api.txt / mpi-abort
[f64125032199:731338] Set MCA parameter "orte_base_help_aggregate" to 0 to see all help / error messages

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
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include ex1p.cpp -o ex1p -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
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
复现sha：bba2c08025c0700ead5965d27d7ed0f8564a0018
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 2779.cpp -o 2779 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
./2779
结果：
DOF missing: 13
[row 0]
 (0,1)
[row 1]
 (1,1)
[row 2]
 (2,1)
[row 3]
 (3,1)
[row 4]
 (4,1)
[row 5]
 (5,1)
[row 6]
 (6,1)
[row 7]
 (7,1)
[row 8]
 (9,1)
[row 9]
 (10,1)
[row 10]
 (11,1)
[row 11]
 (12,1)
[row 12]
 (13,1)
[row 13]
 (16,1)
[row 14]
 (17,1)
[row 15]
 (18,1)
[row 16]
 (19,1)
[row 17]
 (20,1)
[row 18]
 (21,1)
[row 19]
 (22,1)
[row 20]
 (24,1)
[row 21]
 (25,1)
[row 22]
 (26,1)
[row 23]
 (27,1)
[row 24]
 (28,1)
[row 25]
 (29,1)
[row 26]
 (30,1)
[row 27]
 (32,1)
[row 28]
 (33,1)
[row 29]
 (34,1)
[row 30]
 (35,1)
[row 31]
 (36,1)
[row 32]
 (37,1)
[row 33]
 (38,1)
[row 34]
 (39,1)
max_order is 3

### 2559成功.
reset current branch to previous commit,hard reset
去掉头文件#include "stokes.hpp"，因为编译不过去，然后把tst.cpp放入examples，把manifold.msh放入data
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include tst.cpp -o tst -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov

mpirun -np 4 tst -m /root/mfem-code-analyzer/bugs/issue2559/manifold.msh
结果：
root@f64125032199:~/mfem/examples# mpirun -np 4 ./tst -m /root/mfem-code-analyzer/bugs/issue2559/manifold.msh
Options used:
   --mesh /root/mfem-code-analyzer/bugs/issue2559/manifold.msh
   --refine-serial 1
   --refine-parallel 1
   --order 1
   --no-visualization
   --no-static-condensation
   --relative-tolerance 1e-07
   --absolute-tolerance 1e-15
   --linear-iterations 100

### 1230成功.
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 1230.cpp -o 1230 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
mpirun -np 4 1230
结果：
root@f64125032199:~/mfem/examples# mpirun -np 4 1230
0 0 0 0.125 0.125 0.125 0 0
0 0 0 0 -0.00954915 0.0654508 -0.00954915 0.0654508
-0.00954915 0.0654508 -0.00954915 -0.00954915 -0.00954915 0.0654508 0.0654508 0.0654508


### 2599成功.
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include tst.cpp -o tst -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
mpirun -np 4 tst

### 1238成功.
rm -rf hypre
ln -s hypre-2.20.0 hypre
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 1238.cpp -o 1238 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
valgrind --leak-check=full mpirun -np 2 1238

### 2343成功.
复现sha:34ad9fca157368768af1869e9821876cf259f940
先使用三条命令清理，然后注释
将2343中的用例放入bug版本中
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd tests/unit
./unit_tests "First order ODE methods"
结果：
root@f64125032199:~/mfem/tests/unit# ./unit_tests "First order ODE methods"
INFO: Test filter: First order ODE methods ~[Parallel] ~[MFEMData]
Filters: First order ODE methods ~[Parallel] ~[MFEMData]

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
unit_tests is a Catch v2.13.9 host application.
Run with -? for options

-------------------------------------------------------------------------------
First order ODE methods
  AB2Solver()
-------------------------------------------------------------------------------
/root/mfem/tests/unit/linalg/test_ode.cpp:303
...............................................................................

/root/mfem/tests/unit/linalg/test_ode.cpp:306: FAILED:
  REQUIRE( conv_rate + tol > 2.0 )
with expansion:
  1.004674203339746 > 2

-------------------------------------------------------------------------------
First order ODE methods
  AB3Solver()
-------------------------------------------------------------------------------
/root/mfem/tests/unit/linalg/test_ode.cpp:315
...............................................................................

/root/mfem/tests/unit/linalg/test_ode.cpp:318: FAILED:
  REQUIRE( conv_rate + tol > 3.0 )
with expansion:
  1.097019196313348 > 3

-------------------------------------------------------------------------------
First order ODE methods
  AB4Solver()
-------------------------------------------------------------------------------
/root/mfem/tests/unit/linalg/test_ode.cpp:321
...............................................................................

/root/mfem/tests/unit/linalg/test_ode.cpp:324: FAILED:
  REQUIRE( conv_rate + tol > 4.0 )
with expansion:
  1.096418543144751 > 4

-------------------------------------------------------------------------------
First order ODE methods
  AB5Solver()
-------------------------------------------------------------------------------
/root/mfem/tests/unit/linalg/test_ode.cpp:327
...............................................................................

/root/mfem/tests/unit/linalg/test_ode.cpp:330: FAILED:
  REQUIRE( conv_rate + tol > 5.0 )
with expansion:
  1.093047012642808 > 5

-------------------------------------------------------------------------------
First order ODE methods
  AM2Solver()
-------------------------------------------------------------------------------
/root/mfem/tests/unit/linalg/test_ode.cpp:358
...............................................................................

/root/mfem/tests/unit/linalg/test_ode.cpp:361: FAILED:
  REQUIRE( conv_rate + tol > 3.0 )
with expansion:
  1.099700679809844 > 3

-------------------------------------------------------------------------------
First order ODE methods
  AM3Solver()
-------------------------------------------------------------------------------
/root/mfem/tests/unit/linalg/test_ode.cpp:370
...............................................................................

/root/mfem/tests/unit/linalg/test_ode.cpp:373: FAILED:
  REQUIRE( conv_rate + tol > 4.0 )
with expansion:
  1.098198954704418 > 4

-------------------------------------------------------------------------------
First order ODE methods
  AM4Solver()
-------------------------------------------------------------------------------
/root/mfem/tests/unit/linalg/test_ode.cpp:376
...............................................................................

/root/mfem/tests/unit/linalg/test_ode.cpp:379: FAILED:
  REQUIRE( conv_rate + tol > 5.0 )
with expansion:
  1.096064884932531 > 5

===============================================================================
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
复现sha：1e82e22374d45afadc383c601f07520ec6cf51b4
将ex5中的mesh文件替换 /root/mfem-code-analyzer/bugs/issue2563/origin_mesh_tri.vtu
/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
./ex5
结果：
root@f64125032199:~/mfem/examples# ./ex5
Options used:
   --mesh /root/mfem-code-analyzer/bugs/issue2563/origin_mesh_tri.vtu
   --order 1
   --no-partial-assembly
   --device cpu
   --visualization
Device configuration: cpu
Memory configuration: host-std
***********************************************************
dim(R) = 255764
dim(W) = 153420
dim(R+W) = 409184
***********************************************************


MFEM abort: Zero diagonal in SparseMatrix::DiagScale
 ... in function: mfem::SparseMatrix::DiagScale(const mfem::Vector&, mfem::Vector&, double) const::<lambda(int)>
 ... in file: linalg/sparsemat.cpp:2443

Aborted (core dumped)


## 3712没有覆盖率
bug sha: b5491f763085b3cc917fed34a58ee816c1bc0cc9
把3712用例替换到bug版本
/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd tests/unit
./unit_tests "PA VectorDivergence"

## 1284成功.
复现sha:e6385f2992b9c2d9001265fe3283403bec30b417
/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
./ex5
结果：
root@f64125032199:~/mfem/examples# ./ex5
Options used:
   --mesh ../data/star.mesh
   --order 1
   --visualization
***********************************************************
dim(R) = 41280
dim(W) = 20480
dim(R+W) = 61760
***********************************************************
MINRES: iteration   0: ||r||_B = 59.8979
MINRES: iteration   1: ||r||_B = 40.9717
MINRES: iteration   2: ||r||_B = 30.1814
MINRES: iteration   3: ||r||_B = 13.8522
MINRES: iteration   4: ||r||_B = 13.8151
MINRES: iteration   5: ||r||_B = 7.88953
MINRES: iteration   6: ||r||_B = 7.53609
MINRES: iteration   7: ||r||_B = 5.40797
MINRES: iteration   8: ||r||_B = 4.6406
MINRES: iteration   9: ||r||_B = 4.09057
MINRES: iteration  10: ||r||_B = 3.19132
MINRES: iteration  11: ||r||_B = 3.0648
MINRES: iteration  12: ||r||_B = 2.39035
MINRES: iteration  13: ||r||_B = 2.38802
MINRES: iteration  14: ||r||_B = 1.92306
MINRES: iteration  15: ||r||_B = 1.89681
MINRES: iteration  16: ||r||_B = 1.66224
MINRES: iteration  17: ||r||_B = 1.55286
MINRES: iteration  18: ||r||_B = 1.48249
MINRES: iteration  19: ||r||_B = 1.31627
MINRES: iteration  20: ||r||_B = 1.31595
MINRES: iteration  21: ||r||_B = 1.17134
MINRES: iteration  22: ||r||_B = 1.1387
MINRES: iteration  23: ||r||_B = 1.07397
MINRES: iteration  24: ||r||_B = 0.985047
MINRES: iteration  25: ||r||_B = 0.977014
MINRES: iteration  26: ||r||_B = 0.880066
MINRES: iteration  27: ||r||_B = 0.875493
MINRES: iteration  28: ||r||_B = 0.81795
MINRES: iteration  29: ||r||_B = 0.775623
MINRES: iteration  30: ||r||_B = 0.75974
MINRES: iteration  31: ||r||_B = 0.694966
MINRES: iteration  32: ||r||_B = 0.694857
MINRES: iteration  33: ||r||_B = 0.643597
MINRES: iteration  34: ||r||_B = 0.62859
MINRES: iteration  35: ||r||_B = 0.608109
MINRES: iteration  36: ||r||_B = 0.570954
MINRES: iteration  37: ||r||_B = 0.570493
MINRES: iteration  38: ||r||_B = 0.529711
MINRES: iteration  39: ||r||_B = 0.524415
MINRES: iteration  40: ||r||_B = 0.500097
MINRES: iteration  41: ||r||_B = 0.477642
MINRES: iteration  42: ||r||_B = 0.473503
MINRES: iteration  43: ||r||_B = 0.442571
MINRES: iteration  44: ||r||_B = 0.4418
MINRES: iteration  45: ||r||_B = 0.419935
MINRES: iteration  46: ||r||_B = 0.406831
MINRES: iteration  47: ||r||_B = 0.400063
MINRES: iteration  48: ||r||_B = 0.377004
MINRES: iteration  49: ||r||_B = 0.376951
MINRES: iteration  50: ||r||_B = 0.354287
MINRES: iteration  51: ||r||_B = 0.349415
MINRES: iteration  52: ||r||_B = 0.339848
MINRES: iteration  53: ||r||_B = 0.325553
MINRES: iteration  54: ||r||_B = 0.324767
MINRES: iteration  55: ||r||_B = 0.306038
MINRES: iteration  56: ||r||_B = 0.304843
MINRES: iteration  57: ||r||_B = 0.292553
MINRES: iteration  58: ||r||_B = 0.284371
MINRES: iteration  59: ||r||_B = 0.281356
MINRES: iteration  60: ||r||_B = 0.266836
MINRES: iteration  61: ||r||_B = 0.266708
MINRES: iteration  62: ||r||_B = 0.254675
MINRES: iteration  63: ||r||_B = 0.250113
MINRES: iteration  64: ||r||_B = 0.245164
MINRES: iteration  65: ||r||_B = 0.235161
MINRES: iteration  66: ||r||_B = 0.234979
MINRES: iteration  67: ||r||_B = 0.223786
MINRES: iteration  68: ||r||_B = 0.221977
MINRES: iteration  69: ||r||_B = 0.215913
MINRES: iteration  70: ||r||_B = 0.208914
MINRES: iteration  71: ||r||_B = 0.208003
MINRES: iteration  72: ||r||_B = 0.198391
MINRES: iteration  73: ||r||_B = 0.198015
MINRES: iteration  74: ||r||_B = 0.191333
MINRES: iteration  75: ||r||_B = 0.187409
MINRES: iteration  76: ||r||_B = 0.185308
MINRES: iteration  77: ||r||_B = 0.17763
MINRES: iteration  78: ||r||_B = 0.177629
MINRES: iteration  79: ||r||_B = 0.170259
MINRES: iteration  80: ||r||_B = 0.168343
MINRES: iteration  81: ||r||_B = 0.165171
MINRES: iteration  82: ||r||_B = 0.159902
MINRES: iteration  83: ||r||_B = 0.15967
MINRES: iteration  84: ||r||_B = 0.152619
MINRES: iteration  85: ||r||_B = 0.15201
MINRES: iteration  86: ||r||_B = 0.14808
MINRES: iteration  87: ||r||_B = 0.144523
MINRES: iteration  88: ||r||_B = 0.143673
MINRES: iteration  89: ||r||_B = 0.137579
MINRES: iteration  90: ||r||_B = 0.137528
MINRES: iteration  91: ||r||_B = 0.133022
MINRES: iteration  92: ||r||_B = 0.131115
MINRES: iteration  93: ||r||_B = 0.129545
MINRES: iteration  94: ||r||_B = 0.124923
MINRES: iteration  95: ||r||_B = 0.124893
MINRES: iteration  96: ||r||_B = 0.120145
MINRES: iteration  97: ||r||_B = 0.119328
MINRES: iteration  98: ||r||_B = 0.116881
MINRES: iteration  99: ||r||_B = 0.113745
MINRES: iteration 100: ||r||_B = 0.113432
MINRES: iteration 101: ||r||_B = 0.109113
MINRES: iteration 102: ||r||_B = 0.108889
MINRES: iteration 103: ||r||_B = 0.105897
MINRES: iteration 104: ||r||_B = 0.10399
MINRES: iteration 105: ||r||_B = 0.103147
MINRES: iteration 106: ||r||_B = 0.099593
MINRES: iteration 107: ||r||_B = 0.0995907
MINRES: iteration 108: ||r||_B = 0.0964178
MINRES: iteration 109: ||r||_B = 0.0954154
MINRES: iteration 110: ||r||_B = 0.0940408
MINRES: iteration 111: ||r||_B = 0.0912894
MINRES: iteration 112: ||r||_B = 0.0911758
MINRES: iteration 113: ||r||_B = 0.0880703
MINRES: iteration 114: ||r||_B = 0.0877152
MINRES: iteration 115: ||r||_B = 0.0858303
MINRES: iteration 116: ||r||_B = 0.0839611
MINRES: iteration 117: ||r||_B = 0.083546
MINRES: iteration 118: ||r||_B = 0.080746
MINRES: iteration 119: ||r||_B = 0.0806911
MINRES: iteration 120: ||r||_B = 0.0784814
MINRES: iteration 121: ||r||_B = 0.0774873
MINRES: iteration 122: ||r||_B = 0.0766517
MINRES: iteration 123: ||r||_B = 0.0744249
MINRES: iteration 124: ||r||_B = 0.0744187
MINRES: iteration 125: ||r||_B = 0.0720646
MINRES: iteration 126: ||r||_B = 0.0716047
MINRES: iteration 127: ||r||_B = 0.070354
MINRES: iteration 128: ||r||_B = 0.0687258
MINRES: iteration 129: ||r||_B = 0.0685848
MINRES: iteration 130: ||r||_B = 0.0664029
MINRES: iteration 131: ||r||_B = 0.0662527
MINRES: iteration 132: ||r||_B = 0.0647351
MINRES: iteration 133: ||r||_B = 0.0636618
MINRES: iteration 134: ||r||_B = 0.0632611
MINRES: iteration 135: ||r||_B = 0.0613482
MINRES: iteration 136: ||r||_B = 0.061341
MINRES: iteration 137: ||r||_B = 0.0596653
MINRES: iteration 138: ||r||_B = 0.0590846
MINRES: iteration 139: ||r||_B = 0.0584133
MINRES: iteration 140: ||r||_B = 0.0569592
MINRES: iteration 141: ||r||_B = 0.056917
MINRES: iteration 142: ||r||_B = 0.0552828
MINRES: iteration 143: ||r||_B = 0.0550822
MINRES: iteration 144: ||r||_B = 0.0541233
MINRES: iteration 145: ||r||_B = 0.0531325
MINRES: iteration 146: ||r||_B = 0.0529029
MINRES: iteration 147: ||r||_B = 0.0512156
MINRES: iteration 148: ||r||_B = 0.0511882
MINRES: iteration 149: ||r||_B = 0.0496701
MINRES: iteration 150: ||r||_B = 0.0489747
MINRES: iteration 151: ||r||_B = 0.0484401
MINRES: iteration 152: ||r||_B = 0.0467535
MINRES: iteration 153: ||r||_B = 0.0467527
MINRES: iteration 154: ||r||_B = 0.0450585
MINRES: iteration 155: ||r||_B = 0.0446975
MINRES: iteration 156: ||r||_B = 0.0439346
MINRES: iteration 157: ||r||_B = 0.042772
MINRES: iteration 158: ||r||_B = 0.0426866
MINRES: iteration 159: ||r||_B = 0.0411403
MINRES: iteration 160: ||r||_B = 0.041029
MINRES: iteration 161: ||r||_B = 0.0400253
MINRES: iteration 162: ||r||_B = 0.039243
MINRES: iteration 163: ||r||_B = 0.0390052
MINRES: iteration 164: ||r||_B = 0.0376991
MINRES: iteration 165: ||r||_B = 0.0376837
MINRES: iteration 166: ||r||_B = 0.0365825
MINRES: iteration 167: ||r||_B = 0.0361722
MINRES: iteration 168: ||r||_B = 0.0357171
MINRES: iteration 169: ||r||_B = 0.0346764
MINRES: iteration 170: ||r||_B = 0.0346637
MINRES: iteration 171: ||r||_B = 0.0335006
MINRES: iteration 172: ||r||_B = 0.033327
MINRES: iteration 173: ||r||_B = 0.0326776
MINRES: iteration 174: ||r||_B = 0.0319423
MINRES: iteration 175: ||r||_B = 0.031833
MINRES: iteration 176: ||r||_B = 0.0307331
MINRES: iteration 177: ||r||_B = 0.0306911
MINRES: iteration 178: ||r||_B = 0.0298862
MINRES: iteration 179: ||r||_B = 0.0294196
MINRES: iteration 180: ||r||_B = 0.0291696
MINRES: iteration 181: ||r||_B = 0.0282038
MINRES: iteration 182: ||r||_B = 0.0282038
MINRES: iteration 183: ||r||_B = 0.0272543
MINRES: iteration 184: ||r||_B = 0.0270122
MINRES: iteration 185: ||r||_B = 0.0265852
MINRES: iteration 186: ||r||_B = 0.0258312
MINRES: iteration 187: ||r||_B = 0.0257883
MINRES: iteration 188: ||r||_B = 0.0248166
MINRES: iteration 189: ||r||_B = 0.02474
MINRES: iteration 190: ||r||_B = 0.0241255
MINRES: iteration 191: ||r||_B = 0.0235944
MINRES: iteration 192: ||r||_B = 0.0234473
MINRES: iteration 193: ||r||_B = 0.0225561
MINRES: iteration 194: ||r||_B = 0.0225485
MINRES: iteration 195: ||r||_B = 0.0217873
MINRES: iteration 196: ||r||_B = 0.0214798
MINRES: iteration 197: ||r||_B = 0.0211612
MINRES: iteration 198: ||r||_B = 0.0204119
MINRES: iteration 199: ||r||_B = 0.0204038
MINRES: iteration 200: ||r||_B = 0.0195641
MINRES: iteration 201: ||r||_B = 0.019425
MINRES: iteration 202: ||r||_B = 0.0189532
MINRES: iteration 203: ||r||_B = 0.0183741
MINRES: iteration 204: ||r||_B = 0.0182987
MINRES: iteration 205: ||r||_B = 0.0174544
MINRES: iteration 206: ||r||_B = 0.0174194
MINRES: iteration 207: ||r||_B = 0.0167979
MINRES: iteration 208: ||r||_B = 0.0163982
MINRES: iteration 209: ||r||_B = 0.0162116
MINRES: iteration 210: ||r||_B = 0.0154586
MINRES: iteration 211: ||r||_B = 0.0154584
MINRES: iteration 212: ||r||_B = 0.0147639
MINRES: iteration 213: ||r||_B = 0.0145514
MINRES: iteration 214: ||r||_B = 0.0142342
MINRES: iteration 215: ||r||_B = 0.0136624
MINRES: iteration 216: ||r||_B = 0.0136436
MINRES: iteration 217: ||r||_B = 0.012968
MINRES: iteration 218: ||r||_B = 0.012889
MINRES: iteration 219: ||r||_B = 0.0124809
MINRES: iteration 220: ||r||_B = 0.0121128
MINRES: iteration 221: ||r||_B = 0.0120351
MINRES: iteration 222: ||r||_B = 0.0114481
MINRES: iteration 223: ||r||_B = 0.0114342
MINRES: iteration 224: ||r||_B = 0.0109779
MINRES: iteration 225: ||r||_B = 0.0107687
MINRES: iteration 226: ||r||_B = 0.0106194
MINRES: iteration 227: ||r||_B = 0.0101709
MINRES: iteration 228: ||r||_B = 0.01017
MINRES: iteration 229: ||r||_B = 0.00972284
MINRES: iteration 230: ||r||_B = 0.0096265
MINRES: iteration 231: ||r||_B = 0.00941625
MINRES: iteration 232: ||r||_B = 0.00910687
MINRES: iteration 233: ||r||_B = 0.00908403
MINRES: iteration 234: ||r||_B = 0.00869394
MINRES: iteration 235: ||r||_B = 0.00866691
MINRES: iteration 236: ||r||_B = 0.00842026
MINRES: iteration 237: ||r||_B = 0.0082452
MINRES: iteration 238: ||r||_B = 0.00818107
MINRES: iteration 239: ||r||_B = 0.00787237
MINRES: iteration 240: ||r||_B = 0.00787132
MINRES: iteration 241: ||r||_B = 0.00759955
MINRES: iteration 242: ||r||_B = 0.007515
MINRES: iteration 243: ||r||_B = 0.00740043
MINRES: iteration 244: ||r||_B = 0.00717082
MINRES: iteration 245: ||r||_B = 0.00716427
MINRES: iteration 246: ||r||_B = 0.00689051
MINRES: iteration 247: ||r||_B = 0.00685448
MINRES: iteration 248: ||r||_B = 0.00670085
MINRES: iteration 249: ||r||_B = 0.00653424
MINRES: iteration 250: ||r||_B = 0.00651054
MINRES: iteration 251: ||r||_B = 0.00626466
MINRES: iteration 252: ||r||_B = 0.00625368
MINRES: iteration 253: ||r||_B = 0.00607283
MINRES: iteration 254: ||r||_B = 0.00596063
MINRES: iteration 255: ||r||_B = 0.00590642
MINRES: iteration 256: ||r||_B = 0.00568642
MINRES: iteration 257: ||r||_B = 0.00568639
MINRES: iteration 258: ||r||_B = 0.00547438
MINRES: iteration 259: ||r||_B = 0.00541807
MINRES: iteration 260: ||r||_B = 0.00531799
MINRES: iteration 261: ||r||_B = 0.00515753
MINRES: iteration 262: ||r||_B = 0.0051476
MINRES: iteration 263: ||r||_B = 0.00494373
MINRES: iteration 264: ||r||_B = 0.00492575
MINRES: iteration 265: ||r||_B = 0.00479064
MINRES: iteration 266: ||r||_B = 0.00468714
MINRES: iteration 267: ||r||_B = 0.00465307
MINRES: iteration 268: ||r||_B = 0.00447055
MINRES: iteration 269: ||r||_B = 0.00446861
MINRES: iteration 270: ||r||_B = 0.00430958
MINRES: iteration 271: ||r||_B = 0.00424897
MINRES: iteration 272: ||r||_B = 0.00418789
MINRES: iteration 273: ||r||_B = 0.00404156
MINRES: iteration 274: ||r||_B = 0.00403938
MINRES: iteration 275: ||r||_B = 0.0038774
MINRES: iteration 276: ||r||_B = 0.00385191
MINRES: iteration 277: ||r||_B = 0.0037639
MINRES: iteration 278: ||r||_B = 0.00366012
MINRES: iteration 279: ||r||_B = 0.00364578
MINRES: iteration 280: ||r||_B = 0.00349649
MINRES: iteration 281: ||r||_B = 0.00349073
MINRES: iteration 282: ||r||_B = 0.00337623
MINRES: iteration 283: ||r||_B = 0.00331263
MINRES: iteration 284: ||r||_B = 0.0032757
MINRES: iteration 285: ||r||_B = 0.00314587
MINRES: iteration 286: ||r||_B = 0.00314587
MINRES: iteration 287: ||r||_B = 0.00301973
MINRES: iteration 288: ||r||_B = 0.00298868
MINRES: iteration 289: ||r||_B = 0.00293305
MINRES: iteration 290: ||r||_B = 0.00284233
MINRES: iteration 291: ||r||_B = 0.0028386
MINRES: iteration 292: ||r||_B = 0.0027258
MINRES: iteration 293: ||r||_B = 0.00271592
MINRES: iteration 294: ||r||_B = 0.00264467
MINRES: iteration 295: ||r||_B = 0.00259107
MINRES: iteration 296: ||r||_B = 0.00257291
MINRES: iteration 297: ||r||_B = 0.00247219
MINRES: iteration 298: ||r||_B = 0.00247172
MINRES: iteration 299: ||r||_B = 0.00236342
MINRES: iteration 300: ||r||_B = 0.00232493
MINRES: iteration 301: ||r||_B = 0.00227178
MINRES: iteration 302: ||r||_B = 0.00215141
MINRES: iteration 303: ||r||_B = 0.00215027
MINRES: iteration 304: ||r||_B = 0.00201369
MINRES: iteration 305: ||r||_B = 0.00198847
MINRES: iteration 306: ||r||_B = 0.0019233
MINRES: iteration 307: ||r||_B = 0.00183812
MINRES: iteration 308: ||r||_B = 0.00182985
MINRES: iteration 309: ||r||_B = 0.0017137
MINRES: iteration 310: ||r||_B = 0.00170736
MINRES: iteration 311: ||r||_B = 0.00162671
MINRES: iteration 312: ||r||_B = 0.00156955
MINRES: iteration 313: ||r||_B = 0.00154916
MINRES: iteration 314: ||r||_B = 0.00144925
MINRES: iteration 315: ||r||_B = 0.00144879
MINRES: iteration 316: ||r||_B = 0.0013692
MINRES: iteration 317: ||r||_B = 0.00134307
MINRES: iteration 318: ||r||_B = 0.00131228
MINRES: iteration 319: ||r||_B = 0.0012478
MINRES: iteration 320: ||r||_B = 0.00124615
MINRES: iteration 321: ||r||_B = 0.00116942
MINRES: iteration 322: ||r||_B = 0.00115896
MINRES: iteration 323: ||r||_B = 0.00111515
MINRES: iteration 324: ||r||_B = 0.00106929
MINRES: iteration 325: ||r||_B = 0.001062
MINRES: iteration 326: ||r||_B = 0.000997654
MINRES: iteration 327: ||r||_B = 0.000995363
MINRES: iteration 328: ||r||_B = 0.00094789
MINRES: iteration 329: ||r||_B = 0.000921647
MINRES: iteration 330: ||r||_B = 0.000904854
MINRES: iteration 331: ||r||_B = 0.000851801
MINRES: iteration 332: ||r||_B = 0.000851772
MINRES: iteration 333: ||r||_B = 0.000800418
MINRES: iteration 334: ||r||_B = 0.000787833
MINRES: iteration 335: ||r||_B = 0.000763201
MINRES: iteration 336: ||r||_B = 0.0007244
MINRES: iteration 337: ||r||_B = 0.000721833
MINRES: iteration 338: ||r||_B = 0.000672681
MINRES: iteration 339: ||r||_B = 0.000668854
MINRES: iteration 340: ||r||_B = 0.000638182
MINRES: iteration 341: ||r||_B = 0.000612803
MINRES: iteration 342: ||r||_B = 0.000605413
MINRES: iteration 343: ||r||_B = 0.000562921
MINRES: iteration 344: ||r||_B = 0.000562729
MINRES: iteration 345: ||r||_B = 0.000527646
MINRES: iteration 346: ||r||_B = 0.000514158
MINRES: iteration 347: ||r||_B = 0.000501483
MINRES: iteration 348: ||r||_B = 0.000469057
MINRES: iteration 349: ||r||_B = 0.000468651
MINRES: iteration 350: ||r||_B = 0.000434279
MINRES: iteration 351: ||r||_B = 0.00042913
MINRES: iteration 352: ||r||_B = 0.000410511
MINRES: iteration 353: ||r||_B = 0.00038759
MINRES: iteration 354: ||r||_B = 0.000385255
MINRES: iteration 355: ||r||_B = 0.000354406
MINRES: iteration 356: ||r||_B = 0.000352872
MINRES: iteration 357: ||r||_B = 0.00033135
MINRES: iteration 358: ||r||_B = 0.000318649
MINRES: iteration 359: ||r||_B = 0.000312314
MINRES: iteration 360: ||r||_B = 0.000288107
MINRES: iteration 361: ||r||_B = 0.000288072
MINRES: iteration 362: ||r||_B = 0.000266275
MINRES: iteration 363: ||r||_B = 0.000259996
MINRES: iteration 364: ||r||_B = 0.00025069
MINRES: iteration 365: ||r||_B = 0.000234312
MINRES: iteration 366: ||r||_B = 0.000233695
MINRES: iteration 367: ||r||_B = 0.000214433
MINRES: iteration 368: ||r||_B = 0.000212201
MINRES: iteration 369: ||r||_B = 0.000201324
MINRES: iteration 370: ||r||_B = 0.000191218
MINRES: iteration 371: ||r||_B = 0.000188965
MINRES: iteration 372: ||r||_B = 0.000173198
MINRES: iteration 373: ||r||_B = 0.000172852
MINRES: iteration 374: ||r||_B = 0.000160399
MINRES: iteration 375: ||r||_B = 0.000154295
MINRES: iteration 376: ||r||_B = 0.000150391
MINRES: iteration 377: ||r||_B = 0.000137948
MINRES: iteration 378: ||r||_B = 0.00013794
MINRES: iteration 379: ||r||_B = 0.00012624
MINRES: iteration 380: ||r||_B = 0.000123481
MINRES: iteration 381: ||r||_B = 0.000118178
MINRES: iteration 382: ||r||_B = 0.000110022
MINRES: iteration 383: ||r||_B = 0.000109593
MINRES: iteration 384: ||r||_B = 9.97319e-05
MINRES: iteration 385: ||r||_B = 9.88833e-05
MINRES: iteration 386: ||r||_B = 9.26419e-05
MINRES: iteration 387: ||r||_B = 8.77625e-05
MINRES: iteration 388: ||r||_B = 8.64599e-05
MINRES: iteration 389: ||r||_B = 7.85485e-05
MINRES: iteration 390: ||r||_B = 7.84542e-05
MINRES: iteration 391: ||r||_B = 7.19644e-05
MINRES: iteration 392: ||r||_B = 6.93926e-05
MINRES: iteration 393: ||r||_B = 6.71892e-05
MINRES: iteration 394: ||r||_B = 6.12766e-05
MINRES: iteration 395: ||r||_B = 6.12544e-05
MINRES: iteration 396: ||r||_B = 5.55236e-05
MINRES converged in 396 iterations with a residual norm of 5.55236e-05.
MINRES solver took 0.489646s.
|| u_h - u_ex || / || u_ex || = 0.000143587
|| p_h - p_ex || / || p_ex || = 3.49368e-05
Directory content of PVExample5S:
  PVExample5S.pvd
  Cycle000001

### 2413
（未复现）编译失败
url: https://github.com/mfem/mfem/issues/2413
作者提供的网格和用例都放入issues2413中了
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 2413.cpp -o 2413 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt

### 2144成功.
复现sha：913361dd0db723d07e9c7492102f8b887acabc48
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
复现sha:0c98591d4ac4ca48b1cecadef553f2cf8043c6c2
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
结果：
root@f64125032199:~/mfem/examples# ./ex1
Options used:
   --mesh /root/mfem/data/beam-wedge.vtk
   --order 1
   --no-static-condensation
   --no-partial-assembly
   --device cpu
   --visualization
Device configuration: cpu
Memory configuration: host-std
Number of finite element unknowns: 19737
Size of linear system: 19737
   Iteration :   0  (B r, r) = -0.010132
PCG: The preconditioner is not positive definite. (Br, r) = -0.010132

### 1413失败
privious commit
将1413_2放入examples
make clean
make all -j
cd examples
make 1413_2
for i in {1..10000}; do ./1413_2; done

### 1326失败
复现sha:438a458c3f1893e59930bc97df71d907ddffcade
将mpi.cpp放入examples
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include mpi.cpp -o mpi -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
mpirun -np 1 mpi
结果：
root@f64125032199:~/mfem/examples# mpirun -np 1 mpi
Options used:
   --mesh /root/mfem-code-analyzer/bugs/issue1326/xperiodic-square.mesh
   --refine 2
   --refineP 0
   --order 2
Generated mesh file: mesh.000000
Generated solution file: sol_psi.000000

### 1322成功
复现sha:
323ddecd86c0dc48dc904267268bd8a3b783eb0d
cd examples
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 1322.cpp -o 1322 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
./1322
无论哪个sha都是以下结果：
root@f64125032199:~/mfem/examples# ./1322
Options used:
   --device cpu
Device configuration: cpu
Finite element space created.
Total DOFs: 8
Vector coefficient: 0x56416cbe36a0
GridFunction max value: 2
GridFunction min value: 0

### 685成功.
privious commit
复现sha:83cef85c1d1fa02c6b3245d988783f9cb37c451f
将685.cpp放入examples
make clean
make all -j
cd examples
make 685
./685
结果：
root@f64125032199:~/mfem/examples# ./685
Element 0's point matrix before reordering:
[row +0]
-2.454380e-02 +5.300620e-01 +6.748660e-01 +1.628520e-01
+2.530430e-01 +5.550630e-01 +3.892290e-01 +7.410290e-02
+3.318290e-01
[row +1]
+3.026530e-02 +1.198990e-03 +4.820680e-01 +4.719240e-01
-3.692510e-03 +2.408630e-01 +4.683540e-01 +2.333160e-01
+2.335440e-01
Element 0's point matrix after reordering:
[row +0]
-2.454380e-02 +6.263740e-01 +6.748660e-01 +1.628520e-01
+2.530430e-01 +5.550630e-01 +3.892290e-01 +7.410290e-02
+3.318290e-01
[row +1]
+3.026530e-02 -4.801480e-01 +4.820680e-01 +4.719240e-01
-3.692510e-03 +2.408630e-01 +4.683540e-01 +2.333160e-01
+2.335440e-01

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
结果：
root@f64125032199:~/mfem/examples# ./ex6
Options used:
   --mesh /root/mfem/data/inline-tet.mesh
   --order 1
   --visualization
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 125
Number of edges    : 604
Number of faces    : 864
Number of elements : 384
Number of bdr elem : 192
Euler Number       : 1
h_min              : 0.280616
h_max              : 0.280616
kappa_min          : 2.41421
kappa_max          : 2.41421


AMR iteration 0
Number of unknowns: 125
   Iteration :   0  (B r, r) = 0.00974541 ...
   Iteration :   6  (B r, r) = 6.44945e-19
Average reduction factor = 0.0448463
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 161
Number of edges    : 856
Number of faces    : 1296
Number of elements : 600
Number of bdr elem : 192
Euler Number       : 1
h_min              : 0.222725
h_max              : 0.280616
kappa_min          : 2.41421
kappa_max          : 2.56155


AMR iteration 1
Number of unknowns: 161
   Iteration :   0  (B r, r) = 0.0013798 ...
   Iteration :   6  (B r, r) = 1.18412e-17
Average reduction factor = 0.0672664
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 181
Number of edges    : 960
Number of faces    : 1464
Number of elements : 684
Number of bdr elem : 192
Euler Number       : 1
h_min              : 0.176777
h_max              : 0.280616
kappa_min          : 2.35829
kappa_max          : 2.56155


AMR iteration 2
Number of unknowns: 181
   Iteration :   0  (B r, r) = 0.00122243 ...
   Iteration :   6  (B r, r) = 1.14861e-15
Average reduction factor = 0.0994822
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 235
Number of edges    : 1266
Number of faces    : 1968
Number of elements : 936
Number of bdr elem : 192
Euler Number       : 1
h_min              : 0.176777
h_max              : 0.280616
kappa_min          : 2.35829
kappa_max          : 2.56155


AMR iteration 3
Number of unknowns: 235
   Iteration :   0  (B r, r) = 0.000616687 ...
   Iteration :   7  (B r, r) = 2.54098e-17
Average reduction factor = 0.110643
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 349
Number of edges    : 1770
Number of faces    : 2670
Number of elements : 1248
Number of bdr elem : 348
Euler Number       : 1
h_min              : 0.176777
h_max              : 0.280616
kappa_min          : 2.35829
kappa_max          : 2.56155


AMR iteration 4
Number of unknowns: 349
   Iteration :   0  (B r, r) = 0.000264903 ...
   Iteration :   8  (B r, r) = 3.46054e-17
Average reduction factor = 0.156586
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 543
Number of edges    : 2966
Number of faces    : 4560
Number of elements : 2136
Number of bdr elem : 576
Euler Number       : 1
h_min              : 0.140308
h_max              : 0.222725
kappa_min          : 2.35829
kappa_max          : 2.56155


AMR iteration 5
Number of unknowns: 543
   Iteration :   0  (B r, r) = 0.000289073 ...
   Iteration :   8  (B r, r) = 1.71401e-16
Average reduction factor = 0.172113
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 813
Number of edges    : 4676
Number of faces    : 7344
Number of elements : 3480
Number of bdr elem : 768
Euler Number       : 1
h_min              : 0.111362
h_max              : 0.222725
kappa_min          : 2.35829
kappa_max          : 2.56155


AMR iteration 6
Number of unknowns: 813
   Iteration :   0  (B r, r) = 0.000302314 ...
   Iteration :   9  (B r, r) = 7.55584e-17
Average reduction factor = 0.199471
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 1051
Number of edges    : 6426
Number of faces    : 10368
Number of elements : 4992
Number of bdr elem : 768
Euler Number       : 1
h_min              : 0.0883883
h_max              : 0.176777
kappa_min          : 2.35829
kappa_max          : 3.94272


AMR iteration 7
Number of unknowns: 1051
   Iteration :   0  (B r, r) = 0.000164683 ...
   Iteration :  11  (B r, r) = 1.90902e-17
Average reduction factor = 0.25823
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 3355
Number of edges    : 20718
Number of faces    : 33660
Number of elements : 16296
Number of bdr elem : 2136
Euler Number       : 1
h_min              : 0.0556812
h_max              : 0.176777
kappa_min          : 2.35829
kappa_max          : 6.24804


AMR iteration 8
Number of unknowns: 3355
   Iteration :   0  (B r, r) = 0.000341805 ...
   Iteration :  15  (B r, r) = 5.48277e-17
Average reduction factor = 0.374548
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 3949
Number of edges    : 24432
Number of faces    : 39660
Number of elements : 19176
Number of bdr elem : 2616
Euler Number       : 1
h_min              : 0.0441942
h_max              : 0.140308
kappa_min          : 1.41421
kappa_max          : 6.98736


AMR iteration 9
Number of unknowns: 3949
   Iteration :   0  (B r, r) = 6.25931e-05 ...
   Iteration :  15  (B r, r) = 2.05793e-17
Average reduction factor = 0.383616
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 4803
Number of edges    : 30218
Number of faces    : 49416
Number of elements : 24000
Number of bdr elem : 2832
Euler Number       : 1
h_min              : 0.0441942
h_max              : 0.140308
kappa_min          : 1.41421
kappa_max          : 6.98736


AMR iteration 10
Number of unknowns: 4803
   Iteration :   0  (B r, r) = 9.57021e-05 ...
   Iteration :  16  (B r, r) = 3.57879e-17
Average reduction factor = 0.408931
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 6295
Number of edges    : 39438
Number of faces    : 64680
Number of elements : 31536
Number of bdr elem : 3216
Euler Number       : 1
h_min              : 0.0350769
h_max              : 0.111362
kappa_min          : 1.41421
kappa_max          : 9.44001


AMR iteration 11
Number of unknowns: 6295
   Iteration :   0  (B r, r) = 6.26342e-05 ...
   Iteration :  18  (B r, r) = 4.66146e-17
Average reduction factor = 0.460366
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 8437
Number of edges    : 52920
Number of faces    : 87240
Number of elements : 42756
Number of bdr elem : 3456
Euler Number       : 1
h_min              : 0.0278406
h_max              : 0.0883883
kappa_min          : 1.41421
kappa_max          : 11.4124


AMR iteration 12
Number of unknowns: 8437
   Iteration :   0  (B r, r) = 5.43043e-05 ...
   Iteration :  21  (B r, r) = 2.37913e-17
Average reduction factor = 0.507869
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 33267
Number of edges    : 219962
Number of faces    : 367968
Number of elements : 181272
Number of bdr elem : 10848
Euler Number       : 1
h_min              : 0.0139203
h_max              : 0.0883883
kappa_min          : 1.41421
kappa_max          : 29.8203


AMR iteration 13
Number of unknowns: 33267
   Iteration :   0  (B r, r) = 0.00011308 ...
   Iteration :  32  (B r, r) = 4.70583e-17
Average reduction factor = 0.640547
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 35487
Number of edges    : 235298
Number of faces    : 393936
Number of elements : 194124
Number of bdr elem : 11376
Euler Number       : 1
h_min              : 0.0139203
h_max              : 0.0701539
kappa_min          : 1.41421
kappa_max          : 29.8203


AMR iteration 14
Number of unknowns: 35487
   Iteration :   0  (B r, r) = 9.79599e-06 ...
   Iteration :  32  (B r, r) = 6.36177e-18
Average reduction factor = 0.645016
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 92415
Number of edges    : 605438
Number of faces    : 1015440
Number of elements : 502416
Number of bdr elem : 21216
Euler Number       : 1
h_min              : 0.0110485
h_max              : 0.0556812
kappa_min          : 1.41421
kappa_max          : 29.8203


AMR iteration 15
Number of unknowns: 92415
   Iteration :   0  (B r, r) = 5.34682e-05 ...
   Iteration :  43  (B r, r) = 3.97341e-17
Average reduction factor = 0.722713
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 129491
Number of edges    : 850462
Number of faces    : 1428852
Number of elements : 707880
Number of bdr elem : 26184
Euler Number       : 1
h_min              : 0.00696015
h_max              : 0.0556812
kappa_min          : 1.41421
kappa_max          : 34.5041


AMR iteration 16
Number of unknowns: 129491
   Iteration :   0  (B r, r) = 1.89008e-05 ...
   Iteration :  51  (B r, r) = 1.25112e-17
Average reduction factor = 0.75962
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 131219
Number of edges    : 860230
Number of faces    : 1444740
Number of elements : 715728
Number of bdr elem : 26568
Euler Number       : 1
h_min              : 0.00696015
h_max              : 0.0556812
kappa_min          : 1.41421
kappa_max          : 34.5041


AMR iteration 17
Number of unknowns: 131219
   Iteration :   0  (B r, r) = 2.95446e-06 ...
   Iteration :  49  (B r, r) = 2.11804e-18
Average reduction factor = 0.751755
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 204043
Number of edges    : 1353528
Number of faces    : 2281350
Number of elements : 1131864
Number of bdr elem : 35244
Euler Number       : 1
h_min              : 0.00552427
h_max              : 0.0556812
kappa_min          : 1.41421
kappa_max          : 41.3223


AMR iteration 18
Number of unknowns: 204043
   Iteration :   0  (B r, r) = 1.63474e-05 ...
   Iteration :  58  (B r, r) = 1.13689e-17
Average reduction factor = 0.785583
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 224865
Number of edges    : 1496120
Number of faces    : 2523816
Number of elements : 1252560
Number of bdr elem : 37392
Euler Number       : 1
h_min              : 0.00552427
h_max              : 0.0441942
kappa_min          : 1.41421
kappa_max          : 41.3223


AMR iteration 19
Number of unknowns: 224865
   Iteration :   0  (B r, r) = 4.8457e-06 ...
   Iteration :  54  (B r, r) = 3.51963e-18
Average reduction factor = 0.771975
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 321651
Number of edges    : 2150090
Number of faces    : 3635712
Number of elements : 1807272
Number of bdr elem : 42336
Euler Number       : 1
h_min              : 0.00438462
h_max              : 0.0350769
kappa_min          : 1.41421
kappa_max          : 41.3223


AMR iteration 20
Number of unknowns: 321651
   Iteration :   0  (B r, r) = 8.17487e-06 ...
   Iteration :  67  (B r, r) = 7.92359e-18
Average reduction factor = 0.813479
Mesh Characteristics:
Dimension          : 3
Space dimension    : 3
Number of vertices : 510227
Number of edges    : 3407068
Number of faces    : 5764650
Number of elements : 2867808
Number of bdr elem : 58068
Euler Number       : 1
h_min              : 0.00438462
h_max              : 0.0350769
kappa_min          : 1.41421
kappa_max          : 42.2025


AMR iteration 21
Number of unknowns: 510227
   Iteration :   0  (B r, r) = 9.48384e-06 ...
   Iteration :  74  (B r, r) = 9.09241e-18
Average reduction factor = 0.82946
Reached the maximum number of dofs. Stop.

### 443成功.

bug版本使用fix的用例，运行ex19
/root/mfem/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
./ex19
结果：
root@f64125032199:~/mfem/examples# ./ex19
Options used:
   --mesh /root/mfem/data/beam-tet.mesh
   --refine 0
   --order 2
   --visualization
   --relative-tolerance 0.0001
   --absolute-tolerance 1e-06
   --newton-iterations 500
   --shear-modulus 1
***********************************************************
dim(u) = 459
dim(p) = 36
dim(u+p) = 495
***********************************************************
Newton iteration  0 : ||r|| = 2.90593
Newton iteration  1 : ||r|| = 0.115213, ||r||/||r_0|| = 0.0396474
Newton iteration  2 : ||r|| = 0.0168574, ||r||/||r_0|| = 0.00580103
Newton iteration  3 : ||r|| = 6.91198e-05, ||r||/||r_0|| = 2.37858e-05

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

### 2492
复现sha:4937ee34faac8bfbf1b17cfcadc252f3ef238ec6
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd tests/unit/
./unit_tests "3D ProjectBdrCoefficientTangent"
结果：
root@f64125032199:~/mfem/tests/unit# ./unit_tests "3D ProjectBdrCoefficientTangent"
INFO: Test filter: 3D ProjectBdrCoefficientTangent ~[Parallel] ~[MFEMData]
Filters: 3D ProjectBdrCoefficientTangent ~[Parallel] ~[MFEMData]
0:0 nd (-4.40748,15.9206,-0.60178) vs. (10.7288,-12.167,-0.0675716) 97.3302
0:1 nd (-6.19745,12.2406,3.12902) vs. (3.78965,-5.99015,-2.59753) 42.5295
0:2 nd (-1.06906,2.83886,0.254765) vs. (13.0549,-7.54087,-2.30556) 90.4579
0:3 nd (-3.6509,7.73068,1.63962) vs. (13.6899,-7.84119,-5.19156) 94.6589
0:4 nd (-2.8171,9.44491,-0.0982529) vs. (29.4307,-21.8527,-2.47993) 219.94
0:5 nd (-5.206,13.8244,1.24063) vs. (8.41342,-18.3351,-1.65889) 121.04

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
unit_tests is a Catch v2.13.2 host application.
Run with -? for options

-------------------------------------------------------------------------------
3D ProjectBdrCoefficientTangent
  3D GetVectorValue tests for element type 4
-------------------------------------------------------------------------------
/root/mfem/tests/unit/fem/test_project_bdr.cpp:48
...............................................................................

/root/mfem/tests/unit/fem/test_project_bdr.cpp:118: FAILED:
  REQUIRE( nd_err == MFEM_Approx(0.0) )
with expansion:
  110.9926670492195 == Approx( 0 )

===============================================================================
test cases: 1 | 1 failed
assertions: 7 | 6 passed | 1 failed

### 2413失败
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 2413.cpp -o 2413 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt

### 129成功.
复现sha:3ecf917a0c7d6cfda06110918ef6be73884a972b
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 129.cpp -o 129 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
cd examples
valgrind ./129
结果：
root@f64125032199:~/mfem/examples# valgrind ./129
==3731662== Memcheck, a memory error detector
==3731662== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==3731662== Using Valgrind-3.18.1 and LibVEX; rerun with -h for copyright info
==3731662== Command: ./129
==3731662==
==3731662== Invalid read of size 8
==3731662==    at 0x2B6431: mfem::Mesh::Mesh(mfem::Mesh*, int, int) (in /root/mfem/examples/129)
==3731662==    by 0x270469: main (in /root/mfem/examples/129)
==3731662==  Address 0x51931c0 is 0 bytes after a block of size 256 alloc'd
==3731662==    at 0x484A2F3: operator new[](unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3731662==    by 0x3F422B: mfem::DenseMatrix::SetSize(int, int) (in /root/mfem/examples/129)
==3731662==    by 0x322913: mfem::IsoparametricTransformation::Transform(mfem::IntegrationRule const&, mfem::DenseMatrix&) (in /root/mfem/examples/129)
==3731662==    by 0x2B63AD: mfem::Mesh::Mesh(mfem::Mesh*, int, int) (in /root/mfem/examples/129)
==3731662==    by 0x270469: main (in /root/mfem/examples/129)
==3731662==
==3731662==
==3731662== HEAP SUMMARY:
==3731662==     in use at exit: 0 bytes in 0 blocks
==3731662==   total heap usage: 1,280 allocs, 1,280 frees, 235,001 bytes allocated
==3731662==
==3731662== All heap blocks were freed -- no leaks are possible
==3731662==
==3731662== For lists of detected and suppressed errors, rerun with: -s
==3731662== ERROR SUMMARY: 20 errors from 1 contexts (suppressed: 0 from 0)

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
复现sha:d9275d734e060fc653236ab4901b370cbb6dd7ad
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -I.. -I../../hypre/src/hypre/include 2035.cpp -o 2035 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
添加覆盖率：mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 2035.cpp -o 2035 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
valgrind --leak-check=full mpirun -np 5 2035
结果：
root@f64125032199:~/mfem/examples# valgrind --leak-check=full mpirun -np 5 2035
==1921429== Memcheck, a memory error detector
==1921429== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==1921429== Using Valgrind-3.18.1 and LibVEX; rerun with -h for copyright info
==1921429== Command: mpirun -np 5 2035
==1921429==
hwloc x86 backend cannot work under Valgrind, disabling.
May be reenabled by dumping CPUIDs with hwloc-gather-cpuid
and reloading them under Valgrind with HWLOC_CPUID_PATH.
hwloc x86 backend cannot work under Valgrind, disabling.
May be reenabled by dumping CPUIDs with hwloc-gather-cpuid
and reloading them under Valgrind with HWLOC_CPUID_PATH.
==1921429== Warning: noted but unhandled ioctl 0x5441 with no size/direction hints.
==1921429==    This could cause spurious value errors to appear.
==1921429==    See README_MISSING_SYSCALL_OR_IOCTL for guidance on writing a proper wrapper.
==1921640== Warning: invalid file descriptor 1048564 in syscall close()
==1921640== Warning: invalid file descriptor 1048565 in syscall close()
==1921640== Warning: invalid file descriptor 1048566 in syscall close()
==1921640== Warning: invalid file descriptor 1048567 in syscall close()
==1921640==    Use --log-fd=<number> to select an alternative log fd.
==1921640== Warning: invalid file descriptor 1048568 in syscall close()
==1921640== Warning: invalid file descriptor 1048569 in syscall close()
==1921643== Warning: invalid file descriptor 1048564 in syscall close()
==1921643== Warning: invalid file descriptor 1048565 in syscall close()
==1921643== Warning: invalid file descriptor 1048566 in syscall close()
==1921643== Warning: invalid file descriptor 1048567 in syscall close()
==1921643==    Use --log-fd=<number> to select an alternative log fd.
==1921643== Warning: invalid file descriptor 1048568 in syscall close()
==1921643== Warning: invalid file descriptor 1048569 in syscall close()
==1921646== Warning: invalid file descriptor 1048564 in syscall close()
==1921646== Warning: invalid file descriptor 1048565 in syscall close()
==1921646== Warning: invalid file descriptor 1048566 in syscall close()
==1921646== Warning: invalid file descriptor 1048567 in syscall close()
==1921646==    Use --log-fd=<number> to select an alternative log fd.
==1921646== Warning: invalid file descriptor 1048568 in syscall close()
==1921646== Warning: invalid file descriptor 1048569 in syscall close()
==1921649== Warning: invalid file descriptor 1048564 in syscall close()
==1921649== Warning: invalid file descriptor 1048565 in syscall close()
==1921649== Warning: invalid file descriptor 1048566 in syscall close()
==1921649== Warning: invalid file descriptor 1048567 in syscall close()
==1921649==    Use --log-fd=<number> to select an alternative log fd.
==1921649== Warning: invalid file descriptor 1048568 in syscall close()
==1921649== Warning: invalid file descriptor 1048569 in syscall close()
==1921652== Warning: invalid file descriptor 1048564 in syscall close()
==1921652== Warning: invalid file descriptor 1048565 in syscall close()
==1921652== Warning: invalid file descriptor 1048566 in syscall close()
==1921652== Warning: invalid file descriptor 1048567 in syscall close()
==1921652==    Use --log-fd=<number> to select an alternative log fd.
==1921652== Warning: invalid file descriptor 1048568 in syscall close()
==1921652== Warning: invalid file descriptor 1048569 in syscall close()
==1921429==
==1921429== HEAP SUMMARY:
==1921429==     in use at exit: 199,720 bytes in 1,388 blocks
==1921429==   total heap usage: 35,021 allocs, 33,633 frees, 9,061,861 bytes allocated
==1921429==
==1921429== 5 bytes in 1 blocks are definitely lost in loss record 11 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x4AB260E: strdup (strdup.c:42)
==1921429==    by 0x775A04A: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x1091E3: ??? (in /usr/bin/orterun)
==1921429==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==1921429==
==1921429== 12 bytes in 1 blocks are definitely lost in loss record 50 of 276
==1921429==    at 0x484DCD3: realloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x772A93F: ???
==1921429==    by 0x772ADB7: ???
==1921429==    by 0x7734507: ???
==1921429==    by 0x77597AE: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x1091E3: ??? (in /usr/bin/orterun)
==1921429==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==1921429==
==1921429== 20 bytes in 1 blocks are definitely lost in loss record 93 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x4AB260E: strdup (strdup.c:42)
==1921429==    by 0x77C5EB7: ???
==1921429==    by 0x7759935: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x1091E3: ??? (in /usr/bin/orterun)
==1921429==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==1921429==
==1921429== 23 (16 direct, 7 indirect) bytes in 1 blocks are definitely lost in loss record 98 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x77295A1: ???
==1921429==    by 0x77295E8: ???
==1921429==    by 0x7729777: ???
==1921429==    by 0x7814FD2: ???
==1921429==    by 0x77B5991: ???
==1921429==    by 0x77B5EA1: ???
==1921429==    by 0x77B5EE3: ???
==1921429==    by 0x775925B: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==
==1921429== 32 bytes in 1 blocks are definitely lost in loss record 119 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x499230A: opal_hwloc_base_get_npus (in /usr/lib/x86_64-linux-gnu/libopen-pal.so.40.30.2)
==1921429==    by 0xA39F1CA: ???
==1921429==    by 0xA39FC01: ???
==1921429==    by 0x48EBEF9: orte_rmaps_base_map_job (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x10928B: ??? (in /usr/bin/orterun)
==1921429==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==1921429==
==1921429== 37 (24 direct, 13 indirect) bytes in 1 blocks are definitely lost in loss record 123 of 276
==1921429==    at 0x484DCD3: realloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x7729557: ???
==1921429==    by 0x77295E8: ???
==1921429==    by 0x7729777: ???
==1921429==    by 0x78216C2: ???
==1921429==    by 0x77B5991: ???
==1921429==    by 0x77B5EA1: ???
==1921429==    by 0x77B5EE3: ???
==1921429==    by 0x77597CF: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==
==1921429== 38 (24 direct, 14 indirect) bytes in 1 blocks are definitely lost in loss record 124 of 276
==1921429==    at 0x484DCD3: realloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x7729557: ???
==1921429==    by 0x77295E8: ???
==1921429==    by 0x7729777: ???
==1921429==    by 0x7814F02: ???
==1921429==    by 0x77B5991: ???
==1921429==    by 0x77B5EA1: ???
==1921429==    by 0x77B5EE3: ???
==1921429==    by 0x775925B: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==
==1921429== 64 bytes in 1 blocks are definitely lost in loss record 163 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x7821217: ???
==1921429==    by 0x7758FC4: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x1091E3: ??? (in /usr/bin/orterun)
==1921429==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==1921429==
==1921429== 96 (48 direct, 48 indirect) bytes in 1 blocks are definitely lost in loss record 178 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x77AD8F5: ???
==1921429==    by 0x77B0A9A: ???
==1921429==    by 0x77B591D: ???
==1921429==    by 0x77B5EA1: ???
==1921429==    by 0x77B5EE3: ???
==1921429==    by 0x7757C53: ???
==1921429==    by 0x7758FC4: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==
==1921429== 96 (48 direct, 48 indirect) bytes in 1 blocks are definitely lost in loss record 179 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x77B083D: ???
==1921429==    by 0x77B591D: ???
==1921429==    by 0x77B5EA1: ???
==1921429==    by 0x77B5EE3: ???
==1921429==    by 0x775925B: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x1091E3: ??? (in /usr/bin/orterun)
==1921429==
==1921429== 99 (88 direct, 11 indirect) bytes in 1 blocks are definitely lost in loss record 180 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x775A31C: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x1091E3: ??? (in /usr/bin/orterun)
==1921429==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==1921429==
==1921429== 128 (64 direct, 64 indirect) bytes in 1 blocks are definitely lost in loss record 190 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x78138E7: ???
==1921429==    by 0x775926C: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x1091E3: ??? (in /usr/bin/orterun)
==1921429==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==1921429==
==1921429== 136 bytes in 1 blocks are definitely lost in loss record 196 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x48E5D99: orte_rmaps_base_print_mapping (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48B1EA6: orte_pmix_server_register_nspace (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48CD8CC: orte_odls_base_default_construct_child_list (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0xA3C0C15: ???
==1921429==    by 0x48A1AAF: orte_daemon_recv (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48EDE3C: orte_rml_base_process_msg (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x10928B: ??? (in /usr/bin/orterun)
==1921429==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==1921429==
==1921429== 260 bytes in 1 blocks are definitely lost in loss record 211 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x778C226: ???
==1921429==    by 0x7758A8D: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x1091E3: ??? (in /usr/bin/orterun)
==1921429==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==1921429==
==1921429== 280 (64 direct, 216 indirect) bytes in 1 blocks are definitely lost in loss record 212 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0xA7D8841: ???
==1921429==    by 0x48D8B3B: orte_plm_base_post_launch (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x10928B: ??? (in /usr/bin/orterun)
==1921429==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==1921429==
==1921429== 563 (64 direct, 499 indirect) bytes in 1 blocks are definitely lost in loss record 225 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0xA3C857F: ???
==1921429==    by 0x48EE091: orte_rtc_base_assign (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48CDC62: orte_odls_base_default_construct_child_list (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0xA3C0C15: ???
==1921429==    by 0x48A1AAF: orte_daemon_recv (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48EDE3C: orte_rml_base_process_msg (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x10928B: ??? (in /usr/bin/orterun)
==1921429==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==1921429==
==1921429== 2,048 bytes in 1 blocks are definitely lost in loss record 262 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x495125E: opal_dss_buffer_extend (in /usr/lib/x86_64-linux-gnu/libopen-pal.so.40.30.2)
==1921429==    by 0x4951564: opal_dss_pack_int32 (in /usr/lib/x86_64-linux-gnu/libopen-pal.so.40.30.2)
==1921429==    by 0x4951F59: opal_dss_pack (in /usr/lib/x86_64-linux-gnu/libopen-pal.so.40.30.2)
==1921429==    by 0x48B2A99: orte_pmix_server_register_nspace (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48CD8CC: orte_odls_base_default_construct_child_list (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0xA3C0C15: ???
==1921429==    by 0x48A1AAF: orte_daemon_recv (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48EDE3C: orte_rml_base_process_msg (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x10928B: ??? (in /usr/bin/orterun)
==1921429==
==1921429== 2,048 bytes in 1 blocks are definitely lost in loss record 263 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x495125E: opal_dss_buffer_extend (in /usr/lib/x86_64-linux-gnu/libopen-pal.so.40.30.2)
==1921429==    by 0x4951564: opal_dss_pack_int32 (in /usr/lib/x86_64-linux-gnu/libopen-pal.so.40.30.2)
==1921429==    by 0x4951F59: opal_dss_pack (in /usr/lib/x86_64-linux-gnu/libopen-pal.so.40.30.2)
==1921429==    by 0x48B2B81: orte_pmix_server_register_nspace (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48CD8CC: orte_odls_base_default_construct_child_list (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0xA3C0C15: ???
==1921429==    by 0x48A1AAF: orte_daemon_recv (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48EDE3C: orte_rml_base_process_msg (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x10928B: ??? (in /usr/bin/orterun)
==1921429==
==1921429== 3,202 (72 direct, 3,130 indirect) bytes in 1 blocks are definitely lost in loss record 266 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x77B6517: ???
==1921429==    by 0x781543A: ???
==1921429==    by 0x77B5E8E: ???
==1921429==    by 0x77B5EE3: ???
==1921429==    by 0x775925B: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x1091E3: ??? (in /usr/bin/orterun)
==1921429==
==1921429== 3,374 (840 direct, 2,534 indirect) bytes in 5 blocks are definitely lost in loss record 267 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x48E5354: orte_rmaps_base_setup_proc (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0xA39F1E5: ???
==1921429==    by 0xA39FC01: ???
==1921429==    by 0x48EBEF9: orte_rmaps_base_map_job (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==1921429==    by 0x10928B: ??? (in /usr/bin/orterun)
==1921429==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==1921429==
==1921429== 71,575 (896 direct, 70,679 indirect) bytes in 1 blocks are definitely lost in loss record 275 of 276
==1921429==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==1921429==    by 0x4C58C1E: ??? (in /usr/lib/x86_64-linux-gnu/libhwloc.so.15.5.2)
==1921429==    by 0x77344A1: ???
==1921429==    by 0x77597AE: ???
==1921429==    by 0x76D7383: ???
==1921429==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x5229188: ???
==1921429==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==1921429==    by 0x1091E3: ??? (in /usr/bin/orterun)
==1921429==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==1921429==
==1921429== LEAK SUMMARY:
==1921429==    definitely lost: 6,873 bytes in 25 blocks
==1921429==    indirectly lost: 77,263 bytes in 1,223 blocks
==1921429==      possibly lost: 0 bytes in 0 blocks
==1921429==    still reachable: 115,584 bytes in 140 blocks
==1921429==         suppressed: 0 bytes in 0 blocks
==1921429== Reachable blocks (those to which a pointer was found) are not shown.
==1921429== To see them, rerun with: --leak-check=full --show-leak-kinds=all
==1921429==
==1921429== For lists of detected and suppressed errors, rerun with: -s
==1921429== ERROR SUMMARY: 21 errors from 21 contexts (suppressed: 0 from 0)

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
复现sha:bbac26bffe986f9f4d0cee480dcdd1924ce699d9
privious commit
463.cpp放入examples
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 -fprofile-arcs -ftest-coverage -I.. -I../../hypre/src/hypre/include 463.cpp -o 463 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt -lgcov
mpirun -n 2 ./463
结果：
root@f64125032199:~/mfem/examples# mpirun -n 2 ./463
After creation : Boundary attribute size: 4
After creation : Boundary attribute size: 4
After refinement : Boundary attribute size: 4
After refinement : Boundary attribute size: 4
After derefinement : Boundary attribute size: 3
After derefinement : Boundary attribute size: 3


## 413成功
复现sha:78d65bd549cfd0aa2bcc2f9d91e0df1aa3f32538
v2101，修复版本也有这个段错误
privious commit
413.cpp放入examples
cd mfem
make clean
make all -j
cd examples
mpicxx -O3 -std=c++11 --coverage -I.. -I../../hypre/src/hypre/include 413.cpp -o 413 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
valgrind --leak-check=full mpirun -n 2 ./413
结果：
root@f64125032199:~/mfem/examples# valgrind --leak-check=full mpirun -n 2 ./413
==3720569== Memcheck, a memory error detector
==3720569== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==3720569== Using Valgrind-3.18.1 and LibVEX; rerun with -h for copyright info
==3720569== Command: mpirun -n 2 ./413
==3720569==
hwloc x86 backend cannot work under Valgrind, disabling.
May be reenabled by dumping CPUIDs with hwloc-gather-cpuid
and reloading them under Valgrind with HWLOC_CPUID_PATH.
hwloc x86 backend cannot work under Valgrind, disabling.
May be reenabled by dumping CPUIDs with hwloc-gather-cpuid
and reloading them under Valgrind with HWLOC_CPUID_PATH.
==3720569== Warning: noted but unhandled ioctl 0x5441 with no size/direction hints.
==3720569==    This could cause spurious value errors to appear.
==3720569==    See README_MISSING_SYSCALL_OR_IOCTL for guidance on writing a proper wrapper.
==3720866== Warning: invalid file descriptor 1048564 in syscall close()
==3720866== Warning: invalid file descriptor 1048565 in syscall close()
==3720866== Warning: invalid file descriptor 1048566 in syscall close()
==3720866== Warning: invalid file descriptor 1048567 in syscall close()
==3720866==    Use --log-fd=<number> to select an alternative log fd.
==3720866== Warning: invalid file descriptor 1048568 in syscall close()
==3720866== Warning: invalid file descriptor 1048569 in syscall close()
==3720869== Warning: invalid file descriptor 1048564 in syscall close()
==3720869== Warning: invalid file descriptor 1048565 in syscall close()
==3720869== Warning: invalid file descriptor 1048566 in syscall close()
==3720869== Warning: invalid file descriptor 1048567 in syscall close()
==3720869==    Use --log-fd=<number> to select an alternative log fd.
==3720869== Warning: invalid file descriptor 1048568 in syscall close()
==3720869== Warning: invalid file descriptor 1048569 in syscall close()
warning: CSR matrix nnz was not set properly (!= ia[nrow], 1789918880 2)
warning: CSR matrix nnz was not set properly (!= ia[nrow], -1982660912 2)
[f64125032199:3720869] *** Process received signal ***
[f64125032199:3720869] Signal: Segmentation fault (11)
[f64125032199:3720869] Signal code: Address not mapped (1)
[f64125032199:3720869] Failing at address: (nil)
[f64125032199:3720869] [ 0] /lib/x86_64-linux-gnu/libc.so.6(+0x42520)[0x7f8b129de520]
[f64125032199:3720869] [ 1] ./413(+0x4eca8d)[0x557f891d3a8d]
[f64125032199:3720869] [ 2] ./413(+0x1b3788)[0x557f88e9a788]
[f64125032199:3720869] [ 3] ./413(+0x19b92f)[0x557f88e8292f]
[f64125032199:3720869] [ 4] /lib/x86_64-linux-gnu/libc.so.6(+0x29d90)[0x7f8b129c5d90]
[f64125032199:3720869] [ 5] /lib/x86_64-linux-gnu/libc.so.6(__libc_start_main+0x80)[0x7f8b129c5e40]
[f64125032199:3720869] [ 6] ./413(+0x19d605)[0x557f88e84605]
[f64125032199:3720869] *** End of error message ***
[f64125032199:3720866] *** Process received signal ***
[f64125032199:3720866] Signal: Segmentation fault (11)
[f64125032199:3720866] Signal code: Address not mapped (1)
[f64125032199:3720866] Failing at address: (nil)
[f64125032199:3720866] [ 0] /lib/x86_64-linux-gnu/libc.so.6(+0x42520)[0x7f022c30d520]
[f64125032199:3720866] [ 1] ./413(+0x4eca8d)[0x56256885fa8d]
[f64125032199:3720866] [ 2] ./413(+0x1b3788)[0x562568526788]
[f64125032199:3720866] [ 3] ./413(+0x19b92f)[0x56256850e92f]
[f64125032199:3720866] [ 4] /lib/x86_64-linux-gnu/libc.so.6(+0x29d90)[0x7f022c2f4d90]
[f64125032199:3720866] [ 5] /lib/x86_64-linux-gnu/libc.so.6(__libc_start_main+0x80)[0x7f022c2f4e40]
[f64125032199:3720866] [ 6] ./413(+0x19d605)[0x562568510605]
[f64125032199:3720866] *** End of error message ***
--------------------------------------------------------------------------
Primary job  terminated normally, but 1 process returned
a non-zero exit code. Per user-direction, the job has been aborted.
--------------------------------------------------------------------------
--------------------------------------------------------------------------
mpirun noticed that process rank 0 with PID 0 on node f64125032199 exited on signal 11 (Segmentation fault).
--------------------------------------------------------------------------
==3720569==
==3720569== HEAP SUMMARY:
==3720569==     in use at exit: 201,775 bytes in 1,385 blocks
==3720569==   total heap usage: 32,850 allocs, 31,465 frees, 8,192,125 bytes allocated
==3720569==
==3720569== 5 bytes in 1 blocks are definitely lost in loss record 11 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x4AB260E: strdup (strdup.c:42)
==3720569==    by 0x775A04A: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x1091E3: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== 5 bytes in 1 blocks are definitely lost in loss record 12 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x4AB260E: strdup (strdup.c:42)
==3720569==    by 0x772ED65: ???
==3720569==    by 0x772F33C: ???
==3720569==    by 0x772F7DD: ???
==3720569==    by 0x778D03F: ???
==3720569==    by 0x7758490: ???
==3720569==    by 0x76D4FF5: ???
==3720569==    by 0x48B05DF: pmix_server_finalize (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x522A6B3: ???
==3720569==    by 0x4886384: orte_finalize (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x10934F: ??? (in /usr/bin/orterun)
==3720569==
==3720569== 12 bytes in 1 blocks are definitely lost in loss record 52 of 294
==3720569==    at 0x484DCD3: realloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x772A93F: ???
==3720569==    by 0x772ADB7: ???
==3720569==    by 0x7734507: ???
==3720569==    by 0x77597AE: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x1091E3: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== 20 bytes in 1 blocks are definitely lost in loss record 96 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x4AB260E: strdup (strdup.c:42)
==3720569==    by 0x77C5EB7: ???
==3720569==    by 0x7759935: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x1091E3: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== 23 (16 direct, 7 indirect) bytes in 1 blocks are definitely lost in loss record 103 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x77295A1: ???
==3720569==    by 0x77295E8: ???
==3720569==    by 0x7729777: ???
==3720569==    by 0x7814FD2: ???
==3720569==    by 0x77B5991: ???
==3720569==    by 0x77B5EA1: ???
==3720569==    by 0x77B5EE3: ???
==3720569==    by 0x775925B: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==
==3720569== 24 bytes in 1 blocks are definitely lost in loss record 120 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x4A921D7: __vasprintf_internal (vasprintf.c:71)
==3720569==    by 0x4B40362: __asprintf_chk (asprintf_chk.c:34)
==3720569==    by 0x772ECDD: ???
==3720569==    by 0x772F33C: ???
==3720569==    by 0x772F7DD: ???
==3720569==    by 0x778D03F: ???
==3720569==    by 0x7758490: ???
==3720569==    by 0x76D4FF5: ???
==3720569==    by 0x48B05DF: pmix_server_finalize (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x522A6B3: ???
==3720569==    by 0x4886384: orte_finalize (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==
==3720569== 24 bytes in 1 blocks are definitely lost in loss record 121 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x4A921D7: __vasprintf_internal (vasprintf.c:71)
==3720569==    by 0x4B40362: __asprintf_chk (asprintf_chk.c:34)
==3720569==    by 0x772ED50: ???
==3720569==    by 0x772F33C: ???
==3720569==    by 0x772F7DD: ???
==3720569==    by 0x778D03F: ???
==3720569==    by 0x7758490: ???
==3720569==    by 0x76D4FF5: ???
==3720569==    by 0x48B05DF: pmix_server_finalize (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x522A6B3: ???
==3720569==    by 0x4886384: orte_finalize (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==
==3720569== 24 bytes in 1 blocks are definitely lost in loss record 122 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x4AB260E: strdup (strdup.c:42)
==3720569==    by 0x772EF23: ???
==3720569==    by 0x772ED78: ???
==3720569==    by 0x772F33C: ???
==3720569==    by 0x772F7DD: ???
==3720569==    by 0x778D03F: ???
==3720569==    by 0x7758490: ???
==3720569==    by 0x76D4FF5: ???
==3720569==    by 0x48B05DF: pmix_server_finalize (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x522A6B3: ???
==3720569==    by 0x4886384: orte_finalize (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==
==3720569== 37 (24 direct, 13 indirect) bytes in 1 blocks are definitely lost in loss record 131 of 294
==3720569==    at 0x484DCD3: realloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x7729557: ???
==3720569==    by 0x77295E8: ???
==3720569==    by 0x7729777: ???
==3720569==    by 0x78216C2: ???
==3720569==    by 0x77B5991: ???
==3720569==    by 0x77B5EA1: ???
==3720569==    by 0x77B5EE3: ???
==3720569==    by 0x77597CF: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==
==3720569== 38 (24 direct, 14 indirect) bytes in 1 blocks are definitely lost in loss record 132 of 294
==3720569==    at 0x484DCD3: realloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x7729557: ???
==3720569==    by 0x77295E8: ???
==3720569==    by 0x7729777: ???
==3720569==    by 0x7814F02: ???
==3720569==    by 0x77B5991: ???
==3720569==    by 0x77B5EA1: ???
==3720569==    by 0x77B5EE3: ???
==3720569==    by 0x775925B: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==
==3720569== 64 bytes in 1 blocks are definitely lost in loss record 175 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x7821217: ???
==3720569==    by 0x7758FC4: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x1091E3: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== 96 (48 direct, 48 indirect) bytes in 1 blocks are definitely lost in loss record 189 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x77AD8F5: ???
==3720569==    by 0x77B0A9A: ???
==3720569==    by 0x77B591D: ???
==3720569==    by 0x77B5EA1: ???
==3720569==    by 0x77B5EE3: ???
==3720569==    by 0x7757C53: ???
==3720569==    by 0x7758FC4: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==
==3720569== 96 (48 direct, 48 indirect) bytes in 1 blocks are definitely lost in loss record 190 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x77B083D: ???
==3720569==    by 0x77B591D: ???
==3720569==    by 0x77B5EA1: ???
==3720569==    by 0x77B5EE3: ???
==3720569==    by 0x775925B: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x1091E3: ??? (in /usr/bin/orterun)
==3720569==
==3720569== 99 (88 direct, 11 indirect) bytes in 1 blocks are definitely lost in loss record 191 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x775A31C: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x1091E3: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== 128 (64 direct, 64 indirect) bytes in 1 blocks are definitely lost in loss record 200 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x78138E7: ???
==3720569==    by 0x775926C: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x1091E3: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== 136 bytes in 1 blocks are definitely lost in loss record 206 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x48E5D99: orte_rmaps_base_print_mapping (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48B1EA6: orte_pmix_server_register_nspace (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48CD8CC: orte_odls_base_default_construct_child_list (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0xA3C0C15: ???
==3720569==    by 0x48A1AAF: orte_daemon_recv (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48EDE3C: orte_rml_base_process_msg (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x10928B: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== 260 bytes in 1 blocks are definitely lost in loss record 227 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x778C226: ???
==3720569==    by 0x7758A8D: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x1091E3: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== 280 (64 direct, 216 indirect) bytes in 1 blocks are definitely lost in loss record 228 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0xA7D8841: ???
==3720569==    by 0x48D8B3B: orte_plm_base_post_launch (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x10928B: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== 460 (136 direct, 324 indirect) bytes in 1 blocks are definitely lost in loss record 236 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x488C882: ??? (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x4891CB8: orte_show_help_norender (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x4891F80: orte_show_help (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x76972CF: ???
==3720569==    by 0x7697984: ???
==3720569==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x1092F3: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== 504 (168 direct, 336 indirect) bytes in 1 blocks are definitely lost in loss record 238 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x48F212A: orte_state_base_activate_job_state (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x7697856: ???
==3720569==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x1092F3: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== 563 (64 direct, 499 indirect) bytes in 1 blocks are definitely lost in loss record 241 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0xA3C857F: ???
==3720569==    by 0x48EE091: orte_rtc_base_assign (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48CDC62: orte_odls_base_default_construct_child_list (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0xA3C0C15: ???
==3720569==    by 0x48A1AAF: orte_daemon_recv (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48EDE3C: orte_rml_base_process_msg (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x10928B: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== 1,845 (176 direct, 1,669 indirect) bytes in 1 blocks are definitely lost in loss record 274 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x5229674: ???
==3720569==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x1091E3: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== 2,048 bytes in 1 blocks are definitely lost in loss record 280 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x495125E: opal_dss_buffer_extend (in /usr/lib/x86_64-linux-gnu/libopen-pal.so.40.30.2)
==3720569==    by 0x4951564: opal_dss_pack_int32 (in /usr/lib/x86_64-linux-gnu/libopen-pal.so.40.30.2)
==3720569==    by 0x4951F59: opal_dss_pack (in /usr/lib/x86_64-linux-gnu/libopen-pal.so.40.30.2)
==3720569==    by 0x48B2A99: orte_pmix_server_register_nspace (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48CD8CC: orte_odls_base_default_construct_child_list (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0xA3C0C15: ???
==3720569==    by 0x48A1AAF: orte_daemon_recv (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48EDE3C: orte_rml_base_process_msg (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x10928B: ??? (in /usr/bin/orterun)
==3720569==
==3720569== 2,048 bytes in 1 blocks are definitely lost in loss record 281 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x495125E: opal_dss_buffer_extend (in /usr/lib/x86_64-linux-gnu/libopen-pal.so.40.30.2)
==3720569==    by 0x4951564: opal_dss_pack_int32 (in /usr/lib/x86_64-linux-gnu/libopen-pal.so.40.30.2)
==3720569==    by 0x4951F59: opal_dss_pack (in /usr/lib/x86_64-linux-gnu/libopen-pal.so.40.30.2)
==3720569==    by 0x48B2B81: orte_pmix_server_register_nspace (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48CD8CC: orte_odls_base_default_construct_child_list (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0xA3C0C15: ???
==3720569==    by 0x48A1AAF: orte_daemon_recv (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48EDE3C: orte_rml_base_process_msg (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x49F2EE7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x10928B: ??? (in /usr/bin/orterun)
==3720569==
==3720569== 2,760 (584 direct, 2,176 indirect) bytes in 1 blocks are definitely lost in loss record 283 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x782D02D: ???
==3720569==    by 0x782DD59: ???
==3720569==    by 0x49F2FD7: ??? (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x49F4BF6: event_base_loop (in /usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1)
==3720569==    by 0x7785405: ???
==3720569==    by 0x4A9EB42: start_thread (pthread_create.c:442)
==3720569==    by 0x4B2FBB3: clone (clone.S:100)
==3720569==
==3720569== 3,202 (72 direct, 3,130 indirect) bytes in 1 blocks are definitely lost in loss record 285 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x77B6517: ???
==3720569==    by 0x781543A: ???
==3720569==    by 0x77B5E8E: ???
==3720569==    by 0x77B5EE3: ???
==3720569==    by 0x775925B: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x1091E3: ??? (in /usr/bin/orterun)
==3720569==
==3720569== 71,575 (896 direct, 70,679 indirect) bytes in 1 blocks are definitely lost in loss record 293 of 294
==3720569==    at 0x4848899: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==3720569==    by 0x4C58C1E: ??? (in /usr/lib/x86_64-linux-gnu/libhwloc.so.15.5.2)
==3720569==    by 0x77344A1: ???
==3720569==    by 0x77597AE: ???
==3720569==    by 0x76D7383: ???
==3720569==    by 0x48ACB6C: pmix_server_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x5229188: ???
==3720569==    by 0x48F94CB: orte_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x48A6BE4: orte_submit_init (in /usr/lib/x86_64-linux-gnu/libopen-rte.so.40.30.2)
==3720569==    by 0x1091E3: ??? (in /usr/bin/orterun)
==3720569==    by 0x4A33D8F: (below main) (libc_start_call_main.h:58)
==3720569==
==3720569== LEAK SUMMARY:
==3720569==    definitely lost: 7,142 bytes in 27 blocks
==3720569==    indirectly lost: 79,234 bytes in 1,224 blocks
==3720569==      possibly lost: 0 bytes in 0 blocks
==3720569==    still reachable: 115,399 bytes in 134 blocks
==3720569==         suppressed: 0 bytes in 0 blocks
==3720569== Reachable blocks (those to which a pointer was found) are not shown.
==3720569== To see them, rerun with: --leak-check=full --show-leak-kinds=all
==3720569==
==3720569== For lists of detected and suppressed errors, rerun with: -s
==3720569== ERROR SUMMARY: 27 errors from 27 contexts (suppressed: 0 from 0)

### 1871
复现sha：7083d53dd7e59b2de82800e4571be5241f1fe7ad
/root/mfem-code-analyzer/get_normal_testcase_covarage/add_coverage.sh
cd examples
mpicxx -O3 -std=c++11 --coverage -I.. -I../../hypre/src/hypre/include 1871.cpp -o 1871 -L.. -lmfem -L../../hypre/src/hypre/lib -lHYPRE -L../../metis-4.0 -lmetis -lrt
mpirun -np 1 ./1871
结果：
root@f64125032199:~/mfem/examples# mpirun -np 1 ./1871
MFEM mesh v1.0

#
# MFEM Geometry Types (see mesh/geom.hpp):
#
# POINT       = 0
# SEGMENT     = 1
# TRIANGLE    = 2
# SQUARE      = 3
# TETRAHEDRON = 4
# CUBE        = 5
# PRISM       = 6
#

dimension
2

elements
4
1 3 0 1 2 3
1 3 1 4 5 2
1 3 2 5 6 7
1 3 3 2 7 8

boundary
8
1 1 0 1
4 1 3 0
1 1 1 4
2 1 4 5
2 1 5 6
3 1 6 7
3 1 7 8
4 1 8 3

vertices
9
2
0 0
0.5 0
0.5 0.5
0 0.5
1 0
1 0.5
1 1
0.5 1
0 1
FiniteElementSpace
FiniteElementCollection: RT_2D_P2
VDim: 1
Ordering: 1

0
0
0
0.125
0.125
0.125
0.125
0.125
0.125
0
0
0
0
0
0
0.5
0.5
0.5
-0.125
-0.125
-0.125
0.5
0.5
0.5
0.5
0.5
0.5
0.125
0.125
0.125
0.5
0.5
0.5
0
0
0
-0.0095491503
0.06545085
-0.0095491503
0.06545085
-0.0095491503
0.06545085
-0.0095491503
-0.0095491503
-0.0095491503
0.06545085
0.06545085
0.06545085
-0.20364745
0.37135255
-0.20364745
0.37135255
-0.20364745
0.37135255
-0.0095491503
-0.0095491503
-0.0095491503
0.06545085
0.06545085
0.06545085
-0.20364745
0.37135255
-0.20364745
0.37135255
-0.20364745
0.37135255
-0.20364745
-0.20364745
-0.20364745
0.37135255
0.37135255
0.37135255
-0.0095491503
0.06545085
-0.0095491503
0.06545085
-0.0095491503
0.06545085
-0.20364745
-0.20364745
-0.20364745
0.37135255
0.37135255
0.37135255
程序执行完毕。
执行的进程数: 1

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