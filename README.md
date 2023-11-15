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

## 编译失败：
### 2563
linalg/hypre.cpp:1566:48: error: cannot convert ‘HYPRE_BigInt**’ {aka ‘int**’} to ‘HYPRE_BigInt*’ {aka ‘int*’}
 1566 |                               CF_marker, NULL, &cpts_global);
      |                                                ^~~~~~~~~~~~
      |                                                |
      |                                                HYPRE_BigInt** {aka int**}
fem/bilininteg_hcurl.cpp:1749:26: warning: ‘void* __builtin_memcpy(void*, const void*, long unsigned int)’ writing between 8 and 34359738368 bytes into a region of size 0 overflows the destination [-Wstringop-overflow=]
 1749 |                sBc[d][q] = Bc(q,d);
      |                ~~~~~~~~~~^~~~~~~~~

### 2492
linalg/hypre.cpp:1549:31: error: cannot convert ‘mfem::Array<int>’ to ‘hypre_IntArray*’
 1549 |                               CF_marker, NULL, &cpts_global);
      |                               ^~~~~~~~~
      |                               |
      |                               mfem::Array<int>
fem/bilininteg_hcurl.cpp:1750:26: warning: ‘void* __builtin_memcpy(void*, const void*, long unsigned int)’ writing between 8 and 34359738368 bytes into a region of size 0 overflows the destination [-Wstringop-overflow=]
 1750 |                sGc[d][q] = Gc(q,d);
      |                ~~~~~~~~~~^~~~~~~~~

### 2413
linalg/hypre_parcsr.cpp:504:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  504 |    hypre_ParCSRMatrixSetRowStartsOwner(*Ae, 0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre_parcsr.cpp:505:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  505 |    hypre_ParCSRMatrixSetColStartsOwner(*Ae, 0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
mpicxx   -O3 -std=c++11 -I./../hypre/src/hypre/include  -c fem/conduitdatacollection.cpp -o fem/conduitdatacollection.o
linalg/hypre_parcsr.cpp: In function ‘void mfem::internal::hypre_ParCSRMatrixSplit(hypre_ParCSRMatrix*, HYPRE_Int, HYPRE_Int, hypre_ParCSRMatrix**, int, int)’:
linalg/hypre_parcsr.cpp:984:7: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  984 |       hypre_ParCSRMatrixOwnsRowStarts(blocks[i]) = !i;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixRowStarts
linalg/hypre_parcsr.cpp:985:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  985 |       hypre_ParCSRMatrixOwnsColStarts(blocks[i]) = !i;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
mpicxx   -O3 -std=c++11 -I./../hypre/src/hypre/include  -c fem/convergence.cpp -o fem/convergence.o
mpicxx   -O3 -std=c++11 -I./../hypre/src/hypre/include  -c fem/datacollection.cpp -o fem/datacollection.o
linalg/hypre_parcsr.cpp: In function ‘hypre_ParCSRMatrix* mfem::internal::hypre_ParCSRMatrixAdd(hypre_ParCSRMatrix*, hypre_ParCSRMatrix*)’:
linalg/hypre_parcsr.cpp:1898:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1898 |    hypre_ParCSRMatrixSetRowStartsOwner(C, 0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
mpicxx   -O3 -std=c++11 -I./../hypre/src/hypre/include  -c fem/eltrans.cpp -o fem/eltrans.o
linalg/hypre_parcsr.cpp:1899:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1899 |    hypre_ParCSRMatrixSetColStartsOwner(C, 0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner

### 2231
linalg/hypre_parcsr.cpp: In function ‘void mfem::internal::hypre_ParCSRMatrixEliminateAAe(hypre_ParCSRMatrix*, hypre_ParCSRMatrix**, HYPRE_Int, HYPRE_Int*, int)’:
linalg/hypre_parcsr.cpp:504:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  504 |    hypre_ParCSRMatrixSetRowStartsOwner(*Ae, 0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre_parcsr.cpp:505:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  505 |    hypre_ParCSRMatrixSetColStartsOwner(*Ae, 0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
mpicxx   -O3 -std=c++11 -I./../hypre/src/hypre/include  -c fem/pnonlinearform.cpp -o fem/pnonlinearform.o
mpicxx   -O3 -std=c++11 -I./../hypre/src/hypre/include  -c fem/prestriction.cpp -o fem/prestriction.o
linalg/hypre_parcsr.cpp: In function ‘void mfem::internal::hypre_ParCSRMatrixSplit(hypre_ParCSRMatrix*, HYPRE_Int, HYPRE_Int, hypre_ParCSRMatrix**, int, int)’:
linalg/hypre_parcsr.cpp:984:7: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  984 |       hypre_ParCSRMatrixOwnsRowStarts(blocks[i]) = !i;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixRowStarts
mpicxx   -O3 -std=c++11 -I./../hypre/src/hypre/include  -c fem/quadinterpolator.cpp -o fem/quadinterpolator.o
make: *** [makefile:430: linalg/complex_operator.o] Error 1
make: *** Waiting for unfinished jobs....
linalg/hypre_parcsr.cpp:985:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  985 |       hypre_ParCSRMatrixOwnsColStarts(blocks[i]) = !i;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre_parcsr.cpp: In function ‘hypre_ParCSRMatrix* mfem::internal::hypre_ParCSRMatrixAdd(hypre_ParCSRMatrix*, hypre_ParCSRMatrix*)’:
linalg/hypre_parcsr.cpp:1809:35: error: cannot convert ‘hypre_CSRMatrix*’ to ‘HYPRE_Complex’ {aka ‘double’}
 1809 |       C_diag = hypre_CSRMatrixAdd(A_diag, B_diag);
      |                                   ^~~~~~
      |                                   |
      |                                   hypre_CSRMatrix*
In file included from ./../hypre/src/hypre/include/_hypre_parcsr_mv.h:10,
                 from linalg/hypre_parcsr.hpp:22,
                 from linalg/hypre_parcsr.cpp:17:
./../hypre/src/hypre/include/seq_mv.h:291:53: note:   initializing argument 1 of ‘hypre_CSRMatrix* hypre_CSRMatrixAdd(HYPRE_Complex, hypre_CSRMatrix*, HYPRE_Complex, hypre_CSRMatrix*)’
  291 | hypre_CSRMatrix *hypre_CSRMatrixAdd ( HYPRE_Complex alpha, hypre_CSRMatrix *A, HYPRE_Complex beta,
      |                                       ~~~~~~~~~~~~~~^~~~~
linalg/hypre_parcsr.cpp:1814:35: error: cannot convert ‘hypre_CSRMatrix*’ to ‘HYPRE_Complex’ {aka ‘double’}
 1814 |       C_offd = hypre_CSRMatrixAdd(A_offd, B_offd);
      |                                   ^~~~~~
      |                                   |
      |                                   hypre_CSRMatrix*
In file included from ./../hypre/src/hypre/include/_hypre_parcsr_mv.h:10,
                 from linalg/hypre_parcsr.hpp:22,
                 from linalg/hypre_parcsr.cpp:17:
./../hypre/src/hypre/include/seq_mv.h:291:53: note:   initializing argument 1 of ‘hypre_CSRMatrix* hypre_CSRMatrixAdd(HYPRE_Complex, hypre_CSRMatrix*, HYPRE_Complex, hypre_CSRMatrix*)’
  291 | hypre_CSRMatrix *hypre_CSRMatrixAdd ( HYPRE_Complex alpha, hypre_CSRMatrix *A, HYPRE_Complex beta,
      |                                       ~~~~~~~~~~~~~~^~~~~
linalg/hypre_parcsr.cpp:1862:39: error: cannot convert ‘hypre_CSRMatrix*’ to ‘HYPRE_Complex’ {aka ‘double’}
 1862 |       csr_C_temp = hypre_CSRMatrixAdd(csr_A,csr_B);
      |                                       ^~~~~
      |                                       |
      |                                       hypre_CSRMatrix*
In file included from ./../hypre/src/hypre/include/_hypre_parcsr_mv.h:10,
                 from linalg/hypre_parcsr.hpp:22,
                 from linalg/hypre_parcsr.cpp:17:
./../hypre/src/hypre/include/seq_mv.h:291:53: note:   initializing argument 1 of ‘hypre_CSRMatrix* hypre_CSRMatrixAdd(HYPRE_Complex, hypre_CSRMatrix*, HYPRE_Complex, hypre_CSRMatrix*)’
  291 | hypre_CSRMatrix *hypre_CSRMatrixAdd ( HYPRE_Complex alpha, hypre_CSRMatrix *A, HYPRE_Complex beta,
      |                                       ~~~~~~~~~~~~~~^~~~~
linalg/hypre_parcsr.cpp:1898:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1898 |    hypre_ParCSRMatrixSetRowStartsOwner(C, 0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre_parcsr.cpp:1899:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1899 |    hypre_ParCSRMatrixSetColStartsOwner(C, 0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre_parcsr.cpp: In function ‘HYPRE_Int mfem::internal::hypre_ParCSRMatrixSetConstantValues(hypre_ParCSRMatrix*, HYPRE_Complex)’:
linalg/hypre_parcsr.cpp:1945:69: error: call of overloaded ‘hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix*&, HYPRE_Complex&)’ is ambiguous
 1945 |    hypre_CSRMatrixSetConstantValues(hypre_ParCSRMatrixDiag(A), value);
linalg/hypre_parcsr.cpp:1926:1: note: candidate: ‘HYPRE_Int mfem::internal::hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix*, HYPRE_Complex)’
 1926 | hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix *A,
      | ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In file included from ./../hypre/src/hypre/include/_hypre_parcsr_mv.h:10,
                 from linalg/hypre_parcsr.hpp:22,
                 from linalg/hypre_parcsr.cpp:17:
./../hypre/src/hypre/include/seq_mv.h:315:11: note: candidate: ‘HYPRE_Int hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix*, HYPRE_Complex)’
  315 | HYPRE_Int hypre_CSRMatrixSetConstantValues( hypre_CSRMatrix *A, HYPRE_Complex value);
      |           ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
linalg/hypre_parcsr.cpp:1946:69: error: call of overloaded ‘hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix*&, HYPRE_Complex&)’ is ambiguous
 1946 |    hypre_CSRMatrixSetConstantValues(hypre_ParCSRMatrixOffd(A), value);
      |                                                                     ^
linalg/hypre_parcsr.cpp:1926:1: note: candidate: ‘HYPRE_Int mfem::internal::hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix*, HYPRE_Complex)’
 1926 | hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix *A,
      | ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In file included from ./../hypre/src/hypre/include/_hypre_parcsr_mv.h:10,
                 from linalg/hypre_parcsr.hpp:22,
                 from linalg/hypre_parcsr.cpp:17:
./../hypre/src/hypre/include/seq_mv.h:315:11: note: candidate: ‘HYPRE_Int hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix*, HYPRE_Complex)’
  315 | HYPRE_Int hypre_CSRMatrixSetConstantValues( hypre_CSRMatrix *A, HYPRE_Complex value);
      |           ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
make: *** [makefile:430: linalg/hypre_parcsr.o] Error 1
linalg/hypre.cpp: In constructor ‘mfem::HypreParVector::HypreParVector(MPI_Comm, HYPRE_BigInt, HYPRE_BigInt*)’:
linalg/hypre.cpp:58:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
   58 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In constructor ‘mfem::HypreParVector::HypreParVector(MPI_Comm, HYPRE_BigInt, double*, HYPRE_BigInt*)’:
linalg/hypre.cpp:72:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
   72 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In copy constructor ‘mfem::HypreParVector::HypreParVector(const mfem::HypreParVector&)’:
linalg/hypre.cpp:89:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
   89 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In constructor ‘mfem::HypreParVector::HypreParVector(mfem::ParFiniteElementSpace*)’:
linalg/hypre.cpp:123:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
  123 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_BigInt, HYPRE_BigInt*, mfem::SparseMatrix*)’:
linalg/hypre.cpp:331:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  331 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:332:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  332 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_BigInt, HYPRE_BigInt, HYPRE_BigInt*, HYPRE_BigInt*, mfem::SparseMatrix*)’:
linalg/hypre.cpp:370:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  370 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:371:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  371 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_BigInt, HYPRE_BigInt, HYPRE_BigInt*, HYPRE_BigInt*, mfem::SparseMatrix*, mfem::SparseMatrix*, HYPRE_BigInt*)’:
linalg/hypre.cpp:409:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  409 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:410:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  410 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_BigInt, HYPRE_BigInt, HYPRE_BigInt*, HYPRE_BigInt*, HYPRE_Int*, HYPRE_Int*, double*, HYPRE_Int*, HYPRE_Int*, double*, HYPRE_Int, HYPRE_BigInt*)’:
linalg/hypre.cpp:451:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  451 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:452:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  452 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_BigInt, HYPRE_BigInt, HYPRE_BigInt*, HYPRE_BigInt*, mfem::Table*)’:
linalg/hypre.cpp:544:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  544 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:545:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  545 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, int, int, HYPRE_BigInt*, HYPRE_BigInt*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_BigInt*, HYPRE_Int)’:
linalg/hypre.cpp:600:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  600 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:601:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  601 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In member function ‘void mfem::HypreParMatrix::CopyRowStarts()’:
linalg/hypre.cpp:830:14: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  830 |    if (!A || hypre_ParCSRMatrixOwnsRowStarts(A) ||
      |              ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |              hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:832:9: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  832 |         hypre_ParCSRMatrixOwnsColStarts(A)))
      |         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |         hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:856:35: error: incompatible types in assignment of ‘HYPRE_BigInt*’ {aka ‘int*’} to ‘HYPRE_BigInt [2]’ {aka ‘int [2]’}
  856 |    hypre_ParCSRMatrixRowStarts(A) = new_row_starts;
linalg/hypre.cpp:857:4: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  857 |    hypre_ParCSRMatrixOwnsRowStarts(A) = 1;
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:861:38: error: incompatible types in assignment of ‘HYPRE_BigInt*’ {aka ‘int*’} to ‘HYPRE_BigInt [2]’ {aka ‘int [2]’}
  861 |       hypre_ParCSRMatrixColStarts(A) = new_row_starts;
linalg/hypre.cpp:862:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  862 |       hypre_ParCSRMatrixOwnsColStarts(A) = 0;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp: In member function ‘void mfem::HypreParMatrix::CopyColStarts()’:
linalg/hypre.cpp:868:14: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  868 |    if (!A || hypre_ParCSRMatrixOwnsColStarts(A) ||
      |              ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |              hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:870:9: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  870 |         hypre_ParCSRMatrixOwnsRowStarts(A)))
      |         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |         hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:894:35: error: incompatible types in assignment of ‘HYPRE_BigInt*’ {aka ‘int*’} to ‘HYPRE_BigInt [2]’ {aka ‘int [2]’}
  894 |    hypre_ParCSRMatrixColStarts(A) = new_col_starts;
linalg/hypre.cpp:898:38: error: incompatible types in assignment of ‘HYPRE_BigInt*’ {aka ‘int*’} to ‘HYPRE_BigInt [2]’ {aka ‘int [2]’}
  898 |       hypre_ParCSRMatrixRowStarts(A) = new_col_starts;
linalg/hypre.cpp:899:7: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  899 |       hypre_ParCSRMatrixOwnsRowStarts(A) = 1;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:900:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  900 |       hypre_ParCSRMatrixOwnsColStarts(A) = 0;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:904:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  904 |       hypre_ParCSRMatrixOwnsColStarts(A) = 1;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp: In member function ‘mfem::HypreParMatrix* mfem::HypreParMatrix::ExtractSubmatrix(const mfem::Array<int>&, double) const’:
linalg/hypre.cpp:1028:31: error: cannot convert ‘mfem::Array<int>’ to ‘hypre_IntArray*’
 1028 |                               CF_marker, NULL, &cpts_global);
      |                               ^~~~~~~~~
      |                               |
      |                               mfem::Array<int>
In file included from linalg/hypre.hpp:27,
                 from linalg/complex_operator.hpp:18,
                 from linalg/linalg.hpp:21,
                 from linalg/hypre.cpp:16:
./../hypre/src/hypre/include/_hypre_parcsr_ls.h:2360:107: note:   initializing argument 5 of ‘HYPRE_Int hypre_BoomerAMGCoarseParms(MPI_Comm, HYPRE_Int, HYPRE_Int, hypre_IntArray*, hypre_IntArray*, hypre_IntArray**, HYPRE_BigInt*)’
 2360 |                                        HYPRE_Int num_functions, hypre_IntArray *dof_func, hypre_IntArray *CF_marker,
      |                                                                                           ~~~~~~~~~~~~~~~~^~~~~~~~~
linalg/hypre.cpp: In member function ‘mfem::HypreParMatrix* mfem::HypreParMatrix::LeftDiagMult(const mfem::SparseMatrix&, HYPRE_BigInt*) const’:
linalg/hypre.cpp:1239:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1239 |    hypre_ParCSRMatrixSetRowStartsOwner(DA->A, 1);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:1240:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1240 |    hypre_ParCSRMatrixSetColStartsOwner(DA->A, 1);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In member function ‘void mfem::HypreParMatrix::Threshold(double)’:
linalg/hypre.cpp:1384:24: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
 1384 |    bool old_owns_row = hypre_ParCSRMatrixOwnsRowStarts(A);
      |                        ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |                        hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:1385:24: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
 1385 |    bool old_owns_col = hypre_ParCSRMatrixOwnsColStarts(A);
      |                        ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |                        hypre_ParCSRMatrixColStarts
linalg/hypre.cpp: In function ‘mfem::HypreParMatrix* mfem::Add(double, const mfem::HypreParMatrix&, double, const mfem::HypreParMatrix&)’:
linalg/hypre.cpp:1816:4: error: ‘hypre_ParcsrAdd’ was not declared in this scope; did you mean ‘hypre_GraphAdd’?
 1816 |    hypre_ParcsrAdd(alpha, A, beta, B, &C);
      |    ^~~~~~~~~~~~~~~
      |    hypre_GraphAdd
linalg/hypre.cpp: In function ‘mfem::HypreParMatrix* mfem::ParAdd(const mfem::HypreParMatrix*, const mfem::HypreParMatrix*)’:
linalg/hypre.cpp:1824:4: error: ‘hypre_ParcsrAdd’ was not declared in this scope; did you mean ‘hypre_GraphAdd’?
 1824 |    hypre_ParcsrAdd(1.0, *A, 1.0, *B, &C);
      |    ^~~~~~~~~~~~~~~
      |    hypre_GraphAdd
linalg/hypre.cpp: In function ‘mfem::HypreParMatrix* mfem::RAP(const mfem::HypreParMatrix*, const mfem::HypreParMatrix*)’:
linalg/hypre.cpp:1851:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
 1851 |       hypre_ParCSRMatrixOwnsColStarts((hypre_ParCSRMatrix*)(*P));
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:1860:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1860 |    hypre_ParCSRMatrixSetRowStartsOwner(rap,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:1861:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1861 |    hypre_ParCSRMatrixSetColStartsOwner(rap,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In function ‘mfem::HypreParMatrix* mfem::RAP(const mfem::HypreParMatrix*, const mfem::HypreParMatrix*, const mfem::HypreParMatrix*)’:
linalg/hypre.cpp:1875:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
 1875 |       hypre_ParCSRMatrixOwnsColStarts((hypre_ParCSRMatrix*)(*P));
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:1887:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1887 |    hypre_ParCSRMatrixSetRowStartsOwner(rap,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:1888:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1888 |    hypre_ParCSRMatrixSetColStartsOwner(rap,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In member function ‘virtual void mfem::HypreSmoother::SetOperator(const mfem::Operator&)’:
linalg/hypre.cpp:2509:65: error: too few arguments to function ‘HYPRE_Int hypre_ParCSRMaxEigEstimate(hypre_ParCSRMatrix*, HYPRE_Int, HYPRE_Real*, HYPRE_Real*)’
 2509 |          hypre_ParCSRMaxEigEstimate(*A, poly_scale, &max_eig_est);
      |                                                                 ^
In file included from linalg/hypre.hpp:27,
                 from linalg/complex_operator.hpp:18,
                 from linalg/linalg.hpp:21,
                 from linalg/hypre.cpp:16:
./../hypre/src/hypre/include/_hypre_parcsr_ls.h:2812:11: note: declared here
 2812 | HYPRE_Int hypre_ParCSRMaxEigEstimate ( hypre_ParCSRMatrix *A, HYPRE_Int scale, HYPRE_Real *max_eig,
      |           ^~~~~~~~~~~~~~~~~~~~~~~~~~
linalg/hypre.cpp:2524:65: error: too few arguments to function ‘HYPRE_Int hypre_ParCSRMaxEigEstimate(hypre_ParCSRMatrix*, HYPRE_Int, HYPRE_Real*, HYPRE_Real*)’
 2524 |          hypre_ParCSRMaxEigEstimate(*A, poly_scale, &max_eig_est);
      |                                                                 ^
In file included from linalg/hypre.hpp:27,
                 from linalg/complex_operator.hpp:18,
                 from linalg/linalg.hpp:21,
                 from linalg/hypre.cpp:16:
./../hypre/src/hypre/include/_hypre_parcsr_ls.h:2812:11: note: declared here
 2812 | HYPRE_Int hypre_ParCSRMaxEigEstimate ( hypre_ParCSRMatrix *A, HYPRE_Int scale, HYPRE_Real *max_eig,
      |           ^~~~~~~~~~~~~~~~~~~~~~~~~~
fem/pfespace.cpp: In member function ‘void mfem::ParFiniteElementSpace::Lose_Dof_TrueDof_Matrix()’:
fem/pfespace.cpp:1281:4: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
 1281 |    hypre_ParCSRMatrixOwnsRowStarts(csrP) = 1;
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixRowStarts
fem/pfespace.cpp:1282:4: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
 1282 |    hypre_ParCSRMatrixOwnsColStarts(csrP) = 1;
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### 2144
linalg/hypre_parcsr.cpp:504:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  504 |    hypre_ParCSRMatrixSetRowStartsOwner(*Ae, 0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
mpicxx   -O3 -std=c++11 -I./../hypre/src/hypre/include  -c fem/ceed/full-assembly.cpp -o fem/ceed/full-assembly.o
linalg/hypre_parcsr.cpp:505:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  505 |    hypre_ParCSRMatrixSetColStartsOwner(*Ae, 0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
mpicxx   -O3 -std=c++11 -I./../hypre/src/hypre/include  -c fem/ceed/mass.cpp -o fem/ceed/mass.o
mpicxx   -O3 -std=c++11 -I./../hypre/src/hypre/include  -c fem/ceed/nlconvection.cpp -o fem/ceed/nlconvection.o
mpicxx   -O3 -std=c++11 -I./../hypre/src/hypre/include  -c fem/ceed/operator.cpp -o fem/ceed/operator.o
linalg/hypre_parcsr.cpp: In function ‘void mfem::internal::hypre_ParCSRMatrixSplit(hypre_ParCSRMatrix*, HYPRE_Int, HYPRE_Int, hypre_ParCSRMatrix**, int, int)’:
linalg/hypre_parcsr.cpp:976:7: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  976 |       hypre_ParCSRMatrixOwnsRowStarts(blocks[i]) = !i;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixRowStarts
mpicxx   -O3 -std=c++11 -I./../hypre/src/hypre/include  -c fem/ceed/solvers-atpmg.cpp -o fem/ceed/solvers-atpmg.o
mpicxx   -O3 -std=c++11 -I./../hypre/src/hypre/include  -c fem/ceed/util.cpp -o fem/ceed/util.o
linalg/hypre_parcsr.cpp:977:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  977 |       hypre_ParCSRMatrixOwnsColStarts(blocks[i]) = !i;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre_parcsr.cpp: In function ‘hypre_ParCSRMatrix* mfem::internal::hypre_ParCSRMatrixAdd(hypre_ParCSRMatrix*, hypre_ParCSRMatrix*)’:
linalg/hypre_parcsr.cpp:1801:35: error: cannot convert ‘hypre_CSRMatrix*’ to ‘HYPRE_Complex’ {aka ‘double’}
 1801 |       C_diag = hypre_CSRMatrixAdd(A_diag, B_diag);
      |                                   ^~~~~~
      |                                   |
      |                                   hypre_CSRMatrix*
In file included from ./../hypre/src/hypre/include/_hypre_parcsr_mv.h:10,
                 from linalg/hypre_parcsr.hpp:22,
                 from linalg/hypre_parcsr.cpp:17:
./../hypre/src/hypre/include/seq_mv.h:291:53: note:   initializing argument 1 of ‘hypre_CSRMatrix* hypre_CSRMatrixAdd(HYPRE_Complex, hypre_CSRMatrix*, HYPRE_Complex, hypre_CSRMatrix*)’
  291 | hypre_CSRMatrix *hypre_CSRMatrixAdd ( HYPRE_Complex alpha, hypre_CSRMatrix *A, HYPRE_Complex beta,
      |                                       ~~~~~~~~~~~~~~^~~~~
linalg/hypre_parcsr.cpp:1806:35: error: cannot convert ‘hypre_CSRMatrix*’ to ‘HYPRE_Complex’ {aka ‘double’}
 1806 |       C_offd = hypre_CSRMatrixAdd(A_offd, B_offd);
      |                                   ^~~~~~
      |                                   |
      |                                   hypre_CSRMatrix*
In file included from ./../hypre/src/hypre/include/_hypre_parcsr_mv.h:10,
                 from linalg/hypre_parcsr.hpp:22,
                 from linalg/hypre_parcsr.cpp:17:
./../hypre/src/hypre/include/seq_mv.h:291:53: note:   initializing argument 1 of ‘hypre_CSRMatrix* hypre_CSRMatrixAdd(HYPRE_Complex, hypre_CSRMatrix*, HYPRE_Complex, hypre_CSRMatrix*)’
  291 | hypre_CSRMatrix *hypre_CSRMatrixAdd ( HYPRE_Complex alpha, hypre_CSRMatrix *A, HYPRE_Complex beta,
      |                                       ~~~~~~~~~~~~~~^~~~~
linalg/hypre_parcsr.cpp:1854:39: error: cannot convert ‘hypre_CSRMatrix*’ to ‘HYPRE_Complex’ {aka ‘double’}
 1854 |       csr_C_temp = hypre_CSRMatrixAdd(csr_A,csr_B);
      |                                       ^~~~~
      |                                       |
      |                                       hypre_CSRMatrix*
In file included from ./../hypre/src/hypre/include/_hypre_parcsr_mv.h:10,
                 from linalg/hypre_parcsr.hpp:22,
                 from linalg/hypre_parcsr.cpp:17:
./../hypre/src/hypre/include/seq_mv.h:291:53: note:   initializing argument 1 of ‘hypre_CSRMatrix* hypre_CSRMatrixAdd(HYPRE_Complex, hypre_CSRMatrix*, HYPRE_Complex, hypre_CSRMatrix*)’
  291 | hypre_CSRMatrix *hypre_CSRMatrixAdd ( HYPRE_Complex alpha, hypre_CSRMatrix *A, HYPRE_Complex beta,
      |                                       ~~~~~~~~~~~~~~^~~~~
linalg/hypre_parcsr.cpp:1890:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1890 |    hypre_ParCSRMatrixSetRowStartsOwner(C, 0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre_parcsr.cpp:1891:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1891 |    hypre_ParCSRMatrixSetColStartsOwner(C, 0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre_parcsr.cpp: In function ‘HYPRE_Int mfem::internal::hypre_ParCSRMatrixSetConstantValues(hypre_ParCSRMatrix*, HYPRE_Complex)’:
linalg/hypre_parcsr.cpp:1937:69: error: call of overloaded ‘hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix*&, HYPRE_Complex&)’ is ambiguous
 1937 |    hypre_CSRMatrixSetConstantValues(hypre_ParCSRMatrixDiag(A), value);
      |                                                                     ^
linalg/hypre_parcsr.cpp:1918:1: note: candidate: ‘HYPRE_Int mfem::internal::hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix*, HYPRE_Complex)’
 1918 | hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix *A,
      | ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In file included from ./../hypre/src/hypre/include/_hypre_parcsr_mv.h:10,
                 from linalg/hypre_parcsr.hpp:22,
                 from linalg/hypre_parcsr.cpp:17:
./../hypre/src/hypre/include/seq_mv.h:315:11: note: candidate: ‘HYPRE_Int hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix*, HYPRE_Complex)’
  315 | HYPRE_Int hypre_CSRMatrixSetConstantValues( hypre_CSRMatrix *A, HYPRE_Complex value);
      |           ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
linalg/hypre_parcsr.cpp:1938:69: error: call of overloaded ‘hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix*&, HYPRE_Complex&)’ is ambiguous
 1938 |    hypre_CSRMatrixSetConstantValues(hypre_ParCSRMatrixOffd(A), value);
      |                                                                     ^
linalg/hypre_parcsr.cpp:1918:1: note: candidate: ‘HYPRE_Int mfem::internal::hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix*, HYPRE_Complex)’
 1918 | hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix *A,
      | ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In file included from ./../hypre/src/hypre/include/_hypre_parcsr_mv.h:10,
                 from linalg/hypre_parcsr.hpp:22,
                 from linalg/hypre_parcsr.cpp:17:
./../hypre/src/hypre/include/seq_mv.h:315:11: note: candidate: ‘HYPRE_Int hypre_CSRMatrixSetConstantValues(hypre_CSRMatrix*, HYPRE_Complex)’
  315 | HYPRE_Int hypre_CSRMatrixSetConstantValues( hypre_CSRMatrix *A, HYPRE_Complex value);
      |           ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
make: *** [makefile:430: linalg/hypre_parcsr.o] Error 1
make: *** Waiting for unfinished jobs....
linalg/complex_operator.cpp: In member function ‘mfem::HypreParMatrix* mfem::ComplexHypreParMatrix::GetSystemMatrix() const’:
linalg/complex_operator.cpp:802:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  802 |    hypre_ParCSRMatrixSetRowStartsOwner((hypre_ParCSRMatrix*)(*A),1);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/complex_operator.cpp:803:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  803 |    hypre_ParCSRMatrixSetColStartsOwner((hypre_ParCSRMatrix*)(*A),1);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
make: *** [makefile:430: linalg/complex_operator.o] Error 1
linalg/hypre.cpp: In constructor ‘mfem::HypreParVector::HypreParVector(MPI_Comm, HYPRE_Int, HYPRE_Int*)’:
linalg/hypre.cpp:58:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
   58 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In constructor ‘mfem::HypreParVector::HypreParVector(MPI_Comm, HYPRE_Int, double*, HYPRE_Int*)’:
linalg/hypre.cpp:72:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
   72 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In copy constructor ‘mfem::HypreParVector::HypreParVector(const mfem::HypreParVector&)’:
linalg/hypre.cpp:89:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
   89 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In constructor ‘mfem::HypreParVector::HypreParVector(mfem::ParFiniteElementSpace*)’:
linalg/hypre.cpp:123:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
  123 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int*, mfem::SparseMatrix*)’:
linalg/hypre.cpp:321:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  321 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:322:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  322 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int, HYPRE_Int*, HYPRE_Int*, mfem::SparseMatrix*)’:
linalg/hypre.cpp:360:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  360 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:361:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  361 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int, HYPRE_Int*, HYPRE_Int*, mfem::SparseMatrix*, mfem::SparseMatrix*, HYPRE_Int*)’:
linalg/hypre.cpp:399:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  399 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:400:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  400 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, double*, HYPRE_Int*, HYPRE_Int*, double*, HYPRE_Int, HYPRE_Int*)’:
linalg/hypre.cpp:441:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  441 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:442:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  442 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
fem/pfespace.cpp: In member function ‘void mfem::ParFiniteElementSpace::Lose_Dof_TrueDof_Matrix()’:
fem/pfespace.cpp:1281:4: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
 1281 |    hypre_ParCSRMatrixOwnsRowStarts(csrP) = 1;
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int, HYPRE_Int*, HYPRE_Int*, mfem::Table*)’:
linalg/hypre.cpp:534:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  534 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
fem/pfespace.cpp:1282:4: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
 1282 |    hypre_ParCSRMatrixOwnsColStarts(csrP) = 1;
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:535:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  535 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, int, int, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int)’:
linalg/hypre.cpp:590:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  590 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:591:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  591 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In member function ‘void mfem::HypreParMatrix::CopyRowStarts()’:
linalg/hypre.cpp:820:14: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  820 |    if (!A || hypre_ParCSRMatrixOwnsRowStarts(A) ||
      |              ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |              hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:822:9: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  822 |         hypre_ParCSRMatrixOwnsColStarts(A)))
      |         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |         hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:845:35: error: incompatible types in assignment of ‘HYPRE_Int*’ {aka ‘int*’} to ‘HYPRE_BigInt [2]’ {aka ‘int [2]’}
  845 |    hypre_ParCSRMatrixRowStarts(A) = new_row_starts;
linalg/hypre.cpp:846:4: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  846 |    hypre_ParCSRMatrixOwnsRowStarts(A) = 1;
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:850:38: error: incompatible types in assignment of ‘HYPRE_Int*’ {aka ‘int*’} to ‘HYPRE_BigInt [2]’ {aka ‘int [2]’}
  850 |       hypre_ParCSRMatrixColStarts(A) = new_row_starts;
linalg/hypre.cpp:851:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  851 |       hypre_ParCSRMatrixOwnsColStarts(A) = 0;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp: In member function ‘void mfem::HypreParMatrix::CopyColStarts()’:
linalg/hypre.cpp:857:14: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  857 |    if (!A || hypre_ParCSRMatrixOwnsColStarts(A) ||
      |              ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |              hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:859:9: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  859 |         hypre_ParCSRMatrixOwnsRowStarts(A)))
      |         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |         hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:882:35: error: incompatible types in assignment of ‘HYPRE_Int*’ {aka ‘int*’} to ‘HYPRE_BigInt [2]’ {aka ‘int [2]’}
  882 |    hypre_ParCSRMatrixColStarts(A) = new_col_starts;
linalg/hypre.cpp:886:38: error: incompatible types in assignment of ‘HYPRE_Int*’ {aka ‘int*’} to ‘HYPRE_BigInt [2]’ {aka ‘int [2]’}
  886 |       hypre_ParCSRMatrixRowStarts(A) = new_col_starts;
linalg/hypre.cpp:887:7: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  887 |       hypre_ParCSRMatrixOwnsRowStarts(A) = 1;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:888:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  888 |       hypre_ParCSRMatrixOwnsColStarts(A) = 0;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:892:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  892 |       hypre_ParCSRMatrixOwnsColStarts(A) = 1;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp: In member function ‘mfem::HypreParMatrix* mfem::HypreParMatrix::ExtractSubmatrix(const mfem::Array<int>&, double) const’:
linalg/hypre.cpp:1016:31: error: cannot convert ‘mfem::Array<int>’ to ‘hypre_IntArray*’
 1016 |                               CF_marker, NULL, &cpts_global);
      |                               ^~~~~~~~~
      |                               |
      |                               mfem::Array<int>
In file included from linalg/hypre.hpp:27,
                 from linalg/complex_operator.hpp:18,
                 from linalg/linalg.hpp:21,
                 from linalg/hypre.cpp:16:
./../hypre/src/hypre/include/_hypre_parcsr_ls.h:2360:107: note:   initializing argument 5 of ‘HYPRE_Int hypre_BoomerAMGCoarseParms(MPI_Comm, HYPRE_Int, HYPRE_Int, hypre_IntArray*, hypre_IntArray*, hypre_IntArray**, HYPRE_BigInt*)’
 2360 |                                        HYPRE_Int num_functions, hypre_IntArray *dof_func, hypre_IntArray *CF_marker,
      |                                                                                           ~~~~~~~~~~~~~~~~^~~~~~~~~
linalg/hypre.cpp: In member function ‘mfem::HypreParMatrix* mfem::HypreParMatrix::LeftDiagMult(const mfem::SparseMatrix&, HYPRE_Int*) const’:
linalg/hypre.cpp:1227:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1227 |    hypre_ParCSRMatrixSetRowStartsOwner(DA->A, 1);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:1228:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1228 |    hypre_ParCSRMatrixSetColStartsOwner(DA->A, 1);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In member function ‘void mfem::HypreParMatrix::Threshold(double)’:
linalg/hypre.cpp:1372:24: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
 1372 |    bool old_owns_row = hypre_ParCSRMatrixOwnsRowStarts(A);
      |                        ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |                        hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:1373:24: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
 1373 |    bool old_owns_col = hypre_ParCSRMatrixOwnsColStarts(A);
      |                        ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |                        hypre_ParCSRMatrixColStarts
linalg/hypre.cpp: In function ‘mfem::HypreParMatrix* mfem::Add(double, const mfem::HypreParMatrix&, double, const mfem::HypreParMatrix&)’:
linalg/hypre.cpp:1737:4: error: ‘hypre_ParcsrAdd’ was not declared in this scope; did you mean ‘hypre_GraphAdd’?
 1737 |    hypre_ParcsrAdd(alpha, A, beta, B, &C);
      |    ^~~~~~~~~~~~~~~
      |    hypre_GraphAdd
linalg/hypre.cpp: In function ‘mfem::HypreParMatrix* mfem::ParAdd(const mfem::HypreParMatrix*, const mfem::HypreParMatrix*)’:
linalg/hypre.cpp:1745:4: error: ‘hypre_ParcsrAdd’ was not declared in this scope; did you mean ‘hypre_GraphAdd’?
 1745 |    hypre_ParcsrAdd(1.0, *A, 1.0, *B, &C);
      |    ^~~~~~~~~~~~~~~
      |    hypre_GraphAdd
linalg/hypre.cpp: In function ‘mfem::HypreParMatrix* mfem::RAP(const mfem::HypreParMatrix*, const mfem::HypreParMatrix*)’:
linalg/hypre.cpp:1772:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
 1772 |       hypre_ParCSRMatrixOwnsColStarts((hypre_ParCSRMatrix*)(*P));
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:1781:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1781 |    hypre_ParCSRMatrixSetRowStartsOwner(rap,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:1782:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1782 |    hypre_ParCSRMatrixSetColStartsOwner(rap,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In function ‘mfem::HypreParMatrix* mfem::RAP(const mfem::HypreParMatrix*, const mfem::HypreParMatrix*, const mfem::HypreParMatrix*)’:
linalg/hypre.cpp:1796:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
 1796 |       hypre_ParCSRMatrixOwnsColStarts((hypre_ParCSRMatrix*)(*P));
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:1808:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1808 |    hypre_ParCSRMatrixSetRowStartsOwner(rap,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:1809:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1809 |    hypre_ParCSRMatrixSetColStartsOwner(rap,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In member function ‘virtual void mfem::HypreSmoother::SetOperator(const mfem::Operator&)’:
linalg/hypre.cpp:2428:65: error: too few arguments to function ‘HYPRE_Int hypre_ParCSRMaxEigEstimate(hypre_ParCSRMatrix*, HYPRE_Int, HYPRE_Real*, HYPRE_Real*)’
 2428 |          hypre_ParCSRMaxEigEstimate(*A, poly_scale, &max_eig_est);
      |                                                                 ^
In file included from linalg/hypre.hpp:27,
                 from linalg/complex_operator.hpp:18,
                 from linalg/linalg.hpp:21,
                 from linalg/hypre.cpp:16:
./../hypre/src/hypre/include/_hypre_parcsr_ls.h:2812:11: note: declared here
 2812 | HYPRE_Int hypre_ParCSRMaxEigEstimate ( hypre_ParCSRMatrix *A, HYPRE_Int scale, HYPRE_Real *max_eig,
      |           ^~~~~~~~~~~~~~~~~~~~~~~~~~
linalg/hypre.cpp:2443:65: error: too few arguments to function ‘HYPRE_Int hypre_ParCSRMaxEigEstimate(hypre_ParCSRMatrix*, HYPRE_Int, HYPRE_Real*, HYPRE_Real*)’
 2443 |          hypre_ParCSRMaxEigEstimate(*A, poly_scale, &max_eig_est);
      |                                                                 ^

### 2035
linalg/complex_operator.cpp:802:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  802 |    hypre_ParCSRMatrixSetRowStartsOwner((hypre_ParCSRMatrix*)(*A),1);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/complex_operator.cpp:803:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  803 |    hypre_ParCSRMatrixSetColStartsOwner((hypre_ParCSRMatrix*)(*A),1);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
make: *** [makefile:430: linalg/complex_operator.o] Error 1
linalg/hypre.cpp: In constructor ‘mfem::HypreParVector::HypreParVector(MPI_Comm, HYPRE_Int, HYPRE_Int*)’:
linalg/hypre.cpp:58:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
   58 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In constructor ‘mfem::HypreParVector::HypreParVector(MPI_Comm, HYPRE_Int, double*, HYPRE_Int*)’:
linalg/hypre.cpp:72:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
   72 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In copy constructor ‘mfem::HypreParVector::HypreParVector(const mfem::HypreParVector&)’:
linalg/hypre.cpp:89:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
   89 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In constructor ‘mfem::HypreParVector::HypreParVector(mfem::ParFiniteElementSpace*)’:
linalg/hypre.cpp:123:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
  123 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int*, mfem::SparseMatrix*)’:
linalg/hypre.cpp:321:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  321 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:322:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  322 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int, HYPRE_Int*, HYPRE_Int*, mfem::SparseMatrix*)’:
linalg/hypre.cpp:360:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  360 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
fem/pfespace.cpp: In member function ‘void mfem::ParFiniteElementSpace::Lose_Dof_TrueDof_Matrix()’:
fem/pfespace.cpp:1281:4: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
 1281 |    hypre_ParCSRMatrixOwnsRowStarts(csrP) = 1;
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixRowStarts
fem/pfespace.cpp:1282:4: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
 1282 |    hypre_ParCSRMatrixOwnsColStarts(csrP) = 1;
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:361:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  361 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int, HYPRE_Int*, HYPRE_Int*, mfem::SparseMatrix*, mfem::SparseMatrix*, HYPRE_Int*)’:
linalg/hypre.cpp:399:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  399 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:400:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  400 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, double*, HYPRE_Int*, HYPRE_Int*, double*, HYPRE_Int, HYPRE_Int*)’:
linalg/hypre.cpp:441:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  441 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:442:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  442 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int, HYPRE_Int*, HYPRE_Int*, mfem::Table*)’:
linalg/hypre.cpp:534:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  534 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:535:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  535 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, int, int, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int)’:
linalg/hypre.cpp:590:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  590 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:591:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  591 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In member function ‘void mfem::HypreParMatrix::CopyRowStarts()’:
linalg/hypre.cpp:820:14: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  820 |    if (!A || hypre_ParCSRMatrixOwnsRowStarts(A) ||
      |              ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |              hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:822:9: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  822 |         hypre_ParCSRMatrixOwnsColStarts(A)))
      |         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |         hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:845:35: error: incompatible types in assignment of ‘HYPRE_Int*’ {aka ‘int*’} to ‘HYPRE_BigInt [2]’ {aka ‘int [2]’}
  845 |    hypre_ParCSRMatrixRowStarts(A) = new_row_starts;
linalg/hypre.cpp:846:4: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  846 |    hypre_ParCSRMatrixOwnsRowStarts(A) = 1;
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:850:38: error: incompatible types in assignment of ‘HYPRE_Int*’ {aka ‘int*’} to ‘HYPRE_BigInt [2]’ {aka ‘int [2]’}
  850 |       hypre_ParCSRMatrixColStarts(A) = new_row_starts;
make: *** [makefile:430: fem/pfespace.o] Error 1
linalg/hypre.cpp:851:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  851 |       hypre_ParCSRMatrixOwnsColStarts(A) = 0;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp: In member function ‘void mfem::HypreParMatrix::CopyColStarts()’:
linalg/hypre.cpp:857:14: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  857 |    if (!A || hypre_ParCSRMatrixOwnsColStarts(A) ||
      |              ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |              hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:859:9: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  859 |         hypre_ParCSRMatrixOwnsRowStarts(A)))
      |         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |         hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:882:35: error: incompatible types in assignment of ‘HYPRE_Int*’ {aka ‘int*’} to ‘HYPRE_BigInt [2]’ {aka ‘int [2]’}
  882 |    hypre_ParCSRMatrixColStarts(A) = new_col_starts;
linalg/hypre.cpp:886:38: error: incompatible types in assignment of ‘HYPRE_Int*’ {aka ‘int*’} to ‘HYPRE_BigInt [2]’ {aka ‘int [2]’}
  886 |       hypre_ParCSRMatrixRowStarts(A) = new_col_starts;
linalg/hypre.cpp:887:7: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
  887 |       hypre_ParCSRMatrixOwnsRowStarts(A) = 1;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:888:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  888 |       hypre_ParCSRMatrixOwnsColStarts(A) = 0;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:892:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
  892 |       hypre_ParCSRMatrixOwnsColStarts(A) = 1;
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp: In member function ‘mfem::HypreParMatrix* mfem::HypreParMatrix::ExtractSubmatrix(const mfem::Array<int>&, double) const’:
linalg/hypre.cpp:1016:31: error: cannot convert ‘mfem::Array<int>’ to ‘hypre_IntArray*’
 1016 |                               CF_marker, NULL, &cpts_global);
      |                               ^~~~~~~~~
      |                               |
      |                               mfem::Array<int>
In file included from linalg/hypre.hpp:27,
                 from linalg/complex_operator.hpp:18,
                 from linalg/linalg.hpp:21,
                 from linalg/hypre.cpp:16:
./../hypre/src/hypre/include/_hypre_parcsr_ls.h:2360:107: note:   initializing argument 5 of ‘HYPRE_Int hypre_BoomerAMGCoarseParms(MPI_Comm, HYPRE_Int, HYPRE_Int, hypre_IntArray*, hypre_IntArray*, hypre_IntArray**, HYPRE_BigInt*)’
 2360 |                                        HYPRE_Int num_functions, hypre_IntArray *dof_func, hypre_IntArray *CF_marker,
      |                                                                                           ~~~~~~~~~~~~~~~~^~~~~~~~~
linalg/hypre.cpp: In member function ‘mfem::HypreParMatrix* mfem::HypreParMatrix::LeftDiagMult(const mfem::SparseMatrix&, HYPRE_Int*) const’:
linalg/hypre.cpp:1227:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1227 |    hypre_ParCSRMatrixSetRowStartsOwner(DA->A, 1);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:1228:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1228 |    hypre_ParCSRMatrixSetColStartsOwner(DA->A, 1);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In member function ‘void mfem::HypreParMatrix::Threshold(double)’:
linalg/hypre.cpp:1372:24: error: ‘hypre_ParCSRMatrixOwnsRowStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixRowStarts’?
 1372 |    bool old_owns_row = hypre_ParCSRMatrixOwnsRowStarts(A);
      |                        ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |                        hypre_ParCSRMatrixRowStarts
linalg/hypre.cpp:1373:24: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
 1373 |    bool old_owns_col = hypre_ParCSRMatrixOwnsColStarts(A);
      |                        ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |                        hypre_ParCSRMatrixColStarts
linalg/hypre.cpp: In function ‘mfem::HypreParMatrix* mfem::Add(double, const mfem::HypreParMatrix&, double, const mfem::HypreParMatrix&)’:
linalg/hypre.cpp:1737:4: error: ‘hypre_ParcsrAdd’ was not declared in this scope; did you mean ‘hypre_GraphAdd’?
 1737 |    hypre_ParcsrAdd(alpha, A, beta, B, &C);
      |    ^~~~~~~~~~~~~~~
      |    hypre_GraphAdd
linalg/hypre.cpp: In function ‘mfem::HypreParMatrix* mfem::ParAdd(const mfem::HypreParMatrix*, const mfem::HypreParMatrix*)’:
linalg/hypre.cpp:1746:4: error: ‘hypre_ParcsrAdd’ was not declared in this scope; did you mean ‘hypre_GraphAdd’?
 1746 |    hypre_ParcsrAdd(1.0, *A, 1.0, *B, &C);
      |    ^~~~~~~~~~~~~~~
      |    hypre_GraphAdd
linalg/hypre.cpp: In function ‘mfem::HypreParMatrix* mfem::RAP(const mfem::HypreParMatrix*, const mfem::HypreParMatrix*)’:
linalg/hypre.cpp:1775:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
 1775 |       hypre_ParCSRMatrixOwnsColStarts((hypre_ParCSRMatrix*)(*P));
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:1784:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1784 |    hypre_ParCSRMatrixSetRowStartsOwner(rap,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:1785:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1785 |    hypre_ParCSRMatrixSetColStartsOwner(rap,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In function ‘mfem::HypreParMatrix* mfem::RAP(const mfem::HypreParMatrix*, const mfem::HypreParMatrix*, const mfem::HypreParMatrix*)’:
linalg/hypre.cpp:1799:7: error: ‘hypre_ParCSRMatrixOwnsColStarts’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixColStarts’?
 1799 |       hypre_ParCSRMatrixOwnsColStarts((hypre_ParCSRMatrix*)(*P));
      |       ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |       hypre_ParCSRMatrixColStarts
linalg/hypre.cpp:1811:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1811 |    hypre_ParCSRMatrixSetRowStartsOwner(rap,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:1812:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
 1812 |    hypre_ParCSRMatrixSetColStartsOwner(rap,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In member function ‘virtual void mfem::HypreSmoother::SetOperator(const mfem::Operator&)’:
linalg/hypre.cpp:2431:65: error: too few arguments to function ‘HYPRE_Int hypre_ParCSRMaxEigEstimate(hypre_ParCSRMatrix*, HYPRE_Int, HYPRE_Real*, HYPRE_Real*)’
 2431 |          hypre_ParCSRMaxEigEstimate(*A, poly_scale, &max_eig_est);
      |                                                                 ^
In file included from linalg/hypre.hpp:27,
                 from linalg/complex_operator.hpp:18,
                 from linalg/linalg.hpp:21,
                 from linalg/hypre.cpp:16:
./../hypre/src/hypre/include/_hypre_parcsr_ls.h:2812:11: note: declared here
 2812 | HYPRE_Int hypre_ParCSRMaxEigEstimate ( hypre_ParCSRMatrix *A, HYPRE_Int scale, HYPRE_Real *max_eig,
      |           ^~~~~~~~~~~~~~~~~~~~~~~~~~
linalg/hypre.cpp:2446:65: error: too few arguments to function ‘HYPRE_Int hypre_ParCSRMaxEigEstimate(hypre_ParCSRMatrix*, HYPRE_Int, HYPRE_Real*, HYPRE_Real*)’
 2446 |          hypre_ParCSRMaxEigEstimate(*A, poly_scale, &max_eig_est);
      |                                                                 ^
In file included from linalg/hypre.hpp:27,
                 from linalg/complex_operator.hpp:18,
                 from linalg/linalg.hpp:21,
                 from linalg/hypre.cpp:16:

### 2884
/root/mfem/tests/unit/catch.hpp:10818:58: error: call to non-‘constexpr’ function ‘long int sysconf(int)’
10818 |     static constexpr std::size_t sigStackSize = 32768 >= MINSIGSTKSZ ? 32768 : MINSIGSTKSZ;
      |                                                          ^~~~~~~~~~~
In file included from /usr/include/x86_64-linux-gnu/bits/sigstksz.h:24,
                 from /usr/include/signal.h:328,
                 from /root/mfem/tests/unit/catch.hpp:8030,
                 from /root/mfem/tests/unit/unit_tests.hpp:15,
                 from /root/mfem/tests/unit/run_unit_tests.hpp:15,
                 from /root/mfem/tests/unit/unit_test_main.cpp:14:
/usr/include/unistd.h:640:17: note: ‘long int sysconf(int)’ declared here
  640 | extern long int sysconf (int __name) __THROW;
      |                 ^~~~~~~
In file included from /root/mfem/tests/unit/unit_tests.hpp:15,
                 from /root/mfem/tests/unit/run_unit_tests.hpp:15,
                 from /root/mfem/tests/unit/unit_test_main.cpp:14:
/root/mfem/tests/unit/catch.hpp:10877:45: error: size of array ‘altStackMem’ is not an integral constant-expression
10877 |     char FatalConditionHandler::altStackMem[sigStackSize] = {};
      |                                             ^~~~~~~~~~~~
In file included from /usr/include/signal.h:328,
                 from /root/mfem/tests/unit/catch.hpp:8030,
                 from /root/mfem/tests/unit/unit_tests.hpp:15,
                 from /root/mfem/tests/unit/run_unit_tests.hpp:15,
                 from /root/mfem/tests/unit/punit_test_main.cpp:14:
/root/mfem/tests/unit/catch.hpp:10818:58: error: call to non-‘constexpr’ function ‘long int sysconf(int)’
10818 |     static constexpr std::size_t sigStackSize = 32768 >= MINSIGSTKSZ ? 32768 : MINSIGSTKSZ;
      |                                                          ^~~~~~~~~~~
In file included from /usr/include/x86_64-linux-gnu/bits/sigstksz.h:24,
                 from /usr/include/signal.h:328,
                 from /root/mfem/tests/unit/catch.hpp:8030,
                 from /root/mfem/tests/unit/unit_tests.hpp:15,
                 from /root/mfem/tests/unit/run_unit_tests.hpp:15,
                 from /root/mfem/tests/unit/punit_test_main.cpp:14:
/usr/include/unistd.h:640:17: note: ‘long int sysconf(int)’ declared here
  640 | extern long int sysconf (int __name) __THROW;
      |                 ^~~~~~~
In file included from /root/mfem/tests/unit/unit_tests.hpp:15,
                 from /root/mfem/tests/unit/run_unit_tests.hpp:15,
                 from /root/mfem/tests/unit/punit_test_main.cpp:14:
/root/mfem/tests/unit/catch.hpp:10877:45: error: size of array ‘altStackMem’ is not an integral constant-expression
10877 |     char FatalConditionHandler::altStackMem[sigStackSize] = {};
      |                                             ^~~~~~~~~~~~
make[1]: Leaving directory '/root/mfem/miniapps/mtop'
make[1]: Leaving directory '/root/mfem/miniapps/nurbs'
mpicxx -O3 -std=c++11 -I../.. -I../../../hypre/src/hypre/include seq_example.o -o seq_example -L../.. -lmfem -L../../../hypre/src/hypre/lib -lHYPRE -L../../../metis-4.0 -lmetis -lrt
rm navier_tgv.o navier_shear.o ortho_solver.o navier_solver.o navier_mms.o navier_3dfoc.o navier_kovasznay.o navier_kovasznay_vs.o
make[1]: Leaving directory '/root/mfem/miniapps/navier'
mpicxx -O3 -std=c++11 -I../.. -I../../../hypre/src/hypre/include -o block-solvers div_free_solver.o block-solvers.o -L../.. -lmfem -L../../../hypre/src/hypre/lib -lHYPRE -L../../../metis-4.0 -lmetis -lrt
make[1]: *** [makefile:133: unit_test_main.o] Error 1
make[1]: *** Waiting for unfinished jobs....
rm seq_test.o seq_example.o par_example.o
make[1]: Leaving directory '/root/mfem/miniapps/autodiff'
make[1]: Leaving directory '/root/mfem/miniapps/solvers'
make[1]: Leaving directory '/root/mfem/examples'
make[1]: *** [makefile:133: punit_test_main.o] Error 1
make[1]: Leaving directory '/root/mfem/miniapps/meshing'
make[1]: Leaving directory '/root/mfem/miniapps/toys'
make[1]: Leaving directory '/root/mfem/miniapps/electromagnetics'
make[1]: Leaving directory '/root/mfem/miniapps/performance'
make[1]: Leaving directory '/root/mfem/tests/unit'
make: *** [makefile:446: tests/unit] Error 2

### 1930
linalg/complex_operator.cpp:802:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  802 |    hypre_ParCSRMatrixSetRowStartsOwner((hypre_ParCSRMatrix*)(*A),1);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/complex_operator.cpp:803:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  803 |    hypre_ParCSRMatrixSetColStartsOwner((hypre_ParCSRMatrix*)(*A),1);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
make: *** [makefile:430: linalg/complex_operator.o] Error 1
linalg/hypre.cpp: In constructor ‘mfem::HypreParVector::HypreParVector(MPI_Comm, HYPRE_Int, HYPRE_Int*)’:
linalg/hypre.cpp:58:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
   58 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In constructor ‘mfem::HypreParVector::HypreParVector(MPI_Comm, HYPRE_Int, double*, HYPRE_Int*)’:
linalg/hypre.cpp:72:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
   72 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In copy constructor ‘mfem::HypreParVector::HypreParVector(const mfem::HypreParVector&)’:
linalg/hypre.cpp:89:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
   89 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In constructor ‘mfem::HypreParVector::HypreParVector(mfem::ParFiniteElementSpace*)’:
linalg/hypre.cpp:123:4: error: ‘hypre_ParVectorSetPartitioningOwner’ was not declared in this scope; did you mean ‘hypre_ParVectorPartitioning’?
  123 |    hypre_ParVectorSetPartitioningOwner(x,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParVectorPartitioning
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int*, mfem::SparseMatrix*)’:
linalg/hypre.cpp:321:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  321 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:322:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  322 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int, HYPRE_Int*, HYPRE_Int*, mfem::SparseMatrix*)’:
linalg/hypre.cpp:360:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  360 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:361:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  361 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int, HYPRE_Int*, HYPRE_Int*, mfem::SparseMatrix*, mfem::SparseMatrix*, HYPRE_Int*)’:
linalg/hypre.cpp:399:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  399 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:400:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  400 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp: In constructor ‘mfem::HypreParMatrix::HypreParMatrix(MPI_Comm, HYPRE_Int, HYPRE_Int, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, HYPRE_Int*, double*, HYPRE_Int*, HYPRE_Int*, double*, HYPRE_Int, HYPRE_Int*)’:
linalg/hypre.cpp:441:4: error: ‘hypre_ParCSRMatrixSetRowStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  441 |    hypre_ParCSRMatrixSetRowStartsOwner(A,0);
      |    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      |    hypre_ParCSRMatrixSetDataOwner
linalg/hypre.cpp:442:4: error: ‘hypre_ParCSRMatrixSetColStartsOwner’ was not declared in this scope; did you mean ‘hypre_ParCSRMatrixSetDataOwner’?
  442 |    hypre_ParCSRMatrixSetColStartsOwner(A,0);